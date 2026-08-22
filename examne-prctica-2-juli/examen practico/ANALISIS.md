# Análisis técnico

## 1. Restricción REST más clara
La restricción de Uniform Interface se refleja en los recursos versionados como /api/v1/productos y /api/v1/pedidos, usando verbos HTTP con semántica clara.

## 2. Nivel de madurez de Richardson
El diseño alcanza el Nivel 2: se usan recursos identificados por URI, verbos HTTP y códigos de estado semánticos como 201, 404, 409 y 422.

## 3. Acoplamiento residual
Existe acoplamiento entre svc-pedidos y svc-catalogo por la validación de stock en tiempo de creación del pedido. En producción se mitiga con un patrón Circuit Breaker y caché de lectura.

## 4. Justificación de microservicios
La separación permite escalado independiente del catálogo y pedidos, además de aislar fallos y simplificar despliegue reproducible en contenedores.

## 5. REST vs gRPC
REST ofrece interoperabilidad externa y facilidad para consumidores web; gRPC mejora tipado y rendimiento en comunicaciones internas, pero complica clientes externos.

## 6. Fallo del catálogo
Si svc-catalogo falla, el pedido recibe 424 Failed Dependency o 503 Service Unavailable según el caso. Un Circuit Breaker evitaría saturar la dependencia.
