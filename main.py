from multiprocessing import Process, Manager, freeze_support
import sys

from PyQt6 import QtWidgets

from workers.log_worker import LogWorker
from workers.main_worker import MainWorker
from workers.gui import MainWindow
from workers.data_extract_worker import DataExtractWorker
from workers.iot_worker import IotWorker
from workers.named_queues import NamedQueues as q


def main():
    with Manager() as manager:
        queues = {q.log_queue: manager.Queue(maxsize=100),
                  q.gui_queue: manager.Queue(maxsize=100),
                  q.main_queue: manager.Queue(maxsize=100),
                  q.data_extract_queue: manager.Queue(maxsize=100),
                  q.iot_queue: manager.Queue(maxsize=100)}

        log_worker = LogWorker("log_worker", queues)
        log_worker_p = Process(target=log_worker.initialize_event_loop, args=())
        log_worker_p.start()

        main_worker = MainWorker("main_worker", queues)
        main_worker_p = Process(target=main_worker.initialize_event_loop, args=())
        main_worker_p.start()

        data_extract_worker = DataExtractWorker("data_extract_worker", queues)
        data_extract_worker_p = Process(target=data_extract_worker.initialize_event_loop, args=())
        data_extract_worker_p.start()

        iot_worker = IotWorker("iot_worker", queues)
        iot_worker_p = Process(target=iot_worker.initialize_event_loop, args=())
        iot_worker_p.start()

        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow("gui_controller", queues)
        mainWindow.show()

        ret = app.exec()
        log_worker_p.join()
        main_worker_p.join()
        data_extract_worker_p.join()
        iot_worker_p.join()
        sys.exit(ret)


if __name__ == '__main__':
    freeze_support()
    main()

