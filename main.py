#!/usr/bin/python3
import signal
import time
import RPi.GPIO as io
import Adafruit_DHT
import paho.mqtt.client as mqtt
import time
import utils
import sys
import datetime
door_relay = 21
class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True
def on_message(client, userdata, message):
    print(str(datetime.datetime.now()) + "message received " ,str(message.payload.decode("utf-8")))
    print(str(datetime.datetime.now()) + "message topic=",message.topic)
    print(str(datetime.datetime.now()) + "message qos=",message.qos)
    print(str(datetime.datetime.now()) + "message retain flag=",message.retain)

if __name__ == '__main__':
  #if not utils.is_running(sys.argv[0]):
    killer = GracefulKiller()
    #
    # Provide delay on system startup
    #
    seconds_up = utils.uptime()
    if seconds_up < 60.0:
        sleep_time = 60.0-seconds_up
        print(str(datetime.datetime.now()) + "Going to sleep for " + str(sleep_time) + " seconds.")
        sleep(sleep_time) # give the system 1 minute to startup before running
    print(str(datetime.datetime.now()) + "Creating MQTT client instance")
    client = mqtt.Client("GaragePI")
    client.on_message=on_message
    print(str(datetime.datetime.now()) + "Connecting to broker")
    client.connect("mqtt.thegrays.duckdns.org")
    client.loop_start()
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
        print(str(datetime.datetime.now()) + 'Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(temperature, humidity))
        client.publish("garage/temp1", temperature)
        client.publish("garage/humidity1", humidity)
      else:
        print(str(datetime.datetime.now()) + 'Failed to get reading. Try again!') 
      time.sleep(60)
      if killer.kill_now:
        break
    print (str(datetime.datetime.now()) + "End of the program. I was killed gracefully")

