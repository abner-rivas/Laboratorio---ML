# Hallazgos, limitaciones y trabajo futuro

Este documento distingue conclusiones respaldadas por la ejecución, restricciones del diseño y propuestas que no fueron implementadas. Ningún elemento de trabajo futuro debe presentarse como parte del sistema actual.

## 1. Hallazgos

### 1.1 Un score QA alto no implica una respuesta correcta

El baseline 800/0 obtuvo score QA promedio de 0.942767 y solo 40 % de accuracy. Seis respuestas fueron incorrectas aunque el selector encontrara spans de alta confianza. El score describe la preferencia del extractor dentro del contexto suministrado; no comprueba que ese contexto sea pertinente.

El fenómeno inverso también apareció: respuestas correctas del contexto propio obtuvieron 0.251790 y 0.354680. Por ello, ni un score alto garantiza corrección ni uno bajo demuestra error.

### 1.2 La recuperación fue el cuello de botella histórico

Con MiniLM Top-10, las preguntas con evidencia recuperada fueron [1, 3, 4, 7] y coincidieron exactamente con las respuestas correctas. Cinco fallos se debieron a evidencia ausente del Top-10 y uno a evidencia dividida por chunking. No se observó un fallo exclusivamente QA cuando el extractor recibió evidencia completa.

La igualdad Recall@10 = Accuracy = 40 % tuvo una interpretación específica para esa ejecución: toda evidencia completa recuperada terminó en respuesta correcta. No constituye una identidad general entre ambas métricas.

### 1.3 MPNet mejoró la recuperación

Al sustituir MiniLM por MPNet y mantener fijos PDF, BETO-SQAC, 217 chunks, 800/0, diez preguntas y Top-10:

- Recall@10 aumentó de 40 % a 60 %.
- Accuracy aumentó de 40 % a 60 %.
- El score QA medio aumentó de 0.836432 a 0.861635.

El cambio de 20 puntos en Recall y accuracy respalda que la representación vectorial fue relevante. No demuestra que toda mejora futura dependa solo de los embeddings.

### 1.4 MPNet tuvo mayor coste de preparación

MiniLM generó sus embeddings en 0.536 s y MPNet en 1.642 s dentro de la comparación controlada. La razón fue 3.06. Los tiempos de diez consultas fueron 1.432 s y 1.420 s, respectivamente. El coste adicional se concentró en construir la matriz, no en la consulta registrada.

### 1.5 El overlap no siempre ayudó

El solapamiento agregó una respuesta correcta para 300/50 y 500/100, pero no para 800/150. Siempre aumentó el número de chunks y el tiempo. En la variante final de 800 caracteres, 150 de overlap añadió 50 chunks y 45.897 s sin mejorar el total de respuestas.

Este resultado no niega la función teórica del overlap. Muestra que su beneficio debe comprobarse y que no resolvió la pregunta diseñada cerca del límite.

### 1.6 Más chunks no implicaron mejor QA

Las configuraciones con más ventanas no superaron las cuatro respuestas correctas. El barrido exhaustivo también mostró que comparar contra más contextos podía favorecer falsos positivos de alto score. La cantidad de chunks afecta cobertura, ruido y coste de manera conjunta.

### 1.7 Top-K representó un compromiso

Con MiniLM, aumentar $K$ de 1 a 10 elevó Recall y accuracy de 10 % a 40 %, mientras el tiempo creció de 0.189 s a 1.408 s. Top-5 no mejoró Top-3. El valor final 10 fue seleccionado porque ofreció la mejor calidad dentro de los cuatro valores ejecutados, no porque sea universal.

### 1.8 FAISS redujo las inferencias

El baseline 800/0 ejecutó 2 170 evaluaciones QA. RAG Top-10 ejecutó 100, una reducción de 95.4 %. Esta disminución es independiente de la diferencia de hardware entre fases y constituye la evidencia más sólida de eficiencia arquitectónica.

El speedup temporal registrado fue $167.75\times$, pero mezcla reducción de contextos con un cambio de CPU a CUDA. Se conserva como dato de ejecución y no como estimación aislada del aporte de FAISS.

### 1.9 Los distractores modificaron el ranking

Las bases de 50 y 100 vectores obtuvieron Recall@10 de 70 %; las de 150 y 217, 60 %. Todas contenían los chunks obligatorios. La pérdida de Recall se atribuye a que distractores semánticamente competitivos desplazaron evidencia fuera del Top-10.

