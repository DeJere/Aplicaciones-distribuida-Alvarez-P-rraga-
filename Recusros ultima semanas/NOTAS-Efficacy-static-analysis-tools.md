# Notas de investigación — "Efficacy of static analysis tools for software defect detection on open-source projects"

**Autores:** Jones Yeboah, Saheed Popoola (School of Information Technology, University of Cincinnati, USA)
**Publicación:** CSCI'23 — 10th Annual Conf. on Computational Science & Computational Intelligence,
13–15 dic. 2023, USA.

## Tema
Comparación empírica de **herramientas de análisis estático** para la **detección de defectos de software**
en proyectos open-source escritos en Java, C/C++ y Python.

## Herramientas comparadas
- **SonarQube** — análisis multi-lenguaje (Java, C/C++, Python…); reporta "issues" por violar reglas de
  codificación, con categorías de fiabilidad (bugs), mantenibilidad (code smells) y seguridad.
- **FindBugs** — analiza *bytecode* Java; detecta "bug patterns" en 9 categorías (bad practice,
  correctness, seguridad, rendimiento, multithreading, etc.), con ranking de gravedad 1–20.
- **Checkstyle** — calidad/estilo de código Java según un estándar (Google/Sun Java Style o config.
  propia); 14 categorías de checks, severidades error / warning.
- **PMD** — reglas de calidad para Java + otros lenguajes (variables no usadas, bloques catch vacíos,
  creación innecesaria de objetos…); 8 categorías, prioridad 1–5.

## Metodología
- **Dataset:** 50 proyectos open-source de GitHub (computación científica, desarrollo web, programación
  de sistemas), en Java, C/C++ y Python, de tamaños y complejidad variados.
- **Métricas:** Precision, Recall y F1-score (TP/FP/FN/TN sobre detección de errores).
- **Diseño experimental:** 4 grupos, cada proyecto asignado aleatoriamente a un grupo y cada grupo
  usando una herramienta distinta; validación cruzada + ANOVA de una vía y post-hoc de Tukey.

## Resultados
| Herramienta | Precision | Recall | F1-score |
|-------------|-----------|--------|----------|
| **SonarQube** | **0.83** | **0.87** | **0.85** |
| FindBugs | 0.78 | 0.82 | 0.80 |
| PMD | 0.71 | 0.76 | 0.73 |
| Checkstyle | 0.69 | 0.71 | 0.70 |

- **SonarQube es la más efectiva** en los tres lenguajes; le siguen FindBugs, PMD y Checkstyle.
- **ANOVA:** diferencia significativa en F1 entre herramientas (F(3,196) = 4.63, p < 0.05).
- **Post-hoc Tukey:** SonarQube difiere significativamente de Checkstyle y de PMD (p < 0.05);
  **no** hay diferencia significativa entre SonarQube y FindBugs.
- Coincide con estudios previos que también señalan a SonarQube como herramienta fiable; aunque otros
  trabajos hallaron que PMD y FindBugs superan a SonarQube para ciertos tipos de defectos en Java.

## Limitaciones y trabajo futuro
Solo 50 proyectos y solo open-source (no generaliza a software propietario); no se exploró el efecto de
distintas configuraciones de cada herramienta ni tipos específicos de defectos. Futuro: probar ESLint,
Infer y técnicas de Machine Learning para mejorar la detección; estudiar contextos propietarios.

## Recomendación del estudio
Elegir **SonarQube o FindBugs** como herramientas principales, pero la elección debe guiarse por las
necesidades del proyecto (lenguaje, tamaño del código, complejidad, balance precision/recall) y
combinar las herramientas con buenas prácticas de aseguramiento de calidad; no confiar únicamente en
el análisis estático.

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Guía práctica para elegir herramientas de análisis estático y asegurar la calidad del código en
proyectos de software, con evidencia empírica y análisis estadístico.
