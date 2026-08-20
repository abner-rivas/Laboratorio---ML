# Metodología

Este documento describe cómo se realizó el laboratorio. Los valores cuantitativos completos se concentran en `05_resultados_y_analisis.md`; aquí se presentan el diseño, las entradas, las funciones y la arquitectura que produjeron esos resultados.

## 1. Flujo experimental

El trabajo se organizó de forma incremental:

1. Carga y verificación de un modelo QA en español.
2. Pruebas sobre contextos breves, respuestas candidatas y preguntas sin evidencia.
3. Evaluación de diez preguntas sobre un contexto propio.
4. Comparación controlada de tres modelos QA en tres dominios.
5. Selección de BETO-SQAC como extractor documental.
6. Extracción y limpieza del PDF institucional.
7. Evaluación exhaustiva de seis configuraciones de chunking y overlap.
8. Selección de chunks de 800 caracteres sin solapamiento.
9. Construcción de un RAG histórico con MiniLM y FAISS.
10. Evaluación de $K=1,3,5,10$.
11. Comparación del baseline exhaustivo con RAG Top-10.
12. Clasificación de errores.
13. Comparación de MiniLM y MPNet.
14. Evaluación de bases vectoriales de 50, 100, 150 y 217 elementos.
15. Registro de la configuración final.

Cada fase mantuvo sus resultados históricos. Las decisiones finales se tomaron con las salidas ejecutadas más recientes del notebook, no con descripciones preliminares.

## 2. Entorno y herramientas

`requirements.txt` declara las bibliotecas sin fijar versiones. El notebook indica Python 3.10 o superior.

| Herramienta | Función en el laboratorio |
|---|---|
| `transformers` | Carga de tokenizers, modelos QA y pipelines de Hugging Face. |
| `torch` | Ejecución de inferencia, dispositivo, modo de evaluación y lotes sin gradientes. |
| `sentence-transformers` | Generación de embeddings para chunks y preguntas. |
| `faiss-cpu` | Construcción de `IndexFlatIP` y búsqueda vectorial exacta. |
| `pandas` | Tablas de resultados, agrupaciones, ordenamientos y exportación a CSV. |
| `numpy` | Matrices, normalización y operaciones numéricas. |
| `matplotlib` | Visualización de resultados y exportación de gráficos. |
| `PyMuPDF` | Apertura del PDF y extracción de texto página por página. |
| `huggingface-hub` | Consulta y carga de información de modelos. |

Las comparaciones de modelos QA y la fase exhaustiva del documento quedaron registradas en CPU. La etapa RAG posterior registró CUDA para BETO. Esta diferencia no modifica los conteos de inferencias, pero limita la atribución del speedup temporal exclusivamente a la arquitectura.

## 3. Modelos QA evaluados

Se usaron los identificadores reales del notebook:

| Nombre abreviado | Identificador exacto |
|---|---|
| BETO-SQuAD2 (mrm8488) | `mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es` |
| BETO-SQuAD2 (MMG) | `MMG/bert-base-spanish-wwm-cased-finetuned-squad2-es` |
| BETO-SQAC (MMG) | `MMG/bert-base-spanish-wwm-cased-finetuned-sqac` |

Los modelos se cargaron como `AutoModelForQuestionAnswering` junto con su `AutoTokenizer`. En la comparación controlada, cada uno recibió exactamente cinco preguntas por contexto con `top_k=1`. El tiempo de carga se registró aparte; antes de medir inferencia se realizó calentamiento. Después de cada conjunto, el modelo se liberó antes de cargar el siguiente.

## 4. Modelo QA final

El extractor seleccionado fue:

`MMG/bert-base-spanish-wwm-cased-finetuned-sqac`

La selección ocurrió después de integrar los resultados de tres contextos. El criterio jerárquico priorizó respuestas correctas y estabilidad de extracción antes de score y tiempo. BETO-SQAC obtuvo 15/15 en el agregado y se conservó sin reentrenamiento para chunking y RAG.

