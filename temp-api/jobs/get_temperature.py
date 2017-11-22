from datetime import datetime

import app


def run():
    import os
    import glob
    import time

    # These tow lines mount the device:
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    base_dir = '/sys/bus/w1/devices/'
    # Get all the filenames begin with 28 in the path base_dir.
    print(glob.glob(base_dir + '*'))
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    def read_rom():
        name_file = device_folder + '/name'
        f = open(name_file, 'r')
        return f.readline()

    def read_temp_raw():
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp():
        lines = read_temp_raw()
        # Analyze if the last 3 characters are 'YES'.
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        # Find the index of 't=' in a string.
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            # Read the temperature .
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

    print(' rom: ' + read_rom())
    while True:
        print(' C=%3.3f  F=%3.3f' % read_temp())
        #
        # if crawler.status == 0:
        #     data = crawler.get_data()
        #     write_to_db(data)
        #     now = datetime.utcnow().date()
        #     query = app.models.TleData.query.filter_by(
        #         addTime=int(datetime(now.year, now.month, now.day).timestamp())).all()
        #     if query is not None:
        #         with app.app.app_context():
        #             app.mailer.Mailer.new_tle_notify(query)
        # else:
        #     with app.app.app_context():
        #         app.mailer.Mailer.tle_provider_fail_notify()


def write_to_db(data):
    now = datetime.utcnow().date()
    timestamp = int(datetime(now.year, now.month, now.day).timestamp())
    for temp in data:
        query = app.models.Temperature.query.filter_by(timestamp=temp[0]).first()
        if query is None:
            row = app.models.Temperature(timestamp=temp[0], data=temp[1])
            app.db.session.add(row)
            app.db.session.commit()
        else:
            if query.data != temp[1]:
                query.data = temp[1]
                query.timestamp = timestamp
                app.db.session.commit()
