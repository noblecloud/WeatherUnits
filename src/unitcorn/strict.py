"""Strict unit lookup: `lookup`, `parse` and `suggest`.

Reading a unit string you did not choose (a weather API's `"degC"`, a sensor's
`"%"`) is the one place a wrong guess is worse than an error: a value in the
wrong unit looks fine. So these functions either return the unit the text names
or raise `UnknownUnit` / `AmbiguousUnit`. They never fall back to a near miss.
`suggest` is the explicit, separate way to ask for near misses.

How a string is matched, in order. Each step looks only at the units of the
`dimension` when one is given.

1. **Normalise** the text: Unicode compatibility form (`µ` `μ` `u`, `²` `^2` `2`,
   `℃`), `°` and `deg` are one spelling (`°C`, `° C`, `deg C` and `degC` are the
   same text), `·` `⋅` `*` are one form, runs of whitespace collapse.
2. **Exact**, case sensitive, against unit symbols and declared aliases
   (`_parse_aliases` on the class).
3. **Name**, ignoring case, spaces and hyphens: `meter`, `Square Meter`, `meters`.
4. **Case insensitive** symbols, only if exactly one unit matches. So `KM` is the
   kilometer but `K` and `k` stay apart. This step is refused for a single
   character (`k` is not Kelvin, `w` is not Watt) and when the difference is an
   `m` against an `M` (`mW` is not Megawatt, `mm` is not `Mm`).
5. A text with one `/` that did not match is read as a **compound**: both sides
   are looked up the same way and divided with the dimension algebra
   (`km/h` is `Kilometer / Hour`). Only a result the library has a named or rate
   type for is accepted; a catch-all `Compound`, or a plain number, is refused.

Ambiguity. Matches are grouped by dimension (Length, Time, …). More than one
group is an `AmbiguousUnit`. Inside one group, duplicates are not the caller's
problem and the choice is deterministic: when a `dimension` is given, a unit
whose own type *is* that dimension wins; otherwise the most derived class wins
(`Wind.MilesPerHour` over `DistanceOverTime.MilesPerHour`, both of which are
`mph`); with neither, they are different units that share a spelling, and it is ambiguous
(`m` within Time is Minute and Month).

A class declares extra spellings with `_parse_aliases = ('degC',)`, and spellings
that are only valid when a dimension is given (`C` for Celsius, `%` for
PartsPer.Hundred) with `_parse_scoped = ('c', 'C')`. Both are read from the class's
own `__dict__`, never inherited, so `Humidity` does not answer to `%`. The
plural symbols the library generates by adding `s` (`ms` for Meter, `kms`, `ts`
for Ton) are not accepted: they are not how anyone writes a unit, and `ms` is
the millisecond.
"""
import re
import unicodedata
from difflib import SequenceMatcher
from itertools import product
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type

from .base import Dimension, Measurement
from .base import _SmartFloat
from .base._Algebra import Compound
from .base.Registry import UnitRegistry
from .errors import AmbiguousUnit, UnknownUnit

__all__ = ['lookup', 'parse', 'suggest']

_NUMBER = re.compile(r'^\s*(?P<number>[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(?P<unit>.*?)\s*$', re.S)
_DOT_OPERATORS = str.maketrans({'·': '*', '⋅': '*', '∙': '*', '•': '*', '×': '*'})
_NAME_SEPARATORS = re.compile(r'[\s\-_]+')


def normalise(text: str) -> str:
	"""The spelling every unit string is compared in. See the module docstring."""
	# the masculine ordinal and the ring above are what keyboards and fonts give for a degree sign
	text = text.replace('\u00ba', '\u00b0').replace('\u02da', '\u00b0')
	text = unicodedata.normalize('NFKC', text)
	text = text.replace('μ', 'u').translate(_DOT_OPERATORS)
	text = text.replace('**', '^')
	text = re.sub(r'\^(\d)', r'\1', text)
	text = text.replace('°', 'deg')
	text = re.sub(r'(?i)deg\s+', 'deg', text)
	text = re.sub(r'\s+', ' ', text).strip()
	text = re.sub(r'\s*([/*])\s*', r'\1', text)
	return text


def _nameKey(text: str) -> str:
	return _NAME_SEPARATORS.sub('', normalise(text)).casefold()


