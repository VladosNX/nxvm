#!/bin/python3
import time
import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QIntValidator
import random
import os
import yaml
import subprocess
import threading
import shutil
from nxvmtranslate import translateInit
import sys
from check_configs import check_configs

check_configs()
version = '0.4.0'
globalConfig = yaml.load(open(os.getenv('HOME') + '/NXVMs/config.yaml').read(), yaml.Loader)
translate = translateInit(globalConfig['LANGUAGE'])

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

def parseCustomOptions(options):
    result = []
    quote, doubleQuote = False, False
    section = ''
    i = 0
    backslash = False
    optionsLength = len(options)
    while i < optionsLength:
        symbol = options[i]
        if symbol == '\\':
            backslash = True
        elif symbol == "'" and not backslash:
            quote = not quote
        elif symbol == "'" and not backslash:
            doubleQuote = not doubleQuote
        elif symbol == ' ' and not True in [quote, doubleQuote]:
            result.append(section)
            section = ''
        else:
            section += symbol
        if i == optionsLength - 1:
            result.append(section)
        i += 1
    return result

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
        self.welcomeText.setText(translate['welcomeToNXVM'])
        self.welcomeText.setFont(QFont(fontNames.standard, 12))
        self.welcomeText.adjustSize()
        self.welcomeText.move(int((self.content.width() - self.welcomeText.width()) / 2), 240)
        self.welcomeText.setStyleSheet("color: white;")

        self.newVmButton = QtWidgets.QPushButton(self.content)
        self.newVmButton.setText(translate['newVm'])
        self.newVmButton.setFont(QFont(fontNames.standard))
        self.newVmButton.adjustSize()
        self.newVmButton.move(int((self.content.width() - self.newVmButton.width()) / 2) - 100, 300)
        self.newVmButton.setStyleSheet("color: white;")
        self.newVmButton.clicked.connect(self.newVm)

        self.openVmButton = QtWidgets.QPushButton(self.content)
        self.openVmButton.setText(translate['openVm'])
        self.openVmButton.setFont(QFont(fontNames.standard))
        self.openVmButton.adjustSize()
        self.openVmButton.move(int((self.content.width() - self.openVmButton.width()) / 2), 300)
        self.openVmButton.setStyleSheet("color: white;")

        self.settingsButton = QtWidgets.QPushButton(self.content)
        self.settingsButton.setText(translate['settings'])
        self.settingsButton.setFont(QFont(fontNames.standard))
        self.settingsButton.adjustSize()
        self.settingsButton.move(int((self.content.width() - self.openVmButton.width()) / 2) + 100, 300)
        self.settingsButton.setStyleSheet("color: white;")
        self.settingsButton.clicked.connect(self.openSettings)

        self.qemuNotInstalledBox = QtWidgets.QWidget(self.content)
        self.qemuNotInstalledBox.setFixedSize(self.content.width() - 100, 100)
        self.qemuNotInstalledBox.move(50, 450)
        self.qemuNotInstalledBox.setStyleSheet(f"background-color: {colors.block}")

        self.qemuNotInstalledTitle = QtWidgets.QLabel(self.qemuNotInstalledBox)
        self.qemuNotInstalledTitle.setText(translate['qemuIsNotInstalled'])
        self.qemuNotInstalledTitle.setFont(QFont(fontNames.standard, 18))
        self.qemuNotInstalledTitle.adjustSize()
        self.qemuNotInstalledTitle.move(20, 20)
        self.qemuNotInstalledTitle.setStyleSheet("color: white;")

        self.qemuNotInstalledText = QtWidgets.QLabel(self.qemuNotInstalledBox)
        self.qemuNotInstalledText.setText(translate['qemuNotInstalledText'])
        self.qemuNotInstalledText.setFont(QFont(fontNames.standard, 12))
        self.qemuNotInstalledText.setFixedSize(self.qemuNotInstalledBox.width() - 60, 30)
        self.qemuNotInstalledText.setStyleSheet("border: none; color: white;")
        self.qemuNotInstalledText.setOpenExternalLinks(True)
        self.qemuNotInstalledText.move(20, 60)
        self.qemuNotInstalledUpdate()
        
    def newVm(self):
        self.newVmWindow = NewVmWindow(self.app, self.parent)
        self.newVmWindow.show()
        self.newVmWindow.raise_()

    def openSettings(self):
        self.settingsWindow = SettingsWindow(self.app, self.parent)
        self.settingsWindow.show()

    def qemuNotInstalledUpdate(self):
        found = False
        for item in os.getenv('PATH').split(':'):
            if os.path.exists(f'{item}/qemu-system-x86_64'):
                found = True
                break
        if found:
            self.qemuNotInstalledBox.hide()
        else:
            self.qemuNotInstalledBox.show()

