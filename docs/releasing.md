# Releasing

Release order matters: `unitcorn` first, then the `WeatherUnits` shim, which depends on it.
The `Release` workflow does both in that order when a `v*` tag is pushed.

One-time setup, on pypi.org (needs the account owner):

1. Add a pending trusted publisher for `unitcorn` and another for `WeatherUnits`:
   owner `noblecloud`, repository `WeatherUnits` (or `unitcorn` after a repo rename),
   workflow `release.yml`, environment `pypi`.
2. Create a `pypi` environment in the repo's GitHub settings.

Then: bump the version in `pyproject.toml` and `compat/WeatherUnits/pyproject.toml`,
merge to `main`, `git tag v0.9.0 && git push origin v0.9.0`.

Renaming the GitHub repo to `unitcorn` keeps the old URL redirecting. After it, update
the `repository` and `Bug Tracker` URLs in `pyproject.toml` and LevityDash's setup scripts.
