# Notas de investigación — "Informed and Assessable Observability Design Decisions in Cloud-native Microservice Applications"

**Autores:** Maria C. Borges, Joshua Bauer, Sebastian Werner, Michael Gebauer, Stefan Tai
(Information Systems Engineering, Technische Universität Berlin, Alemania)
**Publicación:** preprint, arXiv:2403.00633v2 [cs.SE], 12 jul. 2024. Financiado por la UE (proyecto TEADAL).
**Herramienta:** Oxn — https://github.com/nymphbox/oxn

## Problema
Instrumentar y configurar la **observabilidad** (monitoreo, tracing, logging) de aplicaciones de
microservicios es difícil, dependiente de la herramienta y costoso. Los arquitectos deben sopesar
**trade-offs** (overhead de rendimiento y coste de la infraestructura de observabilidad frente al valor
que aporta), pero hoy esas decisiones se toman por "intuición profesional" sin método sistemático.
Una mala configuración puede **ocultar fallos** y aumentar latencia y coste.

## Objetivo
Convertir la **observabilidad de fallos** ("fault observability") en una propiedad **testable y
cuantificable** del sistema, análoga a la cobertura de tests, para guiar decisiones de configuración e
instrumentación de forma informada y continuamente evaluable.

## Contribuciones
1. **Modelo** del espacio de decisiones de observabilidad en el stack cloud-native (CloudEnvironment →
   Cluster → VM → Container → Microservice[Runtime, Framework, ApplicationCode]; InstrumentationPoints
   de tipo Metric/Log/Trace; Monitoring, Tracing y FaultDetection con Classifier/Alert/Dashboard).
   Sirve como lenguaje común para documentar y discutir alternativas de diseño.
2. **Métricas de observabilidad de fallos** (testables):
   - **Fault visibility** `v(f,m,d)` = 1 si la función de detección `DF(mt)` supera el umbral α durante
     el fallo (los datos del fallo son suficientemente distintos de la operación normal), 0 si no.
   - **Fault coverage** `FC(f,d)` = fracción de métricas en las que el fallo f es visible.
   - **Overall Fault Observability (OFO)** = fracción de fallos que son visibles en al menos una métrica.
   - **Métrica de coste**: en el paper se usa utilización de CPU (extensible a memoria/almacenamiento).
   Para subir el OFO: reconfigurar métricas existentes, añadir métricas más sensibles, o cambiar el
   mecanismo de detección — siempre sopesando el coste.
3. **Oxn — "Observability Experiment Engine"**: framework para ejecutar **experimentos de observabilidad**
   (inspirados en Chaos Engineering). Un experimento se define en un YAML versionable con: SUE (System
   Under Experiment, total o subconjunto), workload, *treatments* y *response variables*.
   - **Fault treatments** (runtime): Pause, Kill (Docker); NetworkDelay, PacketLoss, PacketCorruption
     (tc); Stress (stress-ng).
   - **Instrumentation treatments** (compilación): MetricSamplingRate, TracingSamplingStrategy,
     TracingSamplingRate (Collector) — cambian la config sin tocar el código del SUE.
   - Response variables = métricas y trazas (desacopladas de los treatments, permiten efectos de
     segundo orden). Componentes: orchestrator (Docker Compose), runner, load generator (Locust),
     observers (Jaeger, Prometheus), store, reporter, accountant (coste por CPU).
   - Trae por defecto un clasificador de **regresión logística** (umbral de accuracy α = 0.7) como
     mecanismo de detección de fallos, reemplazable por el del usuario.

## Evaluación (caso de ejemplo)
- **SUE:** OpenTelemetry Astronomy Shop Demo (20 servicios + 4 de observabilidad), en una VM de 8 vCPU /
  32 GB; experimentos centrados en el `recommendation-service`.
- **Baseline:** systemCPU (sampling 5 s), custom metric recommsPerMinute (60 s), tracing probabilístico
  al 1%. Fallos probados: Pause, PacketLoss [15%], NetworkDelay [0–90 ms], 10 min × 10 repeticiones,
  50 usuarios concurrentes.
- **Resultados baseline:** Pause visible en las 3 métricas (FC 3/3); PacketLoss solo en systemCPU
  (FC 1/3); NetworkDelay **no visible** (FC 0/3). **OFO = 2/3**.
- **Alternativas de diseño:** (A) subir sampling del contador de recomendaciones a 5 s; (B) tracing al
  5%; (C) tracing al 10%.
  - (A): mejora FC de PacketLoss (1/3 → 2/3) pero NO cambia el OFO (delay sigue invisible).
  - (B) y (C): hacen visible el NetworkDelay → **OFO = 3/3**. Rendimiento similar entre ambas.
  - **Coste (overhead CPU):** (A) +3.98%, (B) +3.05%, (C) +5.33% → **(B) es la mejor opción**: mismo
    beneficio de observabilidad que (C) a menor coste.

## Limitaciones y trabajo futuro
Basado en simulación y experimentos aislados (no cargas reales completas); métricas deliberadamente
simples e independientes de la tecnología; Oxn aún sin soporte de logs ni integración con Kubernetes.
Futuro: soporte de alerting y MTTD, más métricas de coste, integración en pipelines CI, y optimización
automática/inteligente de los parámetros de configuración de observabilidad.

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Método y herramienta para tomar decisiones de arquitectura sobre observabilidad en microservicios de
forma medible: modelo del espacio de diseño, métricas de visibilidad/cobertura de fallos y experimentos
tipo Chaos Engineering con OpenTelemetry, Jaeger, Prometheus y Locust, evaluando el trade-off
observabilidad vs. coste.
