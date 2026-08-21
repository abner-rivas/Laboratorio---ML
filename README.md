# Laboratorio 2 — Question Answering y RAG

## Descripción

Proyecto académico de Question Answering (QA) extractivo en español y
recuperación semántica sobre normativa de la Universidad de El Salvador. El
trabajo conserva dos experimentos independientes:

- el laboratorio obligatorio, sobre un único PDF de 62 páginas;
- una extensión posterior RAG multidocumento, sobre nueve PDF y 199 páginas.

El notebook canónico y ejecutado es [`LaboratorioML.ipynb`](LaboratorioML.ipynb).
`laboratorio_ml_qa.ipynb` se conserva únicamente como antecedente histórico.

## Objetivo

Evaluar de forma separada la capacidad de extraer respuestas, recuperar
evidencia y reducir el espacio sometido a QA. El proyecto prioriza la
trazabilidad: cada resultado final puede relacionarse con el notebook, los CSV,
el código de apoyo y la fuente documental.

## Arquitectura

La parte obligatoria no incorpora el corpus complementario:

```text
documento_fuente.pdf → extracción → chunks → embeddings MPNet
                      → FAISS Top-10 → BETO-SQAC → evaluación
```

La extensión mantiene cada PDF por separado y añade procedencia:

```text
pregunta → recuperación → documento → página → chunk
         → BETO-SQAC → respuesta + fuente
```

FAISS usa `IndexFlatIP` con vectores normalizados; en esas condiciones, el
producto interno equivale a similitud coseno. La respuesta sigue siendo
extractiva: el sistema no genera texto libre.

## Estructura del repositorio

```text
.
├── LaboratorioML.ipynb              # notebook canónico (273 celdas)
├── laboratorio_ml_qa.ipynb          # antecedente histórico
├── data/
│   ├── documento_fuente.pdf          # única fuente de la parte obligatoria
│   ├── preguntas_multidocumento.json
│   └── corpus_complementario/        # ocho PDF adicionales
├── src/
│   ├── funciones_qa.py
│   └── ejecutar_rag_multidocumento.py
├── tests/                            # cuatro pruebas deterministas y ligeras
├── scripts/validar_entrega.py        # auditoría sin modelos pesados
├── results/                          # CSV, índice FAISS, metadata y gráficos
└── docs/
    ├── informe.md                    # fuente narrativa
    ├── informe.tex                   # informe universitario maquetado
    ├── informe.pdf                   # entregable compilado
    └── checklist_entrega.md
```

## Dataset / corpus

`data/documento_fuente.pdf` es el *Reglamento de la Gestión
Académico-Administrativa de la Universidad de El Salvador*: 62 páginas, 26 119
palabras aproximadas y 217 chunks con la configuración final 800/0.

La extensión agrega ocho reglamentos de `data/corpus_complementario/` sin
concatenarlos ni borrar su identidad. El total ejecutado es de 9 documentos,
199 páginas, 94 263 palabras aproximadas y 765 chunks. La metadata conserva
`documento`, `pagina`, `chunk_id`, identificador global, posición vectorial y
`texto` para cada fragmento.

## Modelos utilizados

