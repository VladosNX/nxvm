#!/bin/python3
import time
import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QIntValidator
import random
import os
import yaml
import subprocess
import threading

class FontNames():
    def __init__(self):
        self.standard = 'Montserrat'
        self.splash = 'Times New Roman'
fontNames = FontNames()

class Colors():
    def __init__(self):
        self.bg = "#313131"
        self.block = "#464646"
        self.disabled = "gray"
colors = Colors()

splashes = ['NXVM']

appWidth = 1100
appHeight = 600

checkboxStyle = """
QCheckBox {
    color: white;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
}
"""

class ContentWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.app = app
        self.parent = parent
        screenSize = parent.app.desktop().availableGeometry()
        appWidth = 1100
        appHeight = 600
        
        self.content = QtWidgets.QWidget(parent)
        self.contentLayout = QtWidgets.QVBoxLayout(self.content)
        self.content.setFixedSize(appWidth - parent.leftMenu.width(), appHeight)
        self.content.setStyleSheet(f"background-color: {colors.bg};")
        self.content.move(parent.leftMenu.width(), 0)

        self.splashText = QtWidgets.QLabel(self.content)
        self.splashText.setText(splashes[random.randint(0, len(splashes)) - 1])
        self.splashText.setFont(QFont(fontNames.splash, 32))
        self.splashText.adjustSize()
        self.splashText.move(int((self.content.width() - self.splashText.width()) / 2), 180)
        self.splashText.setStyleSheet("color: white;")

        self.welcomeText = QtWidgets.QLabel(self.content)
        self.welcomeText.setText('Welcome to NXVM')
        self.welcomeText.setFont(QFont(fontNames.standard, 12))
        self.welcomeText.adjustSize()
        self.welcomeText.move(int((self.content.width() - self.welcomeText.width()) / 2), 240)
        self.welcomeText.setStyleSheet("color: white;")

        self.newVmButton = QtWidgets.QPushButton(self.content)
        self.newVmButton.setText("New VM")
        self.newVmButton.setFont(QFont(fontNames.standard))
        self.newVmButton.adjustSize()
        self.newVmButton.move(int((self.content.width() - self.newVmButton.width()) / 2) - 100, 300)
        self.newVmButton.setStyleSheet("color: white;")
        self.newVmButton.clicked.connect(self.newVm)

        self.openVmButton = QtWidgets.QPushButton(self.content)
        self.openVmButton.setText("Open VM")
        self.openVmButton.setFont(QFont(fontNames.standard))
        self.openVmButton.adjustSize()
        self.openVmButton.move(int((self.content.width() - self.openVmButton.width()) / 2), 300)
        self.openVmButton.setStyleSheet("color: white;")

        self.settingsButton = QtWidgets.QPushButton(self.content)
        self.settingsButton.setText("Settings")
        self.settingsButton.setFont(QFont(fontNames.standard))
        self.settingsButton.adjustSize()
        self.settingsButton.move(int((self.content.width() - self.openVmButton.width()) / 2) + 100, 300)
        self.settingsButton.setStyleSheet("color: white;")
        
    def newVm(self):
        self.newVmWindow = NewVmWindow(self.app, self.parent)
        self.newVmWindow.show()
        self.newVmWindow.raise_()

