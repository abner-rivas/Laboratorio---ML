# Fundamentos teóricos

Este documento presenta los conceptos necesarios para comprender el laboratorio. No contiene las conclusiones cuantitativas del experimento; esas se desarrollan en `05_resultados_y_analisis.md`. La separación evita confundir propiedades generales de una técnica con el comportamiento observado en una muestra concreta.

## 1. Procesamiento de Lenguaje Natural

El Procesamiento de Lenguaje Natural, conocido como NLP por sus siglas en inglés, estudia métodos computacionales para representar, analizar y producir lenguaje humano. El texto debe transformarse en estructuras numéricas antes de que un modelo pueda operar sobre él. Esta transformación permite resolver tareas como clasificación, análisis de sentimiento, extracción de entidades, resumen y preguntas y respuestas.

Question Answering pertenece a este campo porque relaciona una consulta escrita en lenguaje natural con información contenida en un contexto. El sistema debe representar ambas entradas, reconocer su relación y localizar o producir una respuesta según la arquitectura empleada.

## 2. Question Answering

Un sistema de Question Answering recibe al menos dos entradas:

- **Pregunta:** consulta formulada por la persona usuaria.
- **Contexto:** texto que contiene, o debería contener, la evidencia necesaria.

La salida es una respuesta y, según el sistema, información adicional como score, posición o fuente. La calidad de esa salida depende tanto del modelo como de la pertinencia del contexto. Un extractor competente no puede recuperar una respuesta correcta si nunca recibe la evidencia correspondiente.

## 3. Question Answering extractivo

En QA extractivo, la respuesta se selecciona de una secuencia existente en el contexto. El modelo estima qué token tiene mayor probabilidad de iniciar la respuesta y cuál tiene mayor probabilidad de terminarla. El intervalo comprendido entre ambos se denomina **span**.

- **Start token:** token estimado como inicio.
- **End token:** token estimado como final.
- **Span:** secuencia extraída entre las posiciones de inicio y fin.

BETO-SQAC no genera libremente una explicación como un modelo generativo. Su función es seleccionar un span del contexto suministrado. Puede devolver un fragmento más amplio o más corto que la respuesta esperada y, si el contexto es irrelevante, puede seleccionar de todas formas el span que obtenga el mayor score.

## 4. Transformers

La arquitectura Transformer representa cada token considerando su relación con otros tokens de la secuencia. Su mecanismo central es la atención, que asigna pesos a distintas partes de la entrada para construir representaciones dependientes del contexto.

En **self-attention**, una misma secuencia proporciona las consultas, claves y valores usados para calcular relaciones internas. Esto permite que una palabra adopte una representación distinta según las palabras que la rodean. La arquitectura general también incorpora embeddings, información posicional, varias cabezas de atención y redes de transformación por posición.

En QA extractivo basado en BERT se utiliza principalmente el encoder. La pregunta y el contexto se preparan como una entrada conjunta; las representaciones contextualizadas resultantes permiten estimar los extremos del span.

## 5. Tokenización

El modelo no recibe directamente caracteres o palabras completas. El flujo conceptual es:

```text
texto → tokens o subwords → identificadores numéricos → modelo
```

Los tokenizers pueden dividir una palabra en unidades menores llamadas subwords. Esto permite representar vocabulario que no aparece como una unidad completa y reutilizar partes frecuentes entre palabras. Además de los identificadores, el tokenizer agrega tokens especiales, máscaras de atención y la estructura requerida por el modelo.

La longitud máxima se mide en tokens, no en caracteres. Por esa razón, un tamaño de chunk expresado en caracteres debe verificarse empíricamente con el tokenizer si se quiere asegurar que pregunta y contexto caben en el límite.

## 6. Modelos preentrenados

El **pretraining** aprende representaciones generales a partir de grandes colecciones de texto. El **fine-tuning** adapta posteriormente el modelo a una tarea concreta mediante ejemplos supervisados. Los modelos utilizados en el laboratorio ya se encontraban preentrenados y ajustados para Question Answering.

