# Registro de decisiones técnicas

Este registro documenta por qué se eligió la configuración final. Cada decisión distingue el problema, las opciones, la evidencia y sus consecuencias. Las cifras proceden del notebook ejecutado y de los CSV consolidados.

## Decisión 1 — Selección del modelo QA

### Problema

Era necesario elegir un extractor en español para las fases de documento largo, chunking y RAG. Una prueba aislada podía favorecer un modelo por el dominio o la formulación.

### Alternativas consideradas

- BETO-SQuAD2 (mrm8488).
- BETO-SQuAD2 (MMG).
- BETO-SQAC (MMG).

### Evidencia experimental

| Modelo | Correctas globales | Exactas | Score medio | Tiempo medio (s) |
|---|---:|---:|---:|---:|
| BETO-SQuAD2 (mrm8488) | 13/15 | 9 | 0.541198 | 0.1215 |
| BETO-SQuAD2 (MMG) | 13/15 | 11 | 0.424900 | 0.1132 |
| BETO-SQAC (MMG) | 15/15 | 9 | 0.691953 | 0.1154 |

El ganador por contexto cambió: BETO-SQuAD2 (MMG) encabezó UES y BETO-SQAC encabezó bases de datos y Wikipedia.

### Decisión tomada

Seleccionar `MMG/bert-base-spanish-wwm-cased-finetuned-sqac`.

### Justificación

El criterio priorizó respuestas correctas antes que exactitud literal, score o latencia. BETO-SQAC fue el único con 15/15 y no dependió de ser el más rápido ni de producir más spans exactos.

### Consecuencia

Todas las comparaciones documentales posteriores usaron el mismo extractor. La elección sigue limitada a tres contextos y quince preguntas.

## Decisión 2 — Selección de `chunk_size`

### Problema

El PDF completo excedía el límite de tokens de BETO. Era necesario escoger una longitud que conservara contexto sin multiplicar excesivamente las ventanas.

### Alternativas consideradas

- 300 caracteres.
- 500 caracteres.
- 800 caracteres.

Cada tamaño se evaluó sin overlap y con una variante solapada.

### Evidencia experimental

Los mejores resultados por tamaño fueron:

| Tamaño | Mejor variante | Correctas | Chunks | Tiempo (s) |
|---:|---|---:|---:|---:|
| 300 | 300/50 | 4/10 | 694 | 350.798 |
| 500 | 500/100 | 4/10 | 434 | 325.274 |
| 800 | 800/0 | 4/10 | 217 | 236.143 |

Entre las variantes con cuatro respuestas correctas, 800/0 tuvo el mayor score medio, 0.942767, y simultáneamente menos chunks y menor tiempo.

### Decisión tomada

Usar `chunk_size=800` caracteres.

### Justificación

El tamaño seleccionado preservó el mejor número de aciertos observado con una base más pequeña. Permitió reducir la competencia y el coste sin disminuir la accuracy frente a las alternativas con cuatro aciertos.

### Consecuencia

El RAG indexó 217 chunks. La decisión dejó pendiente la evidencia que cruza un límite, como ocurrió en la pregunta 10.

## Decisión 3 — Evaluación del overlap

### Problema

Los cortes pueden separar una respuesta de su contexto. El overlap podía conservar continuidad, pero aumentaba duplicación y coste.

### Alternativas consideradas

- 300/0 frente a 300/50.
- 500/0 frente a 500/100.
- 800/0 frente a 800/150.

### Evidencia experimental

| Tamaño | Cambio en correctas | Chunks añadidos | Tiempo añadido (s) | Cambio de score |
|---:|---:|---:|---:|---:|
| 300 | +1 | 115 | 62.650 | -0.019346 |
| 500 | +1 | 87 | 101.469 | +0.021781 |
| 800 | 0 | 50 | 45.897 | -0.044622 |

La pregunta diseñada cerca del límite no fue contestada correctamente por ninguna configuración.

### Decisión tomada

No considerar el overlap como mejora garantizada y compararlo siempre con su variante sin solapamiento.

