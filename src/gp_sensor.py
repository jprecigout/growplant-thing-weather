import dht
import machine
import uasyncio
import ujson
import onewire
import ds18x20
from neopixel import NeoPixel
from sensor_lib.si7021 import Si7021


# Abstract Class do not instanciate
class AbstractSensor:

    def __init__(self, thing_id, mqtt_client, config_sensor):
        self.mqtt_client = mqtt_client
        self.sensor_id = config_sensor["id"]
        self.thing_id = thing_id
        self.topic = config_sensor["topic"]

        self.pin = None
        self.period_on_s = None
        self.period_off_s = None
        self.sensor = None

        for config in config_sensor["configs"]:
            if config["name"] == "period_on":
                self.period_on_s = int(config["value"])
            if config["name"] == "period_off":
                self.period_off_s = int(config["value"])
            if config["name"] == "pin":
                self.pin = int(config["value"])

    async def run(self):
        raise NotImplementedError("Subclass must implement abstract method")


class PumpSensor(AbstractSensor):

    def __init__(self, thing_id, mqtt_client, config_sensor, network):
        super().__init__(thing_id, mqtt_client, config_sensor)

        self.sensor = machine.Pin(self.pin, machine.Pin.OUT)
        self.network = network

    async def run(self):
        while True:
            try:
                self.sensor.value(0)
            except Exception as error:
                print("Error writing pump : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msgOn = {'thingId': self.thing_id,
                             'sensorId': self.sensor_id,
                             'status': 0,
                             'topic': self.topic,
                             'name': 'pump'}
                    print("msgOn : {}".format(msgOn))
                    # await self.mqtt_client.publish(self.topic, ujson.dumps(msgOn), qos=1)
                    #self.mqtt_client.publish(self.topic, ujson.dumps(msgOn))
                    self.network.publish(self.topic, ujson.dumps(msgOn))
                except Exception as error:
                    print("Error sending pump onMessage : {}".format(error))

            await uasyncio.sleep(self.period_on_s)

            try:
                self.sensor.value(1)
            except Exception as error:
                print("Error writing pump : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msgOff = {'thingId': self.thing_id,
                              'sensorId': self.sensor_id,
                              'status': 1,
                              'topic': self.topic,
                              'name': 'pump'}
                    print("msgOff : {}".format(msgOff))
                    # await self.mqtt_client.publish(self.topic, ujson.dumps(msgOff), qos=1)
                    #self.mqtt_client.publish(self.topic, ujson.dumps(msgOff))
                    self.network.publish(self.topic, ujson.dumps(msgOff))
                except Exception as error:
                    print("Error sending pump offMessage: {}".format(error))

            await uasyncio.sleep(self.period_off_s)


class LightSensor(AbstractSensor):

    def __init__(self, thing_id, mqtt_client, config_sensor, network):
        super().__init__(thing_id, mqtt_client, config_sensor)

        self.color = None
        self.number_led = 0
        self.network = network

        for config in config_sensor["configs"]:
            if config["name"] == "color":
                self.color = tuple(
                    map(int, config["value"].replace(' ', '').replace('(', '').replace(')', '').split(',')))
            if config["name"] == "number_led":
                self.number_led = int(config["value"])

        self.sensor = NeoPixel(machine.Pin(
            self.pin, machine.Pin.OUT), self.number_led)

    def _clear(self):
        for i in range(self.number_led):
            self.sensor[i] = (0, 0, 0)
        self.sensor.write()

    def _set_color(self, rgb):
        for i in range(self.number_led):
            self.sensor[i] = rgb
        self.sensor.write()

    async def run(self):

        while True:
            try:
                # Set color
                self._set_color(self.color)
            except Exception as error:
                print("Error writing light onMessage : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msgOn = {'thingId': self.thing_id,
                             'sensorId': self.sensor_id,
                             'status': 0,
                             'topic': self.topic,
                             'name': 'light'}
                    print("msgOn : {}".format(msgOn))
                    self.network.publish(self.topic, ujson.dumps(msgOn))
                except Exception as error:
                    print("Error sending light onMessage : {}".format(error))

            await uasyncio.sleep(self.period_on_s)

            try:
                # Clear
                self._clear()
            except Exception as error:
                print("Error writing light offMessage : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msgOff = {'thingId': self.thing_id,
                              'sensorId': self.sensor_id,
                              'status': 0,
                              'topic': self.topic,
                              'name': 'light'}
                    print("msgOff : {}".format(msgOff))
                    # await self.mqtt_client.publish(self.topic, ujson.dumps(msgOff), qos=1)
                    #self.mqtt_client.publish(self.topic, ujson.dumps(msgOff))
                    self.network.publish(self.topic, ujson.dumps(msgOff))
                except Exception as error:
                    print("Error sending light offMessage : {}".format(error))

            await uasyncio.sleep(self.period_off_s)


