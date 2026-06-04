import sys
import pyvisa
import serial
from PyQt5 import QtWidgets, QtCore, QtTest
import pipetteAPI
import json
from PyQt5.QtWidgets import QApplication, QComboBox, QFileDialog,  QGridLayout, QLabel, QLineEdit,  QMainWindow,  QTabWidget, QWidget,  QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg 
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QIcon
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"), # Zapis do pliku
        logging.StreamHandler(sys.stdout)                # Próba wypisania na konsolę
    ]
)
logging.info("Application started")

class instruction:
    def __init__(self, pipette_name, instruction_type, position_name = None, value = None,speedset = [70,2000,500]):
        self.pipette_name = pipette_name
        self.instruction_type = instruction_type
        self.position_name = position_name
        self.value = value
        self.speedset = speedset


class PipetteGUI(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        self.pipette_dixt = {}
        self.timer = time.time()
        self.spincoater = None
        try:
            rm = pyvisa.ResourceManager('C:\\visa32.dll')
            list_of_pippetes = rm.list_resources('?*::45905::?*')
            for i,inst in enumerate(list_of_pippetes):
                inst = rm.open_resource(inst)
                self.pipette_dixt[f'pipette {i}'] = pipetteAPI.PipetteAPI(steps2volume=0.1, resource= inst, testmode=0)
        except:
            for i in range(3):
                self.pipette_dixt[f"pipette test {i}"] = pipetteAPI.PipetteAPI(steps2volume=0.1, resource= None,testmode=1)
            logging.info(f"Error of importing library or connecting to the device. Running in test mode.")
    
        try:
            self.spincoater = serial.Serial('COM5', 19200, timeout=1)
        except:
            logging.info(f"Error connecting to the spincoater. Spincoater functions will be unavailable.")


        self.filename = ""
        self.positionsSet = {"Initial": (0,0,0), "Sample": (0,0,0), "Tube": (0,0,0)}
        self.initPosition()
        self.setWindowTitle('Pipette Control')
        self.setGeometry(100, 100, 800, 500)
        self.createMenu()
        self.createTabs()
        

        
    
    # Funkcja dodająca pasek menu do okna
    def createMenu(self):
        self.menu = self.menuBar()
        self.FileMenu = self.menu.addMenu("File")
        self.FileMenu.addAction('Exit', self.close)
        self.FileMenu.addAction('Wybierz plik ustawień', self.settingchoose)
        self.FileMenu.addAction('Zapisz plik ustawień', self.settingsave)
        self.FileMenu.addAction('Zapisz program', self.programsave)
        self.FileMenu.addAction('Wczytaj program', self.programload)

    def programsave(self):
        fileName, selectedFilter = QFileDialog.getSaveFileName(self, "Wybierz plik ustawień",  "settings", "JSON Files (*.json);;All Files (*);;XML Files (*.xml)")
        if fileName:
            jsondict = dict()#zrobić zapis z wszystkich pipet
            jsondict["PositionsSet"] = dict()
            jsondict["PipetteSettings"] = dict()
            for position_name, position in self.positionsSet.items():
                jsondict["PositionsSet"][position_name] = position
            for name,inst in self.pipette_dixt.items():
                jsondict["PipetteSettings"][name] = dict()
                jsondict["PipetteSettings"][name]["m0speed"] = inst.speedset['m0']
                jsondict["PipetteSettings"][name]["m1speed"] = inst.speedset['m1']
                jsondict["PipetteSettings"][name]["m2speed"] = inst.speedset['m2']
                jsondict["PipetteSettings"][name]["steps2volume"] = inst.steps2volume
            jsondict["Instructions"] = []
            for row_index in range(self.instructionsTabel.rowCount()):
                instruction = []
                for col_index in range(self.instructionsTabel.columnCount()):
                    if col_index < 4:
                        if self.instructionsTabel.item(row_index, col_index) is not None:
                            instruction.append(self.instructionsTabel.item(row_index, col_index).text())
                jsondict["Instructions"].append(instruction)

            with open(fileName, 'w') as file:
                json.dump(jsondict,file)

    def settingsave(self):
        fileName, selectedFilter = QFileDialog.getSaveFileName(self, "Wybierz plik ustawień",  "settings", "JSON Files (*.json);;All Files (*);;XML Files (*.xml)")
        if fileName:
            jsondict = dict()#zrobić zapis z wszystkich pipet
            jsondict["PositionsSet"] = dict()
            jsondict["PipetteSettings"] = dict()
            for position_name, position in self.positionsSet.items():
                jsondict["PositionsSet"][position_name] = position
            for name,inst in self.pipette_dixt.items():
                jsondict["PipetteSettings"][name] = dict()
                jsondict["PipetteSettings"][name]["m0speed"] = inst.speedset['m0']
                jsondict["PipetteSettings"][name]["m1speed"] = inst.speedset['m1']
                jsondict["PipetteSettings"][name]["m2speed"] = inst.speedset['m2']
                jsondict["PipetteSettings"][name]["steps2volume"] = inst.steps2volume
            with open(fileName, 'w') as file:
                json.dump(jsondict,file)
            # file.write(jsondict)
    def settingchoose(self):
      fileName, selectedFilter = QFileDialog.getOpenFileName(self, "Wybierz plik ustawień",  "settings", "JSON Files (*.json);;All Files (*);;XML Files (*.xml)")
      if fileName:
            json_file = open(fileName)
            self.settings = json.load(json_file)
            self.positionsSet = self.settings["PositionsSet"]
            for name in self.settings["PipetteSettings"]:#zrobić niezależne dla każdej pipetki
                self.pipette_dixt[name].speedset['m0'] = self.settings["PipetteSettings"][name]["m0speed"]
                self.pipette_dixt[name].speedset['m1'] = self.settings["PipetteSettings"][name]["m1speed"]
                self.pipette_dixt[name].speedset['m2'] = self.settings["PipetteSettings"][name]["m2speed"]
                self.pipette_dixt[name].steps2volume = self.settings["PipetteSettings"][name]["steps2volume"]

            self.steps2volumeLabel.setText(f"Current steps2volume {self.pipette_dixt[name].steps2volume} stepes/μL")
            self.samplePositonlabel.setText(f"Sample position: {self.positionsSet["Sample"]}")
            self.samplePositonlabel2.setText(f"Sample position: {self.positionsSet["Sample"]}")
            self.tubePositonlabel.setText(f"Tube position: {self.positionsSet["Tube"]}")
            self.tubePositonlabel2.setText(f"Tube position: {self.positionsSet["Tube"]}")
            self.positionNameList.clear()
            for position_name in self.positionsSet.keys():
                self.positionNameList.addItem(position_name)
            self.show()   

    def programload(self):
        fileName, selectedFilter = QFileDialog.getOpenFileName(self, "Wybierz plik ustawień",  "settings", "JSON Files (*.json);;All Files (*);;XML Files (*.xml)")
        if fileName:
            json_file = open(fileName)
            self.settings = json.load(json_file)
            self.instructionsTabel.setRowCount(0)
            for instruction in self.settings["Instructions"]:
                row_position = self.instructionsTabel.rowCount()
                self.instructionsTabel.insertRow(row_position)
                for col_index, value in enumerate(instruction):
                    self.instructionsTabel.setItem(row_position, col_index, QTableWidgetItem(value))

                deleteButton = QtWidgets.QPushButton(QIcon("delete.svg"), "")
                deleteButton.clicked.connect(self.deleteClicked)

                moveUpButton = QtWidgets.QPushButton(QIcon("up.svg"), "")
                moveUpButton.clicked.connect(self.moveUpClicked)

                moveDownButton = QtWidgets.QPushButton(QIcon("down.svg"), "")
                moveDownButton.clicked.connect(self.moveDownClicked)
                self.instructionsTabel.setCellWidget(row_position, 4, deleteButton)
                self.instructionsTabel.setCellWidget(row_position, 5, moveUpButton)
                self.instructionsTabel.setCellWidget(row_position, 6, moveDownButton)


            self.positionsSet = self.settings["PositionsSet"]
            for name in self.settings["PipetteSettings"]:#zrobić niezależne dla każdej pipetki
                self.pipette_dixt[name].speedset['m0'] = self.settings["PipetteSettings"][name]["m0speed"]
                self.pipette_dixt[name].speedset['m1'] = self.settings["PipetteSettings"][name]["m1speed"]
                self.pipette_dixt[name].speedset['m2'] = self.settings["PipetteSettings"][name]["m2speed"]
                self.pipette_dixt[name].steps2volume = self.settings["PipetteSettings"][name]["steps2volume"]

            self.steps2volumeLabel.setText(f"Current steps2volume {self.pipette_dixt[name].steps2volume} stepes/μL")
            self.samplePositonlabel.setText(f"Sample position: {self.positionsSet["Sample"]}")
            self.samplePositonlabel2.setText(f"Sample position: {self.positionsSet["Sample"]}")
            self.tubePositonlabel.setText(f"Tube position: {self.positionsSet["Tube"]}")
            self.tubePositonlabel2.setText(f"Tube position: {self.positionsSet["Tube"]}")
            self.positionNameList.clear()
            for position_name in self.positionsSet.keys():
                self.positionNameList.addItem(position_name)

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

        # Zakładka 3
        self.tabs.addTab(self.tab_3, "Moduł ogólny")
        self.tab_3.setLayout(self.Z3Init())
        
        self.setCentralWidget(self.tabs)

    def changeSteps2Volume(self):
        try:
            name = self.pipetteComboBoxForInstructionZ2.currentText() 
            val = float(self.steps2volumeForms.text())
            self.pipette_dixt[name].steps2volume = val
            self.steps2volumeLabel.setText(f"Current steps2volume {self.pipette_dixt[name].steps2volume} stepes/μL")
        except:
            self.steps2volumeForms.setText('')
            self.steps2volumeForms.setPlaceholderText("Proszę podać liczbę")
            logging.warning("Invalid input for steps2volume. Please enter a name.")

    def Z3Init(self):
        layout = QGridLayout()
        self.instructionsTabel = QTableWidget()
        self.instructionsTabel.setColumnCount(7)
        self.instructionsTabel.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)
        self.instructionsTabel.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.instructionsTabel.setHorizontalHeaderLabels(["Pipeta","Instruction type", "Position name", "Volume/steps", "Delete","Up", "Down"])
        self.instructionsTabel.setColumnWidth(4,60)
        self.instructionsTabel.setColumnWidth(5,60)
        self.instructionsTabel.setColumnWidth(6,60)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.instructionsTabel.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.Fixed)


        self.instructionsTabel
        self.pipetteComboBoxForInstructionZ3 = QComboBox()
        for name,inst in self.pipette_dixt.items():
            self.pipetteComboBoxForInstructionZ3.addItem(name)
            
        self.insertToolBar = QGroupBox("Dodaj instrukcję")
    
        self.insertToolBarLayout = QVBoxLayout()    
        self.instructionType = QComboBox()
        self.instructionType.addItem("Move to position")
        self.instructionType.addItem("Prepare draw up")
        self.instructionType.addItem("Draw up")
        self.instructionType.addItem("Spit out")
        self.instructionType.addItem("Reset position")
        self.instructionType.addItem("Move Motor M0")
        self.instructionType.addItem("Move Motor M1")
        self.instructionType.addItem("Move Motor M2")
        self.instructionType.addItem("Start Timer")
        self.instructionType.addItem("Reset timer and wait")
        self.instructionType.addItem("Wait")
        self.instructionType.addItem("Run spincoater")
        self.instructionType.addItem("Prepare spincoater")
        self.instructionType.currentTextChanged.connect(self.instructionTypeChanged)

        self.positionNameList = QComboBox()
        self.positionNameList.addItem("Sample")
        self.positionNameList.addItem("Tube")
        self.volume = QLineEdit()
        self.volume.setPlaceholderText("Objętość w μL")
        self.addInstructionButton = QPushButton("Dodaj instrukcję")
        self.runInstructionsButton = QPushButton("Uruchom zestaw instrukcji")
        
        self.addInstructionButton.clicked.connect(self.addInstruction)
        self.runInstructionsButton.clicked.connect(self.runInstructions)
        self.insertToolBarLayout.addWidget(self.instructionType)
        self.insertToolBarLayout.addWidget(self.pipetteComboBoxForInstructionZ3)
        self.insertToolBarLayout.addWidget(self.positionNameList)
        self.insertToolBarLayout.addWidget(self.volume)
        self.volume.setVisible(False)
        self.insertToolBarLayout.addWidget(self.addInstructionButton)
        self.insertToolBarLayout.addWidget(self.runInstructionsButton)
        self.insertToolBar.setLayout(self.insertToolBarLayout)
        layout.addWidget(self.insertToolBar,0,0)
        layout.addWidget(self.instructionsTabel,1,0)

        return layout
    
    def instructionTypeChanged(self):
        instruction_type = self.instructionType.currentText()
        if instruction_type == "Move to position":
            self.positionNameList.setVisible(True)
            self.volume.setVisible(False)
        elif instruction_type in ["Draw up", "Spit out"]:
            self.positionNameList.setVisible(False)
            self.volume.setVisible(True)
        elif instruction_type == "Reset position":
            self.positionNameList.setVisible(False)
            self.volume.setVisible(False)
        elif instruction_type in ["Move Motor M0", "Move Motor M1", "Move Motor M2"]:
            self.positionNameList.setVisible(False)
            self.volume.setVisible(True)
            self.volume.setPlaceholderText("Liczba kroków do przesunięcia")
        elif instruction_type == "Prepare draw up":
            self.positionNameList.setVisible(False)
            self.volume.setVisible(False)
        elif instruction_type == "Start Timer":
            self.pipetteComboBoxForInstructionZ3.setVisible(False)
            self.positionNameList.setVisible(False)
            self.volume.setVisible(False)
            self.volume.setPlaceholderText("Czas w sekundach")
        elif instruction_type == "Reset timer and wait":
            self.pipetteComboBoxForInstructionZ3.setVisible(False)
            self.positionNameList.setVisible(False)
            self.volume.setVisible(True)
            self.volume.setPlaceholderText("Czas w sekundach")
        elif instruction_type == "Wait":
            self.pipetteComboBoxForInstructionZ3.setVisible(False)
            self.positionNameList.setVisible(False)
            self.volume.setVisible(True)
            self.volume.setPlaceholderText("Czas w sekundach")
        elif instruction_type == "Run spincoater" or instruction_type == "Prepare spincoater":
            self.pipetteComboBoxForInstructionZ3.setVisible(False)
            self.positionNameList.setVisible(False)
            self.volume.setVisible(False)

    def setColortoRow(self, table, rowIndex, color):
        for j in range(table.columnCount()-3):
            table.item(rowIndex, j).setBackground(color)

    @pyqtSlot()
    def runInstructions(self):
        Deactived = QBrush(QColor(155, 155, 155))
        CurrentColor = QBrush(QColor(200, 255, 200))
        Actived = QBrush(QColor(255, 255, 255))
        self.setEnabled(False)
        for row in range(self.instructionsTabel.rowCount()):
            self.setColortoRow(self.instructionsTabel, row, CurrentColor)
            self.instructionsTabel.scrollToItem(self.instructionsTabel.item(row, 0), QtWidgets.QAbstractItemView.ScrollHint.PositionAtCenter)
            self.repaint()
            name = self.instructionsTabel.item(row,0).text()
            instruction_type = self.instructionsTabel.item(row, 1).text()
            if instruction_type == "Move to position":
                position_name = self.instructionsTabel.item(row, 2).text()
                self.pipette_dixt[name].move2position(self.positionsSet[position_name])
            elif instruction_type == "Run spincoater":
                self.spincoater.write(b'go=4 \n')
            elif instruction_type == "Prepare spincoater":
                QtTest.QTest.qWait(1000)
                self.spincoater.write(b'va=1 \n')
                QtTest.QTest.qWait(1000)
                self.spincoater.write(b'em \n')
                QtTest.QTest.qWait(1000)
                self.spincoater.write(b'rm \n')
                QtTest.QTest.qWait(1000)
                self.spincoater.write(b'pg=0 \n')

                QtTest.QTest.qWait(1000)
                self.spincoater.write(b'up \n')

            elif instruction_type == "Draw up":
                volume = self.instructionsTabel.item(row, 3).text()
                self.pipette_dixt[name].onlyDrawUp(volume=int(volume))
            elif instruction_type == "Spit out":
                volume = self.instructionsTabel.item(row, 3).text()
                self.pipette_dixt[name].onlySplitOut(volume=int(volume))
            elif instruction_type == "Reset position":
                self.pipette_dixt[name].resetposition()
            elif instruction_type == "Prepare draw up":
                self.pipette_dixt[name].prepareDrawUp()
            elif instruction_type == "Move Motor M0":
                volume = self.instructionsTabel.item(row, 3).text()
                self.pipette_dixt[name].moveM0(steps=int(volume))
            elif instruction_type == "Move Motor M1":
                volume = self.instructionsTabel.item(row, 3).text()
                self.pipette_dixt[name].moveM1(steps=int(volume))
            elif instruction_type == "Move Motor M2":
                volume = self.instructionsTabel.item(row, 3).text()
                self.pipette_dixt[name].moveM2(steps=int(volume))
            elif instruction_type == "Start Timer":
                self.timer = time.time()
            elif instruction_type == "Reset timer and wait":
                volume = self.instructionsTabel.item(row, 3).text()
                self.timer = time.time()
                QtCore.QTimer.singleShot( int(int(volume)-time.time()+self.timer)*1000, lambda: self.setEnabled(True))
                self.setEnabled(False)
                while time.time() - self.timer < int(volume):
                    QtTest.QTest.qWait(100)

            elif instruction_type == "Wait":
                volume = self.instructionsTabel.item(row, 3).text()
                QtCore.QTimer.singleShot( int(int(volume)-time.time()+self.timer)*1000, lambda: self.setEnabled(True))
                self.setEnabled(False)
                while time.time() - self.timer < int(volume):
                    QtTest.QTest.qWait(100)

            self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
            self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
            self.setColortoRow(self.instructionsTabel, row, Deactived)
            self.repaint()
            self.setEnabled(True)
        for i in range(self.instructionsTabel.rowCount()):
            self.setColortoRow(self.instructionsTabel, i, Actived)

    def addInstruction(self):
        instruction_type = self.instructionType.currentText()
        position_name = "-"
        volume = "-"
        if instruction_type in ["Draw up", "Spit out", "Move Motor M0", "Move Motor M1", "Move Motor M2", "Reset timer and wait", "Wait"]:
            if not self.volume.text().isdigit():
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage('Proszę podać liczbę w polu objętości/kroków')
                if error_dialog.exec_():
                    return
            volume = self.volume.text()
        if instruction_type in ["Move to position"]:
            position_name = self.positionNameList.currentText()
        deleteButton = QtWidgets.QPushButton(QIcon("delete.svg"), "")
        deleteButton.clicked.connect(self.deleteClicked)

        moveUpButton = QtWidgets.QPushButton(QIcon("up.svg"), "")
        moveUpButton.clicked.connect(self.moveUpClicked)

        moveDownButton = QtWidgets.QPushButton(QIcon("down.svg"), "")
        moveDownButton.clicked.connect(self.moveDownClicked)

        row_position = self.instructionsTabel.rowCount()
        pipette_name = self.pipetteComboBoxForInstructionZ3.currentText()
        self.instructionsTabel.insertRow(row_position)

        self.instructionsTabel.setItem(row_position, 0, QTableWidgetItem(pipette_name))
        item = self.instructionsTabel.item(row_position, 0)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.instructionsTabel.setItem(row_position, 1, QTableWidgetItem(instruction_type,QtCore.Qt.AlignmentFlag.AlignCenter))
        item = self.instructionsTabel.item(row_position, 1)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.instructionsTabel.setItem(row_position, 2, QTableWidgetItem(position_name,QtCore.Qt.AlignmentFlag.AlignCenter))
        item = self.instructionsTabel.item(row_position, 2)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.instructionsTabel.setItem(row_position, 3, QTableWidgetItem(volume,QtCore.Qt.AlignmentFlag.AlignCenter))
        item = self.instructionsTabel.item(row_position, 3)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.instructionsTabel.setCellWidget(row_position, 4, deleteButton)
        self.instructionsTabel.setCellWidget(row_position, 5, moveUpButton)
        self.instructionsTabel.setCellWidget(row_position, 6, moveDownButton)

    def deleteClicked(self):
        button = self.sender()
        if button:
            row = self.instructionsTabel.indexAt(button.pos()).row()
            self.instructionsTabel.removeRow(row)

    def moveUpClicked(self):
        button = self.sender()
        if button:
            row = self.instructionsTabel.indexAt(button.pos()).row()
            if row > 0:
                self.instructionsTabel.insertRow(row - 1)
                for col in range(self.instructionsTabel.columnCount()):
                    item = self.instructionsTabel.takeItem(row + 1, col)
                    if item:
                        self.instructionsTabel.setItem(row - 1, col, item)
                    else:
                        widget = self.instructionsTabel.cellWidget(row + 1, col)
                        if widget:
                            self.instructionsTabel.setCellWidget(row - 1, col, widget)
                self.instructionsTabel.removeRow(row + 1)
    def moveDownClicked(self):
        button = self.sender()
        if button:
            row = self.instructionsTabel.indexAt(button.pos()).row()
            if row < self.instructionsTabel.rowCount() - 1:
                self.instructionsTabel.insertRow(row + 2)
                for col in range(self.instructionsTabel.columnCount()):
                    item = self.instructionsTabel.takeItem(row, col)
                    if item:
                        self.instructionsTabel.setItem(row + 2, col, item)
                    else:
                        widget = self.instructionsTabel.cellWidget(row, col)
                        if widget:
                            self.instructionsTabel.setCellWidget(row + 2, col, widget)
                self.instructionsTabel.removeRow(row)
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
        self.pipetteComboBoxForInstructionZ2 = QComboBox()
        for name,inst in self.pipette_dixt.items():
            self.pipetteComboBoxForInstructionZ2.addItem(name)
        name = self.pipetteComboBoxForInstructionZ2.currentText()
        layout.addWidget(self.GetButtonUp,1,0)
        layout.addWidget(self.M1ButtonUp,2,0)

        self.steps2volumeForms = QLineEdit()
        self.steps2volumeForms.setPlaceholderText("Enter name of steps per μL or load from file")
        # self.steps2volumeForms.textChanged.connect(self.changeSteps2Volume)
        self.steps2volumeForms.textEdited.connect(self.changeSteps2Volume)

        self.drawUpVolume = QLineEdit()
        self.drawUpVolume.setPlaceholderText("Volume to draw up (μL)")

        self.spitOutVolume = QLineEdit()
        self.spitOutVolume.setPlaceholderText("Volume to spit out (μL)")

        layout.addWidget(self.pipetteComboBoxForInstructionZ2,0,0,1,4)
        layout.addWidget(self.drawUpVolume,1,1,1,1)
        layout.addWidget(self.drawUpunits,1,2,1,1)

        layout.addWidget(self.spitOutVolume,2,1,1,1)
        layout.addWidget(self.spitOutunits,2,2,1,1)

        self.positonlabel2 = QLabel(f"Current position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.samplePositonlabel2 = QLabel(f"Sample position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.tubePositonlabel2 = QLabel(f"Tube position: {self.M0Position}, {self.M1Position}, {self.M2Position}")
        testp = self.pipette_dixt[name]
        self.steps2volumeLabel = QLabel(f"Current steps2volume {testp.steps2volume} stepes/μL")
        self.positonlabel2.setMaximumHeight(15)
        self.samplePositonlabel2.setMaximumHeight(15)
        self.tubePositonlabel2.setMaximumHeight(15)
        self.steps2volumeLabel.setMaximumHeight(15)
        self.positonlabel2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.samplePositonlabel2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.tubePositonlabel2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.steps2volumeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        layout.addWidget(self.steps2volumeForms,3,0,1,3)
        layout.addWidget(self.positonlabel2,4,0,1,4)
        layout.addWidget(self.samplePositonlabel2,5,0,1,4)
        layout.addWidget(self.tubePositonlabel2,6,0,1,4)
        layout.addWidget(self.steps2volumeLabel,7,0,1,4)

        return layout

    def Z1Init(self):


        # Create layout
        layout = QGridLayout()
        self.pipetteComboBoxForInstructionZ1 = QComboBox()
        self.pipetteComboBoxForInstructionZ1.editTextChanged.connect(self.changePipette)
        for name,inst in self.pipette_dixt.items():
            self.pipetteComboBoxForInstructionZ1.addItem(name)
        # Create buttons for pipette control
        self.M0ButtonUp = QPushButton('Motor 1 Up', self)
        self.M1ButtonUp = QPushButton('Motor 2 Up', self)
        self.M2ButtonUp = QPushButton('Motor 3 Up', self)

        self.M0ButtonDown = QPushButton('Motor 1 Down', self)
        self.M1ButtonDown = QPushButton('Motor 2 Down', self)
        self.M2ButtonDown = QPushButton('Motor 3 Down', self)
        text01 = QLabel('Ustawienia pozycji pipety')
        text01.setMaximumHeight(15)
        text01.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        text2 = QLabel('Liczba kroków do przesunięcia pipety')
        text2.setMaximumHeight(15)
        text2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        text3 = QLabel('Mnożnik kroków')
        text3.setMaximumHeight(15)
        text3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.SaveSamplePositionButton = QPushButton('Set current postion for Sample', self)
        self.SaveSamplePositionButton.clicked.connect(self.saveSample)
        self.SaveTubePositionButton = QPushButton('Set current postion for Tube', self)
        self.SaveTubePositionButton.clicked.connect(self.saveTube)

        self.SavePositionButton = QPushButton('Save current position in dataset', self)
        self.SavePositionButton.clicked.connect(self.savePosition)
        self.PositionName = QLineEdit()
        self.PositionName.setPlaceholderText("Name of the position to save in dataset")


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
        
        self.positonlabel.setMaximumHeight(15)
        self.samplePositonlabel.setMaximumHeight(15)
        self.tubePositonlabel.setMaximumHeight(15)
        self.positonlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.samplePositonlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.tubePositonlabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 

        # Add buttons to layout
        layout.addWidget(self.pipetteComboBoxForInstructionZ1,0,0,1,4)
        layout.addWidget(text01,1,0,1,2)
        layout.addWidget(text2,1,2,1,1)
        layout.addWidget(text3,1,3,1,1)
        layout.addWidget(self.M0ButtonUp,2,0)
        layout.addWidget(self.M1ButtonUp,3,0)
        layout.addWidget(self.M2ButtonUp,4,0)
        layout.addWidget(self.M0ButtonDown,2,1)
        layout.addWidget(self.M1ButtonDown,3,1)
        layout.addWidget(self.M2ButtonDown,4,1)
      
        layout.addWidget(self.M0Steps,2,2)
        layout.addWidget(self.M1Steps,3,2)
        layout.addWidget(self.M2Steps,4,2)

        layout.addWidget(self.M0Speed,2,3)
        layout.addWidget(self.M1Speed,3,3)  
        layout.addWidget(self.M2Speed,4,3)

        layout.addWidget(self.SaveSamplePositionButton,5,0,1,4)
        layout.addWidget(self.SaveTubePositionButton,6,0,1,4)


        layout.addWidget(self.SavePositionButton,7,0,1,2)
        layout.addWidget(self.PositionName,7,2,1,2)

        layout.addWidget(self.positonlabel,8,0,1,4)
        layout.addWidget(self.samplePositonlabel,9,0,1,4)
        layout.addWidget(self.tubePositonlabel,10,0,1,4)


        # Set the layout for the widget
        return layout
    def changePipette(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

    def savePosition(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        position_name = self.PositionName.text() or f"Position{len(self.positionsSet)-2}"
        self.positionsSet[position_name] = (self.pipette_dixt[name].m0Position, self.pipette_dixt[name].m1Position, self.pipette_dixt[name].m2Position)
        self.PositionName.setText('')
        self.positionNameList.setCurrentIndex(0)
        self.positionNameList.addItem(position_name)
        logging.info(f"Positions set: {self.positionsSet}")
        
    def drawUp(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()

        if self.drawUpVolume.text().isdigit():
            volume = int(self.drawUpVolume.text())
        else:
            volume = 50
            self.drawUpVolume.setText("50")
        #print("Prepare draw up")
        self.pipette_dixt[name].resetposition()
        self.pipette_dixt[name].prepareDrawUp()
        if self.positionsSet["Tube"] is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Ustaw pozycję do pobrania lub załaduj z pliku')
            if error_dialog.exec_():
                return
        if self.pipette_dixt[name].steps2volume is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Ustaw pozycję do liczbę kroków na μL lub załaduj z pliku')
            if error_dialog.exec_():
                return

        #print(f"Go to position of Tube: {self.positionsSet["Tube"]}")
        self.pipette_dixt[name].move2position(position=self.positionsSet["Tube"])
        #print(f"Drawing up the solution: {volume} {self.drawUpunits.currentText()}")
        self.pipette_dixt[name].onlyDrawUp(volume=volume)
        # self.pipette_dixt[name].drawUp(self.positionsSet["Tube"],volume)
        self.M0Position = self.pipette_dixt[name].m0Position
        self.M1Position = self.pipette_dixt[name].m1Position
        self.M2Position = self.pipette_dixt[name].m2Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")


        
        
    def spitOut(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()

        if self.spitOutVolume.text().isdigit():
            volume = int(self.spitOutVolume.text())
        else:
            volume = 50
            self.spitOutVolume.setText("50")
        if self.positionsSet["Tube"] is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Ustaw pozycję do depozycji lub załaduj z pliku')
            if error_dialog.exec_():
                return
            
        if self.pipette_dixt[name].steps2volume is None:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Ustaw pozycję do liczbę kroków na μL lub załaduj z pliku')
            if error_dialog.exec_():
                return
        #print(f"Go to position of Sample: {self.positionsSet["Sample"]}")
        self.pipette_dixt[name].move2position(self.positionsSet["Sample"])
        #print(f"Spitting out the solution: {volume} {self.spitOutunits.currentText()}")
        self.pipette_dixt[name].onlySplitOut(volume)
        self.M0Position = self.pipette_dixt[name].m0Position
        self.M1Position = self.pipette_dixt[name].m1Position
        self.M2Position = self.pipette_dixt[name].m2Position

        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

        # self.pipette_dixt[name].splitOut(volume,speed=self.m1speed)

    

    def moveM0Up(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        if self.M0Steps.text().isdigit() and self.M0Speed.text().isdigit():
            self.m0steps = int(self.M0Steps.text())
            self.m0speed = int(self.M0Speed.text())
        else:
            self.m0steps = 2000
            self.m0speed = 200
            self.M0Steps.setText("2000")
            self.M0Speed.setText("200")
        self.pipette_dixt[name].moveM0(self.m0steps,self.m0speed)
        self.M0Position = self.pipette_dixt[name].m0Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

        #print(f"Moving pipette up by {self.m0steps} steps at speed {self.m0speed}")

    def moveM1Up(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        if self.M1Steps.text().isdigit() and self.M1Speed.text().isdigit():
            self.m1steps = int(self.M1Steps.text())
            self.m1speed = int(self.M1Speed.text())
        else:
            self.m1steps = 50
            self.m1speed = 2000
            self.M1Steps.setText("50")
            self.M1Speed.setText("2000")
        self.pipette_dixt[name].moveM1(-self.m1steps,self.m1speed)
        self.M1Position = self.pipette_dixt[name].m1Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

        #print(f"Moving pipette down by {self.m1steps} steps at speed {self.m1speed}")

    def moveM2Up(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        if self.M2Steps.text().isdigit() and self.M2Speed.text().isdigit():
            self.m2steps = int(self.M2Steps.text())
            self.m2speed = int(self.M2Speed.text())
        else:
            self.m2steps = 100
            self.m2speed = 600
            self.M2Steps.setText("100")
            self.M2Speed.setText("600")
        self.pipette_dixt[name].moveM2(-self.m2steps,self.m2speed)
        self.M2Position = self.pipette_dixt[name].m2Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

        #print(f"Moving pipette left by {self.m2steps} steps at speed {self.m2speed}")

    def moveM0Down(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        if self.M0Steps.text().isdigit() and self.M0Speed.text().isdigit():
            self.m0steps = int(self.M0Steps.text())
            self.m0speed = int(self.M0Speed.text())
        else:
            self.m0steps = 2000
            self.m0speed = 200
            self.M0Steps.setText("2000")
            self.M0Speed.setText("200")
        self.pipette_dixt[name].moveM0(-self.m0steps,self.m0speed)
        self.M0Position = self.pipette_dixt[name].m0Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")

        #print(f"Moving pipette down by {-self.m0steps} steps at speed {self.m0speed}")

    def moveM1Down(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        if self.M1Steps.text().isdigit() and self.M1Speed.text().isdigit():
            self.m1steps = int(self.M1Steps.text())
            self.m1speed = int(self.M1Speed.text())
        else:
            self.m1steps = 50
            self.m1speed = 2000
            self.M1Steps.setText("50")
            self.M1Speed.setText("2000")
        self.M1Position -= self.m1steps
        self.pipette_dixt[name].moveM1(self.m1steps,self.m1speed)
        self.M1Position = self.pipette_dixt[name].m1Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")


        #print(f"Moving pipette down by {-self.m1steps} steps at speed {self.m1speed}")

    def moveM2Down(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()

        if self.M2Steps.text().isdigit() and self.M2Speed.text().isdigit():
            self.m2steps = int(self.M2Steps.text())
            self.m2speed = int(self.M2Speed.text())
        else:
            self.m2steps = 100
            self.m2speed = 600
            self.M2Steps.setText("100")
            self.M2Speed.setText("600")
        self.pipette_dixt[name].moveM2(self.m2steps,self.m2speed)
        self.M2Position = self.pipette_dixt[name].m2Position
        self.positonlabel.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")
        self.positonlabel2.setText(f"Current position: {self.pipette_dixt[name].m0Position}, {self.pipette_dixt[name].m1Position}, {self.pipette_dixt[name].m2Position}")


        #print(f"Moving pipette left by {-self.m2steps} steps at speed {self.m2speed}")

    def saveSample(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()

        #print(f"Saving current position as Sample position {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.M0Position = self.pipette_dixt[name].m0Position
        self.M1Position = self.pipette_dixt[name].m1Position
        self.M2Position = self.pipette_dixt[name].m2Position
        self.positionsSet["Sample"] = (self.M0Position, self.M1Position, self.M2Position)
        self.samplePositonlabel.setText(f"Sample position: {self.positionsSet["Sample"]}")
        self.samplePositonlabel2.setText(f"Sample position: {self.positionsSet["Sample"]}")


    def saveTube(self):
        name = self.pipetteComboBoxForInstructionZ1.currentText()
        #print(f"Saving current position as Tube position {self.M0Position}, {self.M1Position}, {self.M2Position}")
        self.M0Position = self.pipette_dixt[name].m0Position
        self.M1Position = self.pipette_dixt[name].m1Position
        self.M2Position = self.pipette_dixt[name].m2Position
        self.positionsSet["Tube"] = (self.M0Position, self.M1Position, self.M2Position)
        self.tubePositonlabel.setText(f"Tube position: {self.positionsSet["Tube"]}")
        self.tubePositonlabel2.setText(f"Tube position: {self.positionsSet["Tube"]}")
    def __delete__(self, instance):
        for pipette in self.pipette_dixt:
            pipette.stopMotors()
            pipette.close()


if __name__ == '__main__':
    app = QApplication([])
    gui = PipetteGUI()
    try:
        gui.show()
        app.exec_()
    except Exception as e:
        logging.error(f"An error occurred: {e}")