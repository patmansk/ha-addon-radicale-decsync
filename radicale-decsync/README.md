# Radicale DecSync Add-on for Home Assistant

A Home Assistant add-on that runs a [Radicale](https://radicale.org) CalDAV/CardDAV server with [DecSync](https://github.com/39aldo39/DecSync) storage integration.

This allows you to access DecSync-synchronized calendars and contacts via any CalDAV/CardDAV client (Thunderbird, GNOME Calendar, iOS Calendar, DAVx5, etc.) directly from your Home Assistant instance.

## How it works

1. **DecSync** synchronizes calendar/contact data across devices using a shared directory (e.g., via [Syncthing](https://syncthing.net)).
2. **Radicale** serves that data over the CalDAV/CardDAV protocol.
3. Any CalDAV/CardDAV client can connect to Radicale to read and write calendars and contacts.
4. Changes made through CalDAV clients are written back to the DecSync directory and synced to all other devices.

## Quick start

1. Install the add-on.
2. Make sure your DecSync directory is accessible under `/share/decsync` (e.g., synced there via the Syncthing add-on).
3. Start the add-on.
4. Open the Web UI or connect a CalDAV client to `http://<your-ha-ip>:5232`.

See [DOCS.md](DOCS.md) for full configuration details.