### 1.10 Los tiempos de FAISS fueron estables a esta escala

La construcción de los cuatro índices tardó entre 0.000039 y 0.000138 s. Las diez consultas completas variaron 0.010 s entre tamaños. Como BETO siempre recibió Top-10, el coste dominante se mantuvo fijo. Una sola ejecución y 217 vectores no permiten extrapolar el comportamiento a bases grandes.

### 1.11 La selección documental no garantiza recuperar evidencia

La extensión multidocumento alcanzó Document Recall@10 de 93.75 %, pero Chunk
Recall@10 de 56.25 %. En 15 de 16 preguntas respondibles apareció al menos un
chunk del PDF esperado; solo en 9 apareció un chunk que además cubriera la
página y evidencia anotadas. Esta diferencia demuestra que «documento
correcto» y «contexto suficiente» son niveles distintos.

### 1.12 La fuente puede ser incorrecta aunque el texto coincida

En la pregunta sobre la periodicidad del Consejo Académico, BETO extrajo «una
vez al mes», pero desde `ley_organica_ues.pdf` y no desde
`documento_fuente.pdf`. Evaluar únicamente el texto habría ocultado el falso
positivo. La metadata documental convirtió la procedencia en un criterio
auditable.

### 1.13 El RAG multidocumento no se abstuvo

Las dos preguntas sin evidencia recibieron los spans `sta` y `***`. La tasa de
abstención correcta fue 0 %. Un score bajo tampoco resolvió el problema: el
modelo extractivo siempre intenta seleccionar un fragmento si no existe una
regla externa de rechazo.

## 2. Errores observados

El análisis definió siete categorías con precedencia. La tabla diferencia definición y presencia real en MiniLM Top-10.

| Categoría | Definición operativa | Casos observados |
|---|---|---:|
| `error_recuperacion` | La evidencia completa existe en el corpus, pero no aparece en Top-10. | 5 |
| `error_qa` | La evidencia entra al Top-10 y BETO selecciona un span incorrecto. | 0 |
| `respuesta_parcial` | El contexto correcto se recupera, pero el span solo cubre parte de lo esperado. | 0 |
| `ambiguedad` | Varios contextos recuperados sostienen interpretaciones plausibles. | 0 |
| `chunking` | Ningún chunk individual contiene la evidencia completa, aunque aparece en ventanas adyacentes. | 1 |
| `evaluacion` | La respuesta es válida, pero el criterio no la reconoce. | 0 |
| `otro` | Caso sin explicación suficiente en las categorías anteriores. | 0 |

Las categorías con cero casos siguen siendo útiles para auditar futuros experimentos, pero no deben mencionarse como errores ocurridos. La pregunta 10 se clasificó como chunking porque la evidencia quedó repartida entre los chunks 155 y 156.

### 2.1 Errores de la extensión multidocumento

La clasificación multidocumento considera la fuente del candidato QA ganador,
no solo el texto de la respuesta.

| Categoría | Casos observados |
|---|---:|
| Documento incorrecto | 6 |
| Documento correcto, chunk incorrecto | 6 |
| Recuperación correcta, QA incorrecto | 1 |
| Respuesta parcialmente correcta | 0 |
| Pregunta sin respuesta | 2 |
| Sin error integral | 3 |

No se inventó un caso de respuesta parcial. Los ejemplos completos se
conservan en `results/rag_multidocumento_errores.csv`.

## 3. Limitaciones

### 3.1 Conjunto de evaluación pequeño

La fase final utilizó diez preguntas. Un cambio de una sola respuesta equivale a diez puntos porcentuales, por lo que las diferencias son sensibles a pocos casos.

### 3.2 Alcance documental limitado

La parte obligatoria continúa siendo monodocumento. La extensión amplió la
evaluación a nueve PDF institucionales y 199 páginas, pero todos pertenecen al
mismo dominio normativo. No se evaluaron documentos narrativos, tablas
complejas, PDFs escaneados ni colecciones de miles de fuentes.

### 3.3 Dominio regulatorio específico

El documento presenta artículos, enumeraciones y lenguaje normativo. Los resultados no necesariamente se transfieren a otros dominios académicos o técnicos.

### 3.4 Evaluación con variantes y revisión

La normalización y las variantes explícitas evitan penalizar tildes, spans amplios y núcleos semánticos. Sin embargo, algunos casos aceptados dependen de un criterio manual documentado. No se realizó una evaluación humana con múltiples anotadores.

