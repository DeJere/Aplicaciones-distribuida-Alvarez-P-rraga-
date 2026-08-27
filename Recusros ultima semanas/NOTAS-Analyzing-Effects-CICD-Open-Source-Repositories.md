# Notas de investigación — "Analyzing the Effects of CI/CD on Open Source Repositories in GitHub and GitLab"

**Autores:** Jeffrey Fairbanks, Akshharaa Tharigonda, Nasir U. Eisty (Dept. of Computer Science,
Boise State University, Idaho, USA)
**Publicación:** arXiv:2303.16393v1 [cs.SE], 29 mar. 2023.

## Tema
Estudio empírico (Mining Software Repositories) sobre el **impacto real de adoptar CI/CD**
(Integración y Entrega Continua) en la **velocidad de commits** y el **número de issues** de proyectos
open-source, comparando **GitHub** y **GitLab**.

## Preguntas de investigación
- **RQ1:** ¿Integrar CI/CD mejora la velocidad de commits?
- **RQ2:** ¿Integrar CI/CD afecta al número de issues del proyecto?
- **RQ3:** ¿Hay diferencias significativas en el uso/efecto de CI/CD entre GitLab y GitHub?

## Metodología
- Minaron **> 12.000 repositorios** open-source vía las APIs de GitHub y GitLab, con y sin CI/CD.
  - GitHub: buscaron el path `.github/workflow` (indica CI/CD); ante el límite de 1000 resultados por
    búsqueda usaron GitArchive y filtros por lenguaje y nº de estrellas.
  - GitLab: la API es más limitada (no permite buscar por path de archivo, estrellas, lenguaje ni
    CI/CD); usaron un wrapper de Python buscando palabras clave ('ci', 'cd', 'git', 'workflow') en el
    nombre del repo. Recolectar datos de GitLab fue ~3× más lento que de GitHub.
- **Filtros:** solo repos con ≥ 2 desarrolladores y activos en 2022; deduplicación y validación de
  buckets ("usa CI/CD" / "no usa CI/CD").
- **Dataset final:** GitHub 3223 con CI/CD y 6007 sin; GitLab 1357 con y 1356 sin.
- Atributos por repo: nº de issues (activas + cerradas) y **commit velocity** = tiempo medio entre
  commits (en horas; menor = más rápido).
- Análisis estadístico (media, mediana, desviación) en Google Sheets + Python/Google Colab.

## Resultados
### Velocidad de commits (media, horas; menor es mejor)
| Plataforma | Con CI/CD | Sin CI/CD |
|------------|-----------|-----------|
| GitHub | 16.51 h (mediana 18 h) | 27.11 h (mediana 487 h) |
| GitLab | 22.01 h (mediana 32 h) | ~25.7–26.7 h (mediana 120 h) |

→ **CI/CD aumenta la velocidad de commits en +141.19%** de media (la mejora más notable es en la
**mediana** del tiempo entre commits).

### Número de issues (media)
| Plataforma | Con CI/CD | Sin CI/CD |
|------------|-----------|-----------|
| GitHub | 175.38 (tabla III) / 135.38 (tabla X) | 52.33 / 57.33 |
| GitLab | 52.04 | 17.56 / 17.68 |

→ **CI/CD aumenta el número de issues en +321.21%** de media (mayor media y mucha mayor desviación).
Los autores lo atribuyen a que el pipeline genera errores al ejecutarse y a que más commits (y más
rápidos) implican más issues.

### RQ3 — GitHub vs GitLab
GitHub aporta más beneficios: mayor velocidad de commits y mejores herramientas de análisis/recolección
de datos. En GitHub, **más estrellas ⇒ más probabilidad de tener CI/CD**; en GitLab esa correlación no
se observó. La API de GitLab es menos completa y más lenta (una llamada por cada issue y timestamp).

## Conclusión
Implementar CI/CD **sí acelera la velocidad de commits**, pero **también aumenta mucho el número de
issues**. Los desarrolladores deben equilibrar el beneficio (entrega más rápida) frente al coste (más
issues en el repositorio y esfuerzo de configuración de las herramientas).

## Amenazas a la validez
Muestra pequeña frente a los millones de repos existentes (~12.000); análisis estadístico limitado por
tiempo; método de recolección de GitLab poco óptimo. Futuro: ampliar el dataset y análisis más profundo.

## Relevancia para el portafolio (Aplicaciones Distribuidas)
Evidencia empírica sobre los efectos de CI/CD en el flujo de desarrollo (velocidad de entrega vs.
cantidad de issues) y sobre las diferencias prácticas entre GitHub y GitLab como plataformas de
integración continua.