### Justificación

El efecto fue inconsistente: mejoró dos combinaciones, no mejoró la tercera y siempre incrementó el coste. La evidencia no respaldó conservarlo por principio.

### Consecuencia

La metodología separa la utilidad teórica del overlap de su resultado particular. Las conclusiones no generalizan que el overlap sea inútil.

## Decisión 4 — Selección de Top-K

### Problema

Un $K$ pequeño reduce inferencias, pero puede omitir la evidencia. Un $K$ mayor aumenta la cobertura potencial y el coste de BETO.

### Alternativas consideradas

$K=1$, $3$, $5$ y $10$ sobre el mismo índice MiniLM y las mismas diez preguntas.

### Evidencia experimental

| K | Correctas | Recall@K | Tiempo total (s) | Inferencias QA |
|---:|---:|---:|---:|---:|
| 1 | 1/10 | 10 % | 0.189 | 10 |
| 3 | 3/10 | 30 % | 0.508 | 30 |
| 5 | 3/10 | 30 % | 0.721 | 50 |
| 10 | 4/10 | 40 % | 1.408 | 100 |

### Decisión tomada

Seleccionar Top-10.

### Justificación

Top-10 fue el único valor con cuatro respuestas correctas y 40 % de Recall. El incremento de coste se mantuvo muy por debajo del barrido de 217 chunks por pregunta.

### Consecuencia

Las fases finales procesaron como máximo diez contextos por consulta. La elección se restringe a los valores probados y no demuestra que $K>10$ no pueda cambiar el resultado.

## Decisión 5 — Selección del modelo de embeddings

### Problema

MiniLM reducía el espacio de búsqueda, pero su Recall@10 de 40 % limitaba el máximo de respuestas observadas. Era necesario comprobar si otro embedding recuperaba mejor la evidencia sin modificar BETO ni el chunking.

### Alternativas consideradas

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.

### Evidencia experimental

| Modelo | Dimensión | Recall@10 | Accuracy | Embeddings (s) | Consultas (s) |
|---|---:|---:|---:|---:|---:|
| MiniLM | 384 | 40 % | 40 % | 0.536 | 1.432 |
| MPNet | 768 | 60 % | 60 % | 1.642 | 1.420 |

MPNet mejoró Recall y accuracy en 20 puntos, pero la preparación de embeddings tardó 3.06 veces más.

### Decisión tomada

