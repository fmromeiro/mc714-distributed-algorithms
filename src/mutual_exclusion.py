import threading
from typing import Callable


class MutualExclusionLeader:
    queue: [int]
    in_use: bool
    _lock: threading.Lock
    clients: ["MutualExclusionClient"]

    def __init__(self):
        self.queue = []
        self.in_use = False
        self._lock = threading.Lock()

    def receive_request(self, id: int):
        with self._lock:
            if in_use:
                queue.append(id)
                return False
            return True

    def release(self):
        with self._lock:
            if queue:
                clients[queue.pop()].allow()
                return True
            self.in_use = False
            return True


class MutualExclusionClient:
    callback: Callable
    leader: MutualExclusionLeader
    id: int

    def __init__(self, id: int):
        self.id = id

    def request(self, callback: Callable) -> bool:
        self.callback = callback
        if self.leader.receive_request(id):
            callback()

    def allow():
        self.callback()
