#!/usr/bin/with-contenv bashio

# Alapvető hibakeresés: Ennek mindenképpen meg kell jelennie a logban
echo "[DEBUG] run.sh script started. Setting log level..."

# Garantáljuk, hogy az INFO szintű logok láthatóak legyenek
bashio::log.level 'info'

bashio::log.info "--- Kezdődik a konfiguráció beolvasása ---"

# Konfigurációs változók beolvasása alapértelmezett értékekkel
export SNMP_HOST=$(bashio::config 'snmp_host')
export SNMP_PORT=$(bashio::config 'snmp_port' 161)
export SNMP_COMMUNITY_PUBLIC=$(bashio::config 'community_public' 'public')
export SNMP_COMMUNITY_PRIVATE=$(bashio::config 'community_private' 'private')
export SCAN_INTERVAL=$(bashio::config 'scan_interval' 15)

# MQTT beállítások
if bashio::services.available "mqtt"; then
    bashio::log.info "Hivatalos Home Assistant MQTT szolgáltatás megtalálva, használat..."
    export MQTT_HOST=$(bashio::services mqtt "host")
    export MQTT_PORT=$(bashio::services mqtt "port")
    export MQTT_USER=$(bashio::services mqtt "username")
    export MQTT_PASSWORD=$(bashio::services mqtt "password")
else
    bashio::log.info "Hivatalos MQTT szolgáltatás nem található. Manuális beállítások használata..."
    export MQTT_HOST=$(bashio::config 'mqtt_host')
    export MQTT_PORT=$(bashio::config 'mqtt_port')
    export MQTT_USER=$(bashio::config 'mqtt_user')
    export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
fi

bashio::log.info "--- HIBAKERESÉSI INFORMÁCIÓK ---"
bashio::log.info "SNMP Host: ${SNMP_HOST}"
bashio::log.info "SNMP Port: ${SNMP_PORT}"
bashio::log.info "MQTT Host: ${MQTT_HOST}"
bashio::log.info "MQTT Port: ${MQTT_PORT}"
bashio::log.info "MQTT User: ${MQTT_USER}"
# A jelszót biztonsági okokból nem íratjuk ki, de ellenőrizzük, hogy létezik-e
if [ -n "${MQTT_PASSWORD}" ]; then
    bashio::log.info "MQTT Password: (megadva)"
else
    bashio::log.info "MQTT Password: (nincs megadva)"
fi
bashio::log.info "---------------------------------"

# Indítjuk a Python scriptet
bashio::log.info "ELTEK Smartpack SNMP to MQTT Bridge indítása..."
python3 /eltek_mqtt_bridge.py

