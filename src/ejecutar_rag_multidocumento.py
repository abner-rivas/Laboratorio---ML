"""Ejecuta y guarda la extensión experimental de RAG multidocumento.

Uso desde la raíz del repositorio::

    python src/ejecutar_rag_multidocumento.py

El script no modifica los CSV ni los gráficos del experimento monodocumento.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

from funciones_qa import (
    buscar_chunks_multidocumento,
    calcular_metricas_recuperacion,
    cargar_corpus_multidocumento,
    chunk_relevante_multidocumento,
    clasificar_error_multidocumento,
    construir_indice_faiss_multidocumento,
    crear_chunks_multidocumento,
    evaluar_ranking_multidocumento,
    evaluar_respuesta_multidocumento,
    rag_multidocumento,
    resumir_corpus_multidocumento,
    validar_metadata_chunks,
)


MODELO_EMBEDDINGS = (
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
MODELO_QA = "MMG/bert-base-spanish-wwm-cased-finetuned-sqac"
CHUNK_SIZE = 800
OVERLAP = 0
TOP_K = 10
VALORES_K = (1, 3, 5, 10)
SEMILLA = 42


class ExtractorQAManual:
    """Adaptador QA compatible con la inferencia manual del notebook."""

    def __init__(self, modelo: str, dispositivo: str) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(modelo)
        self.modelo = AutoModelForQuestionAnswering.from_pretrained(modelo)
        self.dispositivo = torch.device(dispositivo)
        self.modelo.to(self.dispositivo)
        self.modelo.eval()

    def __call__(
        self,
        *,
        question: str,
        context: str,
        top_k: int = 1,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        codificacion = self.tokenizer(
            question,
            context,
            truncation="only_second",
            max_length=512,
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        ids_secuencia = codificacion.sequence_ids(0)
        offsets = codificacion.pop("offset_mapping")[0]
        entradas = {
            clave: valor.to(self.dispositivo)
            for clave, valor in codificacion.items()
        }
        with torch.no_grad():
            salida = self.modelo(**entradas)
        mascara_contexto = torch.tensor(
            [identificador == 1 for identificador in ids_secuencia],
            dtype=torch.bool,
        )
        logits_inicio = salida.start_logits[0].detach().cpu().masked_fill(
            ~mascara_contexto, -1e9
        )
        logits_fin = salida.end_logits[0].detach().cpu().masked_fill(
            ~mascara_contexto, -1e9
        )
        probabilidades_inicio = torch.softmax(logits_inicio, dim=-1)
        probabilidades_fin = torch.softmax(logits_fin, dim=-1)
        cantidad = min(12, int(mascara_contexto.sum().item()))
        inicios = torch.topk(probabilidades_inicio, cantidad).indices.tolist()
        finales = torch.topk(probabilidades_fin, cantidad).indices.tolist()
        candidatos = []
        for inicio_token in inicios:
            for fin_token in finales:
                longitud = fin_token - inicio_token + 1
                if not 1 <= longitud <= 45:
                    continue
                inicio = int(offsets[inicio_token, 0])
                fin = int(offsets[fin_token, 1])
                if fin <= inicio:
                    continue
                candidatos.append({
                    "answer": context[inicio:fin].strip(),
                    "score": float(
                        probabilidades_inicio[inicio_token]
                        * probabilidades_fin[fin_token]
                    ),
                    "start": inicio,
                    "end": fin,
                })
        candidatos.sort(key=lambda candidato: candidato["score"], reverse=True)
        if not candidatos:
            candidatos = [{"answer": "", "score": 0.0, "start": 0, "end": 0}]
        seleccionados = candidatos[:top_k]
        return seleccionados[0] if top_k == 1 else seleccionados


def localizar_raiz() -> Path:
    """Localiza el repositorio sin introducir rutas dependientes del equipo."""
    actual = Path.cwd().resolve()
    for candidata in (actual, *actual.parents):
        if (
            (candidata / "LaboratorioML.ipynb").is_file()
            and (candidata / "data/documento_fuente.pdf").is_file()
        ):
            return candidata
    raise FileNotFoundError("No se encontró la raíz de Laboratorio---ML")


def cargar_preguntas(ruta: Path) -> list[dict[str, Any]]:
    preguntas = json.loads(ruta.read_text(encoding="utf-8"))
    if not 16 <= len(preguntas) <= 20:
        raise AssertionError("La evaluación debe contener entre 16 y 20 preguntas")
    numeros = [int(item["numero"]) for item in preguntas]
    if numeros != list(range(1, len(preguntas) + 1)):
        raise AssertionError("Los números de pregunta deben ser consecutivos")
    cantidad_sin_respuesta = sum(bool(item.get("sin_respuesta")) for item in preguntas)
    if not 2 <= cantidad_sin_respuesta <= 3:
        raise AssertionError("Deben existir dos o tres preguntas sin respuesta")
    return preguntas


def validar_evidencias(
    preguntas: list[dict[str, Any]],
    documentos: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
) -> None:
    """Comprueba que las respuestas esperadas proceden realmente de los PDF."""
    por_nombre = {documento["documento"]: documento for documento in documentos}
    documentos_evaluados = set()
    for item in preguntas:
        if item.get("sin_respuesta"):
            if item.get("documento_esperado") is not None:
                raise AssertionError("Una pregunta sin respuesta no debe fingir una fuente")
            continue
        nombre = item["documento_esperado"]
        if nombre not in por_nombre:
            raise AssertionError(f"Documento esperado fuera del corpus: {nombre}")
        documentos_evaluados.add(nombre)
        pagina = int(item["pagina_esperada"])
        if not 1 <= pagina <= int(por_nombre[nombre]["numero_paginas"]):
            raise AssertionError(f"Página inválida en la pregunta {item['numero']}")
        relevantes = [
            chunk for chunk in chunks
            if chunk_relevante_multidocumento(chunk, item)
        ]
        if not relevantes:
            raise AssertionError(
                f"La evidencia de la pregunta {item['numero']} no cabe en un chunk 800/0"
            )
    if documentos_evaluados != set(por_nombre):
        faltantes = set(por_nombre) - documentos_evaluados
        raise AssertionError(f"Documentos sin pregunta evaluable: {sorted(faltantes)}")


def obtener_metricas_monodocumento(ruta_csv: Path) -> dict[str, float | int]:
    """Lee la fila final MPNet sin alterar ni reinterpretar el experimento previo."""
    with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    candidatas = [
        fila for fila in filas
        if fila["experimento"] == "rag_mpnet"
        and fila["tipo_registro"] == "resumen_experimental"
        and fila["configuracion"] == "800/0; Top-10; base completa"
    ]
    if len(candidatas) != 1:
        raise AssertionError("No se encontró una única fila final de RAG MPNet")
    fila = candidatas[0]
    return {
        "documentos": 1,
        "paginas": 62,
        "chunks": int(fila["numero_chunks"]),
        "vectores": int(fila["numero_chunks"]),
        "dimension": int(fila["dimension_embeddings"]),
        "top_k": int(fila["top_k"]),
        "recall_at_10": float(fila["recall_at_k"]),
        "qa_accuracy": float(fila["accuracy"]),
        "preguntas": int(fila["total_preguntas"]),
    }


def guardar_graficos(
    salida_graficos: Path,
    metricas: dict[str, float],
    mono: dict[str, float | int],
    totales: dict[str, int],
    estadisticas_indice: dict[str, float | int | str],
) -> None:
    salida_graficos.mkdir(parents=True, exist_ok=True)
    ks = list(VALORES_K)

    fig, ax = plt.subplots(figsize=(7, 4))
    valores = [metricas[f"Document Recall@{k}"] for k in ks]
    ax.plot(ks, valores, marker="o", linewidth=2, color="#3568a8")
    ax.set(xticks=ks, ylim=(0, 1.05), xlabel="K", ylabel="Document Recall@K")
    ax.set_title("Recuperación del documento esperado")
    ax.grid(alpha=0.25)
    for k, valor in zip(ks, valores):
        ax.annotate(f"{valor:.1%}", (k, valor), xytext=(0, 8),
                    textcoords="offset points", ha="center")
    fig.tight_layout()
    fig.savefig(salida_graficos / "rag_multidocumento_document_recall_at_k.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    valores = [metricas[f"Chunk Recall@{k}"] for k in ks]
    ax.plot(ks, valores, marker="o", linewidth=2, color="#5b9a5b")
    ax.set(xticks=ks, ylim=(0, 1.05), xlabel="K", ylabel="Chunk Recall@K")
    ax.set_title("Recuperación del chunk con evidencia")
    ax.grid(alpha=0.25)
    for k, valor in zip(ks, valores):
        ax.annotate(f"{valor:.1%}", (k, valor), xytext=(0, 8),
                    textcoords="offset points", ha="center")
    fig.tight_layout()
    fig.savefig(salida_graficos / "rag_multidocumento_chunk_recall_at_k.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)

    etiquetas = ["RAG\nmonodocumento", "RAG\nmultidocumento"]
    recall = [float(mono["recall_at_10"]), metricas["Chunk Recall@10"]]
    accuracy = [float(mono["qa_accuracy"]), metricas["QA Accuracy respondibles"]]
    x = np.arange(len(etiquetas))
    ancho = 0.34
    fig, ax = plt.subplots(figsize=(8, 4.5))
    barras_1 = ax.bar(x - ancho / 2, recall, ancho, label="Recall@10",
                      color="#3568a8")
    barras_2 = ax.bar(x + ancho / 2, accuracy, ancho, label="QA Accuracy",
                      color="#d07a32")
    ax.set(xticks=x, xticklabels=etiquetas, ylim=(0, 1.05), ylabel="Proporción")
    ax.set_title("Comparación descriptiva (conjuntos de preguntas distintos)")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    for barra in [*barras_1, *barras_2]:
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.02,
                f"{barra.get_height():.1%}", ha="center")
    fig.tight_layout()
    fig.savefig(salida_graficos / "rag_monodocumento_vs_multidocumento.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)

    vectores = [int(mono["vectores"]), int(totales["chunks"])]
    memoria_mib = [
        int(mono["vectores"]) * int(mono["dimension"]) * 4 / 1024 ** 2,
        int(estadisticas_indice["memoria_embeddings_bytes"]) / 1024 ** 2,
    ]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
    colores = ["#7b5ea7", "#4f9b8f"]
    barras = ax1.bar(etiquetas, vectores, color=colores)
    ax1.set_title("Vectores/chunks")
    ax1.set_ylabel("Cantidad")
    for barra, valor in zip(barras, vectores):
        ax1.text(barra.get_x() + barra.get_width() / 2, valor,
                 f"{valor}", ha="center", va="bottom")
    barras = ax2.bar(etiquetas, memoria_mib, color=colores)
    ax2.set_title("Matriz de embeddings")
    ax2.set_ylabel("MiB (float32)")
    for barra, valor in zip(barras, memoria_mib):
        ax2.text(barra.get_x() + barra.get_width() / 2, valor,
                 f"{valor:.2f}", ha="center", va="bottom")
    fig.suptitle("Crecimiento de la base vectorial")
    fig.tight_layout()
    fig.savefig(salida_graficos / "rag_multidocumento_tamano_base_vectorial.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)


def observacion_error(
    categoria: str,
    item: dict[str, Any],
    resultado: dict[str, Any],
    ranking: dict[str, int | None],
) -> str:
    if categoria == "Sin error":
        return (
            f"Respuesta correcta desde {resultado['documento_fuente']}, "
            f"página {resultado['pagina_fuente']}, chunk "
            f"{resultado['chunk_fuente']}."
        )
    if item.get("sin_respuesta"):
        return (
            f"El corpus no contiene evidencia, pero BETO extrajo "
            f"{resultado['respuesta']!r} desde {resultado['documento_fuente']}."
        )
    if categoria.startswith("Error tipo A"):
        detalle_rank = (
            "no apareció en Top-10"
            if ranking["rank_documento_correcto"] is None
            else f"apareció por primera vez en rank {ranking['rank_documento_correcto']}"
        )
        return (
            f"El documento esperado {item['documento_esperado']} {detalle_rank}; "
            f"el candidato QA ganador procedió de {resultado['documento_fuente']}."
        )
    if categoria.startswith("Error tipo B"):
        return (
            f"El documento apareció en rank {ranking['rank_documento_correcto']}, "
            f"pero el ganador fue el chunk {resultado['chunk_fuente']} sin la "
            "evidencia y página esperadas."
        )
    return (
        f"La evidencia apareció en rank {ranking['rank_chunk_correcto']}, pero "
        f"BETO extrajo {resultado['respuesta']!r}."
    )


def ejecutar(args: argparse.Namespace) -> None:
    raiz = localizar_raiz()
    salida = raiz / args.salida
    graficos = salida / "graficos"
    salida.mkdir(parents=True, exist_ok=True)

    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    torch.manual_seed(SEMILLA)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEMILLA)
    dispositivo = "cuda" if torch.cuda.is_available() and not args.cpu else "cpu"

    preguntas = cargar_preguntas(raiz / "data/preguntas_multidocumento.json")
    documentos = cargar_corpus_multidocumento(
        raiz / "data/documento_fuente.pdf",
        raiz / "data/corpus_complementario",
    )
    chunks = crear_chunks_multidocumento(
        documentos, chunk_size=CHUNK_SIZE, overlap=OVERLAP
    )
    filas_corpus, totales = resumir_corpus_multidocumento(documentos, chunks)
    validar_evidencias(preguntas, documentos, chunks)
    print(f"Corpus validado: {totales}", flush=True)

    modelo_embeddings = SentenceTransformer(MODELO_EMBEDDINGS, device=dispositivo)
    embeddings, indice, estadisticas_indice = construir_indice_faiss_multidocumento(
        modelo_embeddings, chunks, batch_size=args.batch_size
    )
    validar_metadata_chunks(chunks, embeddings, dimension_esperada=768)
    print(f"Índice construido: {estadisticas_indice}", flush=True)

    qa = ExtractorQAManual(MODELO_QA, dispositivo)
    # Calentamiento fuera de las mediciones por pregunta.
    _ = qa(question=preguntas[0]["pregunta"], context=chunks[0]["texto"], top_k=1)

    filas_resultados: list[dict[str, Any]] = []
    filas_recuperacion: list[dict[str, Any]] = []
    filas_metricas_recuperacion: list[dict[str, Any]] = []
    filas_errores: list[dict[str, Any]] = []

    for item in preguntas:
        resultado = rag_multidocumento(
            item["pregunta"], modelo_embeddings, indice, chunks, qa, top_k=TOP_K
        )
        ranking = evaluar_ranking_multidocumento(resultado["recuperados"], item)
        correcta, detalle_qa = evaluar_respuesta_multidocumento(
            resultado["respuesta"], item
        )
        top1 = resultado["recuperados"][0]
        fuente_qa_correcta = (
            not item.get("sin_respuesta")
            and resultado["documento_fuente"] == item["documento_esperado"]
        )
        ganador_qa = next(
            candidato for candidato in resultado["candidatos_qa"]
            if candidato["chunk_global_id"] == resultado["chunk_global_fuente"]
        )
        chunk_fuente_correcto = chunk_relevante_multidocumento(ganador_qa, item)
        categoria = clasificar_error_multidocumento(
            item,
            correcta,
            detalle_qa,
            ranking["rank_documento_correcto"],
            ranking["rank_chunk_correcto"],
            documento_fuente=resultado["documento_fuente"],
            chunk_fuente_correcto=chunk_fuente_correcto,
        )
        fila_base = {
            "numero": item["numero"],
            "tipo_pregunta": item["tipo_pregunta"],
            "dificultad": item["dificultad"],
            "pregunta": item["pregunta"],
            "respuesta_esperada": item["respuesta_esperada"],
            "respuesta_predicha": resultado["respuesta"],
            "correcta": "Sí" if correcta else "No",
            "detalle_evaluacion": detalle_qa,
            "documento_esperado": item.get("documento_esperado"),
            "documento_top1": top1["documento"],
            "documento_recuperado": resultado["documento_fuente"],
            "documento_correcto": "Sí" if fuente_qa_correcta else "No",
            "pagina_esperada": item.get("pagina_esperada"),
            "pagina_recuperada": resultado["pagina_fuente"],
            "chunk_recuperado": resultado["chunk_fuente"],
            "chunk_global_recuperado": resultado["chunk_global_fuente"],
            "chunk_correcto": "Sí" if chunk_fuente_correcto else "No",
            "score_qa": resultado["score_qa"],
            "similitud": resultado["similitud_recuperacion"],
            "rank_fuente_qa": resultado["rank_fuente"],
            "rank_documento_correcto": ranking["rank_documento_correcto"],
            "rank_chunk_correcto": ranking["rank_chunk_correcto"],
            "tiempo_s": resultado["tiempo_s"],
            "sin_respuesta": bool(item.get("sin_respuesta")),
            "categoria_error": categoria,
        }
        filas_resultados.append(fila_base)
        filas_metricas_recuperacion.append({
            **ranking,
            "sin_respuesta": bool(item.get("sin_respuesta")),
        })
        filas_errores.append({
            "numero": item["numero"],
            "pregunta": item["pregunta"],
            "categoria": categoria,
            "observacion": observacion_error(categoria, item, resultado, ranking),
        })
        for chunk in resultado["recuperados"]:
            filas_recuperacion.append({
                "numero": item["numero"],
                "pregunta": item["pregunta"],
                "documento_esperado": item.get("documento_esperado"),
                "pagina_esperada": item.get("pagina_esperada"),
                "sin_respuesta": bool(item.get("sin_respuesta")),
                "rank": chunk["rank"],
                "documento": chunk["documento"],
                "titulo_documento": chunk["titulo_documento"],
                "pagina_inicio": chunk["pagina_inicio"],
                "pagina_fin": chunk["pagina_fin"],
                "chunk_id": chunk["chunk_id"],
                "chunk_global_id": chunk["chunk_global_id"],
                "vector_posicion": chunk["vector_posicion"],
                "similitud": chunk["similitud"],
                "documento_correcto": bool(
                    not item.get("sin_respuesta")
                    and chunk["documento"] == item["documento_esperado"]
                ),
                "chunk_relevante": chunk_relevante_multidocumento(chunk, item),
                "texto": chunk["texto"],
            })
        print(
            f"P{item['numero']:02d}: {resultado['respuesta']!r} · "
            f"{resultado['documento_fuente']} · {categoria}",
            flush=True,
        )

    metricas = calcular_metricas_recuperacion(
        filas_metricas_recuperacion, VALORES_K
    )
    respondibles = [fila for fila in filas_resultados if not fila["sin_respuesta"]]
    sin_respuesta = [fila for fila in filas_resultados if fila["sin_respuesta"]]
    metricas["QA Accuracy"] = sum(
        fila["correcta"] == "Sí" for fila in filas_resultados
    ) / len(filas_resultados)
    metricas["QA Accuracy respondibles"] = sum(
        fila["correcta"] == "Sí" for fila in respondibles
    ) / len(respondibles)
    metricas["Abstención correcta sin respuesta"] = sum(
        fila["correcta"] == "Sí" for fila in sin_respuesta
    ) / len(sin_respuesta)

    if len({fila["documento"] for fila in filas_recuperacion}) < 2:
        raise AssertionError("La recuperación no devolvió documentos diferentes")
    if not any(
        len({f["documento"] for f in filas_recuperacion if f["numero"] == numero}) > 1
        for numero in range(1, len(preguntas) + 1)
    ):
        raise AssertionError("Ninguna consulta mezcló candidatos documentales")

    df_corpus = pd.DataFrame(filas_corpus)
    df_corpus.loc[len(df_corpus)] = {
        "documento": "TOTAL",
        "titulo_documento": f"{totales['documentos']} documentos",
        "paginas": totales["paginas"],
        "paginas_con_texto": totales["paginas_con_texto"],
        "paginas_sin_texto": "",
        "caracteres": totales["caracteres"],
        "palabras_aproximadas": totales["palabras_aproximadas"],
        "chunks": totales["chunks"],
    }
    df_corpus.to_csv(salida / "rag_multidocumento_corpus.csv", index=False)
    pd.DataFrame(filas_resultados).to_csv(
        salida / "rag_multidocumento_resultados.csv", index=False
    )
    pd.DataFrame(filas_recuperacion).to_csv(
        salida / "rag_multidocumento_recuperacion.csv", index=False
    )
    pd.DataFrame(filas_errores).to_csv(
        salida / "rag_multidocumento_errores.csv", index=False
    )
    pd.DataFrame([
        {"metrica": nombre, "valor": valor}
        for nombre, valor in metricas.items()
    ]).to_csv(salida / "rag_multidocumento_metricas.csv", index=False)

    with (salida / "rag_multidocumento_metadata.jsonl").open(
        "w", encoding="utf-8"
    ) as archivo:
        for chunk in chunks:
            archivo.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    import faiss

    faiss.write_index(indice, str(salida / "indice_rag_multidocumento.faiss"))

    mono = obtener_metricas_monodocumento(salida / "resultados_qa.csv")
    comparacion = pd.DataFrame([
        {
            "sistema": "RAG monodocumento",
            **mono,
            "seleccion_documental": "No aplica",
            "metadata": "Página + chunk",
            "nota_comparabilidad": "Conjunto original de 10 preguntas",
        },
        {
            "sistema": "RAG multidocumento",
            "documentos": totales["documentos"],
            "paginas": totales["paginas"],
            "chunks": totales["chunks"],
            "vectores": estadisticas_indice["numero_vectores"],
            "dimension": estadisticas_indice["dimension"],
            "top_k": TOP_K,
            "recall_at_10": metricas["Chunk Recall@10"],
            "qa_accuracy": metricas["QA Accuracy respondibles"],
            "preguntas": len(preguntas),
            "seleccion_documental": "Sí",
            "metadata": "Documento + página + chunk",
            "nota_comparabilidad": (
                "16 preguntas respondibles y 2 sin respuesta; comparación descriptiva"
            ),
        },
    ])
    comparacion.to_csv(
        salida / "rag_multidocumento_comparacion.csv", index=False
    )
    guardar_graficos(graficos, metricas, mono, totales, estadisticas_indice)

    configuracion = {
        "fecha_ejecucion_utc": datetime.now(timezone.utc).isoformat(),
        "semilla": SEMILLA,
        "modelo_qa": MODELO_QA,
        "modelo_embeddings": MODELO_EMBEDDINGS,
        "chunk_size": CHUNK_SIZE,
        "overlap": OVERLAP,
        "top_k_qa": TOP_K,
        "valores_k_recuperacion": list(VALORES_K),
        "dispositivo": dispositivo,
        "corpus": totales,
        "indice": estadisticas_indice,
        "metricas": metricas,
        "version_python": sys.version,
        "version_torch": torch.__version__,
    }
    (salida / "rag_multidocumento_configuracion.json").write_text(
        json.dumps(configuracion, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("MÉTRICAS", json.dumps(metricas, ensure_ascii=False), flush=True)
    print(f"Artefactos guardados en {salida.relative_to(raiz)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--salida", default="results",
        help="Directorio de salida relativo a la raíz (predeterminado: results)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=32,
        help="Tamaño de lote para embeddings (predeterminado: 32)",
    )
    parser.add_argument(
        "--cpu", action="store_true",
        help="Fuerza CPU aunque CUDA esté disponible",
    )
    args = parser.parse_args()
    ejecutar(args)


if __name__ == "__main__":
    main()
