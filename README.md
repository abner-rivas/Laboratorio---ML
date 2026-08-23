# Laboratorio 2 — Question Answering y RAG

## Descripción

Proyecto académico de Question Answering (QA) extractivo en español y
recuperación semántica sobre normativa de la Universidad de El Salvador. El
trabajo conserva dos experimentos independientes:

- el laboratorio obligatorio, sobre un único PDF de 62 páginas;
- una extensión posterior RAG multidocumento, sobre nueve PDF y 199 páginas.

Los notebooks tienen responsabilidades distintas:

- [`laboratorio_ml_qa.ipynb`](laboratorio_ml_qa.ipynb) es el notebook completo,
  canónico y la evidencia oficial de los experimentos;
- [`RAG_UES_Demo.ipynb`](RAG_UES_Demo.ipynb) es el notebook auxiliar limpio
  para explicación y defensa del pipeline final;

## Objetivo

Evaluar de forma separada la capacidad de extraer respuestas, recuperar
evidencia y reducir el espacio sometido a QA. El proyecto prioriza la
trazabilidad: cada resultado final puede relacionarse con el notebook, los CSV,
el código de apoyo y la fuente documental.

## Arquitectura

La parte obligatoria no incorpora el corpus complementario:

```text
documento_fuente.pdf → extracción → chunks → embeddings MiniLM
                      → FAISS Top-3 → BETO-SQAC → evaluación
```

La extensión mantiene cada PDF por separado y añade procedencia:

```text
pregunta → recuperación → documento → página → chunk
         → embeddings MPNet → FAISS Top-10 → BETO-SQAC → respuesta + fuente
```

FAISS usa `IndexFlatIP` con vectores normalizados; en esas condiciones, el
producto interno equivale a similitud coseno. La respuesta sigue siendo
extractiva: el sistema no genera texto libre.

## Estructura del repositorio

```text
.
├── RAG_UES_Demo.ipynb                # demostración final multidocumento
├── laboratorio_ml_qa.ipynb          # notebook principal de experimentos
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

## Configuración Evaluada

El proyecto se divide en dos fases con configuraciones distintas:

| Característica | Monodocumento (laboratorio_ml_qa.ipynb) | Multidocumento (RAG_UES_Demo.ipynb) |
|---|---|---|
| Documentos | 1 | 9 |
| Páginas | 62 | 199 |
| Chunks | 544 (óptimo 300 char) | 765 |
| Embedding | MiniLM (384d) | MPNet (768d) |
| Top-K | 3 | 10 |
| QA | BETO-SQAC | BETO-SQAC |

## Hallazgos Principales (Experimentos Monodocumento)

- **Modelo QA:** BETO-SQAC obtuvo la mayor cantidad de aciertos (18/20) y mayor score medio frente a variantes de BETO-SQuAD2.
- **Tamaño de Chunk:** Fragmentos más pequeños (300 caracteres) superaron en exactitud (70%) a bloques mayores (800 caracteres), debido a que reducen el ruido contextual para el extractor.
- **Overlap:** Incluir solapamiento redujo la precisión e incrementó los tiempos de inferencia significativamente al aumentar el número total de fragmentos en el índice.
- **Top-K:** Al contrario de lo esperado teóricamente, aumentar la cantidad de fragmentos inyectados (Top-10) confundió al modelo QA, desplomando el Accuracy del 50% (Top-1) al 20%. Un valor de K=3 ofreció el mejor balance.

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
jupyter lab laboratorio_ml_qa.ipynb
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

**Catedrático:** Bladimir Diaz Campos
**Institución:** Universidad de El Salvador, Facultad de Ingeniería y
Arquitectura, Escuela de Sistemas Informáticos.
