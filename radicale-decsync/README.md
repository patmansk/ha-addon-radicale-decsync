# Radicale DecSync Add-on for Home Assistant

Sync your calendars, contacts, and tasks across all devices — without a cloud service.

This add-on runs a [Radicale](https://radicale.org) CalDAV/CardDAV server with the [DecSync](https://github.com/39aldo39/DecSync) storage plugin. It reads and writes to a shared DecSync directory (synced via [Syncthing](https://syncthing.net) or similar), letting any CalDAV/CardDAV client access your data.

## How it works

1. **DecSync apps** (like [DecSync CC](https://github.com/39aldo39/DecSyncCC) on Android) store calendar/contact data in a shared directory.
2. **Syncthing** syncs that directory to your Home Assistant at `/share/decsync`.
3. **This add-on** serves the data over CalDAV/CardDAV on port 5232.
4. **Any client** (Thunderbird, iOS Calendar, DAVx5, GNOME Calendar, etc.) connects to Radicale and can read/write your calendars and contacts.
5. Changes flow back through DecSync to all your devices.

## Quick start

1. Install the add-on from the add-on store.
2. Ensure your DecSync directory is synced to `/share/decsync` (with `calendars/`, `contacts/`, etc. inside it).
3. Start the add-on.
4. Open `http://<your-ha-ip>:5232` in a browser — log in with any username.
5. Your DecSync calendars should appear automatically.

## Authentication

- **`none`** (default): Any username/password is accepted. Fine for local-only use.
- **`htpasswd`**: Only configured users can log in. Set usernames and passwords in the add-on options.

See [DOCS.md](DOCS.md) for full configuration details, client setup guides, and troubleshooting.
