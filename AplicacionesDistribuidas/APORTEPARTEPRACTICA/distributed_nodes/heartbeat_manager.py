"""Gestor de heartbeats para detección de nodos caídos.


"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from distributed_nodes.node_registry import NodeRegistry


class HeartbeatManager:
    """Gestor de heartbeats con envío periódico y monitoreo.
    
    Características:
    - Envío periódico de heartbeats a nodos conocidos
    - Recepción y registro de heartbeats
    - Detección de timeouts automática
    - Logging de eventos de salud
    """
    
    def __init__(
        self,
        local_node_id: int,
        registry: NodeRegistry,
        heartbeat_interval: float = 2.0,
        heartbeat_timeout: float = 6.0,
        event_logger: Optional[object] = None,
    ) -> None:
        """Inicializa el gestor de heartbeats.
        
        Args:
            local_node_id: ID del nodo local.
            registry: Registro de nodos (NodeRegistry).
            heartbeat_interval: Intervalo de envío en segundos (default: 2s).
            heartbeat_timeout: Timeout de detección en segundos (default: 6s).
            event_logger: Logger de eventos para Lamport (opcional).
        """
        if heartbeat_interval <= 0:
            raise ValueError("heartbeat_interval debe ser > 0")
        if heartbeat_timeout <= 0:
            raise ValueError("heartbeat_timeout debe ser > 0")
        if heartbeat_timeout <= heartbeat_interval:
            logging.warning(
                "heartbeat_timeout (%s) <= heartbeat_interval (%s). "
                "Considere aumentar timeout.",
                heartbeat_timeout,
                heartbeat_interval
            )
        
        self.local_node_id = local_node_id
        self.registry = registry
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.event_logger = event_logger
        
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        
        self._heartbeats_sent = 0
        self._heartbeats_received = 0
        
        logging.info(
            "HeartbeatManager inicializado: "
            "intervalo=%.1fs, timeout=%.1fs",
            self.heartbeat_interval,
            self.heartbeat_timeout
        )
    
    def create_heartbeat_message(self) -> dict:
        """Crea un mensaje de heartbeat.
        
        Returns:
            Diccionario con datos del heartbeat.
        """
        return {
            "type": "HEARTBEAT",
            "node_id": self.local_node_id,
            "timestamp": datetime.now().isoformat(),
            "alive": True,
        }
    
    def is_heartbeat(self, message: dict) -> bool:
        """Verifica si un mensaje es un heartbeat.
        
        Args:
            message: Diccionario del mensaje.
            
        Returns:
            True si es un heartbeat, False en caso contrario.
        """
        return message.get("type") == "HEARTBEAT"
    
    def handle_heartbeat(
        self,
        message: dict,
        lamport_ts: int,
        source_node_id: Optional[int] = None,
    ) -> bool:
        """Procesa un heartbeat recibido.
        
        Args:
            message: Mensaje de heartbeat.
            lamport_ts: Timestamp de Lamport (para logging).
            source_node_id: ID del nodo que envió el heartbeat.
                           Si es None, se extrae del mensaje.
        
        Returns:
            True si fue procesado, False si hay error.
        """
        try:
            # Extraer información del heartbeat
            if source_node_id is None:
                source_node_id = message.get("node_id")
            
            if source_node_id is None:
                logging.warning("Heartbeat sin identificador de nodo")
                return False
            
            # Actualizar registro
            node_info = self.registry.get_node(source_node_id)
            if node_info is None:
                logging.debug(
                    "Heartbeat de nodo desconocido: %d",
                    source_node_id
                )
                return False
            
            # Registrar heartbeat
            self.registry.update_heartbeat(source_node_id)
            
            with self._lock:
                self._heartbeats_received += 1
            
            # Registrar evento en logger de Lamport
            if self.event_logger:
                self.event_logger.log_event(
                    event_type="HEARTBEAT_RECEIVED",
                    lamport_timestamp=lamport_ts,
                    description=f"Heartbeat de nodo {source_node_id}",
                    metadata={
                        "source_node_id": source_node_id,
                        "heartbeat_count": node_info.heartbeat_count,
                    }
                )
            
            logging.debug(
                "Heartbeat recibido de nodo %d [total=%d]",
                source_node_id,
                node_info.heartbeat_count
            )
            
            return True
            
        except Exception as error:
            logging.error("Error procesando heartbeat: %s", error)
            return False
    
    async def send_heartbeat_to_node(
        self,
        host: str,
        port: int,
        node_id: int,
    ) -> bool:
        """Envía un heartbeat a un nodo específico.
        
        Args:
            host: Host del nodo destino.
            port: Puerto del nodo destino.
            node_id: ID del nodo destino.
        
        Returns:
            True si fue enviado, False si hay error.
        """
        try:
            # Conectar al nodo remoto
            reader, writer = await asyncio.open_connection(host, port)
            
            # Crear mensaje de heartbeat
            from distributed_nodes.lamport_framing import send_message_with_lamport
            
            heartbeat_msg = self.create_heartbeat_message()
            
            # Usar timestamp actual (no sincronizado)
            await send_message_with_lamport(
                writer,
                heartbeat_msg,
                0  # El nodo remoto ignorará el timestamp para heartbeats
            )
            
            with self._lock:
                self._heartbeats_sent += 1
            
            logging.debug(
                "Heartbeat enviado a nodo %d (%s:%d) [total=%d]",
                node_id,
                host,
                port,
                self._heartbeats_sent
            )
            
            # Registrar evento si tenemos logger
            if self.event_logger:
                self.event_logger.log_event(
                    event_type="HEARTBEAT_SENT",
                    lamport_timestamp=0,
                    description=f"Heartbeat enviado a nodo {node_id}",
                    metadata={
                        "target_node_id": node_id,
                        "target_host": host,
                        "target_port": port,
                    }
                )
            
            writer.close()
            await writer.wait_closed()
            return True
            
        except ConnectionRefusedError:
            logging.debug(
                "No se pudo conectar a nodo %d (%s:%d)",
                node_id,
                host,
                port
            )
            return False
        except Exception as error:
            logging.debug(
                "Error enviando heartbeat a nodo %d: %s",
                node_id,
                error
            )
            return False
    
    def _heartbeat_sender_loop(self) -> None:
        """Loop principal para envío de heartbeats (ejecutado en hilo)."""
        logging.info("Iniciando loop de envío de heartbeats")
        
        while self._running:
            try:
                # Obtener lista de nodos activos
                nodes = self.registry.get_all_nodes()
                
                if not nodes:
                    logging.debug("No hay nodos para enviar heartbeats")
                    time.sleep(self.heartbeat_interval)
                    continue
                
                # Enviar heartbeats de forma asincrónica
                async def send_all():
                    tasks = [
                        self.send_heartbeat_to_node(n.host, n.port, n.node_id)
                        for n in nodes
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                asyncio.run(send_all())
                
                # Esperar antes del siguiente ciclo
                time.sleep(self.heartbeat_interval)
                
            except Exception as error:
                logging.error(
                    "Error en loop de envío de heartbeats: %s",
                    error
                )
                time.sleep(self.heartbeat_interval)
    
    def _health_monitor_loop(self) -> None:
        """Loop principal para monitoreo de salud (ejecutado en hilo)."""
        logging.info("Iniciando loop de monitoreo de salud")
        
        while self._running:
            try:
                # Verificar salud de todos los nodos
                self.registry.check_all_nodes_health(self.heartbeat_timeout)
                
                # Detectar cambios de estado
                self._detect_state_changes()
                
                # Esperar antes del siguiente chequeo
                time.sleep(self.heartbeat_interval)
                
            except Exception as error:
                logging.error(
                    "Error en loop de monitoreo de salud: %s",
                    error
                )
                time.sleep(self.heartbeat_interval)
    
    def _detect_state_changes(self) -> None:
        """Detecta cambios de estado de nodos (mejora con tracking)."""
        # Esta función puede extenderse para detectar transiciones
        # de estado más sofisticadas
        pass
    
    def start(self) -> None:
        """Inicia los hilos de heartbeat y monitoreo."""
        with self._lock:
            if self._running:
                logging.warning("HeartbeatManager ya está corriendo")
                return
            
            self._running = True
        
        # Crear hilos daemon
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_sender_loop,
            daemon=True,
            name=f"HeartbeatSender-{self.local_node_id}"
        )
        
        self._monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True,
            name=f"HealthMonitor-{self.local_node_id}"
        )
        
        # Iniciar hilos
        self._heartbeat_thread.start()
        self._monitor_thread.start()
        
        logging.info(
            "HeartbeatManager iniciado: "
            "sender_thread=%s, monitor_thread=%s",
            self._heartbeat_thread.name,
            self._monitor_thread.name
        )
    
    def stop(self) -> None:
        """Detiene los hilos de heartbeat y monitoreo."""
        with self._lock:
            if not self._running:
                logging.warning("HeartbeatManager no está corriendo")
                return
            
            self._running = False
        
        # Esperar a que terminen los hilos
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=2)
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)
        
        logging.info("HeartbeatManager detenido")
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del heartbeat.
        
        Returns:
            Diccionario con estadísticas.
        """
        with self._lock:
            return {
                "heartbeats_sent": self._heartbeats_sent,
                "heartbeats_received": self._heartbeats_received,
                "is_running": self._running,
            }
    
    def print_stats(self) -> None:
        """Imprime estadísticas del heartbeat."""
        stats = self.get_stats()
        registry_stats = self.registry.get_stats()
        
        print(f"\n{'='*80}")
        print(f"Estadísticas de Heartbeat (Nodo {self.local_node_id})")
        print(f"{'='*80}\n")
        
        print(f"Estado: {'CORRIENDO' if stats['is_running'] else 'DETENIDO'}")
        print(f"Heartbeats enviados: {stats['heartbeats_sent']}")
        print(f"Heartbeats recibidos: {stats['heartbeats_received']}")
        print(f"Intervalo de envío: {self.heartbeat_interval}s")
        print(f"Timeout de detección: {self.heartbeat_timeout}s")
        
        print(f"\nRegistro de Nodos:")
        print(f"  Total: {registry_stats['total_nodes']}")
        print(f"  Vivos: {registry_stats['alive_nodes']}")
        print(f"  Caídos: {registry_stats['dead_nodes']}")
        print(f"  Total de heartbeats recibidos: {registry_stats['total_heartbeats_received']}")
        
        print(f"\n{'='*80}\n")
    
    def __repr__(self) -> str:
        return (
            f"HeartbeatManager(node_id={self.local_node_id}, "
            f"interval={self.heartbeat_interval}s, "
            f"timeout={self.heartbeat_timeout}s, "
            f"running={self._running})"
        )
