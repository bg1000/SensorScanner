from threading import Timer
from threading import Lock

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
  
    def __init__(self, config):
        self.config = config
        self.sensors = []
        self.timer = RepeatTimer(self.config["scan_interval"], tick)
    def tick():
        for sensor = self.sensors:
            sensor.counter += 1
            if sensor.counter = sensor.scan_count:
                sensor.counter = 0
                sensor.read()



class sensor(object):
    def __init__(self, config):
        self.config = config
        self.scan_count = self.config["scan_count"]
        self.counter = 0
    
    def read():
        pass

class DHT_type(sensor_type)
    
    def __init__(self, config):
        super().__init__(config)
        for sensor in config.["sensors"]:
            self.sensors.append(DHT)


class DHT(sensor)
    def __init__(self, config):
        super().__init__(config)

        if self.config["type"] == "DHT22":
            self.type = Adafruit_DHT.DHT22
        elif self.config["type"] == "DHT11":
            self.type = Adafruit_DHT.DHT11
        self.gpio = self.config["gpio"]
        self.temperature_topic = self.config["temperature_topic"]
        self.humidity_topic = self.config["humidity_topic"]


    def read():
        humidity, temperature = Adafruit_DHT.read_retry(self.type, self.gpio)
        humidity = round(humidity,1)
        temperature = round((temperature * 9.0 / 5.0)+ 32.0,1)
        #
        # Timer is a subclass of thread
        # We are going to assume that Paho is not thread safe 
        # and use a lock while publishing mqtt messages
        #
        with mqtt_lock:
            if humidity is not None and temperature is not None:
                logging.info(str('Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(temperature, humidity)))
                client.publish(self.temperature_topic, temperature)
                client.publish(self.humidity_topic, humidity)
            else:
                logging.warning(str(datetime.datetime.now()) + 'Failed to get reading from DHT sensor')
