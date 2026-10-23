"""Dimension algebra: `*` and `/` between measurements of different dimensions.

Every algebraic dimension carries an exponent vector over the SI base
dimensions (length, mass, time, temperature), so a product or quotient adds or
subtracts vectors and multiplies the values *in the SI reference units*. SI is
coherent, so the result is already the reference unit of the result's
dimension (m × m = m², kg·m⁻¹·s⁻² = Pa) and no conversion tables are needed.

The result is a registered named type when one exists for the vector (speed,
pressure, length, ...), a dimensionless `float` when the vector is zero, and
otherwise a `Compound`, which carries its vector and prints its SI unit.
"""
from __future__ import annotations

from typing import Optional

from ._Measurement import Measurement, DerivedMeasurement

__all__ = ['Compound', 'register', 'vectorOf', 'siValue', 'multiply', 'divide', 'hasDimension']

Vector = tuple[int, int, int, int]

BASES = ('m', 'kg', 's', 'K')
ZERO: Vector = (0, 0, 0, 0)
MAX_EXPONENT = 3

_dimensions: dict[type, Vector] = {}
_references: dict[Vector, type] = {}
_SUPERSCRIPT = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


def register(dimension: type, vector: Vector, reference: Optional[type] = None) -> None:
	"""Declare `dimension`'s exponent vector. `reference` is the SI coherent unit
	class, which results with that vector are built as."""
	_dimensions[dimension] = tuple(vector)
	if reference is not None:
		_references[tuple(vector)] = reference
		_references[ZERO] = None


def hasDimension(measurement) -> bool:
	try:
		vectorOf(measurement)
	except TypeError:
		return False
	return True


def vectorOf(m) -> Vector:
	if isinstance(m, Compound):
		return m._vector
	if isinstance(m, DerivedMeasurement):
		n, d = vectorOf(m.numerator), vectorOf(m.denominator)
		return tuple(a - b for a, b in zip(n, d))
	for klass in type(m).__mro__:
		if klass in _dimensions:
			return _dimensions[klass]
	raise TypeError(f'{type(m).__name__} has no dimension to multiply or divide by')


def siValue(m) -> float:
	"""The measurement's magnitude in the coherent SI unit of its dimension."""
	if isinstance(m, Compound):
		return float(m)
	if isinstance(m, DerivedMeasurement):
		return siValue(m.numerator) / siValue(m.denominator)
	vector = vectorOf(m)
	if (factor := getattr(m, '_factor', None)) is not None and vector == (0, 0, 0, 1):
		return float(m) * factor  # a change in temperature: kelvin per degree
	reference = _references.get(vector)
	if vector == (0, 0, 0, 1):
		# A temperature *reading* is not a quantity: 20 °C × 2 is not 40 °C.
		from ..temperature import Temperature
		if isinstance(m, Temperature) and type(m).__name__ != 'Kelvin':
			raise TypeError(f'{m.withUnit} is a temperature reading and does not multiply or divide; use Kelvin or a change in temperature')
	return float(reference(m))


def _combine(a, b, sign: int):
	va, vb = vectorOf(a), vectorOf(b)
	vector = tuple(x + sign * y for x, y in zip(va, vb))
	if any(abs(e) > MAX_EXPONENT for e in vector):
		raise ValueError(f'{_symbol(vector)} is beyond the supported exponent range of ±{MAX_EXPONENT}')
	x, y = siValue(a), siValue(b)
	value = x * y if sign > 0 else x / y
	return build(value, vector)


def build(value: float, vector: Vector):
	"""A registered named type for `vector` if there is one, else a `Compound`."""
	if vector == ZERO:
		return float(value)
	if (reference := _references.get(vector)) is not None:
		return reference(value)
	return Compound(value, vector)


def multiply(a, b):
	return _combine(a, b, 1)


def divide(a, b):
	return _combine(a, b, -1)


def _symbol(vector: Vector) -> str:
	def term(base, e):
		return base if e == 1 else f'{base}{str(e).translate(_SUPERSCRIPT)}'
	pos = [term(b, e) for b, e in zip(BASES, vector) if e > 0]
	neg = [term(b, e) for b, e in zip(BASES, vector) if e < 0]
	if not pos:
		pos = ['1']
	if len(neg) == 1 and len(pos) == 1 and vector[BASES.index(neg[0].rstrip('⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))] == -1:
		return f'{pos[0]}/{neg[0].rstrip("⁻⁰¹²³⁴⁵⁶⁷⁸⁹")}'
	return '·'.join(pos + neg)



class Compound(Measurement):
	"""A value in a coherent SI unit with no named type (m², kg·m²·s⁻³).

	It knows its exponent vector, so it takes part in further `*` and `/`.
	"""
	_vector: Vector = ZERO
	_precision = 3

	def __new__(cls, value, vector: Vector = None, *args, **kwargs):
		if isinstance(value, Compound) and vector is None:
			vector = value._vector
		return Measurement.__new__(cls, value, *args, **kwargs)

	def __init__(self, value, vector: Vector = None, *args, **kwargs):
		if isinstance(value, Compound) and vector is None:
			vector = value._vector
		if vector is None:
			raise TypeError('Compound needs an exponent vector')
		self._vector = tuple(vector)
		self._unit = _symbol(self._vector)
		Measurement.__init__(self, float(value), *args, **kwargs)

	def _same(self, value):
		return Compound(value, self._vector)

	def __neg__(self):
		return self._same(-float(self))

	def __pos__(self):
		return self._same(float(self))

	def __abs__(self):
		return self._same(abs(float(self)))

	def __add__(self, other):
		return self._same(float(self) + self._operand(other))

	__radd__ = __add__

	def __sub__(self, other):
		return self._same(float(self) - self._operand(other))

	def __rsub__(self, other):
		return self._same(self._operand(other) - float(self))

	def __mul__(self, other):
		if isinstance(other, Measurement) and hasDimension(other):
			return multiply(self, other)
		return self._same(float(self) * float(other))

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Measurement) and hasDimension(other):
			return divide(self, other)
		return self._same(float(self) / float(other))

	def __rtruediv__(self, other):
		return build(float(other) / float(self), tuple(-e for e in self._vector))

	def __pow__(self, power, modulo=None):
		vector = tuple(e * int(power) for e in self._vector)
		if int(power) != power or any(abs(e) > MAX_EXPONENT for e in vector):
			raise ValueError(f'{self.unit} ** {power} is beyond the supported integer powers')
		return build(float(self) ** int(power), vector)

	def _operand(self, other) -> float:
		if isinstance(other, Compound):
			if other._vector != self._vector:
				from .. import errors
				raise errors.BadConversion(self, other)
			return float(other)
		if isinstance(other, Measurement) and hasDimension(other):
			if vectorOf(other) != self._vector:
				from .. import errors
				raise errors.BadConversion(self, other)
			return siValue(other)
		return float(other)

	def __eq__(self, other):
		try:
			return abs(float(self) - self._operand(other)) <= 1e-9 * max(1.0, abs(float(self)))
		except Exception:
			return False

	def __hash__(self):
		return hash((round(float(self), 9), self._vector))
