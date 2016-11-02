#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import subprocess
import re
import logging
import logging.handlers
import os
import sys
import time
import cloud4rpi
import RPi.GPIO as GPIO  # pylint: disable=E0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = 'AGyBWv7NH4D7bXQwQoQNhRr9r'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.1  # 100 ms

LOG_FILE_PATH = '/var/log/cloud4rpi.log'

log = logging.getLogger(cloud4rpi.config.loggerName)
log.setLevel(logging.INFO)


def configure_logging(logger):
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(console)
    log_file = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=1024 * 1024,
        backupCount=10
    )
    log_file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(log_file)


def configure_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    current = GPIO.input(LED_PIN)
    return current

class UPS(object):
    def read(self):
    	try:
        	outStr = subprocess.check_output(["/etc/init.d/apcupsd", "status"])
    	except:
        	outStr = ''
    	match = re.search('STATUS\s+:\s+(\S+)', outStr)
    	if match:
        	status = match.group(1)
    	else:
        	status = 'UNKNOWN'
    	return status == 'ONLINE'
	
def main():
    configure_logging(log)
    configure_gpio()

    #  load w1 modules
    cloud4rpi.modprobe('w1-gpio')
    cloud4rpi.modprobe('w1-therm')

    # detect ds18b20 temperature sensors
    ds_sensors = cloud4rpi.DS18b20.find_all()

    # Put variable declarations here
    variables = {
         'RoomTemp': {
             'type': 'numeric',
             'bind': ds_sensors[0]
         },
	'UpsOnline': {
             'type': 'bool',
             'bind': UPS()
         }

        # 'CurrentTemp_2': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[1]
        # },

        #'LEDOn': {
        #    'type': 'bool',
        #    'value': False,
        #    'bind': led_control
        #},

        #'CPUTemp': {
        #    'type': 'numeric',
        #    'bind': cloud4rpi.CpuTemperature()
        #}
    }

    diagnostics = {
        'CPU Temperature': cloud4rpi.CpuTemperature(),
        'IPAddress': cloud4rpi.IPAddress(),
        'Host': cloud4rpi.Hostname(),
        'OS Name': ' '.join(str(x) for x in os.uname())
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.send_data()
    device.send_diag()

    try:
        time_passed = 0
        next_data_sending = DATA_SENDING_INTERVAL
        next_diag_sending = DIAG_SENDING_INTERVAL
        while True:
            if time_passed >= next_data_sending:
                next_data_sending += DATA_SENDING_INTERVAL
                device.send_data()

            if time_passed >= next_diag_sending:
                next_diag_sending += DIAG_SENDING_INTERVAL
                device.send_diag()

            time.sleep(POLL_INTERVAL)
            time_passed += POLL_INTERVAL

    except KeyboardInterrupt:
        log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