class TempSensor(AbstractSensor):

    def __init__(self, thing_id, mqtt_client, config_sensor, network):
        super().__init__(thing_id, mqtt_client, config_sensor)

        self.scl = None
        self.sda = None
        self.network = network

        for config in config_sensor["configs"]:
            if config["name"] == "scl":
                self.scl = int(config["value"])
            if config["name"] == "sda":
                self.sda = int(config["value"])

        self._dht = (self.pin is not None)

        if self._dht:
            self.sensor = dht.DHT11(machine.Pin(self.pin))
        else:
            i2c = machine.I2C(scl=machine.Pin(self.scl),
                              sda=machine.Pin(self.sda))
            self.sensor = Si7021(i2c)

    async def run(self):
        while True:
            try:
                # Get temp & hum
                if self._dht:
                    self.sensor.measure()
                    temp = self.sensor.temperature()
                    hum = self.sensor.humidity()
                else:
                    self.sensor.reset()
                    temp = self.sensor.temperature
                    hum = self.sensor.relative_humidity
            except Exception as error:
                print("Error reading temp : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msgTemp = {'thingId': self.thing_id,
                               'sensorId': self.sensor_id,
                               'status': temp,
                               'topic': self.topic,
                               'name': 'temp'}
                    print("msgOn : {}".format(msgTemp))
                    # await self.mqtt_client.publish(self.topic, ujson.dumps(msgTemp), qos=1)
                    # self.mqtt_client.publish(self.topic, ujson.dumps(msgTemp))
                    self.network.publish(self.topic, ujson.dumps(msgTemp))
                except Exception as error:
                    print("Error sending temp : {}".format(error))

                try:
                    msgHum = {'thingId': self.thing_id,
                              'sensorId': self.sensor_id,
                              'status': hum,
                              'topic': self.topic,
                              'name': 'hum'}
                    print("msgOn : {}".format(msgHum))
                    # await self.mqtt_client.publish(self.topic, ujson.dumps(msgHum), qos=1)
                    # self.mqtt_client.publish(self.topic, ujson.dumps(msgHum))
                    self.network.publish(self.topic, ujson.dumps(msgHum))
                except Exception as error:
                    print("Error sending hum : {}".format(error))

            await uasyncio.sleep(self.period_off_s)


class TempWaterSensor(AbstractSensor):

    def __init__(self, thing_id, mqtt_client, config_sensor, network):
        super().__init__(thing_id, mqtt_client, config_sensor)
        self.network = network
        self.sensor = ds18x20.DS18X20(onewire.OneWire(machine.Pin(self.pin)))

    async def run(self):
        address = self.sensor.scan()
        while True:
            try:
                # Read the temp
                self.sensor.convert_temp()
                await uasyncio.sleep_ms(750)
                # TODO améliorer Si address a plusieurs sonde il faut faire autrement boucler
                temp = self.sensor.read_temp(address[0])

            except Exception as error:
                print("Error reading temp_water : {}".format(error))

            if self.mqtt_client is not None:
                try:
                    msg = {'thingId': self.thing_id,
                           'sensorId': self.sensor_id,
                           'status': temp,
                           'topic': self.topic,
                           'name': 'temp_water'}
                    print("msgOn : {}".format(msg))
                    self.network.publish(self.topic, ujson.dumps(msg))
                except Exception as error:
                    print("Error sending temp_water : {}".format(error))

            await uasyncio.sleep(self.period_off_s)
