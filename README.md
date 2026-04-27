# Home Assistant Add-on: Radicale DecSync

[![GitHub Release](https://img.shields.io/github/v/release/patmansk/ha-addon-radicale-decsync)](https://github.com/patmansk/ha-addon-radicale-decsync/releases)
[![License](https://img.shields.io/github/license/patmansk/ha-addon-radicale-decsync)](LICENSE)

A Home Assistant OS add-on that runs a [Radicale](https://radicale.org) CalDAV/CardDAV server with [DecSync](https://github.com/39aldo39/DecSync) storage integration for **serverless synchronization** of calendars, contacts, and tasks.

## What does this add-on do?

This add-on lets you **sync calendars and contacts across all your devices without relying on a cloud service** like Google or iCloud. Instead, it uses a shared folder (synced via [Syncthing](https://syncthing.net) or similar) to keep everything in sync.

**How it works:**

1. [DecSync CC](https://github.com/39aldo39/DecSyncCC) (Android) or other DecSync apps write calendar/contact data to a shared **DecSync directory**.
2. That directory is synced to your Home Assistant instance (e.g., via the [Syncthing add-on](https://github.com/Poeschl/Hassio-Addons/tree/main/syncthing)) into `/share/decsync`.
3. This add-on runs **Radicale** with the [DecSync storage plugin](https://github.com/39aldo39/Radicale-DecSync), which reads and writes to that directory.
4. Any **CalDAV/CardDAV client** (Thunderbird, iOS Calendar, GNOME Calendar, DAVx5, etc.) can connect to Radicale and access all your calendars and contacts.
5. Changes made through any client are synced back to all devices via DecSync.

**No cloud account needed. Your data stays on your devices.**

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click **⋮** (top-right) → **Repositories**.
3. Add this repository URL:
   ```
   https://github.com/patmansk/ha-addon-radicale-decsync
   ```
4. Find **"Radicale DecSync"** in the store and click **Install**.
5. Configure the add-on (see below).
6. Click **Start**.

## Configuration

| Option | Default | Description |
|---|---|---|
| `decsync_dir` | `/share/decsync` | Path to your DecSync directory (must be under `/share`). |
| `auth_type` | `none` | `none` = any username/password accepted. `htpasswd` = only configured users allowed. |
| `users` | `[]` | List of users (only used with `htpasswd` auth). |
| `log_level` | `info` | Log verbosity: `debug`, `info`, `warning`, `error`, `critical`. |

### Authentication

#### No authentication (`auth_type: none`)

By default, Radicale accepts **any username and password**. This is convenient for local-only setups, but anyone on your network can access and modify your data. Each username gets its own set of collections — just log in with a name, and your DecSync calendars will appear.

#### Password authentication (`auth_type: htpasswd`)

For better security, switch to `htpasswd` authentication. You define users and passwords in the add-on configuration:

```yaml
auth_type: htpasswd
users:
  - username: patrick
    password: mysecretpassword
  - username: anna
    password: herpassword
```

Only the configured users can log in. Each user sees their own calendars and contacts (populated from the shared DecSync directory).

**When should you use htpasswd?**
- If your HA instance is accessible from outside your local network
- If multiple people share the same network and you want separate accounts
- If you want to prevent accidental access

## Connecting clients

Once the add-on is running, connect any CalDAV/CardDAV client to:

```
http://<your-home-assistant-ip>:5232
```

### Thunderbird

1. Go to the **Calendar** tab.
2. Right-click in the calendar list → **New Calendar…** → **On the Network**.
3. Username: your Radicale username.
4. Location: `http://<ha-ip>:5232/<username>/`

### DAVx5 (Android)

1. Add a new account → **Login with URL and username**.
2. Base URL: `http://<ha-ip>:5232`
3. Enter your username and password.

### iOS / macOS

1. **Settings → Calendar → Accounts → Add Account → Other → CalDAV**.
2. Server: `<ha-ip>`, Port: `5232`.
3. Enter your username and password.

### GNOME Calendar / Evolution

1. **Settings → Online Accounts** → add a CalDAV account.
2. URL: `http://<ha-ip>:5232/<username>/`

## DecSync directory structure

Your DecSync directory (default `/share/decsync`) should have this structure:

```
/share/decsync/
├── calendars/
│   ├── <calendar-id>/
│   │   ├── v2/
│   │   │   └── <app-id>/...
│   │   └── local/...
├── contacts/
│   └── <addressbook-id>/...
└── tasks/
    └── <task-list-id>/...
```

This structure is created automatically by DecSync-compatible apps like [DecSync CC](https://github.com/39aldo39/DecSyncCC). Make sure Syncthing (or your sync tool) syncs the **root DecSync directory** — the one that contains the `calendars/`, `contacts/`, and `tasks/` folders — into `/share/decsync`.

## Prerequisites

- **DecSync data source**: An app that writes DecSync data, like [DecSync CC](https://github.com/39aldo39/DecSyncCC) on Android.
- **Sync tool**: [Syncthing](https://syncthing.net) (available as an [HA add-on](https://github.com/Poeschl/Hassio-Addons/tree/main/syncthing)) or any other file sync tool to get the DecSync directory onto your HA instance.
- **64-bit system**: Only amd64 and aarch64 architectures are supported (required by the libdecsync native library).

## Troubleshooting

| Problem | Solution |
|---|---|
| Empty calendar list after login | Check that your DecSync directory has the correct structure (see above). The `calendars/` folder must exist inside your `decsync_dir`. |
| "Failed to load storage module" | Check the add-on logs. The DecSync directory may not exist or may have permission issues. |
| Cannot reach port 5232 | Make sure the port is not blocked by your firewall and the add-on is running. Check **Network** settings in the add-on config. |
| Changes not syncing to other devices | Verify Syncthing is running and the DecSync directory is actively syncing. |

## Components

- [Radicale](https://radicale.org) v3.2.3 — CalDAV/CardDAV server
- [radicale_storage_decsync](https://github.com/39aldo39/Radicale-DecSync) v2.1.0 — DecSync storage plugin
- [libdecsync](https://github.com/39aldo39/libdecsync) — DecSync native library

## License

This project is open source. See individual component licenses for details.