Seleccionar `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.

### Justificación

El criterio jerárquico priorizó respuestas y recuperación. El mayor coste fue inicial y el tiempo de consulta permaneció similar en la ejecución registrada.

### Consecuencia

La matriz final tiene 217 vectores de 768 dimensiones. La decisión no atribuye la mejora únicamente a la dimensión; compara dos modelos completos bajo condiciones fijas.

## Decisión 6 — Uso de FAISS `IndexFlatIP`

### Problema

Era necesario ordenar los chunks por proximidad semántica y conservar una métrica interpretable.

### Alternativas consideradas

- Producto interno sobre vectores sin normalizar.
- Similitud coseno calculada directamente.
- `IndexFlatIP` con embeddings normalizados.
- Índices aproximados de FAISS.

Los índices aproximados no se evaluaron experimentalmente y no fueron necesarios para 217 vectores.

### Evidencia experimental

Los embeddings de documentos y preguntas se normalizaron con norma L2. En esas condiciones, el producto interno equivale a similitud coseno. Los tiempos de indexación fueron inferiores a 0.001 s para las bases evaluadas.

### Decisión tomada

Usar `faiss.IndexFlatIP` sobre vectores L2 normalizados.

### Justificación

La opción realiza búsqueda exacta, evita parámetros de aproximación y mantiene una relación matemática directa con la similitud coseno.

### Consecuencia

FAISS recupera candidatos, pero no decide la respuesta. El score vectorial y el score QA se mantienen separados.

## Decisión 7 — No usar overlap en la configuración final

### Problema

Después de seleccionar 800 caracteres, debía decidirse si conservar 150 caracteres de overlap para proteger límites.

### Alternativas consideradas

- 800/0.
- 800/150.
- Reabrir la búsqueda con otro overlap no ejecutado.

La tercera alternativa se descartó porque habría requerido un experimento adicional fuera de los resultados disponibles.

### Evidencia experimental

800/0 y 800/150 obtuvieron 4/10. La variante solapada pasó de 217 a 267 chunks, aumentó el tiempo de 236.143 a 282.039 s y redujo el score promedio de 0.942767 a 0.898146. Tampoco resolvió la pregunta de límite.

### Decisión tomada

Fijar `overlap=0`.

### Justificación

En el tamaño elegido, el overlap añadió coste sin mejorar el número de respuestas. Mantener cero conservó la base más pequeña y el mejor compromiso observado.

### Consecuencia

El sistema puede fallar cuando la evidencia cruza ventanas. Esta limitación se registra y se propone chunking semántico o recomposición adyacente como trabajo futuro, sin presentarlos como implementados.

## Decisión 8 — Mantener un único documento en la fase obligatoria

### Problema

Una arquitectura multidocumento ampliaría el conocimiento, pero introduciría variación de fuentes, procedencia y dificultad de recuperación.

### Alternativas consideradas

- Indexar únicamente el reglamento oficial.
- Agregar otros documentos académicos.
- Construir un corpus institucional multidocumento.

### Evidencia experimental

`data/README.md` identifica `documento_fuente.pdf` como el único documento oficial para QA extenso, chunking, embeddings, FAISS y evaluación final. Todas las métricas finales se calcularon sobre ese PDF y diez preguntas anotadas.

### Decisión tomada

Mantener el alcance monodocumento durante la parte obligatoria del laboratorio.

### Justificación

El objetivo era comparar decisiones técnicas bajo una fuente estable. Añadir documentos habría cambiado el tamaño, la distribución de distractores y la interpretación de Recall. En ese momento, el sistema multidocumento no era parte del alcance implementado.

### Consecuencia

Las conclusiones de las secciones 12–19 no deben presentarse como rendimiento
sobre una colección documental. La ampliación se implementó después como una
extensión independiente, con preguntas, metadata, CSV y métricas propias.

## Decisión 9 — Extender sin reemplazar el experimento original

### Problema

Era necesario estudiar selección de fuente sin invalidar la comparación
monodocumento ni atribuir sus métricas a un corpus distinto.

### Alternativas consideradas

- Reemplazar el PDF original por una carpeta de reglamentos.
- Recalcular las preguntas previas sobre el corpus ampliado.
- Mantener la fase original y añadir una extensión posterior controlada.

### Evidencia experimental

Con nueve PDF y 765 vectores, Document Recall@10 fue 93.75 %, Chunk Recall@10
56.25 % y QA Accuracy respondible 25 %. La brecha reveló problemas que el
resultado monodocumento de 60 % no medía.

### Decisión tomada

Conservar intacto el RAG monodocumento y añadir la sección **«Extensión
experimental: RAG multidocumento»** con prefijos de resultados independientes.

### Justificación

Mantener 800/0, MPNet, BETO-SQAC, `IndexFlatIP` y Top-10 aísla el aumento del
corpus. Separar datasets impide presentar una comparación descriptiva como si
fuera pareada.

### Consecuencia

El repositorio contiene dos alcances explícitos: una fase obligatoria de un PDF
y una extensión de nueve PDF. Los resultados negativos se conservan y la
metadata documental pasa a formar parte de la evaluación.

## Resumen de configuración decidida

| Decisión | Valor final |
|---|---|
| QA | BETO-SQAC (MMG) |
| Chunk | 800 caracteres |
| Overlap | 0 |
| Embeddings | MPNet-base multilingüe |
| Dimensión | 768 |
| Índice | FAISS `IndexFlatIP` |
| Top-K | 10 |
| Documento obligatorio | Un reglamento de 62 páginas |
| Extensión | Nueve PDF, 199 páginas y 765 chunks |
