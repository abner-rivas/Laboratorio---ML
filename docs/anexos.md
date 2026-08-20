# Anexos

Los anexos reúnen evidencia secundaria útil para auditoría y maquetación. No reproducen las 273 celdas del notebook ni sustituyen las salidas ejecutadas.

## Anexo A — Preguntas del contexto propio

El contexto propio tuvo 308 palabras y trató Inteligencia Artificial y Machine Learning en sistemas informáticos. BETO-SQuAD2 (mrm8488) respondió correctamente las diez preguntas según la normalización y las revisiones explícitas.

| # | Dificultad | Pregunta | Respuesta esperada | Score |
|---:|---|---|---|---:|
| 1 | Fácil | ¿Qué rama permite a los programas aprender patrones a partir de datos? | Machine Learning | 0.874933 |
| 2 | Intermedia | ¿Para qué tres etapas se separan los datos durante el desarrollo? | entrenamiento, validación y prueba | 0.637630 |
| 3 | Fácil | ¿Qué tipo de aprendizaje utiliza ejemplos etiquetados? | aprendizaje supervisado | 0.787396 |
| 4 | Fácil | ¿Qué puede aprender a detectar un clasificador en ciberseguridad? | correos maliciosos | 0.929076 |
| 5 | Intermedia | ¿Dónde puede ejecutarse la inferencia cuando la latencia y la privacidad son prioritarias? | en dispositivos periféricos mediante edge computing | 0.251790 |
| 6 | Intermedia | ¿Qué puede aparecer si los datos históricos representan de forma desigual a distintos grupos? | sesgo | 0.537380 |
| 7 | Relación | ¿Qué permite reconstruir qué versión del modelo produjo un resultado? | la trazabilidad de los datos, el código y los parámetros | 0.490008 |
| 8 | Intermedia | ¿Para qué se supervisa el modelo en producción? | para detectar degradación causada por cambios en los datos | 0.354680 |
| 9 | Relación | ¿Qué recursos pueden utilizarse para reducir costos computacionales? | modelos compactos y aceleradores especializados | 0.741229 |
| 10 | Difícil | ¿Qué elementos debe combinar un sistema responsable? | rendimiento predictivo, calidad de datos, seguridad, explicabilidad, supervisión humana y evaluación continua | 0.711581 |

La pregunta 5 fue aceptada mediante revisión explícita porque el modelo respondió «en dispositivos periféricos» y omitió «mediante edge computing». La pregunta 6 produjo un span más amplio. Estos registros no se deben ocultar al resumir el 10/10.

## Anexo B — Preguntas del documento extenso

| # | Dificultad | Pregunta | Respuesta esperada | Artículo | Página |
|---:|---|---|---|---|---:|
| 1 | Fácil | ¿Con qué periodicidad sesiona ordinariamente el Consejo Académico? | una vez al mes | 6, continuación | 3 |
| 2 | Fácil | ¿Cuál es el máximo de veces que un estudiante puede cambiar de carrera? | dos veces | 156 | 40 |
| 3 | Fácil | ¿Cuánto dura ordinariamente la calidad de egresado? | tres años académicos | 184 | 45 |
| 4 | Intermedia | ¿Qué unidades integran internamente la Secretaría de Asuntos Académicos? | Administración Académica Central; Unidad Curricular; Unidad de Ingreso Universitario | 13 | 4 |
| 5 | Intermedia | ¿Qué prueba se aplica después del curso de refuerzo académico en línea? | prueba de conocimiento general | 41 | 15 |
| 6 | Intermedia | ¿A qué proceso se somete al estudiante con CUM acumulado menor a siete punto cero? | proceso de asesoría presencial o en línea | 111 | 30 |
| 7 | Intermedia | ¿Quién nombra a los miembros del Tribunal Calificador? | Junta Directiva | 207 | 50 |
| 8 | Difícil | ¿Según qué reglamento se tramita la selección de ingreso de un aspirante a posgrado? | Reglamento General del Sistema de Estudios de Posgrado de la Universidad de El Salvador | 68 | 20 |
| 9 | Difícil | ¿Cuándo entra en vigencia el Reglamento? | ocho días después de su publicación en El Diario Oficial | 258 | 62 |
| 10 | Límite de fragmento | ¿Por cuánto tiempo se amplía automáticamente la calidad de egresado si el plazo vence después de aprobar el trabajo de graduación y antes del acto de graduación? | un año académico más | 184 | 45 |

Las respuestas y páginas se validaron contra `data/documento_fuente.pdf` antes de ejecutar las configuraciones. La pregunta 10 necesitó los chunks adyacentes 155 y 156 en la inspección 800/0.

## Anexo C — Configuraciones de chunking y overlap

