import asyncio
import random
import time

from workers.base_worker import BaseWorker


class MainWorker(BaseWorker):
    def __init__(self, name: str, queues: dict, active: bool=False,
                       msg_check_interval: float=0.2, run_interval: float=2):
        super().__init__(name, queues)
        self.active = active
        self.msg_check_interval = msg_check_interval
        self.run_interval = run_interval
        self.last_run_time = time.time()  # Track the last time run was executed

    async def main(self):
        while self.alive:
            msg = self.get_message(self.queues["main_queue"])
            if msg:
                command, data, sender = msg["command"], msg["data"], msg["sender"]
                self.log_msg("info", str(msg))
                if command == "shutdown":
                    self.shutdown()

                elif command == "start":
                    self.start()

                elif command == "stop":
                    self.stop()

            if self.active:
                self.run()

        await asyncio.sleep(self.msg_check_interval)

    def shutdown(self):
        self.alive = False
        for q in self.queues.values():
            self.send_message(q, "shutdown")

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def run(self):
        current_time = time.time()
        if (current_time - self.last_run_time) >= self.run_interval:
            value = random.random()
            if 0 <= value <= 0.3:  # Corrected condition
                data = "Running"
            elif 0.3 < value <= 0.6:  # Corrected condition
                data = "Stopped"
            elif value > 0.6:
                data = "Interlock"
            self.send_message(self.queues["gui_queue"], "status", data)
            self.last_run_time = current_time
