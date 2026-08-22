# Portafolio Personal de Evidencias de Aprendizaje y Autoevaluación Sumativa Individual

**Asignatura:** Aplicaciones Distribuidas (ISR-701)  
**Institución:** Universidad Técnica Estatal de Quevedo (UTEQ)  
**Facultad:** Facultad de Ciencias de la Computación  
**Carrera:** Ingeniería de Software  
**Estudiante:** Jeremy Alexis Alvarez Párraga ([@DeJere](https://github.com/DeJere))  
**Correo Institucional:** `jalvarezp3@uteq.edu.ec`  
**Docente Responsable:** Gleiston C. Guerrero-Ulloa, M.Sc.  
**Período Académico:** 2026–2027 PPA  
**Modalidad:** Individual | **Carácter:** Sumativa (Autoevaluación de fin de período)  

---

## 📊 Desglose Oficial de Calificación de la Actividad

| Componente de Evaluación | Ponderación | Nota Obtenida | Puntaje Ponderado |
| :--- | :---: | :---: | :---: |
| **Portafolio de Evidencias de Aprendizaje y Autoevaluación** | 60% | 10.00 / 10.00 | **6.00 / 6.00** |
| **Cuestionario de Evaluación Formativa de Fin de Período** | 40% | 10.00 / 10.00 | **4.00 / 4.00** |
| **CALIFICACIÓN FINAL CONSOLIDADA (100%)** | **100%** | **10.00 / 10.00** | **10.00 / 10.00** |

---

## 📑 Estructura y Contenido del Portafolio

El portafolio se encuentra completamente documentado y formalizado en formato LaTeX/PDF, cumpliendo con todos los criterios de la rúbrica institucional:

### 1. Tres (3) Evidencias Concretas de Aprendizaje del Período
1. **Evidencia 1 (Unidad 1 y 2 - Sockets y Sincronización Lógica):**
   - Implementación en Python del algoritmo de **Relojes Lógicos de Lamport** con soporte *thread-safe*, enmarcado de paquetes (*length-prefix framing*) y ordenación causal estricta de eventos ($a \to b$).
   - *Código de referencia:* `AplicacionesDistribuidas/APORTEPARTEPRACTICA/distributed_nodes/`
2. **Evidencia 2 (Unidad 3 - Arquitectura de Microservicios y Resiliencia):**
   - Diseño de un ecosistema distribuido desacoplado con **API Gateway (Nginx)**, autenticación *stateless* basada en **JSON Web Tokens (JWT)** y microservicios independientes (`auth-service`, `resource-service`, `notification-service`, `catalogo`, `pedidos`).
   - *Código de referencia:* `-GA_SUM_03/` y `examne-prctica-2-juli/`
3. **Evidencia 3 (Unidad 4 - Cómputo Paralelo Masivo y Ley de Amdahl):**
   - Pipeline distribuido en **Apache Spark (PySpark)** sobre un conjunto de datos real de más de 600,000 registros (FCC Consumer Complaints), con análisis comparativo frente a Pandas monohilo y contrastación experimental del *Speedup* ($S(N)$) y fracción paralelizable ($p \approx 89.2\%$) según la **Ley de Amdahl**.
   - *Código de referencia:* `pe-u4-spark-Soporte-Tecnico-ISP/` y `TA-IND-04-An-lisis-de-Rendimiento-Paralelo/`

### 2. Contribución Individual al PFC y Registro de Commits GitHub
- Repositorio Oficial: [`https://github.com/DeJere/Aplicaciones-distribuida-Alvarez-P-rraga-.git`](https://github.com/DeJere/Aplicaciones-distribuida-Alvarez-P-rraga-)
- Historial inmutable y continuo de commits desde mayo de 2026 hasta agosto de 2026, con autoría única de **Jeremy Alexis Alvarez Párraga** (`DeJere <jalvarezp3@uteq.edu.ec>`).

### 3. Cuestionario de Evaluación Formativa de Fin de Período (40%)
- Banco de 10 preguntas teórico-prácticas resueltas con fundamentación formal sobre Teorema CAP, Relojes de Lamport vs Vectoriales, gRPC/Protobuf, API Gateway, JWT Stateless, Transformaciones Narrow vs Wide en Spark, Ley de Amdahl, DAGs y Tolerancia a Fallos, Fallos Bizantinos y Orquestación con Docker Compose.

---

## 📂 Archivos del Entregable

- **Documento LaTeX fuente:** [`docs/Portafolio_Autoevaluacion_Sumativa.tex`](./docs/Portafolio_Autoevaluacion_Sumativa.tex)
- **Bibliografía IEEE:** [`docs/references.bib`](./docs/references.bib)
- **Documento PDF Compilado:** [`Portafolio_Autoevaluacion_Sumativa_AlvarezParraga_Jeremy.pdf`](./Portafolio_Autoevaluacion_Sumativa_AlvarezParraga_Jeremy.pdf)
