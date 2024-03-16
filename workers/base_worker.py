import asyncio
from _datetime import datetime

from workers.named_queues import NamedQueues as q

class BaseWorker:
    def __init__(self, name: str, queues: dict):
        self.name = name
        self.queues = queues
        self.alive = True
        self.shutdown_initiated = False

    def initialize_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())
        self.loop.close()

    async def main(self):
        pass

    def start_process_shutdown(self):
        self.shutdown_initiated = True

    def start_application_shutdown(self):
        self.send_message(q.main_queue, "shutdown")

    def finalise_process_shutdown(self):
        self.alive = False

    def get_message(self, q_name):
        msg = None
        try:
            if not self.queues[q_name].empty():
                msg = self.queues[q_name].get()
            return msg
        except Exception as e:
            self.alive = False
            self.log_msg("error", f"Error receiving message from {q_name}: {e}", self.name)

    def send_message(self, q_name: str, command: str, data: str = ""):
        try:
            self.queues[q_name].put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            self.log_msg("error", f"Error sending message to {q_name}: {e}", self.name)

    def log_msg(self, level: str, msg: str, log_originator: str):
        timestamp = datetime.now()
        log_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{log_time} - log originator:{log_originator} - {msg}"
        recent_log = {"level": level, "msg": formatted_message}
        self.queues[q.log_queue].put({"command": "log",
                   "data": recent_log,
                   "sender": self.name})
