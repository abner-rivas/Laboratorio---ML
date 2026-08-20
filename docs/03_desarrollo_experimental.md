# Desarrollo experimental

Este documento narra la evolución del laboratorio. Las cifras se conservan para explicar por qué se abrió cada fase y cómo cambiaron las decisiones. Las tablas de síntesis y las figuras se encuentran en `05_resultados_y_analisis.md`.

## Fase 1. QA básico

La primera fase buscó comprobar que un modelo QA en español podía cargar, tokenizar una pregunta y extraer un span de un contexto breve. El modelo base fue `mrm8488/bert-base-spanish-wwm-cased-finetuned-spa-squad2-es`.

Las pruebas confirmaron que el pipeline devolvía `answer`, `score`, `start` y `end`. En un contexto sobre la Universidad de El Salvador, la pregunta por el año de fundación devolvió «1841» con score 0.986. En ejemplos posteriores se observó que el extractor no construía explicaciones: elegía una secuencia existente.

Esta fase también permitió corregir una identificación antigua. El checkpoint ejecutado pertenecía a BERT/BETO y no a RoBERTa-BNE. La documentación posterior adoptó el identificador real.

## Fase 2. Contexto propio

El siguiente paso fue probar un contexto académico de 308 palabras sobre Inteligencia Artificial y Machine Learning en sistemas informáticos. Se formularon diez preguntas con distintos niveles: fáciles, intermedias, de relación y una difícil. Todas tenían evidencia explícita en el texto.

BETO-SQuAD2 (mrm8488) obtuvo 10/10 según la evaluación normalizada y las revisiones declaradas. El score medio fue 0.631570 y el tiempo total 1.7577 s. Sin embargo, dos casos revelaron límites importantes:

- La pregunta 5 obtuvo score 0.251790 y respondió «en dispositivos periféricos», omitiendo «mediante edge computing». Se aceptó como suficiente para el lugar solicitado y quedó marcada como revisión.
- La pregunta 6 devolvió «sesgo y producir decisiones injustas», un span más amplio que el núcleo esperado.

Primero se había usado la confianza como indicio intuitivo de calidad. Esta actividad mostró que una respuesta correcta podía tener score bajo y que los límites del span requerían evaluación explícita.

## Fase 3. Score y `top_k` de respuestas

Se compararon `top_k=1`, `3` y `5` sobre tres preguntas del Sistema Solar. El candidato de rango 1 se mantuvo estable en 3/3 preguntas. Con cinco respuestas, la caída media entre la primera y la última puntuación fue 0.6266. De 18 alternativas, 17 se solapaban con el mejor span.

El hallazgo fue que aumentar `top_k` no corregía por sí solo la mejor respuesta. Las alternativas servían para inspeccionar spans más amplios o reducidos, pero la mayoría era redundante.

También se probaron preguntas sin evidencia. En el contexto de Python, «Guido van Rossum» y «1991» obtuvieron 0.9700 y 0.8396. Las preguntas por Francia y Java, ausentes del texto, produjeron tokens especiales o información no pertinente con 0.0013 y 0.0395. Esto motivó una regla experimental de abstención en 0.40, entendida como alerta de revisión y no como garantía de corrección.

## Fase 4. Comparación inicial de modelos

La comparación controlada comenzó con un contexto sobre la Universidad de El Salvador y cinco preguntas. Se separó el tiempo de carga, se calentó cada modelo y se midió únicamente inferencia en CPU.

| Modelo | Correctas | Exactas | Score promedio | Tiempo medio (s) |
|---|---:|---:|---:|---:|
| BETO-SQuAD2 (mrm8488) | 4/5 | 3 | 0.639995 | 0.0620 |
| BETO-SQuAD2 (MMG) | 5/5 | 5 | 0.536869 | 0.0630 |
| BETO-SQAC (MMG) | 5/5 | 2 | 0.615832 | 0.0612 |

BETO-SQuAD2 (MMG) fue recomendado para ese contexto porque combinó cinco correctas y cinco spans exactos. El resultado no se trató como selección global: se decidió repetir la prueba en otros dominios.

## Fase 5. Segundo contexto

El segundo contexto trató bases de datos y SGBD, tuvo 323 palabras y cinco preguntas. Los resultados cambiaron el ranking:

| Modelo | Correctas | Score promedio | Tiempo medio (s) |
|---|---:|---:|---:|
| BETO-SQuAD2 (mrm8488) | 4/5 | 0.436674 | 0.1833 |
| BETO-SQuAD2 (MMG) | 4/5 | 0.329666 | 0.1774 |
| BETO-SQAC (MMG) | 5/5 | 0.778458 | 0.1818 |

