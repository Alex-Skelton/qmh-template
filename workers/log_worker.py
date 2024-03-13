import asyncio

from loguru import logger

from workers.base_worker import BaseWorker

# Configure Loguru to write logs to a file, capping file size and rotating data. First In Last Out
logger.add("log_file.log", rotation="10 MB", enqueue=True)


class LogWorker(BaseWorker):
    def __init__(self, name: str, queues: dict, active: bool = False, msg_check_interval: float=0.2):
        super().__init__(name, queues)
        self.msg_check_interval = msg_check_interval
        self.active = active
        self.log_buffer = []
        self.max_bugger_length = 5

    async def main(self):
        while self.alive:
            msg = self.get_message(self.queues["log_queue"])
            if msg:
                command, data, sender = msg["command"], msg["data"], msg["sender"]
                if command == "shutdown":
                    self.shutdown()

                elif command == "log":
                    # self.log_with_buffer(data)
                    self.log_no_buffer(data)

        await asyncio.sleep(self.msg_check_interval)

    def shutdown(self):
        self.alive = False
        for q in self.queues.values():
            self.send_message(q, "shutdown")
        for log in self.log_buffer:
            logger.info(log)
        self.log_buffer.clear()

    def log_with_buffer(self, msg: str):
        self.log_buffer.append(msg)
        if len(self.log_buffer) >= self.max_bugger_length:
            for log in self.log_buffer:
                if log["level"] == "info":
                    logger.info(msg)
                elif log["level"] == "warning":
                    logger.warning(msg)
                elif log["level"] == "error":
                    logger.error(msg)
            self.log_buffer.clear()

    def log_no_buffer(self, msg: dict):
        if msg["level"] == "info":
            logger.info(msg["msg"])
        elif msg["level"] == "warning":
            logger.warning(msg["msg"])
        elif msg["level"] == "error":
            logger.error(msg["msg"])
