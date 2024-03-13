import asyncio

from loguru import logger

from workers.base_worker import BaseWorker


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
        print("running")
