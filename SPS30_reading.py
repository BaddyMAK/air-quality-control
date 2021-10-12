import subprocess
import serial
import struct
import time
import pandas as pd
import numpy as np
#s1 = SPS30(port='/dev/ttyUSB0')

def get_usb(): # - list all devices connected to USB port and make sure no other devices rather SDS011 sensors connected
    try:
        with subprocess.Popen(['ls /dev/ttyUSB*'], shell=True, stdout=subprocess.PIPE) as f:
            usbs = f.stdout.read().decode('utf-8')
        usbs = usbs.split('\n')
        usbs = [usb for usb in usbs if len(usb) > 3]
    except Exception as e:
        print('No USB available')
    return usbs

usbs = get_usb()
print(usbs)
def read_values(ser):
    ser.flushInput()
    # Ask for data
    ser.write([0x7E, 0x00, 0x03, 0x00, 0xFC, 0x7E])
    toRead = ser.inWaiting()
    # Wait for full response
    # (may be changed for looking for the stop byte 0x7E)
    while toRead < 47:
        toRead = ser.inWaiting()
        print(f'Wait: {toRead}')
        time.sleep(1)
    raw = ser.read(toRead)
    # Reverse byte-stuffing
    if b'\x7D\x5E' in raw:
        raw = raw.replace(b'\x7D\x5E', b'\x7E')
    if b'\x7D\x5D' in raw:
        raw = raw.replace(b'\x7D\x5D', b'\x7D')
    if b'\x7D\x31' in raw:
        raw = raw.replace(b'\x7D\x31', b'\x11')
    if b'\x7D\x33' in raw:
        raw = raw.replace(b'\x7D\x33', b'\x13')
    # Discard header and tail
    rawData = raw[5:-2]
    try:
        data = struct.unpack(">ffffffffff", rawData)
    except struct.error:
        data = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return data

def read_serial(ser):
    ser.flushInput()
    ser.write([0x7E, 0x00, 0xD0, 0x01, 0x03, 0x2B, 0x7E])
    toRead = ser.inWaiting()
    while toRead < 7:  # 24
        toRead = ser.inWaiting()
        print(f'Wait: {toRead}')
        time.sleep(1)
    raw = ser.read(toRead)
    # Reverse byte-stuffing
    if b'\x7D\x5E' in raw:
        raw = raw.replace(b'\x7D\x5E', b'\x7E')
    if b'\x7D\x5D' in raw:
        raw = raw.replace(b'\x7D\x5D', b'\x7D')
    if b'\x7D\x31' in raw:
        raw = raw.replace(b'\x7D\x31', b'\x11')
    if b'\x7D\x33' in raw:
        raw = raw.replace(b'\x7D\x33', b'\x13')
    # Discard header, tail and decode
    serial_number = raw[5:-3].decode('ascii')
    return serial_number

def datetime_():
    return time.strftime('%x %X', time.localtime())

port=usbs
# 1- Connect to the sensor
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, stopbits=1, parity="N",  timeout=2)
# Start the reading :
ser.write([0x7E, 0x00, 0x00, 0x02, 0x01, 0x03, 0xF9, 0x7E])
# Read the serial number of device
ser_num=read_serial(ser)
# Read the values
output = read_values(ser)
sensorData = ""
for val in output:
    sensorData += "{0:.2f},".format(val)
# Join all the data
name = 'SPS30'
#print(name)
output = ','.join([name, datetime_(), sensorData[:-1]])
# stop connection
ser.write([0x7E, 0x00, 0x01, 0x00, 0xFE, 0x7E])
print(output)
output=output.split(',')
columns=['sensor', 'time', 'PM1', 'PM25', 'PM4', 'PM10', 'b0305', 'b031', 'b0325', 'b034', 'b0310','tsize']
data_sps30={'sensor': output[0], 'time': output[1], 'PM1':output[2], 'PM25': output[3],
            'PM4':output[4], 'PM10': output[5], 'b0305': output[6], 'b031': output[7], 'b0325': output[8],
            'b034':output[9],'b0310': output[10], 'tsize': output[11]}
Mydata=pd.DataFrame([data_sps30])
print(Mydata)