# Changelog


## 1.2.11
- **Feature:** `[sharing]` – `collection_by_map = true` + `permit_create_map = true` + `database_path` ergaenzt; aktiviert map-basiertes Sharing (u. a. fuer den eingebauten Geburtstagskalender / Conversion=bday in Radicale 3.8)

## 1.2.10


- **Fix (Radicale 3.8.0):** `discover()` – neue `user_groups`-Signatur unterstützt
- **Fix (Radicale 3.8.0):** `upload()` – Return-Wert `Tuple[Item, Optional[Item]]` korrekt entpackt
- **Fix (Radicale 3.8.0):** `check_and_sanitize_items()` – `max_vevent_rrule_occurrence=10000` ergänzt
- **Fix (Radicale 3.8.0):** `create_collection()` – 3-tuple Return-Wert per `[0]` entpackt
- **Fix (Radicale 3.8.0):** `resources_listener()` – `try/except` pro Eintrag, ein kaputter Eintrag bricht Sync nicht mehr ab
- **Fix (libdecsync):** `pkg_resources` → `importlib.resources` Shim (Python 3.12+)
- **Fix:** Add-on-Version in `config.yaml` auf 1.2.10 gesetzt

## 1.2.9
- **Fix:** [sharing] type = csv – ohne DB-Backend (Default none) liefert die Sharing-API 404

## 1.2.8
- **Fix:** `[sharing]` – `type`-Feld entfernt; Radicale 3.8 hat für Sharing kein Pluggable-Modul (im Gegensatz zu auth/group/rights); Sharing wird ausschließlich über Sub-Options aktiviert (`collection_by_token`, `permit_create_token`)

## 1.2.7
- **Fix:** `[sharing]` – fehlte `type = radicale.sharing.token`; ohne diesen Wert defaultet Radicale 3.8.0 auf `radicale.sharing.none` und deaktiviert die gesamte Sharing-API trotz korrekt gesetzter Sub-Options

## 1.2.6
- **Fix:** `[sharing]` config – korrekte Optionen `collection_by_token = true` + `permit_create_token = true` (ersetzt frühere invaliden Optionen); Web-UI Sharing-API liefert jetzt 200 statt 404
- **Cleanup:** Stale `.Radicale.cache`-Ordner wird bei jedem Start entfernt (verhindert Inkompatibilitäten mit älteren Radicale-Versionen)

## 1.2.5
- **Fix:** Removed `[sharing]` section entirely – Radicale 3.8.0 does not accept `calendar`, `address_book`, or `enabled` as valid options in this section (caused CRITICAL abort at startup)
- **Note:** Web-UI sharing-API 404s (`/.sharing/v1/all/list`) are cosmetic and do not affect CalDAV/CardDAV sync

## 1.2.4
- **Fix:** `[sharing]` config – `calendar`/`address_book` sind keine gültigen Optionen in Radicale 3.8.0; ersetzt durch `enabled = true` (korrigiert CRITICAL-Abort beim Start)

## 1.2.3
- **Fix:** Added `[sharing]` section to generated Radicale config – stops 404 errors from Web-UI sharing API calls (`/.sharing/v1/all/list`, `/.sharing/v1/all/info`)
- **Note:** Web-UI rendering quirks (stuck spinner, "Title" entry, broken logout) are upstream Radicale 3.8.0 bugs – not fixable from add-on side

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
