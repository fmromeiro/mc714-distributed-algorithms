from datetime import datetime
import json
import logging
import threading
from typing import *

CLOCK_START = 0

class Clock:
    def __init__(self: "Clock", process: str, debug_level: int = 2) -> "Clock":
        self._clock = CLOCK_START
        self._process = process
        self.debug_level = debug_level
        self._lock = threading.Lock()

    def debug_message(self: "Clock", msg: str, obj: dict = None) -> None:
        if self.debug_level >= 1:
            logging.info(
                f"[{datetime.now().strftime('%c')}] {msg} {self._clock}.{self._process}")

            if self.debug_level >= 2 and obj:
                logging.info(json.dumps(obj, sort_keys=True, indent=4))

    def get_time(self: "Clock") -> int:
        return self._clock

    def event(self: "Clock", msg: str = "", obj: dict = None) -> None:
        with self._lock:
            self._clock += 1
        msg = msg if msg else "Evento local"
        self.debug_message(msg, obj)

    def recv(self: "Clock", func: Callable[dict, dict]) -> Callable[dict, dict]:
        def _recv(params: dict) -> dict:
            with self._lock:
                ts = max(self._clock, params.get('ts', CLOCK_START)) + 1
                self._clock = ts
            self.debug_message("Recebeu evento e relógio local é", {
                               "params": params})
            result = func(params)
            self.event("Rodou função do RPC")
            with self._lock:
                self._clock += 1
                result['ts'] = self._clock
            self.debug_message("Disparou retorno e relógio local é", {
                               "params": params})
            return result
        return _recv

    def send(self: "Clock", func: Callable[dict, dict]) -> Callable[dict, dict]:
        def _send(params: dict) -> dict:
            with self._lock:
                self._clock += 1
                params['ts'] = self._clock
            self.debug_message("Disparou evento e relógio local é", {
                               "params": params})
            result = func(params)
            with self._lock:
                ts = max(self._clock, result.get('ts', 0)) + 1
                self._clock = result['ts'] = ts
            self.debug_message("Recebeu retorno e relógio local é", {
                               "result": result, "params": params})
            return result
        return _send
