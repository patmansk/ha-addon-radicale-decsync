# Changelog

## 1.0.8

- **Fix:** Remove `[rights]` section entirely when `auth_type=none` (Radicale 3.x has no `radicale.rights.none` or `radicale.rights.everyone` module; omitting the section grants default full access)

## 1.0.7

- **Fix:** Correct rights module name from `radicale.rights.none` to `radicale.rights.everyone` (module does not exist in Radicale 3.x)

## 1.0.6

- **Release:** Bump version to 1.0.6
- **Fix:** Use full Python module paths for Radicale 3.x rights

## 1.0.5

- **Fix:** Use full Python module paths in the `[rights]` section: `radicale.rights.none` (no auth) and `radicale.rights.authenticated` (htpasswd). Radicale 3.x does not accept short keywords like `everyone` or `authenticated`

## 1.0.3

- **Security:** htpasswd password is now passed via stdin instead of a CLI argument (no longer visible in `ps aux` or shell history)
- **Fix:** Rights section no longer forces `type = authenticated` when `auth_type` is `none`, so the server works out-of-the-box without authentication
- **Docs:** Added explanatory comment for the `setuptools<81` pin in the Dockerfile (required by `radicale_storage_decsync` 2.1.0's `pkg_resources` dependency)

## 1.0.2

- Fix s6-overlay PID 1 error: switch to python:3.12-alpine base image
- Fix startup crash: read options directly from /data/options.json
- Fix calendar discovery: use `authenticated` rights type (recommended by DecSync plugin)
- Pin setuptools<81 for libdecsync compatibility

## 1.0.0

- Initial release
- Radicale 3.2.3 with DecSync storage plugin 2.1.0
- Support for `none` and `htpasswd` (bcrypt) authentication
- Configurable DecSync directory path
- Web UI access on port 5232
- Multi-arch support: amd64, aarch64