El primer modelo devolvió «un sistema de [UNK]» en la definición de SGBD. El segundo extrajo solo «tablas formadas por filas» para el modelo relacional. BETO-SQAC respondió las cinco y quedó mejor clasificado en este dominio.

Esta fase invalidó la idea de que el ganador de un contexto sería necesariamente el mejor en otro. El dominio y la formulación cambiaron respuestas, scores y tiempos.

## Fase 6. Wikipedia

Se usó un extracto adaptado y autocontenido de Wikipedia en español sobre aprendizaje automático, con 197 palabras y cinco preguntas. No se dependió de Internet durante la ejecución.

| Modelo | Correctas | Score promedio | Tiempo medio (s) |
|---|---:|---:|---:|
| BETO-SQuAD2 (mrm8488) | 5/5 | 0.546924 | 0.1192 |
| BETO-SQuAD2 (MMG) | 4/5 | 0.408166 | 0.0992 |
| BETO-SQAC (MMG) | 5/5 | 0.681568 | 0.1033 |

BETO-SQuAD2 (MMG) falló la pregunta sobre aprendizaje por refuerzo al devolver únicamente «retroalimentación». BETO-SQAC y mrm8488 obtuvieron 5/5, pero BETO-SQAC tuvo mayor score promedio.

Al integrar los tres contextos, los resultados fueron 13/15 para mrm8488, 13/15 para BETO-SQuAD2 (MMG) y 15/15 para BETO-SQAC. Esto motivó seleccionar BETO-SQAC para el documento largo.

## Fase 7. Documento extenso

El experimento documental utilizó el *Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador*. PyMuPDF extrajo texto de sus 62 páginas sin OCR. La limpieza redujo 177 390 caracteres crudos a 173 419 y conservó aproximadamente 26 119 palabras.

Se formularon diez preguntas con evidencia anotada. Las páginas objetivo abarcaron desde la 3 hasta la 62 e incluyeron distintos niveles de dificultad. La pregunta 10 consultó la ampliación automática de la calidad de egresado y se diseñó para inspeccionar evidencia próxima a límites de fragmentos.

La limitación de 512 tokens impidió enviar el PDF completo a BETO. Esto condujo a dividir el texto y conservar metadata de página y offsets.

## Fase 8. Baseline exhaustivo

La configuración base fue 500 caracteres sin overlap. Produjo 347 chunks y procesó todos ellos para cada pregunta. Alcanzó 3/10, score medio 0.917160 y 223.805 s.

Se observó una contradicción aparente: los scores eran altos aunque muchas respuestas fueran incorrectas. El selector elegía el máximo entre cientos de contextos, por lo que un span seguro de un artículo irrelevante podía superar la evidencia correcta.

Este resultado motivó dos líneas: comparar tamaños y solapamientos, y posteriormente restringir los contextos mediante recuperación semántica.

## Fase 9. Chunking y overlap

Se compararon 300/0, 300/50, 500/0, 500/100, 800/0 y 800/150. Los resultados oscilaron entre tres y cuatro correctas. El overlap agregó un acierto en 300/50 y 500/100, pero no en 800/150; siempre aumentó chunks y tiempo.

La pregunta de límite no fue resuelta por ninguna variante. En 300/50, el candidato llegó a la página 45, pero extrajo «tres años» en vez de «un año académico más». Las demás configuraciones eligieron principalmente «dos años» en otro contexto.

Entre las variantes con cuatro correctas, 800/0 tuvo 217 chunks, el mayor score medio, el menor tiempo y la menor base. Se seleccionó para RAG. Esta decisión no significó que el overlap carezca de utilidad teórica, sino que no produjo un beneficio consistente en la muestra.

## Fase 10. Embeddings y FAISS

