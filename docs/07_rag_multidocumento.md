# Extensión experimental: RAG multidocumento

## 1. Definición y alcance

Un RAG multidocumento recupera evidencia desde una colección de fuentes antes
de responder. A diferencia del RAG monodocumento, no basta con localizar una
región pertinente: primero debe competir entre documentos relacionados y
mantener la identidad de la fuente durante todo el pipeline.

Esta extensión se ejecutó después del laboratorio obligatorio y no modifica sus
resultados. El sistema original conserva 1 PDF, 217 chunks, Recall@10 de 60 % y
QA Accuracy de 60 %. La extensión incorpora el PDF original y ocho documentos
institucionales adicionales.

## 2. Diferencias con RAG monodocumento

| Aspecto | Monodocumento | Multidocumento |
|---|---:|---:|
| PDF | 1 | 9 |
| Páginas | 62 | 199 |
| Palabras aproximadas | 26 119 | 94 263 |
| Chunks/vectores | 217 | 765 |
| Dimensión | 768 | 768 |
| Selección documental | No aplica | Necesaria |
| Metadata | Página + chunk | Documento + título + página + chunk |
| Falsos positivos entre fuentes | Limitados | Explícitamente evaluados |

Las métricas de QA son descriptivas porque se utilizaron preguntas distintas.
La comparación controlada mantiene constantes chunking, overlap, embeddings,
índice, Top-K y extractor para observar el efecto de aumentar el corpus.

## 3. Corpus

El corpus contiene exclusivamente normativa de la Universidad de El Salvador:

1. Reglamento de la Gestión Académico-Administrativa;
2. Ley Orgánica;
3. Reglamento General de Arancel Académico;
4. Reglamento de Becas;
5. Reglamento Disciplinario;
6. Reglamento Electoral;
7. Reglamento General de la Ley Orgánica;
8. Reglamento General del Sistema de Escalafón del Personal;
9. Reglamento de Unidades Valorativas y CUM.

PyMuPDF extrajo texto de las 199 páginas; no hubo páginas vacías ni necesidad
de OCR. `results/rag_multidocumento_corpus.csv` registra páginas, caracteres,
palabras y chunks por PDF.

## 4. Problema de selección documental

Los reglamentos comparten entidades y vocabulario: UES, estudiante, personal,
matrícula, beca, sanción, Consejo y CUM. Una consulta puede recuperar un chunk
semánticamente plausible de una fuente equivocada. Por ello se separan:

- **Document Accuracy@1:** el primer candidato pertenece al PDF esperado;
- **Document Recall@K:** al menos un candidato Top-K pertenece al PDF esperado;
- **Chunk Recall@K:** al menos un candidato contiene documento, página y
  evidencia anotados.

La respuesta P1 ilustra el riesgo: BETO devolvió correctamente «una vez al mes»,
pero desde `ley_organica_ues.pdf`, no desde `documento_fuente.pdf`. La
coincidencia textual no elimina el falso positivo documental.

## 5. Importancia de la metadata

Cada chunk contiene como mínimo:

```python
{
    "documento": "reglamento_becas_ues.pdf",
    "titulo_documento": "Reglamento de Becas de la Universidad de El Salvador",
    "pagina": 9,
    "pagina_inicio": 9,
    "pagina_fin": 9,
    "chunk_id": 36,
    "chunk_global_id": 358,
    "vector_posicion": 357,
    "texto": "..."
}
```

`vector_posicion` es cero-based y coincide con la fila agregada a FAISS;
`chunk_global_id` es uno-based para exposición. Las validaciones comprueban que
las 765 posiciones son consecutivas, que ningún chunk carece de procedencia y
que `len(embeddings) == len(metadata_chunks)`.

## 6. Arquitectura utilizada

```text
Pregunta
   ↓
paraphrase-multilingual-mpnet-base-v2
   ↓  vector normalizado de 768 dimensiones
FAISS IndexFlatIP
   ↓
Top-10 con documento, página, chunk y similitud
   ↓
BETO-SQAC sobre cada candidato
   ↓
span de mayor score + fuente exacta
```

Se mantuvieron `chunk_size=800` y `overlap=0`. Para aislar el efecto del aumento
del número de documentos se mantuvieron constantes el tamaño de chunk,
overlap, modelo de embeddings, modelo QA y Top-K seleccionados previamente.

## 7. FAISS y embeddings

MPNet generó 765 vectores normalizados `float32`. La matriz ocupa 2 350 080
bytes (2.24 MiB), frente a 0.64 MiB para 217 vectores monodocumento. La última
ejecución CUDA tardó 6.147 s en embeddings y 0.000254 s en construir el índice;
son tiempos del entorno, no una garantía de rendimiento.