- QA final: `MMG/bert-base-spanish-wwm-cased-finetuned-sqac`.
- Embeddings finales:
  `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.
- Baseline histórico de embeddings:
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

Los checkpoints se descargan desde Hugging Face al ejecutar las fases pesadas;
no se almacenan pesos en el repositorio.

## Configuración final

| Componente | Valor |
|---|---|
| Chunk | 800 caracteres |
| Overlap | 0 |
| Top-K | 10 |
| Índice | FAISS `IndexFlatIP` |
| Dimensión MPNet | 768 |
| QA | BETO-SQAC (MMG) |

## Resultados principales

| Experimento monodocumento | Recall@10 | QA Accuracy |
|---|---:|---:|
| RAG MiniLM histórico | 40 % | 40 % |
| RAG MPNet final | **60 %** | **60 % (6/10)** |

El QA exhaustivo y el RAG MiniLM obtuvieron ambos 40 %, pero el RAG redujo las
inferencias QA de 2 170 a 100. El speedup temporal registrado no es una
comparación aislada de arquitectura porque las fases usaron dispositivos
distintos; la reducción de 95.4 % en inferencias sí es estructural.

## RAG multidocumento

| Métrica | Resultado |
|---|---:|
| Document Recall@10 | 93.75 % |
| Chunk Recall@10 | 56.25 % |
| MRR documento | 0.7833 |
| MRR chunk | 0.31875 |
| QA Accuracy respondibles | 25 % (4/16) |
| QA Accuracy global | 22.22 % (4/18) |
| Abstención correcta | 0 % (0/2) |

El hallazgo central es la pérdida encadenada: identificar el documento no
garantiza recuperar el fragmento exacto y recuperar evidencia no garantiza una
extracción correcta. Estos valores se conservan sin cambiar preguntas,
etiquetas ni respuestas.

## Instalación

Se recomienda Python 3.12; la ejecución multidocumento registró Python 3.12.3.
Desde la raíz:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En sistemas donde el ejecutable se llama `python3`, sustituya `python` por
`python3`. Las dependencias no se fijaron a versiones inventadas: los únicos
datos exactos conservados son los que registran el notebook y
`results/rag_multidocumento_configuracion.json`.

## Ejecución

Abra el notebook desde la raíz para que las rutas relativas sean válidas:

```bash
jupyter lab LaboratorioML.ipynb
```

El notebook ya contiene todas las salidas finales. **Run All** descarga modelos
y repite experimentos costosos; no es necesario para revisar la entrega. Para
recrear deliberadamente la extensión multidocumento:

```bash
python src/ejecutar_rag_multidocumento.py
```

Este comando sobrescribe los artefactos `results/rag_multidocumento_*` con una
nueva ejecución y puede variar en tiempos según hardware y versiones.

## Tests

```bash
pytest -q
python -m unittest
```

La suite contiene cuatro pruebas ligeras sobre metadata, ranking, métricas y
preguntas sin respuesta. No descarga modelos.

## Reproducibilidad

La validación completa de artefactos tampoco ejecuta inferencia:

```bash
python scripts/validar_entrega.py
python -m compileall src
git diff --check
```

La fuente de verdad se resuelve en este orden: salidas finales del notebook;
CSV específico del experimento; código de apoyo; documentación narrativa. El
benchmark histórico de 60 filas está en `results/comparacion_modelos.csv`; la
comparación controlada final de 45 inferencias que seleccionó BETO-SQAC está en
`results/resultados_qa.csv`.

## Documentación

- [`docs/informe.pdf`](docs/informe.pdf): entregable final.
- [`docs/informe.tex`](docs/informe.tex): fuente LaTeX reproducible.
- [`docs/informe.md`](docs/informe.md): fuente narrativa extensa.
- [`docs/07_trazabilidad.md`](docs/07_trazabilidad.md): matriz requisito–evidencia.
- [`docs/07_rag_multidocumento.md`](docs/07_rag_multidocumento.md): extensión.
- [`docs/checklist_entrega.md`](docs/checklist_entrega.md): control final.

## Limitaciones

- Diez preguntas finales en el experimento monodocumento y dieciocho en la
  extensión; una respuesta cambia varios puntos porcentuales.
- Una medición temporal por configuración y hardware diferente entre algunas
  fases históricas.
- Dependencias y revisiones de modelos no fijadas con certeza durante los
  experimentos originales.
- Chunking por caracteres, sin reranking ni detector calibrado de abstención.
- Resultados monodocumento y multidocumento descriptivos, no pareados, porque
  usan conjuntos de preguntas distintos.

## Autores

- Josias Abner Rivas Fuentes
- Elmer Edenilson Rosales Molina

**Catedrático:** Vladimir Dias
**Institución:** Universidad de El Salvador, Facultad de Ingeniería y
Arquitectura, Escuela de Sistemas Informáticos.
