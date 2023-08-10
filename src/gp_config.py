import utime
import ubinascii
import ure
import ujson
from ucryptolib import aes


class GrowplantConfig:

    def __init__(self, filename):
        self.filename = filename
        self.thing_id = None
        self.thing_hostname = ""
        self.thing_sensors = []
        self.monitoring = False
        self.mqtt_url = ""
        self.mqtt_login = ""
        self.mqtt_password = ""
        self.wifi_ssid = ""
        self.wifi_password = ""
        self._parse()

    def _decrypt_password(self, encrypted_pass):
        key = 'GrowplantEncrypt'
        iv = 'encryptionIntVec'
        MODE_CBC = 2
        cipher = aes(key, MODE_CBC, iv)
        encrypted = ubinascii.a2b_base64(encrypted_pass)
        decrypted = cipher.decrypt(encrypted).decode('UTF-8')
        decrypted = ure.sub(r'\\.*', '', repr(decrypted)
                           ).replace('\'', '')  # Remove special chars

        return decrypted

    def _parse(self):
        try:
            with open(self.filename) as fp:
                json = ujson.loads(fp.read())
                self.thing_id = json["thing_id"]
                self.thing_hostname = json["thing_hostname"]
                self.wifi_ssid = json["wifi"]["ssid"]
                self.wifi_password = self._decrypt_password(
                    json["wifi"]["password"])
                self.monitoring = bool(json["thing_monitoring"])
                self.mqtt_url = json["mqtt"]["url"]
                self.mqtt_login = json["mqtt"]["login"]
                self.mqtt_password = self._decrypt_password(
                    json["mqtt"]["password"])
                self.thing_sensors = json["thing_sensors"]
        except Exception as e:
            print("Parsing error : {}".format(e))
            utime.sleep(2)
            # machine.reset()
