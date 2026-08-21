# Guía breve para la defensa técnica

Duración objetivo: 7 minutos. La demostración utiliza las salidas existentes y
no requiere descargar modelos durante la exposición.

1. **Problema y objetivo (45 s).** Explicar que QA extractivo selecciona un span
   y que RAG reduce los chunks sometidos al extractor.
2. **Arquitectura (45 s).** Mostrar los dos flujos del `README.md` y aclarar que
   el laboratorio obligatorio usa un solo PDF.
3. **Evolución experimental (90 s).** Abrir las secciones de comparación QA,
   chunking, Top-K y embeddings de `LaboratorioML.ipynb`.
4. **Resultado monodocumento (60 s).** Presentar BETO-SQAC, MPNet, 800/0,
   Top-10, Recall@10 de 60 % y accuracy de 60 %.
5. **Extensión multidocumento (90 s).** Presentar 9 documentos, 199 páginas,
   765 chunks y la trazabilidad documento--página--chunk.
6. **Hallazgo central (60 s).** Explicar la caída 93.75 % → 56.25 % → 25 % y
   relacionarla con los errores A--E.
7. **Cierre (30 s).** Señalar limitaciones, reproducibilidad y evidencia.

Antes de la exposición, desde la raíz:

```bash
source .venv/bin/activate
pytest -q
python scripts/validar_entrega.py
jupyter lab LaboratorioML.ipynb
```

Si el entorno no tiene las dependencias instaladas, ejecutar primero
`python -m pip install -r requirements.txt`. No usar **Run All** durante una
defensa salvo que los modelos ya estén descargados y exista tiempo suficiente.

Preguntas previsibles:

- **¿Por qué inner product?** Los embeddings están normalizados; por ello el
  producto interno induce el mismo ranking que la similitud coseno.
- **¿Por qué overlap 0?** En 800 caracteres el solapamiento no añadió aciertos,
  aumentó chunks y elevó el tiempo en el experimento ejecutado.
- **¿Por qué MPNet?** Elevó Recall@10 y accuracy de 40 % a 60 % frente a MiniLM
  sobre los mismos 217 chunks.
- **¿Por qué no comparar directamente mono y multidocumento?** Cambian preguntas,
  fuentes y ambigüedad; la comparación es descriptiva, no pareada.
- **¿Por qué falla QA si recupera el documento?** El documento correcto puede
  aparecer sin que el chunk exacto alcance el Top-K; aun con evidencia, el
  extractor puede seleccionar otro span.
