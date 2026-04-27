#!/usr/bin/with-contenv bashio
# ==============================================================================
# Radicale DecSync Add-on for Home Assistant
# Starts the Radicale CalDAV/CardDAV server with DecSync storage backend
# ==============================================================================

declare decsync_dir
declare auth_type
declare log_level

# --- Read add-on options ------------------------------------------------------
decsync_dir=$(bashio::config 'decsync_dir')
auth_type=$(bashio::config 'auth_type')
log_level=$(bashio::config 'log_level')

bashio::log.info "Starting Radicale DecSync add-on..."
bashio::log.info "  DecSync directory : ${decsync_dir}"
bashio::log.info "  Auth type         : ${auth_type}"
bashio::log.info "  Log level         : ${log_level}"

# --- Ensure directories exist ------------------------------------------------
mkdir -p /data/radicale/collections
mkdir -p "${decsync_dir}" 2>/dev/null || true

# --- Build htpasswd file if auth_type is htpasswd ----------------------------
if [ "${auth_type}" = "htpasswd" ]; then
    bashio::log.info "Configuring htpasswd authentication..."
    HTPASSWD_FILE="/config/radicale/users"
    : > "${HTPASSWD_FILE}"

    for entry in $(bashio::config 'users|keys'); do
        username=$(bashio::config "users[${entry}].username")
        password=$(bashio::config "users[${entry}].password")
        htpasswd -bB "${HTPASSWD_FILE}" "${username}" "${password}"
        bashio::log.info "  Added user: ${username}"
    done
fi

# --- Generate Radicale configuration -----------------------------------------
cat > /config/radicale/config <<EOF
[server]
hosts = 0.0.0.0:5232

[auth]
EOF

if [ "${auth_type}" = "htpasswd" ]; then
    cat >> /config/radicale/config <<EOF
type = htpasswd
htpasswd_filename = /config/radicale/users
htpasswd_encryption = bcrypt
EOF
else
    cat >> /config/radicale/config <<EOF
type = none
EOF
fi

cat >> /config/radicale/config <<EOF

[storage]
type = radicale_storage_decsync
filesystem_folder = /data/radicale/collections
decsync_dir = ${decsync_dir}

[logging]
level = ${log_level}

[rights]
type = owner_only
EOF

bashio::log.info "Radicale configuration written to /config/radicale/config"

# --- Start Radicale ----------------------------------------------------------
bashio::log.info "Launching Radicale server on port 5232..."
exec python3 -m radicale --config /config/radicale/config
