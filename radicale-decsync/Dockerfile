ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Install Python, pip, and glibc compatibility layer for libdecsync native lib
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-bcrypt \
    py3-passlib \
    apache2-utils \
    gcompat \
    libstdc++

# Install Radicale and the DecSync storage plugin
RUN pip3 install --no-cache-dir --break-system-packages \
    radicale==3.2.3 \
    radicale_storage_decsync==2.1.0

# Radicale data directory (created at runtime in run.sh via /data volume)
RUN mkdir -p /data/collections

# Copy entrypoint script
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

LABEL \
    io.hass.version="1.0.0" \
    io.hass.type="addon" \
    io.hass.arch="amd64|aarch64"
