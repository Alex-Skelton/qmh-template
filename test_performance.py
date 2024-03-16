from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(431, 276)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.start_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start_btn.setGeometry(QtCore.QRect(10, 10, 89, 25))
        self.start_btn.setObjectName("start_btn")
        self.stop_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.stop_btn.setGeometry(QtCore.QRect(130, 10, 89, 25))
        self.stop_btn.setObjectName("stop_btn")
        self.restart_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.restart_btn.setGeometry(QtCore.QRect(130, 40, 89, 25))
        self.restart_btn.setObjectName("restart_btn")
        self.frame_2 = QtWidgets.QFrame(parent=self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(20, 80, 191, 151))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label_2 = QtWidgets.QLabel(parent=self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(0, 10, 189, 16))
        self.label_2.setObjectName("label_2")
        self.workers_spinbox = QtWidgets.QSpinBox(parent=self.frame_2)
        self.workers_spinbox.setGeometry(QtCore.QRect(0, 30, 181, 26))
        self.workers_spinbox.setMinimum(1)
        self.workers_spinbox.setMaximum(10)
        self.workers_spinbox.setProperty("value", 2)
        self.workers_spinbox.setObjectName("workers_spinbox")
        self.label_3 = QtWidgets.QLabel(parent=self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(0, 90, 189, 21))
        self.label_3.setObjectName("label_3")
        self.samples_spinbox = QtWidgets.QSpinBox(parent=self.frame_2)
        self.samples_spinbox.setGeometry(QtCore.QRect(0, 110, 181, 26))
        self.samples_spinbox.setMinimum(1000)
        self.samples_spinbox.setMaximum(999999999)
        self.samples_spinbox.setSingleStep(1000)
        self.samples_spinbox.setObjectName("samples_spinbox")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(240, 30, 171, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(240, 10, 189, 16))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 431, 22))
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
        self.start_btn.setText(_translate("MainWindow", "Start Test"))
        self.stop_btn.setText(_translate("MainWindow", "Stop Test"))
        self.restart_btn.setText(_translate("MainWindow", "Restart Test"))
        self.label_2.setText(_translate("MainWindow", "Number workers to spawn"))
        self.label_3.setText(_translate("MainWindow", "Number samples to test"))
        self.label_4.setText(_translate("MainWindow", "Test completion time"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, name: str, queues, msg_check_interval: int=100, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.name = name
        self.log_list_text = []
        self.setupUi(self)
        self.queues = queues
        self.msg_check_interval = msg_check_interval
        self.iot_connected_btn.clicked.connect(lambda: self.connect_iot_device())
        self.tabWidget.currentChanged.connect(self.on_tab_changed)  # Connect the signal
        self.timer = QtCore.QTimer()
        self.timer.setInterval(msg_check_interval)
        self.timer.timeout.connect(self.check_queue)
        self.timer.start()

    def send_message(self, q_name, command: str, data: str = ""):
        try:
            self.queues[q_name].put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            self.log_msg("error", f"Error sending message to {q_name}: {e}", self.name)

    def check_queue(self):
        if not self.queues[q.gui_queue].empty():
            msg = self.queues[q.gui_queue].get()
            command, data, sender = msg["command"], msg["data"], msg["sender"]
            self.log_msg("info", str(msg), self.name)
            if command == "shutdown":
                self.close()


    def closeEvent(self, event):
        self.send_message(q.main_queue, "shutdown")
        super().closeEvent(event)

    def log_msg(self, level: str, msg: str, log_originator):
        timestamp = datetime.now()
        log_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{log_time} - log originator:{log_originator} - {msg}"
        recent_log = {"level": level, "msg": formatted_message}
        self.queues[q.log_queue].put({"command": "log",
                   "data": recent_log,
                   "sender": self.name})

    def connect_iot_device(self):
        self.send_message(q.iot_queue, "connect")
        self.iot_connected_btn.setText("Connecting...")