class _Entry:
	__slots__ = ('unit', 'spelling', 'scopedOnly')

	def __init__(self, unit: type, spelling: str, scopedOnly: bool):
		self.unit = unit
		self.spelling = spelling
		self.scopedOnly = scopedOnly


class _Index:
	"""Every spelling of every unit, built from the registry and kept until a unit class changes."""
	__slots__ = ('generation', 'exact', 'names', 'folded', 'units')

	def __init__(self):
		self.generation = _SmartFloat._unitGeneration
		self.exact: Dict[str, List[_Entry]] = {}
		self.names: Dict[str, List[_Entry]] = {}
		self.folded: Dict[str, List[_Entry]] = {}
		self.units: List[type] = []
		for unit in sorted(UnitRegistry._all_units, key=lambda c: (c.__module__, c.__qualname__)):
			self._add(unit)

	def _add(self, unit: type):
		if '[' in unit.__name__:
			# `DistanceOverTime[km/hr]`: made on demand by the algebra, reached by splitting the text
			return
		own = unit.__dict__
		symbol = getattr(unit, 'unit', None) or ''
		spellings: Dict[str, bool] = {}  # normalised spelling -> scoped only
		if symbol:
			spellings[normalise(symbol)] = False
		# A unit that inherits its symbol (Wind.Knot from Rate.Knot) inherits that class's aliases too
		declared = getattr(unit, '_aliases', None) or () if symbol else own.get('_aliases', ())
		for alias in (*declared, *own.get('_parse_aliases', ())):
			spellings[normalise(alias)] = False
		for spelling in own.get('_parse_scoped', ()):
			spellings[normalise(spelling)] = True
		if not spellings:
			return
		self.units.append(unit)
		for spelling, scopedOnly in spellings.items():
			entry = _Entry(unit, spelling, scopedOnly)
			self.exact.setdefault(spelling, []).append(entry)
			self.folded.setdefault(spelling.casefold(), []).append(entry)
		names = [getattr(unit, 'name', None)]
		plural = getattr(unit, 'pluralName', None)
		# The generated plural of `Percentage` is `Dimensionlesses`; a plural that does not begin like the name is not one
		if plural and names[0] and plural.casefold().startswith(names[0].casefold()[:4]):
			names.append(plural)
		for name in names:
			if name:
				self.names.setdefault(_nameKey(name), []).append(_Entry(unit, name, False))


_index: Optional[_Index] = None


def _current() -> _Index:
	global _index
	index = _index
	if index is None or index.generation != _SmartFloat._unitGeneration:
		index = _index = _Index()
	return index


def _checkDimension(dimension):
	if dimension is not None and not isinstance(dimension, type):
		raise TypeError(f'dimension must be a unit class such as unitcorn.Time, not {dimension!r}')


def _inScope(unit: type, dimension: Optional[type]) -> bool:
	if dimension is None:
		return True
	try:
		return issubclass(unit, dimension)
	except TypeError:
		return False


def _dimensionOf(unit: type) -> type:
	"""The dimension a unit belongs to, for telling a real ambiguity from a duplicate."""
	dimensions = [base for base in unit.__mro__ if isinstance(base, Dimension)]
	if dimensions:
		return dimensions[-1]
	generic = unit.type
	if generic is Measurement or generic is None:
		return unit
	from .derived import DistanceOverTime
	try:
		if issubclass(generic, DistanceOverTime):
			return DistanceOverTime
	except TypeError:
		pass
	return generic


def _pick(group: List[type], dimension: Optional[type]) -> List[type]:
	"""The units left out of several of one dimension: one if they are duplicates, more if they are different units."""
	if len(group) == 1:
		return group
	if dimension is not None:
		exact = [unit for unit in group if unit.type is dimension]
		if len(exact) == 1:
			return exact
		if exact:
			group = exact
	derived = [unit for unit in group if all(other is unit or issubclass(unit, other) for other in group)]
	if len(derived) == 1:
		return derived
	# Unrelated classes of one dimension sharing a spelling are different units (`m` is Minute and Month)
	return sorted(group, key=lambda c: (c.__module__, c.__qualname__))


def _choose(text: str, entries: Iterable[_Entry], dimension: Optional[type]) -> type:
	groups: Dict[type, List[type]] = {}
	for entry in entries:
		group = groups.setdefault(_dimensionOf(entry.unit), [])
		if entry.unit not in group:
			group.append(entry.unit)
	picked = [unit for _, group in sorted(groups.items(), key=lambda item: item[0].__name__) for unit in _pick(group, dimension)]
	if len(picked) > 1:
		raise AmbiguousUnit(text, picked, dimension=dimension)
	return picked[0]


