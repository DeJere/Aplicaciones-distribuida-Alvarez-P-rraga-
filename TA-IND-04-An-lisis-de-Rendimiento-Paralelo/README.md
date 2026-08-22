# TA-IND-04 — Informe Técnico Individual (Jeremy Alexis Alvarez Parraga)

Análisis de Rendimiento Paralelo (Unidad 4) aplicado al Proyecto Fin de Curso — Aplicaciones
Distribuidas (ISR-701), Universidad Técnica Estatal de Quevedo, período 2026–2027 PPA.

**Transformación individual declarada como foco: T1 — Filtrado y selección.**

## Identificación

- **Estudiante:** Jeremy Alexis Alvarez Parraga (`jalvarezp3@uteq.edu.ec`)
- **Equipo PE-U4 / GA-SUM-05:** ACC — Soporte Técnico ISP (Alvarez Parraga Jeremy Alexis,
  Aucatoma Celorio Jhinson Stalyn, Carpio Mendoza Carlos Jose)
- **PFC de referencia:** ACC — Soporte Técnico ISP (gestión de tickets de soporte técnico)
- **Docente responsable:** Gleiston C. Guerrero-Ulloa, M.Sc.

## Procedencia de los datos (trazabilidad)

Todas las cifras de este informe provienen, sin modificación, del repositorio grupal de
PE-U4:

- **Repositorio de origen:** https://github.com/carlospatroner-boop/pe-u4-spark-Soporte-Tecnico-ISP
- **Commit declarado:** `d9ce0e69ab81c4a8b7373c5a29f0522dc048f2f9` (HEAD de `main` al momento
  de la consulta)
- **Plataforma de ejecución del equipo:** contenedor Docker (`eclipse-temurin:21-jdk-jammy`,
  Java 21) con PySpark 4.1.2, `local[N]` (no Google Colab ni Databricks Community Edition;
  ver Sección 1 del informe para la justificación de esta diferencia con la guía).

**Este repositorio individual no modifica ni contiene código del repositorio de origen del
equipo** — solo una copia de los archivos de resultados estrictamente necesarios para la
trazabilidad exigida por la rúbrica (`datos/tiempos_base.csv`).

## Estructura del repositorio

```
ta-ind-04-alvarezparraga/
├── README.md                  (este archivo)
├── LICENSE
├── TA-IND-04_AlvarezParraga_Jeremy.pdf  (carátula LMS, 1 página; origen: docs/LMS_caratula.tex)
├── docs/
│   ├── TA_IND_04_Informe.tex
│   ├── TA_IND_04_Informe.pdf  (compilado, committeado)
│   ├── LMS_caratula.tex       (carátula de identificación para el LMS)
│   └── references.bib
├── datos/
│   └── tiempos_base.csv       (copia literal de resultados/tiempos_resumen.csv del equipo)
└── figuras/
    ├── fig_speedup_T1.png     (figura propia, 300 dpi)
    └── generar_figura.py      (script que genera fig_speedup_T1.png)
```

## Instrucciones exactas de compilación

El documento requiere una distribución TeX completa con **biblatex + biber** (estilo IEEE).
Probado con TeX Live 2021/2022 (`pdflatex`, `biber` 2.17+).

```bash
cd docs
pdflatex -interaction=nonstopmode TA_IND_04_Informe.tex
biber TA_IND_04_Informe
pdflatex -interaction=nonstopmode TA_IND_04_Informe.tex
pdflatex -interaction=nonstopmode TA_IND_04_Informe.tex
```

Secuencia obligatoria: **pdflatex → biber → pdflatex → pdflatex** (4 pasadas). Compila sin
errores; produce `TA_IND_04_Informe.pdf` (10 páginas: portada + 8 páginas de contenido +
referencias). Paquetes requeridos además de una instalación TeX Live estándar:
`biblatex-ieee` (parte de `texlive-bibtex-extra`), `siunitx` y `babel-spanish` (parte de
`texlive-lang-spanish`), `tikz` (parte de `texlive-pictures`). En Overleaf, todos estos
paquetes ya están disponibles por defecto.

Para regenerar la figura propia (opcional, ya está versionada):

```bash
cd figuras
python3 -m pip install matplotlib numpy
python3 generar_figura.py
```

## Lista de verificación previa a la entrega (Anexo B de la guía TA-IND-04)

- [ ] Reemplazar el placeholder de la URL del repositorio individual en la portada del
      `.tex` (`docs/TA_IND_04_Informe.tex`, línea con `<usuario-de-Jeremy>`) y en
      `docs/LMS_caratula.tex` por la URL real una vez creado este repositorio en GitHub
      como **público**; recompilar `pdflatex` y regenerar `TA-IND-04_AlvarezParraga_Jeremy.pdf`
      (origen: `docs/LMS_caratula.tex`).
- [ ] Verificar en una ventana de navegación anónima que el repositorio abre sin sesión
      iniciada.
- [ ] Verificar `GIT_TERMINAL_PROMPT=0 git ls-remote <url> HEAD` en modo anónimo (piso P3).
- [x] Confirmar que el PDF compilado está *committeado* en el repositorio.
- [x] Generar el PDF de una sola página para el LMS (`TA-IND-04_AlvarezParraga_Jeremy.pdf`)
      con la carátula de identificación y la URL de este repositorio en un solo renglón.
      Nota: compilado con el placeholder de URL; regenerarlo tras reemplazarlo.
- [ ] Confirmar que ningún párrafo coincide con el de un compañero del mismo equipo (regla
      de individualidad, piso P4).

## Declaración de uso de inteligencia artificial generativa

Ver Sección 8 de `docs/TA_IND_04_Informe.pdf`.
