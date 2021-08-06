import aranet4
import sqlite3
import pandas as pd
import time
import csv

# Declare my columns
Colum=['temperature', 'humidity', 'pressure', 'co2']
# define the MAC address of my Aranet
device_mac = "EE:E3:FC:40:09:5C"

while True:
    time.sleep(10)
    # connecting to Aranet
    ar4 = aranet4.Aranet4(device_mac)
    current = ar4.currentReadings()
    Temp = current["temperature"]
    Humid = current["humidity"]
    Press = current["pressure"]
    CO2 = current["co2"]
    # Connecting to database
    #conn = sqlite3.connect('sensordata.db') #Database connection
    break

MyData_csv = pd.DataFrame([Temp, Humid, Press, CO2], columns=Colum)

# Write your csv file :

MyData_csv.to_csv('Aranet_dati', index=False, header=False, sep=';', encoding='utf-8')

with open('Aranet_dati.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    # write the data
    writer.writerow(MyData_csv)



dict_1={'temperature':Temp,'humidity':Humid,'pressure':Press, 'co2' :CO2 }