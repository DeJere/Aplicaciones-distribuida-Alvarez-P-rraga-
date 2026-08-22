"""Protocolo de framing basado en longitud previa para mensajes JSON.
"""

import asyncio
import json
import logging
from typing import Any, Dict

# Tamaño del prefijo de longitud en bytes
LENGTH_HEADER_SIZE = 4


async def send_message(writer: asyncio.StreamWriter, message: Dict[str, Any]) -> None:
    """Envía un mensaje JSON con prefijo de longitud.

    """
    # Serializar mensaje a JSON y convertir a bytes
    json_payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    payload_length = len(json_payload)

    # Crear prefijo de 4 bytes (big-endian) con la longitud
    length_header = payload_length.to_bytes(LENGTH_HEADER_SIZE, byteorder="big")

    # Enviar prefijo + payload
    writer.write(length_header + json_payload)
    await writer.drain()

    logging.debug(
        "Mensaje enviado: longitud=%d bytes, contenido=%s",
        payload_length,
        message,
    )


async def receive_message(reader: asyncio.StreamReader) -> Dict[str, Any] | None:
    """Recibe un mensaje JSON precedido por su longitud.
    """
    # Leer prefijo de 4 bytes
    length_header = await reader.readexactly(LENGTH_HEADER_SIZE)
    if not length_header:
        logging.debug("Conexión cerrada: no se recibieron bytes de longitud")
        return None

    # Convertir prefijo a entero (big-endian)
    payload_length = int.from_bytes(length_header, byteorder="big")

    if payload_length <= 0:
        raise ValueError(f"Longitud inválida del mensaje: {payload_length}")

    # Leer exactamente la cantidad de bytes indicada
    json_payload = await reader.readexactly(payload_length)

    # Deserializar JSON
    message = json.loads(json_payload.decode("utf-8"))

    logging.debug(
        "Mensaje recibido: longitud=%d bytes, contenido=%s",
        payload_length,
        message,
    )

    return message