El primer recuperador usó `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Generó 217 embeddings de 384 dimensiones, normalizados con norma L2. `faiss.IndexFlatIP` almacenó los vectores y aplicó producto interno equivalente a similitud coseno.

La matriz se construyó una vez y se reutilizó. FAISS devolvió chunks con rank, similitud, identificador y páginas. BETO-SQAC respondió sobre ese subconjunto sin combinar score vectorial y score QA.

El primer ensayo con Top-3 obtuvo 3/10. La recuperación redujo el espacio, pero aún era necesario medir si un $K$ mayor incorporaba evidencia.

## Fase 11. Top-K de recuperación

Se evaluaron $K=1,3,5,10$ con los mismos chunks, índice y preguntas.

| K | Correctas | Recall@K | Tiempo total (s) |
|---:|---:|---:|---:|
| 1 | 1/10 | 10 % | 0.189 |
| 3 | 3/10 | 30 % | 0.508 |
| 5 | 3/10 | 30 % | 0.721 |
| 10 | 4/10 | 40 % | 1.408 |

Aumentar $K$ de 1 a 10 mejoró correctas y Recall, pero elevó el tiempo. Top-5 no superó Top-3. Top-10 fue seleccionado porque fue el único con cuatro respuestas correctas.

## Fase 12. Baseline frente a RAG

La comparación histórica usó la configuración común 800/0 y BETO-SQAC:

- Baseline: 217 chunks por pregunta, 4/10, 2 170 inferencias y 236.143 s.
- RAG MiniLM Top-10: diez chunks por pregunta, 4/10, 100 inferencias y 1.408 s.

RAG no mejoró la accuracy en esa etapa, pero evitó 2 070 inferencias, una reducción de 95.4 %. El speedup registrado fue $167.75\times$. La interpretación temporal quedó limitada porque el baseline fue ejecutado en CPU y la fase RAG posterior registró CUDA.

## Fase 13. Análisis de errores

Se definió una precedencia para clasificar fallos: recuperación, QA, respuesta parcial, ambigüedad, chunking, evaluación y otro. En MiniLM Top-10 aparecieron cinco errores de recuperación y uno de chunking. No aparecieron errores QA ni las demás categorías.

Las preguntas con evidencia recuperada fueron [1, 3, 4, 7], exactamente las mismas que resultaron correctas. En esta ejecución, BETO respondió correctamente siempre que recibió un chunk con evidencia completa. El principal cuello de botella quedó localizado antes del extractor.

## Fase 14. Modelo alternativo de embeddings

Se comparó MiniLM con `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` manteniendo BETO-SQAC, 217 chunks, 800/0, diez preguntas y Top-10.

MiniLM obtuvo 40 % de Recall y accuracy. MPNet obtuvo 60 % en ambas. El tiempo de consultas fue 1.432 s frente a 1.420 s, mientras que MPNet tardó 1.642 s en generar embeddings contra 0.536 s de MiniLM, una razón de 3.06.

La mejora de 20 puntos en recuperación y respuesta justificó seleccionar MPNet, aun con mayor coste de preparación.

## Fase 15. Tamaño de la base vectorial

Se construyeron bases anidadas de 50, 100, 150 y 217 vectores, todas con evidencia de 10/10 preguntas. El resto se completó con distractores usando semilla 42.

| Vectores | Recall@10 | Accuracy | Tiempo de consultas (s) |
|---:|---:|---:|---:|
| 50 | 70 % | 50 % | 1.408 |
| 100 | 70 % | 60 % | 1.410 |
| 150 | 60 % | 60 % | 1.403 |
| 217 | 60 % | 60 % | 1.412 |

Al aumentar distractores, Recall disminuyó de 70 % a 60 %, aunque la evidencia permanecía en la base. Esto mostró competencia de ranking. Los tiempos variaron solo 0.010 s porque Top-10 mantuvo constante el número de contextos enviados a BETO.

## Fase final

La configuración registrada fue:

| Componente | Valor |
|---|---|
| QA | `MMG/bert-base-spanish-wwm-cased-finetuned-sqac` |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Chunk | 800 caracteres |
| Overlap | 0 |
| Top-K | 10 |
| FAISS | `IndexFlatIP` |
| Base completa | 217 vectores |
| Accuracy | 60 % |
| Recall@10 | 60 % |

La evolución experimental permitió sustituir dos hipótesis iniciales. Primero, un score alto no garantizaba corrección. Segundo, procesar más contextos no garantizaba una mejor respuesta. La mejora final procedió del modelo de recuperación, mientras que FAISS aportó principalmente reducción del espacio sometido a QA.

## Extensión posterior. RAG multidocumento

La extensión recuperó ocho PDF institucionales del historial Git y los añadió
al documento original sin alterar las fases anteriores. PyMuPDF extrajo 199
páginas y se construyeron 765 chunks 800/0 con documento, título, página,
identificadores local/global y posición vectorial.

Se diseñaron 18 preguntas verificadas y se ejecutó el mismo MPNet,
`IndexFlatIP`, Top-10 y BETO-SQAC. Document Recall@10 fue 93.75 %, Chunk
Recall@10 56.25 % y QA Accuracy respondible 25 %. Las dos preguntas sin
evidencia recibieron spans. El análisis encontró seis falsos positivos
documentales, seis ganadores de chunk incorrectos, un error QA puro y dos
errores de ausencia de respuesta.

El resultado no reemplazó el 60 % monodocumento. Mostró una nueva evolución:

```text
fuente estable
→ corpus relacionado
→ selección documental alta
→ localización de evidencia menor
→ extracción QA todavía menor
→ prioridad futura: reranking y abstención
```
