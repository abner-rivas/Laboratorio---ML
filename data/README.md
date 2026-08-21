# Documento fuente oficial

`documento_fuente.pdf` corresponde al **Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador**.

El documento pertenece a la Universidad de El Salvador, contiene 62 páginas y aproximadamente 26 119 palabras. Su texto es extraíble directamente y no requirió reconocimiento óptico de caracteres (OCR).

Este es el único documento utilizado en la parte obligatoria para:

- Question Answering sobre documentos extensos;
- evaluación de fragmentación (*chunking*);
- evaluación de solapamiento (*overlap*);
- generación y comparación de embeddings;
- construcción y búsqueda con FAISS;
- evaluación de Top-K;
- experimentos RAG;
- evaluación final del laboratorio.

Todas las métricas monodocumento reportadas antes de la sección de extensión se
calcularon sobre `documento_fuente.pdf`. El contenido del PDF no se modificó
durante los experimentos.

## Corpus complementario

La extensión experimental multidocumento incorpora, sin sustituir el documento
original, los ocho PDF institucionales de `corpus_complementario/`:

- `ley_organica_ues.pdf`;
- `reglamento_arancel_academico_ues.pdf`;
- `reglamento_becas_ues.pdf`;
- `reglamento_disciplinario_ues.pdf`;
- `reglamento_electoral_ues.pdf`;
- `reglamento_general_ley_organica_ues.pdf`;
- `reglamento_sistema_escalafon_personal_ues.pdf`;
- `reglamento_unidades_valorativas_cum_ues.pdf`.

Los archivos fueron recuperados del commit histórico
`962d28de8bfb76ba877a6194c6171743e4753791` y reubicados en la carpeta
complementaria sin reescribir el historial. Junto con `documento_fuente.pdf`,
forman un corpus de nueve documentos, 199 páginas, 94 263 palabras aproximadas
y 765 chunks con configuración 800/0. Las 199 páginas contienen texto
extraíble; no se aplicó OCR.

`preguntas_multidocumento.json` conserva 18 preguntas con respuesta esperada,
documento, página, artículo y evidencia. Las dos preguntas marcadas con
`sin_respuesta: true` no atribuyen una fuente inexistente.

No pertenecen al corpus instrucciones, rúbricas, informes, documentación
técnica, README ni otros archivos Markdown.
