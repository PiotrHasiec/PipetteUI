import pyvisa
import numpy as np


class MeasurementsManager:
    def __init__(self, pinlist: list, side='a', ground_pins=[0, 5, 6, 11], resource_name='?*::45905::?*',
                 lib_path='C:\\Windows\\System32\\visa32.dll', verbose=False):
        rm = pyvisa.ResourceManager(lib_path)
        list1 = rm.list_resources(resource_name)
        self.inst = rm.open_resource(list1[0])
        self.inst.write("S")
        self.pinlist = pinlist
        self.side = side
        self.ground_pins = ground_pins
        if verbose:
            print(self.inst.query('*IDN?'))

        self.current_pin = 1

    def measurement_step(self, pin=False):

        if type(pin) == int and pin < 29:
            self.current_pin = pin

        else:
            print("Zły numer pinu")
            return
        instr = f"S {self.pinlist[self.ground_pins[0]]}{self.side}g {self.pinlist[self.ground_pins[1]]}{self.side}g {self.current_pin}{self.side}s"
        print(instr)
        self.inst.write(instr)

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

        input("kliknij Enter po zakończeniu pomiarów\n")
        self.inst.write("S")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mm = MeasurementsManager([i for i in range(12)])
    mm.measurement_loop()
    # print()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
