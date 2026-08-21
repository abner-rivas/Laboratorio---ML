# Matriz de trazabilidad

La matriz permite auditar las afirmaciones principales sin reconstruir el experimento. La ubicación del notebook se expresa por título de sección o salida visible, porque el número de celda puede cambiar si se edita la estructura.

## Matriz de requisitos de cierre

| Requisito | Implementación | Archivo | Resultado | Evidencia | Estado |
|---|---|---|---|---|---|
| Notebook canónico ejecutado | Desarrollo completo con salidas persistidas | `LaboratorioML.ipynb` | 273 celdas; 129 de código; 144 Markdown; sin errores | Validación `nbformat` y `scripts/validar_entrega.py` | COMPLETO |
| Antecedente histórico diferenciado | Señalización explícita en la entrada del proyecto | `README.md`, `laboratorio_ml_qa.ipynb` | No compite con el notebook canónico | Sección «Ejecución» del README | COMPLETO |
| QA extractivo | Funciones y pipeline BETO/SQAC | `src/funciones_qa.py`, notebook | Configuración final conservada | Salidas y CSV monodocumento | COMPLETO |
| Preparación documental y chunking | Extracción por página y fragmentos trazables | `src/funciones_qa.py`, notebook | 62 páginas y 217 chunks en 800/0 | `data/documento_fuente.pdf`, CSV | COMPLETO |
| Embeddings y FAISS | MPNet normalizado e `IndexFlatIP` | Notebook, `requirements.txt` | 217 vectores de 768 dimensiones | Resultados RAG | COMPLETO |
| Evaluación Top-K | Comparación de K=1, 3, 5 y 10 | Notebook | Top-10 seleccionado con evidencia | CSV y gráficos Top-K | COMPLETO |
| RAG monodocumento | Recuperación y QA sobre el documento oficial | Notebook | Recall@10 y accuracy de 60 % | `results/resultados_qa.csv` | COMPLETO |
| RAG multidocumento | Nueve índices lógicos preservando identidad de fuente | `src/ejecutar_rag_multidocumento.py`, notebook | 9 PDF, 199 páginas y 765 chunks | Artefactos `rag_multidocumento_*` | COMPLETO |
| Trazabilidad de chunks | Metadata alineada uno a uno con el índice | Código y JSONL | 765 registros válidos | `rag_multidocumento_metadata.jsonl` | COMPLETO |
| Análisis de errores | Tipología A--E y observaciones reales | Documentación y CSV | 6 A, 6 B, 1 C, 0 D y 2 E | `rag_multidocumento_errores.csv` | COMPLETO |
| Pruebas ligeras | Cuatro pruebas deterministas sin modelos pesados | `tests/` | Suite rápida desde la raíz | `pytest -q` | COMPLETO |
| Dependencias y reproducibilidad | Instalación, ejecución y validación documentadas | `requirements.txt`, `README.md` | Comandos reproducibles; versiones experimentales registradas sin inventar lock | Configuración JSON y README | COMPLETO |
| Resultados y gráficos | Consolidación sin regenerar experimentos | `results/` | CSV, FAISS y 14 PNG válidos | Validador integral | COMPLETO |
| Informe académico | Reestructuración según el orden oficial del laboratorio | `docs/informe.tex` | Secciones 2--18 en el orden solicitado, sin capítulos ajenos a la guía | Índice, fuente LaTeX y referencias verificadas | COMPLETO |
| Entregable PDF | Compilación desde la fuente LaTeX | `docs/informe.pdf` | 20 páginas de cuerpo, 2 de anexos y 26 físicas con portada e índice | Log limpio, conteo e inspección visual | COMPLETO |
| Privacidad y portabilidad | Eliminación de metadata personal de ejecución y uso de rutas relativas | Notebooks y repositorio | Sin credenciales ni rutas locales necesarias | Búsquedas de cierre | COMPLETO |

## Mapeo de la guía al informe definitivo