class ShowVmWindow(QtWidgets.QMainWindow):
    def __init__(self, app, parent):
        super().__init__()
        self.app = app
        self.vmConfig = None
        self.subprocess = None
        self.thread = None
        self.vncThread = None
        self.vncProcess = None
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
        self.runButton.setText(translate['run'])
        self.runButton.setFont(QFont(fontNames.splash))
        self.runButton.setFixedSize(100, 30)
        self.runButton.move(200, 10)
        self.runButton.setStyleSheet("color: white;")
        self.runButton.clicked.connect(self.runVm)

        self.stopButton = QtWidgets.QPushButton(self.content)
        self.stopButton.setText(translate['stop'])
        self.stopButton.setFont(QFont(fontNames.splash))
        self.stopButton.setFixedSize(100, 30)
        self.stopButton.move(200, 10)
        self.stopButton.setStyleSheet("color: white;")
        self.stopButton.clicked.connect(self.stopVm)
        self.stopButton.hide()

        self.vncViewButton = QtWidgets.QPushButton(self.content)
        self.vncViewButton.setText(translate['connectToVNC'])
        self.vncViewButton.setFont(QFont(fontNames.splash))
        self.vncViewButton.setFixedSize(120, 30)
        self.vncViewButton.move(int((self.content.width() - self.vncViewButton.width()) / 2), 10)
        self.vncViewButton.clicked.connect(self.vncViewStart)
        self.vncViewButton.setDisabled(True)
        self.vncViewButton.setStyleSheet(f"color: {colors.disabled};")

        self.cdromBootCheckbox = QtWidgets.QCheckBox(self.content)
        self.cdromBootCheckbox.setText(translate['cdromBoot'])
        self.cdromBootCheckbox.setFont(QFont(fontNames.standard, 14))
        self.cdromBootCheckbox.setStyleSheet(checkboxStyle)
        self.cdromBootCheckbox.adjustSize()
        self.cdromBootCheckbox.move(100, appHeight - 100)

        self.settingsButton = QtWidgets.QPushButton(self.content)
        self.settingsButton.setText(translate['settings'])
        self.settingsButton.setFont(QFont(fontNames.splash))
        self.settingsButton.setFixedSize(100, 30)
        self.settingsButton.move(appWidth - parent.leftMenu.width() - self.settingsButton.width() - 200, 10)
        self.settingsButton.setStyleSheet("color: white;")
        self.settingsButton.clicked.connect(self.openSettings)

    def loadOption(self, key):
        if key in self.vmConfig:
            return self.vmConfig[key]
        else:
            return ''

    def setVmConfig(self, vmConfig):
        self.vmConfig = vmConfig
        description = ""
        for k, v in vmConfig.items():
            if f"vmconfig_{k}" in translate:
                value = f'`{v}`'
                if v == '': value = f"*{translate['valueNotSet']}*"
                elif v == 'TRUE': value = f"*{translate['valueTrue']}*"
                elif v == 'FALSE': value = f"*{translate['valueFalse']}*"
                description += f"**{translate[f'vmconfig_{k}']}**: {value}\n\n"
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
        for item in parseCustomOptions(self.loadOption('CUSTOM_OPTIONS')):
            command.append(item)

        # TODO: Parse custom options
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
        self.subprocess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
                if not code in [0, -9]:
                    stderr = self.subprocess.stderr.read()
                    print('\nFailed with error:\n' + stderr)
                    QtCore.QMetaObject.invokeMethod(
                        self.parent,
                        "_show_error_message",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, stderr),
                        QtCore.Q_ARG(int, code)
                    )

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
        if self.parent.nxvmConfig['VNCVIEWER'] == 'tigervnc':
            self.vncProcess = subprocess.Popen(['vncviewer', 'localhost:5900', 'MenuKey=Pause'],
                                               stdout=subprocess.PIPE, text=True)
        elif self.parent.nxvmConfig['VNCVIEWER'] == 'remmina':
            self.vncProcess = subprocess.Popen(['remmina', 'vnc://localhost:5900'],
                                               stdout=subprocess.PIPE, text=True)

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
        self.settingsTitle.setText(translate['settings'])
        self.settingsTitle.setFont(QFont(fontNames.splash, 28))
        self.settingsTitle.adjustSize()
        self.settingsTitle.move(50, int((self.titleBlock.height() - self.settingsTitle.height()) / 2))
        self.settingsTitle.setStyleSheet("color: white;")

        self.vmNameSubtitle = QtWidgets.QLabel(self.titleBlock)
        self.vmNameSubtitle.setText(self.config['NAME'])
        self.vmNameSubtitle.setFont(QFont(fontNames.splash, 14))
        self.vmNameSubtitle.adjustSize()
        self.vmNameSubtitle.move(self.titleBlock.width() - self.vmNameSubtitle.width() - 50,
                        int((self.titleBlock.height() - self.vmNameSubtitle.height()) / 2))
        self.vmNameSubtitle.setStyleSheet("color: white;")

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
        self.vmNameInputbox.setText(self.config['NAME'])
        self.vmNameHint = QtWidgets.QLabel(self.vmNameWidget)
        self.vmNameHint.setText(translate['vmName'] + ':')
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
        self.vmHdaPathHint.setText(translate['pathToHda'] + ':')
        self.vmHdaPathHint.setFont(QFont(fontNames.standard, 14))
        self.vmHdaPathHint.setStyleSheet("color: white;")
        self.vmHdaPathHint.adjustSize()
        self.vmHdaPathHint.move(hintStart, 50)
        self.vmHdaPathFileDialog = QtWidgets.QPushButton(self.vmStorageWidget)
        self.vmHdaPathFileDialog.setFixedSize(fileButtonWidth, lineEditHeight)
        self.vmHdaPathFileDialog.setText(translate['browse'])
        self.vmHdaPathFileDialog.move(fileButtonStart, 50)
        self.vmHdaPathFileDialog.setStyleSheet("color: white;")
        self.vmHdaPathFileDialog.clicked.connect(lambda: self.vmHdaPathInputbox.setText(self.openFileSelect("HDA Path")[0]))

        self.vmCdromPathInputbox = QtWidgets.QLineEdit(self.vmStorageWidget)
        self.vmCdromPathInputbox.setFixedSize(fileEditWidth, lineEditHeight)
        self.vmCdromPathInputbox.move(lineEditStart, 80)
        self.vmCdromPathInputbox.setStyleSheet("color: white;")
        self.vmCdromPathInputbox.setText(self.config['CDROM'])
        self.vmCdromPathHint = QtWidgets.QLabel(self.vmStorageWidget)
        self.vmCdromPathHint.setText(translate['pathToCdrom'] + ':')
        self.vmCdromPathHint.setFont(QFont(fontNames.standard, 14))
        self.vmCdromPathHint.setStyleSheet("color: white;")
        self.vmCdromPathHint.adjustSize()
        self.vmCdromPathHint.move(hintStart, 80)
        self.vmCdromPathFileDialog = QtWidgets.QPushButton(self.vmStorageWidget)
        self.vmCdromPathFileDialog.setFixedSize(fileButtonWidth, lineEditHeight)
        self.vmCdromPathFileDialog.setText(translate['browse'])
        self.vmCdromPathFileDialog.move(fileButtonStart, 80)
        self.vmCdromPathFileDialog.setStyleSheet("color: white;")
        self.vmCdromPathFileDialog.clicked.connect(lambda: self.vmCdromPathInputbox.setText(self.openFileSelect("CDROM Path")[0]))

        # Hardware block
        self.vmHardwareWidget = QtWidgets.QWidget()
        self.vmCpusInputbox = QtWidgets.QLineEdit(self.vmHardwareWidget)
        self.vmCpusInputbox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vmCpusInputbox.move(lineEditStart, 50)
        self.vmCpusInputbox.setStyleSheet("color: white;")
        self.vmCpusInputbox.setText(str(self.config['CPUS']))
        self.vmCpusInputbox.setValidator(QIntValidator())
        self.vmCpusHint = QtWidgets.QLabel(self.vmHardwareWidget)
        self.vmCpusHint.setText(translate['cpusAmount'] + ':')
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
        self.vmRamHint.setText(f"{translate['ram']} (MB):")
        self.vmRamHint.setFont(QFont(fontNames.standard, 14))
        self.vmRamHint.setStyleSheet("color: white;")
        self.vmRamHint.adjustSize()
        self.vmRamHint.move(hintStart, 80)

        self.vmUseKvmCheckbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseKvmCheckbox.setText(translate['useKvmAcceleration'])
        self.vmUseKvmCheckbox.setStyleSheet(checkboxStyle)
        self.vmUseKvmCheckbox.adjustSize()
        self.vmUseKvmCheckbox.move(lineEditStart, 110)
        self.vmUseKvmCheckbox.setChecked(True if self.config['USE_KVM'] == 'TRUE' else False)

        self.vmUseQ35Checkbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseQ35Checkbox.setText(translate['emulateIntelQ35Chipset'])
        self.vmUseQ35Checkbox.setStyleSheet(checkboxStyle)
        self.vmUseQ35Checkbox.adjustSize()
        self.vmUseQ35Checkbox.move(lineEditStart, 140)
        self.vmUseQ35Checkbox.setChecked(True if self.config['USE_Q35'] == 'TRUE' else False)

        self.vmUseHostCpuCheckbox = QtWidgets.QCheckBox(self.vmHardwareWidget)
        self.vmUseHostCpuCheckbox.setText(translate['allowUsingHostCpu'])
        self.vmUseHostCpuCheckbox.setStyleSheet(checkboxStyle)
        self.vmUseHostCpuCheckbox.adjustSize()
        self.vmUseHostCpuCheckbox.move(lineEditStart, 170)
        self.vmUseHostCpuCheckbox.setChecked(True if self.config['USE_HOST_CPU'] == 'TRUE' else False)

        # Custom options widget
        self.customOptionsWidget = QtWidgets.QWidget()
        self.customOptionsHint = QtWidgets.QLabel(self.customOptionsWidget)
        self.customOptionsHint.setText(translate['customQemuOptions'])
        self.customOptionsHint.setFont(QFont(fontNames.standard, 14))
        self.customOptionsHint.setStyleSheet("color: white;")
        self.customOptionsHint.adjustSize()
        self.customOptionsHint.move(hintStart, 20)

        self.customOptionsInputbox = QtWidgets.QTextEdit(self.customOptionsWidget)
        self.customOptionsInputbox.setText(self.loadOption('CUSTOM_OPTIONS'))
        self.customOptionsInputbox.setFixedSize(500, 200)
        self.customOptionsInputbox.move(hintStart, 50)
        self.customOptionsInputbox.setStyleSheet("color: white;")

        # Deleting block
        self.deleteVmWidget = QtWidgets.QWidget()
        self.deleteVmWarning = QtWidgets.QLabel(self.deleteVmWidget)
        self.deleteVmWarning.setText(translate['deleteVmWarning'])
        self.deleteVmWarning.setFont(QFont(fontNames.splash, 18))
        self.deleteVmWarning.adjustSize()
        self.deleteVmWarning.setStyleSheet("color: red;")

        self.deleteVmText = QtWidgets.QTextEdit(self.deleteVmWidget)
        self.deleteVmText.setReadOnly(True)
        self.deleteVmText.setMarkdown(translate['deleteVmText'].replace('$FOLDER', self.vmPath))
        self.deleteVmText.setFixedSize(self.deleteVmWidget.width(), 60)
        self.deleteVmText.setStyleSheet('color: white;')
        self.deleteVmText.move(0, 30)

        self.deleteButton = QtWidgets.QPushButton(self)
        self.deleteButton.setText(translate['confirm'])
        self.deleteButton.setStyleSheet('color: white;')
        self.deleteButton.adjustSize()
        self.deleteButton.move(windowWidth - self.deleteButton.width() - 50, windowHeight - 50)
        self.deleteButton.clicked.connect(self.deleteVm)
        self.deleteButton.hide()

        # Left menu
        self.leftMenu = QtWidgets.QListWidget(self)
        self.leftMenu.setFixedSize(180, windowHeight - self.titleBlock.height() - 20)
        self.leftMenu.move(10, self.titleBlock.height() + 10)
        self.leftMenu.setStyleSheet(f"background-color: {colors.block}; color: white;")
        self.leftMenu.addItems([
            translate['vmName'], translate['storage'], translate['hardware'], translate['deleteVm'],
            translate['customOptions']])
        self.leftMenu.currentRowChanged.connect(self.changeBlock)

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.setFixedSize(windowWidth - self.leftMenu.width() - 30,
                                        windowHeight - self.titleBlock.height() - 70)
        self.stackedWidget.move(self.leftMenu.width() + 20, self.titleBlock.height() + 10)
        self.stackedWidget.addWidget(self.vmNameWidget)
        self.stackedWidget.addWidget(self.vmStorageWidget)
        self.stackedWidget.addWidget(self.vmHardwareWidget)
        self.stackedWidget.addWidget(self.deleteVmWidget)
        self.stackedWidget.addWidget(self.customOptionsWidget)

        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setText(translate['save'])
        self.saveButton.setStyleSheet("color: white;")
        self.saveButton.adjustSize()
        self.saveButton.move(windowWidth - self.saveButton.width() - 50, windowHeight - 50)
        self.saveButton.clicked.connect(self.saveSettings)

    def loadOption(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return ''

    def openFileSelect(self, title):
        selecter = QtWidgets.QFileDialog()
        selecter.setStyleSheet("color: white;")
        return selecter.getOpenFileName(self, title)

    def changeBlock(self, index):
        self.stackedWidget.setCurrentIndex(index)
        if index == 3:
            self.saveButton.hide()
            self.deleteButton.show()
        else:
            self.saveButton.show()
            self.deleteButton.hide()

    def deleteVm(self):
        msg = QtWidgets.QMessageBox()
        msg.setText(translate['deleteVmConfirmation'])
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        code = msg.exec_()
        if code == QtWidgets.QMessageBox.Yes:
            self.close()
            shutil.rmtree(self.vmPath)
            self.parent.parent.updateVmList()

    def saveSettings(self):
        self.vmName = self.vmNameInputbox.text()
        self.vmHda = self.vmHdaPathInputbox.text()
        self.vmCdrom = self.vmCdromPathInputbox.text()
        self.vmCpus = int(self.vmCpusInputbox.text())
        self.vmRam = int(self.vmRamInputbox.text())
        self.vmUseKvm = 'TRUE' if self.vmUseKvmCheckbox.isChecked() else 'FALSE'
        self.vmUseQ35 = 'TRUE' if self.vmUseQ35Checkbox.isChecked() else 'FALSE'
        self.vmUseHostCpu = 'TRUE' if self.vmUseHostCpuCheckbox.isChecked() else 'FALSE'
        self.customOptions = self.customOptionsInputbox.toPlainText()
        config = {
            'ARCH': 'x86_64',
            'NAME': self.vmName,
            'HDA': self.vmHda,
            'CDROM': self.vmCdrom,
            'RAM': self.vmRam,
            'CPUS': self.vmCpus,
            'USE_KVM': self.vmUseKvm,
            'USE_Q35': self.vmUseQ35,
            'USE_HOST_CPU': self.vmUseHostCpu,
            'CUSTOM_OPTIONS': self.customOptions
        }
        raw = yaml.dump(config)
        print(self.vmPath)
        with open(self.vmPath + '/nxvm.yaml', 'w') as file:
            file.write(raw)
        # self.parent.parent.updateVmList()
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
        self.setWindowTitle(translate['newVirtualMachine'])
        self.setStyleSheet(f"background-color: {colors.bg};")

        self.titleBlock = QtWidgets.QWidget(self)
        self.titleBlockLayout = QtWidgets.QVBoxLayout(self.titleBlock)
        self.titleBlock.setFixedSize(windowWidth, 100)
        self.titleBlock.move(0, 0)
        self.titleBlock.setStyleSheet(f"background-color: {colors.block};")

        self.newVmTitle = QtWidgets.QLabel(self.titleBlock)
        self.newVmTitle.setText(translate['newVirtualMachine'])
        self.newVmTitle.setFont(QFont(fontNames.splash, 24))
        self.newVmTitle.adjustSize()
        self.newVmTitle.move(int((windowWidth - self.newVmTitle.width()) / 2), int((self.titleBlock.height() - self.newVmTitle.height()) / 2))
        self.newVmTitle.setStyleSheet("color: white;")

        lineEditStart = 270

        self.newVmNameHint = QtWidgets.QLabel(self)
        self.newVmNameHint.setText(translate['vmName'] + ':')
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
        self.newVmPathHint.setText(translate['vmPath'] + ':')
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
        self.newVmRamHint.setText(translate['ram'] + ':')
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
        self.newVmDiskSizeHint.setText(translate['diskSize'] + ':')
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
        self.newVmCpusAmountHint.setText(translate['cpusAmount'] + ':')
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
        self.confirmButton.setText(translate['confirm'])
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
                self.warnText.setText(translate['nameContainsForbiddenSymbol'])
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
            self.warnText.setText(translate['folderAlreadyExists'].replace('$FOLDER', text))
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
                'GRAPHICS': 'vnc',
                'CUSTOM_OPTIONS': ''
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

class SettingsWindow(QtWidgets.QMainWindow):
    def __init__(self, app, parent):
        super().__init__()
        self.app = app
        self.parent = parent
        self.vncViewersLabels = ['Tiger VNC', 'Remmina']
        self.vncViewers = ['tigervnc', 'remmina']
        self.vncViewersPaths = ['/bin/vncviewer', '/bin/remmina']
        self.languages = ['Русский', 'English']

        screenSize = self.app.desktop().availableGeometry()
        windowWidth = 1000
        windowHeight = 500
        self.setGeometry(int((screenSize.width() - windowWidth) / 2), int((screenSize.height() - windowHeight) / 2),
                         windowWidth, windowHeight)
        self.setStyleSheet(f"background-color: {colors.bg};")

        with open(os.path.join(os.getenv('HOME'), 'NXVMs', 'config.yaml'), 'r') as file:
            raw = file.read()

        self.titleBlock = QtWidgets.QWidget(self)
        self.titleBlock.setFixedSize(windowWidth, 100)
        self.titleBlock.move(0, 0)
        self.titleBlock.setStyleSheet(f"background-color: {colors.block};")

        self.settingsTitle = QtWidgets.QLabel(self.titleBlock)
        self.settingsTitle.setText(translate['settings'])
        self.settingsTitle.setFont(QFont(fontNames.splash, 28))
        self.settingsTitle.adjustSize()
        self.settingsTitle.move(50, int((self.titleBlock.height() - self.settingsTitle.height()) / 2))
        self.settingsTitle.setStyleSheet("color: white;")

        self.nxvmSubtitle = QtWidgets.QLabel(self.titleBlock)
        self.nxvmSubtitle.setText(f"NXVM v{version}")
        self.nxvmSubtitle.setFont(QFont(fontNames.splash, 14))
        self.nxvmSubtitle.adjustSize()
        self.nxvmSubtitle.move(self.titleBlock.width() - self.nxvmSubtitle.width() - 50,
                    int((self.titleBlock.height() - self.nxvmSubtitle.height()) / 2))
        self.nxvmSubtitle.setStyleSheet("color: white;")

        # Widgets for stacked widget
        lineEditWidth = 400
        lineEditHeight = 25
        lineEditStart = 250
        fileEditWidth = 300
        fileButtonStart = lineEditStart + fileEditWidth + 10
        fileButtonWidth = 90
        hintStart = 50

        self.generalWidget = QtWidgets.QWidget()
        self.vncViewerHint = QtWidgets.QLabel(self.generalWidget)
        self.vncViewerHint.setText(translate['vncViewer'])
        self.vncViewerHint.setFont(QFont(fontNames.standard, 14))
        self.vncViewerHint.setStyleSheet("color: white;")
        self.vncViewerHint.adjustSize()
        self.vncViewerHint.move(hintStart, 50)
        self.vncViewerCombobox = QtWidgets.QComboBox(self.generalWidget)
        self.vncViewerCombobox.setFixedSize(lineEditWidth, lineEditHeight)
        self.vncViewerCombobox.move(lineEditStart, 50)
        self.vncViewerCombobox.addItems(self.vncViewersLabels)
        self.vncViewerCombobox.setCurrentIndex(self.vncViewers.index(globalConfig['VNCVIEWER']))
        self.vncViewerCombobox.setStyleSheet("color: white;")
        self.vncViewerCombobox.currentIndexChanged.connect(self.updateVncViewerStatus)

        self.vncViewerStatus = QtWidgets.QLabel(self.generalWidget)
        self.vncViewerStatus.setFont(QFont(fontNames.splash, 12))
        self.vncViewerStatus.adjustSize()
        self.vncViewerStatus.move(lineEditStart, 80)
        self.vncViewerStatus.setStyleSheet("color: white;")
        self.updateVncViewerStatus(self.vncViewerCombobox.currentIndex())

        self.languageHint = QtWidgets.QLabel(self.generalWidget)
        self.languageHint.setText(translate['language'])
        self.languageHint.setFont(QFont(fontNames.standard, 14))
        self.languageHint.setStyleSheet("color: white;")
        self.languageHint.adjustSize()
        self.languageHint.move(hintStart, 110)
        self.languageCombobox = QtWidgets.QComboBox(self.generalWidget)
        self.languageCombobox.setFixedSize(lineEditWidth, lineEditHeight)
        self.languageCombobox.move(lineEditStart, 110)
        self.languageCombobox.addItems(self.languages)
        self.languageCombobox.setCurrentIndex(self.languages.index(globalConfig['LANGUAGE']))
        self.languageCombobox.setStyleSheet("color: white;")

        self.leftMenu = QtWidgets.QListWidget(self)
        self.leftMenu.setFixedSize(180, windowHeight - self.titleBlock.height() - 20)
        self.leftMenu.move(10, self.titleBlock.height() + 10)
        self.leftMenu.setStyleSheet(f"background-color: {colors.block}; color: white;")
        self.leftMenu.addItems([translate['general']])
        self.leftMenu.currentRowChanged.connect(self.changeBlock)

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.setFixedSize(windowWidth - self.leftMenu.width() - 30,
                                        windowHeight - self.titleBlock.height() - 70)
        self.stackedWidget.move(self.leftMenu.width() + 20, self.titleBlock.height() + 10)
        self.stackedWidget.addWidget(self.generalWidget)

        self.saveButton = QtWidgets.QPushButton(self)
        self.saveButton.setText(translate['save'])
        self.saveButton.setStyleSheet("color: white;")
        self.saveButton.adjustSize()
        self.saveButton.move(windowWidth - self.saveButton.width() - 50, windowHeight - 50)
        self.saveButton.clicked.connect(self.saveSettings)

    def changeBlock(self, index): pass

    def saveSettings(self):
        oldLanguage = globalConfig['LANGUAGE']
        newConfig = {
            'VNCVIEWER': self.vncViewers[self.vncViewerCombobox.currentIndex()],
            'LANGUAGE': self.languages[self.languageCombobox.currentIndex()]
        }
        with open(os.path.join(os.getenv('HOME'), 'NXVMs', 'config.yaml'), 'w') as file:
            file.write(yaml.dump(newConfig))
        self.parent.updateConfig()
        if newConfig['LANGUAGE'] != oldLanguage:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle('Restart NXVM')
            msg.setStyleSheet(f"background-color: {colors.bg}; color: white;")
            msg.setText(translate['restartAfterChangeLanguage'])
            msg.exec_()
        self.close()

    def updateVncViewerStatus(self, index):
        viewerPath = self.vncViewersPaths[index]
        viewerLabel = self.vncViewersLabels[index]
        if not os.path.exists(viewerPath):
            self.vncViewerStatus.setText(translate['vncViewerNotFound'].replace('$VIEWER', viewerLabel))
            self.vncViewerStatus.adjustSize()
        else:
            self.vncViewerStatus.setText("")

class Window(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.vmsList = []
        self.vmsPath = os.path.join(os.getenv('HOME'), 'NXVMs')
        self.ignoreRowChanged = False
        screenSize = app.desktop().availableGeometry()
        self.setGeometry(int((screenSize.width() - appWidth) / 2), int((screenSize.height() - appHeight) / 2), appWidth, appHeight)
        self.nxvmConfig = None
        self.updateConfig()

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
        self.menuTitle.setFont(QFont(fontNames.splash, 32))
        self.menuTitle.adjustSize()
        self.menuTitle.move(int((self.leftMenu.width() - self.menuTitle.width()) / 2), 10)
        self.menuTitle.setStyleSheet("color: white;")

        self.content = ContentWidget(self)

        self.showVm = ShowVmWindow(self.app, self)
        self.showVm.setFixedSize(appWidth - self.leftMenu.width(), appHeight)
        self.showVm.move(self.leftMenu.width(), 0)
        self.showVm.content.hide()
        self.updateVmList()
        self.leftMenuList.setCurrentRow(0)

    @QtCore.pyqtSlot(str, int)
    def _show_error_message(self, stderr, code):
        msg = QtWidgets.QMessageBox()
        msg.setText("Failed to start VM, see details below:\n\n"
                    f"Exit code: {code}\n"
                    f"stderr output:\n{stderr}")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setStyleSheet(f"background-color: {colors.bg}; color: white;")
        msg.exec_()

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
        self.leftMenuList.addItems([translate['mainMenu']])
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
        if len(self.vmsList) != 0:
            self.showVm.setVmConfig(self.vmsList[index - 1])
        else:
            self.setToMainMenu()

    def updateConfig(self):
        if not os.path.exists(os.path.join(os.getenv('HOME'), 'NXVMs', 'config.yaml')):
            os.makedirs(os.path.join(os.getenv('HOME'), 'NXVMs'))
            with open(os.path.join(os.getenv('HOME'), 'NXVMs', 'config.yaml'), 'w') as file:
                file.write("VNCVIEWER: tigervnc")
        with open(os.path.join(os.getenv('HOME'), 'NXVMs', 'config.yaml'), 'r') as file:
            raw = file.read()
            self.nxvmConfig = yaml.load(raw, yaml.Loader)

def showBetaWarning():
    msg = QtWidgets.QMessageBox()
    msg.setText(translate['betaWarning'].replace('\\n', '\n'))
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setStyleSheet(f"background-color: {colors.bg}; color: white;")
    msg.exec_()

app = QtWidgets.QApplication([])
showBetaWarning()
window = Window(app)
window.show()
app.exec_()
