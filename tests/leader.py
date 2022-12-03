import logging
import os
import random
import threading
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from src.leader import Leader

NUM_PROCESSES = 4
MIN_WAIT = 5
MAX_WAIT = 10


def healthcheck():
    logging.info("Recebeu pedido de healthcheck")
    return True


def serve(leader: Leader) -> None:
    server = SimpleXMLRPCServer(("0.0.0.0", 8080))
    server.register_function(healthcheck, 'healthcheck')
    server.register_instance(leader)
    server.serve_forever()


def client(leader: Leader, process: int, event: threading.Event, clients: dict[int, ServerProxy]) -> None:
    event.wait(2)
    leader.start_election()
    while True:
        event.wait(random.randint(MIN_WAIT, MAX_WAIT))
        for i, client in clients.items():
            try:
                logging.info(f"Enviando healthcheck para {i}")
                client.healthcheck()
            except Exception as e:
                logging.debug(e)
                if i == leader.leader:
                    leader.start_election()
                    break


def run():
    process = int(os.getenv("PROCESS_NUM"))
    neighbors = list(range(1, NUM_PROCESSES + 1))
    leader = Leader(process, neighbors, None)
    event = threading.Event()
    logging.basicConfig(level=logging.DEBUG)
    
    thread = threading.Thread(target=serve, args=(leader,), daemon=True)
    thread.start()

    event.wait(3)
    clients = {i: ServerProxy(f"http://p{i}:8080") for i in neighbors}
    leader.leader_mapper = lambda i: clients.get(i)
    
    client(leader, process, event, clients)
