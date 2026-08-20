# Laboratorio 2 — Question Answering y RAG

Laboratorio de Machine Learning sobre Question Answering extractivo y
Retrieval-Augmented Generation (RAG) en español. El notebook canónico es
`LaboratorioML.ipynb` y conserva la evolución completa: QA básico, comparación
de modelos, documento extenso, chunking, embeddings, FAISS, RAG monodocumento y
una extensión experimental multidocumento.

## Sistemas evaluados

La parte obligatoria trabaja únicamente con
`data/documento_fuente.pdf` (62 páginas). Su configuración final fue:

- QA: `MMG/bert-base-spanish-wwm-cased-finetuned-sqac` (BETO-SQAC);
- embeddings: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`;
- chunks: 800 caracteres, overlap 0;
- recuperación: FAISS `IndexFlatIP`, Top-10 y vectores normalizados;
- base: 217 vectores de dimensión 768;
- resultado final: QA Accuracy 60 % y Recall@10 60 %.

La sección posterior **«Extensión experimental: RAG multidocumento»** mantiene
esa configuración y amplía el corpus a nueve PDF institucionales de la
Universidad de El Salvador: el documento original y ocho reglamentos
complementarios. No reemplaza ni recalcula las métricas monodocumento.

```text
Pregunta
   ↓
MPNet normalizado
   ↓
FAISS IndexFlatIP
   ↓
Top-10
   ↓
Documento + página + chunk
   ↓
BETO-SQAC
   ↓
Respuesta + score + fuente
```

## Resultados multidocumento ejecutados

El corpus multidocumento contiene 199 páginas, 94 263 palabras aproximadas y
765 chunks/vectores de 768 dimensiones. Las 18 preguntas de evaluación incluyen
16 respondibles distribuidas entre los nueve PDF y dos sin respuesta.

| Métrica | Resultado |
|---|---:|
| Document Accuracy@1 | 68.75 % |
| Document Recall@3 | 87.50 % |
| Document Recall@5 | 93.75 % |
| Document Recall@10 | 93.75 % |
| Chunk Recall@1 | 25.00 % |
| Chunk Recall@3 | 31.25 % |
| Chunk Recall@5 | 43.75 % |
| Chunk Recall@10 | 56.25 % |
| MRR documento | 0.7833 |
| MRR chunk | 0.3188 |
| QA Accuracy sobre respondibles | 25.00 % (4/16) |
| QA Accuracy global | 22.22 % (4/18) |
| Abstención correcta | 0 % (0/2) |

La comparación de QA con el 60 % monodocumento es descriptiva: los conjuntos
de preguntas son distintos. El hallazgo controlado es la separación entre
seleccionar el documento (93.75 % en Top-10), recuperar el chunk con evidencia
(56.25 %) y extraer la respuesta (25 %). El resultado negativo se conserva sin
ajustar scores ni respuestas.

## Estructura

```text
.
├── LaboratorioML.ipynb              # notebook canónico ejecutado
├── data/
│   ├── documento_fuente.pdf          # corpus monodocumento original
│   ├── preguntas_multidocumento.json # 18 preguntas con evidencia
│   └── corpus_complementario/        # ocho PDF institucionales
├── src/
│   ├── funciones_qa.py               # extracción, metadata, RAG y métricas
│   └── ejecutar_rag_multidocumento.py
├── tests/test_funciones_qa.py
├── results/                           # CSV, índice, metadata y gráficos
└── docs/                              # teoría, informe y trazabilidad
```

`laboratorio_ml_qa.ipynb` se conserva como antecedente histórico, pero no es la
implementación final.

## Ejecución

Desde un entorno limpio, en la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/ejecutar_rag_multidocumento.py
```

El script descarga o reutiliza MPNet y BETO-SQAC, valida los nueve PDF, genera
embeddings normalizados, construye un índice independiente y recrea los
artefactos `results/rag_multidocumento_*`. Para ejecutar todo el desarrollo,
abra `LaboratorioML.ipynb` desde la raíz y use **Run All**.

## Artefactos principales

- `results/rag_multidocumento_corpus.csv`: extracción por documento;
- `results/rag_multidocumento_recuperacion.csv`: 180 candidatos Top-10;
- `results/rag_multidocumento_resultados.csv`: respuesta, score y fuente;
- `results/rag_multidocumento_metricas.csv`: Recall, Accuracy y MRR;
- `results/rag_multidocumento_errores.csv`: ejemplos reales por categoría;
- `results/rag_multidocumento_comparacion.csv`: contraste descriptivo;
- `results/indice_rag_multidocumento.faiss` y metadata alineada;
- `results/graficos/rag_*multidocumento*.png`: cuatro gráficos ejecutados.

Los resultados originales permanecen en `results/resultados_qa.csv`,
`results/comparacion_modelos.csv` y los gráficos históricos sin prefijo
multidocumento.
