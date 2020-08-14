# Standard Library imports
from copy import deepcopy
import json
import logging
import queue
from threading import Timer


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
  
    def __init__(self, config, queue, global_discovery, discovery_prefix):
        self.config = config
        self.queue = queue
        self.global_discovery = global_discovery
        self.sensors = []
        self.timer = RepeatTimer(self.config["scan_interval"], self.tick)
        self.discovery_prefix = discovery_prefix
    def tick(self):
        for sensor in self.sensors:
            sensor.counter += 1
            if sensor.counter == sensor.scan_count:
                sensor.counter = 0
                sensor.read()
    def send_discovery(self):
        message = {}
        for sensor in self.sensors:
            if self.global_discovery and sensor.discovery:
                
                for item in sensor.discovery_info:
                    #
                    # make a copy so we can remove topic, qos, retain and send
                    # everything else as the payload
                    # without altering original config in case
                    # we need it later.
                    #
                    discovery_info = deepcopy(item)
                    message["topic"] = self.discovery_prefix + discovery_info["discovery_topic"]
                    message["qos"] = discovery_info["qos"]
                    message["retain"] = True # always retain discovery info
                    del discovery_info["discovery_topic"]
                    del discovery_info["qos"]
                    message["payload"] = json.dumps(discovery_info)
                    try:
                        self.queue.put(deepcopy(message))
                    except queue.Full:
                        logging.critical ("Queue is full. Unable to send discovery info")      



class sensor(object):
    def __init__(self, config, queue, discovery_prefix):
        self.config = config
        self.queue = queue
        self.scan_count = self.config["scan_count"]
        self.counter = 0
        self.discovery = config["discovery"]
        self.state_topic = discovery_prefix + config["state_topic"]
        self.discovery_info = config["discovery_info"]
        self.qos = config["qos"]
        self.retain = config["retain"] 
    def read(self):
        pass

