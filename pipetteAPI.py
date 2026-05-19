import pyvisa
class PipetteAPI:
    def __init__(self, steps2volume, resource_name='?*::45905::?*',lib_path='C:\\Windows\\System32\\visa32.dll', verbose=False):
        self.testmode = 0
        try:
            rm = pyvisa.ResourceManager(lib_path)
            list1 = rm.list_resources(resource_name)
            self.inst = rm.open_resource(list1[0])
            self.inst.write("s")
        except:
            self.testmode = 1
            print("Error of importing library")
        self.steps2volume = steps2volume
        self.m0Position = 0
        self.m1Position = 0
        self.m2Position = 0
        self.speedset = {'M0':3200, 'M1':1000, 'M2':1000}

        if verbose and not self.testmode:
            print(self.inst.query('*IDN?'))

    def wait_for_stop(self):
        stopset = ['_','A','B','C','D','E','F','G','H','I','J']
        if self.testmode:
            return 0
        while True:
            values = self.inst.query_ascii_values('g', separator='$')
            print(values)
            if values in stopset:
                if not values == '_':
                    return 1
                return 0

    def move2stop(self, motor):
        if self.testmode:
            return
        while self.wait_for_stop():
            self.inst.write(f'{motor} 100 {self.speedset[motor]}')
        
    def stop(self):
        if self.testmode:
            return
        self.inst.write('s')
    
    def stop(self,motor):
        if self.testmode:
            return
        self.inst.write(f's{motor}')
    

    def absoluteMoveM0(self, steps, speed = 3200):
        if self.testmode:
            return
        self.move2stop('M0')
        self.m0Position = 0
        self.inst.write(f'M0 {steps} {speed}')
        self.m0Position = (self.m0Position + steps)*self.wait_for_stop()
        self.stop(0)

    def absoluteMoveM1(self, steps, speed = 1000):
        if self.testmode:
            return
        self.move2stop('M1')
        self.m1Position = 0
        self.inst.write(f'M1 {steps} {speed}')
        self.m1Position = (self.m1Position + steps)*self.wait_for_stop()
        self.stop(1)

    def absoluteMoveM2(self, steps, speed = 1000):
        if self.testmode:
            return
        self.move2stop('M2')
        self.m2Position = 0
        self.inst.write(f'M2 {steps} {speed}')
        self.m2Position = (self.m2Position + steps)*self.wait_for_stop()
        self.stop(2)
        
    def moveM0(self, steps, speed = 3200):
        if self.testmode:
            return
        self.inst.write(f'M0 {steps} {speed}')
        self.m0Position = (self.m0Position + steps)*self.wait_for_stop()
        self.stop(0)

    def moveM1(self, steps, speed = 1000):
        if self.testmode:
            return
        self.inst.write(f'M1 {steps} {speed}')
        self.m1Position = (self.m1Position + steps)*self.wait_for_stop()
        self.stop(1)

    def moveM2(self, steps, speed = 1000):
        if self.testmode:
            return
        self.inst.write(f'M2 {steps} {speed}')
        self.m2Position = (self.m2Position + steps)*self.wait_for_stop()
        self.stop(2)

    def start(self):
        if self.testmode:
            return
        self.inst.write("s")
        self.moveM0(-50, 3200)
        self.moveM0(500, 3200)
        self.moveM0(-100, 3200)

        self.moveM1(-50, 3200)
        self.moveM1(500, 3200)
        self.moveM1(-100, 3200)

        self.moveM2(-50, 3200)
        self.moveM2(500, 3200)
        self.moveM2(-100, 3200)

        self.stop()
    def move2position(self, position):
        if self.testmode:
            return
        self.absoluteMoveM2(position[2])
        self.absoluteMoveM1(position[1])
        
    def oneStepSplitOut(self,position, volume):
        if self.testmode:
            return
        self.absoluteMoveM2(position[2])
        self.absoluteMoveM1(position[1])
        self.moveM0((volume)/self.steps2volume+50)
        self.moveM0(-50)

    def onlySplitOut(self,volume):
        if self.testmode:
            return
        self.moveM0((volume)/self.steps2volume+50)
        self.moveM0(-50)

    def oneStepdrawUp(self,position, volume):
        if self.testmode:
            return
        self.moveM0(-100)
        self.moveM0(50)
        self.absoluteMoveM2(position[2])
        self.absoluteMoveM1(position[1])
        self.moveM0(-(volume)/self.steps2volume+50)
        self.absoluteMoveM0(-50)

    def prepareDrawUp(self):
        if self.testmode:
            return
        self.moveM0(-100)
        self.moveM0(50)

    def onlyDrawUp(self, volume):
        if self.testmode:
            return
        self.moveM0(-(volume)/self.steps2volume+50)
        self.absoluteMoveM0(-50)
        

