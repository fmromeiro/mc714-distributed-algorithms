import logging
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

    def receive_request(self, process: int):
        logging.info(f"Recebi pedido de mutex para {process}")
        with self._lock:
            if self.in_use:
                logging.info(f"Mutex em uso, adicionando na fila {self.queue}")
                self.queue.append(process)
                return False
            logging.info("Fila vazia, liberando mutex")
            self.in_use = True
            return True

    def release(self):
        logging.info("Liberando mutex")
        with self._lock:
            if self.queue:
                logging.info(f"Próximo da fila é {self.queue[0]}")
                self.clients[self.queue.pop()].allow()
                return True
            logging.info("Fila vazia, liberando mutex")
            self.in_use = False
            return True


class MutualExclusionClient:
    callback: Callable
    leader: MutualExclusionLeader
    process: int

    def __init__(self, process: int):
        self.process = process

    def request(self, callback: Callable) -> bool:
        logging.info("Vou solicitar o mutex")
        self.callback = callback
        if self.leader.receive_request(self.process):
            logging.info("Consegui o mutex na hora")
            callback()

    def allow():
        logging.info("Consegui o mutex depois")
        self.callback()
        logging.info("Acabou a chamada do mutex")

    def release():
        leader.release()