### 3.5 QA extractivo

BETO-SQAC solo selecciona spans. No sintetiza evidencia de varios fragmentos ni explica su respuesta. Si la información está repartida, el modelo no la integra automáticamente.

### 3.6 Dependencia del chunk

La evidencia puede quedar cortada o acompañada por distractores. El tamaño fijo en caracteres no sigue artículos, oraciones ni estructura semántica.

### 3.7 Dependencia del embedding

La entrada a BETO depende del ranking vectorial. MiniLM y MPNet produjeron resultados distintos con el mismo corpus. Otros modelos no fueron evaluados.

### 3.8 Ausencia de reranking

El pipeline utiliza directamente el orden de FAISS y luego el score QA. No existe una etapa adicional que reordene candidatos con un modelo especializado.

### 3.9 Dispositivos distintos en la comparación temporal histórica

El baseline exhaustivo se registró en CPU y RAG posterior en CUDA. Por ello, el speedup temporal no aísla completamente el cambio algorítmico.

### 3.10 Una ejecución temporal por configuración

No se reportan repeticiones, desviaciones ni intervalos. Las diferencias pequeñas pueden incluir calentamiento y ruido del sistema.

### 3.11 Dependencias no fijadas

`requirements.txt` enumera paquetes sin versiones. Tampoco se registraron revisiones concretas de los checkpoints. La reproducción exacta puede variar con actualizaciones.

### 3.12 Comparabilidad de métricas

La extensión añadió MRR documental y de chunk. No se calculó nDCG porque solo
se anotó relevancia binaria. Además, las preguntas monodocumento y
multidocumento son distintas; sus métricas de QA permiten una comparación
descriptiva, no pareada.

## 4. Trabajo futuro

Las propuestas siguientes no fueron implementadas ni evaluadas.

### 4.1 Reranking

Agregar un modelo que reordene los candidatos Top-K antes de QA podría separar evidencia de distractores semánticamente próximos. Requeriría definir tiempos y métricas adicionales.

### 4.2 Búsqueda híbrida BM25 y embeddings

Combinar coincidencia léxica con similitud semántica podría ayudar en artículos, números y términos normativos. Debe compararse contra MPNet bajo las mismas preguntas.

### 4.3 Chunking semántico

Dividir por artículos, párrafos u oraciones podría preservar unidades normativas completas. La comparación debería controlar longitud y cantidad de fragmentos.

### 4.4 Overlap adaptativo

En lugar de repetir una longitud fija, el solapamiento podría activarse cerca de límites sintácticos o estructurales. Su beneficio tendría que medirse frente a 800/0.

### 4.5 Corpus multidocumento a mayor escala

La primera extensión multidocumento ya fue implementada con nueve PDF,
metadata de fuente y 18 preguntas. El trabajo futuro es ampliar a cientos o
miles de documentos, separar validación y prueba y medir índices aproximados
sin asumir que los resultados de 765 vectores escalan linealmente.

### 4.6 Recuperación por artículo

Los encabezados y números de artículo podrían utilizarse para construir unidades o filtros. Esta extensión sería especialmente pertinente en documentos regulatorios.

### 4.7 Filtros y metadata estructural

La extensión ya conserva documento, título, página, chunk, posición vectorial
y texto. Aún podrían extraerse capítulo, artículo y sección para aplicar filtros
previos a FAISS y producir citas normativas más precisas.

### 4.8 Mayor conjunto de evaluación

Se recomienda formular más preguntas, separar validación y prueba, e incluir respuestas imposibles. También sería conveniente evaluar dificultad y procedencia mediante revisión independiente.

### 4.9 nDCG y relevancia graduada

MRR ya se calculó en la extensión: 0.7833 para documento y 0.3188 para chunk.
nDCG requeriría definir grados de relevancia y anotaciones compatibles; no se
debe derivar de forma retroactiva sin ese protocolo.

### 4.10 Interfaz de usuario

Una interfaz podría mostrar pregunta, respuesta, score, artículo y página. Su diseño no debe confundirse con una mejora del modelo.

### 4.11 Evaluación humana

Personas evaluadoras podrían valorar suficiencia, claridad y procedencia de la respuesta. El protocolo debería conservar las salidas originales y documentar desacuerdos.

### 4.12 Repetición temporal controlada

Baseline y RAG deberían ejecutarse en el mismo dispositivo, con calentamiento y varias repeticiones. Así se podría estimar la ganancia temporal atribuible a la reducción de contextos.
