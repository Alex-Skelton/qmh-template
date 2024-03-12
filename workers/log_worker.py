import asyncio

from loguru import logger

from workers.base_worker import BaseWorker
# Configure Loguru to write logs to a file, capping file size and rotating data. First In Last Out
logger.add("log_file.log", rotation="10 MB", enqueue=True)


class LogWorker(BaseWorker):
    def __init__(self, name, queues, active=False, timeout=2):
        super().__init__(name, queues)
        self.timeout = timeout
        self.active = active
        self.log_buffer = []

    async def main(self):
        max_length = 5
        while self.alive:
            command, data, sender = self.get_message(self.queues["main_queue"])
            if command == "shutdown":
                self.shutdown()

            elif command == "info":
                self.log_buffer.append(data)
                if len(self.log_buffer) >= max_length:
                    for log in self.log_buffer:
                        logger.info(log)
                    self.log_buffer.clear()

            elif command == "warning":
                logger.warning(data)

            elif command == "error":
                logger.error(data)

        await asyncio.sleep(self.timeout)

    def shutdown(self):
        self.alive = False
        for q in self.queues.values():
            self.send_message(q, "shutdown")
        for log in self.log_buffer:
            logger.info(log)
        self.log_buffer.clear()
