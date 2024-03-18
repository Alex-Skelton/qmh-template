import asyncio
import time

from workers.base_worker import BaseWorker
from workers.named_queues import NamedQueues as q


class TemplateWorker(BaseWorker):
    def __init__(self, name: str, queues: dict, active: bool=False,
                       msg_check_interval: float=0.5, run_interval: float=2):
        super().__init__(name, queues)
        self.active = active
        self.msg_check_interval = msg_check_interval
        self.run_interval = run_interval
        self.last_run_time = time.time()
        self.shutdown_initiated = False
        self.class_queue = q.main_queue

    async def main(self):
        while self.alive or not self.shutdown_initiated:
            msg = self.get_message(q.main_queue)
            if msg:
                command, data, sender = msg["command"], msg["data"], msg["sender"]
                self.log_msg("info", str(msg), self.name)
                if command == "shutdown":
                    self.start_process_shutdown()

                elif command == "start":
                    self.start()

                elif command == "stop":
                    self.stop()

            else:
                if self.shutdown_initiated and self.queues[q.log_queue].empty():
                    break
            if self.active:
                self.run()
            await asyncio.sleep(self.msg_check_interval)
        self.finalise_process_shutdown()

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def run(self):
        current_time = time.time()
        if (current_time - self.last_run_time) >= self.run_interval:
            self.last_run_time = current_time