`IndexFlatIP` se eligió porque realiza búsqueda exacta y, con vectores de norma
uno, el producto interno coincide con la similitud coseno. A una escala de 765
vectores no se justificó introducir aproximación y sus hiperparámetros.

## 8. Dataset de evaluación

`data/preguntas_multidocumento.json` contiene 18 preguntas:

- 16 respondibles, con cobertura de los nueve documentos;
- preguntas fáciles, con términos compartidos y potencialmente ambiguas;
- 2 preguntas sin respuesta, sin documento ni página ficticios.

Cada ítem respondible conserva respuesta, variantes aceptables cuando son
necesarias, documento, página física, artículo y evidencia textual verificada.
La evidencia de los 16 ítems cabe en al menos un chunk 800/0.

## 9. Métricas y resultados

| Métrica | K=1 | K=3 | K=5 | K=10 |
|---|---:|---:|---:|---:|
| Document Recall | 68.75 % | 87.50 % | 93.75 % | 93.75 % |
| Chunk Recall | 25.00 % | 31.25 % | 43.75 % | 56.25 % |

Resultados adicionales:

- Document Accuracy@1: 68.75 %;
- MRR documento: 0.7833;
- MRR chunk: 0.3188;
- QA Accuracy respondible: 4/16, 25.00 %;
- QA Accuracy global: 4/18, 22.22 %;
- abstención correcta: 0/2.

El documento correcto apareció en Top-10 para 15 de 16 preguntas. La evidencia
exacta apareció solo para 9 de 16. Por tanto, la selección documental fue mucho
mejor que la localización del fragmento. QA añadió otra pérdida incluso después
de recuperar evidencia.

## 10. Análisis de errores

| Categoría | Casos | Ejemplo real |
|---|---:|---|
| A. Documento incorrecto | 6 | P6 recuperó evidencia de arancel en rank 5, pero el ganador QA procedió de escalafón. |
| B. Documento correcto, chunk incorrecto | 6 | P10 ganó con otro fragmento disciplinario y respondió «amonestación verbal». |
| C. Recuperación correcta, QA incorrecto | 1 | P16 tenía evidencia en rank 1 y BETO extrajo solo «veinte». |
| D. Respuesta parcial | 0 | No apareció un caso bajo la regla adoptada. |
| E. Pregunta sin respuesta | 2 | P17 y P18 produjeron spans pese a no existir evidencia. |
| Sin error integral | 3 | P4, P7 y P13 conservaron respuesta y fuente correctas. |

La clasificación analiza el pipeline completo. Por ello P1 se marca tipo A
aunque su texto sea correcto: la fuente elegida no es la anotada.

## 11. Comparación experimental

| Característica | Monodocumento | Multidocumento |
|---|---:|---:|
| Documentos | 1 | 9 |
| Páginas | 62 | 199 |
| Chunks | 217 | 765 |
| Dimensiones | 768 | 768 |
| Top-K | 10 | 10 |
| Selección documental | No aplica | Sí |
| Metadata documental | Página + chunk | Documento + página + chunk |
| Recall@10 de evidencia | 60 % | 56.25 % |
| QA Accuracy respondible | 60 % | 25 % |

El descenso no debe interpretarse como una comparación pareada: el conjunto
multidocumento incluye preguntas nuevas y más ambiguas. Sí demuestra que el
pipeline enfrenta nuevos niveles de error al crecer el corpus.

## 12. Limitaciones

- El conjunto tiene 18 preguntas y una diferencia de un caso cambia varios
  puntos porcentuales.
- Se ejecutó una medición temporal por configuración.
- El chunking por caracteres no respeta artículos completos.
- No existe reranking ni búsqueda léxica complementaria.
- BETO-SQAC extrae un span por chunk y no integra varios fragmentos.
- No hay detector calibrado de preguntas sin respuesta.
- Los documentos pertenecen a un mismo dominio institucional.

## 13. Conclusiones

El experimento separó tres capacidades que un RAG monodocumento puede ocultar:
selección documental, recuperación de evidencia y extracción. Document
Recall@10 de 93.75 % no se tradujo en Chunk Recall@10 equivalente ni en alta QA
Accuracy. La metadata permitió observar falsos positivos que una evaluación
basada solo en texto habría aceptado.

Como trabajo futuro quedan reranking, índices aproximados para corpus mucho
mayores, modelos generativos, detección explícita de preguntas sin respuesta,
embeddings especializados, filtros por metadata, búsqueda híbrida y chunking
por artículo. Ninguna de esas propuestas se presenta como implementada.
