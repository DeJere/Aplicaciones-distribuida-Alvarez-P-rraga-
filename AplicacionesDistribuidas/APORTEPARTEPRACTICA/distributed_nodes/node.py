import asyncio
import json
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from distributed_nodes.event_logger import EventLogger
from distributed_nodes.heartbeat_manager import HeartbeatManager
from distributed_nodes.lamport_clock import LamportClock
from distributed_nodes.lamport_framing import (
    receive_message_with_lamport,
    send_message_with_lamport,
)
from distributed_nodes.node_registry import NodeRegistry


class Node:
    """Servidor TCP con sincronización de Relojes Lógicos de Lamport
    y tolerancia a fallos mediante Heartbeats.
    
    """

    def __init__(
        self,
        node_id: int,
        host: str = "127.0.0.1",
        port: int = 5000,
        heartbeat_interval: float = 2.0,
        heartbeat_timeout: float = 6.0,
    ) -> None:
        """Inicializa el nodo con Lamport Clock y Heartbeats.

        """
        self.node_id = node_id
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        # Inicializar reloj de Lamport
        self.lamport_clock = LamportClock(node_id=node_id)
        
        # Inicializar logger de eventos
        self.event_logger = EventLogger(node_id=node_id)
        
        # Inicializar registro de nodos
        self.node_registry = NodeRegistry(local_node_id=node_id)
        
        # Inicializar gestor de heartbeats
        self.heartbeat_manager = HeartbeatManager(
            local_node_id=node_id,
            registry=self.node_registry,
            heartbeat_interval=heartbeat_interval,
            heartbeat_timeout=heartbeat_timeout,
            event_logger=self.event_logger,
        )
        
        logging.info(
            "Nodo %d inicializado en %s:%d "
            "(heartbeat: intervalo=%.1fs, timeout=%.1fs)",
            self.node_id,
            self.host,
            self.port,
            self.heartbeat_interval,
            self.heartbeat_timeout
        )

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Maneja la conexión de un cliente con sincronización de Lamport."""
        peer = writer.get_extra_info("peername")
        
        # Evento: conexión entrante
        ts = self.lamport_clock.event()
        self.event_logger.log_event(
            event_type="CONNECTION_RECEIVED",
            lamport_timestamp=ts,
            description=f"Conexión entrante desde {peer}",
            metadata={"peer": str(peer)},
        )
        logging.info("Conexión entrante desde %s [T=%d]", peer, ts)
        
        try:
            # Enviar mensaje de bienvenida
            welcome_msg = {
                "type": "WELCOME",
                "status": "connected",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat(),
            }
            ts_welcome = self.lamport_clock.send_message()
            await send_message_with_lamport(writer, welcome_msg, ts_welcome)
            
            self.event_logger.log_message_sent(
                lamport_timestamp=ts_welcome,
                target_node=None,
                message_type="WELCOME",
            )

            # Procesar mensajes del cliente
            while not reader.at_eof():
                try:
                    message, remote_lamport = await receive_message_with_lamport(reader)
                    if message is None:
                        break

                    # Sincronizar reloj de Lamport
                    ts_received = self.lamport_clock.receive_message(remote_lamport)
                    
                    # Verificar si es un heartbeat
                    if self.heartbeat_manager.is_heartbeat(message):
                        # Procesar heartbeat
                        source_node_id = message.get("node_id")
                        self.heartbeat_manager.handle_heartbeat(
                            message,
                            ts_received,
                            source_node_id
                        )
                        # No enviar respuesta a heartbeats
                        continue
                    
                    self.event_logger.log_message_received(
                        lamport_timestamp=ts_received,
                        remote_lamport=remote_lamport,
                        source_node=None,
                        message_type=message.get("type", "UNKNOWN"),
                    )

                    logging.info(
                        "Operación recibida de %s: %s [T_local=%d, T_remoto=%d]",
                        peer,
                        message.get("type"),
                        ts_received,
                        remote_lamport,
                    )

                    # Procesar la operación
                    response = await self.process_operation(message, peer, ts_received)

                    # Enviar respuesta
                    ts_response = self.lamport_clock.send_message()
                    await send_message_with_lamport(writer, response, ts_response)
                    
                    self.event_logger.log_message_sent(
                        lamport_timestamp=ts_response,
                        target_node=None,
                        message_type=response.get("type", "UNKNOWN"),
                    )

                except asyncio.IncompleteReadError:
                    ts = self.lamport_clock.event()
                    self.event_logger.log_event(
                        event_type="CONNECTION_CLOSED",
                        lamport_timestamp=ts,
                        description=f"Conexión cerrada por {peer}",
                    )
                    logging.info("Conexión cerrada por %s [T=%d]", peer, ts)
                    break
                    
                except json.JSONDecodeError as error:
                    logging.error("Error al decodificar JSON de %s: %s", peer, error)
                    ts = self.lamport_clock.event()
                    error_response = {
                        "type": "ERROR",
                        "status": "invalid_json",
                        "message": str(error),
                    }
                    ts_error = self.lamport_clock.send_message()
                    await send_message_with_lamport(writer, error_response, ts_error)
                    
                except Exception as error:
                    logging.error("Error procesando mensaje de %s: %s", peer, error)
                    ts = self.lamport_clock.event()
                    error_response = {
                        "type": "ERROR",
                        "status": "processing_error",
                        "message": str(error),
                    }
                    ts_error = self.lamport_clock.send_message()
                    await send_message_with_lamport(writer, error_response, ts_error)

            ts_final = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="CONNECTION_FINALIZED",
                lamport_timestamp=ts_final,
                description=f"Conexión finalizada con {peer}",
            )
            logging.info("Conexión finalizada con %s [T=%d]", peer, ts_final)
            
        except Exception as error:
            logging.exception("Error manejando la conexión de %s: %s", peer, error)
        finally:
            writer.close()
            await writer.wait_closed()

    async def process_operation(self, message: dict, peer: str, lamport_ts: int) -> dict:
        """Procesa una operación con registro de evento.

        Args:
            message: Diccionario con la operación.
            peer: Información del cliente.
            lamport_ts: Timestamp de Lamport sincronizado.

        Returns:
            Diccionario con la respuesta.
        """
        operation_type = message.get("type", "UNKNOWN")
        
        # Registrar operación procesada
        self.event_logger.log_operation_processed(
            lamport_timestamp=lamport_ts,
            operation_type=operation_type,
            client_id=str(peer),
        )
        
        if operation_type == "PING":
            return {
                "type": "PONG",
                "status": "ok",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat(),
                "echo": message.get("data"),
            }
        
        elif operation_type == "ECHO":
            return {
                "type": "ECHO_RESPONSE",
                "status": "ok",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat(),
                "data": message.get("data"),
            }
        
        elif operation_type == "INFO":
            return {
                "type": "INFO_RESPONSE",
                "status": "ok",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat(),
                "node_host": self.host,
                "node_port": self.port,
                "client": str(peer),
                "lamport_clock": self.lamport_clock.get_current(),
            }
        
        else:
            logging.warning(
                "Operación desconocida de %s: %s [T=%d]",
                peer,
                operation_type,
                lamport_ts
            )
            return {
                "type": "ERROR",
                "status": "unknown_operation",
                "message": f"Operación '{operation_type}' no reconocida",
            }

    async def start(self) -> None:
        """Inicia el servidor TCP y escucha conexiones con heartbeat."""
        # Registrar evento de inicio de servidor
        ts = self.lamport_clock.event()
        self.event_logger.log_event(
            event_type="SERVER_STARTED",
            lamport_timestamp=ts,
            description=f"Nodo escuchando en {self.host}:{self.port}",
            metadata={"host": self.host, "port": self.port},
        )
        logging.info(
            "Nodo %d escuchando en %s:%s [T=%d]",
            self.node_id,
            self.host,
            self.port,
            ts
        )
        
        # Iniciar heartbeat manager
        self.heartbeat_manager.start()
        
        try:
            server = await asyncio.start_server(self.handle_client, self.host, self.port)
            
            async with server:
                await server.serve_forever()
        finally:
            # Detener heartbeat manager
            self.heartbeat_manager.stop()
    
    def register_peer_node(self, node_id: int, host: str, port: int) -> None:
        """Registra otro nodo en la red para heartbeating.
        
        Args:
            node_id: Identificador del nodo remoto.
            host: Host del nodo remoto.
            port: Puerto del nodo remoto.
        """
        self.node_registry.register_node(node_id, host, port)
        
        ts = self.lamport_clock.event()
        self.event_logger.log_event(
            event_type="PEER_REGISTERED",
            lamport_timestamp=ts,
            description=f"Nodo {node_id} registrado como peer",
            metadata={"peer_node_id": node_id, "host": host, "port": port},
        )
    
    def register_peer_nodes(self, nodes: List[Tuple[int, str, int]]) -> None:
        """Registra múltiples nodos en la red.
        
        Args:
            nodes: Lista de tuplas (node_id, host, port).
        """
        self.node_registry.register_nodes(nodes)
        
        ts = self.lamport_clock.event()
        self.event_logger.log_event(
            event_type="PEERS_REGISTERED",
            lamport_timestamp=ts,
            description=f"Se registraron {len(nodes)} nodos como peers",
            metadata={"peer_count": len(nodes), "peers": nodes},
        )
    
    def get_node_status(self) -> dict:
        """Obtiene el estado completo del nodo.
        
        Returns:
            Diccionario con información del nodo.
        """
        return {
            "node_id": self.node_id,
            "address": f"{self.host}:{self.port}",
            "lamport_clock": self.lamport_clock.get_current(),
            "events_logged": len(self.event_logger),
            "registered_peers": len(self.node_registry),
            "alive_peers": len(self.node_registry.get_alive_nodes()),
            "dead_peers": len(self.node_registry.get_dead_nodes()),
            "heartbeat_stats": self.heartbeat_manager.get_stats(),
        }
    
    def print_full_status(self) -> None:
        """Imprime el estado completo del nodo con todos sus componentes."""
        status = self.get_node_status()
        
        print(f"\n{'='*80}")
        print(f"Estado Completo del Nodo {self.node_id}")
        print(f"{'='*80}\n")
        
        print(f"Configuración:")
        print(f"  Dirección: {status['address']}")
        print(f"  Reloj de Lamport: {status['lamport_clock']}")
        print(f"  Eventos registrados: {status['events_logged']}")
        
        print(f"\nPeers en la Red:")
        print(f"  Total registrados: {status['registered_peers']}")
        print(f"  Vivos: {status['alive_peers']}")
        print(f"  Caídos: {status['dead_peers']}")
        
        print(f"\nHeartbeats:")
        print(f"  Enviados: {status['heartbeat_stats']['heartbeats_sent']}")
        print(f"  Recibidos: {status['heartbeat_stats']['heartbeats_received']}")
        print(f"  Estado: {'CORRIENDO' if status['heartbeat_stats']['is_running'] else 'DETENIDO'}")
        
        print(f"\n{'='*80}\n")
        
        # Mostrar estado de peers
        self.node_registry.print_status()
        
        # Mostrar estadísticas de heartbeat
        self.heartbeat_manager.print_stats()
