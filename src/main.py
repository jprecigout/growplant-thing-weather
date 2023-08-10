import gc
import umachine
import ujson
import dht
from time import sleep
from gp_config import GrowplantConfig
from gp_network import GrowplantNetwork


# Mem free
gc.collect()
gc.enable()
# gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

# Config
print("Reading config...")
gp_config = GrowplantConfig("secrets.json")


# Network
print("Init network...")
network = GrowplantNetwork(gp_config.thing_hostname, gp_config.wifi_ssid, gp_config.wifi_password, gp_config.monitoring,
                               gp_config.mqtt_url, gp_config.mqtt_login, gp_config.mqtt_password)
network.connect_all()

# Main loop
print("Start task...")

thing_id = 9
sensor_id = 10
pin = 4
temp_sensor = dht.DHT11(umachine.Pin(pin))

while True:
    try:
        temp_sensor.measure()
        temp = temp_sensor.temperature()
        hum = temp_sensor.humidity()
    except Exception as error:
        print("Error reading temp : {}".format(error))

    try:
        msgTemp = {'thingId': thing_id,
                            'sensorId': sensor_id,
                            'status': temp,
                            'topic': "sensors/activity",
                            'name': 'temp'}
        print("msgOn : {}".format(msgTemp))
        network.publish("sensors/activity", ujson.dumps(msgTemp))
        msgHum = {'thingId': thing_id,
                            'sensorId': sensor_id,
                            'status': hum,
                            'topic': "sensors/activity",
                            'name': 'hum'}
        print("msgOn : {}".format(msgHum))
        network.publish("sensors/activity", ujson.dumps(msgimport machioHum))
    except Exception as error:
        print("Error sending hum : {}".format(error))

    print("sleep...")

    sleep(10) #10s # pour debug

# print("deep sleep...")
# # umachine.deepsleep(900000) #15 min
# umachine.deepsleep(60*1000) #60s
