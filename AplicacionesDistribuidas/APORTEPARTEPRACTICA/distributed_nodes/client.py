import asyncio
import json
import logging
from datetime import datetime

from distributed_nodes.event_logger import EventLogger
from distributed_nodes.lamport_clock import LamportClock
from distributed_nodes.lamport_framing import (
    receive_message_with_lamport,
    send_message_with_lamport,
)


class Client:
    """Cliente TCP con sincronización de Relojes Lógicos de Lamport.
   
    """

    def __init__(
        self,
        client_id: int,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> None:
        """Inicializa el cliente con Lamport Clock.
    
        """
        self.client_id = client_id
        self.host = host
        self.port = port
        
        # Inicializar reloj de Lamport
        self.lamport_clock = LamportClock(node_id=client_id)
        
        # Inicializar logger de eventos
        self.event_logger = EventLogger(node_id=client_id)
        
        logging.info(
            "Cliente %d inicializado. Conectará a %s:%d",
            self.client_id,
            self.host,
            self.port
        )

    async def connect(self) -> None:
        """Conecta con el nodo y ejecuta operaciones de prueba."""
        ts = self.lamport_clock.event()
        self.event_logger.log_event(
            event_type="CONNECTION_STARTED",
            lamport_timestamp=ts,
            description=f"Iniciando conexión a {self.host}:{self.port}",
        )
        logging.info(
            "Cliente %d: iniciando conexión a %s:%s [T=%d]",
            self.client_id,
            self.host,
            self.port,
            ts
        )
        
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            peer = writer.get_extra_info("peername")
            
            ts = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="CONNECTION_ESTABLISHED",
                lamport_timestamp=ts,
                description=f"Conectado al nodo en {peer}",
                metadata={"peer": str(peer)},
            )
            logging.info("Cliente %d: conectado [T=%d]", self.client_id, ts)

            # Recibir mensaje de bienvenida del nodo
            welcome, remote_ts = await receive_message_with_lamport(reader)
            if welcome:
                # Sincronizar reloj
                ts = self.lamport_clock.receive_message(remote_ts)
                self.event_logger.log_message_received(
                    lamport_timestamp=ts,
                    remote_lamport=remote_ts,
                    source_node=welcome.get("node_id"),
                    message_type="WELCOME",
                )
                logging.info(
                    "Cliente %d: bienvenida recibida [T_local=%d, T_remoto=%d]",
                    self.client_id,
                    ts,
                    remote_ts
                )

            # Enviar operaciones de prueba
            await self.send_operation(reader, writer, {
                "type": "PING",
                "data": f"Hello from client {self.client_id}",
                "timestamp": datetime.now().isoformat(),
            })

            await self.send_operation(reader, writer, {
                "type": "ECHO",
                "data": f"Mensaje de eco desde cliente {self.client_id}",
                "timestamp": datetime.now().isoformat(),
            })

            await self.send_operation(reader, writer, {
                "type": "INFO",
                "timestamp": datetime.now().isoformat(),
            })

        except ConnectionRefusedError:
            ts = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="CONNECTION_FAILED",
                lamport_timestamp=ts,
                description=f"No se pudo conectar a {self.host}:{self.port}",
                metadata={"host": self.host, "port": self.port},
            )
            logging.error(
                "Cliente %d: no se pudo conectar a %s:%s",
                self.client_id,
                self.host,
                self.port
            )
        except Exception as error:
            ts = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="CONNECTION_ERROR",
                lamport_timestamp=ts,
                description=f"Error durante la conexión: {error}",
            )
            logging.exception("Cliente %d: error durante la conexión", self.client_id)
        finally:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
            
            ts = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="CONNECTION_CLOSED",
                lamport_timestamp=ts,
                description="Desconectado del nodo",
            )
            logging.info("Cliente %d: desconectado [T=%d]", self.client_id, ts)

    async def send_operation(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        operation: dict,
    ) -> None:
        """Envía una operación al nodo y espera la respuesta.

        """
        try:
            # Crear timestamp de Lamport para el envío
            ts_send = self.lamport_clock.send_message()
            
            logging.info(
                "Cliente %d: enviando operación %s [T=%d]",
                self.client_id,
                operation.get("type"),
                ts_send
            )
            
            await send_message_with_lamport(writer, operation, ts_send)
            
            self.event_logger.log_message_sent(
                lamport_timestamp=ts_send,
                target_node=None,
                message_type=operation.get("type", "UNKNOWN"),
            )

            # Recibir respuesta
            response, remote_ts = await receive_message_with_lamport(reader)
            if response:
                # Sincronizar reloj con respuesta
                ts_recv = self.lamport_clock.receive_message(remote_ts)
                
                self.event_logger.log_message_received(
                    lamport_timestamp=ts_recv,
                    remote_lamport=remote_ts,
                    source_node=response.get("node_id"),
                    message_type=response.get("type", "UNKNOWN"),
                )
                
                logging.info(
                    "Cliente %d: respuesta recibida: %s [T_local=%d, T_remoto=%d]",
                    self.client_id,
                    response.get("type"),
                    ts_recv,
                    remote_ts
                )
            else:
                logging.warning("Cliente %d: nodo cerró la conexión sin respuesta", self.client_id)

        except Exception as error:
            ts = self.lamport_clock.event()
            self.event_logger.log_event(
                event_type="OPERATION_ERROR",
                lamport_timestamp=ts,
                description=f"Error enviando operación: {error}",
            )
            logging.error("Cliente %d: error enviando operación: %s", self.client_id, error)