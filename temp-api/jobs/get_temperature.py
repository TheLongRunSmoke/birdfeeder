from datetime import datetime

import app
from app.models import Temperature
from config import INTERNAL_ROM, EXTERNAL_ROM
from subprocess import PIPE, Popen


def run():
    import os
    import glob

    base_dir = '/sys/bus/w1/devices/'
    devices = glob.glob(base_dir + '28*')

    # if no devices try to mount them
    if len(devices) == 0:
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

    temp = Temperature()

    for device in devices:
        if EXTERNAL_ROM in device:
            device_file = device + '/w1_slave'
            temp.external = read_temp(device_file)
        if INTERNAL_ROM in device:
            device_file = device + '/w1_slave'
            temp.internal = read_temp(device_file)

    temp.cpu = get_cpu_temperature()

    write_to_db(temp)


def read_temp_raw(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(file):
    lines = read_temp_raw(file)
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Read the temperature.
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index(b"=")+1:output.index(b"'")])


def write_to_db(data: Temperature):
    now = int(datetime.utcnow().timestamp())
    data.timestamp = now
    app.db.session.add(data)
    app.db.session.commit()
