"""WeatherUnits is now unitcorn.

This package only forwards to `unitcorn`. Every `WeatherUnits` module is the
`unitcorn` module of the same name — not a copy — so a class imported through
either name is the same class, and `isinstance` and pickles work across both.

Change ``import WeatherUnits`` to ``import unitcorn``. This shim warns once on
import and will not be updated past the 0.9 series.
"""
import importlib
import importlib.abc
import importlib.util
import sys
import warnings

import unitcorn as _target

warnings.warn(
	'WeatherUnits has been renamed to unitcorn; import unitcorn instead. '
	'The WeatherUnits package only forwards to it and will not be updated.',
	DeprecationWarning,
	stacklevel=2,
)

_OLD = __name__
_NEW = _target.__name__


class _Alias(importlib.abc.MetaPathFinder, importlib.abc.Loader):
	"""Resolve ``WeatherUnits.x.y`` to the already-imported ``unitcorn.x.y``."""

	def find_spec(self, fullname, path=None, target=None):
		if not fullname.startswith(_OLD + '.'):
			return None
		new = _NEW + fullname[len(_OLD):]
		module = importlib.import_module(new)
		return importlib.util.spec_from_loader(fullname, self, is_package=hasattr(module, '__path__'))

	def create_module(self, spec):
		# Hand back the real module, so both names share one object.
		module = importlib.import_module(_NEW + spec.name[len(_OLD):])
		spec.loader_state = module.__spec__
		return module

	def exec_module(self, module):
		# The import system has just set __spec__ to the alias's spec. Put the
		# real one back, or unitcorn's own relative imports and reloads would
		# start resolving against WeatherUnits.
		module.__spec__ = module.__spec__.loader_state


if not any(isinstance(finder, _Alias) for finder in sys.meta_path):
	sys.meta_path.insert(0, _Alias())

from unitcorn import *  # noqa: E402,F401,F403


def __getattr__(name):
	return getattr(_target, name)


def __dir__():
	return sorted(set(globals()) | set(dir(_target)))
