from threading import Timer
from copy import deepcopy
import logging
import queue
from sensors.sensor import RepeatTimer # pylint: disable=import-error
from sensors.sensor import sensor # pylint: disable=import-error
from sensors.sensor import sensor_type # pylint: disable=import-error
import json
import Adafruit_DHT
#
# template sensor implmentation 
# replace "your_sensor" and modify indicated by comments
#
class your_sensor_type(sensor_type):
    
    def __init__(self, config, queue, global_discovery, discovery_prefix):
        #
        # Runs the base class intialization that applies to all sensors
        #
        super().__init__(config, queue, global_discovery, discovery_prefix)
        for sensor in config["sensors"]:
            self.sensors.append(your_sensor(sensor, queue))          
        #
        # If this sensor has some initialization (beyond what is done in the base class) that is done once and applies to all sensors
        # all sensors of this type(e.g. - intialize some library) then add it here.
        
        #
        # Leave this here to keep homeassistant mqtt discovery as an option.
        # If you don't want to use discovery set it to false on a per sensor basis
        # or globally in config.yaml
        super().send_discovery()                                                      
        # 
        # avoids having to wait for the timer to run before the first update
        #
        self.tick()
        #
        # start the repeating timer
        # 
        self.timer.start()

class your_sensor(sensor):
    message = {}
    def __init__(self, config, queue):
        #
        # runs the base class intialization that applies to all indivdual sensors
        #
        super().__init__(config, queue)
        #
        # add your code here to initialize each iondividual sensor of this type


    def read(self):
        #
        # This method takes a reading for individual sensor and puts it in the queue
        # to be sent to the mqtt broker
        #
        
        message = {}
        #
        # This is the queue message sent to the main thread. It needs to contain:
        # "topic": This is the mqtt (state) topic to use for the sensor.
        # "payload": This is the payload to write to the topic.  It is often json formatted
        # but can be anything.  If you used a value_template in your config the payload needs to match 
        # what is expected there.
        #
        payload = {}
        #
        # If you are using a json formated payload put it in this dictionary and then
        # use json.dumps(payload) to format the payload as shown below
        #
        # Add whatever code you need to get a reading from your sensor here,
        # do unit conversions, etc.
        #

        
  
        #
        # Then use this code or something similar to put the reading in the
        # queue so the main thread will publish it.
        # 
        message["topic"] = self.state_topic
        payload["your_reading"] = some_value # <- change this
        # could be more than one value (e.g. - temperature and humidity)
        message["payload"] = json.dumps(payload)
        #
        # 1) Using deepcopy ensures that we get the intended message even if we send a second readiing before 
        # the first is taken out of the queue.
        # 2) If your are getting queue full warnings you can increase the queue size on the config file (assumming
        # there isn't some other problem you need to fix).
        #
        #
        try:
            self.queue.put(deepcopy(message))    
        except Queue.Full:
            logging.warning("The queue is full.  Sensor reading discarded.") 
