FROM python:3.12-alpine

# Install glibc compatibility layer for libdecsync native lib, plus htpasswd
RUN apk add --no-cache \
    bash \
    jq \
    apache2-utils \
    gcompat \
    libstdc++ \
    curl

# Install Radicale and the DecSync storage plugin
# NOTE: setuptools is pinned to <81 because radicale_storage_decsync 2.1.0
# relies on the legacy `pkg_resources` entry-point mechanism, which was
# removed in setuptools 81+.  Bump this pin only after the plugin drops
# its pkg_resources dependency.
# NOTE: Radicale >= 3.6.0 replaced the stale `passlib` dependency with
# `libpass >= 1.9.3` for htpasswd bcrypt hashing.
RUN pip3 install --no-cache-dir \
    "setuptools<81" \
    radicale==3.8.0 \
    bcrypt \
    "libpass>=1.9.3" \
    radicale_storage_decsync==2.1.0

# Copy entrypoint script
COPY run.sh /
RUN chmod a+x /run.sh

ENTRYPOINT []
CMD [ "/run.sh" ]

LABEL \
    io.hass.version="1.0.3" \
    io.hass.type="addon" \
    io.hass.arch="amd64|aarch64"
