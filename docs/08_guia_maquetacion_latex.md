# Guía y registro de maquetación en LaTeX

## 1. Objetivo

La entrega final sigue este flujo:

```text
docs/informe.md
        ↓
docs/informe.tex
        ↓
docs/informe.pdf
```

`informe.md` contiene la narrativa principal. Los otros Markdown sirven para ampliar secciones, comprobar cifras y trasladar evidencia secundaria a anexos. La conversión no debe alterar métricas ni reinterpretar resultados.

## 2. Límite

- Cuerpo principal: máximo 25 páginas sin anexos.
- Longitud recomendada: 18–22 páginas.
- Los anexos deben comenzar después de conclusiones y referencias.

Si la primera maquetación supera el límite, se debe reducir repetición, trasladar tablas detalladas a anexos y conservar únicamente las figuras que respondan preguntas experimentales centrales.

## 3. Distribución recomendada

| Bloque | Páginas aproximadas |
|---|---:|
| Portada | 1 |
| Introducción y objetivos | 1–2 |
| Fundamentos teóricos | 3–4 |
| Herramientas y metodología | 2–3 |
| Desarrollo experimental | 4–5 |
| RAG, Top-K y baseline | 3–4 |
| Resultados, hallazgos y limitaciones | 3–4 |
| Conclusiones | 1 |
| Referencias | 1 |
| Anexos | Fuera del límite cuando corresponda |

La suma es una guía. La prioridad es mantener teoría, metodología, resultados e interpretación en secciones distintas.

## 4. Paquetes LaTeX sugeridos

El preámbulo final utiliza paquetes estables de TeX Live para español, tablas,
ecuaciones, gráficos, microtipografía y enlaces:

| Paquete | Uso sugerido |
|---|---|
| `geometry` | Márgenes y tamaño de página. |
| `graphicx` | Inclusión y escalado de figuras. |
| `booktabs` | Reglas tipográficas de tablas. |
| `hyperref` | Enlaces, referencias y metadatos del PDF. |
| `amsmath` | Ecuaciones y símbolos matemáticos. |
| `array` | Tipos de columna y control de tablas. |
| `longtable` | Tablas que deben ocupar varias páginas. |
| `xcolor` | Colores sobrios cuando sean necesarios. |
| `microtype` | Mejora tipográfica y ajuste de párrafos. |

El documento está preparado para `pdflatex`; utiliza codificación UTF-8, fuentes
T1 y `babel` con español. `latexmk` ejecuta automáticamente las pasadas necesarias
para resolver índice y referencias cruzadas. La copia final también fue compilada
con Tectonic 0.17.0, alternativa autocontenida basada en XeTeX.

## 5. Figuras

Las figuras originales están en `results/graficos/`. Desde `docs/`, las rutas Markdown comienzan con `../results/graficos/`.

Recomendaciones:

- conservar proporciones;
- fijar ancho relativo a `\textwidth` y no ancho/alto simultáneos;
- no ampliar imágenes más allá de lo necesario;
- incluir título numerado y etiqueta para referencia cruzada;
- escribir debajo o en el párrafo siguiente una interpretación propia;
- evitar insertar gráficos que repitan exactamente una tabla sin aportar lectura visual;
- usar `subcaption` para pares como accuracy/Recall de embeddings si ayuda a reducir páginas;
- mantener la advertencia de CPU/CUDA junto a la figura temporal baseline–RAG.

Figuras prioritarias para el cuerpo:

1. comparación de modelos;
2. accuracy o Recall por Top-K;
3. tiempo baseline frente a RAG;
4. comparación de embeddings;
5. Recall por tamaño de base.

Las restantes pueden aparecer como subfiguras o en anexos. `07_trazabilidad.md` explica las diez.

## 6. Tablas

- Usar `booktabs` en lugar de líneas verticales cuando la plantilla lo permita.
- Alinear números por columna y conservar el mismo número razonable de decimales.
- Abreviar nombres en tablas y presentar identificadores completos en el texto.
- Evitar más columnas de las que caben en el margen.
- Usar `longtable` para el listado de preguntas o trazabilidad si se incluye completo.
- No duplicar las 45 respuestas individuales en el cuerpo principal.
- Mantener unidades en encabezados: segundos, caracteres, dimensiones y porcentajes.
- Distinguir `Score QA`, `Accuracy` y `Recall@K` en columnas separadas.

Tablas recomendadas para el cuerpo:

