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
        self.max_bugger_length = 5


    async def main(self):
        while self.alive:
            command, data, sender = self.get_message(self.queues["main_queue"])
            if command == "shutdown":
                self.shutdown()

            elif command in ["info", "warning", "error"]:
                self.log_with_buffer(command, data)

        await asyncio.sleep(self.timeout)

    def shutdown(self):
        self.alive = False
        for q in self.queues.values():
            self.send_message(q, "shutdown")
        for log in self.log_buffer:
            logger.info(log)
        self.log_buffer.clear()

    def log_with_buffer(self, command, data):
        recent_log = {"level": command,
                      "msg": data}
        self.log_buffer.append(recent_log)
        if len(self.log_buffer) >= self.max_bugger_length:
            for log in self.log_buffer:
                if log["level"] == "info":
                    logger.info(log)
                elif log["level"] == "warning":
                    logger.warning(log)
                elif log["level"] == "error":
                    logger.error(log)
            self.log_buffer.clear()
