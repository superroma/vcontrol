import sys, time
import cloud4rpi

def read_ups_status():
    return 'OFFLINE'

def ups_online():
    return read_ups_status() == 'ONLINE'

def get_sensors():
    return 25

def cpu_temp():
    return 70

def ip_address():
    return '8.8.8.8'

def hostname():
    return 'hostname'

def osname():
    return 'osx'

DEVICE_TOKEN = '9vZPYh7ybYxXLZaCrVZWvJLZv'
DATA_SENDING_INTERVAL = 5  # secs
DIAG_SENDING_INTERVAL = 20  # secs
POLL_INTERVAL = 0.5  # 100 ms

def main():
    # Put variable declarations here
    variables = {
        'RoomTemp': {
            'type': 'numeric',
            'bind': get_sensors
        },
        'UpsOnline': {
            'type': 'bool',
            'bind': ups_online
        }
    }

    diagnostics = {
        'CPU Temperature': cpu_temp,
        'IPAddress': ip_address,
        'Host': hostname,
        'OS Name': osname
    }

    device = cloud4rpi.connect_mqtt(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    try:
        diag_timer = 0
        data_timer = 0
        prev_ups = 'ONLINE'
        while True:
            if diag_timer <= 0:
                device.send_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            new_ups = read_ups_status()
            if (data_timer <= 0) | (new_ups != prev_ups):
                device.send_data()
                prev_ups = new_ups
                data_timer = DATA_SENDING_INTERVAL


            time.sleep(POLL_INTERVAL)
            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
