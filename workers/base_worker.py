import asyncio
from _datetime import datetime

from multiprocessing import Queue

class BaseWorker:
    def __init__(self, name: str, queues: dict):
        self.name = name
        self.queues = queues
        self.alive = True

    def initialize_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())
        self.loop.close()

    async def main(self):
        pass

    def get_message(self, queue: Queue):
        msg = None
        try:
            if not queue.empty():
                msg = queue.get()
            return msg
        except Exception as e:
            self.alive = False
            self.log_msg("Error", f"{self.name}: Error receiving message from {queue.name}: {e}")

    def send_message(self, queue: Queue, command: str, data: str = ""):
        try:
            queue.put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            self.log_msg("Error", f"{self.name}: Error sending message to {queue.name}: {e}")

    def log_msg(self, level: str, msg: str):
        timestamp = datetime.now()
        log_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{log_time} - {msg}"
        recent_log = {"level": level, "msg": formatted_message}
        self.queues["log_queue"].put({"command": "log",
                   "data": recent_log,
                   "sender": self.name})
