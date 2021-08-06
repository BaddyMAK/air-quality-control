import aranet4
import sqlite3
import time
import csv
import pandas as pd
import os.path

# Declare my columns
Colum=['temperature', 'humidity', 'pressure', 'co2']
# define the MAC address of my Aranet
device_mac = "EE:E3:FC:40:09:5C"


# connecting to Aranet
ar4 = aranet4.Aranet4(device_mac)
current = ar4.currentReadings()
Temp = current["temperature"]
Humid = current["humidity"]
Press = current["pressure"]
CO2 = current["co2"]
# print(Temp)
# print(Humid)
# print(Press)
# print(CO2)
dict_1 = {'temperature': Temp, 'humidity': Humid, 'pressure': Press, 'co2': CO2}
MyData_csv = pd.DataFrame([dict_1])
# Verify if the file exists to append rows otherwise create a new one
if not os.path.exists('Aranet_dati.csv'):
    # If the file does not exists ==> create it
    MyData_csv.to_csv('Aranet_dati.csv', index=False, header=False, sep=',', encoding='utf-8')
else:
    # If the file does exists ==> just write the new row
    with open('Aranet_dati.csv', 'a+', encoding='UTF8', newline='') as f:
        data = [Temp, Humid, Press, CO2]
        writer = csv.writer(f)
        # write the data
        writer.writerow(data)