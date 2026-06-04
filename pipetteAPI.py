import logging
from PyQt5 import QtTest
import io

import pyvisa

class Instruction:
    def __init__(self, pipette_name, instruction_type, position = None, position_name = None, value = None,speedset = [70,2000,500]):
        self.pipette_name = pipette_name
        self.instruction_type = instruction_type
        self.position = position
        self.position_name = position_name
        self.value = value
        self.speedset = speedset

class PipetteAPI:
    def __init__(self, steps2volume, testmode,resource, verbose=False):
        self.testmode = testmode
        self.inst = resource
        if self.testmode == 0:
            self.write('s')
        self.name2function = {"Move to position": self.move2position, "Prepare draw up": self.prepareDrawUp, "Draw up": self.onlyDrawUp, "Spit out": self.onlySplitOut, "Reset position": self.resetposition, "Move Motor M0": self.moveM0, "Move Motor M1": self.moveM1, "Move Motor M2": self.moveM2}
        self.steps2volume = steps2volume
        self.position = (0,0,0)
        self.speedset = {'m0':80, 'm1':2000, 'm2':700}
        if verbose and not self.testmode:
            self.query('*IDN?')
        self.start()

    def write(self, command):
        if self.testmode:
            QtTest.QTest.qWait(100)
            
        self.inst.write(command)
        QtTest.QTest.qWait(100)

    def query(self, command):
        if self.testmode:
            QtTest.QTest.qWait(100) 
            return 0
        q = self.inst.query(command)
        QtTest.QTest.qWait(100)
        return q

    def wait_for_stop(self,nr):
       
        if self.testmode:
            QtTest.QTest.qWait(100)
            return 1
        while True:
            values = self.query(f'g{nr}')
            if values == '_':
                return 1
            if str(values).split(' ')[0] == '1':
                continue
            if str(values).split(' ')[0] == '0':
                if nr == '0':
                    self.position = (0, self.position[1], self.position[2])
                if nr == '1':
                    self.position = (self.position[0], 0, self.position[2])
                if nr == '2':
                    self.position = (self.position[0], self.position[1], 0)
                return 0

    def move2stop(self, motor):
        if self.testmode:
            QtTest.QTest.qWait(100)
            return
        while self.wait_for_stop(motor):
            self.write(f'{motor} 100 {self.speedset[motor]}')
        
    def stopMotors(self):
        if self.testmode:
            QtTest.QTest.qWait(100) 
            return
        self.write('s')
   
        
    def moveM0(self, steps, speed = None):
        if self.testmode:
            self.position = (self.position[0] + steps, self.position[1], self.position[2])
            self.wait_for_stop('0')
            return
        if speed is None:
            speed = self.speedset['m0']
        self.write(f'm0 {steps} {speed}')
        self.position = (self.position[0] + steps, self.position[1], self.position[2])
        self.wait_for_stop('0')
        self.stopMotors()

    def moveM1(self, steps, speed = None):
        if self.testmode:
            self.position = (self.position[0], self.position[1] + steps, self.position[2])
            self.wait_for_stop('1')
            return
        if speed is None:
            speed = self.speedset['m1']
        self.write(f'm1 {steps} {speed}')
        self.position = (self.position[0], self.position[1] + steps, self.position[2])
        self.wait_for_stop('1')
        self.stopMotors()

    def moveM2(self, steps, speed = None):
        if self.testmode:
            self.position = (self.position[0], self.position[1], self.position[2] + steps)
            self.wait_for_stop('2')
            return
        if speed is None:
            speed = self.speedset['m2']
        self.write(f'm2 {steps} {speed}')
        self.position = (self.position[0], self.position[1], self.position[2] + steps)
        self.wait_for_stop('2')
        self.stopMotors()

    def start(self):
        if self.testmode:
            return
        self.write("s")

        self.moveM0(500000, self.speedset['m0'])
        self.moveM2(500000, self.speedset['m2'])
        self.moveM1(500000, self.speedset['m1'])
        self.stopMotors()

    def resetposition(self):
        if  not self.testmode:
            self.write("s")

        self.moveM0(500000, self.speedset['m0'])
        self.moveM2(500000, self.speedset['m2'])
        self.stopMotors()

    def move2position(self, position):
        self.moveM2(position[2]-self.position[2], self.speedset['m2'])
        self.moveM0(position[0]-self.position[0], self.speedset['m0'])

    def oneStepSplitOut(self,position, volume):
        self.move2position(position)
        self.moveM1((volume)/self.steps2volume+100, self.speedset['m1'])
        self.moveM1(-50)

    def onlySplitOut(self,volume):
        self.moveM1(int((volume)/self.steps2volume+100), self.speedset['m1'])
        self.moveM1(-50)

    def oneStepdrawUp(self,position, volume):
        self.moveM1(10000, self.speedset['m1'])
        self.moveM1(-50, self.speedset['m1'])
        self.move2position(position)
        self.moveM1(-(volume)/self.steps2volume-50, self.speedset['m1'])
        self.moveM0(1000)

    def prepareDrawUp(self):
        self.moveM1(10000, self.speedset['m1'])
        self.moveM1(-50, self.speedset['m1'])

    def onlyDrawUp(self, volume):
        value = -(volume)/self.steps2volume
        self.moveM1(int(value), self.speedset['m1'])
        QtTest.QTest.qWait(1000)
        self.moveM0(50000)

    def getPosition(self):
        return self.position
    
    def runInstruction(self, instruction):
            if instruction.instruction_type == "Move to position":
                self.name2function[instruction.instruction_type](instruction.position)
            elif instruction.instruction_type in ["Prepare draw up", "Reset position"]:
                self.name2function[instruction.instruction_type]()
            elif instruction.instruction_type in ["Draw up", "Spit out","Move Motor M0", "Move Motor M1", "Move Motor M2"]:
                self.name2function[instruction.instruction_type](instruction.value)


    def close(self):
        self.resetposition()
        self.stopMotors()
        self.inst.close()
    def __del__(self):
        self.close()
        super().__del__()
        

