# Notas de investigación — "LO2: Microservice API Anomaly Dataset of Logs and Metrics"

**Autores:** Alexander Bakhtin, Jesse Nyyssölä, Yuqing Wang, Noman Ahmad, Ke Ping, Matteo Esposito,
Mika Mäntylä, Davide Taibi (Univ. de Oulu y Univ. de Helsinki, Finlandia)
**Publicación:** PROMISE '25 (21st Int. Conf. on Predictive Models and Data Analytics in SE),
Trondheim, Noruega, 26 jun. 2025 · arXiv:2504.12067v1 (16 abr. 2025) · DOI 10.1145/3727582.3728682
**Licencia del dataset:** CC BY 4.0 · **Datos en Zenodo:** 10.5281/zenodo.14257989 (dataset) y
10.5281/zenodo.14229369 (paquete de replicación) · **Repo comunidad:** github.com/M3SOulu/LO2-Dataset-Community

## Tema
Presentan **LO2**, un dataset de datos de monitoreo (logs, métricas y trazas) de un sistema de
**microservicios de producción open-source** para investigar **detección de anomalías** y degradación
arquitectónica, en particular con **métodos multi-modales** (fusión de logs + métricas + trazas).

## Sistema bajo estudio y método
- **Light-OAuth2** (de networknt): implementación OSS del protocolo **OAuth 2.0**, 7 microservicios +
  base de datos MySQL, desplegado con Docker Compose. El proyecto fue archivado durante la recolección.
- **Pruebas con Locust** (herramienta de carga en Python): tareas *correctas* según la documentación y
  tareas de *error* (**negative testing**) para cada error documentado de la API. Flujos cubiertos:
  Authorization Code (con y sin PKCE), Client Credentials, Refresh Token, y operaciones CRUD de
  client/user/service. Se excluyó el flujo inseguro Resource Owner Password.
- **Un "run"** = desplegar el sistema → correr tareas correctas 60 s → consultar logs/trazas/métricas →
  por cada tarea de error: correr correctas + esa tarea de error 10 s → consultar datos → parar.
- Ejecutado cada hora como cronjob (jul-ago 2024) hasta llenar 540 GB de disco:
  **1740 runs × 54 tests** (1 solo-correcto + 53 de error). Datos crudos sin comprimir ≈ 540 GB.
- Recolección: logs de contenedor vía `docker logs`; métricas inyectando **Prometheus node exporter**;
  trazas inyectando el **agente Jaeger**. Consultas cada 5 s, guardadas en JSON (métricas) y CSV (trazas).

## Contenido del dataset
- **~657.000 archivos de log** (1740 runs × 54 tests × 7 servicios), con **> 2 mil millones de líneas**
  de log a nivel DEBUG.
- **> 45,5 millones de archivos de métricas**, con **485 métricas únicas** (formato timestamp-valor).
- **Trazas:** en CSV (Trace ID, Span ID, Operation Name, Start/End Time, Tags), pero **cada traza tiene
  un solo span** — Light-OAuth2 no está instrumentado para trazabilidad entre sub-operaciones; solo
  captura llamadas directas a MySQL. Por eso no se analizaron las trazas.
- **Metadatos:** logs de respuesta de Locust por run (ground truth de qué tarea causó cada error y
  timestamps), y un apéndice con distribuciones de tamaño de archivo (posible predictor barato).
- Preparado según principios **FAIR** (Findable, Accessible, Interoperable, Reusable).

## Análisis preliminar y hallazgos
- **Logs** (herramienta LogLead; representaciones: words, trigrams, event IDs):
  - *Etapa 1* (concatenar servicios, sin distinguir error/servicio): solo **DecisionTree** funciona
    razonablemente (F1 > 0.7, AUCROC ~0.73). Modelos no supervisados (IsolationForest, KMeans,
    RarityModel, OOVD) ~aleatorios (AUCROC ~0.5). Conclusión: **concatenar logs de servicios no sirve**.
  - *Etapa 2* (un modelo DecisionTree por cada par error×servicio, matriz 53×7): los logs de los
    servicios **Token** (F1 medio 0.98) y **Client** (0.95) son los más informativos; el servicio
    **Key** es el peor (0.35, no tiene tareas Locust). Con el servicio adecuado por tipo de error se
    llega a F1 = 1.0 en varios casos → modelos individuales dan cobertura completa.
- **Métricas** (PCA sobre 172 timestamps × 1124 series): los **3 primeros componentes explican > 99%**
  de la varianza; las ~10 features más relevantes son casi todas de **uso de memoria** (MemFree,
  MemAvailable, AnonPages, Committed_AS, Inactive, Shmem…) más disco escrito y bytes disponibles de FS.
- **Trazas:** no analizadas por la limitación de un solo span.

## Trabajo futuro / cómo contribuir
Instrumentar trazado real (OpenTelemetry o el sistema de networknt); cambiar los pesos de spawn de
las tareas para simular distribuciones realistas de códigos HTTP (p. ej. World Cup 1998); capturar
métricas por servicio y no solo del host; inyectar anomalías de hardware/red (latencia, disco lento,
caída de contenedores); usar otros MSS con el mismo procedimiento; contribuciones de la comunidad vía
issues de GitHub (revisión por pares pública). Meta a largo plazo: un **esquema común** que armonice
logs/métricas/trazas con identificadores compartidos (request IDs, timestamps) para fusión multi-modal.

## Amenazas a la validez
Documentación incompleta de la API de Light-OAuth2 (mitigado con revisión cruzada entre autores y el
estándar OAuth 2.0); imposible tener las 3 modalidades completas por el problema de trazado; condiciones
de test no estandarizadas; selección de tareas Locust con probabilidad igual → distribución irreal de
llamadas correctas vs. erróneas (se puede muestrear del dataset con las frecuencias deseadas sin
regenerarlo); servidor universitario que no representa una nube de producción; MySQL elegido de forma
arbitraria (aunque soportado oficialmente).

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Caso práctico de observabilidad en microservicios: pipeline de recolección de logs/métricas/trazas con
Docker + Prometheus + Jaeger, pruebas de carga y negativas con Locust sobre OAuth 2.0, y detección de
anomalías con ML sobre datos de monitoreo de un sistema distribuido real.
