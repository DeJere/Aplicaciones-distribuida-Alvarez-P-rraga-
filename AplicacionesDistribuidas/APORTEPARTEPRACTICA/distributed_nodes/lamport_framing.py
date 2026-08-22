import asyncio
import json
import logging
from typing import Any, Dict

from distributed_nodes.framing import LENGTH_HEADER_SIZE


async def send_message_with_lamport(
    writer: asyncio.StreamWriter,
    message: Dict[str, Any],
    lamport_timestamp: int,
) -> None:
    """Envía un mensaje JSON con prefijo de longitud y timestamp de Lamport.
    """
    # Envolver el mensaje con timestamp de Lamport
    wrapped_message = {
        "lamport_timestamp": lamport_timestamp,
        "payload": message,
    }

    # Serializar a JSON
    json_payload = json.dumps(wrapped_message, ensure_ascii=False).encode("utf-8")
    payload_length = len(json_payload)

    # Crear prefijo de longitud (4 bytes, big-endian)
    length_header = payload_length.to_bytes(LENGTH_HEADER_SIZE, byteorder="big")

    # Enviar prefijo + payload
    writer.write(length_header + json_payload)
    await writer.drain()

    logging.debug(
        "Mensaje enviado con Lamport: timestamp=%d, payload=%s",
        lamport_timestamp,
        message.get("type", "UNKNOWN"),
    )


async def receive_message_with_lamport(
    reader: asyncio.StreamReader,
) -> tuple[Dict[str, Any], int] | tuple[None, None]:
    """Recibe un mensaje JSON con timestamp de Lamport.
    """
    # Leer prefijo de 4 bytes
    length_header = await reader.readexactly(LENGTH_HEADER_SIZE)
    if not length_header:
        logging.debug("Conexión cerrada: sin bytes de longitud")
        return None, None

    # Convertir prefijo a entero
    payload_length = int.from_bytes(length_header, byteorder="big")

    if payload_length <= 0:
        raise ValueError(f"Longitud inválida: {payload_length}")

    # Leer exactamente payload_length bytes
    json_payload = await reader.readexactly(payload_length)

    # Deserializar JSON
    wrapped_message = json.loads(json_payload.decode("utf-8"))

    # Extraer campos
    lamport_timestamp = wrapped_message.get("lamport_timestamp")
    payload = wrapped_message.get("payload")

    if lamport_timestamp is None or payload is None:
        raise ValueError(
            "Mensaje incompleto: faltan 'lamport_timestamp' o 'payload'"
        )

    logging.debug(
        "Mensaje recibido con Lamport: timestamp=%d, tipo=%s",
        lamport_timestamp,
        payload.get("type", "UNKNOWN"),
    )

    return payload, lamport_timestamp
