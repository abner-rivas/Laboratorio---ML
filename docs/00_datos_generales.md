# Datos generales

| Campo | Información |
|---|---|
| Universidad | Universidad de El Salvador |
| Facultad | Facultad de Ingeniería y Arquitectura |
| Escuela | Escuela de Sistemas Informáticos |
| Curso | Curso de Especialización en Machine Learning |
| Laboratorio | Laboratorio 2 |
| Fecha | 14 de agosto de 2026 |

## Estudiantes

- Josias Abner Rivas Fuentes
- Elmer Edenilson Rosales Molina

## Catedrático

Vladimir Dias

## Fecha

14 de agosto de 2026

## Repositorio

https://github.com/abner-rivas/Laboratorio---ML.git

## Título recomendado

**Laboratorio 2: Question Answering y Retrieval-Augmented Generation sobre documentación académica de la Universidad de El Salvador**

## Resumen propuesto

El Laboratorio 2 estudió sistemas de Question Answering extractivo en español y su integración con recuperación semántica sobre un documento académico-administrativo de la Universidad de El Salvador. El desarrollo comenzó con ejemplos controlados para analizar respuestas, scores y candidatos `top_k`. Posteriormente se compararon tres modelos BETO en tres contextos; BETO-SQAC (MMG) obtuvo 15 respuestas correctas de 15 y fue seleccionado como extractor. El documento final de evaluación fue el *Reglamento de la Gestión Académico-Administrativa de la Universidad de El Salvador*, compuesto por 62 páginas. Se evaluaron seis configuraciones de chunking y overlap. La variante de 800 caracteres sin solapamiento produjo 217 fragmentos y fue elegida por su relación entre aciertos, coste y cantidad de chunks. El RAG histórico con MiniLM y Top-10 alcanzó 40 % de accuracy y Recall@10, pero redujo las inferencias QA de 2 170 a 100. La comparación posterior seleccionó embeddings MPNet multilingües, que elevaron accuracy y Recall@10 a 60 %. La configuración final combina BETO-SQAC, MPNet, FAISS `IndexFlatIP`, chunks de 800 caracteres, overlap cero y Top-10. Las conclusiones se restringen a un documento, diez preguntas finales y una ejecución temporal por configuración.

## Notas para la portada

- Vladimir Dias debe aparecer únicamente como catedrático.
- No se deben agregar carnets porque no están disponibles en las fuentes autorizadas.
- La portada final deberá conservar los nombres institucionales exactamente como aparecen en este archivo.
- El repositorio puede presentarse como enlace, sin sustituirlo por una URL abreviada.

