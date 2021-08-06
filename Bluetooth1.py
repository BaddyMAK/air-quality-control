import sqlite3
import bluetooth
import time
import serial
import os

os.system("sudo rfcomm connect 0  EE:E3:FC:40:09:5C") #This number bluetooth MAC adress(20:15....)

ser=serial.Serial('/dev/rfcomm0',38400) #Listen to data,baudrate(38400) has to be same with the arduino code

conn = sqlite3.connect('sensordata.db') #Database connection

if(conn):            #Check database connection
    print('y')

else:
    print('n')

my_string=[]      #Sensor data array

while 1:

    timeout=time.time()+5            #Receive data every five sec.
    my_string.clear()
    if time.time() > timeout:  # verificare il tempo
        break
    data=ser.readline()      #Read all data on one line
    my_string.split()    # dividere la stringa
    selct=conn.cursor()          #for database

    selct.execute('''INSERT INTO sensor1 VALUES (?)''',(i,))     #Write in database -sensor1 table name in database-
    conn.commit()

conn.close()
sock.close()