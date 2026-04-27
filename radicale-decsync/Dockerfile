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
RUN pip3 install --no-cache-dir \
    "setuptools<81" \
    radicale==3.2.3 \
    bcrypt \
    passlib \
    radicale_storage_decsync==2.1.0

# Copy entrypoint script
COPY run.sh /
RUN chmod a+x /run.sh

ENTRYPOINT []
CMD [ "/run.sh" ]

LABEL \
    io.hass.version="1.0.2" \
    io.hass.type="addon" \
    io.hass.arch="amd64|aarch64"
