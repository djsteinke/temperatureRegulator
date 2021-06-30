import logging
import properties
import smbus
import time
import os

bus = smbus.SMBus(1)
config = [0x08, 0x00]

fdir = os.path.abspath('/home/pi/projects/temperatureRegulator')
# fdir = os.path.abspath('C:/MyData/Program Files/PyCharm/temperatureRegulator')


def get_logging_level():
    if properties.log_debug:
        return logging.DEBUG
    elif properties.log_info:
        return logging.INFO
    elif properties.log_warning:
        return logging.WARNING
    else:
        return logging.ERROR


def get_temperature(status):
    bus.write_i2c_block_data(0x38, 0xE1, config)
    byt = bus.read_byte(0x38)
    print(byt & 0x68)
    measure_cmd = [0x33, 0x00]
    bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38, 0x00)
    temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    temp_c = ((temp_raw*200) / 1048576) - 50
    humid_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    humid = humid_raw * 100 / 1048576
    status.temperature(temp_c)
    status.humidity(humid)
    return status


def get_temp():
    bus.write_i2c_block_data(0x38, 0xE1, config)
    byt = bus.read_byte(0x38)
    measure_cmd = [0x33, 0x00]
    bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38, 0x00)
    temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    temp_c = ((temp_raw*200) / 1048576) - 50
    humid_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    humid = humid_raw * 100 / 1048576
    return [temp_c, humid]

