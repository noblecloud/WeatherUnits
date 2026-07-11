from typing import Dict, Type, TYPE_CHECKING, Optional, Set, Union, Tuple, List
import logging

if TYPE_CHECKING:
	from ._Measurement import Measurement

log = logging.getLogger('WeatherUnits').getChild('Registry')

class UnitRegistry:
	_units_by_symbol: Dict[str, Type['Measurement']] = {}
	_units_by_name: Dict[str, Type['Measurement']] = {}
	_units_by_alias: Dict[str, Type['Measurement']] = {}
	_all_units: Set[Type['Measurement']] = set()
	_derived_units: Dict[Tuple[Type['Measurement'], Type['Measurement']], List[Type['Measurement']]] = {}

	@classmethod
	def register(cls, unit_class: Type['Measurement']):
		cls._all_units.add(unit_class)
		
		# Register by name
		name = getattr(unit_class, '_name', unit_class.__name__).lower()
		cls._units_by_name[name] = unit_class
		
		# Register by unit symbol
		if hasattr(unit_class, '_unit') and unit_class._unit:
			cls._units_by_symbol[unit_class._unit.lower()] = unit_class
			
		# Register by plural unit
		if hasattr(unit_class, '_pluralUnit') and unit_class._pluralUnit:
			cls._units_by_symbol[unit_class._pluralUnit.lower()] = unit_class

		# Register by aliases
		if hasattr(unit_class, '_aliases') and unit_class._aliases:
			for alias in unit_class._aliases:
				cls._units_by_alias[alias.lower()] = unit_class

		# Register derived units by (numerator_dim, denominator_dim)
		if getattr(unit_class, 'isDerived', False):
			cls.register_derived(unit_class)

	@classmethod
	def register_derived(cls, derived_class: Type['Measurement']):
		if not (hasattr(derived_class, 'numerator') and hasattr(derived_class, 'denominator')):
			return
		num = derived_class.numerator
		den = derived_class.denominator
		if num and den and not (num.isGeneric or den.isGeneric):
			key = (num.type, den.type)
			if key not in cls._derived_units:
				cls._derived_units[key] = []
			if derived_class not in cls._derived_units[key]:
				cls._derived_units[key].append(derived_class)

	@classmethod
	def get_derived(cls, numerator: Type['Measurement'], denominator: Type['Measurement']) -> Optional[Type['Measurement']]:
		key = (numerator.type, denominator.type)
		matches = cls._derived_units.get(key, [])
		for match in matches:
			if match.numerator == numerator and match.denominator == denominator:
				return match
		
		# If no exact match, return a generic one if available
		for match in matches:
			if match.isGeneric:
				return match[numerator:denominator]
		return None

	@classmethod
	def get(cls, unit_str: str) -> Optional[Type['Measurement']]:
		unit_str = unit_str.lower()
		return (cls._units_by_symbol.get(unit_str) or 
				cls._units_by_name.get(unit_str) or 
				cls._units_by_alias.get(unit_str))

UnitRegistryInstance = UnitRegistry()
