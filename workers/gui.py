from datetime import datetime
from multiprocessing import Process, Queue
import sys
import time

from PyQt6 import QtCore, QtGui, QtWidgets
from serial.tools import list_ports


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(659, 463)
        MainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.enable_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.enable_btn.setGeometry(QtCore.QRect(60, 110, 221, 41))
        self.enable_btn.setObjectName("enable_btn")
        # self.device_dropdown = QtWidgets.QComboBox(parent=self.centralwidget)
        self.device_dropdown = CustomComboBox(parent=self.centralwidget)
        self.device_dropdown.setGeometry(QtCore.QRect(10, 40, 351, 31))
        self.device_dropdown.setObjectName("device_dropdown")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 101, 17))
        self.label_2.setObjectName("label_2")
        self.log_list = QtWidgets.QListView(parent=self.centralwidget)
        self.log_list.setGeometry(QtCore.QRect(340, 190, 256, 192))
        self.log_list.setObjectName("log_list")
        self.model = QtCore.QStringListModel()
        self.log_list.setModel(self.model)
        self.status_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.status_btn.setEnabled(False)
        self.status_btn.setGeometry(QtCore.QRect(110, 240, 131, 101))
        self.status_btn.setObjectName("status_btn")
        self.serial_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.serial_btn.setEnabled(False)
        self.serial_btn.setGeometry(QtCore.QRect(610, 30, 25, 25))
        self.serial_btn.setAutoFillBackground(False)
        self.serial_btn.setText("")
        self.serial_btn.setObjectName("serial_btn")
        self.data_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.data_btn.setEnabled(False)
        self.data_btn.setGeometry(QtCore.QRect(610, 60, 25, 25))
        self.data_btn.setText("")
        self.data_btn.setObjectName("data_btn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 659, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.enable_btn.setText(_translate("MainWindow", "Enable"))
        self.label_2.setText(_translate("MainWindow", "Select device"))
        self.status_btn.setText(_translate("MainWindow", "Status"))


# Function for background process
def background_task(q):
    for i in range(5):
        q.put({"command": "status", "data": "Running"})
        time.sleep(5)
        q.put({"command": "status", "data": "Failure"})
        time.sleep(5)
        q.put({"command": "status", "data": "Standby"})
        time.sleep(5)
        q.put({"command": "status", "data": "Running"})
        time.sleep(5)

class CustomComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def showPopup(self):
        self.clear()  # Clear the existing items
        self.populate_com_ports()  # Populate the COM ports
        super().showPopup()  # Call the base class showPopup

    def populate_com_ports(self):
        com_ports = list_ports.comports()
        for port in com_ports:
            self.addItem(f"{port.device} - {port.description}")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, name, gui_queue, main_queue, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.name = name
        self.log_list_text = []
        self.setupUi(self)
        self.gui_queue = gui_queue
        self.gui_queue.name = "gui_q"
        self.main_queue = main_queue
        self.main_queue.name = "main_q"
        self.enable_btn.clicked.connect(lambda: self.send_message(self.main_queue,
                                                                  "start"))
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # Check every 100ms
        self.timer.timeout.connect(self.check_queue)
        self.timer.start()

    def send_message(self, queue, command, data=""):
        try:
            queue.put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            print(f"{self.name}: Error sending message to queue: {e}")

    def check_queue(self):
        if not self.gui_queue.empty():
            msg = self.gui_queue.get()
            command, data, sender = msg["command"], msg["data"], msg["sender"]
            now = datetime.now()
            formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
            log_msg = f"{formatted_time}; {self.name}: Received command ({command}) from ({sender})"
            self.log_list_text.append(log_msg)
            self.model.setStringList(self.log_list_text)
            if command == "status":
                if data == "Running":
                    colour = "#15d418"
                elif data == "Stopped":
                    colour = "#e38a17"
                elif data == "Interlock":
                    colour = "#d42515"
                else:
                    colour = "#b3b1ad"
                self.status_btn.setStyleSheet(f"QPushButton {{background-color: {colour}; color: black;}}")
                self.status_btn.setText(data)

    def closeEvent(self, event):
        # Logic to execute before the window closes
        print("Window is closing")
        self.send_message(self.main_queue, "shutdown")
        # Ensure the parent method gets called
        super().closeEvent(event)


if __name__ == "__main__":
    # Setup multiprocessing queue
    q = Queue()
    mainq = Queue()

    # Start the background process
    p = Process(target=background_task, args=(q,))
    p.start()

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(q, mainq)
    mainWindow.show()

    ret = app.exec()
    p.join()  # Ensure the process finishes
    sys.exit(ret)
