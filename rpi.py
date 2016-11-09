import subprocess
import re

def parse_output(pattern, default, args):
    try:
        out_str = subprocess.check_output(args)
    except:
        out_str = 'error'
    match = re.search(pattern, out_str)
    if match:
        result = match.group(1)
    else:
        result = default
    return result


def cpu_temp():
    return parse_output('temp=(.*)C', '0', ['vcgencmd', 'measure_temp'])

def ip_address():
    return parse_output('(.*)', '?', ['hostname', '-I'])

def hostname():
    return parse_output('(.*)', '?', ['hostname'])

def osname():
    return parse_output('(.*)', '?', ['uname', '-a'])
