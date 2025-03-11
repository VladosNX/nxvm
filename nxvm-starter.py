#!/usr/bin/python3
import os
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

process = subprocess.Popen(['nxvm'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
process.wait()
exitcode = process.poll()
if exitcode != 0:
    app = QApplication([])
    msg = QtWidgets.QMessageBox()
    msg.setText("NXVM has been closed with error, see details below!\n\n"
                f"Exit code: {exitcode}\nstderr output: {process.stderr.read()}")
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setStyleSheet("background-color: #313131; color: white;")
    msg.exec_()
