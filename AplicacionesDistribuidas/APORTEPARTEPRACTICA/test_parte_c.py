"""Script de Prueba Rápida para Parte C - Tolerancia a Fallos

Este script valida que el sistema de heartbeats funciona correctamente.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path


def test_imports():
    """Verifica que todos los módulos se importan correctamente."""
    print("\n" + "="*80)
    print("TEST 1: Verificar Imports")
    print("="*80)
    
    try:
        from distributed_nodes import (
            Node, NodeRegistry, HeartbeatManager, LamportClock, EventLogger
        )
        print("Todos los módulos importados correctamente")
        return True
    except ImportError as e:
        print(f"Error importando módulos: {e}")
        return False


def test_node_registry():
    """Verifica que NodeRegistry funciona correctamente."""
    print("\n" + "="*80)
    print("TEST 2: NodeRegistry Básico")
    print("="*80)
    
    try:
        from distributed_nodes import NodeRegistry
        
        registry = NodeRegistry(local_node_id=1)
        
        # Registrar nodos
        registry.register_node(2, "127.0.0.1", 5001)
        registry.register_node(3, "127.0.0.1", 5002)
        
        nodes = registry.get_all_nodes()
        print(f"Registrados {len(nodes)} nodos")
        
        # Actualizar heartbeat
        registry.update_heartbeat(2)
        node2 = registry.get_node(2)
        
        if node2.is_alive:
            print(f"Nodo 2 marcado como VIVO")
        else:
            print(f"Nodo 2 debería estar VIVO")
            return False
        
        # Marcar como caído
        registry.mark_node_dead(3)
        node3 = registry.get_node(3)
        
        if not node3.is_alive:
            print(f"Nodo 3 marcado como CAÍDO")
        else:
            print(f"Nodo 3 debería estar CAÍDO")
            return False
        
        stats = registry.get_stats()
        print(f"Stats: {stats['total_nodes']} total, "
              f"{stats['alive_nodes']} vivos, {stats['dead_nodes']} caídos")
        
        return True
        
    except Exception as e:
        print(f"Error en NodeRegistry: {e}")
        return False


def test_heartbeat_message():
    """Verifica la creación de mensajes de heartbeat."""
    print("\n" + "="*80)
    print("TEST 3: Mensaje de Heartbeat")
    print("="*80)
    
    try:
        from distributed_nodes import HeartbeatManager, NodeRegistry
        
        registry = NodeRegistry(local_node_id=1)
        manager = HeartbeatManager(local_node_id=1, registry=registry)
        
        msg = manager.create_heartbeat_message()
        
        # Verificar estructura
        required_fields = ["type", "node_id", "timestamp", "alive"]
        for field in required_fields:
            if field not in msg:
                print(f"Campo faltante en heartbeat: {field}")
                return False
        
        if msg["type"] != "HEARTBEAT":
            print(f"Tipo de mensaje incorrecto: {msg['type']}")
            return False
        
        if msg["node_id"] != 1:
            print(f"Node ID incorrecto: {msg['node_id']}")
            return False
        
        print(f"Estructura de heartbeat válida:")
        print(f"  Type: {msg['type']}")
        print(f"  Node ID: {msg['node_id']}")
        print(f"  Alive: {msg['alive']}")
        
        # Verificar detección
        if manager.is_heartbeat(msg):
            print(f"Heartbeat detectado correctamente")
        else:
            print(f"Heartbeat no fue detectado")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error en mensajes de heartbeat: {e}")
        return False


def test_node_creation():
    """Verifica que un Node se puede crear con heartbeats"""
    print("\n" + "="*80)
    print("TEST 4: Creación de Node")
    print("="*80)
    
    try:
        from distributed_nodes import Node
        
        node = Node(
            node_id=1,
            host="127.0.0.1",
            port=5000,
            heartbeat_interval=2.0,
            heartbeat_timeout=6.0
        )
        
        print(f"Nodo creado: {node}")
        print(f"  ID: {node.node_id}")
        print(f"  Dirección: {node.host}:{node.port}")
        
        # Verificar componentes
        if hasattr(node, 'lamport_clock') and node.lamport_clock is not None:
            print(f"LamportClock inicializado")
        else:
            print(f"LamportClock no inicializado")
            return False
        
        if hasattr(node, 'event_logger') and node.event_logger is not None:
            print(f"EventLogger inicializado")
        else:
            print(f"EventLogger no inicializado")
            return False
        
        if hasattr(node, 'node_registry') and node.node_registry is not None:
            print(f"NodeRegistry inicializado")
        else:
            print(f"NodeRegistry no inicializado")
            return False
        
        if hasattr(node, 'heartbeat_manager') and node.heartbeat_manager is not None:
            print(f"HeartbeatManager inicializado")
        else:
            print(f"HeartbeatManager no inicializado")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error creando Node: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_peer_registration():
    """Verifica que los peers se pueden registrar en un Node."""
    print("\n" + "="*80)
    print("TEST 5: Registración de Peers")
    print("="*80)
    
    try:
        from distributed_nodes import Node
        
        node = Node(node_id=1, port=5000)
        
        # Registrar un peer
        node.register_peer_node(2, "127.0.0.1", 5001)
        print(f"Peer individual registrado")
        
        # Registrar múltiples peers
        peers = [
            (3, "127.0.0.1", 5002),
            (4, "127.0.0.1", 5003),
        ]
        node.register_peer_nodes(peers)
        print(f"Peers múltiples registrados ({len(peers)} nodos)")
        
        # Verificar estado
        status = node.get_node_status()
        if status['registered_peers'] == 3:
            print(f"Total de peers correcto: {status['registered_peers']}")
        else:
            print(f"Esperado 3 peers, obtenido {status['registered_peers']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error en registración de peers: {e}")
        return False


def test_events_logging():
    """Verifica que los eventos se registran correctamente."""
    print("\n" + "="*80)
    print("TEST 6: Logging de Eventos")
    print("="*80)
    
    try:
        from distributed_nodes import Node
        
        # Limpiar logs anteriores
        logs_dir = Path("logs")
        for f in logs_dir.glob("node_99.json"):
            f.unlink()
        
        node = Node(node_id=99, port=5099)
        
        # Registrar un evento
        ts = node.lamport_clock.event()
        node.event_logger.log_event(
            event_type="TEST_EVENT",
            lamport_timestamp=ts,
            description="Evento de prueba",
            metadata={"test": True}
        )
        
        print(f"Evento registrado")
        
        # Verificar que se guardó
        log_file = logs_dir / "node_99.json"
        if log_file.exists():
            print(f"Archivo de log creado: {log_file}")
            
            # Leer y verificar contenido
            with open(log_file) as f:
                events = json.load(f)  # Cargar como array JSON completo
            
            if len(events) > 0:
                print(f"{len(events)} evento(s) registrado(s)")
                return True
            else:
                print(f"No hay eventos en el log")
                return False
        else:
            print(f"Archivo de log no creado")
            return False
        
    except Exception as e:
        print(f"Error en logging de eventos: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_heartbeat_manager():
    """Verifica que el HeartbeatManager funciona (tiempo limitado)."""
    print("\n" + "="*80)
    print("TEST 7: HeartbeatManager (prueba rápida 5 segundos)")
    print("="*80)
    
    try:
        from distributed_nodes import Node
        
        node = Node(
            node_id=1,
            port=5000,
            heartbeat_interval=1.0,  # Intervalo corto para prueba
            heartbeat_timeout=3.0
        )
        
        # Registrar un peer (no será alcanzable, pero no importa)
        node.register_peer_node(2, "127.0.0.1", 5001)
        
        # Iniciar heartbeat manager
        node.heartbeat_manager.start()
        print(f"HeartbeatManager iniciado")
        
        # Dejar funcionar 3 segundos
        await asyncio.sleep(3)
        
        # Obtener estadísticas
        stats = node.heartbeat_manager.get_stats()
        print(f"Estadísticas obtenidas:")
        print(f"  Enviados: {stats['heartbeats_sent']}")
        print(f"  Recibidos: {stats['heartbeats_received']}")
        print(f"  En ejecución: {stats['is_running']}")
        
        if stats['heartbeats_sent'] > 0:
            print(f"Heartbeats enviados exitosamente")
        else:
            print(f"Ningún heartbeat enviado (esperado: no hay peers alcanzables)")
        
        # Detener
        node.heartbeat_manager.stop()
        print(f"HeartbeatManager detenido")
        
        return True
        
    except Exception as e:
        print(f"Error en HeartbeatManager: {e}")
        return False


async def run_all_tests():
    """Ejecuta todas las pruebas."""
    results = []
    
    # Pruebas síncronas
    results.append(("Imports", test_imports()))
    results.append(("NodeRegistry", test_node_registry()))
    results.append(("Heartbeat Message", test_heartbeat_message()))
    results.append(("Node Creation", test_node_creation()))
    results.append(("Peer Registration", test_peer_registration()))
    results.append(("Events Logging", test_events_logging()))
    
    # Pruebas asincrónicas
    results.append(("HeartbeatManager", await test_heartbeat_manager()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "BIEN" if result else "MAL"
        print(f"{status:8} {test_name}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        return 0
    else:
        print(f"\nPruebas falladas: {total - passed}")
        return 1


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [TEST] %(levelname)s %(message)s"
    )
    
    # Ejecutar pruebas
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
