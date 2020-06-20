import paho.mqtt.client as mqttClient
import time
import os
import subprocess
import config
# Create a credentials.py file with the following structure:
#
#     username = 'xxx',
#     password = 'xxx',
import credentials

global Connected

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected =True
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    print "Message received: " + message.topic + " : " + message.payload
    time.sleep(1.5)
    if message.topic == 'home/living/curtain/left':
        print 'left'
    if message.topic == 'home/living/curtain/right':
        print 'right'


Connected = False

broker_address = config.broker #Your MQTT broker IP address
port = config.port #default port change as required
user = credentials.username #mqtt user name change as required
password = credentials.password #mqtt password change as required
client = mqttClient.Client(config.client_name)
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port=port)
client.loop_start()

while Connected != True:
    time.sleep(0.1)

client.subscribe('Misc/PrayerTrigger')
client.subscribe('Misc/PrayerTriggerFajr')

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()
