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
    i=0
    while [ "${i}" -lt "${user_count}" ]; do
        username="$(jq --raw-output ".users[${i}].username" "${CONFIG_PATH}")"
        password="$(jq --raw-output ".users[${i}].password" "${CONFIG_PATH}")"
        printf '%s\n' "${password}" | htpasswd -iB "${HTPASSWD_FILE}" "${username}"
        log "  Added user: ${username}"
        i=$((i + 1))
    done
fi

# --- Generate Radicale configuration -----------------------------------------
{
    echo '[server]'
    echo 'hosts = 0.0.0.0:5232'
    echo ''
    echo '[auth]'
    if [ "${auth_type}" = "htpasswd" ]; then
        echo 'type = htpasswd'
        echo "htpasswd_filename = ${HTPASSWD_FILE}"
        echo 'htpasswd_encryption = bcrypt'
    else
        echo 'type = none'
    fi
    echo ''
    echo '[storage]'
    echo 'type = radicale_storage_decsync'
    echo "filesystem_folder = ${RADICALE_DATA}"
    echo "decsync_dir = ${decsync_dir}"
    echo ''
    echo '[logging]'
    echo "level = ${log_level}"
    if [ "${auth_type}" = "htpasswd" ]; then
        echo ''
        echo '[rights]'
        echo 'type = radicale.rights.authenticated'
    fi
} > "${RADICALE_CONFIG}"

log "Generated Radicale configuration:"
while IFS= read -r line; do
    log "  ${line}"
done < "${RADICALE_CONFIG}"

# --- Apply Radicale 3.8.0 compatibility patch (if present) ---------------
if [ -f /patch_compatibility.py ]; then
    log "Applying DecSync/Radicale compatibility patch..."
    python3 /patch_compatibility.py || log "WARNING: Compatibility patch failed (non-fatal)"
fi

# --- Start Radicale ----------------------------------------------------------
log "Launching Radicale server on port 5232..."
exec python3 -m radicale --config "${RADICALE_CONFIG}"
