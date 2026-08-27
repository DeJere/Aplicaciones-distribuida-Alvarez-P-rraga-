# Notas de investigación — "Scalable and Accurate Test Case Prioritization in Continuous Integration Contexts"

**Autores:** Ahmadreza Saboor Yaraghi, Mojtaba Bagherzadeh, Nafiseh Kahani, Lionel Briand
**Publicación:** arXiv:2109.13168v3 (5 abr. 2022) — trabajo tipo IEEE TSE
**Repositorio de datos/herramienta:** https://github.com/Ahmadreza-SY/TCP-CI

## Tema
Priorización de casos de prueba (TCP, *Test Case Prioritization*) para pruebas de regresión en contextos de
Integración Continua (CI), usando modelos de Machine Learning (ML). El objetivo es ejecutar primero los
casos de prueba con mayor probabilidad de detectar fallos, reduciendo el tiempo de feedback del build.

## Aportes principales
1. **Modelo de datos conceptual** de un build de CI (entidades: Build, Build Log, Test Case, Source Code,
   Commit, Bug/Fault y sus relaciones: COV cobertura, CHN cambios, IMP impacto, DET detección, etc.).
2. **Conjunto exhaustivo de 150 features** en 9 subgrupos, organizados en 3 grupos de alto nivel:
   - **REC** (Test Case Execution Records): historial de ejecución — edad del test, tasas de fallo/aserción/
     excepción/transición, tiempos de ejecución previos, último veredicto.
   - **TES** (Test Case Source Code): complejidad, proceso de desarrollo y métricas de cambio del código
     fuente del propio test (subgrupos TES_COM, TES_PRO, TES_CHN).
   - **COV** (Coverage): features de los archivos fuente cubiertos/impactados por el test (F_COV, COD_COV_*,
     DET_COV), calculadas con análisis estático ligero + minería de reglas de asociación sobre co-cambios.
3. **Clasificador de commits defect-fix vs. non-defect** con TF-IDF + XGBoost (83.5% exactitud en CV),
   alternativa más barata que BERT (~92%) para el contexto de CI.
4. **Herramientas de recolección** de las 150 features para proyectos Java con Travis CI (usa PyDriller,
   Understand y RankLib).
5. **Benchmark de 25 proyectos** open-source Java (21.5k builds, 2.5k builds fallidos, mediana 229k SLOC,
   tasa de fallo mediana 14%, tiempo de regresión ≥ 5 min) para comparar futuras técnicas de TCP.

## Preguntas de investigación y hallazgos
- **RQ1 — Tiempo de recolección de datos:** varía de 0.1 a 11.7 min por build. Los grupos basados en
  **cobertura (COV)** son los más caros (requieren análisis estático + de dependencias); **TES_CHN** el más
  barato (~1.3 s). ~21% del tiempo se gasta en features de archivos impactados. El tamaño del sujeto (SLOC)
  y el nº de tests correlacionan fuertemente con el tiempo de recolección (Spearman ρ ≈ 0.79–0.85).
- **RQ2 — Efectividad (métrica APFD_C):**
  - Random Forest es el mejor modelo de ranking (supera a MART/LambdaMART/RankBoost/ListNet/CA).
  - Con el set completo de features: APFD_C medio = **0.82**.
  - Incluir o no los archivos impactados **no** cambia significativamente la efectividad.
  - Quitar cualquiera de los 9 subgrupos no produce diferencia práctica; los grupos **REC** y **TES**
    solos logran casi el mismo APFD_C que el set completo, mientras que los grupos de **cobertura solos
    son los peores**.
  - Features más usadas: edad del test (REC), experiencia de los desarrolladores y nº de commits
    (TES_PRO), tiempos de ejecución (REC), tamaño del test (TES_COM).
- **RQ3 — Decaimiento del modelo:** hay que reentrenar con una ventana (RW) **menor a 11 builds** para
  resultados estables; cuanto más frecuente el reentrenamiento, mejor.
- **RQ4 — Trade-off / guías prácticas:**
  - Si el coste de recolección es asumible → **RF con el set completo, reentrenando en cada build o cada
    ≤ 11 builds**.
  - Si no → **RF solo con features REC** (coste casi nulo, efectividad cercana al set completo).
  - Opción más rápida y menos efectiva → **heurísticas basadas en historial de fallos** (útil sobre todo
    en sistemas con muchos builds y altas tasas de fallo).

## Amenazas a la validez
Cobertura estimada por análisis estático (sobreestima), cobertura a nivel de archivo, eliminación de
tests "frequently-failing" con la regla de los tres sigmas, dependencia de GHTorrent/TravisTorrent/RTPTorrent,
solo proyectos Java con Travis CI (no GitHub Actions ni otros lenguajes).

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Referencia sobre pruebas de regresión y CI/CD en sistemas grandes: cómo priorizar pruebas con ML,
qué datos recolectar y a qué coste, y el trade-off entre tiempo de recolección y efectividad.
