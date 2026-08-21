# Documentación del Laboratorio 2

Esta carpeta contiene las fuentes documentales en Markdown necesarias para comprender, auditar y maquetar el Laboratorio 2 de Question Answering y recuperación semántica. La documentación separa fundamentos teóricos, metodología, desarrollo experimental, decisiones, resultados, interpretación y limitaciones. Su propósito es evitar que la persona encargada del informe final tenga que reconstruir el trabajo a partir de las 273 celdas del notebook.

El notebook ejecutado continúa siendo la evidencia experimental principal. Los archivos Markdown organizan esa evidencia, explican su significado y registran las decisiones adoptadas. No sustituyen los resultados originales ni autorizan recalcular métricas.

| Archivo | Propósito |
|---|---|
| `README.md` | Explica la organización de `docs/` y el flujo para construir el informe final. |
| `00_datos_generales.md` | Contiene los datos institucionales, el título recomendado y un resumen reutilizable. |
| `01_fundamentos_teoricos.md` | Desarrolla la teoría de NLP, QA, Transformers, chunking, embeddings, FAISS y RAG extractivo. |
| `02_metodologia_y_arquitectura.md` | Describe exactamente cómo se procesaron los datos, cómo se evaluó y cómo se conectan los componentes. |
| `03_desarrollo_experimental.md` | Narra la evolución de las quince fases experimentales y las hipótesis revisadas. |
| `04_decisiones_tecnicas.md` | Registra problemas, alternativas, evidencia, decisiones, justificación y consecuencias. |
| `05_resultados_y_analisis.md` | Reúne las tablas compactas, figuras principales e interpretación cuantitativa. |
| `06_hallazgos_limitaciones_y_trabajo_futuro.md` | Separa hallazgos demostrados, errores, limitaciones y extensiones no implementadas. |
| `07_rag_multidocumento.md` | Documenta corpus, arquitectura, métricas, errores y conclusiones de la extensión multidocumento. |
| `07_trazabilidad.md` | Relaciona afirmaciones y figuras con el notebook, los CSV, el PDF y el código de apoyo. |
| `08_guia_maquetacion_latex.md` | Registra las decisiones y verificaciones de la maquetación LaTeX/PDF. |
| `referencias.md` | Bibliografía verificada y enlaces primarios u oficiales. |
| `checklist_entrega.md` | Evidencia breve de la validación final. |
| `guia_defensa.md` | Guion de siete minutos, comandos y preguntas previsibles. |
| `anexos.md` | Conserva preguntas, configuraciones y evidencia secundaria que no debe recargar el cuerpo principal. |
| `informe.md` | Fuente narrativa principal del informe. |
| `informe.tex` | Fuente LaTeX final con tablas, figuras, ecuaciones y bibliografía. |
| `informe.pdf` | Entregable académico compilado. |

## Flujo documental

```text
LaboratorioML.ipynb
        ↓
resultados experimentales y CSV
        ↓
documentación modular en docs/
        ↓
informe.md
        ↓
LaTeX
        ↓
informe.pdf
```

Cada nivel cumple una función distinta:

- **Notebook:** código, salidas ejecutadas y evidencia primaria del experimento.
- **CSV y gráficos:** resultados consolidados y visualizaciones reproducibles.
- **Markdown modular:** explicación técnica, decisiones, interpretación y trazabilidad.
- **`informe.md`:** fuente narrativa consolidada para el cuerpo académico.
- **`informe.tex`:** maquetación, referencias cruzadas, numeración y control tipográfico.
- **`informe.pdf`:** entrega final compilada desde la fuente LaTeX.

## Orden de lectura recomendado

Para comprender el proyecto desde cero se recomienda leer `00_datos_generales.md`, `01_fundamentos_teoricos.md`, `02_metodologia_y_arquitectura.md` y `03_desarrollo_experimental.md`. Luego deben consultarse `04_decisiones_tecnicas.md` y `05_resultados_y_analisis.md`. Las condiciones que limitan las conclusiones están en `06_hallazgos_limitaciones_y_trabajo_futuro.md`; la ampliación se desarrolla en `07_rag_multidocumento.md`. Para auditar la entrega se deben revisar `07_trazabilidad.md`, `08_guia_maquetacion_latex.md`, `checklist_entrega.md` y `anexos.md`.

## Reglas de uso

- No sustituir cifras del notebook por estimaciones.
- Mantener diferenciados los resultados MiniLM históricos y la configuración MPNet final.
- No describir BETO-SQAC como modelo generativo: extrae spans del contexto.
- No afirmar que los modelos fueron entrenados desde cero.
- Distinguir siempre la parte obligatoria monodocumento de la extensión multidocumento.
- Consultar `referencias.md` antes de modificar una cita bibliográfica.
- Regenerar `informe.pdf` únicamente desde `informe.tex` y conservar fuera del repositorio los archivos auxiliares de LaTeX.
