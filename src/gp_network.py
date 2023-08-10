import utime
import usocket
import ubinascii
import umachine
import network
from umqtt.robust import MQTTClient

class GrowplantNetwork:

    def __init__(self, hostname, network_ssid, network_password, monitoring=False, mqtt_server_addr="", mqtt_login="", mqtt_password=""):
        self.hostname = hostname
        self.network_ssid = network_ssid
        self.network_password = network_password
        self.monitoring = monitoring
        self.mqtt_server_addr = mqtt_server_addr
        self.mqtt_server_addr_ip = None
        self.mqtt_login = mqtt_login
        self.mqtt_password = mqtt_password
        self.mqtt_client = None
        self.wlan = network.WLAN(network.STA_IF)

    def connect_all(self):
        self.connect_network()
        if (self.monitoring is True):
            self._connect_mqtt()

    def connect_network(self):
        self.wlan.active(True)
        utime.sleep_us(100)
        # self.wlan.config(dhcp_hostname=self.hostname)
        self.wlan.connect(self.network_ssid, self.network_password)

        while self.wlan.isconnected() is False:
            pass
        print('Connection Network successful')

    def _connect_mqtt(self):
        self.mqtt_server_addr_ip = usocket.getaddrinfo(self.mqtt_server_addr, 1883)[0][-1][0]
        client_id = ubinascii.hexlify( umachine.unique_id())

        self.mqtt_client = MQTTClient(
            client_id, server=self.mqtt_server_addr_ip, user=self.mqtt_login, password=self.mqtt_password, port=1883, keepalive=60)
        self.mqtt_client.connect()
        print("Connected to MQTT broker : {}".format(self.mqtt_server_addr))

    def publish(self, topic, data):
        if self.wlan.isconnected() is False:
            print("Plus de wifi ... reconnect")
            self.connect_network()
            self.mqtt_client.reconnect()

        try:
            self.mqtt_client.publish(topic, data)
        except Exception as error:
            print("Error sending data : {}".format(error))
