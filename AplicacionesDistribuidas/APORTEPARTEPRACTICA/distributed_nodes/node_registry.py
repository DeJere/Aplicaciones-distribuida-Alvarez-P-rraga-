"""Registro de nodos en la red con monitoreo de estado.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, List, Optional, Tuple


@dataclass
class NodeInfo:
    
    node_id: int
    host: str
    port: int
    is_alive: bool = True
    last_heartbeat_time: Optional[datetime] = None
    heartbeat_count: int = 0
    missed_heartbeats: int = 0
    
    def update_heartbeat(self) -> None:
        self.last_heartbeat_time = datetime.now()
        self.heartbeat_count += 1
        self.missed_heartbeats = 0  # Resetear contador de fallas
        self.is_alive = True
    
    def mark_as_dead(self) -> None:
        self.is_alive = False
        self.missed_heartbeats += 1
    
    def mark_as_alive(self) -> None:
        self.is_alive = True
        self.missed_heartbeats = 0
    
    def get_time_since_heartbeat(self) -> Optional[timedelta]:
        if self.last_heartbeat_time is None:
            return None
        return datetime.now() - self.last_heartbeat_time
    
    def get_address(self) -> Tuple[str, int]:
        return (self.host, self.port)
    
    def __repr__(self) -> str:
        status = "ALIVE" if self.is_alive else "DEAD"
        return (
            f"NodeInfo(id={self.node_id}, addr={self.host}:{self.port}, "
            f"status={status}, heartbeats={self.heartbeat_count}, "
            f"missed={self.missed_heartbeats})"
        )


class NodeRegistry:
    """Registro centralizado de nodos en la red con monitoreo de estado.
    """
    
    def __init__(self, local_node_id: int) -> None:
        self.local_node_id = local_node_id
        self.nodes: Dict[int, NodeInfo] = {}
        self._lock = Lock()
        
        logging.info(
            "NodeRegistry inicializado para nodo %d",
            self.local_node_id
        )
    
    def register_node(self, node_id: int, host: str, port: int) -> None:
  
        if node_id == self.local_node_id:
            logging.warning(
                "Intento de registrar el nodo local (%d). Ignorado.",
                node_id
            )
            return
        
        with self._lock:
            if node_id in self.nodes:
                logging.warning(
                    "Nodo %d ya está registrado. Actualizando...",
                    node_id
                )
            
            node_info = NodeInfo(
                node_id=node_id,
                host=host,
                port=port,
                is_alive=True,
            )
            self.nodes[node_id] = node_info
            
            logging.info(
                "Nodo registrado: %s",
                node_info
            )
    
    def register_nodes(self, nodes: List[Tuple[int, str, int]]) -> None:
        for node_id, host, port in nodes:
            self.register_node(node_id, host, port)
    
    def get_node(self, node_id: int) -> Optional[NodeInfo]:
        with self._lock:
            return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[NodeInfo]:
        with self._lock:
            return list(self.nodes.values())
    
    def get_alive_nodes(self) -> List[NodeInfo]:
        with self._lock:
            return [n for n in self.nodes.values() if n.is_alive]
    
    def get_dead_nodes(self) -> List[NodeInfo]:
        with self._lock:
            return [n for n in self.nodes.values() if not n.is_alive]
    
    def update_heartbeat(self, node_id: int) -> bool:
     
        with self._lock:
            if node_id not in self.nodes:
                logging.warning(
                    "Heartbeat de nodo desconocido: %d",
                    node_id
                )
                return False
            
            node = self.nodes[node_id]
            was_dead = not node.is_alive
            node.update_heartbeat()
            
            if was_dead:
                logging.info(
                    "Nodo %d recuperado [heartbeats=%d]",
                    node_id,
                    node.heartbeat_count
                )
            else:
                logging.debug(
                    "Heartbeat de nodo %d recibido [total=%d]",
                    node_id,
                    node.heartbeat_count
                )
            
            return True
    
    def mark_node_dead(self, node_id: int) -> bool:
      
        with self._lock:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            was_alive = node.is_alive
            node.mark_as_dead()
            
            if was_alive:
                logging.warning(
                    "Nodo %d marcado como CAÍDO [missed=%d]",
                    node_id,
                    node.missed_heartbeats
                )
            
            return True
    
    def mark_node_alive(self, node_id: int) -> bool:
        
        with self._lock:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            was_dead = not node.is_alive
            node.mark_as_alive()
            
            if was_dead:
                logging.info(
                    "Nodo %d recuperado [estado=ALIVE]",
                    node_id
                )
            
            return True
    
    def check_node_health(
        self,
        node_id: int,
        timeout_seconds: float = 6.0,
    ) -> bool:
      
        with self._lock:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            
            # Si nunca se recibió heartbeat, asumir que está caído
            if node.last_heartbeat_time is None:
                if node.is_alive:
                    node.mark_as_dead()
                return False
            
            # Verificar timeout
            time_since_heartbeat = datetime.now() - node.last_heartbeat_time
            is_alive = time_since_heartbeat.total_seconds() < timeout_seconds
            
            if is_alive and not node.is_alive:
                # Recuperación
                node.mark_as_alive()
                logging.info("Nodo %d recuperado", node_id)
            elif not is_alive and node.is_alive:
                # Detección de caída
                node.mark_as_dead()
                logging.warning(
                    "Nodo %d timeout detectado (%.1f segundos sin heartbeat)",
                    node_id,
                    time_since_heartbeat.total_seconds()
                )
            
            return node.is_alive
    
    def check_all_nodes_health(self, timeout_seconds: float = 6.0) -> None:
       
        for node in self.get_all_nodes():
            self.check_node_health(node.node_id, timeout_seconds)
    
    def get_stats(self) -> Dict:
      
        with self._lock:
            total = len(self.nodes)
            alive = sum(1 for n in self.nodes.values() if n.is_alive)
            dead = total - alive
            total_heartbeats = sum(n.heartbeat_count for n in self.nodes.values())
            
            return {
                "total_nodes": total,
                "alive_nodes": alive,
                "dead_nodes": dead,
                "total_heartbeats_received": total_heartbeats,
            }
    
    def print_status(self) -> None:
        """Imprime el estado actual de todos los nodos."""
        with self._lock:
            print(f"\n{'='*80}")
            print(f"Estado del Registro de Nodos (Nodo Local: {self.local_node_id})")
            print(f"{'='*80}\n")
            
            if not self.nodes:
                print("No hay nodos registrados.\n")
                return
            
            for node in sorted(self.nodes.values(), key=lambda n: n.node_id):
                status = "✓ VIVO" if node.is_alive else "✗ CAÍDO"
                time_since = node.get_time_since_heartbeat()
                time_str = (
                    f"{time_since.total_seconds():.1f}s"
                    if time_since else "NUNCA"
                )
                
                print(
                    f"  Nodo {node.node_id}: {status:10s} | "
                    f"{node.host}:{node.port} | "
                    f"Heartbeats: {node.heartbeat_count} | "
                    f"Último: {time_str} | "
                    f"Fallos: {node.missed_heartbeats}"
                )
            
            print(f"\n{'='*80}\n")
    
    def __len__(self) -> int:
        """Retorna el número de nodos registrados."""
        return len(self.nodes)
    
    def __repr__(self) -> str:
        return (
            f"NodeRegistry(local_node={self.local_node_id}, "
            f"nodes={len(self.nodes)})"
        )
