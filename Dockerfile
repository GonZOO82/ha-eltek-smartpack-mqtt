ARG BUILD_FROM
FROM ${BUILD_FROM}

# Telepítjük a build-hez szükséges C library-ket és a Pythont
# A python3-dev csomag tartalmazza a "Python.h" fájlt, ami a fordításhoz kell
RUN apk add --no-cache \
    build-base \
    python3 \
    python3-dev \
    py3-pip \
    net-snmp-dev \
    gcc \
    musl-dev

# Telepítjük a Python library-ket pip-pel
# Az --break-system-packages kapcsoló szükséges a Home Assistant alaprendszerben
RUN pip3 install --no-cache-dir --break-system-packages \
    paho-mqtt \
    easysnmp

# Másoljuk az add-on fájlokat a konténerbe
COPY run.sh /
COPY eltek_mqtt_bridge.py /

# Futtathatóvá tesszük a run.sh scriptet
RUN chmod a+x /run.sh

# A run.sh scriptet indítjuk, ami beállítja a környezetet és elindítja a Pythont
CMD [ "/run.sh" ]