def _caseMayFold(key: str, spelling: str) -> bool:
	"""Whether a match that differs only in case is safe to accept."""
	if len(key) < 2:
		return False
	if len(key) == len(spelling):
		for a, b in zip(key, spelling):
			# milli and mega differ by nine orders of magnitude and only in case. Capitals alone
			# carry no case information (`KM`), so `M` may stand for `m` there and nowhere else.
			if a != b and a in 'mM' and not (a == 'M' and key.isupper()):
				return False
	return True


def _resolve(text: str, dimension: Optional[type]) -> type:
	"""Steps 1 to 4 of the module docstring, for a single unit with no `/`-splitting."""
	index = _current()
	key = normalise(text)
	scoped = dimension is not None

	def usable(entries: Iterable[_Entry]) -> List[_Entry]:
		return [entry for entry in entries if (scoped or not entry.scopedOnly) and _inScope(entry.unit, dimension)]

	if key:
		for table, lookupKey in ((index.exact, key), (index.names, _nameKey(key))):
			if found := usable(table.get(lookupKey, ())):
				return _choose(text, found, dimension)
		if found := [entry for entry in usable(index.folded.get(key.casefold(), ())) if _caseMayFold(key, entry.spelling)]:
			try:
				return _choose(text, found, dimension)
			except AmbiguousUnit:
				pass  # more than one unit differs only in case: not "exactly one match"
	raise UnknownUnit(text, suggest(text, dimension), dimension=dimension)


def _divide(top: type, bottom: type, dimension: Optional[type]) -> Optional[type]:
	"""The unit class of one `top` per `bottom`, or None if the library has no proper type for it."""
	if dimension is not None and getattr(dimension, 'isDerived', False):
		# Wind and the like: dividing gives a plain DistanceOverTime, so ask the dimension to make it
		try:
			made = dimension[top:bottom]
			if isinstance(made(1), dimension):
				return made
		except Exception:
			pass
	try:
		result = top(1) / bottom(1)
	except (TypeError, ValueError, ArithmeticError):
		return None
	# A float is a ratio of like units (min/s), a Compound is the algebra's catch-all in SI units
	if not isinstance(result, Measurement) or isinstance(result, Compound):
		return None
	if dimension is not None and not isinstance(result, dimension):
		return None
	return type(result)


def _compound(text: str, dimension: Optional[type]) -> List[Tuple[type, type, type]]:
	"""`(numerator, denominator, result)` for every way `text` reads as `a/b`; raises `UnknownUnit` if none."""
	key = normalise(text)
	numerator, _, denominator = key.partition('/')
	# `m/m` would read as meters per minute, the one combination that is not a plain ratio
	if key.count('/') != 1 or not numerator or not denominator or numerator == denominator:
		raise UnknownUnit(text, suggest(text, dimension), dimension=dimension)
	sides = []
	for part in (numerator, denominator):
		try:
			sides.append([_resolve(part, None)])
		except AmbiguousUnit as ambiguous:
			sides.append(ambiguous.candidates)
		except UnknownUnit as unknown:
			raise UnknownUnit(text, unknown.candidates, dimension=dimension, reason=f'{part!r} is not a unit') from None
	built = []
	for top, bottom in product(*sides):
		if (result := _divide(top, bottom, dimension)) is not None:
			built.append((top, bottom, result))
	if not built:
		raise UnknownUnit(text, dimension=dimension, reason=f'{numerator!r} per {denominator!r} is not a unit this library can represent')
	if len({result for _, _, result in built}) > 1:
		raise AmbiguousUnit(text, [result for _, _, result in built], dimension=dimension)
	return built


