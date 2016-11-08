#!/usr/bin/env python2.7

import sys
sys.path.append('../cloud4rpi/')
import subprocess, re, os, time
import cloud4rpi
#import RPi.GPIO as GPIO  # pylint: disable=E0401


# Put your device token here. To get the token, sign up at https://cloud4rpi.io and create a device.
cloud4rpi.DEVICE_TOKEN = '9vZPYh7ybYxXLZaCrVZWvJLZv' 

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 10  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.1  # 100 ms


def configure_gpio():
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(LED_PIN, GPIO.OUT)
    return


# handler for the button or switch variable
def led_control(value=None):
    #GPIO.output(LED_PIN, value)
    #current = GPIO.input(LED_PIN)
    #return current
    return value

def getUpsStatus():
    return 'UNKNOWN'

class UPS(object):
    def read(self):
        return getUpsStatus() == 'ONLINE'

class Sensor(object):
    def read(self):
        return 42

def main():
    #configure_logging(log)
    configure_gpio()

    #  load w1 modules
    #cloud4rpi.modprobe('w1-gpio')
    #cloud4rpi.modprobe('w1-therm')

    # detect ds18b20 temperature sensors
    #ds_sensors = cloud4rpi.DS18b20.find_all()

    # Put variable declarations here
    variables = {
         'RoomTemp': {
             'type': 'numeric',
             'bind': Sensor()
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

    device = cloud4rpi.connect()
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.send_data()
    device.send_diag()

    try:
        time_passed = 0
        prevUPS = 'ONLINE'
        next_data_sending = DATA_SENDING_INTERVAL
        next_diag_sending = DIAG_SENDING_INTERVAL
        while True:
            newUPS = getUpsStatus()
            if (time_passed >= next_data_sending) | (newUPS != prevUPS):
                next_data_sending += DATA_SENDING_INTERVAL
                device.send_data()
                prevUPS = newUPS

            if time_passed >= next_diag_sending:
                next_diag_sending += DIAG_SENDING_INTERVAL
                device.send_diag()

            time.sleep(POLL_INTERVAL)
            time_passed += POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.logger.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.logger.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