## 5. Documento

El único documento oficial de las fases extensas obligatorias fue:

`data/documento_fuente.pdf`

Título: *Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador*.

| Propiedad | Valor ejecutado |
|---|---:|
| Páginas | 62 |
| Caracteres crudos | 177 390 |
| Caracteres limpios | 173 419 |
| Palabras aproximadas | 26 119 |
| Páginas con texto | 62 |
| Páginas sin texto | 0 |
| Páginas con menos de 200 caracteres | 0 |
| Tamaño | 497 732 bytes |

El PDF se mantuvo sin modificaciones y fue la fuente de las diez preguntas finales.

## 6. Extracción del PDF

PyMuPDF abrió el documento y extrajo cada página de forma independiente. Por cada registro se conservaron número de página, texto crudo, texto limpio y offsets dentro del texto unido.

No se aplicó OCR porque las 62 páginas contenían texto extraíble y ninguna presentó extracción corta. Esta comprobación evitó introducir un procesamiento innecesario y permitió usar el contenido textual original.

## 7. Limpieza de texto

La función `limpiar_texto_pagina()` de `src/funciones_qa.py` realizó solo operaciones conservadoras:

- eliminación del carácter de guion blando;
- unión de palabras cortadas por guion y salto de línea;
- normalización de secuencias de espacios;
- eliminación de espacios al inicio y al final.

No se resumieron artículos, no se corrigió redacción y no se sustituyeron términos. La limpieza buscó eliminar artefactos de extracción sin cambiar la evidencia.

## 8. Construcción de chunks

`crear_fragmentos_con_metadata()` recorrió el texto con un paso igual a `chunk_size - overlap`. Para cada ventana conservó:

| Campo | Significado |
|---|---|
| `chunk_id` | Identificador secuencial. |
| `texto` | Contenido del fragmento. |
| `inicio` | Offset inicial en el texto limpio unido. |
| `fin` | Offset final. |
| `pagina_inicio` | Página física asociada al inicio. |
| `pagina_fin` | Página física asociada al final. |

La implementación valida que `chunk_size` sea positivo y que $0 \leq overlap < chunk\_size$. La asociación entre offset y página permite comprobar procedencia y detectar cuándo un span correcto proviene de otro artículo.

Se evaluaron seis configuraciones:

| Etiqueta | Chunk | Overlap |
|---|---:|---:|
| A | 300 | 0 |
| B | 300 | 50 |
| C | 500 | 0 |
| D | 500 | 100 |
| E | 800 | 0 |
| F | 800 | 150 |

## 9. Evaluación QA

La función `normalizar_texto()` convierte a minúsculas, elimina diacríticos mediante normalización Unicode, retira signos no alfanuméricos y compacta espacios. `evaluar_coincidencia()` aplica esta precedencia:

1. igualdad exacta tras normalización;
2. respuesta esperada contenida en un span más amplio;
3. variante textual con cobertura léxica mínima de 0.80 y precisión mínima de 0.60;
4. respuesta parcial cuando la cobertura es al menos 0.60;
5. respuesta incorrecta o no relacionada.

Cuando una pregunta tenía variantes aceptables declaradas antes de la ejecución, `evaluar_respuesta_con_variantes()` podía aceptarlas y las marcaba como revisión manual explícita. Esta lógica no cambiaba la cadena, el score ni el tiempo del modelo.

Para validar recuperación documental, `evidencia_en_fragmento()` exigió presencia textual de la evidencia y, cuando correspondía, cobertura de la página objetivo. Esta verificación separó coincidencia léxica de procedencia.

## 10. Arquitectura del baseline exhaustivo

El baseline aplicó BETO-SQAC sobre cada chunk de una configuración y seleccionó el mayor score para la pregunta:

```text
pregunta
  ↓
todos los chunks
  ↓
BETO-SQAC en lotes
  ↓
span con score máximo
```

