import argparse
import socket
import threading
import signal
import sys
import os
from typing import Dict, Any

# Aseguramos que el paquete common sea localizable cuando se ejecuta desde nodo/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
from common.utils import LamportClock, encode_message, recv_message, is_valid_token


class NodeServer:
    def __init__(self, node_id: int, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.clock = LamportClock()
        self.operations: list[Dict[str, Any]] = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.is_running = threading.Event()

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running.set()
        print(f"Nodo {self.node_id} escuchando en {self.host}:{self.port}")

        try:
            while self.is_running.is_set():
                client_socket, client_address = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        self.is_running.clear()
        try:
            self.server_socket.close()
        except OSError:
            pass
        print(f"Nodo {self.node_id} detenido")

    def handle_client(self, client_socket: socket.socket, client_address: tuple[str, int]) -> None:
        try:
            message = recv_message(client_socket)
            if not message:
                return

            token = message.get("token", "")
            if not is_valid_token(token):
                error = {"type": "ERROR", "detail": "Token inválido o ausente"}
                client_socket.sendall(encode_message(error))
                return

            if message.get("type") != "OPERACION":
                error = {"type": "ERROR", "detail": "Tipo de mensaje desconocido"}
                client_socket.sendall(encode_message(error))
                return

            operation = str(message.get("operacion", "")).strip()
            current_clock = self.clock.tick()
            record = {
                "node": self.node_id,
                "clock": current_clock,
                "operation": operation,
            }
            self.operations.append(record)

            response = {
                "type": "ACK",
                "node": self.node_id,
                "clock": current_clock,
                "detalle": f"Operación '{operation}' registrada con LC={current_clock}",
            }
            client_socket.sendall(encode_message(response))
            print(f"[{self.node_id}] {client_address} -> {operation} (LC={current_clock})")
        except Exception as exc:
            error = {"type": "ERROR", "detail": f"Error interno: {exc}"}
            try:
                client_socket.sendall(encode_message(error))
            except OSError:
                pass
        finally:
            try:
                client_socket.close()
            except OSError:
                pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nodo de registro distribuido con reloj de Lamport y autenticación simple"
    )
    parser.add_argument("node_id", type=int, help="Identificador del nodo")
    parser.add_argument("port", type=int, help="Puerto TCP donde escuchará el nodo")
    parser.add_argument("--host", default="127.0.0.1", help="Dirección del host donde escuchar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = NodeServer(args.node_id, args.host, args.port)

    def handle_signal(signum: int, frame: Any) -> None:
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    server.start()


if __name__ == "__main__":
    main()
