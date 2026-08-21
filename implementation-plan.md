### 📋 Tablero de Seguimiento: Laboratorio ML - Asistente QA & RAG

**Instrucciones de uso para el agente/equipo:**
* Marca con `[x]` las tareas completadas.
* Actualiza el estado: `🔴 Pendiente` ➔ `🟡 En Progreso` ➔ `🟢 Completado`.
* Asegúrate de generar el **Artefacto esperado** antes de cerrar cada fase.

---
#### Fase 1: Configuración del Entorno y Repositorio (5 Puntos)
**Estado:** 🟢 Completado

* [x] Inicializar el repositorio en Git/GitHub (Individual o por equipo).
* [x] Crear la estructura de carpetas exigida: `data/`, `src/`, `results/`, `docs/`.
* [x] Crear el archivo `.gitignore` para excluir los pesos de los modelos Transformer/Sentence Transformer (archivos binarios grandes).
* [x] Redactar la versión inicial del `README.md` incluyendo: nombre, objetivo, descripción, dependencias y cómo ejecutar el notebook.
* [x] Generar el archivo `requirements.txt` con las librerías necesarias.

> **Artefacto esperado:** Repositorio en GitHub funcional y estructurado.
> **Nota:** El repositorio está publicado en GitHub y contiene `data/`, `src/`, `results/`, `tests/` y `docs/`. El `README.md` describe el proyecto completo y `requirements.txt` lista las dependencias necesarias.

#### Fase 2: Fundamentos e Implementación QA Básica (20 Puntos)
**Estado:** 🟢 Completado

* [x] Instalar dependencias en el entorno de desarrollo (Google Colab/Jupyter, PyTorch, Transformers, etc.).
* [x] Escribir bloques de texto (Markdown) explicando: QA, Transformer, Tokenizer, Score, top_k y limitaciones.
* [x] Cargar el Tokenizer y el modelo QA (`mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es`).
* [x] Crear la función `responder_pregunta()` extrayendo: respuesta, score, posición inicial (start) y final (end).
* [x] Agregar celda Markdown con explicación del Score, tabla de rangos, funcionamiento de `top_k` y tabla de limitaciones.
* [x] Agregar y ejecutar celda de demostración con 3 pruebas (respuesta correcta, sin respuesta, comparación top_k).

> **Artefacto esperado:** Notebook `.ipynb` con la función de QA ejecutándose sin errores. ✔
> **Resultados verificados:**
> - Prueba 1: `'john mccarthy'` con score **0.9408** (alta confianza ✔)
> - Prueba 2 (sin respuesta): `'estados'` con score **0.000981** (falsa confianza demostrada ✔)
> - Prueba 3: top_k=1 → `'1956'` (score 0.8288) | top_k=5 → 5 candidatos con degradación de score ✔

#### Fase 3: Contexto Propio y Análisis de Score / Top-K (20 Puntos)
**Estado:** 🟢 Completado

* [x] Redactar un contexto propio de aproximadamente 300 palabras.
* [x] Diseñar 10 preguntas basadas en el contexto creado.
* [x] Ejecutar la función de QA para las 10 preguntas y guardar las respuestas con sus scores.
* [x] Realizar pruebas modificando el parámetro `top_k` (k=1, 3, 5) para 3 preguntas representativas.
* [x] Hacer pruebas con 3 preguntas cuyas respuestas NO estén en el texto y documentar el comportamiento.
* [x] Redactar el análisis crítico sobre por qué varía el score y la utilidad del `top_k`.

> **Artefacto esperado:** Tabla de resultados renderizada en el notebook y celdas de análisis completadas. ✔
> **Resultados reales (10 preguntas, BETO-SQuAD2):**
> | N° | Dificultad | Respuesta obtenida | Score |
> |---:|:-----------|:-------------------|------:|
> | 1 | Fácil | `machine learning` | **0.8749** ✔ |
> | 2 | Intermedia | `entrenamiento, validacion y prueba` | **0.6376** ✔ |
> | 3 | Fácil | `aprendizaje supervisado` | **0.7874** ✔ |
> | 4 | Fácil | `correos maliciosos` | **0.9291** ✔ |
> | 5 | Intermedia | `en dispositivos perifericos` | **0.2518** ~ |
> | 6 | Intermedia | `sesgo y producir decisiones injustas` | **0.5374** ✔ |
> | 7 | Relación | `trazabilidad de los datos, el codigo y los parametros` | **0.4900** ✔ |
> | 8 | Intermedia | `detectar degradacion causada por cambios en los datos` | **0.3547** ✔ |
> | 9 | Relación | `modelos compactos y aceleradores especializados` | **0.7412** ✔ |
> | 10 | Difícil | `rendimiento predictivo, calidad de datos, seguridad...` | **0.7116** ✔ |
>
> Score promedio: **0.6316** | 9/10 con score ≥ 0.30 | Preguntas sin respuesta: score ≈ 0.000

#### Fase 4: Benchmark y Comparación de Modelos (15 Puntos)
**Estado:** 🟢 Completado

