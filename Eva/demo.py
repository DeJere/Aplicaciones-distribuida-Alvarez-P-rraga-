import subprocess
import sys
import time
import os
import socket

sys.path.insert(0, os.path.dirname(__file__))
from common.utils import encode_message, recv_message

CLUSTER = {
    1: ("127.0.0.1", 9001),
    2: ("127.0.0.1", 9002),
    3: ("127.0.0.1", 9003),
}

TOKEN_VALIDO   = "token-cliente-1"
TOKEN_INVALIDO = "token-falso"


def send(host, port, payload, timeout=4):
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.sendall(encode_message(payload))
        r = recv_message(s)
        s.close()
        return r
    except Exception as e:
        return {"error": str(e)}


def titulo(texto):
    print(f"\n{'═'*60}")
    print(f"  {texto}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    titulo("DEMO — RegistroDistribuido")

    # ── Levantar los 3 nodos ──────────────────────────────────
    titulo("1. Levantando los 3 nodos...")
    nodo_dir = os.path.join(os.path.dirname(__file__), "nodo")
    procs = {}
    for nid in [1, 2, 3]:
        p = subprocess.Popen(
            [sys.executable, "nodo.py", str(nid), str(9000 + nid)],
            cwd=nodo_dir,
        )
        procs[nid] = p
        print(f"  → N{nid} PID={p.pid}")

    print("  Esperando que arranquen (5 s)...")
    time.sleep(5)

    # ── Prueba de autenticación fallida ──────────────────────
    titulo("2. Prueba de SEGURIDAD — token inválido")
    r = send("127.0.0.1", 9001, {
        "type": "OPERACION", "token": TOKEN_INVALIDO,
        "operacion": "Operacion con token falso"
    })
    print(f"  Respuesta N1: {r}")

    # ── Envío de operaciones legítimas ───────────────────────
    titulo("3. Enviando operaciones con token válido")
    ops = [
        "CARGA: Paquete #001 recibido en bodega A",
        "DESPACHO: Paquete #002 enviado a destino",
        "INVENTARIO: Stock actualizado — 150 unidades",
        "CARGA: Paquete #003 recibido en bodega B",
        "ALERTA: Temperatura fuera de rango en zona C",
    ]
    for i, op in enumerate(ops):
        nid = (i % 3) + 1   # distribuir entre los 3 nodos
        r = send("127.0.0.1", 9000 + nid, {
            "type": "OPERACION", "token": TOKEN_VALIDO,
            "operacion": op
        })
        print(f"  Op→N{nid}: {r.get('detalle', r) if r else 'sin respuesta'}")
        time.sleep(0.3)

    time.sleep(1)

    # ── Simular caída del coordinador (N3) ───────────────────
    titulo("4. Simulando caída del COORDINADOR (N3)")
    procs[3].terminate()
    procs[3].wait()
    print("  N3 terminado. Esperando detección de fallo y nueva elección (8 s)...")
    time.sleep(8)

    # ── Enviar más operaciones sin el coordinador ─────────────
    titulo("5. Operaciones DESPUÉS de la caída de N3")
    for i, op in enumerate(["CARGA: Paquete #004 — post-fallo", "DESPACHO: Paquete #005 — post-fallo"]):
        nid = (i % 2) + 1   # solo N1 y N2
        r = send("127.0.0.1", 9000 + nid, {
            "type": "OPERACION", "token": TOKEN_VALIDO,
            "operacion": op
        })
        print(f"  Op→N{nid}: {r.get('detalle', r) if r else 'sin respuesta'}")
        time.sleep(0.3)

    # ── Fin ──────────────────────────────────────────────────
    titulo("6. Demo completada — revisa las consolas de los nodos")
    print("  El log de eventos con ORDEN TOTAL se muestra en cada nodo.")
    print("  Presiona Ctrl+C para terminar todos los procesos.\n")

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    finally:
        for nid, p in procs.items():
            try:
                p.terminate()
            except Exception:
                pass
        print("  Todos los nodos detenidos.")