class ShowVmWindow(QtWidgets.QMainWindow):
    def __init__(self, app, parent):
        super().__init__()
        self.app = app
        self.vmConfig = None
        self.subprocess = None
        self.thread = None
        self.vncThread = None
        self.parent = parent

        self.content = QtWidgets.QWidget(parent)
        # self.contentLayout = QtWidgets.QVBoxLayout(self.content)
        self.content.setFixedSize(appWidth - parent.leftMenu.width(), appHeight)
        self.content.setStyleSheet(f"background-color: {colors.bg};")
        self.content.move(parent.leftMenu.width(), 0)

        self.vmTitle = QtWidgets.QLabel(self.content)
        self.vmTitle.setText("VM Title")
        self.vmTitle.setFont(QFont(fontNames.splash, 28))
        self.vmTitle.setStyleSheet("color: white;")
        self.vmTitle.adjustSize()
        self.vmTitle.move(int((self.content.width() - self.vmTitle.width()) / 2), 50)

        self.descriptionText = QtWidgets.QTextEdit(self.content)
        self.descriptionText.setText("Description")
        self.descriptionText.setReadOnly(True)
        self.descriptionText.setFont(QFont(fontNames.standard, 12))
        self.descriptionText.setFixedSize(appWidth - parent.leftMenu.width() - 200, appHeight - 200)
        self.descriptionText.move(100, 120)
        self.descriptionText.setStyleSheet("border: none; color: white;")

        self.runButton = QtWidgets.QPushButton(self.content)
        self.runButton.setText("Run")
        self.runButton.setFont(QFont(fontNames.splash))
        self.runButton.setFixedSize(100, 30)
        self.runButton.move(200, 10)
        self.runButton.setStyleSheet("color: white;")
        self.runButton.clicked.connect(self.runVm)

        self.stopButton = QtWidgets.QPushButton(self.content)
        self.stopButton.setText("Stop")
        self.stopButton.setFont(QFont(fontNames.splash))
        self.stopButton.setFixedSize(100, 30)
        self.stopButton.move(200, 10)
        self.stopButton.setStyleSheet("color: white;")
        self.stopButton.clicked.connect(self.stopVm)
        self.stopButton.hide()

        self.vncViewButton = QtWidgets.QPushButton(self.content)
        self.vncViewButton.setText("Connect to VNC")
        self.vncViewButton.setFont(QFont(fontNames.splash))
        self.vncViewButton.setFixedSize(100, 30)
        self.vncViewButton.move(int((self.content.width() - self.vncViewButton.width()) / 2), 10)
        self.vncViewButton.clicked.connect(self.vncViewStart)
        self.vncViewButton.setDisabled(True)
        self.vncViewButton.setStyleSheet(f"color: {colors.disabled};")

        self.cdromBootCheckbox = QtWidgets.QCheckBox(self.content)
        self.cdromBootCheckbox.setText("Cdrom Boot")
        self.cdromBootCheckbox.setFont(QFont(fontNames.standard, 14))
        # self.cdromBootCheckbox.setStyleSheet("""
        # QCheckBox {
        #     color: white;
        # }
        # QCheckBox::indicator {
        #     border: 2px solid white;
        #     width: 20px;
        #     height: 20px;
        # }
        # QCheckBox::indicator:checked {
        #     border: 2px solid green;
        # }
        # """)
        self.cdromBootCheckbox.setStyleSheet(checkboxStyle)
        self.cdromBootCheckbox.adjustSize()
        self.cdromBootCheckbox.move(100, appHeight - 100)

        self.settingsButton = QtWidgets.QPushButton(self.content)
        self.settingsButton.setText("Settings")
        self.settingsButton.setFont(QFont(fontNames.splash))
        self.settingsButton.setFixedSize(100, 30)
        self.settingsButton.move(appWidth - parent.leftMenu.width() - self.settingsButton.width() - 200, 10)
        self.settingsButton.setStyleSheet("color: white;")
        self.settingsButton.clicked.connect(self.openSettings)

    def setVmConfig(self, vmConfig):
        self.vmConfig = vmConfig
        description = ""
        for k, v in vmConfig.items():
            description += f"**{k}**: `{v}`\n\n"
        self.descriptionText.setMarkdown(description)
        self.vmTitle.setText(vmConfig["NAME"])
        self.vmTitle.adjustSize()
        self.vmTitle.move(int((self.content.width() - self.vmTitle.width()) / 2), 50)

    def runVm(self):
        print(f"Running VM {self.vmConfig}")
        command = [f'qemu-system-{self.vmConfig["ARCH"]}',
                   '-smp', str(self.vmConfig["CPUS"]),
                   '-hda', self.vmConfig["HDA"],
                   '-m', str(self.vmConfig["RAM"]),
                   '-netdev', 'user,id=net0',
                   '-device', 'virtio-net-pci,netdev=net0',
                   '-vga', 'virtio',
                   '-vnc', ':0']
        if self.vmConfig["USE_KVM"] == 'TRUE':
            command.append('-enable-kvm')
        if self.vmConfig["USE_HOST_CPU"] == 'TRUE':
            command.append('-cpu')
            command.append('host,nx')
        if self.vmConfig["USE_Q35"] == 'TRUE':
            command.append('-machine')
            command.append('type=q35')
        if self.vmConfig["CDROM"] != '':
            command.append('-cdrom')
            command.append(self.vmConfig["CDROM"])
            if self.cdromBootCheckbox.isChecked():
                command.append('-boot')
                command.append('d')
        print(command)
        self.subprocess = subprocess.Popen(command)
        self.thread = threading.Thread(target=self.handleVm)
        self.thread.start()
        self.vncViewStart()
        self.vmTitle.setText(f"{self.vmConfig['NAME']} (Running)")
        self.vmTitle.adjustSize()
        self.vmTitle.move(int((self.content.width() - self.vmTitle.width()) / 2), 50)
        self.runButton.hide()
        self.stopButton.show()
        self.vncViewButton.setDisabled(False)
        self.vncViewButton.setStyleSheet("color: white;")

    def handleVm(self):
        while True:
            code = self.subprocess.poll()
            if code:
                print(f"Process exited with code {code}")
                self.stopButton.hide()
                self.runButton.show()
                self.vncViewButton.setDisabled(True)
                self.vncViewButton.setStyleSheet(f"color: {colors.disabled};")
                self.vmTitle.setText(f"{self.vmConfig['NAME']}")
                self.vmTitle.adjustSize()
                self.vmTitle.move(int((self.content.width() - self.vmTitle.width()) / 2), 50)
                break

    def stopVm(self):
        self.subprocess.kill()

    def vncViewStart(self):
        self.vncThread = threading.Thread(target=self.vncViewer)
        self.vncThread.start()

    def vncViewer(self):
        time.sleep(0.1)
        os.system('vncviewer localhost:5900 MenuKey=Pause')

    def openSettings(self):
        self.vmPath = os.path.join(os.getenv('HOME'), 'NXVMs', self.vmConfig["NAME"])
        self.settingsWindow = VmSettingsWindow(self.app, self, self.vmConfig, self.vmPath)
        self.settingsWindow.show()

