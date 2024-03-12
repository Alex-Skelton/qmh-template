import asyncio


class BaseWorker:
    def __init__(self, name, queues):
        self.name = name
        self.queues = queues
        self.alive = True
        self.loop = self.initialize_event_loop()

    @staticmethod
    def initialize_event_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

    def get_message(self, queue):
        command, data, sender = None
        try:
            if not queue.empty():
                msg = self.queues["main_queue"].get()
                command, data, sender = msg["command"], msg["data"], msg["sender"]
            return command, data, sender
        except Exception as e:
            self.alive = False
            self.log_msg("Error", f"{self.name}: Error receiving message from {queue.name}: {e}")

    def send_message(self, queue, command, data=""):
        try:
            # asyncio.run_coroutine_threadsafe(self.queue.put(data), loop)
            queue.put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            self.log_msg("Error", f"{self.name}: Error sending message to {queue.name}: {e}")

    def log_msg(self, level, msg):
        self.queues["log_queue"].put({"command": level,
                   "data": msg,
                   "sender": self.name})
