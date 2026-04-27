#!/bin/bash
set -e

# ==============================================================================
# Radicale DecSync Add-on for Home Assistant
# Starts the Radicale CalDAV/CardDAV server with DecSync storage backend
# ==============================================================================

CONFIG_PATH="/data/options.json"
RADICALE_CONFIG="/data/radicale.conf"
RADICALE_DATA="/data/collections"
HTPASSWD_FILE="/data/htpasswd"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

# --- Read add-on options ------------------------------------------------------
if [ ! -f "${CONFIG_PATH}" ]; then
    log "FATAL: Options file ${CONFIG_PATH} not found!"
    exit 1
fi

decsync_dir="$(jq --raw-output '.decsync_dir // "/share/decsync"' "${CONFIG_PATH}")"
auth_type="$(jq --raw-output '.auth_type // "none"' "${CONFIG_PATH}")"
log_level="$(jq --raw-output '.log_level // "info"' "${CONFIG_PATH}")"

log "Starting Radicale DecSync add-on..."
log "  DecSync directory : ${decsync_dir}"
log "  Auth type         : ${auth_type}"
log "  Log level         : ${log_level}"

# --- Ensure directories exist ------------------------------------------------
mkdir -p "${RADICALE_DATA}"
mkdir -p "${decsync_dir}" 2>/dev/null || log "WARNING: Could not create DecSync directory '${decsync_dir}'"

# --- Build htpasswd file if auth_type is htpasswd ----------------------------
if [ "${auth_type}" = "htpasswd" ]; then
    log "Configuring htpasswd authentication..."
    : > "${HTPASSWD_FILE}"

    user_count="$(jq '.users | length' "${CONFIG_PATH}")"
    for i in $(seq 0 $((user_count - 1))); do
        username="$(jq --raw-output ".users[${i}].username" "${CONFIG_PATH}")"
        password="$(jq --raw-output ".users[${i}].password" "${CONFIG_PATH}")"
        htpasswd -bB "${HTPASSWD_FILE}" "${username}" "${password}"
        log "  Added user: ${username}"
    done
fi

# --- Generate Radicale configuration -----------------------------------------
cat > "${RADICALE_CONFIG}" <<CONF
[server]
hosts = 0.0.0.0:5232

[auth]
CONF

if [ "${auth_type}" = "htpasswd" ]; then
    cat >> "${RADICALE_CONFIG}" <<CONF
type = htpasswd
htpasswd_filename = ${HTPASSWD_FILE}
htpasswd_encryption = bcrypt
CONF
else
    cat >> "${RADICALE_CONFIG}" <<CONF
type = none
CONF
fi

cat >> "${RADICALE_CONFIG}" <<CONF

[storage]
type = radicale_storage_decsync
filesystem_folder = ${RADICALE_DATA}
decsync_dir = ${decsync_dir}

[logging]
level = ${log_level}

[rights]
type = authenticated
CONF

log "Generated Radicale configuration:"
while IFS= read -r line; do
    log "  ${line}"
done < "${RADICALE_CONFIG}"

# --- Start Radicale ----------------------------------------------------------
log "Launching Radicale server on port 5232..."
exec python3 -m radicale --config "${RADICALE_CONFIG}"
