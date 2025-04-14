import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox

NXVMS_PATH = os.getenv('HOME') + '/NXVMs'
CONFIG_PATH = f'{NXVMS_PATH}/config.yaml'
DOTNXVM_PATH = os.getenv('HOME') + '/.nxvm'

DEFAULT_CONFIG = "LANGUAGE: English\nVNCVIEWER: tigervnc"

def check_configs():
    if not os.path.exists(CONFIG_PATH):
        if not os.path.exists(NXVMS_PATH):
            os.mkdir(NXVMS_PATH)
        open(CONFIG_PATH, 'w').write(DEFAULT_CONFIG)
    if not os.path.exists(DOTNXVM_PATH):
        os.write(2, f'[\x1b[31mX\x1b[0m] {DOTNXVM_PATH} not found. You need to reinstall NXVM\n'.encode())
        app = QApplication([])
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("NXVM Start Failure")
        msg.setText(f"{DOTNXVM_PATH} not found. You need to reinstall NXVM")
        msg.setStyleSheet("background-color: #313131; color: white;")
        msg.show()
        app.exec_()
        sys.exit(1)