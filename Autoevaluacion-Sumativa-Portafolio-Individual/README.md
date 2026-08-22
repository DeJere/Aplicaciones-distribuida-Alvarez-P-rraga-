# EV-AUT-03 — Portafolio de Evidencias Individuales

**Asignatura:** Aplicaciones Distribuidas (ISR-701)  
**Institución:** Universidad Técnica Estatal de Quevedo (UTEQ)  
**Facultad:** Facultad de Ciencias de la Computación  
**Carrera:** Ingeniería de Software  
**Estudiante:** Jeremy Alexis Alvarez Párraga ([@DeJere](https://github.com/DeJere))  
**Correo Institucional:** `jalvarezp3@uteq.edu.ec`  
**Equipo PFC:** D / ACC (ACC — Soporte Técnico ISP)  
**Docente Responsable:** Gleiston C. Guerrero-Ulloa, M.Sc.  
**Período Académico:** 2026–2027 PPA  
**Código de Actividad:** **EV-AUT-03**  
**Modalidad:** Individual | **Carácter:** Sumativa (Autoevaluación final del período)  

---

## 🔗 Enlaces Oficiales de Entrega

* **URL del repositorio del portafolio (única línea):**  
  `https://github.com/DeJere/Aplicaciones-distribuida-Alvarez-P-rraga-.git`
* **URL del repositorio del PFC (única línea):**  
  `https://github.com/DeJere/Aplicaciones-distribuida-Alvarez-P-rraga-.git`

---

## 🛠️ Instrucciones de Compilación Limpia (Regla de Piso 2)

Para reproducir y compilar de manera determinista y limpia los documentos PDF desde cualquier entorno con distribución LaTeX (TeX Live, MiKTeX o MacTeX):

### 1. Dependencias y Requisitos
* Compilador: `pdflatex` (versión $\ge 3.14159265$)
* Procesador bibliográfico: `biber` (versión $\ge 2.19$)
* Paquetes de LaTeX requeridos:
  * `babel` (con opción `spanish,es-tabla`), `inputenc` (utf8), `fontenc` (T1)
  * `geometry`, `amsmath`, `amssymb`, `siunitx`, `booktabs`, `tabularx`
  * `listings`, `xcolor`, `tcolorbox`, `tikz`, `fancyhdr`, `biblatex` (estilo `ieee`), `hyperref`, `cleveref`

### 2. Orden de Comandos para Compilación

#### A. Documento Principal del Portafolio (`Portafolio_Autoevaluacion_Sumativa.tex`):
```bash
cd Autoevaluacion-Sumativa-Portafolio-Individual/docs
pdflatex -interaction=nonstopmode Portafolio_Autoevaluacion_Sumativa.tex
biber Portafolio_Autoevaluacion_Sumativa
pdflatex -interaction=nonstopmode Portafolio_Autoevaluacion_Sumativa.tex
pdflatex -interaction=nonstopmode Portafolio_Autoevaluacion_Sumativa.tex
```

#### B. Carátula de 1 Página para Entrega en LMS SGA (`LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.tex`):
```bash
cd Autoevaluacion-Sumativa-Portafolio-Individual/docs
pdflatex -interaction=nonstopmode LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.tex
```

---

## 📑 Estructura del Entregable y Correspondencia con la Rúbrica EV-AUT-03

1. **Carátula:** Datos de identificación completos y URLs en una sola línea.
2. **Parte (a) — Tres Evidencias de Aprendizaje del Período:**
   * **Evidencia 1 (D1 - Código Propio):** Sincronización con Relojes Lógicos de Lamport *thread-safe* en Python (`AplicacionesDistribuidas/APORTEPARTEPRACTICA/distributed_nodes/lamport_clock.py`, commit `5532cbb`). Explicación en primera persona con decisión de diseño, alternativas descartadas y concepto de causalidad lógica.
   * **Evidencia 2 (D2 - Análisis Técnico sobre Datos Propios):** Medición empírica de tiempos de ejecución y *Speedup* en Apache Spark sobre 600,000 registros FCC (`pe-u4-spark-Soporte-Tecnico-ISP/resultados/tiempos_resumen.csv`, commit `e4406fe`). Protocolo detallado con `time.perf_counter()`, ajuste de Ley de Amdahl ($p \approx 89.2\%$) y análisis de la métrica de Karp-Flatt.
   * **Evidencia 3 (D3 - Reflexión Documentada):** Análisis crítico de fallos en cascada por acoplamiento síncrono HTTP en el API Gateway y propuesta transferible de *Event-Driven Architecture* (`-GA_SUM_03/api-gateway/nginx.conf`, commit `a91b0a8`).
3. **Parte (b) — Contribución Individual al PFC (D4):**
   * Historial exhaustivo de commits individuales verificables con autoría de `DeJere <jalvarezp3@uteq.edu.ec>`.
4. **Declaración de Uso de IA Generativa (D6.2):** Herramientas, alcance y distinción de autoría.
5. **Referencias Bibliográficas IEEE (D6.1):** Citas académicas reales con DOIs resolubles.
6. **Hoja de Calificación:** Autoevaluación analítica con nota **10.00 / 10.00 (Sobresaliente)**.
7. **Anexo Formativo:** Cuestionario de evaluación formativa de 10 preguntas técnicas justificadas.

---

## 📁 Archivos Disponibles en este Directorio

* [`Portafolio_Autoevaluacion_Sumativa_AlvarezParraga_Jeremy.pdf`](./Portafolio_Autoevaluacion_Sumativa_AlvarezParraga_Jeremy.pdf) — Documento completo del portafolio.
* [`LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.pdf`](./LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.pdf) — Carátula de 1 sola página para subir al LMS SGA.
* [`docs/Portafolio_Autoevaluacion_Sumativa.tex`](./docs/Portafolio_Autoevaluacion_Sumativa.tex) — Código fuente LaTeX del portafolio.
* [`docs/LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.tex`](./docs/LMS_Caratula_EV-AUT-03_AlvarezParraga_Jeremy.tex) — Código fuente LaTeX de la carátula LMS.
* [`docs/references.bib`](./docs/references.bib) — Base de datos bibliográfica en formato BibLaTeX/IEEE.
