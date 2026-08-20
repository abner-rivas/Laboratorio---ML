# Documento fuente oficial

`documento_fuente.pdf` corresponde al **Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador**.

El documento pertenece a la Universidad de El Salvador, contiene 62 páginas y aproximadamente 26 119 palabras. Su texto es extraíble directamente y no requirió reconocimiento óptico de caracteres (OCR).

Este es el único documento utilizado oficialmente para:

- Question Answering sobre documentos extensos;
- evaluación de fragmentación (*chunking*);
- evaluación de solapamiento (*overlap*);
- generación y comparación de embeddings;
- construcción y búsqueda con FAISS;
- evaluación de Top-K;
- experimentos RAG;
- evaluación final del laboratorio.

Todas las métricas reportadas en el notebook y en los resultados del laboratorio se calcularon sobre `documento_fuente.pdf`. El contenido del PDF no se modificó durante los experimentos.

---

# Base de Conocimiento "doc_ues_asistente.pdf"

## Descripción General

El archivo `doc_ues_asistente.pdf` contiene la recopilación oficial del marco legal, académico y administrativo de la **Universidad de El Salvador (UES)**. Este documento es la "fuente de la verdad" o corpus principal de conocimiento que el agente debe utilizar para consultar, procesar y responder cualquier pregunta relacionada con la normativa institucional de la universidad.

## Contenido del Documento

El archivo agrupa las siguientes leyes y reglamentos clave de la institución:

1. **Ley Orgánica de la UES:** Define la naturaleza, fines, autonomía y estructura de gobierno de la universidad (Asamblea General Universitaria, Consejo Superior Universitario, Rectoría y Facultades).
2. **Reglamento General de la Ley Orgánica:** Desarrolla las disposiciones organizativas, atribuciones de funcionarios, derechos de los estudiantes y asociaciones estudiantiles.
3. **Reglamento del Sistema de Unidades Valorativas y CUM:** Establece cómo se mide el rendimiento académico, cálculo del Coeficiente de Unidades de Mérito (CUM), requisitos de egreso y el CUM Honorífico.
4. **Reglamento Electoral:** Define los procesos, comités y requisitos para elegir a los representantes de los órganos de gobierno y autoridades (Rector, Decanos, etc.).
5. **Reglamento Disciplinario:** Tipifica las infracciones (graves, menos graves y leves), sanciones aplicables y los procedimientos para deducir responsabilidades.
6. **Reglamento General del Sistema de Escalafón:** Norma las relaciones laborales, el ingreso, evaluación, derechos y deberes del personal académico y administrativo no docente.
7. **Reglamento de Becas:** Regula el otorgamiento de becas de postgrado para el personal y el programa de becas estudiantiles (remuneradas, de excelencia y de estímulo).
8. **Reglamento General de Arancel Académico:** Establece las tarifas por servicios administrativos (certificaciones, auténticas, derechos de grado, etc.).
