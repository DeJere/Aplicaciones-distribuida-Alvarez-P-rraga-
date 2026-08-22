# TiendaTech Microservices - Guía de Ejecución

## Descripción General

Sistema de microservicios para TiendaTech con:
- **API Gateway** (Nginx) - Puerto 8080
- **Auth Service** (Spring Boot) - Puerto 8001
- **Resource Service** (Spring Boot) - Puerto 8002
- **Notification Service** (Spring Boot) - Puerto 8003
- **Bases de datos PostgreSQL** para auth-service y resource-service

## Requisitos Previos

- Docker >= 20.10
- Docker Compose >= 1.29
- (Opcional) Postman o cURL para testing

## Instrucciones de Compilación y Ejecución

### 1. Navegar al directorio del proyecto

```bash
cd c:\Users\carlo\Downloads\PFC2\tiendatech-microservices
```

### 2. Compilar y levantar los contenedores

```bash
docker-compose up --build
```

**Primera vez:** La compilación Maven de los servicios puede tardar 3-5 minutos.

**Salida esperada:**
```
api-gateway         | 2026/06/15 12:34:56 [notice] ... master process started
auth-db             | ... PostgreSQL ... is ready to accept connections
auth-service        | Started AuthServiceApplication in ... seconds
resource-db         | ... PostgreSQL ... is ready to accept connections
resource-service    | Started ResourceServiceApplication in ... seconds
notification-service| Started NotificationServiceApplication in ... seconds
```

### 3. Detener el sistema

```bash
docker-compose down
```

### 4. Detener y limpiar volúmenes (eliminar datos de bases de datos)

```bash
docker-compose down -v
```

---

## Endpoints de Prueba

### **1. Auth Service (Puerto 8001)**

#### 1.1 Login (obtener JWT token)

**Request:**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "P@ssw0rd"
  }'
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": {
    "token": "eyJhbGciOiJIUzUxMiJ9...",
    "expiresIn": 3600000
  },
  "message": "Autenticación exitosa",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

#### 1.2 Validar Token JWT

**Request:**
```bash
curl -X GET "http://localhost:8001/auth/validate?token=eyJhbGciOiJIUzUxMiJ9..."
```

O con header:
```bash
curl -X GET http://localhost:8001/auth/validate \
  -H "Authorization: Bearer eyJhbGciOiJIUzUxMiJ9..."
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": {
    "username": "admin",
    "valid": true
  },
  "message": "Token válido",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

---

### **2. Resource Service (Puerto 8002)**

**Nota:** Todos los endpoints requieren token JWT válido en header `Authorization: Bearer <token>`

#### 2.1 Listar todos los productos

**Request:**
```bash
curl -X GET http://localhost:8002/resources \
  -H "Authorization: Bearer <TOKEN_JWT>"
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": [],
  "message": "Productos obtenidos correctamente",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

#### 2.2 Crear un producto

**Request:**
```bash
curl -X POST http://localhost:8002/resources \
  -H "Authorization: Bearer <TOKEN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Procesador Intel i7-13700K",
    "description": "Procesador de alto rendimiento para gaming y productividad",
    "price": 429.99,
    "stock": 15,
    "category": "Procesadores"
  }'
```

**Response (Código 201):**
```json
{
  "status": 201,
  "data": {
    "id": 1,
    "name": "Procesador Intel i7-13700K",
    "description": "Procesador de alto rendimiento para gaming y productividad",
    "price": 429.99,
    "stock": 15,
    "category": "Procesadores"
  },
  "message": "Producto creado exitosamente",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

#### 2.3 Obtener un producto específico

**Request:**
```bash
curl -X GET http://localhost:8002/resources/1 \
  -H "Authorization: Bearer <TOKEN_JWT>"
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": {
    "id": 1,
    "name": "Procesador Intel i7-13700K",
    "description": "Procesador de alto rendimiento para gaming y productividad",
    "price": 429.99,
    "stock": 15,
    "category": "Procesadores"
  },
  "message": "Producto encontrado",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

#### 2.4 Actualizar un producto

**Request:**
```bash
curl -X PUT http://localhost:8002/resources/1 \
  -H "Authorization: Bearer <TOKEN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Procesador Intel i7-13700K",
    "description": "Procesador de alto rendimiento actualizado",
    "price": 399.99,
    "stock": 20,
    "category": "Procesadores"
  }'
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": {
    "id": 1,
    "name": "Procesador Intel i7-13700K",
    "description": "Procesador de alto rendimiento actualizado",
    "price": 399.99,
    "stock": 20,
    "category": "Procesadores"
  },
  "message": "Producto actualizado exitosamente",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

#### 2.5 Eliminar un producto

**Request:**
```bash
curl -X DELETE http://localhost:8002/resources/1 \
  -H "Authorization: Bearer <TOKEN_JWT>"