No se entrenó BETO desde cero. El proyecto cargó checkpoints publicados y ejecutó inferencia. La comparación evaluó su comportamiento sobre contextos comunes, sin modificar sus pesos.

## 7. BERT y BETO

BERT es una arquitectura Transformer basada en encoder que produce representaciones contextuales bidireccionales. Para QA extractivo se añade una cabeza que estima logits de inicio y fin sobre la secuencia.

BETO designa modelos BERT orientados al español. Los tres modelos comparados pertenecen a esta familia, pero fueron ajustados con corpus o configuraciones diferentes. Por ello pueden seleccionar spans distintos ante la misma pregunta. El identificador `mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es` corresponde a BERT/BETO y no debe denominarse RoBERTa-BNE.

## 8. Score de Question Answering

El score del pipeline expresa la confianza relativa del modelo en el span seleccionado dentro del contexto recibido. No equivale a accuracy y no garantiza que el contexto sea relevante. Un modelo puede encontrar un span con score alto en un artículo que no responde la pregunta.

En la implementación de apoyo, los scores se clasifican de forma operativa como altos desde 0.75, medios desde 0.40 y bajos por debajo de 0.40. También se ensayó 0.40 como umbral de abstención. Estos valores pertenecen a la lógica del laboratorio y no constituyen umbrales universales.

La corrección se debe evaluar comparando la respuesta con la evidencia esperada. Score y corrección responden preguntas diferentes:

- **Score:** ¿qué tan seguro está el modelo respecto a este span?
- **Corrección:** ¿el span responde realmente la pregunta según la evidencia?

## 9. Top-K en QA

El parámetro `top_k` del pipeline QA permite solicitar varias respuestas candidatas para un mismo contexto. El primer candidato tiene el mayor score y los siguientes muestran alternativas de menor puntuación. Esto facilita inspeccionar límites de span y ambigüedad.

Este `top_k` no debe confundirse con el Top-K de recuperación semántica. En QA se devuelven varios spans de un contexto. En RAG se recuperan varios fragmentos antes de ejecutar el extractor.

## 10. Documentos largos

Los modelos BETO evaluados admiten un máximo de 512 tokens entre pregunta y contexto. Un PDF de decenas de páginas supera ampliamente esa capacidad. Truncarlo eliminaría información y enviarlo completo no es posible para esta arquitectura.

La solución consiste en extraer el texto, dividirlo y conservar la procedencia de cada fragmento. Después se puede ejecutar QA sobre todos los chunks o recuperar primero un subconjunto pertinente.

## 11. Chunking

Chunking es la división del documento en ventanas limitadas. El parámetro `chunk_size` controla la longitud máxima de cada ventana. En el laboratorio la unidad fue el carácter.

Los chunks pequeños pueden localizar secciones específicas y reducir tokens por inferencia, pero incrementan la cantidad total y pueden cortar evidencia. Los chunks grandes conservan más contexto y reducen la cantidad de ventanas, aunque también incorporan más información potencialmente irrelevante.

## 12. Overlap

El overlap repite una parte del final de un chunk al inicio del siguiente. Si $L$ es el tamaño y $O$ el solapamiento, el paso entre ventanas es:

$$
P = L - O.
$$

Teóricamente, el overlap puede conservar relaciones cercanas a un límite. A cambio, aumenta el número de chunks, duplica contenido y eleva el coste de evaluación. Esta propiedad general no determina por sí sola si mejorará un experimento; su efecto debe medirse.

## 13. Embeddings

Un embedding representa texto mediante un vector numérico. El objetivo es codificar propiedades semánticas en una forma que pueda compararse matemáticamente. Un documento dividido produce un vector por chunk, y una pregunta produce otro vector en el mismo espacio.

```text
texto → modelo de embeddings → vector
```

La dimensión depende del modelo. Una dimensión mayor describe el tamaño de la representación, pero no garantiza por sí sola mejor recuperación.

## 14. Espacio vectorial

En un espacio vectorial semántico se espera que textos relacionados queden relativamente próximos. La cercanía no representa igualdad literal: dos fragmentos pueden usar vocabulario diferente y conservar una relación conceptual. De forma inversa, distractores con términos similares pueden ocupar posiciones competitivas aunque no contengan la respuesta.

