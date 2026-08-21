"""Valida los artefactos finales sin descargar modelos ni repetir experimentos.

Uso desde la raíz del repositorio::

    python scripts/validar_entrega.py
"""

from __future__ import annotations

import csv
import json
import re
import struct
from pathlib import Path

import nbformat


RAIZ = Path(__file__).resolve().parents[1]
ARCHIVOS_OBLIGATORIOS = (
    "README.md",
    "LaboratorioML.ipynb",
    "requirements.txt",
    "pytest.ini",
    "data/documento_fuente.pdf",
    "src/funciones_qa.py",
    "results/rag_multidocumento_metricas.csv",
    "results/rag_multidocumento_errores.csv",
    "docs/informe.md",
    "docs/informe.tex",
    "docs/informe.pdf",
    "docs/checklist_entrega.md",
)
METRICAS_ESPERADAS = {
    "Document Recall@10": 0.9375,
    "Chunk Recall@10": 0.5625,
    "MRR documento": 0.7833333333333333,
    "MRR chunk": 0.31875,
    "QA Accuracy respondibles": 0.25,
    "Abstención correcta sin respuesta": 0.0,
}


def exigir(condicion: bool, mensaje: str) -> None:
    """Interrumpe la validación con una causa legible."""
    if not condicion:
        raise AssertionError(mensaje)


def validar_archivos() -> None:
    """Comprueba la estructura mínima de entrega."""
    faltantes = [ruta for ruta in ARCHIVOS_OBLIGATORIOS if not (RAIZ / ruta).is_file()]
    exigir(not faltantes, f"Faltan archivos obligatorios: {faltantes}")
    pdfs = sorted((RAIZ / "data/corpus_complementario").glob("*.pdf"))
    exigir(len(pdfs) == 8, "El corpus complementario debe conservar ocho PDF")
    nombre_pdf_descartado = "_".join(("doc", "ues", "asistente.pdf"))
    exigir(
        not any(ruta.name == nombre_pdf_descartado for ruta in RAIZ.rglob("*.pdf")),
        "El PDF descartado no debe reincorporarse",
    )


def validar_notebook() -> None:
    """Valida estructura, ejecución y ausencia de salidas de error."""
    ruta = RAIZ / "LaboratorioML.ipynb"
    with ruta.open(encoding="utf-8") as archivo:
        notebook = nbformat.read(archivo, as_version=4)
    nbformat.validate(notebook)
    codigo = [celda for celda in notebook.cells if celda.cell_type == "code"]
    markdown = [celda for celda in notebook.cells if celda.cell_type == "markdown"]
    exigir(len(notebook.cells) == 273, "El notebook canónico debe conservar 273 celdas")
    exigir(len(codigo) == 129, "El notebook canónico debe conservar 129 celdas de código")
    exigir(len(markdown) == 144, "El notebook canónico debe conservar 144 celdas Markdown")
    exigir(all(celda.source.strip() for celda in notebook.cells), "Hay celdas vacías")
    exigir(
        all(celda.execution_count is not None for celda in codigo),
        "Hay celdas de código sin ejecutar",
    )
    errores = [
        salida
        for celda in codigo
        for salida in celda.get("outputs", [])
        if salida.get("output_type") == "error" or salida.get("traceback")
    ]
    exigir(not errores, "El notebook contiene errores o tracebacks almacenados")


def leer_csv(nombre: str) -> list[dict[str, str]]:
    with (RAIZ / "results" / nombre).open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def validar_resultados() -> None:
    """Recalcula conteos y verifica las métricas publicadas."""
    metricas = {
        fila["metrica"]: float(fila["valor"])
        for fila in leer_csv("rag_multidocumento_metricas.csv")
    }
    for nombre, esperado in METRICAS_ESPERADAS.items():
        exigir(abs(metricas[nombre] - esperado) < 1e-12, f"Métrica inconsistente: {nombre}")

    resultados = leer_csv("rag_multidocumento_resultados.csv")
    respondibles = [fila for fila in resultados if fila["sin_respuesta"].lower() == "false"]
    sin_respuesta = [fila for fila in resultados if fila["sin_respuesta"].lower() == "true"]
    exigir((len(resultados), len(respondibles), len(sin_respuesta)) == (18, 16, 2), "Dataset inválido")
    exigir(sum(fila["correcta"] == "Sí" for fila in respondibles) == 4, "QA debe conservar 4/16")
    exigir(sum(fila["correcta"] == "Sí" for fila in sin_respuesta) == 0, "Abstención alterada")
    exigir(len(leer_csv("rag_multidocumento_recuperacion.csv")) == 180, "Top-10 incompleto")
    exigir(len(leer_csv("rag_multidocumento_errores.csv")) == 18, "Análisis de errores incompleto")

    corpus = leer_csv("rag_multidocumento_corpus.csv")
    total = corpus[-1]
    exigir(
        (int(total["paginas"]), int(total["chunks"])) == (199, 765),
        "El corpus debe conservar 199 páginas y 765 chunks",
    )


def validar_metadata() -> None:
    """Comprueba procedencia y alineación vectorial de los 765 chunks."""
    ruta = RAIZ / "results/rag_multidocumento_metadata.jsonl"
    metadata = [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines()]
    campos = {"documento", "pagina", "chunk_id", "chunk_global_id", "vector_posicion", "texto"}
    exigir(len(metadata) == 765, "La metadata debe contener 765 filas")
    exigir(len({fila["documento"] for fila in metadata}) == 9, "La metadata debe cubrir nueve PDF")
    exigir(all(campos <= set(fila) for fila in metadata), "Faltan campos de trazabilidad")
    exigir(
        all(
            fila["vector_posicion"] == posicion
            and fila["chunk_global_id"] == posicion + 1
            for posicion, fila in enumerate(metadata)
        ),
        "La metadata dejó de estar alineada con FAISS",
    )


def validar_figuras_y_referencias() -> None:
    """Comprueba PNG y rutas usadas por las fuentes del informe."""
    figuras = list((RAIZ / "results/graficos").glob("*.png"))
    exigir(len(figuras) == 14, "Deben conservarse los catorce gráficos finales")
    for figura in figuras:
        datos = figura.read_bytes()
        exigir(datos[:8] == b"\x89PNG\r\n\x1a\n", f"PNG inválido: {figura.name}")
        ancho, alto = struct.unpack(">II", datos[16:24])
        exigir(ancho >= 600 and alto >= 350, f"Figura poco legible: {figura.name}")

    tex = (RAIZ / "docs/informe.tex").read_text(encoding="utf-8")
    referencias = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)
    for referencia in referencias:
        ruta = (RAIZ / "docs" / referencia).resolve()
        exigir(ruta.is_file(), f"Figura referenciada pero ausente: {referencia}")


def main() -> None:
    validar_archivos()
    validar_notebook()
    validar_resultados()
    validar_metadata()
    validar_figuras_y_referencias()
    print("Validación de entrega completada: notebook, corpus, métricas y figuras coherentes.")


if __name__ == "__main__":
    main()