- agregado global de modelos QA;
- seis configuraciones de chunking;
- Top-K MiniLM;
- baseline frente a RAG;
- MiniLM frente a MPNet;
- tamaño de base;
- configuración final.

## 7. Código

El informe debe priorizar decisiones y análisis. No se deben copiar funciones completas del notebook o `src/funciones_qa.py`.

Si un fragmento es imprescindible:

- limitarlo a las líneas que expresan la decisión;
- explicar su función en el texto;
- evitar salidas extensas;
- trasladar implementaciones secundarias a anexos;
- conservar sintaxis Python y caracteres escapados correctamente.

La arquitectura puede explicarse mejor mediante flujos simples que mediante bloques de código.

## 8. Bibliografía

Las referencias de Transformer, BERT, BETO, Sentence-BERT, MPNet, FAISS, RAG,
Hugging Face y PyMuPDF fueron contrastadas con publicaciones primarias,
documentación oficial o fichas oficiales de modelos. La relación verificable se
conserva en `referencias.md` y la bibliografía utilizada está incorporada en
`informe.tex`. No se asignaron DOI ni datos editoriales no comprobados.

## 9. Elementos esenciales

El documento final debe incluir:

- portada con datos institucionales exactos;
- numeración de secciones;
- tabla de contenido;
- lista de figuras y tablas si la plantilla lo requiere;
- ecuaciones numeradas cuando se referencien;
- figuras con título, fuente interna y explicación;
- tablas con título y unidades;
- referencias cruzadas;
- bibliografía verificada;
- anexos claramente separados del cuerpo;
- enlaces activos cuando corresponda.

## 10. Flujo de conversión recomendado

1. Revisar `00_datos_generales.md` y trasladar los datos de portada.
2. Usar `informe.md` como fuente del cuerpo principal.
3. Consultar archivos modulares para aclarar o ampliar secciones.
4. Contrastar las referencias con `referencias.md`.
5. Convertir la estructura Markdown a capítulos o secciones LaTeX.
6. Sustituir tablas Markdown por `tabular`, `tabularx` o `longtable` según ancho.
7. Insertar figuras desde `results/graficos/` con rutas válidas.
8. Agregar etiquetas y referencias cruzadas.
9. Aplicar `\appendix` antes del contenido de `anexos.md`.
10. Compilar y revisar advertencias, desbordamientos y páginas.

Desde la raíz del repositorio:

```bash
cd docs
latexmk -pdf -interaction=nonstopmode -halt-on-error informe.tex
latexmk -c informe.tex
```

El segundo comando elimina auxiliares y conserva `informe.pdf`.

Alternativa verificada cuando no se dispone de TeX Live del sistema:

```bash
cd docs
tectonic -X compile informe.tex
```

## 11. Checklist de compilación

### Contenido

- [x] Portada con universidad, facultad, escuela, curso, estudiantes, catedrático y fecha correctos.
- [x] BETO-SQAC aparece como modelo QA final.
- [x] MPNet aparece como embedding final; MiniLM se conserva como resultado histórico.
- [x] Configuración final: 800/0, Top-10 y `IndexFlatIP`.
- [x] Accuracy y Recall@10 finales: 60 %.
- [x] Score QA no se presenta como accuracy.
- [x] El sistema se describe como monodocumento y extractivo.

### Formato

- [x] El PDF tiene 24 páginas físicas y respeta el máximo de 25.
- [x] No hay tablas fuera del margen.
- [x] Las figuras mantienen proporción y resolución.
- [x] Todas las figuras y tablas tienen número, título y referencia.
- [x] Las ecuaciones compilan sin errores.
- [x] Los enlaces utilizados fueron verificados.
- [x] El índice coincide con los títulos.
- [x] Los anexos están separados y el límite se cumple sin depender de excluirlos.

### Bibliografía

- [x] No quedan referencias inventadas.
- [x] No quedan marcas bibliográficas pendientes.
- [x] Las citas del texto tienen entrada bibliográfica.
- [x] El documento fuente UES se identifica sin atribuirle datos no comprobados.

### Compilación

- [x] Compilación final sin errores fatales.
- [x] Referencias cruzadas resueltas después de tres pasadas automáticas.
- [x] No hay advertencias de cajas desbordadas ni problemas de legibilidad.
- [x] El PDF incluye fuentes y caracteres españoles correctamente.
- [x] El archivo final se generó como `docs/informe.pdf` en la fase autorizada.