## 15. Similitud coseno

La similitud coseno mide el ángulo entre dos vectores:

$$
\cos(\theta) =
\frac{\mathbf{a}\cdot\mathbf{b}}
{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}.
$$

Un valor mayor indica mayor alineación entre las representaciones. La métrica considera la dirección y reduce el efecto de la magnitud, por lo que es habitual normalizar los embeddings antes de compararlos.

## 16. Producto interno y normalización

Si $\hat{a}$ y $\hat{b}$ tienen norma L2 igual a uno, entonces:

$$
\hat{a}^{\mathsf{T}}\hat{b} = \cos(\hat{a},\hat{b}).
$$

Por esa equivalencia, un índice de producto interno puede ejecutar búsqueda por similitud coseno cuando documentos y preguntas se normalizan previamente. Esta fue la base para usar `IndexFlatIP`.

## 17. FAISS

FAISS es una biblioteca para indexar vectores y recuperar vecinos según una métrica. El índice organiza la búsqueda, pero no interpreta la respuesta ni genera texto. `IndexFlatIP` conserva todos los vectores y calcula producto interno exacto contra la consulta.

En las bases pequeñas del laboratorio, la búsqueda exacta permitió evitar aproximaciones y mantener una correspondencia directa entre score vectorial y ranking.

## 18. Recuperación semántica

La recuperación semántica sigue este flujo:

```text
pregunta → embedding → búsqueda vectorial → fragmentos relevantes
```

La etapa decide qué contextos recibirá el extractor. Su error principal ocurre cuando la evidencia existe en la base pero queda fuera de los primeros $K$ resultados. La recuperación se evalúa de forma independiente de la respuesta final.

## 19. Recall@K

Recall@K mide la proporción de preguntas cuya evidencia aparece en al menos uno de los $K$ fragmentos recuperados:

$$
\operatorname{Recall@K} =
\frac{\text{preguntas con evidencia en Top-K}}
{\text{total de preguntas}}.
$$

Recall@K no es accuracy QA. La primera métrica comprueba disponibilidad de evidencia; la segunda comprueba la respuesta final. Puede existir evidencia recuperada y aun así fallar la extracción. También puede aparecer una respuesta léxicamente válida desde una procedencia distinta de la anotada.

## 20. Retrieval-Augmented Generation

RAG combina una etapa de recuperación con una etapa que responde usando el contexto recuperado. El nombre general incluye *generation*, pero la implementación del laboratorio no usa generación libre. Se conserva la denominación RAG del proyecto para una arquitectura compuesta por:

```text
recuperación semántica + QA extractivo
```

FAISS limita los contextos y BETO-SQAC extrae el span final. Por ello, las respuestas permanecen condicionadas por el texto recuperado.

## 21. Pipeline completo

La preparación del conocimiento sigue este flujo:

```text
PDF
 ↓
extracción con PyMuPDF
 ↓
limpieza conservadora
 ↓
chunking con metadata
 ↓
embeddings normalizados
 ↓
índice FAISS
```

La consulta sigue este segundo flujo:

```text
pregunta
 ↓
embedding normalizado
 ↓
Top-K de FAISS
 ↓
BETO-SQAC sobre los chunks
 ↓
span con mayor score QA
```

Ambos flujos deben conservarse separados para identificar si un fallo procede de extracción del PDF, fragmentación, recuperación o Question Answering.

## Referencias verificadas

La arquitectura Transformer se sustenta en Vaswani et al. (2017); BERT, en
Devlin et al. (2019); y BETO, en Cañete et al. (2020). La representación de
oraciones y el modelo MPNet se documentan en Reimers y Gurevych (2019) y Song
et al. (2020), respectivamente. FAISS se apoya en Johnson, Douze y Jégou
(2019), y la denominación RAG en Lewis et al. (2020). También se verificaron la
documentación oficial de QA de Hugging Face, las fichas de los dos checkpoints
finales y la guía de extracción de PyMuPDF. Las entradas completas y sus
enlaces están en `referencias.md` y en la bibliografía de `informe.tex`.
