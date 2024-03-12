import asyncio

class MicroController():
    def __init__(self, name, obj_queue, com_port, timeout=1):
        super().__init__()
        self.name = name
        self.obj_queue = obj_queue
        self.com_port = com_port
        self.timeout = timeout
        self.running = True
        self.connected = False
        self.connect()

    async def main(self):
        while self.running:
            try:
                if not self.obj_queue.empty():
                    task = self.obj_queue.get()
                    command, data = task["command"], task["data"]
                    if command == "shutdown":
                        self.disconnect()
                        self.shutdown()

                    if command == "connect":
                        self.connect()

                    if command == "disconnect":
                        self.disconnect()

                    elif command == "send":
                        self.send(data)

                await asyncio.sleep(self.timeout)

            except Exception as e:
                print(f"Error during run in {self.name}: {e}")
                self.running = False

    def shutdown(self):
        self.running = False

    def connect(self):
        self.connected = True
        print(f"Connected to {self.com_port}")

    def disconnect(self):
        self.connected = False
        print(f"Disconnected from {self.com_port}")

    def send(self, data):
        if self.connected:
            print(f"{self.com_port}: {data}")

    def send_message(self, queue, command, data=""):
        try:
            # asyncio.run_coroutine_threadsafe(self.queue.put(data), loop)
            queue.put({"command": command,
                       "data": data,
                       "sender": self.name})
        except Exception as e:
            print(f"{self.name}: Error sending message to queue: {e}")