* [x] Seleccionar e inicializar 3 modelos QA en español propuestos en el laboratorio.
* [x] Ejecutar las 10 preguntas del contexto propio en los 3 modelos.
* [x] Medir y registrar en un DataFrame/CSV: respuestas, scores y tiempos de inferencia por cada modelo.
* [x] Repetir el experimento usando un artículo de Wikipedia en español y 5 preguntas nuevas.
* [x] Repetir el experimento con un segundo contexto técnico (Bases de Datos, IA, Redes, etc.).
* [x] Documentar ventajas y desventajas de cada modelo evaluado.

> **Artefacto esperado:** Archivo `comparacion_modelos.csv`, gráficos de rendimiento y conclusiones comparativas en el notebook.
> **Nota:** Los 3 modelos ya están identificados en el notebook (BETO-SQuAD2 mrm8488, BETO-SQuAD2 MMG, BETO-SQAC MMG). La ejecución comparativa quedó validada y cerrada con análisis de resultados y conclusiones.

#### Fase 5: Documentos Extensos, Chunking y Overlap (20 Puntos)
**Estado:** 🟢 Completado

* [x] Descargar un documento de al menos 5 páginas y ubicarlo en la carpeta `data/`.
* [x] Formular 10 preguntas sobre este documento largo.
* [x] Desarrollar la función de "Chunking" para fragmentar el texto.
* [x] Ejecutar el pipeline de QA iterando sobre los fragmentos y programar la lógica para seleccionar la mejor respuesta.
* [x] Realizar la prueba aislando la variable solapamiento: "Sin overlap" vs "Con overlap".
* [x] Analizar y registrar: cantidad de fragmentos generados, tiempo invertido, calidad de la respuesta y efecto en el score según el overlap.

> **Artefacto esperado:** Celdas del notebook con extracción, fragmentación y QA sobre textos largos, acompañadas por una comparación reproducible de las configuraciones con y sin solapamiento. ✔
> **Nota:** `LaboratorioML.ipynb` conserva el desarrollo ejecutado y `data/documento_fuente.pdf` sigue siendo la única fuente de la parte obligatoria.

#### Fase 6: Sistema RAG + FAISS (Proyecto Final) (15 Puntos)
**Estado:** 🟢 Completado

* [x] Instalar FAISS y la librería de Sentence Transformers.
* [x] Generar los Embeddings para todos los fragmentos del documento seleccionado.
* [x] Construir el índice vectorial (Base Vectorial) utilizando FAISS.
* [x] Construir la función de Búsqueda Semántica: calcular el embedding de la pregunta del usuario y recuperar los fragmentos "Top-K".
* [x] Conectar la salida de FAISS con el modelo QA: inyectar los fragmentos recuperados para que el modelo extraiga la respuesta final.
* [x] Ejecutar experimentos adicionales exigidos: probar otro modelo de embeddings, variar tamaño de chunk (300, 500, 800) y alterar el valor de *K*.

> **Artefacto esperado:** Arquitectura del asistente inteligente (RAG) completamente funcional en el notebook. ✔
> **Extensión adicional:** El corpus multidocumento se mantiene separado por PDF, con metadata de documento, página, chunk, posición y evidencia, además de métricas y análisis de errores propios.

#### Fase 7: Documentación, Informe Técnico y Cierre (5 Puntos)
**Estado:** 🟢 Completado

* [x] Validar estructuralmente el notebook ejecutado, sus tablas, gráficos y resultados de FAISS sin repetir los experimentos pesados.
* [x] Redactar el informe técnico y la documentación modular en español dentro de `docs/`.
* [x] Exportar el informe a PDF y guardarlo en la ruta `docs/informe.pdf`.
* [x] Asegurarse de que el enlace del repositorio GitHub esté en la portada del informe.
* [x] Realizar el commit final y publicar las ramas de entrega en GitHub.
* [x] Preparar la defensa técnica de 5 a 10 minutos en `docs/guia_defensa.md`.

> **Artefacto esperado:** Repositorio subido, notebook validado, pruebas superadas e informe finalizado. Listo para evaluación.

---
### 📊 Resumen de Estado General

| Fase | Descripción | Puntos | Estado |
|------|-------------|--------|--------|
| 1 | Configuración del Entorno y Repositorio | 5 pts | 🟢 Completado |
| 2 | Fundamentos e Implementación QA Básica | 20 pts | 🟢 Completado |
| 3 | Contexto Propio y Análisis de Score / Top-K | 20 pts | 🟢 Completado |
| 4 | Benchmark y Comparación de Modelos | 15 pts | 🟢 Completado |
| 5 | Documentos Extensos, Chunking y Overlap | 20 pts | 🟢 Completado |
| 6 | Sistema RAG + FAISS | 15 pts | 🟢 Completado |
| 7 | Documentación, Informe Técnico y Cierre | 5 pts | 🟢 Completado |
| **TOTAL** | | **100 pts** | **100% completado; entrega validada** |

### Estado de cierre

```text
IMPLEMENTACIÓN           ✅
EXPERIMENTOS             ✅
RAG MONODOCUMENTO        ✅
RAG MULTIDOCUMENTO       ✅
TESTS                    ✅
DOCUMENTACIÓN            ✅
INFORME                  ✅
VALIDACIÓN FINAL         ✅
ENTREGA                  ✅
```

La validación final se realizó con cuatro pruebas `pytest`, cuatro pruebas
`unittest`, compilación de `src/`, validación `nbformat`, auditoría programática
de CSV/metadata/figuras y compilación e inspección de `docs/informe.pdf`.
