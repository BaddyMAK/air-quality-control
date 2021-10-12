### Importing the required libraries ###
import aranet4
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import serial
import struct
import time
import requests
import json


# Code for Aranet Pro
# Define My Data frame
# Declare my columns
Colum=['temperature', 'humidity', 'pressure', 'co2', 'PM10','PM2.5']

# define the MAC address of my Aranet
device_mac = "EE:E3:FC:40:09:5C"
# connecting to Aranet
ar4 = aranet4.Aranet4(device_mac)
current = ar4.currentReadings()
Temp = current["temperature"]
Humid = current["humidity"]
Press = current["pressure"]
CO2 = current["co2"]

dict_aranet = {"temperature": Temp, "humidity": Humid, "pressure": Press, "co2": CO2}

Data_Aranet = pd.DataFrame([dict_aranet])

#Data_Aranet.insert(0, 'TimeStamp', pd.to_datetime('now').replace(microsecond=0) +timedelta(hours=2))
Data_Aranet.to_csv('Aranet_dati', index=False, header=False, sep=';', encoding='utf-8')
print(Data_Aranet)

##### Code for Sensirion SPS30 #########
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

# def datetime_():
#     return time.strftime('%x %X', time.localtime())

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
output = ','.join([name,str(pd.to_datetime('now').replace(microsecond=0) +timedelta(hours=2)), sensorData[:-1]])
# stop connection
ser.write([0x7E, 0x00, 0x01, 0x00, 0xFE, 0x7E])
print(output)
output=output.split(',')
# columns_sps30=['sensor', 'time', 'PM1', 'PM25', 'PM4', 'PM10', 'b0305', 'b031', 'b0325', 'b034', 'b0310','tsize']
dict_sps30={"time": output[1], "PM1":output[2], "PM25": output[3],
            "PM4":output[4], "PM10": output[5], "b0305": output[6], "b031": output[7], "b0325": output[8],
            "b034":output[9],"b0310": output[10], "tsize": output[11]}
Data_sps30=pd.DataFrame([dict_sps30])
print(Data_sps30)

DataFrame_final=pd.concat([Data_sps30, Data_Aranet], axis=1)
print(DataFrame_final)

Final_dict={}
Final_dict.update(dict_sps30)
Final_dict.update(dict_aranet)
print(Final_dict)


url = "https://nviot.netvalue.eu/issk/api.php"
json_pay=json.dumps(Final_dict)
payload={'data': json_pay}
print(payload)
response = requests.request("POST", url, data=payload)

print(response.text)

