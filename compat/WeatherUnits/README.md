# WeatherUnits → unitcorn 🦄

WeatherUnits has been renamed to **[unitcorn](https://pypi.org/project/unitcorn/)**.

This package is a forwarding shim: it depends on unitcorn, and `import WeatherUnits`
(and every `WeatherUnits.*` submodule) resolves to the matching `unitcorn` module,
so classes are identical under both names. Importing it emits a `DeprecationWarning`.

To migrate:

```sh
pip uninstall WeatherUnits
pip install unitcorn
```

and replace `WeatherUnits` with `unitcorn` in your imports. The `WU_CONFIG_PATH` and
`WU_DEBUG` environment variables still work; their new names are
`UNITCORN_CONFIG_PATH` and `UNITCORN_DEBUG`.
