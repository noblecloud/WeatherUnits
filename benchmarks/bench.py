"""Micro-benchmarks for the hot paths. Run: python benchmarks/bench.py [--profile NAME]"""
import re
import subprocess
import sys
import timeit
import tracemalloc
from time import perf_counter

import unitcorn as uc
from unitcorn import Length, Temperature, Pressure, Wind

Celsius, Fahrenheit, Meter = Temperature.Celsius, Temperature.Fahrenheit, Length.Meter
Hectopascal = Pressure.Hectopascal
Mph = Wind.MilesPerHour
SPEC = 'precision=2, show_unit=False'

c, m, hpa, mph = Celsius(21.3), Meter(5), Hectopascal(1013.25), Mph(12.4)

CASES = {
	'construct Celsius(21.3)': lambda: Celsius(21.3),
	'construct Meter(5)': lambda: Meter(5),
	'construct Wind.MilesPerHour(12.4)': lambda: Mph(12.4),
	'convert Fahrenheit(Celsius)': lambda: Fahrenheit(c),
	"convert Meter['ft']": lambda: m['ft'],
	'convert Mph.ms': lambda: mph.ms,
	'str(Celsius)': lambda: str(c),
	'str(Meter)': lambda: str(m),
	'str(Hectopascal)': lambda: str(hpa),
	'str(Mph)': lambda: str(mph),
	f'format(Celsius, spec)': lambda: format(c, SPEC),
	f'format(Hectopascal, spec)': lambda: format(hpa, SPEC),
	f'format(Mph, spec)': lambda: format(mph, SPEC),
	"format(Meter, 'ft')": lambda: format(m, 'ft'),
	'hash(Celsius)': lambda: hash(c),
	'Celsius < Celsius': lambda: c < Celsius(30),
}


def importTime():
	best = None
	for _ in range(5):
		t = perf_counter()
		subprocess.run([sys.executable, '-c', 'import unitcorn'], check=True)
		dt = perf_counter() - t
		best = dt if best is None else min(best, dt)
	out = subprocess.run([sys.executable, '-X', 'importtime', '-c', 'import unitcorn'], capture_output=True, text=True).stderr
	rows = []
	for line in out.splitlines()[1:]:
		mt = re.match(r'import time:\s+(\d+) \|\s+(\d+) \| (\s*)(.*)', line)
		if mt and len(mt.group(3)) == 0 or (mt and mt.group(4).startswith('unitcorn')):
			rows.append((int(mt.group(2)), mt.group(3) + mt.group(4)))
	return best * 1000, sorted(rows, reverse=True)[:6]


def bestOf(fn, n):
	timer = timeit.Timer(fn)
	return min(timer.repeat(repeat=7, number=n)) / n


def memory(factory):
	tracemalloc.start()
	keep = [factory(i) for i in range(10_000)]
	cur, peak = tracemalloc.get_traced_memory()
	tracemalloc.stop()
	del keep
	return cur / 1024


if __name__ == '__main__':
	if len(sys.argv) > 2 and sys.argv[1] == '--profile':
		import cProfile, pstats
		fn = CASES[sys.argv[2]]
		pr = cProfile.Profile()
		pr.enable()
		for _ in range(5000):
			fn()
		pr.disable()
		for key in ('tottime', 'cumtime'):
			pstats.Stats(pr).strip_dirs().sort_stats(key).print_stats(18)
		sys.exit()
	ms, top = importTime()
	print(f'import unitcorn (wall, best of 5): {ms:.1f} ms')
	for us, name in top:
		print(f'    {us / 1000:7.1f} ms cumulative  {name}')
	print()
	print(f'{"case":<38}{"us/op":>10}')
	for name, fn in CASES.items():
		fn()
		n = 2000
		print(f'{name:<38}{bestOf(fn, n) * 1e6:>10.2f}')
	print()
	print('memory per 10k instances (KiB, tracemalloc)')
	for name, f in {'Celsius': lambda i: Celsius(i / 3), 'Meter': lambda i: Meter(i), 'Mph': lambda i: Mph(i)}.items():
		print(f'{name:<38}{memory(f):>10.0f}')
