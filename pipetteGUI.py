import PyQt5 as qt
from PyQt5 import QtWidgets
import pipetteAPI
import json
from PyQt5.QtWidgets import QApplication, QComboBox, QFileDialog, QFormLayout, QGridLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QSlider, QTabWidget, QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg 
from matplotlib.figure import Figure
import numpy as np
from PyQt5 import QtCore 

class MplCanvas(FigureCanvasQTAgg,):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        super(MplCanvas, self).__init__(fig)
        self.scatter_x=None
        self.scatter_y=None
        self.hline = None
        self.vline = None
    def scatter_values(self,scatter_x,scatter_y):
        self.scatter_y = scatter_y
        self.scatter_x = scatter_x
        self.err_plot = self.axes.plot(scatter_x,scatter_y)
        self.axes.set_ylim(0,np.max(scatter_y))
        self.axes.set_xlim(0,np.array(scatter_y).shape[0])


class PipetteGUI(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.filename = ""
        self.pipette = pipetteAPI.PipetteAPI(steps2volume=0.1, verbose=True)
        self.SamplePosition = None
        self.TubePosition = None
        self.initPosition()
        self.setWindowTitle('Pipette Control')
        self.setGeometry(100, 100, 400, 300)
        self.createMenu()
        self.createTabs()
        

        
    
    # Funkcja dodająca pasek menu do okna
    def createMenu(self):
        self.menu = self.menuBar()
        self.FileMenu = self.menu.addMenu("File")
        self.FileMenu.addAction('Exit', self.close)
        self.FileMenu.addAction('Wybierz plik ustawień', self.settingchoose)


    
    def settingchoose(self):
      fileName, selectedFilter = QFileDialog.getOpenFileName(self, "Wybierz plik ustawień",  "Początkowa nazwa pliku", "All Files (*);;XML Files (*.xml);; JSON Files (*.json)")
      if fileName:
            json_file = open(fileName)
            self.settings = json.load(json_file)
            self.SamplePosition = self.settings["SamplePosition"]
            self.TubePosition = self.settings["TubePosition"]
            self.m0speed  = self.settings["m0speed"]
            self.m1speed  = self.settings["m1speed"]
            self.m2speed  = self.settings["m2speed"]
            self.steps2volume = self.settings["steps2volume"]
            self.pipette.steps2volume = self.steps2volume
            self.show()    
       
    def initPosition(self):
        self.M0Position = 0
        self.M1Position = 0
        self.M2Position = 0
        #print("Initializing pipette position")
    
    # Funkcja dodająca wenętrzeny widżet do okna
    def createTabs(self):
        # Tworzenie widżetu posiadającego zakładki
        self.tabs = QTabWidget()
        
        # Stworzenie osobnych widżetów dla zakładek
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.tab_3 = QWidget()
        
        # Dodanie zakładek do widżetu obsługującego zakładki
        # Zakładka 1
        self.tabs.addTab(self.tab_1, "Ręczna kalibracja pozycji pipety") 
        self.tab_1.setLayout(self.Z1Init())

        # Zakładka 2
        self.tabs.addTab(self.tab_2, "Ręczna obsługa pipety")
        self.tab_2.setLayout(self.Z2Init())
        
        self.setCentralWidget(self.tabs)
    def Z2Init(self):
        layout = QGridLayout()
        self.drawUpunits = QComboBox()
        self.drawUpunits.addItem("μL")
        self.drawUpunits.addItem("steps")
        self.spitOutunits = QComboBox()
        self.spitOutunits.addItem("μL")
        self.spitOutunits.addItem("steps")
        self.GetButtonUp = QPushButton('Draw up the solution', self)
        self.M1ButtonUp = QPushButton('Spit out the solution', self)
        self.GetButtonUp.clicked.connect(self.drawUp)
        self.M1ButtonUp.clicked.connect(self.spitOut)
        layout.addWidget(self.GetButtonUp,0,0)
        layout.addWidget(self.M1ButtonUp,1,0)

        self.drawUpVolume = QLineEdit()
        self.drawUpVolume.setPlaceholderText("Volume to draw up (μL)")

        self.spitOutVolume = QLineEdit()
        self.spitOutVolume.setPlaceholderText("Volume to spit out (μL)")


        layout.addWidget(self.drawUpVolume,0,1)
        layout.addWidget(self.spitOutVolume,1,1)
        layout.addWidget(self.drawUpunits,0,2)
        layout.addWidget(self.spitOutunits,1,2)
        self.positonlabel2 = QLabel(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.samplePositonlabel2 = QLabel(f"Sample position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.tubePositonlabel2 = QLabel(f"Tube position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        
        layout.addWidget(self.positonlabel2,2,0,1,4)
        layout.addWidget(self.samplePositonlabel2,3,0,1,4)
        layout.addWidget(self.tubePositonlabel2,4,0,1,4)

        return layout

    def drawUp(self):
        if self.drawUpVolume.text().isdigit():
            volume = int(self.drawUpVolume.text())
        else:
            volume = 50
            self.drawUpVolume.setText("50")
        #print("Prepare draw up")
        self.pipette.prepareDrawUp()
        if self.TubePosition is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Oh no!')
            if error_dialog.exec_():
                return

        #print(f"Go to position of Tube: {self.TubePosition}")
        self.pipette.move2position(position=self.TubePosition)
        #print(f"Drawing up the solution: {volume} {self.drawUpunits.currentText()}")
        self.pipette.onlyDrawUp(volume=volume)
        # self.pipette.drawUp(self.TubePosition,volume)
        self.M0Position = self.pipette.m0Position
        self.M1Position = self.pipette.m1Position
        self.M2Position = self.pipette.m2Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")

        
        
    def spitOut(self):
        if self.spitOutVolume.text().isdigit():
            volume = int(self.spitOutVolume.text())
        else:
            volume = 50
            self.spitOutVolume.setText("50")
        if self.TubePosition is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Oh no!')
            if error_dialog.exec_():
                return
        #print(f"Go to position of Sample: {self.SamplePosition}")
        self.pipette.move2position(self.SamplePosition)
        #print(f"Spitting out the solution: {volume} {self.spitOutunits.currentText()}")
        self.pipette.onlySplitOut(volume)
        self.M0Position = self.pipette.m0Position
        self.M1Position = self.pipette.m1Position
        self.M2Position = self.pipette.m2Position

        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        # self.pipette.splitOut(volume,speed=self.m1speed)

    def Z1Init(self):


        # Create layout
        layout = QGridLayout()

        # Create buttons for pipette control
        self.M0ButtonUp = QPushButton('Motor 1 Up', self)
        self.M1ButtonUp = QPushButton('Motor 2 Up', self)
        self.M2ButtonUp = QPushButton('Motor 3 Up', self)

        self.M0ButtonDown = QPushButton('Motor 1 Down', self)
        self.M1ButtonDown = QPushButton('Motor 2 Down', self)
        self.M2ButtonDown = QPushButton('Motor 3 Down', self)
        text01 = QLabel('Ustawienia pozycji pipety')
        text01.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        text2 = QLabel('Liczba kroków do przesunięcia pipety')
        text2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        text3 = QLabel('Mnożnik kroków')
        text3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.SaveSamplePositionButton = QPushButton('Set current postion for Sample', self)
        self.SaveSamplePositionButton.clicked.connect(self.saveSample)
        self.SaveTubePositionButton = QPushButton('Set current postion for Tube', self)
        self.SaveTubePositionButton.clicked.connect(self.saveTube)


        #Create forms
        self.M0Steps = QLineEdit()
        self.M0Steps.setPlaceholderText("Steps for Motor 1")
        self.M1Steps = QLineEdit()
        self.M1Steps.setPlaceholderText("Steps for Motor 2")
        self.M2Steps = QLineEdit()
        self.M2Steps.setPlaceholderText("Steps for Motor 3")
        self.M0Speed = QLineEdit()
        self.M0Speed.setPlaceholderText("Speed for Motor 1")
        self.M1Speed = QLineEdit()
        self.M1Speed.setPlaceholderText("Speed for Motor 2")
        self.M2Speed = QLineEdit()
        self.M2Speed.setPlaceholderText("Speed for Motor 3")

        # Connect buttons to functions
        self.M0ButtonUp.clicked.connect(self.moveM0Up)
        self.M1ButtonUp.clicked.connect(self.moveM1Up)
        self.M2ButtonUp.clicked.connect(self.moveM2Up)
        self.M0ButtonDown.clicked.connect(self.moveM0Down)
        self.M1ButtonDown.clicked.connect(self.moveM1Down)
        self.M2ButtonDown.clicked.connect(self.moveM2Down)

        self.positonlabel = QLabel(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.samplePositonlabel = QLabel(f"Sample position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.tubePositonlabel = QLabel(f"Tube position: {self.M0Position}, {self.M1Position}, {self.M2Position}")

        self.positonlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 

        # Add buttons to layout
        layout.addWidget(self.M0ButtonUp,1,0)
        layout.addWidget(self.M1ButtonUp,2,0)
        layout.addWidget(self.M2ButtonUp,3,0)
        layout.addWidget(self.M0ButtonDown,1,1)
        layout.addWidget(self.M1ButtonDown,2,1)
        layout.addWidget(self.M2ButtonDown,3,1)
      
        layout.addWidget(self.M0Steps,1,2)
        layout.addWidget(self.M1Steps,2,2)
        layout.addWidget(self.M2Steps,3,2)

        layout.addWidget(self.M0Speed,1,3)
        layout.addWidget(self.M1Speed,2,3)  
        layout.addWidget(self.M2Speed,3,3)

        layout.addWidget(self.SaveSamplePositionButton,4,0,1,4)
        layout.addWidget(self.SaveTubePositionButton,5,0,1,4)

        layout.addWidget(text01,0,0,1,2)
        layout.addWidget(text2,0,2,1,1)
        layout.addWidget(text3,0,3,1,1)
        layout.addWidget(self.positonlabel,6,0,1,4)
        layout.addWidget(self.samplePositonlabel,7,0,1,4)
        layout.addWidget(self.tubePositonlabel,8,0,1,4)


        # Set the layout for the widget
        return layout

    def moveM0Up(self):
        if self.M0Steps.text().isdigit() and self.M0Speed.text().isdigit():
            self.m0steps = int(self.M0Steps.text())
            self.m0speed = int(self.M0Speed.text())
        else:
            self.m0steps = 2000
            self.m0speed = 200
            self.M0Steps.setText("2000")
            self.M0Speed.setText("200")
        self.pipette.moveM0(self.m0steps,self.m0speed)
        self.M0Position = self.pipette.m0Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        #print(f"Moving pipette up by {self.m0steps} steps at speed {self.m0speed}")

    def moveM1Up(self):
        if self.M1Steps.text().isdigit() and self.M1Speed.text().isdigit():
            self.m1steps = int(self.M1Steps.text())
            self.m1speed = int(self.M1Speed.text())
        else:
            self.m1steps = 50
            self.m1speed = 3200
            self.M1Steps.setText("50")
            self.M1Speed.setText("3200")
        self.pipette.moveM1(-self.m1steps,self.m1speed)
        self.M1Position = self.pipette.m1Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        #print(f"Moving pipette down by {self.m1steps} steps at speed {self.m1speed}")

    def moveM2Up(self):
        if self.M2Steps.text().isdigit() and self.M2Speed.text().isdigit():
            self.m2steps = int(self.M2Steps.text())
            self.m2speed = int(self.M2Speed.text())
        else:
            self.m2steps = 100
            self.m2speed = 1000
            self.M2Steps.setText("100")
            self.M2Speed.setText("1000")
        self.pipette.moveM2(-self.m2steps,self.m2speed)
        self.M2Position = self.pipette.m2Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        #print(f"Moving pipette left by {self.m2steps} steps at speed {self.m2speed}")

    def moveM0Down(self):
        if self.M0Steps.text().isdigit() and self.M0Speed.text().isdigit():
            self.m0steps = int(self.M0Steps.text())
            self.m0speed = int(self.M0Speed.text())
        else:
            self.m0steps = 2000
            self.m0speed = 200
            self.M0Steps.setText("2000")
            self.M0Speed.setText("700")
        self.pipette.moveM0(-self.m0steps,self.m0speed)
        self.M0Position = self.pipette.m0Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        #print(f"Moving pipette down by {-self.m0steps} steps at speed {self.m0speed}")

    def moveM1Down(self):
        if self.M1Steps.text().isdigit() and self.M1Speed.text().isdigit():
            self.m1steps = int(self.M1Steps.text())
            self.m1speed = int(self.M1Speed.text())
        else:
            self.m1steps = 50
            self.m1speed = 3200
            self.M1Steps.setText("50")
            self.M1Speed.setText("3200")
        self.M1Position -= self.m1steps
        self.pipette.moveM1(self.m1steps,self.m1speed)
        self.M1Position = self.pipette.m1Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")

        #print(f"Moving pipette down by {-self.m1steps} steps at speed {self.m1speed}")

    def moveM2Down(self):
        if self.M2Steps.text().isdigit() and self.M2Speed.text().isdigit():
            self.m2steps = int(self.M2Steps.text())
            self.m2speed = int(self.M2Speed.text())
        else:
            self.m2steps = 100
            self.m2speed = 1000
            self.M2Steps.setText("100")
            self.M2Speed.setText("1000")
        self.pipette.moveM2(self.m2steps,self.m2speed)
        self.M2Position = self.pipette.m2Position
        self.positonlabel.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.positonlabel2.setText(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")

        #print(f"Moving pipette left by {-self.m2steps} steps at speed {self.m2speed}")

    def saveSample(self):
        #print(f"Saving current position as Sample position {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.M0Position = self.pipette.m0Position
        self.M1Position = self.pipette.m1Position
        self.M2Position = self.pipette.m2Position
        self.SamplePosition = (self.M0Position, self.M1Position, self.M2Position)
        self.samplePositonlabel.setText(f"Sample position: {self.SamplePosition}")
        self.samplePositonlabel2.setText(f"Sample position: {self.SamplePosition}")


    def saveTube(self):
        #print(f"Saving current position as Tube position {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.M0Position = self.pipette.m0Position
        self.M1Position = self.pipette.m1Position
        self.M2Position = self.pipette.m2Position
        self.TubePosition = (self.M0Position, self.M1Position, self.M2Position)
        self.tubePositonlabel.setText(f"Tube position: {self.TubePosition}")
        self.tubePositonlabel2.setText(f"Tube position: {self.TubePosition}")
    def __delete__(self, instance):
        self.pipette.stopMotors()
        self.pipette.close()


if __name__ == '__main__':
    app = QApplication([])
    gui = PipetteGUI()
    gui.show()
    app.exec_()