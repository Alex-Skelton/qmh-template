import asyncio
from multiprocessing import Process, Manager, freeze_support
import sys

from PyQt6 import QtWidgets

from workers.main_worker import MainWorker
from workers.daq_worker import

def main():
    with Manager() as manager:
        queues = {"gui_queue": manager.Queue(maxsize=100),
                  "main_queue": manager.Queue(maxsize=100),
                  "daq_queue": manager.Queue(maxsize=100)}

        queues["gui_queue"].name = "gui_queue"
        queues["main_queue"].name = "main_queue"
        queues["daq_queue"].name = "daq_queue"

        main_worker = MainWorker("main_controller", queues)
        p = Process(target=main_worker.main, args=())
        p.start()

        daq_worker =
        p = Process(target=start_serial, args=("micro_controller", queues, "COM 5"))
        p.start()

        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow("gui_controller", queues)
        mainWindow.show()

        ret = app.exec()
        p.join()  # Ensure the process finishes
        sys.exit(ret)


if __name__ == '__main__':
    freeze_support()
    main()