| Etiqueta | Chunk | Overlap | Chunks | Correctas | Score medio | Mediana | Tiempo (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 300 | 0 | 579 | 3/10 | 0.935121 | 0.941873 | 288.147 |
| B | 300 | 50 | 694 | 4/10 | 0.915775 | 0.916012 | 350.798 |
| C | 500 | 0 | 347 | 3/10 | 0.917160 | 0.945109 | 223.805 |
| D | 500 | 100 | 434 | 4/10 | 0.938941 | 0.952259 | 325.274 |
| E | 800 | 0 | 217 | 4/10 | 0.942767 | 0.947314 | 236.143 |
| F | 800 | 150 | 267 | 4/10 | 0.898146 | 0.923997 | 282.039 |

Configuración seleccionada: E, 800 caracteres sin overlap.

## Anexo D — Resultados Top-K

### Top-K histórico de recuperación con MiniLM

| K | Correctas | Accuracy | Recall@K | Score QA medio | Tiempo (s) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1/10 | 10 % | 10 % | 0.269381 | 0.189 |
| 3 | 3/10 | 30 % | 30 % | 0.640720 | 0.508 |
| 5 | 3/10 | 30 % | 30 % | 0.702736 | 0.721 |
| 10 | 4/10 | 40 % | 40 % | 0.836432 | 1.408 |

### `top_k` de spans en QA básico

En las tres preguntas del Sistema Solar, el candidato principal se mantuvo estable para `top_k=1`, `3` y `5`. La caída media entre el primer y el último score con cinco candidatos fue 0.6266. Este experimento no corresponde al Top-K de chunks de la tabla anterior.

## Anexo E — Comparación de embeddings

| Modelo | Dimensión | Recall@10 | Correctas | Accuracy | Score QA | Embeddings (s) | Índice (s) | Consultas (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MiniLM-L12 multilingüe | 384 | 40 % | 4/10 | 40 % | 0.836432 | 0.536 | 0.000080 | 1.432 |
| MPNet-base multilingüe | 768 | 60 % | 6/10 | 60 % | 0.861635 | 1.642 | 0.000074 | 1.420 |

MPNet fue seleccionado por la mejora de 20 puntos en Recall y accuracy. Su tiempo de embeddings fue 3.06 veces el de MiniLM.

### Tamaños de base con MPNet

| Vectores | Recall@10 | Correctas | Accuracy | Consultas (s) |
|---:|---:|---:|---:|---:|
| 50 | 70 % | 5/10 | 50 % | 1.408 |
| 100 | 70 % | 6/10 | 60 % | 1.410 |
| 150 | 60 % | 6/10 | 60 % | 1.403 |
| 217 | 60 % | 6/10 | 60 % | 1.412 |

## Anexo F — Análisis de errores

La clasificación siguiente corresponde a MiniLM Top-10, no a MPNet final.

| Pregunta | Evidencia en Top-10 | Correcta | Categoría |
|---:|:---:|:---:|---|
| 1 | Sí | Sí | Sin error |
| 2 | No | No | `error_recuperacion` |
| 3 | Sí | Sí | Sin error |
| 4 | Sí | Sí | Sin error |
| 5 | No | No | `error_recuperacion` |
| 6 | No | No | `error_recuperacion` |
| 7 | Sí | Sí | Sin error |
| 8 | No | No | `error_recuperacion` |
| 9 | No | No | `error_recuperacion` |
| 10 | No | No | `chunking` |

Resumen: cinco errores de recuperación, uno de chunking y cero casos observados de error QA, respuesta parcial, ambigüedad, evaluación u otro.

## Anexo G — Repositorio

Repositorio oficial del laboratorio:

https://github.com/abner-rivas/Laboratorio---ML.git

El repositorio contiene el notebook ejecutado, el PDF fuente, las funciones de apoyo, los CSV, los gráficos y esta documentación. No contiene todavía `docs/informe.tex` ni `docs/informe.pdf`.

## Anexo H — Extensión multidocumento

La extensión usa 18 preguntas: 16 respondibles distribuidas entre los nueve
PDF y dos sin respuesta. La definición completa y la evidencia se conservan en
`data/preguntas_multidocumento.json`; esta tabla resume sus resultados.

| # | Documento esperado | Página | Respuesta predicha | Fuente QA | Categoría |
|---:|---|---:|---|---|---|
| 1 | documento fuente | 3 | una vez al mes | ley orgánica | A |
| 2 | documento fuente | 40 | 157 | documento fuente | B |
| 3 | ley orgánica | 1 | patrimonio propio | ley orgánica | B |
| 4 | ley orgánica | 2 | en lo docente, lo administrativo y lo económico | ley orgánica | Sin error |
| 5 | arancel académico | 2 | ½ punto por cada 20 horas adicionales | escalafón | A |
| 6 | arancel académico | 3 | ½ punto por cada 20 horas adicionales | escalafón | A |
| 7 | becas | 9 | cuatro tipos de beca | becas | Sin error |
| 8 | becas | 10 | gastos institucionales de graduación | unidades valorativas | A |
| 9 | disciplinario | 2 | menos graves | disciplinario | B |
| 10 | disciplinario | 5 | amonestación verbal | disciplinario | B |
| 11 | electoral | 19 | tres | electoral | B |
| 12 | electoral | 13 | 7.0 | becas | A |
| 13 | reglamento general | 7 | el Rector | reglamento general | Sin error |
| 14 | reglamento general | 20 | cuarenta horas semanales | escalafón | A |
| 15 | escalafón | 3 | dos | escalafón | B |
| 16 | unidades valorativas | 2 | veinte | unidades valorativas | C |
| 17 | sin respuesta | — | sta | reglamento general | E |
| 18 | sin respuesta | — | *** | documento fuente | E |

Resultados: Document Accuracy@1 68.75 %, Document Recall@10 93.75 %, Chunk
Recall@10 56.25 %, MRR documental 0.7833, MRR de chunk 0.3188, QA Accuracy
respondible 25 % y abstención correcta 0 %. La tabla no sustituye los scores,
similitudes y ranks completos de los CSV.