| Requisito de la guía | Sección del informe | Evidencia factual principal | Estado |
|---|---|---|---|
| Portada institucional | 1. Portada | `docs/00_datos_generales.md` | COMPLETO |
| Introducción y objetivos | 2--3 | Guía y propósito del notebook canónico | COMPLETO |
| Catorce fundamentos teóricos | 4.1--4.14 | Bibliografía académica y componentes ejecutados | COMPLETO |
| Herramientas y tecnologías | 5 | `requirements.txt`, notebooks y `src/` | COMPLETO |
| Desarrollo de QA | 6.1--6.6 | Implementación básica de `LaboratorioML.ipynb` | COMPLETO |
| Experimentos iniciales | 7.1--7.6 | Contexto del Sistema Solar y salidas ejecutadas | COMPLETO |
| Contexto propio y diez preguntas | 8.1--8.7 | Resumen `qa_basico` y tabla ejecutada del notebook | COMPLETO |
| Comparación de modelos | 9.1--9.9 | 45 registros controlados de `resultados_qa.csv` | COMPLETO |
| Diferentes contextos | 10.1--10.5 | UES, bases de datos y Wikipedia en resultados controlados | COMPLETO |
| QA sobre documento extenso | 11.1--11.6 | PDF de 62 páginas y evaluaciones de fragmentación | COMPLETO |
| Evaluación del overlap | 12.1--12.5 | Configuraciones 300/0, 300/50, 500/0, 500/100, 800/0 y 800/150 | COMPLETO |
| Sistema RAG | 13.1--13.8 | MPNet, FAISS, Top-10 y BETO-SQAC | COMPLETO |
| Extensión multidocumento integrada | 13.9 | Artefactos `rag_multidocumento_*` y notebook de demostración | COMPLETO |
| Proyecto final | 14.1--14.13 | Configuración final y resultados mono/multidocumento | COMPLETO |
| Experimentos adicionales | 15.1--15.5 | MiniLM/MPNet, chunks, overlap, K y tamaños de base | COMPLETO |
| Conclusiones requeridas | 16 | Resultados estructurados y análisis por etapa | COMPLETO |
| Referencias bibliográficas | 17 | `docs/referencias.md` | COMPLETO |
| Anexos | 18 | Preguntas, protocolos, comparación y enlaces de evidencia | COMPLETO |

