# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 11:18:00 2025

@author: Prac1
"""

import serial
import serial.tools.list_ports
import time
import numpy as np
import os
import datetime as dt

def check_ports():
    return print([comport.device for comport in serial.tools.list_ports.comports()])


main_dir='G:/NWieczerzynska'
folder=str(dt.datetime.now().year)+"-"+str(dt.datetime.now().month)+"-"+str(dt.datetime.now().day)
n=0
while os.path.exists(os.path.join(main_dir, folder))==True:
    folder=folder+"_"+str(n)
    n+=1
path=os.path.join(main_dir,folder)
os.mkdir(path)   


for i in serial.tools.list_ports.comports():
    if i[2][:21]=="USB VID:PID=0483:374B":
        M_port=i[0]
    if i[2][:21]=="USB VID:PID=0483:5740":
        T_port=i[0]
    if i[2][:21]=="USB VID:PID=067B:2303":
        K_port=i[0]

K_port="COM11"



class Thorlabs_diode:
    
    
    def __init__(self):
        self.port=serial.Serial(T_port, baudrate=19200,bytesize=8,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO)
        self.port.close()
        
    def send_command (self,voltage):
        self.port.open()
        command=str(voltage)+"\n"
        self.port.write(bytearray(command,"ascii"))
        self.port.close()



class Keithley:
    
    def __init__(self,K_port):
        self.port=serial.Serial(K_port,baudrate=19200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO)
        # self.port.close()


    def set_limits(self,voltage_limit=100, current_limit=0.1): 
        # self.port.open()
        self.port.write(bytearray("*RST\n","ascii"))
        self.port.write(bytearray(":SOUR:FUNC VOLT\n",'ascii'))
        self.port.write(bytearray(":SOUR:VOLT:MODE FIX\n",'ascii'))
        self.port.write(bytearray(":SOUR:VOLT:RANG " +str(voltage_limit)+ "\n",'ascii'))  
        self.port.write(bytearray(":SENS:FUNC \"CURR\"\n",'ascii'))
        self.port.write(bytearray(":SENS:CURR:PROT " +str(current_limit)+ "\n",'ascii'))
        self.port.write(bytearray(":SENS:CURR:RANG:AUTO ON\n",'ascii'))
        # self.port.close()
   
    def set_voltage(self, voltage):
        # self.port.open()
        self.port.write(bytearray(":SOUR:VOLT:LEV " +str(voltage)+ "\n",'ascii'))
        # self.port.close()
    
    
    def measure(self):
        # self.port.open()
        self.port.write(bytearray(":READ? \n",'ascii'))
        temp=self.port.readline().decode('ascii').split(",")
        # self.port.close()
        return (temp[0],temp[1])
        
    def ON (self):
        # self.port.open()
        self.port.write(bytearray(":OUTP ON\n",'ascii'))
        # self.port.close()
        
    def OFF (self):
        # self.port.open()
        self.port.write(bytearray(":OUTP OFF\n",'ascii'))
        # self.port.close()
        
    def close(self):
        self.port.close()
