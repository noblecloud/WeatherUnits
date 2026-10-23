"""Pin the units config before unitcorn is first imported.

The config is read at import time, in a class body, so this has to run before
the first `import unitcorn`. Without it the default file follows the
machine's locale (`us.toml` for en_US, `si.toml` otherwise) and the suite passes
or fails with the locale of whoever runs it.

`si.toml` is chosen because the assertions are written against it: its
`[UnitProperties]` (mmHg's precision and trailing zeros) and its local units
(pressure is mmHg, not inHg) are what the expected strings encode. It is the
bundled file that also loads on the CI hosts. `tests/config.ini` is not used: it
has drifted from `us.toml` (`wind = mi/hraust`, stale `[Units]` section).

`setdefault`, so `UNITCORN_CONFIG_PATH=... pytest` still tries another file. Under
`us.toml` 18 tests fail: they assert si.toml's values rather than set their own.
"""
import os
from pathlib import Path

os.environ.setdefault('UNITCORN_CONFIG_PATH', str(Path(__file__).resolve().parents[1] / 'src' / 'unitcorn' / 'config' / 'si.toml'))