| Afirmación / resultado | Fuente | Ubicación aproximada | Archivo de apoyo |
|---|---|---|---|
| El modelo base real es BERT/BETO y no RoBERTa-BNE | `LaboratorioML.ipynb` | Secciones 1.5 y 2.3 | Identificador en las celdas de carga |
| Modelos QA evaluados | `LaboratorioML.ipynb` | Sección 8 | `results/resultados_qa.csv` |
| BETO-SQuAD2 (mrm8488) obtuvo 13/15 | Notebook ejecutado | Sección 11, comparación controlada | `results/resultados_qa.csv` |
| BETO-SQuAD2 (MMG) obtuvo 13/15 | Notebook ejecutado | Sección 11, comparación controlada | `results/resultados_qa.csv` |
| BETO-SQAC obtuvo 15/15 | Notebook ejecutado | Sección 11, comparación controlada | `results/resultados_qa.csv` |
| BETO-SQAC fue el QA final | Notebook ejecutado | Sección 11.1 y configuración final | `results/comparacion_modelos.csv` |
| El contexto propio tuvo 308 palabras y diez preguntas | Notebook ejecutado | Sección 7 | Registro `qa_basico` en `results/resultados_qa.csv` |
| El contexto propio obtuvo 10/10 | Notebook ejecutado | Sección 7.4–7.6 | `results/resultados_qa.csv` |
| Documento oficial y alcance monodocumento | `data/README.md` | Documento fuente oficial | `data/documento_fuente.pdf` |
| Documento de 62 páginas y 26 119 palabras | Notebook ejecutado | Sección 12.1–12.2 | `data/README.md` y PDF |
| No se necesitó OCR | Notebook ejecutado | Estadísticas de extracción | `data/README.md` |
| Operaciones de limpieza | `src/funciones_qa.py` | `limpiar_texto_pagina()` | Sección 12 del notebook |
| Metadata de chunks | `src/funciones_qa.py` | `crear_fragmentos_con_metadata()` | Secciones 12 y 13 del notebook |
| Criterio de coincidencia | `src/funciones_qa.py` | `evaluar_coincidencia()` | Tablas con tipo de coincidencia |
| Variantes aceptables explícitas | `src/funciones_qa.py` | `evaluar_respuesta_con_variantes()` | Observaciones en CSV |
| Clasificación de score 0.75/0.40 | `src/funciones_qa.py` | `nivel_confianza()` | Observaciones en CSV |
| Se evaluaron seis configuraciones de chunking | Notebook ejecutado | Sección 12.7 | Resúmenes `chunking` en `results/resultados_qa.csv` |
| 800/0 produjo 217 chunks y 4/10 | Notebook ejecutado | Sección 12.10 | `results/resultados_qa.csv` |
| Overlap no mejoró consistentemente | Notebook ejecutado | Secciones 12.8–12.10 | Comparación de las seis filas de chunking |
| MiniLM produjo vectores de 384 dimensiones | Notebook ejecutado | Sección 13.4 | Registro `rag_minilm` en CSV |
| FAISS usó `IndexFlatIP` | Notebook ejecutado | Sección 13.5 | `requirements.txt` declara `faiss-cpu` |
| Top-K evaluó 1, 3, 5 y 10 | Notebook ejecutado | Sección 14 | Cuatro registros `rag_minilm` en CSV |
| MiniLM Top-10 obtuvo 4/10 y Recall 40 % | Notebook ejecutado | Secciones 14.4 y 15.3 | `results/resultados_qa.csv` |
| Baseline necesitó 2 170 inferencias | Notebook ejecutado | Secciones 15.4–15.5 | Tabla comparativa del notebook |
| RAG Top-10 necesitó 100 inferencias | Notebook ejecutado | Secciones 15.4–15.5 | Tabla comparativa del notebook |
| Reducción de inferencias de 95.4 % | Notebook ejecutado | Sección 15.5 | `baseline_rag_tiempo.png` como apoyo visual |
| Speedup registrado de 167.75x | Notebook ejecutado | Sección 15.5 | `baseline_rag_tiempo.png` |
| Baseline en CPU y RAG posterior en CUDA | Salidas ejecutadas del notebook | Carga del QA documental y configuración RAG | Tablas de dispositivo visibles |
| Cinco errores de recuperación y uno de chunking | Notebook ejecutado | Sección 16.3 | Tabla de análisis de errores |
| MPNet obtuvo 60 % de Recall y accuracy | Notebook ejecutado | Sección 19.2 | Registro `rag_mpnet` en CSV |
| MPNet usa 768 dimensiones | Notebook ejecutado | Sección 19.2 | `results/resultados_qa.csv` |
| MPNet tardó 3.06 veces más en embeddings | Notebook ejecutado | Sección 19.8 | Tabla de comparación de embeddings |
| Bases de 50, 100, 150 y 217 | Notebook ejecutado | Sección 19.3–19.4 | Registros `tamano_base_vectorial` en CSV |
| Todas las bases conservaron evidencia | Notebook ejecutado | Sección 19.3 | Tabla de validación de bases |
| Configuración final 800/0, Top-10, MPNet | Notebook ejecutado | Sección 19.7 | Registro `RAG_CONFIG_FINAL` y CSV |
| Accuracy y Recall finales de 60 % | Notebook ejecutado | Secciones 19.7–19.8 y conclusiones | `results/resultados_qa.csv` |
| El corpus multidocumento tiene 9 PDF y 199 páginas | Notebook ejecutado | Extensión, sección 20.2 | `results/rag_multidocumento_corpus.csv` |
| La base multidocumento tiene 765 vectores de dimensión 768 | Notebook ejecutado | Extensión, secciones 20.3–20.4 | `results/rag_multidocumento_configuracion.json` |
| FAISS y metadata están alineados uno a uno | `src/funciones_qa.py` | `validar_metadata_chunks()` | `results/rag_multidocumento_metadata.jsonl` |
| Se evaluaron 18 preguntas y 9 documentos | Notebook ejecutado | Extensión, sección 20.5 | `data/preguntas_multidocumento.json` |
| Document Accuracy@1 fue 68.75 % | Notebook ejecutado | Extensión, sección 20.6 | `results/rag_multidocumento_metricas.csv` |
| Document Recall@10 fue 93.75 % | Notebook ejecutado | Extensión, sección 20.6 | `results/rag_multidocumento_metricas.csv` |
| Chunk Recall@10 fue 56.25 % | Notebook ejecutado | Extensión, sección 20.6 | `results/rag_multidocumento_metricas.csv` |
| MRR fue 0.7833 para documento y 0.3188 para chunk | Notebook ejecutado | Extensión, sección 20.6 | `results/rag_multidocumento_metricas.csv` |
| QA Accuracy respondible fue 4/16 | Notebook ejecutado | Extensión, sección 20.7 | `results/rag_multidocumento_resultados.csv` |
| Las dos preguntas sin respuesta produjeron spans | Notebook ejecutado | Extensión, sección 20.7 | `results/rag_multidocumento_resultados.csv` |
| Se observaron 6 errores A, 6 B, 1 C y 2 E | Notebook ejecutado | Análisis de errores multidocumento | `results/rag_multidocumento_errores.csv` |
| Dependencias sin versiones fijadas | `requirements.txt` | Archivo completo | `02_metodologia_y_arquitectura.md` |
| Datos institucionales | Solicitud documental | Datos institucionales | `docs/00_datos_generales.md` |

## Figuras disponibles

Los catorce archivos existen en `results/graficos/`. Las rutas siguientes están expresadas desde `docs/`.

