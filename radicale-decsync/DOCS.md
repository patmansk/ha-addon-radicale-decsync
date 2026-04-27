# Radicale DecSync – Documentation

## Overview

This add-on runs a [Radicale](https://radicale.org) CalDAV/CardDAV server that uses the [DecSync storage plugin](https://github.com/39aldo39/Radicale-DecSync). DecSync enables serverless synchronization of calendars, contacts, and tasks by storing data in a shared directory that you sync between devices (e.g., with [Syncthing](https://syncthing.net)).

## Prerequisites

- A DecSync directory accessible to Home Assistant, typically under `/share/decsync`.
- To sync the DecSync directory across devices you can use the [Syncthing add-on](https://github.com/Poeschl/Hassio-Addons/tree/main/syncthing) or any other file-sync tool that maps into the HA `/share` folder.

## Configuration

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `decsync_dir` | string | `/share/decsync` | Path to the DecSync directory inside the container. Must be under a mapped volume (e.g., `/share`). |
| `auth_type` | enum | `none` | Authentication method: `none` (any credentials accepted) or `htpasswd` (username/password). |
| `users` | list | `[]` | List of `{username, password}` pairs. Only used when `auth_type` is `htpasswd`. |
| `log_level` | enum | `info` | Radicale log level: `debug`, `info`, `warning`, `error`, or `critical`. |

### Example configuration

```yaml
decsync_dir: "/share/decsync"
auth_type: "htpasswd"
users:
  - username: "alice"
    password: "s3cret"
  - username: "bob"
    password: "hunter2"
log_level: "info"
```

## Network

The add-on exposes port **5232** (TCP) by default. You can change the host-side port in the add-on's network configuration.

## Connecting CalDAV/CardDAV clients

Once the add-on is running, point your client to:

```
http://<your-home-assistant-ip>:5232
```

### Thunderbird

1. Open Thunderbird and go to the Calendar tab.
2. Right-click in the calendar list → **New Calendar…**
3. Select **On the Network** → **CalDAV**.
4. Enter the URL: `http://<ha-ip>:5232/<username>/`
5. Enter your username and password (if htpasswd auth is enabled).

### DAVx5 (Android)

1. Open DAVx5 and add a new account.
2. Use **Login with URL and username**.
3. Base URL: `http://<ha-ip>:5232`
4. Enter your username and password.

### GNOME Calendar / Evolution

1. Go to **Settings → Online Accounts → Other** (or add a CalDAV account directly).
2. Enter the CalDAV URL: `http://<ha-ip>:5232/<username>/`

### iOS / macOS Calendar

1. Go to **Settings → Calendar → Accounts → Add Account → Other → CalDAV**.
2. Server: `<ha-ip>:5232`
3. Enter your username and password.

## DecSync directory structure

The DecSync directory (default `/share/decsync`) is expected to contain sub-directories for each sync type:

```
decsync/
├── calendars/
│   ├── <calendar-name>/
│   │   └── ...
├── contacts/
│   ├── <address-book-name>/
│   │   └── ...
└── tasks/
    └── ...
```

These directories are automatically created and managed by DecSync-compatible apps (like [DecSync CC](https://github.com/39aldo39/DecSync-CC) on Android) and synchronized via Syncthing or similar tools.

## Data persistence

- **Radicale internal data** is stored in `/data/radicale/collections` (persisted across add-on restarts via the add-on's `/data` volume).
- **DecSync data** lives in the configured `decsync_dir` (typically `/share/decsync`).

## Security notes

- By default, `auth_type` is set to `none`, meaning **any** username and password is accepted. This is fine if Radicale is only accessible on your local network.
- For remote access or stricter security, set `auth_type` to `htpasswd` and configure users.
- Consider using the Home Assistant NGINX SSL proxy add-on if you need HTTPS.

## Troubleshooting

- **"Failed to load storage module"**: Make sure the DecSync directory exists and is accessible. Check the add-on logs.
- **"libdecsync: A 64bit platform is required"**: This add-on only supports 64-bit platforms (amd64, aarch64).
- **Empty calendar list**: You may need to create a calendar first. Visit the Radicale Web UI at `http://<ha-ip>:5232` and create a new calendar or address book, or let a DecSync-compatible app create them.
- **Permission errors**: Ensure the DecSync directory has correct permissions. The add-on runs as root inside the container.
