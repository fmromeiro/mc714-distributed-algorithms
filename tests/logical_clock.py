import logging
import os
import random
import threading
import time
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer
from src.logical_clock import Clock

NUM_PROCESSES = 4
MIN_WAIT = 5
MAX_WAIT = 10


def respond(params: dict) -> dict:
    return {"param": params["param"], "response": random.randint(0, 100)}


def serve(clock: Clock) -> None:
    server = SimpleXMLRPCServer(("0.0.0.0", 8080))
    server.register_function(clock.recv(respond), "number")
    server.serve_forever()


def client(clock: Clock, process: int, event: threading.Event) -> None:
    processes = []
    clients = []
    for i in range(1, NUM_PROCESSES + 1):
        # logging.info(f'criando {process} {i}')
        if i != process:
            processes.append(i)
            clients.append(clock.send(ServerProxy(f"http://p{i}:8080").number))
    while True:
        event.wait(random.randint(MIN_WAIT, MAX_WAIT))
        target = random.randint(0, NUM_PROCESSES - 2)
        logging.info(f'{process} disparou para {processes[target]}')
        clients[target]({"param": process, "target": processes[target]})


def run():
    process = int(os.getenv("PROCESS_NUM"))
    clock = Clock(process, 2)
    event = threading.Event()
    logging.basicConfig(level=logging.DEBUG)

    thread = threading.Thread(target=serve, args=(clock,), daemon=True)
    thread.start()
    
    event.wait(3)
    client(clock, process, event)
