import argparse
import asyncio
import logging
import sys

from distributed_nodes.node import Node


def parse_peers(peers_str: str) -> list:
    """Parsea una cadena de peers en formato 'id:host:port,id:host:port'.
    """
    peers = []
    if not peers_str:
        return peers
    
    for peer in peers_str.split(","):
        try:
            parts = peer.strip().split(":")
            if len(parts) != 3:
                raise ValueError(f"Formato inválido: {peer}")
            
            node_id = int(parts[0])
            host = parts[1]
            port = int(parts[2])
            
            peers.append((node_id, host, port))
        except ValueError as e:
            print(f"Error parseando peer '{peer}': {e}", file=sys.stderr)
            sys.exit(1)
    
    return peers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Iniciar un nodo TCP con Lamport Clocks y Heartbeats.",
        epilog="Ejemplo de peers: --peers '2:127.0.0.1:5001,3:127.0.0.1:5002'"
    )
    parser.add_argument(
        "--node-id",
        type=int,
        required=True,
        help="Identificador único del nodo (entero >= 0)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host donde escuchar (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto TCP donde escuchar (default: 5000)",
    )
    parser.add_argument(
        "--peers",
        default="",
        help="Lista de peers en formato 'id:host:port,id:host:port' (opcional)",
    )
    parser.add_argument(
        "--hb-interval",
        type=float,
        default=2.0,
        help="Intervalo de heartbeat en segundos (default: 2.0)",
    )
    parser.add_argument(
        "--hb-timeout",
        type=float,
        default=6.0,
        help="Timeout de detección de caída en segundos (default: 6.0)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Aumentar verbosidad de logs",
    )
    
    args = parser.parse_args()

    # Configurar logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [NODO] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Parsear peers
    peers = parse_peers(args.peers)
    
    if peers:
        logging.info("Peers a registrar: %s", peers)

    # Crear y configurar nodo
    node = Node(
        node_id=args.node_id,
        host=args.host,
        port=args.port,
        heartbeat_interval=args.hb_interval,
        heartbeat_timeout=args.hb_timeout,
    )
    
    # Registrar peers
    if peers:
        node.register_peer_nodes(peers)
    
    # Iniciar nodo
    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        logging.info("Nodo %d detenido por el usuario.", args.node_id)
        
        # Mostrar resumen final
        print("\n")
        node.print_full_status()


if __name__ == "__main__":
    main()
