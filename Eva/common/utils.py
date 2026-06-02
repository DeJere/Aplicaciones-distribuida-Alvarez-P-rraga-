import json
import re
import socket
import struct
import threading
import time
from typing import Any, Dict, Optional

VALID_TOKENS = {"token-cliente-1", "token-cliente-2", "token-admin"}


def is_valid_token(token: str) -> bool:
    return token in VALID_TOKENS


class LamportClock:
    def __init__(self, value: int = 0):
        self._clock = value
        self._lock = threading.Lock()

    def tick(self) -> int:
        with self._lock:
            self._clock += 1
            return self._clock

    def update(self, received: int) -> int:
        with self._lock:
            self._clock = max(self._clock, received) + 1
            return self._clock

    @property
    def value(self) -> int:
        with self._lock:
            return self._clock


HEADER_SIZE = 4


def encode_message(payload: Dict[str, Any]) -> bytes:
    body = json.dumps(payload).encode("utf-8")
    header = struct.pack(">I", len(body))
    return header + body


def recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
    data = b""
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
        except OSError:
            return None
        if not chunk:
            return None
        data += chunk
    return data


def recv_message(sock: socket.socket) -> Optional[Dict[str, Any]]:
    raw_len = recv_exact(sock, HEADER_SIZE)
    if raw_len is None:
        return None
    (length,) = struct.unpack(">I", raw_len)
    raw_body = recv_exact(sock, length)
    if raw_body is None:
        return None
    return json.loads(raw_body.decode("utf-8"))


def log(node_id: str, clock: int, msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [N{node_id}] [LC={clock:03d}] {msg}")
