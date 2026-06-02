import sys
import os
import socket
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.utils import encode_message, recv_message

CLUSTER = {
    1: ("127.0.0.1", 9001),
    2: ("127.0.0.1", 9002),
    3: ("127.0.0.1", 9003),
}


def send_request(host: str, port: int, payload: dict) -> dict | None:
    """Envía un mensaje y espera respuesta."""
    try:
        s = socket.create_connection((host, port), timeout=5)
        s.sendall(encode_message(payload))
        resp = recv_message(s)
        s.close()
        return resp
    except ConnectionRefusedError:
        print(f"  ✗ No se pudo conectar a {host}:{port}")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Cliente RegistroDistribuido")
    parser.add_argument("--nodo", type=int, default=1, choices=[1, 2, 3],
                        help="Nodo destino (1, 2 o 3)")
    parser.add_argument("--token", default="token-cliente-1",
                        help="Token de autenticación")
    args = parser.parse_args()

    host, port = CLUSTER[args.nodo]
    print(f"     Cliente RegistroDistribuido          ")
    print(f"  → Conectado a N{args.nodo} ({host}:{port})")
    print(f"  → Token: {args.token}")
    print(f"  Comandos: op <texto> | status | exit\n")

    while True:
        try:
            line = input("cliente> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "exit":
            break

        elif cmd == "op":
            if len(parts) < 2:
                print("  Uso: op <descripcion de la operacion>")
                continue
            operacion = parts[1]
            resp = send_request(host, port, {
                "type": "OPERACION",
                "token": args.token,
                "operacion": operacion,
            })
            if resp:
                if resp.get("type") == "ACK":
                    print(f"  ✓ ACK de N{resp['node']}: {resp['detalle']}")
                else:
                    print(f"  ✗ Respuesta: {resp}")

        elif cmd == "status":
            print(f"  ── Estado del clúster ──")
            for nid, (h, p) in CLUSTER.items():
                try:
                    s = socket.create_connection((h, p), timeout=1)
                    s.close()
                    estado = "✓ ACTIVO"
                except Exception:
                    estado = "✗ CAÍDO"
                print(f"    N{nid} ({h}:{p})  {estado}")

        else:
            print(f"  Comando desconocido: '{cmd}'")
            print(f"  Comandos válidos: op <texto> | status | exit")


if __name__ == "__main__":
    main()
