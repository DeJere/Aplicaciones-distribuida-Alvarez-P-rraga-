"""Registro de eventos con orden total consistente usando Lamport Clocks.

"""

import json
import logging
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


class EventLogger:
    """Registra eventos distribuidos con orden total usando Lamport Clocks.

    """

    def __init__(self, node_id: int, log_file: Optional[Path] = None) -> None:
        """Inicializa el registrador de eventos.

        """
        self.node_id = node_id
        
        if log_file is None:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"node_{node_id}.json"
        
        self.log_file = Path(log_file)
        self.events: List[Dict[str, Any]] = []
        self._lock = Lock()
        
        # Intentar cargar eventos previos si el archivo existe
        self._load_existing_events()
        
        logging.info(
            "EventLogger inicializado: node_id=%d, log_file=%s",
            self.node_id,
            self.log_file
        )

    def _load_existing_events(self) -> None:
        """Carga eventos existentes del archivo JSON."""
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    self.events = json.load(f)
                logging.info(
                    "Cargados %d eventos previos del archivo %s",
                    len(self.events),
                    self.log_file
                )
            except Exception as e:
                logging.warning(
                    "No se pudieron cargar eventos previos: %s",
                    e
                )

    def log_event(
        self,
        event_type: str,
        lamport_timestamp: int,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Registra un evento con su timestamp de Lamport.
   
        """
        with self._lock:
            event = {
                "sequence": len(self.events) + 1,
                "node_id": self.node_id,
                "event_type": event_type,
                "lamport_timestamp": lamport_timestamp,
                "wall_clock_time": datetime.now().isoformat(),
                "description": description,
                "metadata": metadata or {},
            }
            
            self.events.append(event)
            
            logging.debug(
                "Evento registrado: type=%s, lamport=%d, node=%d",
                event_type,
                lamport_timestamp,
                self.node_id
            )
            
            # Guardar en archivo
            self._save_events()
            
            return event

    def log_message_sent(
        self,
        lamport_timestamp: int,
        target_node: Optional[int] = None,
        message_type: str = "UNKNOWN",
        message_size: int = 0,
    ) -> Dict[str, Any]:
        """Registra el envío de un mensaje.
 
        """
        metadata = {
            "target_node": target_node,
            "message_type": message_type,
            "message_size": message_size,
        }
        
        return self.log_event(
            event_type="MESSAGE_SENT",
            lamport_timestamp=lamport_timestamp,
            description=f"Envió {message_type} a nodo {target_node}",
            metadata=metadata,
        )

    def log_message_received(
        self,
        lamport_timestamp: int,
        remote_lamport: int,
        source_node: Optional[int] = None,
        message_type: str = "UNKNOWN",
        message_size: int = 0,
    ) -> Dict[str, Any]:
        """Registra la recepción de un mensaje.

        """
        metadata = {
            "source_node": source_node,
            "remote_lamport_timestamp": remote_lamport,
            "message_type": message_type,
            "message_size": message_size,
        }
        
        return self.log_event(
            event_type="MESSAGE_RECEIVED",
            lamport_timestamp=lamport_timestamp,
            description=f"Recibió {message_type} de nodo {source_node} "
                       f"(remote_lamport={remote_lamport})",
            metadata=metadata,
        )

    def log_operation_processed(
        self,
        lamport_timestamp: int,
        operation_type: str,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Registra el procesamiento de una operación.

        """
        metadata = {
            "operation_type": operation_type,
            "client_id": client_id,
        }
        
        return self.log_event(
            event_type="OPERATION_PROCESSED",
            lamport_timestamp=lamport_timestamp,
            description=f"Procesó operación {operation_type} del cliente {client_id}",
            metadata=metadata,
        )

    def get_events_ordered(self) -> List[Dict[str, Any]]:
        """Obtiene todos los eventos ordenados por Lamport Timestamp + Node ID.

        """
        with self._lock:
            # Ordenar por (lamport_timestamp, node_id)
            sorted_events = sorted(
                self.events,
                key=lambda e: (e["lamport_timestamp"], e["node_id"])
            )
            return sorted_events

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Obtiene eventos de un tipo específico, ordenados por Lamport.
        """
        with self._lock:
            filtered = [e for e in self.events if e["event_type"] == event_type]
            return sorted(
                filtered,
                key=lambda e: (e["lamport_timestamp"], e["node_id"])
            )

    def get_events_in_range(
        self,
        start_lamport: int,
        end_lamport: int,
    ) -> List[Dict[str, Any]]:
        """Obtiene eventos dentro de un rango de timestamps de Lamport.

        """
        with self._lock:
            filtered = [
                e for e in self.events
                if start_lamport <= e["lamport_timestamp"] <= end_lamport
            ]
            return sorted(
                filtered,
                key=lambda e: (e["lamport_timestamp"], e["node_id"])
            )

    def _save_events(self) -> None:
        """Guarda los eventos en el archivo JSON."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error("Error guardando eventos en %s: %s", self.log_file, e)

    def print_events_summary(self) -> None:
        """Imprime un resumen de los eventos en orden de Lamport."""
        ordered = self.get_events_ordered()
        
        print(f"\n{'='*80}")
        print(f"Resumen de Eventos - Nodo {self.node_id}")
        print(f"Total de eventos: {len(ordered)}")
        print(f"{'='*80}")
        
        for event in ordered:
            print(
                f"[{event['sequence']:3d}] "
                f"T={event['lamport_timestamp']:4d}:N{event['node_id']} "
                f"{event['event_type']:20s} {event['description']}"
            )
        
        print(f"{'='*80}\n")

    def export_json(self, filepath: Optional[Path] = None) -> str:
        """Exporta los eventos como JSON en orden de Lamport.
        """
        ordered = self.get_events_ordered()
        json_str = json.dumps(ordered, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
            return str(filepath)
        
        return json_str

    def __len__(self) -> int:
        """Retorna el número total de eventos registrados."""
        return len(self.events)

    def __repr__(self) -> str:
        return (
            f"EventLogger(node_id={self.node_id}, "
            f"events={len(self.events)}, "
            f"log_file={self.log_file})"
        )