El tamaño de lote fue 24. El modelo operó en modo `eval()` y bajo `torch.no_grad()`. Con 217 chunks y diez preguntas, la configuración 800/0 requirió $217 \times 10 = 2\,170$ evaluaciones QA.

Este baseline sirve como referencia, pero su selector no incorpora relevancia documental: compara el score máximo de todos los artículos.

## 11. Arquitectura RAG

La preparación se ejecutó una vez por modelo de embeddings:

```text
217 chunks
  ↓
embeddings L2 normalizados
  ↓
FAISS IndexFlatIP
```

Cada consulta siguió este flujo:

```text
pregunta
  ↓
embedding L2 normalizado
  ↓
FAISS Top-K
  ↓
BETO-SQAC sobre K chunks
  ↓
span con mayor score QA
```

El score FAISS no se combinó con el score QA. La primera métrica ordenó contextos; la segunda seleccionó el span dentro del subconjunto. Top-10 y diez preguntas implicaron como máximo 100 evaluaciones QA.

## 12. Métricas utilizadas

### Accuracy

$$
\operatorname{Accuracy} =
\frac{\text{respuestas correctas}}
{\text{total de preguntas}}.
$$

### Score QA

Promedio o mediana de la confianza asignada por el extractor. No se interpretó como accuracy.

### Recall@K

$$
\operatorname{Recall@K} =
\frac{\text{preguntas con evidencia recuperada}}
{\text{total de preguntas}}.
$$

### Tiempo

Se distinguieron carga, embeddings, índice y consultas. Los tiempos provienen de una ejecución por configuración y no incluyen intervalos de variabilidad.

### Inferencias QA

Se calculó como número de contextos procesados por pregunta multiplicado por el número de preguntas.

### Speedup

$$
\operatorname{speedup} =
\frac{T_{\text{baseline}}}{T_{\text{RAG}}}.
$$

El valor histórico de esta razón debe interpretarse junto con la diferencia de dispositivo registrada entre fases.

### Reducción de inferencias

$$
\operatorname{reduccion} =
1 - \frac{I_{\text{RAG}}}{I_{\text{baseline}}}.
$$

Para 100 y 2 170 inferencias, la reducción fue 95.4 %.

## 13. Diseño del experimento de tamaño

La comparación de bases no eliminó deliberadamente la evidencia. Se identificaron 11 chunks obligatorios únicos para las diez preguntas. La pregunta 10 necesitó los chunks adyacentes 155 y 156. Todas las bases conservaron esos elementos y se completaron con distractores mediante una permutación reproducible con semilla 42.

| Vectores | Chunks obligatorios | Distractores |
|---:|---:|---:|
| 50 | 11 | 39 |
| 100 | 11 | 89 |
| 150 | 11 | 139 |
| 217 | 11 | 206 |

Las bases fueron anidadas: cada tamaño mayor retuvo los vectores de la base menor. Por ello, los cambios de Recall reflejan competencia de ranking y no ausencia intencional de conocimiento.

## 14. Metodología de la extensión multidocumento

La extensión añadió el PDF original y ocho reglamentos complementarios. Cada
documento se extrajo y fragmentó por separado con 800/0; después se concatenó
la metadata, no el texto, para crear 765 filas alineadas con FAISS.

La evaluación utilizó 18 preguntas: 16 respondibles y dos sin respuesta. La
relevancia documental se definió por nombre de PDF; la relevancia de chunk
exigió documento, página y evidencia. Por ello se añadieron Document Recall,
Chunk Recall y MRR independientes. QA se ejecutó con Top-10 una sola vez y no
para cada K, mientras la recuperación se calculó para K=1,3,5,10.

Los resultados se escribieron con prefijo `rag_multidocumento_`; el índice
`indice_rag_multidocumento.faiss` es independiente. La metodología completa,
incluidas fórmulas, corpus y limitaciones, se encuentra en
`07_rag_multidocumento.md`.
