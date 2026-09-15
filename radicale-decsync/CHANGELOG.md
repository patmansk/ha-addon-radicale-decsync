# Changelog


## 1.2.2
- **Fix:** Correct `patch_compatibility.py` – no longer reverts `storage.Storage` to `BaseStorage` (multifilesystem.Storage is the correct base in Radicale 3.8.0); instead *reverts* an incorrect prior patch that had changed it to `BaseStorage`
- **Fix:** `upload()` now correctly returns `(item, old_item)` tuple as required by Radicale 3.6+
- **Note:** All other patches (discover signature, pkg_resources shim) already applied in 1.2.1


## 1.2.1

- **Fix:** `class Storage(storage.Storage)` → `class Storage(BaseStorage)` – multifilesystem in Radicale 3.8.0 no longer exposes a `Storage` attribute
- **Fix:** `libdecsync` `pkg_resources.resource_filename` → `importlib.resources.files` shim (Python 3.13 / setuptools ≥ 81 safety net)
- **Fix:** `discover()` signature + `upload()` Tuple return (Radicale 3.6+ API changes)
- **Note:** Reverted unnecessary `get_uid`/`get_href` patches – plugin defines its own via `CollectionHrefMappingsMixin`

## 1.1.0

- **Upgrade:** Radicale 3.2.3 → 3.8.0 (new features: sharing-by-group/realm, O(n²) PROPFIND fix, improved bcrypt handling, multiple bug fixes)
- **Fix:** Replace deprecated `passlib` with `libpass >= 1.9.3` (required by Radicale ≥ 3.6.0)
- **Note:** `radicale_storage_decsync` remains at 2.1.0 (no newer release available; plugin API unchanged in Radicale 3.8.0)

## 1.0.9

- **Fix:** Rewrite `run.sh` to be fully POSIX-compatible (HAOS uses `sh`, not `bash`). Replace heredocs in if-blocks with echo, replace `<<<` with printf pipe.

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
