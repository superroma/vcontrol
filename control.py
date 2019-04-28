# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import ds18b20
import rpi
import RPi.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = 'YOUR YOKEN'

# Constants
DATA_SENDING_INTERVAL = 300  # sec
DIAG_SENDING_INTERVAL = 3600  # sec
POLL_INTERVAL = 1  # sec


def ups_status():
    result = rpi.parse_output(r'STATUS\s+:\s+(\S+)',
                              ['/etc/init.d/apcupsd', 'status'])
    if result:
        return result
    else:
        return 'UNKNOWN'


def main():
    ds18b20.init_w1()
    ds_sensors = ds18b20.DS18b20.find_all()
    variables = {
        'RoomTemp': {
            'type': 'numeric',
            'bind': ds_sensors[0] if ds_sensors else None
        },
        'UPSStatus': {
            'type': 'string',
            'bind': ups_status
        }
    }

    diagnostics = {
        'CPU Temp': rpi.cpu_temp,
        'IP Address': rpi.ip_address,
        'Host': rpi.host_name,
        'Operating System': rpi.os_name
    }
    device = cloud4rpi.connect(DEVICE_TOKEN)

    try:
        device.declare(variables)
        device.declare_diag(diagnostics)

        device.publish_config()

        # Adds a 1 second delay to ensure device variables are created
        sleep(1)

        data_timer = 0
        diag_timer = 0
        prevUPS = 'ONLINE'

        while True:
            newUPS = ups_status()
            if (data_timer <= 0) or (newUPS != prevUPS):
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL
                prevUPS = newUPS

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            sleep(POLL_INTERVAL)
            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
