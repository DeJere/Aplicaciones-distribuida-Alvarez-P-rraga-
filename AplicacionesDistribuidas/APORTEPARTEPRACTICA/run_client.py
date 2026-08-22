import argparse
import asyncio
import logging

from distributed_nodes.client import Client


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Conectar un cliente a un nodo TCP con Lamport Clocks."
    )
    parser.add_argument(
        "--client-id",
        type=int,
        required=True,
        help="Identificador único del cliente (entero >= 0)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host del nodo.")
    parser.add_argument("--port", type=int, default=5000, help="Puerto TCP del nodo.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [CLIENT] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    client = Client(client_id=args.client_id, host=args.host, port=args.port)
    asyncio.run(client.connect())
    
    # Mostrar resumen de eventos
    client.event_logger.print_events_summary()


if __name__ == "__main__":
    main()
