def MeasurementGroup(cls):
	cls._type = cls
	return cls


def UnitSystem(cls):
	cls._unitSystem = cls
	return cls


def BaseUnit(cls):
	cls._unitSystem._baseUnit = cls.__name__.lower()
	return cls
