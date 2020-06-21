#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Jon Levell <levell@uk.ibm.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# All rights reserved.

# This shows a example of an MQTT subscriber with the ability to use
# user name, password CA certificates based on command line arguments

import paho.mqtt.client as mqtt
import os
import ssl
import argparse
import ThunderBorg
import time
import sys
import config

# Name the global variables
global step
global TB

parser = argparse.ArgumentParser()

parser.add_argument('-H', '--host', required=False, default="mqtt.eclipse.org")
parser.add_argument('-t', '--topic', required=False, default="$SYS/#")
parser.add_argument('-q', '--qos', required=False, type=int, default=0)
parser.add_argument('-c', '--clientid', required=False, default=None)
parser.add_argument('-u', '--username', required=False, default=None)
parser.add_argument('-d', '--disable-clean-session', action='store_true', help="disable 'clean session' (sub + msgs not cleared when client disconnects)")
parser.add_argument('-p', '--password', required=False, default=None)
parser.add_argument('-P', '--port', required=False, type=int, default=None, help='Defaults to 8883 for TLS or 1883 for non-TLS')
parser.add_argument('-k', '--keepalive', required=False, type=int, default=60)
parser.add_argument('-s', '--use-tls', action='store_true')
parser.add_argument('--insecure', action='store_true')
parser.add_argument('-F', '--cacerts', required=False, default=None)
parser.add_argument('--tls-version', required=False, default=None, help='TLS protocol version, can be one of tlsv1.2 tlsv1.1 or tlsv1\n')
parser.add_argument('-D', '--debug', action='store_true')

args, unknown = parser.parse_known_args()

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
step = [-1, -1]

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == "home/living/curtain/left":
        MoveStep(msg.payload,0)
    if msg.topic == "home/living/curtain/right":
        MoveStep(msg.payload,1)


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# Function to perform a sequence of steps as fast as allowed
def MoveStep(count):
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
            TB.SetMotor1(drive[0])
            TB.SetMotor2(drive[1])
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
            TB.SetMotor1(drive[0])
            TB.SetMotor2(drive[1])
        time.sleep(config.stepDelay)
        count -= 1


# Function to switch to holding power
def HoldPosition():
    global step
    global TB

    # For the current step set the required holding drive values
    if step < len(config.sequence):
        drive = config.sequenceHold[step]
        TB.SetMotor1(drive[0])
        TB.SetMotor2(drive[1])


usetls = args.use_tls

if args.cacerts:
    usetls = True

port = args.port
if port is None:
    if usetls:
        port = 8883
    else:
        port = 1883

mqttc = mqtt.Client(args.clientid,clean_session = not args.disable_clean_session)

if usetls:
    if args.tls_version == "tlsv1.2":
        tlsVersion = ssl.PROTOCOL_TLSv1_2
    elif args.tls_version == "tlsv1.1":
        tlsVersion = ssl.PROTOCOL_TLSv1_1
    elif args.tls_version == "tlsv1":
        tlsVersion = ssl.PROTOCOL_TLSv1
    elif args.tls_version is None:
        tlsVersion = None
    else:
        print ("Unknown TLS version - ignoring")
        tlsVersion = None

    if not args.insecure:
        cert_required = ssl.CERT_REQUIRED
    else:
        cert_required = ssl.CERT_NONE

    mqttc.tls_set(ca_certs=args.cacerts, certfile=None, keyfile=None, cert_reqs=cert_required, tls_version=tlsVersion)

    if args.insecure:
        mqttc.tls_insecure_set(True)

if args.username or args.password:
    mqttc.username_pw_set(args.username, args.password)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

if args.debug:
    mqttc.on_log = on_log

print("Connecting to "+args.host+" port: "+str(port))
mqttc.connect(args.host, port, args.keepalive)
mqttc.subscribe(args.topic, args.qos)

mqttc.loop_forever()