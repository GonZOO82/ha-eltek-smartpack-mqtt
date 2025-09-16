import os
import time
import json
import paho.mqtt.client as mqtt
from easysnmp import Session, EasySNMPError

# --- Konfiguráció ---
SNMP_HOST = os.getenv('SNMP_HOST')
SNMP_PORT = int(os.getenv('SNMP_PORT', 161))
SNMP_COMMUNITY_PUBLIC = os.getenv('SNMP_COMMUNITY_PUBLIC', 'public')
SNMP_COMMUNITY_PRIVATE = os.getenv('SNMP_COMMUNITY_PRIVATE', 'private')
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 15))

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')

DEVICE_ID = "eltek_smartpack"
DEVICE_NAME = "ELTEK Smartpack"
DEVICE_MANUFACTURER = "GonZOO"
DEVICE_MODEL = "ELTEK Smartpack"

# --- Entitások definíciója ---
ENTITIES = {
    # Szenzorok (csak olvasható)
    "akkumulator_feszultseg": {"type": "sensor", "name": "Akkumulátor Feszültség", "oid": "1.3.6.1.4.1.12148.9.3.2.0", "unit": "V", "device_class": "voltage", "state_class": "measurement", "transform": lambda x: round(float(x) * 0.01, 2)},
    "akkumulator_aram": {"type": "sensor", "name": "Akkumulátor Áram", "oid": "1.3.6.1.4.1.12148.9.3.3.0", "unit": "A", "device_class": "current", "state_class": "measurement"},
    "akkumulator_homerseklet": {"type": "sensor", "name": "Akkumulátor Hőmérséklet", "oid": "1.3.6.1.4.1.12148.9.3.4.0", "unit": "°C", "device_class": "temperature", "state_class": "measurement"},
    # ... további szenzorok ...
    "toltesi_aram_limit_ertek": {"type": "sensor", "name": "Töltési Áram Limit Érték", "oid": "1.3.6.1.4.1.12148.9.3.7.0", "unit": "A", "device_class": "current", "state_class": "measurement"},
    "float_tolto_feszultseg_ertek": {"type": "sensor", "name": "Float Töltő Feszültség Érték", "oid": "1.3.6.1.4.1.12148.9.3.9.0", "unit": "V", "device_class": "voltage", "state_class": "measurement", "transform": lambda x: round(float(x) * 0.01, 2)},
    "boost_tolto_feszultseg_ertek": {"type": "sensor", "name": "Boost Töltő Feszültség Érték", "oid": "1.3.6.1.4.1.12148.9.3.10.0", "unit": "V", "device_class": "voltage", "state_class": "measurement", "transform": lambda x: round(float(x) * 0.01, 2)},
    "toltesi_statusz": {"type": "sensor", "name": "Töltési Státusz", "oid": "1.3.6.1.4.1.12148.9.2.2.0", "community": "private", "transform": lambda x: {'0': 'Float (feszültség szabályozott)','1': 'Float (hőmérséklet kompenzált)','2': 'Boost','3': 'Battery Test'}.get(x, f'Ismeretlen ({x})')},

    # Kapcsolók (írható/olvasható)
    "toltesi_aram_limit_kapcsolo": {"type": "switch", "name": "Töltési Áram Limit Kapcsoló", "oid": "1.3.6.1.4.1.12148.9.3.6.0", "payload_on": "1", "payload_off": "0", "community": "private"},
    "boost_toltes_kapcsolo": {"type": "switch", "name": "Boost Töltés Kapcsoló", "oid": "1.3.6.1.4.1.12148.9.3.16.0", "payload_on": "1", "payload_off": "2", "state_oid": "1.3.6.1.4.1.12148.9.2.2.0", "state_on": "2", "state_off": "0", "community": "private"},

    # Beállítható értékek (Number)
    "float_feszultseg_beallitas": {"type": "number", "name": "Float Feszültség Beállítás", "oid": "1.3.6.1.4.1.12148.9.3.9.0", "unit": "V", "device_class": "voltage", "min": 48, "max": 58, "step": 0.1, "transform_set": lambda x: int(float(x) * 100), "community": "private"},
    "boost_feszultseg_beallitas": {"type": "number", "name": "Boost Feszültség Beállítás", "oid": "1.3.6.1.4.1.12148.9.3.10.0", "unit": "V", "device_class": "voltage", "min": 48, "max": 59, "step": 0.1, "transform_set": lambda x: int(float(x) * 100), "community": "private"},
    "aram_limit_beallitas": {"type": "number", "name": "Áram Limit Beállítás", "oid": "1.3.6.1.4.1.12148.9.3.7.0", "unit": "A", "device_class": "current", "min": 0, "max": 100, "step": 1, "community": "private"},
}

# --- SNMP Funkciók ---
def snmp_get(session, oid):
    try:
        item = session.get(oid)
        return item.value
    except EasySNMPError as e:
        print(f"Hiba az SNMP GET során ({oid}): {e}")
        return None

def snmp_set(session, oid, value, snmp_type='i'):
    try:
        session.set(oid, value, snmp_type)
        return True
    except EasySNMPError as e:
        print(f"Hiba az SNMP SET során ({oid}): {e}")
        return False

# --- MQTT Callback Funkciók ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Sikeresen csatlakozva az MQTT brókerhez!")
        setup_mqtt_entities(client)
        # Feliratkozás a parancs témakörökre
        for entity_id, config in ENTITIES.items():
            if config["type"] in ["switch", "number"]:
                command_topic = f"homeassistant/{config['type']}/{DEVICE_ID}_{entity_id}/set"
                client.subscribe(command_topic)
                print(f"Feliratkozva a parancs témakörre: {command_topic}")
    else:
        print(f"MQTT csatlakozás sikertelen, kód: {rc}")