class VmSettingsWindow(QtWidgets.QMainWindow):
    def __init__(self, app, parent, config, vmPath):
        super().__init__()
        self.app = app
        self.config = config
        self.vmPath = vmPath
        self.parent = parent
        screenSize = self.app.desktop().availableGeometry()
        windowWidth = 1000
        windowHeight = 500
        self.setGeometry(int((screenSize.width() - windowWidth) / 2), int((screenSize.height() - windowHeight) / 2),
                         windowWidth, windowHeight)
        self.setStyleSheet(f"background-color: {colors.bg};")

        self.titleBlock = QtWidgets.QWidget(self)
        self.titleBlock.setFixedSize(windowWidth, 100)
        self.titleBlock.move(0, 0)
        self.titleBlock.setStyleSheet(f"background-color: {colors.block};")

        self.settingsTitle = QtWidgets.QLabel(self.titleBlock)
        self.settingsTitle.setText("Settings")
        self.settingsTitle.setFont(QFont(fontNames.splash, 28))
        self.settingsTitle.adjustSize()
        self.settingsTitle.move(50, int((self.titleBlock.height() - self.settingsTitle.height()) / 2))
        self.settingsTitle.setStyleSheet("color: white;")

        # Widgets for stacked widget
        lineEditWidth = 400
        lineEditHeight = 25
        lineEditStart = 250
        fileEditWidth = 300
        fileButtonStart = lineEditStart + fileEditWidth + 10
        fileButtonWidth = 90
        hintStart = 50
        # VM Name block
        self.vmNameWidget = QtWidgets.QWidget()
        self.vmNameInputbox = QtWidgets.QLineEdit(self.vmNameWidget)
        self.vmNameInputbox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vmNameInputbox.move(lineEditStart, 50)
        self.vmNameInputbox.setStyleSheet("color: white;")
        self.vmNameHint = QtWidgets.QLabel(self.vmNameWidget)
        self.vmNameHint.setText("VM Name:")
        self.vmNameHint.setFont(QFont(fontNames.standard, 14))
        self.vmNameHint.setStyleSheet("color: white;")
        self.vmNameHint.adjustSize()
        self.vmNameHint.move(hintStart, 50)

        self.vmNameWidget = QtWidgets.QWidget()
        self.vmNameInputbox = QtWidgets.QLineEdit(self.vmNameWidget)
        self.vmNameInputbox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vmNameInputbox.move(lineEditStart, 50)
        self.vmNameInputbox.setStyleSheet("color: white;")
        self.vmNameInputbox.setText(self.config['NAME'])
        self.vmNameHint = QtWidgets.QLabel(self.vmNameWidget)
        self.vmNameHint.setText("VM Name:")
        self.vmNameHint.setFont(QFont(fontNames.standard, 14))
        self.vmNameHint.setStyleSheet("color: white;")
        self.vmNameHint.adjustSize()
        self.vmNameHint.move(hintStart, 50)

        # Storage block
        self.vmStorageWidget = QtWidgets.QWidget()
        self.vmHdaPathInputbox = QtWidgets.QLineEdit(self.vmStorageWidget)
        self.vmHdaPathInputbox.setFixedSize(fileEditWidth, lineEditHeight)
        self.vmHdaPathInputbox.move(lineEditStart, 50)
        self.vmHdaPathInputbox.setStyleSheet("color: white;")
        self.vmHdaPathInputbox.setText(self.config['HDA'])
        self.vmHdaPathHint = QtWidgets.QLabel(self.vmStorageWidget)
        self.vmHdaPathHint.setText("Path to HDA:")
        self.vmHdaPathHint.setFont(QFont(fontNames.standard, 14))
        self.vmHdaPathHint.setStyleSheet("color: white;")
        self.vmHdaPathHint.adjustSize()
        self.vmHdaPathHint.move(hintStart, 50)
        self.vmHdaPathFileDialog = QtWidgets.QPushButton(self.vmStorageWidget)
        self.vmHdaPathFileDialog.setFixedSize(fileButtonWidth, lineEditHeight)
        self.vmHdaPathFileDialog.setText("Browse")
        self.vmHdaPathFileDialog.move(fileButtonStart, 50)
        self.vmHdaPathFileDialog.setStyleSheet("color: white;")
        self.vmHdaPathFileDialog.clicked.connect(lambda: self.vmHdaPathInputbox.setText(
            QtWidgets.QFileDialog.getOpenFileName(self, "HDA Path", "", "")[0]
        ))

        self.vmCdromPathInputbox = QtWidgets.QLineEdit(self.vmStorageWidget)
        self.vmCdromPathInputbox.setFixedSize(fileEditWidth, lineEditHeight)
        self.vmCdromPathInputbox.move(lineEditStart, 80)
        self.vmCdromPathInputbox.setStyleSheet("color: white;")
        self.vmCdromPathInputbox.setText(self.config['CDROM'])
        self.vmCdromPathHint = QtWidgets.QLabel(self.vmStorageWidget)
        self.vmCdromPathHint.setText("Path to CDROM:")
        self.vmCdromPathHint.setFont(QFont(fontNames.standard, 14))
        self.vmCdromPathHint.setStyleSheet("color: white;")
        self.vmCdromPathHint.adjustSize()
        self.vmCdromPathHint.move(hintStart, 80)
        self.vmCdromPathFileDialog = QtWidgets.QPushButton(self.vmStorageWidget)
        self.vmCdromPathFileDialog.setFixedSize(fileButtonWidth, lineEditHeight)
        self.vmCdromPathFileDialog.setText("Browse")
        self.vmCdromPathFileDialog.move(fileButtonStart, 80)
        self.vmCdromPathFileDialog.setStyleSheet("color: white;")
        self.vmCdromPathFileDialog.clicked.connect(lambda: self.vmCdromPathInputbox.setText(
            QtWidgets.QFileDialog.getOpenFileName(self, "HDA Path", "", "")[0]
        ))

        # Hardware block
        self.vmHardwareWidget = QtWidgets.QWidget()
        self.vmCpusInputbox = QtWidgets.QLineEdit(self.vmHardwareWidget)
        self.vmCpusInputbox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vmCpusInputbox.move(lineEditStart, 50)
        self.vmCpusInputbox.setStyleSheet("color: white;")
        self.vmCpusInputbox.setText(str(self.config['CPUS']))
        self.vmCpusInputbox.setValidator(QIntValidator())
        self.vmCpusHint = QtWidgets.QLabel(self.vmHardwareWidget)
        self.vmCpusHint.setText("CPUs amount:")
        self.vmCpusHint.setFont(QFont(fontNames.standard, 14))
        self.vmCpusHint.setStyleSheet("color: white;")
        self.vmCpusHint.adjustSize()
        self.vmCpusHint.move(hintStart, 50)

        self.vmRamInputbox = QtWidgets.QLineEdit(self.vmHardwareWidget)
        self.vmRamInputbox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vmRamInputbox.move(lineEditStart, 80)
        self.vmRamInputbox.setStyleSheet("color: white;")
        self.vmRamInputbox.setText(str(self.config['RAM']))
        self.vmRamInputbox.setValidator(QIntValidator())
        self.vmRamHint = QtWidgets.QLabel(self.vmHardwareWidget)
        self.vmRamHint.setText("RAM (MB):")
        self.vmRamHint.setFont(QFont(fontNames.standard, 14))
        self.vmRamHint.setStyleSheet("color: white;")
        self.vmRamHint.adjustSize()
        self.vmRamHint.move(hintStart, 80)

        self.vmUseKvmCheckbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseKvmCheckbox.setText("Use KVM Acceleration")
        self.vmUseKvmCheckbox.setStyleSheet(checkboxStyle)
        self.vmUseKvmCheckbox.adjustSize()
        self.vmUseKvmCheckbox.move(lineEditStart, 110)
        self.vmUseKvmCheckbox.setChecked(True if self.config['USE_KVM'] == 'TRUE' else False)

        self.vmUseQ35Checkbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseQ35Checkbox.setText("Emulate Intel Q35 chipset")
        self.vmUseQ35Checkbox.setStyleSheet(checkboxStyle)
        self.vmUseQ35Checkbox.adjustSize()
        self.vmUseQ35Checkbox.move(lineEditStart, 140)
        self.vmUseQ35Checkbox.setChecked(True if self.config['USE_Q35'] == 'TRUE' else False)

        self.vmUseHostCpuCheckbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseHostCpuCheckbox.setText("Allow using host CPU")
        self.vmUseHostCpuCheckbox.setStyleSheet(checkboxStyle)
        self.vmUseHostCpuCheckbox.adjustSize()
        self.vmUseHostCpuCheckbox.move(lineEditStart, 170)
        self.vmUseHostCpuCheckbox.setChecked(True if self.config['USE_HOST_CPU'] == 'TRUE' else False)

        self.leftMenu = QtWidgets.QListWidget(self)
        self.leftMenu.setFixedSize(180, windowHeight - self.titleBlock.height() - 20)
        self.leftMenu.move(10, self.titleBlock.height() + 10)
        self.leftMenu.setStyleSheet(f"background-color: {colors.block}; color: white;")
        self.leftMenu.addItems(['VM Name', 'Storage', 'Hardware'])
        self.leftMenu.currentRowChanged.connect(self.changeBlock)

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.setFixedSize(windowWidth - self.leftMenu.width() - 30,
                                        windowHeight - self.titleBlock.height() - 70)
        self.stackedWidget.move(self.leftMenu.width() + 20, self.titleBlock.height() + 10)
        self.stackedWidget.addWidget(self.vmNameWidget)
        self.stackedWidget.addWidget(self.vmStorageWidget)
        self.stackedWidget.addWidget(self.vmHardwareWidget)

        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setText("Save")
        self.saveButton.setStyleSheet("color: white;")
        self.saveButton.adjustSize()
        self.saveButton.move(windowWidth - self.saveButton.width() - 50, windowHeight - 50)
        self.saveButton.clicked.connect(self.saveSettings)

    def changeBlock(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def saveSettings(self):
        self.vmName = self.vmNameInputbox.text()
        self.vmHda = self.vmHdaPathInputbox.text()
        self.vmCdrom = self.vmCdromPathInputbox.text()
        self.vmCpus = int(self.vmCpusInputbox.text())
        self.vmRam = int(self.vmRamInputbox.text())
        self.vmUseKvm = 'TRUE' if self.vmUseKvmCheckbox.isChecked() else 'FALSE'
        self.vmUseQ35 = 'TRUE' if self.vmUseQ35Checkbox.isChecked() else 'FALSE'
        self.vmUseHostCpu = 'TRUE' if self.vmUseHostCpuCheckbox.isChecked() else 'FALSE'
        config = {
            'ARCH': 'x86_64',
            'NAME': self.vmName,
            'HDA': self.vmHda,
            'CDROM': self.vmCdrom,
            'RAM': self.vmRam,
            'CPUS': self.vmCpus,
            'USE_KVM': self.vmUseKvm,
            'USE_Q35': self.vmUseQ35,
            'USE_HOST_CPU': self.vmUseHostCpu
        }
        raw = yaml.dump(config)
        print(self.vmPath)
        with open(self.vmPath + '/nxvm.yaml', 'w') as file:
            file.write(raw)
        self.parent.parent.updateVmList()
        self.parent.setVmConfig(config)
        self.close()

class NewVmWindow(QtWidgets.QMainWindow):
    def __init__(self, app, baseWindow):
        super().__init__()
        self.baseWindow = baseWindow
        self.app = app
        screenSize = app.desktop().availableGeometry()
        windowWidth = 600
        windowHeight = 400
        self.setGeometry(int((screenSize.width() - windowWidth) / 2), int((screenSize.height() - windowHeight) / 2), windowWidth, windowHeight)
        self.setWindowTitle("New virtual machine")
        self.setStyleSheet(f"background-color: {colors.bg};")

        self.titleBlock = QtWidgets.QWidget(self)
        self.titleBlockLayout = QtWidgets.QVBoxLayout(self.titleBlock)
        self.titleBlock.setFixedSize(windowWidth, 100)
        self.titleBlock.move(0, 0)
        self.titleBlock.setStyleSheet(f"background-color: {colors.block};")

        self.newVmTitle = QtWidgets.QLabel(self.titleBlock)
        self.newVmTitle.setText("New virtual machine")
        self.newVmTitle.setFont(QFont(fontNames.splash, 24))
        self.newVmTitle.adjustSize()
        self.newVmTitle.move(int((windowWidth - self.newVmTitle.width()) / 2), int((self.titleBlock.height() - self.newVmTitle.height()) / 2))
        self.newVmTitle.setStyleSheet("color: white;")

        lineEditStart = 270

        self.newVmNameHint = QtWidgets.QLabel(self)
        self.newVmNameHint.setText("VM Name:")
        self.newVmNameHint.setFont(QFont(fontNames.standard, 12))
        self.newVmNameHint.adjustSize()
        self.newVmNameHint.move(100, 120)
        self.newVmNameHint.setStyleSheet("color: white;")
        self.newVmNameInputbox = QtWidgets.QLineEdit(self)
        self.newVmNameInputbox.setFixedSize(int(windowWidth - 350), 20)
        self.newVmNameInputbox.move(lineEditStart, 120)
        self.newVmNameInputbox.setStyleSheet("color: white;")
        self.newVmNameInputbox.textChanged.connect(self.newVmNameInputboxChanged)
        self.newVmNameHasForbiddenSymbol = False

        self.newVmPathHint = QtWidgets.QLabel(self)
        self.newVmPathHint.setText("VM Path:")
        self.newVmPathHint.setFont(QFont(fontNames.standard, 12))
        self.newVmPathHint.adjustSize()
        self.newVmPathHint.move(100, 150)
        self.newVmPathHint.setStyleSheet("color: white;")
        self.newVmPathInputbox = QtWidgets.QLineEdit(self)
        self.newVmPathInputbox.setFixedSize(int(windowWidth - 350), 20)
        self.newVmPathInputbox.move(lineEditStart, 150)
        self.newVmPathInputbox.setStyleSheet("color: white;")
        self.newVmPathInputbox.setText(os.path.join(os.getenv('HOME'), 'NXVMs'))
        self.newVmPathInputbox.textChanged.connect(self.newVmPathInputboxChanged)

        self.newVmRamHint = QtWidgets.QLabel(self)
        self.newVmRamHint.setText("RAM Amount (MB):")
        self.newVmRamHint.setFont(QFont(fontNames.standard, 12))
        self.newVmRamHint.adjustSize()
        self.newVmRamHint.move(100, 180)
        self.newVmRamHint.setStyleSheet("color: white;")
        self.newVmRamInputbox = QtWidgets.QLineEdit(self)
        self.newVmRamInputbox.setFixedSize(int(windowWidth - 350), 20)
        self.newVmRamInputbox.move(lineEditStart, 180)
        self.newVmRamInputbox.setStyleSheet("color: white;")
        self.newVmRamInputbox.setText("2048")
        self.newVmRamInputbox.setValidator(QIntValidator())
        self.newVmRamInputbox.textChanged.connect(self.inputboxChanged)

        self.newVmDiskSizeHint = QtWidgets.QLabel(self)
        self.newVmDiskSizeHint.setText("Disk Size (GB):")
        self.newVmDiskSizeHint.setFont(QFont(fontNames.standard, 12))
        self.newVmDiskSizeHint.adjustSize()
        self.newVmDiskSizeHint.move(100, 210)
        self.newVmDiskSizeHint.setStyleSheet("color: white;")
        self.newVmDiskSizeInputbox = QtWidgets.QLineEdit(self)
        self.newVmDiskSizeInputbox.setFixedSize(int(windowWidth - 350), 20)
        self.newVmDiskSizeInputbox.move(lineEditStart, 210)
        self.newVmDiskSizeInputbox.setStyleSheet("color: white;")
        self.newVmDiskSizeInputbox.setText("20")
        self.newVmDiskSizeInputbox.setValidator(QIntValidator())
        self.newVmDiskSizeInputbox.textChanged.connect(self.inputboxChanged)

        self.newVmCpusAmountHint = QtWidgets.QLabel(self)
        self.newVmCpusAmountHint.setText("CPUs Amount:")
        self.newVmCpusAmountHint.setFont(QFont(fontNames.standard, 12))
        self.newVmCpusAmountHint.adjustSize()
        self.newVmCpusAmountHint.move(100, 240)
        self.newVmCpusAmountHint.setStyleSheet("color: white;")
        self.newVmCpusAmountInputbox = QtWidgets.QLineEdit(self)
        self.newVmCpusAmountInputbox.setFixedSize(int(windowWidth - 350), 20)
        self.newVmCpusAmountInputbox.move(lineEditStart, 240)
        self.newVmCpusAmountInputbox.setStyleSheet("color: white;")
        self.newVmCpusAmountInputbox.setText("4")
        self.newVmCpusAmountInputbox.setValidator(QIntValidator())
        self.newVmCpusAmountInputbox.textChanged.connect(self.inputboxChanged)

        self.warnText = QtWidgets.QLabel(self)
        self.warnText.setText("Here's a warning text")
        self.warnText.setFont(QFont(fontNames.standard, 14))
        self.warnText.adjustSize()
        self.warnText.move(100, windowHeight - 100)
        self.warnText.setStyleSheet("color: white;")
        self.warnText.hide()
        
        self.confirmButton = QtWidgets.QPushButton(self)
        self.confirmButton.setText("Confirm")
        self.confirmButton.setFont(QFont(fontNames.splash, 10))
        self.confirmButton.adjustSize()
        self.confirmButton.move(windowWidth - self.confirmButton.width() - 80, windowHeight - 40)
        self.confirmButton.clicked.connect(self.createVm)
        self.confirmButton.setStyleSheet(f"color: {colors.disabled};")
        self.confirmButton.setDisabled(True)

    def newVmNameInputboxChanged(self, text):
        forbiddenSymbols = '[]/\\,!@#$%^&*()+='
        for symbol in forbiddenSymbols:
            if text.find(symbol) != -1:
                self.warnText.show()
                self.warnText.setText('VM Name contains a forbidden symbol')
                self.warnText.adjustSize()
                self.confirmButton.setStyleSheet(f"color: {colors.disabled};")
                self.confirmButton.setDisabled(True)
                self.newVmNameHasForbiddenSymbol = True
                return
        self.newVmNameHasForbiddenSymbol = False
        self.newVmPathInputbox.setText(os.path.join(os.getenv('HOME'), 'NXVMs', text))
        if self.inputboxChanged(''):
            self.warnText.hide()
            self.confirmButton.setStyleSheet("color: white;")
            self.confirmButton.setDisabled(False)

    def newVmPathInputboxChanged(self, text):
        if os.path.exists(text):
            self.warnText.setText(f"{text} already exists")
            self.warnText.adjustSize()
            self.warnText.show()
            self.confirmButton.setStyleSheet(f"color: {colors.disabled};")
            self.confirmButton.setDisabled(True)
        else:
            self.warnText.hide()
            self.confirmButton.setStyleSheet(f"color: white;")
            if self.inputboxChanged(''):
                self.confirmButton.setDisabled(False)

    def inputboxChanged(self, text):
        # Returns True if all is OK
        vmName = self.newVmNameInputbox.text()
        vmPath = self.newVmPathInputbox.text()
        vmRam = self.newVmRamInputbox.text()
        vmDiskSize = self.newVmDiskSizeInputbox.text()
        vmCpus = self.newVmCpusAmountInputbox.text()
        if '' in [vmName, vmPath, vmRam, vmDiskSize, vmCpus]:
            self.confirmButton.setStyleSheet(f"color: {colors.disabled};")
            self.confirmButton.setDisabled(True)
            return False
        elif not self.newVmNameHasForbiddenSymbol:
            self.confirmButton.setStyleSheet(f"color: white;")
            self.confirmButton.setDisabled(False)
            return True

    def createVm(self):
        vmName = self.newVmNameInputbox.text()
        vmPath = self.newVmPathInputbox.text()
        vmRam = int(self.newVmRamInputbox.text())
        vmDiskSize = int(self.newVmDiskSizeInputbox.text())
        vmCpus = int(self.newVmCpusAmountInputbox.text())

        if not os.path.exists(vmPath):
            os.makedirs(vmPath)
        # os.mkdir(self.newVmPathInputbox.text())
        os.chdir(self.newVmPathInputbox.text())
        with open('nxvm.yaml', 'w') as file:
            config = {
                'NAME': vmName,
                'RAM': vmRam,
                'HDA': f"{vmPath}/hda.qcow2",
                'CPUS': vmCpus,
                'CDROM': "",
                'ARCH': 'x86_64',
                'USE_KVM': 'TRUE',
                'USE_Q35': 'TRUE',
                'USE_HOST_CPU': 'TRUE',
                'GRAPHICS': 'vnc'
            }
            raw = yaml.dump(config)
            file.write(raw)
        os.system('qemu-img create -f qcow2 hda.qcow2 ' + str(vmDiskSize) + 'G')
        self.baseWindow.updateVmList()
        index = self.baseWindow.vmsList.index(config) + 1
        print(f"New VM Index: {index}")
        self.baseWindow.leftMenuList.setCurrentRow(index)
        # self.baseWindow.setToShowVm()
        # self.baseWindow.showVm.setVmConfig(config)
        self.close()

class Window(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.vmsList = []
        self.vmsPath = os.path.join(os.getenv('HOME'), 'NXVMs')
        self.ignoreRowChanged = False
        screenSize = app.desktop().availableGeometry()
        self.setGeometry(int((screenSize.width() - appWidth) / 2), int((screenSize.height() - appHeight) / 2), appWidth, appHeight)

        self.leftMenu = QtWidgets.QWidget(self)
        self.leftMenuLayout = QtWidgets.QVBoxLayout(self.leftMenu)
        self.leftMenu.move(0, 0)
        self.leftMenu.setFixedSize(int(appWidth / 4), appHeight)
        self.leftMenu.setStyleSheet(f"background-color: {colors.block};")

        self.leftMenuList = QtWidgets.QListWidget(self)
        self.leftMenuList.setFixedSize(self.leftMenu.width() - 60, appHeight - 180)
        self.leftMenuList.move(30, 80)
        self.leftMenuList.setStyleSheet(f"background-color: {colors.block}; color: white;")
        self.leftMenuList.currentRowChanged.connect(self.changeShowVm)

        self.menuTitle = QtWidgets.QLabel(self.leftMenu)
        self.menuTitle.setText("NXVM")
        self.menuTitle.setFont(QFont(fontNames.standard, 32))
        self.menuTitle.adjustSize()
        self.menuTitle.move(int((self.leftMenu.width() - self.menuTitle.width()) / 2), 10)
        self.menuTitle.setStyleSheet("color: white;")

        # self.mainMenuButton = QtWidgets.QPushButton(self.leftMenu)
        # self.mainMenuButton.setText("Main Menu")
        # self.mainMenuButton.setFont(QFont(fontNames.standard, 12))
        # self.mainMenuButton.setFixedSize(int(self.leftMenu.width() / 2), 50)
        # self.mainMenuButton.move(int((self.leftMenu.width() - self.mainMenuButton.width()) / 2),
        #                          self.leftMenu.height() - self.mainMenuButton.height() - 25)
        # self.mainMenuButton.clicked.connect(self.setToMainMenu)
        # self.mainMenuButton.setStyleSheet("color: white;")

        self.content = ContentWidget(self)

        self.showVm = ShowVmWindow(self.app, self)
        self.showVm.setFixedSize(appWidth - self.leftMenu.width(), appHeight)
        self.showVm.move(self.leftMenu.width(), 0)
        self.showVm.content.hide()
        self.updateVmList()
        self.leftMenuList.setCurrentRow(0)

    def setToShowVm(self):
        self.content.content.hide()
        self.showVm.content.show()
    def setToMainMenu(self):
        self.showVm.content.hide()
        self.content.content.show()

    def updateVmList(self):
        print('Updating VmList')
        self.vmsList = []
        self.ignoreRowChanged = True
        self.leftMenuList.clear()
        self.leftMenuList.addItems(['Main menu'])
        if os.path.exists(self.vmsPath):
            os.chdir(self.vmsPath)
            for path, dirs, files in os.walk(self.vmsPath):
                print(f"dirs: {dirs}")
                for dir in dirs:
                    if os.path.exists(self.vmsPath + '/' + dir + '/nxvm.yaml'):
                        with open(self.vmsPath + '/' + dir + '/nxvm.yaml', 'r') as file:
                            print(f"Reading nxvm.yaml in {dir}")
                            raw = file.read()
                            print(raw)
                            config = yaml.load(raw, yaml.Loader)
                            if not 'NAME' in config:
                                continue
                            else:
                                print('Found VM: ' + config['NAME'])
                                self.vmsList.append(config)
                                self.leftMenuList.addItems([config['NAME']])
                break
        self.ignoreRowChanged = False

    def changeShowVm(self, index):
        print(f"Changing ShowVM (ignore: {self.ignoreRowChanged}, index: {index})")
        if self.ignoreRowChanged or index == 0:
            self.setToMainMenu()
            return
        self.setToShowVm()
        # if index == len(self.vmsList):
        #     self.showVm.setVmConfig(self.vmsList[index])
        #     print(self.vmsList[index])
        # else:
        #     self.showVm.setVmConfig(self.vmsList[index - 1])
        #     print(self.vmsList[index - 1])
        if len(self.vmsList) != 0:
            self.showVm.setVmConfig(self.vmsList[index - 1])
        else:
            self.setToMainMenu()

def showBetaWarning():
    msg = QtWidgets.QMessageBox()
    msg.setText("You're using a beta version!\nThis program has a lot of bugs, program can be closed with errors "
                "for a many times!")
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setStyleSheet(f"background-color: {colors.bg}; color: white;")
    msg.exec_()

app = QtWidgets.QApplication([])
showBetaWarning()
window = Window(app)
window.show()
app.exec_()