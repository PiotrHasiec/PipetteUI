from time import sleep

import pyvisa
class PipetteAPI:
    def __init__(self, steps2volume, resource_name='?*::45905::?*',lib_path='C:\\visa32.dll', verbose=False):
        self.testmode = 0
        try:
            rm = pyvisa.ResourceManager(lib_path)
            list1 = rm.list_resources(resource_name)
            self.inst = rm.open_resource(list1[0], delay=0.1)
            self.write("s")
        except:
            self.testmode = 1
            #print("Error of importing library")
        self.steps2volume = steps2volume
        self.m0Position = 0
        self.m1Position = 0
        self.m2Position = 0
        self.speedset = {'m0':700, 'm1':3200, 'm2':1000}

        if verbose and not self.testmode:
            self.query('*IDN?')
        self.start()

    def write(self, command):
        if self.testmode:
            return
        self.inst.write(command)
        sleep(0.1)
    
    def query(self, command):
        if self.testmode:
            return 0
        q = self.inst.query(command)
        sleep(0.1)
        return q

    def wait_for_stop(self,nr):
       
        if self.testmode:
            return 0
        while True:
            values = self.query(f'g{nr}')
            if values == '_':
                return 1
            if str(values).split(' ')[0] == '1':
                continue
            if str(values).split(' ')[0] == '0':
                return 0

    def move2stop(self, motor):
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
        
    def moveM0(self, steps, speed = 200):
        if self.testmode:
            return
        self.write(f'm0 {steps} {speed}')
        self.m0Position = (self.m0Position + steps)*self.wait_for_stop('0')
        self.stopMotors()

    def moveM1(self, steps, speed = 3200):
        if self.testmode:
            return
        self.write(f'm1 {steps} {speed}')
        self.m1Position = (self.m1Position + steps)*self.wait_for_stop('1')
        self.stopMotors()

    def moveM2(self, steps, speed = 700):
        if self.testmode:
            return
        self.write(f'm2 {steps} {speed}')
        self.m2Position = (self.m2Position + steps)*self.wait_for_stop('2')
        self.stopMotors()

    def start(self):
        if self.testmode:
            return
        self.write("s")

        self.moveM0(500000, 300)
        self.moveM2(500000, 1000)
        self.moveM1(500000, 3200)
        self.stopMotors()

    def move2position(self, position):
        if self.testmode:
            return
        self.moveM0(500000, 300)
        self.moveM2(500000, 1000)
        self.moveM2(position[2])
        self.moveM0(position[0])
        
    def oneStepSplitOut(self,position, volume):
        if self.testmode:
            return
        self.move2position(position)
        self.moveM1((volume)/self.steps2volume+100)
        self.moveM1(-50)

    def onlySplitOut(self,volume):
        if self.testmode:
            return
        self.moveM1((volume)/self.steps2volume+100)
        self.moveM1(-50)

    def oneStepdrawUp(self,position, volume):
        if self.testmode:
            return
        self.moveM1(10000)
        self.moveM1(-50)
        self.move2position(position)
        self.moveM1(-(volume)/self.steps2volume-50)
        self.moveM0(1000)

    def prepareDrawUp(self):
        if self.testmode:
            return
        self.moveM1(10000)
        self.moveM1(-50)

    def onlyDrawUp(self, volume):
        if self.testmode:
            return
        self.moveM1(-(volume)/self.steps2volume-50)
        self.moveM0(1000)

    def close(self):
        if self.testmode:
            return
        self.stopMotors()
        self.inst.close()
        

