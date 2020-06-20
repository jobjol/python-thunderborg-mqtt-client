#!/usr/bin/env python
# coding: latin-1

import paho.mqtt.client as mqttClient
import time
import os
import subprocess
import config
import ThunderBorg
import sys
import credentials

# Name the global variables
global step
global TB

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()     # Create a new ThunderBorg object
#TB.i2cAddress = 0x15              # Uncomment and change the value if you have changed the board address
TB.Init()                          # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print 'No ThunderBorg found, check you are attached :)'
    else:
        print 'No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'TB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
step = -1


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected =True
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    print ('message incoming')
    print (message.payload)
    if message.topic == 'home/living/curtain/left':
        if is_number(message.payload):
            moveStep(message.payload, 0)

    if message.topic == 'home/living/curtain/right':
        if is_number(message.payload):
            moveStep(message.payload, 1)

# Function to perform a sequence of steps as fast as allowed
def moveStep(count, motornumber):
    global step
    global TB

    # Choose direction based on sign (+/-)
    if count < 0:
        dir = -1
        count *= -1
    else:
        dir = 1

    # Loop through the steps
    while count > 0:
        # Set a starting position if this is the first move
        if step == -1:
            drive = config.sequence[-1]
            if motornumber == 0:
                TB.SetMotor1(drive[motornumber])
            if motornumber == 1:
                TB.SetMotor2(drive[motornumber])
            step = 0
        else:
            step += dir

        # Wrap step when we reach the end of the sequence
        if step < 0:
            step = len(config.sequence) - 1
        elif step >= len(config.sequence):
            step = 0

        # For this step set the required drive values
        if step < len(config.sequence):
            drive = config.sequence[step]
            if motornumber == 0:
                TB.SetMotor1(drive[motornumber])
            if motornumber == 1:
                TB.SetMotor2(drive[motornumber])
        time.sleep(config.stepDelay)
        count -= 1

# Function to switch to holding power
def HoldPosition(motornumber):
    global step
    global TB

    # For the current step set the required holding drive values
    if step < len(config.sequence):
        drive = config.sequenceHold[step]
        TB.SetMotor1(drive[0])
        TB.SetMotor2(drive[1])


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

client.subscribe('home/living/curtain/left')
client.subscribe('home/living/curtain/right')

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print "exiting"
    client.disconnect()
    client.loop_stop()
