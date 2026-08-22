"""Implementación de Relojes Lógicos de Lamport.

Sistema de sincronización causal que garantiza orden total consistente
en eventos distribuidos sin depender de relojes físicos.
"""

import logging
from threading import Lock
from typing import Optional


class LamportClock:
    """Reloj lógico de Lamport para sincronización causal en sistemas distribuidos.

    """

    def __init__(self, node_id: int) -> None:
        """Inicializa el reloj de Lamport.

        """
        if not isinstance(node_id, int) or node_id < 0:
            raise ValueError("node_id debe ser un entero no negativo")
        
        self.node_id = node_id
        self.clock_value = 0
        self._lock = Lock()
        
        logging.info("Reloj de Lamport inicializado: node_id=%d, clock=0", self.node_id)

    def event(self) -> int:
        """Procesa un evento local e incrementa el reloj.
        """
        with self._lock:
            self.clock_value += 1
            logging.debug(
                "Evento local en nodo %d: reloj=%d",
                self.node_id,
                self.clock_value
            )
            return self.clock_value

    def send_message(self) -> int:
        """Obtiene el timestamp de Lamport para un mensaje saliente.
        """
        with self._lock:
            self.clock_value += 1
            timestamp = self.clock_value
            logging.debug(
                "Mensaje enviado desde nodo %d: timestamp_lamport=%d",
                self.node_id,
                timestamp
            )
            return timestamp

    def receive_message(self, remote_timestamp: int) -> int:
        """Procesa la recepción de un mensaje de otro nodo.
        """
        if remote_timestamp < 0:
            raise ValueError("remote_timestamp debe ser no negativo")
        
        with self._lock:
            self.clock_value = max(self.clock_value, remote_timestamp) + 1
            logging.debug(
                "Mensaje recibido en nodo %d: "
                "remote_timestamp=%d, nuevo_clock=%d",
                self.node_id,
                remote_timestamp,
                self.clock_value
            )
            return self.clock_value

    def get_current(self) -> int:
        with self._lock:
            return self.clock_value
    def get_timestamp_tuple(self) -> tuple: 
        with self._lock:
            return (self.clock_value, self.node_id)
    def __str__(self) -> str:
        return f"LamportClock(node_id={self.node_id}, clock={self.clock_value})"
    def __repr__(self) -> str:
        return self.__str__()
