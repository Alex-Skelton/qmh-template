import asyncio
import random

from loguru import logger

from workers.base_worker import BaseWorker
# Configure Loguru to write logs to a file, capping file size and rotating data. First In Last Out
logger.add("log_file.log", rotation="10 MB", enqueue=True)


class MainWorker(BaseWorker):
    def __init__(self, name, queues, active=False, timeout=1):
        super().__init__(name, queues)
        self.timeout = timeout
        self.active = active

    async def main(self):
        while self.alive:
            command, data, sender = self.get_message(self.queues["main_queue"])
            if command == "shutdown":
                self.shutdown()

            elif command == "start":
                self.start()

            elif command == "stop":
                self.stop()

            elif command == "logger":
                self.create_log(data)

        if self.active:
            self.run()

        await asyncio.sleep(self.timeout)

    def shutdown(self):
        self.alive = False
        for q in self.queues.values():
            self.send_message(q, "shutdown")

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def run(self):
        command = "send"
        data = random.random()


    def create_log(self, data):
        if data["log_type"] == "info":
            logger.info(f"{data['sender']}: {data['msg']}")
        elif data["log_type"] == "warning":
            logger.warning(f"{data['sender']}: {data['msg']}")
        elif data["log_type"] == "error":
            logger.error(f"{data['sender']}: {data['msg']}")