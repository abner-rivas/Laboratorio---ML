# Laboratorio 2 — Question Answering y RAG

Proyecto desarrollado para el Laboratorio 2 de Machine Learning, enfocado en el estudio y la implementación de sistemas de Question Answering mediante modelos Transformer y técnicas de Retrieval-Augmented Generation (RAG). El proyecto utiliza documentación académica de la Universidad de El Salvador como fuente de conocimiento y evalúa el procesamiento de documentos PDF extensos, estrategias de *chunking*, embeddings semánticos, recuperación mediante FAISS, selección Top-K y generación de respuestas con modelos de QA en español.

La solución final utiliza BETO-SQAC como modelo de Question Answering, embeddings multilingües MPNet y un índice vectorial FAISS para recuperar fragmentos relevantes del documento antes de extraer la respuesta. Su desarrollo incluye una evaluación experimental de las decisiones principales del sistema, manteniendo diferenciados los resultados históricos y la configuración final seleccionada.
