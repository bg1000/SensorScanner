#!/usr/bin/python3

import time
import os
import RPi.GPIO as io
import Adafruit_DHT
import paho.mqtt.client as mqtt
import yaml
import time
import sys
import datetime
import voluptuous as vol
import json
import random
import logging
import lib.sensors
from voluptuous import Any
from lib.utils import GracefulKiller

DEFAULT_KEEP_ALIVE = 60
DEFAULT_DISCOVERY = False
DEFAULT_DISCOVERY_PREFIX = "homeassistant"
DEFAULT_AVAILABILITY_TOPIC = "home-assistant/cover/availabilty"
DEFAULT_PAYLOAD_AVAILABLE = "online"
DEFAULT_PAYLOAD_NOT_AVAILABLE ="offline"

def on_message(client, userdata, message):
    logging.info("message received = " + str(message.payload.decode("utf-8")))
    logging.info("message topic = " + str(message.topic))
    logging.info("message qos = "+ str(message.qos))
    logging.info("message retain flag = " + str(message.retain))

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code: %s" % mqtt.connack_string(rc))
    # notify subscribed clients that we are available
    client.publish(availability_topic, payload_available, retain=True)

if __name__ == '__main__':

    killer = GracefulKiller()

    CONFIG_SCHEMA = vol.Schema(
    {
    "general": vol.Schema(
        {
          vol.Required("scan_interval"):int,
          vol.Required("log_readings"): bool
        }

    ),
    "logging": vol.Schema(
        {
            vol.Required("log_level"): Any('DEBUG', 'INFO', 'WARNING','ERROR', 'CRITICAL'),
            vol.Required("show_timestamp"): bool
        }
    ),  
    "mqtt": vol.Schema(
        {
            vol.Required("host"): str,
            vol.Required("port"): int,
            vol.Required("user"): str,
            vol.Required("password"): str,
            vol.Optional("keep_alive", default = DEFAULT_KEEP_ALIVE): Any(int, None), 
            vol.Optional("discovery", default = DEFAULT_DISCOVERY): Any(bool, None),
            vol.Optional("discovery_prefix", default = DEFAULT_DISCOVERY_PREFIX): Any(str, None),
            vol.Optional("availability_topic", default = DEFAULT_AVAILABILITY_TOPIC): Any(str, None),
            vol.Optional("payload_available", default = DEFAULT_PAYLOAD_AVAILABLE): Any(str,None),
            vol.Optional("payload_not_available", default = DEFAULT_PAYLOAD_NOT_AVAILABLE ): Any(str, None)


        }
    ),
    vol.Optional("DHT"): 
    vol.Schema(
        {
        vol.Required("scan_interval"): int,
        vol.Required("sensors"): [
                
            vol.Schema({
                       vol.Required("type"): Any("DHT11","DHT22"),
                       vol.Required("scan_count"): int,
                       vol.Required("gpio"): int,
                       vol.Required("temperature_topic"): str, 
                       vol.Required("humidity_topic"): str
                       })]
        })
    })


    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.yaml'), 'r') as ymlfile:
        file_CONFIG = yaml.load(ymlfile, Loader=yaml.FullLoader)

    CONFIG = CONFIG_SCHEMA(file_CONFIG)
    #
    # setup logging and then log sucessful configuration validation
    #
    if CONFIG['logging']['show_timestamp']:
        logging.basicConfig(format='%(asctime)s %(message)s',level=CONFIG["logging"]["log_level"])
    else:
        logging.basicConfig(level=CONFIG["logging"]["log_level"])
    
    logging.info("Config suceesfully validated against schema")
    logging.info(json.dumps(
        CONFIG, indent = 4))
    ### SETUP MQTT ###
    user = CONFIG['mqtt']['user']
    password = CONFIG['mqtt']['password']
    host = CONFIG['mqtt']['host']
    port = int(CONFIG['mqtt']['port'])
    if CONFIG['mqtt']['keep_alive'] is None:
      keep_alive = DEFAULT_KEEP_ALIVE
    else:
         keep_alive = CONFIG['mqtt']['keep_alive']
    if CONFIG['mqtt']['discovery'] is None:
        discovery = DEFAULT_DISCOVERY
    else:
        discovery = CONFIG['mqtt']['discovery']

    if CONFIG['mqtt']['discovery_prefix'] is None:
        discovery_prefix = DEFAULT_DISCOVERY_PREFIX
    else:
        discovery_prefix = CONFIG['mqtt']['discovery_prefix']
    
    #
    # if availability values specified in config use them
    # if not use defaults 
    #

    if CONFIG['mqtt']['availability_topic'] is None:
        availability_topic = DEFAULT_AVAILABILITY_TOPIC
    else:
        availability_topic = CONFIG['mqtt']['availability_topic']

    if CONFIG['mqtt']['payload_available'] is None:
        payload_available = DEFAULT_PAYLOAD_AVAILABLE
    else:
        payload_available = CONFIG['mqtt']['payload_available']

    if CONFIG['mqtt']['payload_not_available'] is None:
        payload_not_available = DEFAULT_PAYLOAD_NOT_AVAILABLE
    else:
        payload_not_available = CONFIG['mqtt']['payload_not_available']

    logging.info("Creating MQTT client instance")
    client = mqtt.Client(client_id="MQTTGarageDoor_{:6s}".format(str(random.randint(
    0, 999999))), clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    
    client.on_message=on_message
    logging.info("Connecting to broker")
    client.on_connect = on_connect

    client.username_pw_set(user, password=password)


    # set a last will message so the broker will notify connected clients when
    # we are not available
    client.will_set(availability_topic, payload_not_available, retain=True)
    logging.info(
        "Set last will message: '" +
        payload_not_available +
        "' for topic: '" +
        availability_topic +
        "'")


    client.connect(host, port, keep_alive)
    client.loop_start()
    # 
    #ToDo add discovery
    #
    
    
    #
    # Set up GPIO
    #
    io.setwarnings(False)
    io.setmode(io.BCM)
    sensor = Adafruit_DHT.DHT22
    pin = 3
    #
    # Main Loop
    #
    while True:
      humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
      humidity = round(humidity,1)
      temperature = round((temperature * 9.0 / 5.0)+ 32.0,1)
      if humidity is not None and temperature is not None:
        logging.info(str('Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(temperature, humidity)))
        client.publish("garage/temp1", temperature)
        client.publish("garage/humidity1", humidity)
      else:
        logging.warning(str(datetime.datetime.now()) + 'Failed to get reading. Try again!') 
      time.sleep(60)
      if killer.kill_now:
        break
    logging.info ("End of the program. I was killed gracefully")