```

**Response (Código 200):**
```json
{
  "status": 200,
  "data": null,
  "message": "Producto eliminado exitosamente",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

---

### **3. Notification Service (Puerto 8003)**

#### 3.1 Enviar notificación

**Request:**
```bash
curl -X POST http://localhost:8003/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "resourceId": 1,
    "action": "CREATED",
    "message": "Nuevo producto agregado al inventario",
    "recipientEmail": "admin@tiendatech.com"
  }'
```

**Response (Código 201):**
```json
{
  "status": 201,
  "data": {
    "id": 1,
    "resourceId": 1,
    "action": "CREATED",
    "message": "Nuevo producto agregado al inventario",
    "recipientEmail": "admin@tiendatech.com",
    "timestamp": "2026-06-15T12:34:56Z"
  },
  "message": "Notificación procesada exitosamente",
  "timestamp": "2026-06-15T12:34:56Z"
}
```

**Salida en logs del contenedor:**
```
===== SMTP EMAIL SIMULATION =====
From: alerts@tiendatech.local
To: admin@tiendatech.com
Subject: TiendaTech Notification - CREATED
------
Resource ID: 1
Action: CREATED
Message: Nuevo producto agregado al inventario
Timestamp: 2026-06-15T12:34:56.123456
=====================================
```

---

### **4. API Gateway (Puerto 8080)**

El gateway redirige las peticiones a los microservicios:

```bash
# Redirige a http://auth-service:8001/
curl http://localhost:8080/api/auth/login

# Redirige a http://resource-service:8002/
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8080/api/resources

# Redirige a http://notification-service:8003/
curl -X POST http://localhost:8080/api/notifications \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Variables de Entorno (.env)

El archivo `.env` en la raíz contiene todas las variables necesarias:

```env
# Auth Service
AUTH_JWT_SECRET=YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwYWJjZA==
AUTH_POSTGRES_USER=auth_user
AUTH_POSTGRES_PASSWORD=SecureAuthPass123!@#
AUTH_POSTGRES_DB=authdb

# Resource Service
RESOURCE_POSTGRES_USER=resource_user
RESOURCE_POSTGRES_PASSWORD=SecureResourcePass456!@#
RESOURCE_POSTGRES_DB=resourcedb

# Notification Service
SMTP_HOST=smtp.tiendatech.local
SMTP_PORT=587
SMTP_USER=notifications@tiendatech.local
SMTP_PASS=NotificationsPass789!@#
SMTP_FROM=alerts@tiendatech.local
```

---

## Notas Importantes

### Credenciales de Prueba

- **Auth Service:** 
  - Usuario: `admin`
  - Contraseña: `P@ssw0rd`

### JWT Token
- **Expiración:** 1 hora (3600 segundos)
- **Algoritmo:** HS512
- **Secret:** Obtenido de variable `AUTH_JWT_SECRET`

### Bases de Datos
- **Auth DB:** `authdb` en contenedor `auth-db:5432`
- **Resource DB:** `resourcedb` en contenedor `resource-db:5432`
- Datos persistentes en volúmenes `auth-db-data` y `resource-db-data`

### Rate Limiting
- API Gateway limita a **100 peticiones por minuto** por IP
- Exceso devuelve `503 Service Unavailable`

---

## Troubleshooting

### Los contenedores no inician

Verifica que Docker está en ejecución:
```bash
docker ps
```

### Error de puerto en uso

Si el puerto 8080, 8001, 8002 u 8003 está en uso, edita `docker-compose.yml` y cambia los puertos.

### Base de datos no se conecta

Asegúrate de que el archivo `.env` existe en la raíz del proyecto y que las variables están correctas.

### Ver logs en tiempo real

```bash
docker-compose logs -f <nombre-servicio>
```

Ejemplo:
```bash
docker-compose logs -f auth-service
docker-compose logs -f resource-service
```

---

## Estructura de Directorios

```
tiendatech-microservices/
├── api-gateway/
│   ├── nginx.conf
│   └── Dockerfile
├── auth-service/
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/java/com/tiendatech/authservice/...
├── resource-service/
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/java/com/tiendatech/resourceservice/...
├── notification-service/
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/java/com/tiendatech/notificationservice/...
├── docs/
│   └── api/
│       ├── auth.yaml
│       ├── resources.yaml
│       └── notifications.yaml
├── docker-compose.yml
├── .env (variables de entorno)
├── .env.example (plantilla de variables)
└── .gitignore
```

---

¡Sistema listo para producción local!
