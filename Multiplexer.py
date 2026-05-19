import pyvisa
import numpy as np
import time
import Keithley
import matplotlib.pyplot as plt
import pandas as pd
class Multiplexer:
    def __init__(self, pinnumber, resource_name='?*::45905::?*',lib_path='C:\\Windows\\System32\\visa32.dll', verbose=False, ground_pins=[0, 11]):
        rm = pyvisa.ResourceManager(lib_path)
        list1 = rm.list_resources(resource_name)
        self.inst = rm.open_resource(list1[0])
        self.inst.write("S")
        self.pinnumber = pinnumber
        self.ground_pins = ground_pins
        self.instructions = []
        if verbose:
            print(self.inst.query('*IDN?'))

    def connect_pin(self,pins_signal_a, pins_signal_b, pins_ground_a = -1, pins_ground_b = -1):
        if pins_ground_a == -1:
            pins_ground_a = self.ground_pins
        if pins_ground_b == -1:
            pins_ground_b = self.ground_pins

        instr = "S"
        for pin in pins_ground_a:
            if type(pin) == int and pin < 29:
                instr += f" {pin}ag"
        for pin in pins_ground_b:
            if type(pin) == int and pin < 29:
                instr += f" {pin}bg"
        for pin in pins_signal_a:
            if type(pin) == int and pin < 29:
                instr += f" {pin}ag"
        for pin in pins_signal_b:
            if type(pin) == int and pin < 29:
                instr += f" {pin}bs"

        self.instructions.append(instr)
        self.inst.write(instr)

    def last_instruction(self):
        if len(self.instructions) > 0:
            return self.instructions[-1]
        else:
            return "Brak instrukcji"
        

class MeasurementsManager:
    def __init__(self, Keithley_port, pinlist: list, side='a', ground_pins=[0, 11], resource_name='?*::45905::?*',
                 lib_path='C:\\Windows\\System32\\visa32.dll', verbose=False,plot=True, nsteps=10, voltage_step=0.1, loop_back=True):
        self.MP = Multiplexer(29, resource_name, lib_path, verbose, ground_pins)
        self.pinlist = pinlist
        self.side = side
        self.ground_pins = ground_pins
        self.current_pin = 1
        self.Keithley = Keithley.Keithley(Keithley_port)
        self.Keithley.set_limits()
        if plot:
            self.fig = plt.figure()
            self.fig.figsize=(10, 6)
            self.fig.axes().set_xlabel("Voltage (V)")
            self.fig.axes().set_ylabel("Current (A)")
            self.fig.axes().set_title("Current vs Voltage")
            self.fig.ion()
            self.fig.show()


    def measurement_step(self, pin=False):

        if type(pin) == int and pin < 29:
            self.current_pin = pin

        else:
            print("Zły numer pinu")
            return
        self.MP.connect_pin(pins_signal_a=[self.current_pin], pins_signal_b=[], pins_ground_a=self.ground_pins, pins_ground_b=[])
        # instr = f"S {self.pinlist[self.ground_pins[0]]}{self.side}g {self.pinlist[self.ground_pins[1]]}{self.side}g {self.current_pin}{self.side}s"
        self.Keithley.ON()

        for i in range(self.nsteps):
            self.Keithley.set_voltage(i * self.voltage_step)
            self.meausurements[self.current_pin].append(self.Keithley.measure())
        if self.loop_back:
            for i in range(self.nsteps - 1, -1, -1):
                self.Keithley.set_voltage(i * self.voltage_step)
                self.meausurements[self.current_pin].append(self.Keithley.measure())
        self.fig.axes().plot([i * self.voltage_step for i in range(self.nsteps)], self.meausurements[self.current_pin][0:self.nsteps], label=f"Pin {self.current_pin} - forward")
        if self.loop_back:
            self.fig.axes().plot([i * self.voltage_step for i in range(self.nsteps)], self.meausurements[self.current_pin][self.nsteps:], label=f"Pin {self.current_pin} - backward")
        self.Keithley.OFF()
        print(self.MP.last_instruction())

    def measurement_loop(self):
        for pin in self.pinlist:
            if pin in self.ground_pins:
                continue
            pin_num = input("Podaj numer pinu lub kliknij Enter po zakończeniu pomiaru, żeby przejść do następnego kroku lub e żeby zakończyć:\n")
            try:
                b = int(pin_num)
                if 29 > b >= 0:
                    self.measurement_step(b)
                else:
                    print("Zły numer pinu")
            except :
                if pin_num == "e":
                    break
                elif pin_num =="":
                    self.measurement_step(pin)
                else:
                    print("Zły numer pinu")

        self.inst.write("S")


if __name__ == '__main__':
    mm = MeasurementsManager([i for i in range(12)])
    mm.measurement_loop()
    # print()
