from multiprocessing import Process, Manager, freeze_support
import sys

from PyQt6 import QtWidgets

from workers.log_worker import LogWorker
from workers.main_worker import MainWorker
from workers.gui import MainWindow
from workers.named_queues import NamedQueues as q


def main():
    with Manager() as manager:
        queues = {q.log_queue: manager.Queue(maxsize=100),
                  q.gui_queue: manager.Queue(maxsize=100),
                  q.main_queue: manager.Queue(maxsize=100)}

        log_worker = LogWorker("log_worker", queues)
        log_worker_p = Process(target=log_worker.initialize_event_loop, args=())
        log_worker_p.start()

        main_worker = MainWorker("main_worker", queues)
        main_worker_p = Process(target=main_worker.initialize_event_loop, args=())
        main_worker_p.start()

        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow("gui_controller", queues)
        mainWindow.show()

        ret = app.exec()
        log_worker_p.join()
        main_worker_p.join()
        sys.exit(ret)


if __name__ == '__main__':
    freeze_support()
    main()

