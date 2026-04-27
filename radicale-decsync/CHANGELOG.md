# Changelog

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
