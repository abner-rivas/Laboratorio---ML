# Corpus documental

El corpus reúne normativa institucional de la Universidad de El Salvador (UES). Se organiza en un documento principal, utilizado en los experimentos controlados del laboratorio, y ocho documentos complementarios destinados a una futura versión multidocumento del asistente UES.

## Documento principal de los experimentos controlados

`documento_fuente.pdf` corresponde al **Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador**.

El documento tiene 62 páginas y aproximadamente 26 119 palabras. Su texto es extraíble directamente, por lo que no requiere OCR. Fue utilizado en los experimentos originales de Question Answering sobre documentos largos y en el cálculo de las métricas de fragmentación (*chunking*), solapamiento (*overlap*), Top-K, modelos de embeddings y RAG con FAISS.

No se modifica el contenido del PDF durante los experimentos. Las métricas históricas del laboratorio corresponden únicamente a `documento_fuente.pdf`; los documentos complementarios incorporados después no forman parte de esos resultados y no deben interpretarse como parte de las evaluaciones anteriores.

## Documentos complementarios del corpus UES

| Archivo | Documento | Área temática | Uso |
|---|---|---|---|
| `reglamento_becas_ues.pdf` | Reglamento de Becas de la Universidad de El Salvador | Becas de posgrado, becas estudiantiles, requisitos, derechos, obligaciones y administración de becas. | Corpus normativo complementario del asistente UES. |
| `reglamento_sistema_escalafon_personal_ues.pdf` | Reglamento General del Sistema de Escalafón del Personal de la Universidad de El Salvador | Carrera, derechos, deberes, evaluación, escalafón y promoción del personal académico y administrativo no docente. | Corpus normativo complementario del asistente UES. |
| `reglamento_arancel_academico_ues.pdf` | Reglamento General de Arancel Académico de la Universidad de El Salvador | Tarifas, certificaciones, constancias, títulos, equivalencias, laboratorios y demás aranceles académicos. | Corpus normativo complementario del asistente UES. |
| `reglamento_electoral_ues.pdf` | Reglamento Electoral de la Universidad de El Salvador | Procesos electorales universitarios, organismos electorales, representantes y autoridades. | Corpus normativo complementario del asistente UES. |
| `ley_organica_ues.pdf` | Ley Orgánica de la Universidad de El Salvador | Organización, autonomía, gobierno, derechos, estructura y funcionamiento general de la UES. | Corpus normativo base del asistente UES. |
| `reglamento_general_ley_organica_ues.pdf` | Reglamento General de la Ley Orgánica de la Universidad de El Salvador | Desarrollo y complementación de las disposiciones de la Ley Orgánica, organización y funcionamiento institucional. | Corpus normativo complementario del asistente UES. |
| `reglamento_disciplinario_ues.pdf` | Reglamento Disciplinario de la Universidad de El Salvador | Infracciones, sanciones, autoridades competentes, procedimientos y recursos disciplinarios. | Corpus normativo complementario del asistente UES. |
| `reglamento_unidades_valorativas_cum_ues.pdf` | Reglamento del Sistema de Unidades Valorativas y de Coeficiente de Unidades de Mérito en la Universidad de El Salvador | Unidades Valorativas, Unidades de Mérito, CUM, rendimiento académico y requisitos relacionados. | Corpus normativo complementario del asistente UES. |

Estos documentos amplían el dominio normativo disponible para una futura recuperación multidocumento. Todavía no forman parte de los experimentos ni de las métricas registradas en el notebook.
