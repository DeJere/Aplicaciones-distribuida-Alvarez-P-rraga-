# ANÁLISIS TEÓRICO

## 1. Propósito del proyecto

Este proyecto demuestra un sistema de registro distribuido simplificado donde un nodo central recibe operaciones de clientes y las ordena usando relojes de Lamport. La idea es ilustrar cómo se puede aplicar un orden lógico a eventos que llegan desde múltiples fuentes y cómo se puede proteger el acceso con autenticación básica.

## 2. Reloj de Lamport

El reloj de Lamport es una opción para ordenar eventos en un sistema distribuido cuando no existe un reloj global confiable. Cada nodo mantiene un contador local:

- `tick()` incrementa el contador antes de emitir o procesar un evento.
- `update(other)` actualiza el reloj usando el valor del mensaje recibido y su propio valor, garantizando que el nuevo tiempo sea mayor que ambos.

Este mecanismo satisface la propiedad de orden lógico: si un evento `a` ocurre antes que `b`, entonces `LC(a) < LC(b)`.

### Ventajas

- Sencillo de implementar.
- No requiere sincronización de tiempo real.
- Permite ordenar causalmente eventos relacionados.

### Limitaciones

- No da un orden total válido entre eventos concurrentes.
- No reemplaza un algoritmo de consenso cuando se requiere consistencia fuerte.

## 3. Enmarcado de mensajes (message framing)

La comunicación TCP es un flujo de bytes; no preserva los límites de mensaje. Para solucionar esto, el proyecto usa un prefijo de 4 bytes de longitud grande-endian antes del cuerpo JSON.

Esto permite que el receptor lea primero cuánto debe leer y luego procese exactamente esa cantidad de bytes.

## 4. Autenticación de tokens

La autenticación en este proyecto es simple y basada en tokens con un patrón fijo (`token-cliente-<n>`). El nodo comprueba que el token sea válido antes de procesar la operación.

### Riesgos y mejoras

- Un patrón predecible no es seguro en producción.
- En un sistema real se usaría un esquema criptográfico: firmas, JWT, TLS o certificados.
- Aquí la autenticación sirve para demostrar la separación entre cliente válido y cliente no autorizado.

## 5. Diseño del nodo

El nodo implementa un servidor TCP que:

- Escucha conexiones entrantes.
- Valida el token del cliente.
- Comprueba el tipo de mensaje.
- Incrementa el reloj de Lamport antes de aceptar una operación.
- Devuelve un `ACK` con el identificador del nodo, el reloj lógico y un detalle.

Este diseño también permite agregar más tipos de mensajes en el futuro, como `SYNC`, `ELECTION` o `QUERY`.

## 6. Cliente y demo

El cliente envía mensajes JSON enmarcados y recibe la respuesta del nodo. El `demo.py` levanta un nodo local y prueba dos casos:

1. Operación con token válido -> `ACK`.
2. Operación con token inválido -> `ERROR`.

Esto comprueba tanto la lógica de negocio como la autenticación y la integración de socket.

## 7. Consistencia y orden lógico

En un sistema distribuido completo, los relojes de Lamport permiten ordenar eventos cuando existe causalidad entre ellos. Sin embargo, dos eventos concurrentes pueden compartir un orden arbitrario según el reloj de Lamport.

Para lograr orden total con garantías fuertes se necesitaría un algoritmo de consenso como Paxos, Raft o un protocolo de transacción distribuida.

## 8. Extensiones posibles

- Soporte para múltiples nodos replicados.
- Persistencia de operaciones en disco o base de datos.
- Sincronización del estado entre nodos.
- Autenticación real con certificados o JWT.
- Manejo de fallos y particiones de red.

## 9. Conclusión

Este proyecto ofrece una base práctica para comprender las piezas clave de un registro distribuido:

- Reloj lógico (Lamport).
- Enmarcado de mensajes para TCP.
- Autenticación de cliente.
- Arquitectura cliente/servidor.

A partir de este diseño se puede evolucionar hacia un sistema distribuido más robusto y resiliente.
