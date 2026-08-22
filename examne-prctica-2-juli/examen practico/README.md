# MercadoQuevedo - Microservicios Distribuidos

## Requisitos
- Docker Desktop
- Docker Compose

## Levantar el stack
```bash
docker compose up --build
```

## Endpoints principales
- Catalogo: http://localhost:8080/api/v1/productos
- Pedidos: http://localhost:8080/api/v1/pedidos

## Arquitectura
- svc-catalogo: gestiona productos y stock
- svc-pedidos: crea pedidos y valida existencia/stock vía HTTP contra el catálogo
- nginx: reverse proxy único
- PostgreSQL: base de datos por servicio

## Justificación de la imagen base
Se usa Python para mantener imágenes livianas, con una superficie de ataque reducida y mantenimiento activo.

## Ejemplos de uso

### Con Postman
1. Importar colección: Import → Raw text → pegar JSON de la colección
2. Base URL: `http://localhost:8080`
3. Flujo recomendado:
   - POST `/api/v1/productos` - Crear un producto
   - GET `/api/v1/productos` - Listar productos
   - POST `/api/v1/pedidos` - Crear un pedido (usar product_id del paso 1)
   - GET `/api/v1/pedidos/1` - Consultar el pedido

### Con cURL
```bash
# Crear producto
curl -X POST http://localhost:8080/api/v1/productos \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU-001","nombre":"Arroz","precio":1.5,"stock":100}'

# Listar productos
curl http://localhost:8080/api/v1/productos

# Crear pedido
curl -X POST http://localhost:8080/api/v1/pedidos \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":5}'
```

### Ejecutar tests
```bash
# Instalar dependencias
pip install -r requirements.txt

# Tests del catálogo
pytest svc_catalogo/tests/ -v

# Tests de pedidos
pytest svc_pedidos/tests/ -v

# Todos los tests
pytest svc_catalogo/tests/ svc_pedidos/tests/ -v
```


