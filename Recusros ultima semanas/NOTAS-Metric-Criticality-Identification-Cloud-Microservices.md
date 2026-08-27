# Notas de investigación — "Metric Criticality Identification for Cloud Microservices"

**Autores:** Akanksha Singal, Divya Pathak, Kaustabha Ray, Felix George, Mudit Verma, Pratibha Moogi
(IBM Research – India; Akanksha Singal también IIIT Delhi)
**Publicación:** arXiv:2501.03547v2 [cs.DC], 28 jul. 2025.

## Problema
En aplicaciones **cloud-native basadas en microservicios**, los Site Reliability Engineers (SREs) deben
definir alertas sobre miles de métricas de observabilidad. Hacerlo a mano es inviable: muchas alertas →
demasiados falsos positivos; pocas alertas → se pierden eventos críticos. El reto es mayor que en
monolitos por: (1) gran nº de microservicios, (2) relaciones de llamada complejas, (3) naturaleza
**estocástica** de las ejecuciones (modeladas como un DAG: nodos = microservicios, aristas = llamadas).

## Propuesta: KIMetrix
Sistema **data-driven** que identifica automáticamente un **subconjunto mínimo pero completo de métricas
críticas** por microservicio para ayudar a los SREs a definir alertas.
- Usa medidas de **teoría de la información**: **entropía** (informatividad individual de cada métrica) y
  **información mutua** (redundancia lineal y no lineal entre métricas).
- Opera **solo con métricas y trazas ligeras** — sin procesar logs no estructurados y **sin datos de
  entrenamiento etiquetados por expertos** (no supervisado).
- Es consciente de la **topología** de la aplicación (probabilidades de ejecución de cada path, obtenidas
  de las trazas).
- Es **offline**: se ejecuta periódicamente o cuando cambia la distribución de la carga.

## Formalización
**Informative Metric Subset Problem:** hallar el mapeo microservicio→métricas que **maximiza la entropía
media por métrica seleccionada**, sujeto a (a) información mutua entre cualquier par ≤ ε, y (b) presupuesto
global de tamaño ≤ χ. Se demuestra que el problema es **NP-Completo** (reducción del Maximum Weighted
Clique). Maximizar la entropía *media* (no la total) evita meter muchas métricas poco informativas.

## Algoritmos
1. **Alg. 1 – selección por microservicio:** ordena métricas por entropía descendente y añade
   greedily las que no superen el umbral ε de información mutua con las ya elegidas + el "pivot set".
2. **Alg. 2 – selección consciente de la topología:** orden topológico del DAG; el pivot de cada nodo
   es la unión de métricas de sus predecesores; ε se ajusta por la probabilidad de cada path
   (paths raros → umbral más alto → se retienen métricas para fallos poco frecuentes).
3. **Alg. 3 – AIMD (Additive Increase / Multiplicative Decrease):** ajusta ε automáticamente por
   iteraciones (sin necesidad de fijar χ), usando la *cobertura* C(Γ) — fracción de métricas cubiertas
   directamente o vía correlación — como proxy de calidad; devuelve el subconjunto más pequeño con
   cobertura máxima. Soporta varias medidas de correlación (Pearson, Spearman, Kendall, información mutua).
- **Complejidad:** O(η · |M| · ρ_max · Ψ_max²).

## Evaluación
- **Datasets:** (a) **QoTD** (Quote of the Day) en un clúster OpenShift, métricas/trazas vía Prometheus e
  Instana, 40 tipos de anomalías inyectadas (CPU, memoria, latencia, error rate), 253 métricas, datos
  cada 3 s durante un día (escenarios "Healthy" y "Mix"); (b) **DeathStarBench** – Social Network en
  Kubernetes, ~40 millones de trazas, métricas CPU/memoria/IO/red con cuellos de botella de intensidad
  variable, 180 métricas.
- **Q1:** KIMetrix reduce mucho el nº de métricas manteniendo alta cobertura de anomalías (C_A); la
  **información mutua** da la selección más generalizable. En QoTD reduce ~81–90% del espacio de métricas.
- **Q2:** el enfoque **consciente de la topología** acelera drásticamente la convergencia frente a un
  enfoque "plano" (p. ej. 12 h → 5.15 h en Healthy; 6.9 h → 0.6 h en Mix, con N=500 iteraciones).
- **Q3:** frente a SelectKBest, mRMR, Boruta y Max Weighted Clique, KIMetrix logra **mejor cobertura
  global C** y devuelve **varios** subconjuntos automáticamente sin necesidad de etiquetas ni de fijar el
  tamaño; en DeathStarBench-CPU alcanza ~99% de cobertura. Su coste de cómputo es mayor pero, al ser
  offline e infrecuente, es asumible. Es más útil en métricas de alta variabilidad.
- **Q4:** factores AIMD altos (α, β) → convergencia más rápida y curvas más suaves, pero exploran menos
  subconjuntos.

## Trabajo futuro
Incorporar logs de forma ligera para refinar aún más la selección de métricas.

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Observabilidad y fiabilidad en microservicios: cómo reducir el espacio de métricas para alertas usando
entropía, información mutua y la topología del sistema distribuido, con evaluación sobre benchmarks reales
(DeathStarBench) y un stack Prometheus/Instana en OpenShift/Kubernetes.