def on_message(client, userdata, msg):
    print(f"MQTT üzenet érkezett a témakörre: {msg.topic}")
    payload = msg.payload.decode()

    # Keresés az entitások között a parancs témakör alapján
    for entity_id, config in ENTITIES.items():
        if config["type"] in ["switch", "number"]:
            command_topic = f"homeassistant/{config['type']}/{DEVICE_ID}_{entity_id}/set"
            if msg.topic == command_topic:
                print(f"Parancs a '{config['name']}' entitásnak: {payload}")

                community = config.get("community", "private")
                session = Session(hostname=SNMP_HOST, community=community, version=2, remote_port=SNMP_PORT, use_numeric=True)

                value_to_set = payload
                if config['type'] == 'switch':
                    value_to_set = config['payload_on'] if payload == 'ON' else config['payload_off']
                elif 'transform_set' in config:
                    value_to_set = config['transform_set'](payload)

                if snmp_set(session, config['oid'], value_to_set):
                    print("SNMP SET sikeres.")
                    # Visszajelzés az állapotról
                    state_topic = f"homeassistant/{config['type']}/{DEVICE_ID}_{entity_id}/state"
                    client.publish(state_topic, payload)
                else:
                    print("SNMP SET sikertelen.")
                break

# --- MQTT Entitás Létrehozás ---
def setup_mqtt_entities(client):
    device_info = {
        "identifiers": [DEVICE_ID],
        "name": DEVICE_NAME,
        "manufacturer": DEVICE_MANUFACTURER,
        "model": DEVICE_MODEL,
    }

    for entity_id, config in ENTITIES.items():
        component = config["type"]
        config_topic = f"homeassistant/{component}/{DEVICE_ID}_{entity_id}/config"
        state_topic = f"homeassistant/{component}/{DEVICE_ID}_{entity_id}/state"

        payload = {
            "name": config["name"],
            "unique_id": f"{DEVICE_ID}_{entity_id}",
            "device": device_info,
            "state_topic": state_topic,
        }

        if component == "sensor":
            if "unit" in config: payload["unit_of_measurement"] = config["unit"]
            if "device_class" in config: payload["device_class"] = config["device_class"]
            if "state_class" in config: payload["state_class"] = config["state_class"]

        elif component == "switch":
            payload["command_topic"] = f"homeassistant/{component}/{DEVICE_ID}_{entity_id}/set"
            payload["payload_on"] = "ON"
            payload["payload_off"] = "OFF"
            if "state_on" in config: payload["state_on"] = config["state_on"]
            if "state_off" in config: payload["state_off"] = config["state_off"]

        elif component == "number":
            payload["command_topic"] = f"homeassistant/{component}/{DEVICE_ID}_{entity_id}/set"
            if "unit" in config: payload["unit_of_measurement"] = config["unit"]
            if "device_class" in config: payload["device_class"] = config["device_class"]
            if "min" in config: payload["min"] = config["min"]
            if "max" in config: payload["max"] = config["max"]
            if "step" in config: payload["step"] = config["step"]

        client.publish(config_topic, json.dumps(payload), retain=True)
    print(f"'{config['name']}' entitás konfigurációja publikálva.")

# --- Fő Program ---
if __name__ == "__main__":
    if not all([SNMP_HOST, MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD]):
        print("FATAL: Hiányzó SNMP vagy MQTT konfiguráció! Ellenőrizd az add-on beállításait.")
        exit(1)

    # Csatlakozás az MQTT brókerhez
    # JAVÍTÁS: A legújabb, V2-es callback API használata
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
    except Exception as e:
        print(f"FATAL: Hiba az MQTT brókerhez való csatlakozás során: {e}")
        exit(1)

    client.loop_start()

    # SNMP session-ök létrehozása
    session_public = Session(hostname=SNMP_HOST, community=SNMP_COMMUNITY_PUBLIC, version=2, remote_port=SNMP_PORT, use_numeric=True)
    session_private = Session(hostname=SNMP_HOST, community=SNMP_COMMUNITY_PRIVATE, version=2, remote_port=SNMP_PORT, use_numeric=True)

    # Fő ciklus az adatok olvasására és publikálására
    while True:
        for entity_id, config in ENTITIES.items():
            if config["type"] in ["sensor", "switch"]: # A number entitások állapotát a parancsból frissítjük

                # Válasszuk ki a megfelelő community stringet
                community = config.get("community", "public")
                session = session_private if community == "private" else session_public

                # A kapcsolóknak lehet külön state OID-jük
                oid_to_read = config.get("state_oid", config["oid"])

                value = snmp_get(session, oid_to_read)

                if value is not None:
                    if "transform" in config:
                        value = config["transform"](value)

                    state_topic = f"homeassistant/{config['type']}/{DEVICE_ID}_{entity_id}/state"

                    # Kapcsolók állapotának leképezése ON/OFF-ra
                    if config["type"] == "switch" and "state_on" in config:
                        payload = "ON" if str(value) == str(config["state_on"]) else "OFF"
                    elif config["type"] == "switch": # Egyszerűbb kapcsoló
                        payload = "ON" if str(value) == str(config["payload_on"]) else "OFF"
                    else:
                        payload = value

                    client.publish(state_topic, payload)

        time.sleep(SCAN_INTERVAL)

