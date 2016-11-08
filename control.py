import sys, time
import logging, logging.handlers

import cloud4rpi

DEVICE_TOKEN = '9vZPYh7ybYxXLZaCrVZWvJLZv'
DATA_SENDING_INTERVAL = 600  # secs
DIAG_SENDING_INTERVAL = 3600  # secs
POLL_INTERVAL = 10  # 100 ms


def get_ups_status():
    return 'OFFLINE'

class UPS(object):
    def read(self):
        return get_ups_status() == 'ONLINE'

class GetSensor(object):
    def read(self):
        return 25

class CPUTemp(object):
    def read(self):
        return 70
class IPAddress(object):
    def read(self):
        return '8.8.8.8'
class Hostname(object):
    def read(self):
        return 'hostname'

class OSName(object):
    def read(self):
        return 'osx'

LOG_FILE_PATH = '../cloud4rpi.log'

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


def main():
    configure_logging(log)

    # Put variable declarations here
    variables = {
         'RoomTemp': {
             'type': 'numeric',
             'bind': GetSensor()
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
        'CPU Temperature': CPUTemp(),
        'IPAddress': IPAddress(),
        'Host': cloud4rpi.Hostname(),
        'OS Name': OSName()
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.send_data()
    device.send_diag()

    try:
        time_passed = 0
        prev_ups = 'ONLINE'
        next_data_sending = DATA_SENDING_INTERVAL
        next_diag_sending = DIAG_SENDING_INTERVAL
        while True:
            new_ups = get_ups_status()
            if (time_passed >= next_data_sending) | (new_ups != prev_ups):
                next_data_sending += DATA_SENDING_INTERVAL
                device.send_data()
                prev_ups = new_ups

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
