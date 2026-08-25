# Changelog

## 1.0.4

- **Fix:** Use `type = everyone` instead of `rights_default = read-write` in the `[rights]` section (Radicale 3.x syntax)

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
