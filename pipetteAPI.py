import logging
from time import sleep
import asyncio

import pyvisa
class PipetteAPI:
    def __init__(self, steps2volume, testmode,resource, verbose=False):
        self.testmode = testmode
        self.inst = resource
        if self.testmode == 0:
            self.write('s')
        self.steps2volume = steps2volume
        self.m0Position = 0
        self.m1Position = 0
        self.m2Position = 0
        self.speedset = {'m0':700, 'm1':3200, 'm2':1000}

        if verbose and not self.testmode:
            self.query('*IDN?')
        self.start()

    async def write(self, command):
        if self.testmode:
            return
        self.inst.write(command)
        sleep(0.1)
    
    async def query(self, command):
        if self.testmode:
            return 0
        q = self.inst.query(command)
        sleep(0.1)
        return q

    def wait_for_stop(self,nr):
       
        if self.testmode:
            sleep(0.1)
            return 1
        while True:
            values = self.query(f'g{nr}')
            if values == '_':
                return 1
            if str(values).split(' ')[0] == '1':
                continue
            if str(values).split(' ')[0] == '0':
                return 0

    async def move2stop(self, motor):
        if self.testmode:
            return
        while self.wait_for_stop(motor):
            self.write(f'{motor} 100 {self.speedset[motor]}')
        
    def stopMotors(self):
        if self.testmode:
            return
        self.write('s')
   

    # def absoluteMoveM0(self, steps, speed = 200):
    #     if self.testmode:
    #         return
    #     self.start()
    #     self.m0Position = 0
    #     self.write(f'm0 {steps} {speed}')
    #     self.m0Position = (self.m0Position + steps)*self.wait_for_stop('0')
    #     self.stopMotors()

    # def absoluteMoveM1(self, steps, speed = 3200):
    #     if self.testmode:
    #         return
    #     self.move2stop('m1')
    #     self.m1Position = 0
    #     self.write(f'm1 {steps} {speed}')
    #     self.m1Position = (self.m1Position + steps)*self.wait_for_stop('1')
    #     self.stopMotors()

    # def absoluteMoveM2(self, steps, speed = 700):
    #     if self.testmode:
    #         return
    #     self.move2stop('m2')
    #     self.m2Position = 0
    #     self.write(f'm2 {steps} {speed}')
    #     self.m2Position = (self.m2Position + steps)*self.wait_for_stop('2')
    #     self.stopMotors()
        
    async def moveM0(self, steps, speed = 200):
        if self.testmode:
            self.m0Position = (self.m0Position + steps)*self.wait_for_stop('0')
            return
        self.write(f'm0 {steps} {speed}')
        self.m0Position = (self.m0Position + steps)*self.wait_for_stop('0')
        self.stopMotors()

    async def moveM1(self, steps, speed = 3200):
        if self.testmode:
            self.m1Position = (self.m1Position + steps)*self.wait_for_stop('1')
            return
        self.write(f'm1 {steps} {speed}')
        self.m1Position = (self.m1Position + steps)*self.wait_for_stop('1')
        self.stopMotors()

    async def moveM2(self, steps, speed = 700):
        if self.testmode:
            self.m2Position = (self.m2Position + steps)*self.wait_for_stop('2')
            return
        self.write(f'm2 {steps} {speed}')
        self.m2Position = (self.m2Position + steps)*self.wait_for_stop('2')
        self.stopMotors()

    async def start(self):
        if self.testmode:
            return
        self.write("s")

        self.moveM0(500000, 300)
        self.moveM2(500000, 1000)
        self.moveM1(500000, 3200)
        self.stopMotors()

    async def resetposition(self):
        if  not self.testmode:
            self.write("s")

        self.moveM0(500000, 300)
        self.moveM2(500000, 1000)
        self.stopMotors()

    async def move2position(self, position):
        self.moveM2(position[2])
        self.moveM0(position[0])
        
    async def oneStepSplitOut(self,position, volume):
        self.move2position(position)
        self.moveM1((volume)/self.steps2volume+100)
        self.moveM1(-50)

    async def onlySplitOut(self,volume):
        self.moveM1(int((volume)/self.steps2volume+100))
        self.moveM1(-50)

    async def oneStepdrawUp(self,position, volume):
        self.moveM1(10000)
        self.moveM1(-50)
        self.move2position(position)
        self.moveM1(-(volume)/self.steps2volume-50)
        self.moveM0(1000)

    async def prepareDrawUp(self):
        self.moveM1(10000)
        self.moveM1(-50)

    async def onlyDrawUp(self, volume):
        value = -(volume)/self.steps2volume
        self.moveM1(int(value))
        sleep(1.0)
        self.moveM0(50000)

    async def close(self):
        self.stopMotors()
        self.inst.close()
        

