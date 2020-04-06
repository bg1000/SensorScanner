from threading import Timer
from copy import deepcopy
import logging
from sensor import RepeatTimer
import Adafruit_DHT
#
# sensor implmentation for the DHT11 and DHT22 temperature & humidity sensors
#
#
class DHT_type(sensor_type):
    
    def __init__(self, config, queue):
        super().__init__(config, queue)
        for sensor in config["sensors"]:
            self.sensors.append(DHT(sensor, queue))
        self.tick()    
        self.timer.start()


class DHT(sensor):
    def __init__(self, config, queue):
        super().__init__(config, queue)

        if self.config["type"] == "DHT22":
            self.type = Adafruit_DHT.DHT22
        elif self.config["type"] == "DHT11":
            self.type = Adafruit_DHT.DHT11
        self.gpio = self.config["gpio"]
        self.temperature_topic = self.config["temperature_topic"]
        self.humidity_topic = self.config["humidity_topic"]
      


    def read(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.type, self.gpio)
        message = {}
        if humidity is not None and temperature is not None:
            humidity = round(humidity,1)
            temperature = round((temperature * 9.0 / 5.0)+ 32.0,1)
            logging.debug(str('Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(temperature, humidity)))
            message["topic"] = self.temperature_topic
            message["payload"] = temperature
            try:
                self.queue.put(deepcopy(message))    
                message["topic"] = self.humidity_topic
                message["payload"] = humidity
                self.queue.put(deepcopy(message))
            except Queue.Full:
                logging.warning("The queue is full.  Sensor reading discarded.")    
        else:
            logging.warning('Failed to get reading from DHT sensor')
