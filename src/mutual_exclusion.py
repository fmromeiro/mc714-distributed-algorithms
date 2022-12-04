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

    def release_mutex(self):
        logging.info("Liberando mutex")
        next_process = None
        with self._lock:
            if self.queue:
                next_process = self.queue.pop(0)
        if next_process:
            logging.info(f"Próximo da fila é {next_process}")
            self.clients(next_process).allow()
            return True
        logging.info("Fila vazia, liberando mutex")
        self.in_use = False
        return True


class MutualExclusionClient:
    callback: Callable
    leader: MutualExclusionLeader
    process: int
    _lock: threading.Lock

    def __init__(self, process: int):
        self.process = process
        self._lock = threading.Lock()

    def request(self, callback: Callable) -> bool:
        logging.info("Vou solicitar o mutex")
        self.callback = callback
        with self._lock:
            result = self.leader.receive_request(self.process)
        if result:
            logging.info("Consegui o mutex na hora")
            callback()

    def allow(self):
        logging.info("Consegui o mutex depois")
        thread = threading.Thread(target=self.callback)
        thread.start()
        return True

    def release(self):
        logging.info("Entrando no release")
        with self._lock:
            logging.info("Começando liberação do mutex")
            self.leader.release_mutex()
            logging.info("Terminei liberação do mutex")