| Figura | Qué demuestra | Sección sugerida |
|---|---|---|
| `../results/graficos/comparacion_modelos.png` | Score y tiempo promedio de los tres modelos en el contexto inicial. | Comparación de modelos QA |
| `../results/graficos/accuracy_topk.png` | Accuracy histórica de MiniLM para $K=1,3,5,10$. | Evaluación Top-K |
| `../results/graficos/recall_topk.png` | Recall histórico para los cuatro valores de $K$. | Evaluación Top-K |
| `../results/graficos/tiempo_topk.png` | Aumento del tiempo de consulta al elevar $K$. | Compromiso Recall/coste |
| `../results/graficos/baseline_rag_accuracy.png` | Igualdad de 40 % entre baseline y RAG MiniLM. | Baseline frente a RAG |
| `../results/graficos/baseline_rag_tiempo.png` | Diferencia temporal registrada entre 236.143 s y 1.408 s. | Eficiencia, con advertencia de hardware |
| `../results/graficos/comparacion_embeddings_accuracy.png` | Mejora de accuracy de 40 % a 60 % con MPNet. | Comparación de embeddings |
| `../results/graficos/comparacion_embeddings_recall.png` | Mejora de Recall@10 de 40 % a 60 %. | Comparación de embeddings |
| `../results/graficos/tamano_base_recall.png` | Descenso de Recall al agregar distractores. | Tamaño de base vectorial |
| `../results/graficos/tamano_base_tiempo.png` | Estabilidad aproximada del tiempo con Top-10 fijo. | Tamaño de base vectorial |
| `../results/graficos/rag_multidocumento_document_recall_at_k.png` | Aumento y meseta de Document Recall para K=1,3,5,10. | Extensión multidocumento |
| `../results/graficos/rag_multidocumento_chunk_recall_at_k.png` | Brecha entre documento y evidencia exacta. | Extensión multidocumento |
| `../results/graficos/rag_monodocumento_vs_multidocumento.png` | Comparación descriptiva con advertencia de datasets distintos. | Extensión multidocumento |
| `../results/graficos/rag_multidocumento_tamano_base_vectorial.png` | Crecimiento de 217 a 765 vectores y de 0.64 a 2.24 MiB. | Extensión multidocumento |

No es necesario insertar las diez figuras en el cuerpo. `informe.md` utiliza una selección para evitar repetición. Las restantes pueden trasladarse a anexos o combinarse durante la maquetación LaTeX.

## Tablas disponibles

### `results/comparacion_modelos.csv`

Contiene 60 inferencias de un benchmark histórico: 20 por modelo, distribuidas
en diez preguntas del contexto propio, cinco de Wikipedia y cinco de bases de
datos. Sus agregados son 17/20, 16/20 y 18/20. No es el mismo conjunto
controlado de 45 inferencias utilizado después para seleccionar BETO-SQAC.

### `results/resultados_qa.csv`

Contiene 61 registros de datos además del encabezado:

- 45 detalles de preguntas de la comparación QA;
- un resumen de QA básico;
- seis resúmenes de chunking;
- cuatro resúmenes MiniLM para Top-K;
- un resumen MPNet final;
- cuatro resúmenes de tamaño de base.

Sus columnas abarcan experimento, contexto, modelo, pregunta, respuesta esperada y obtenida, score, tiempo, coincidencia, configuración, accuracy, Recall@K, chunks, overlap, Top-K, dimensión y modelo de embeddings.

### Artefactos multidocumento

- `rag_multidocumento_corpus.csv`: nueve filas documentales y total;
- `rag_multidocumento_recuperacion.csv`: 180 candidatos Top-10;
- `rag_multidocumento_resultados.csv`: 18 respuestas con fuente y ranks;
- `rag_multidocumento_metricas.csv`: 14 métricas de recuperación y QA;
- `rag_multidocumento_errores.csv`: clasificación y observaciones reales;
- `rag_multidocumento_comparacion.csv`: dos filas descriptivas;
- `rag_multidocumento_configuracion.json`: modelos, tiempos y dimensiones;
- `rag_multidocumento_metadata.jsonl`: 765 chunks alineados;
- `indice_rag_multidocumento.faiss`: índice exacto independiente.

## Regla de resolución de discrepancias

Si un texto narrativo antiguo difiere de las tablas finales, se debe aplicar este orden:

1. salidas y DataFrames finales del notebook ejecutado;
2. el CSV específico del experimento (`rag_multidocumento_*` o `resultados_qa.csv`);
3. `results/comparacion_modelos.csv`;
4. código de apoyo y gráficos;
5. narrativa histórica, conservada únicamente para explicar la evolución.

Las referencias bibliográficas verificadas se conservan en
`docs/referencias.md` y en `docs/informe.tex`. No quedan marcas bibliográficas
pendientes en los entregables finales.