def lookup(unit: str, dimension: Optional[type] = None) -> type:
	"""The unit class a unit string names. Raises rather than guess.

	>>> import unitcorn as uc
	>>> uc.lookup('°C')
	Celsius
	>>> uc.lookup('m', uc.Time)
	Minute

	`dimension` limits the search to the units of that dimension (`uc.Time`,
	`uc.Length`, `uc.Wind`, …) and allows the spellings that are only safe with
	one (`C`, `F`, and `%` as parts-per-hundred).

	Raises `UnknownUnit` if nothing matches (its `candidates` are the closest
	units, from `suggest`) and `AmbiguousUnit` if units of more than one
	dimension match (`lookup('m')` is Meter or Minute). See the module docstring
	for the rules.
	"""
	_checkDimension(dimension)
	if not isinstance(unit, str):
		raise TypeError(f'a unit is a string, not {type(unit).__name__}')
	try:
		return _resolve(unit, dimension)
	except UnknownUnit:
		if '/' not in unit:
			raise
	return _compound(unit, dimension)[0][2]


def parse(value, unit=None, dimension: Optional[type] = None):
	"""A measurement from a number and a unit string. Raises rather than guess.

	Either one string, ``parse('10 m/s')``, or a number and a unit,
	``parse(10, 'm/s')``. A `dimension` can follow either form
	(``parse('10 m', uc.Length)``, ``parse(10, 'm', uc.Time)``) or be named.

	>>> import unitcorn as uc
	>>> uc.parse('10 m/s')
	MetersPerSecond(10 m/s)
	>>> uc.parse(21.5, '°C')
	Celsius(21.5°)

	The text is a number, optional whitespace, then the unit. A compound such as
	``km/h`` gives whatever dividing the two units gives. A percentage is read as
	percent: ``parse('1 %')`` is 1 %, not 100 %.

	Raises `UnknownUnit` or `AmbiguousUnit` (both are `ValueError`) as `lookup` does,
	and a plain `ValueError` if the text has no number or no unit.
	"""
	if unit is not None and not isinstance(unit, str):
		if dimension is not None:
			raise TypeError('dimension given twice')
		unit, dimension = None, unit
	_checkDimension(dimension)
	if unit is None:
		if not isinstance(value, str):
			raise TypeError(f'parse(text) takes a string like "10 m/s", not {type(value).__name__}; give the unit as a second argument')
		match = _NUMBER.match(value)
		if match is None:
			raise ValueError(f'no number at the start of {value!r}')
		value, unit = float(match['number']), match['unit']
		if not unit:
			raise ValueError(f'no unit after the number in {value!r}')
	else:
		if isinstance(value, bool) or not isinstance(value, (int, float, str)):
			raise TypeError(f'a value is a number, not {type(value).__name__}')
		value = float(value)
	try:
		cls = _resolve(unit, dimension)
	except UnknownUnit:
		if '/' not in unit:
			raise
		return _compound(unit, dimension)[0][2](value)
	return _make(cls, value)


def _make(cls: type, value: float):
	from .others import Percentage
	if issubclass(cls, Percentage):
		# The default guesses the scale from the number, and 1 would be read as 100 %
		return cls(value, isPercentage=True)
	return cls(value)


def suggest(text: str, dimension: Optional[type] = None, n: int = 5) -> List[type]:
	"""The units whose spelling is closest to `text`, best first. Never picks one for you.

	Returns a list of unit classes, at most `n`, each once. An empty list means
	nothing is close. Matching is fuzzy and case insensitive, over symbols, aliases
	and names, so it is for showing a person ("did you mean …?"), not for
	deciding. `dimension` limits it to one dimension's units.

	>>> import unitcorn as uc
	>>> uc.suggest('degC')[0]
	Celsius
	"""
	_checkDimension(dimension)
	key = normalise(text).casefold()
	if not key:
		return []
	index = _current()
	scoped = dimension is not None
	best: Dict[type, Tuple[float, int]] = {}

	def consider(candidates: Dict[str, List[_Entry]], transform=str.casefold):
		for spelling, entries in candidates.items():
			for entry in entries:
				if (entry.scopedOnly and not scoped) or not _inScope(entry.unit, dimension):
					continue
				target = transform(spelling)
				score = SequenceMatcher(None, key, target).ratio()
				if len(target) > 2 and len(key) > 2 and (target.startswith(key) or key.startswith(target)):
					score = max(score, 0.75)
				if score >= 0.6:
					previous = best.get(entry.unit)
					rank = (score, -len(target))
					if previous is None or rank > previous:
						best[entry.unit] = rank

	consider(index.exact)
	consider(index.names)
	ranked = sorted(best.items(), key=lambda item: (-item[1][0], -item[1][1], item[0].__name__))
	return [unit for unit, _ in ranked[:n]]
