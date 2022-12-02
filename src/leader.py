import logging
from typing import Callable, Optional
import threading


class Leader:
    leader: Optional[int]
    id: int
    neighbors: [int]
    leader_mapper: Callable[[int], "Leader"]
    running_election: bool

    def __init__(self, id: int, neighbors: [int], leader_mapper: Callable[[int], "Leader"]):
        self.leader = None
        self.id = id
        self.neighbors = neighbors
        self.leader_mapper = leader_mapper
        self.running_election = False

    def receive_result(self, id: int):
        logging.info(f"Recebeu que {id} é o líder")
        self.leader = id
        return True

    def _disclose_result(self):
        for neighbor in self.neighbors:
            if neighbor == self.id:
                continue
            try:
                self.leader_mapper(neighbor).receive_result(self.leader)
            except Exception as e:
                logging.debug(self.leader_mapper)
                logging.debug(f"{self.leader=}")
                logging.debug(e)
                pass

    def start_election(self):
        if self.running_election:
            return True
        logging.debug("Iniciando eleição")
        self.running_election = True
        possible_leaders = filter(lambda nbr: nbr > self.id, self.neighbors)
        if possible_leaders:
            for pos_ldr in sorted(possible_leaders, reverse=True):
                try:
                    logging.debug(f"Perguntando se {pos_ldr} é o novo líder")
                    self.leader_mapper(pos_ldr).receive_election()
                    self.running_election = False
                    return True
                except Exception as e:
                    logging.debug(pos_ldr)
                    logging.debug(e)
                    continue
        logging.debug("Sou o novo leader")
        self.leader = self.id
        self._disclose_result()
        self.running_election = False
        return True

    def receive_election(self):
        thread = threading.Thread(target=self.start_election)
        thread.start()
        return True
