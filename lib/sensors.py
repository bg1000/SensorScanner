from threading import Timer
from threading import Lock
import logging
import Adafruit_DHT

# from:
# https://stackoverflow.com/questions/12435211/python-threading-timer-repeat-function-every-n-seconds
# answer # 16
# This creates a subclass of timer and overwrites the run method which can be seen here
# https://hg.python.org/cpython/file/2.7/Lib/threading.py#l1079 (probably not the right version)
#
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class sensor_type(object):
  
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue
        self.sensors = []
        self.timer = RepeatTimer(self.config["scan_interval"], self.tick)
    def tick(self):
        for sensor in self.sensors:
            sensor.counter += 1
            if sensor.counter == sensor.scan_count:
                sensor.counter = 0
                sensor.read()



class sensor(object):
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue
        self.scan_count = self.config["scan_count"]
        self.counter = 0
    
    def read():
        pass

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
        message1 = {}
        message2 = {}
        if humidity is not None and temperature is not None:
            humidity = round(humidity,1)
            temperature = round((temperature * 9.0 / 5.0)+ 32.0,1)
            logging.debug(str('Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(temperature, humidity)))
            if not self.queue.full():
                message1["topic"] = self.temperature_topic
                message1["payload"] = temperature
                self.queue.put(message1)
            else:
                logging.warning("The queue is full.  Sensor reading discarded.")
            if not self.queue.full():
                message2["topic"] = self.humidity_topic
                message2["payload"] = humidity
                self.queue.put(message2)
            else:
                logging.warning("The queue is full.  Sensor reading discarded.")
        else:
            logging.warning('Failed to get reading from DHT sensor')
