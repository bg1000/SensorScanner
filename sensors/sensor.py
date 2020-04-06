from threading import Timer
from copy import deepcopy
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
#
# sensor_type and sensor are the base classes for implmenting a specific type of sensor
# For each type of sensor there will be one sensor_type subclass with a list of sensors subclasses.
# For example class DHT_type(sensor_type) has a list of class DHT(sensor)'s in self.sensors.
# To implement a new type of sensor:
# 1) copy the file template.py to an appropriate name and complete the ToDo's
# 2) make necessary entries on config.yaml
#
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
