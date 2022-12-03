import logging
import os
import random
import threading
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from src.mutual_exclusion import MutualExclusionClient, MutualExclusionLeader
from src.leader import Leader


NUM_PROCESSES = 4
MIN_WAIT = 5
MAX_WAIT = 10
REQUEST_CHANCE = 0.4


def callback(mutexLeader: MutualExclusionLeader, event: threading.Event):
    logging.info("Consegui o mutex hehe (≖⌣≖)")
    event.wait(random.randint(MIN_WAIT, MAX_WAIT))
    logging.info("Vou liberar o mutex")
    mutexClient.release()

def serve(leader: Leader, mutexLeader: MutualExclusionLeader, mutexClient: MutualExclusionClient) -> None:
    server = SimpleXMLRPCServer(("0.0.0.0", 8080))
    server.register_instance(leader)
    # server.register_instance(mutexLeader)
    server.register_function(mutexLeader.receive_request, "receive_request")
    server.register_function(mutexLeader.release, "release")
    # server.register_instance(mutexClient)
    server.register_function(mutexClient.allow, "allow")
    server.register_function(mutexClient.request, "request")
    server.serve_forever()


def client(leader: Leader, mutexLeader: MutualExclusionLeader, mutexClient: MutualExclusionClient, id: int, event: threading.Event()):
    event.wait(2)
    leader.start_election()
    event.wait(10)
    while True:
        event.wait(random.randint(MIN_WAIT, MAX_WAIT))
        if id != leader.leader:
            roll = random.random()
            if roll < REQUEST_CHANCE:
                mutexClient.request(lambda: callback(event))



def run():
    process = int(os.getenv("PROCESS_NUM"))
    neighbors = list(range(1, NUM_PROCESSES + 1))
    leader = Leader(process, neighbors, None)
    mutexLeader = MutualExclusionLeader()
    mutexClient = MutualExclusionClient(process)
    event = threading.Event()
    logging.basicConfig(level=logging.DEBUG)

    thread = threading.Thread(target=serve, args=(
        leader, mutexLeader, mutexClient), daemon=True)
    thread.start()

    event.wait(3)
    clients = {i: ServerProxy(f"http://p{i}:8080") for i in neighbors}
    leader.leader_mapper = lambda i: clients.get(i)
    mutexLeader.clients = lambda i: clients.get(i)
    mutexClient.leader = mutexLeader

    client(leader, mutexLeader, mutexClient, process, event)
