"""Funciones reutilizables para los experimentos de QA y RAG.

El módulo contiene únicamente transformaciones deterministas y utilidades
independientes del estado del notebook. La carga de modelos y la ejecución de
los experimentos permanecen visibles en ``LaboratorioML.ipynb``.
"""

from __future__ import annotations

import re
import time
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


TITULOS_DOCUMENTOS_UES = {
    "documento_fuente.pdf": (
        "Reglamento de la Gestión Académico-Administrativa de la "
        "Universidad de El Salvador"
    ),
    "ley_organica_ues.pdf": "Ley Orgánica de la Universidad de El Salvador",
    "reglamento_arancel_academico_ues.pdf": (
        "Reglamento General de Arancel Académico de la Universidad de El Salvador"
    ),
    "reglamento_becas_ues.pdf": (
        "Reglamento de Becas de la Universidad de El Salvador"
    ),
    "reglamento_disciplinario_ues.pdf": (
        "Reglamento Disciplinario de la Universidad de El Salvador"
    ),
    "reglamento_electoral_ues.pdf": (
        "Reglamento Electoral de la Universidad de El Salvador"
    ),
    "reglamento_general_ley_organica_ues.pdf": (
        "Reglamento General de la Ley Orgánica de la Universidad de El Salvador"
    ),
    "reglamento_sistema_escalafon_personal_ues.pdf": (
        "Reglamento General del Sistema de Escalafón del Personal de la "
        "Universidad de El Salvador"
    ),
    "reglamento_unidades_valorativas_cum_ues.pdf": (
        "Reglamento del Sistema de Unidades Valorativas y de Coeficiente de "
        "Unidades de Mérito de la Universidad de El Salvador"
    ),
}


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparaciones robustas en español."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " ".join(texto.split())


def evaluar_coincidencia(
    respuesta_modelo: str,
    respuesta_esperada: str,
) -> tuple[bool, str]:
    """Evalúa coincidencia exacta, cobertura y precisión léxica."""
    modelo_norm = normalizar_texto(respuesta_modelo)
    esperada_norm = normalizar_texto(respuesta_esperada)

    if modelo_norm == esperada_norm:
        return True, "Respuesta exacta tras normalización"
    if esperada_norm and esperada_norm in modelo_norm:
        return True, "Respuesta correcta dentro de un fragmento más amplio"

    tokens_modelo = set(modelo_norm.split())
    tokens_esperada = set(esperada_norm.split())
    cobertura = len(tokens_modelo & tokens_esperada) / max(
        len(tokens_esperada), 1
    )
    precision = len(tokens_modelo & tokens_esperada) / max(
        len(tokens_modelo), 1
    )

    if cobertura >= 0.80 and precision >= 0.60:
        return True, "Variante textual correcta"
    if cobertura >= 0.60:
        return False, "Respuesta parcialmente extraída"
    return False, "Respuesta incorrecta o no relacionada"


def evaluar_respuesta_con_variantes(
    respuesta_modelo: str,
    respuesta_esperada: str,
    respuestas_aceptables: Iterable[str] = (),
) -> tuple[bool, str]:
    """Evalúa la respuesta principal y variantes aceptables explícitas."""
    correcta, detalle = evaluar_coincidencia(
        respuesta_modelo, respuesta_esperada
    )
    if correcta:
        return correcta, detalle

    for variante in respuestas_aceptables:
        coincide, _ = evaluar_coincidencia(respuesta_modelo, variante)
        if coincide:
            return True, "Respuesta correcta por revisión manual explícita"
    return correcta, detalle


def nivel_confianza(score: float) -> str:
    """Clasifica el score QA sin interpretarlo como exactitud."""
    if score >= 0.75:
        return "score alto"
    if score >= 0.40:
        return "score medio"
    return "score bajo"


def limpiar_texto_pagina(texto: str) -> str:
    """Aplica la limpieza conservadora usada para el PDF del laboratorio."""
    texto = texto.replace("\u00ad", "")
    texto = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def pagina_para_offset(
    posicion: int,
    paginas: Sequence[Mapping[str, Any]],
) -> int:
    """Asocia un offset del texto unido con su página física."""
    if not paginas:
        raise ValueError("paginas no puede estar vacío")
    for registro in paginas:
        if posicion <= int(registro["fin"]):
            return int(registro["pagina"])
    return int(paginas[-1]["pagina"])


def crear_fragmentos_con_metadata(
    texto: str,
    paginas: Sequence[Mapping[str, Any]],
    chunk_size: int = 800,
    overlap: int = 0,
) -> list[dict[str, Any]]:
    """Divide texto por caracteres y conserva offsets y páginas."""
    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que cero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap debe cumplir 0 <= overlap < chunk_size")

    fragmentos: list[dict[str, Any]] = []
    paso = chunk_size - overlap
    for chunk_id, inicio in enumerate(range(0, len(texto), paso), start=1):
        fin = min(inicio + chunk_size, len(texto))
        fragmentos.append(
            {
                "chunk_id": chunk_id,
                "texto": texto[inicio:fin],
                "pagina_inicio": pagina_para_offset(inicio, paginas),
                "pagina_fin": pagina_para_offset(max(fin - 1, inicio), paginas),
                "inicio": inicio,
                "fin": fin,
            }
        )
    return fragmentos


def evidencia_en_fragmento(
    fragmento: Mapping[str, Any],
    evidencias: Iterable[str],
    pagina_objetivo: int | None = None,
) -> bool:
    """Comprueba evidencia textual y, opcionalmente, procedencia de página."""
    texto_norm = normalizar_texto(str(fragmento["texto"]))
    coincide_texto = all(
        normalizar_texto(evidencia) in texto_norm for evidencia in evidencias
    )
    if not coincide_texto:
        return False
    if pagina_objetivo is None:
        return True
    return (
        int(fragmento["pagina_inicio"])
        <= pagina_objetivo
        <= int(fragmento["pagina_fin"])
    )


def extraer_documento_pdf(
    ruta_pdf: str | Path,
    documento_id: int,
    titulo_documento: str | None = None,
) -> dict[str, Any]:
    """Extrae un PDF por página y conserva offsets físicos verificables."""
    try:
        import pymupdf
    except ImportError:  # Compatibilidad con instalaciones anteriores.
        import fitz as pymupdf

    ruta = Path(ruta_pdf)
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el PDF: {ruta}")
    if ruta.suffix.lower() != ".pdf":
        raise ValueError(f"El archivo no es PDF: {ruta}")

    paginas: list[dict[str, Any]] = []
    partes: list[str] = []
    desplazamiento = 0
    with pymupdf.open(ruta) as pdf:
        numero_paginas = int(pdf.page_count)
        metadatos_pdf = dict(pdf.metadata or {})
        for numero_pagina, pagina in enumerate(pdf, start=1):
            texto_crudo = pagina.get_text("text")
            texto = limpiar_texto_pagina(texto_crudo)
            inicio = desplazamiento
            fin = inicio + len(texto)
            paginas.append(
                {
                    "pagina": numero_pagina,
                    "texto_crudo": texto_crudo,
                    "texto": texto,
                    "inicio": inicio,
                    "fin": fin,
                    "tiene_texto": bool(texto),
                }
            )
            partes.append(texto)
            desplazamiento = fin + 2

    texto_documento = "\n\n".join(partes)
    paginas_con_texto = [p["pagina"] for p in paginas if p["tiene_texto"]]
    paginas_sin_texto = [p["pagina"] for p in paginas if not p["tiene_texto"]]
    titulo = (
        titulo_documento
        or TITULOS_DOCUMENTOS_UES.get(ruta.name)
        or metadatos_pdf.get("title")
        or ruta.stem.replace("_", " ").title()
    )
    return {
        "documento_id": int(documento_id),
        "documento": ruta.name,
        "titulo_documento": titulo,
        "ruta": ruta,
        "paginas": paginas,
        "texto": texto_documento,
        "numero_paginas": numero_paginas,
        "paginas_con_texto": len(paginas_con_texto),
        "paginas_sin_texto": paginas_sin_texto,
        "caracteres": len(texto_documento),
        "palabras_aproximadas": len(texto_documento.split()),
        "tamano_archivo_bytes": ruta.stat().st_size,
    }


def cargar_corpus_multidocumento(
    ruta_documento_fuente: str | Path = Path("data/documento_fuente.pdf"),
    ruta_corpus_complementario: str | Path = Path("data/corpus_complementario"),
) -> list[dict[str, Any]]:
    """Carga el documento original y todos los PDF institucionales adicionales."""
    ruta_fuente = Path(ruta_documento_fuente)
    carpeta = Path(ruta_corpus_complementario)
    if not carpeta.is_dir():
        raise FileNotFoundError(f"No se encontró el corpus complementario: {carpeta}")

    rutas = [ruta_fuente, *sorted(carpeta.glob("*.pdf"))]
    if len(rutas) < 2:
        raise ValueError("El corpus multidocumento requiere al menos dos PDF")
    if len({ruta.name for ruta in rutas}) != len(rutas):
        raise ValueError("Los nombres de los PDF deben ser únicos")

    documentos = [
        extraer_documento_pdf(ruta, documento_id=indice)
        for indice, ruta in enumerate(rutas, start=1)
    ]
    if any(not documento["texto"].strip() for documento in documentos):
        vacios = [d["documento"] for d in documentos if not d["texto"].strip()]
        raise ValueError(f"PDF sin texto extraíble: {vacios}")
    return documentos


def crear_chunks_multidocumento(
    documentos: Sequence[Mapping[str, Any]],
    chunk_size: int = 800,
    overlap: int = 0,
) -> list[dict[str, Any]]:
    """Fragmenta cada documento por separado y añade metadata documental."""
    metadata_chunks: list[dict[str, Any]] = []
    for documento in documentos:
        fragmentos = crear_fragmentos_con_metadata(
            str(documento["texto"]),
            documento["paginas"],
            chunk_size=chunk_size,
            overlap=overlap,
        )
        for fragmento in fragmentos:
            texto = str(fragmento["texto"])
            posicion_vector = len(metadata_chunks)
            metadata_chunks.append(
                {
                    "documento_id": int(documento["documento_id"]),
                    "documento": str(documento["documento"]),
                    "archivo": str(documento["documento"]),
                    "titulo_documento": str(documento["titulo_documento"]),
                    "pagina": int(fragmento["pagina_inicio"]),
                    "pagina_inicio": int(fragmento["pagina_inicio"]),
                    "pagina_fin": int(fragmento["pagina_fin"]),
                    "chunk_id": int(fragmento["chunk_id"]),
                    "chunk_global_id": posicion_vector + 1,
                    "vector_posicion": posicion_vector,
                    "inicio_documento": int(fragmento["inicio"]),
                    "fin_documento": int(fragmento["fin"]),
                    "num_caracteres": len(texto),
                    "num_palabras": len(texto.split()),
                    "texto": texto,
                }
            )
    validar_metadata_chunks(metadata_chunks)
    return metadata_chunks


def validar_metadata_chunks(
    metadata_chunks: Sequence[Mapping[str, Any]],
    embeddings: Any | None = None,
    dimension_esperada: int | None = None,
) -> dict[str, int]:
    """Valida la correspondencia uno a uno entre FAISS y la metadata."""
    if not metadata_chunks:
        raise ValueError("metadata_chunks no puede estar vacío")
    requeridos = {
        "documento", "titulo_documento", "pagina", "pagina_inicio",
        "pagina_fin", "chunk_id", "chunk_global_id", "vector_posicion",
        "texto",
    }
    for posicion, chunk in enumerate(metadata_chunks):
        faltantes = requeridos - set(chunk)
        if faltantes:
            raise ValueError(f"Chunk {posicion} sin campos: {sorted(faltantes)}")
        if int(chunk["vector_posicion"]) != posicion:
            raise AssertionError("La metadata no está alineada con la posición FAISS")
        if int(chunk["chunk_global_id"]) != posicion + 1:
            raise AssertionError("chunk_global_id dejó de ser consecutivo")
        if not str(chunk["documento"]).endswith(".pdf"):
            raise ValueError(f"Procedencia PDF inválida en el chunk {posicion}")
        if int(chunk["pagina"]) < 1 or int(chunk["chunk_id"]) < 1:
            raise ValueError(f"Página o chunk inválido en la posición {posicion}")
        if not str(chunk["texto"]).strip():
            raise ValueError(f"Chunk vacío en la posición {posicion}")

    dimension = 0
    if embeddings is not None:
        if len(embeddings) != len(metadata_chunks):
            raise AssertionError("len(embeddings) != len(metadata_chunks)")
        if getattr(embeddings, "ndim", None) != 2:
            raise ValueError("La matriz de embeddings debe tener dos dimensiones")
        dimension = int(embeddings.shape[1])
        if dimension_esperada is not None and dimension != dimension_esperada:
            raise AssertionError("La dimensionalidad de embeddings no es la esperada")
    return {"chunks": len(metadata_chunks), "dimension": dimension}


def resumir_corpus_multidocumento(
    documentos: Sequence[Mapping[str, Any]],
    metadata_chunks: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Construye el resumen por PDF y los totales del corpus."""
    chunks_por_documento: dict[str, int] = {}
    for chunk in metadata_chunks:
        nombre = str(chunk["documento"])
        chunks_por_documento[nombre] = chunks_por_documento.get(nombre, 0) + 1

    filas = []
    for documento in documentos:
        nombre = str(documento["documento"])
        filas.append(
            {
                "documento": nombre,
                "titulo_documento": str(documento["titulo_documento"]),
                "paginas": int(documento["numero_paginas"]),
                "paginas_con_texto": int(documento["paginas_con_texto"]),
                "paginas_sin_texto": ",".join(
                    map(str, documento["paginas_sin_texto"])
                ),
                "caracteres": int(documento["caracteres"]),
                "palabras_aproximadas": int(documento["palabras_aproximadas"]),
                "chunks": chunks_por_documento.get(nombre, 0),
            }
        )
    totales = {
        "documentos": len(filas),
        "paginas": sum(fila["paginas"] for fila in filas),
        "paginas_con_texto": sum(fila["paginas_con_texto"] for fila in filas),
        "caracteres": sum(fila["caracteres"] for fila in filas),
        "palabras_aproximadas": sum(
            fila["palabras_aproximadas"] for fila in filas
        ),
        "chunks": len(metadata_chunks),
    }
    return filas, totales


def construir_indice_faiss_multidocumento(
    modelo_embeddings: Any,
    metadata_chunks: Sequence[Mapping[str, Any]],
    batch_size: int = 32,
) -> tuple[Any, Any, dict[str, float | int | str]]:
    """Genera embeddings normalizados y un índice exacto ``IndexFlatIP``."""
    import faiss
    import numpy as np

    textos = [str(chunk["texto"]) for chunk in metadata_chunks]
    inicio_embeddings = time.perf_counter()
    embeddings = modelo_embeddings.encode(
        textos,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)
    tiempo_embeddings = time.perf_counter() - inicio_embeddings
    dimension = int(embeddings.shape[1])
    validar_metadata_chunks(metadata_chunks, embeddings, dimension)
    if not np.allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-5):
        raise AssertionError("Los embeddings no quedaron normalizados")

    inicio_indice = time.perf_counter()
    indice = faiss.IndexFlatIP(dimension)
    indice.add(np.ascontiguousarray(embeddings))
    tiempo_indice = time.perf_counter() - inicio_indice
    if indice.ntotal != len(metadata_chunks) or indice.d != dimension:
        raise AssertionError("FAISS no coincide con embeddings y metadata")
    estadisticas = {
        "tipo_indice": type(indice).__name__,
        "numero_vectores": int(indice.ntotal),
        "dimension": dimension,
        "tiempo_embeddings_s": float(tiempo_embeddings),
        "tiempo_indice_s": float(tiempo_indice),
        "memoria_embeddings_bytes": int(embeddings.nbytes),
    }
    return embeddings, indice, estadisticas


def buscar_chunks_multidocumento(
    pregunta: str,
    modelo_embeddings: Any,
    indice_faiss: Any,
    metadata_chunks: Sequence[Mapping[str, Any]],
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Recupera Top-K y devuelve similitud junto con procedencia completa."""
    import numpy as np

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")
    if not 1 <= top_k <= len(metadata_chunks):
        raise ValueError("top_k debe estar entre 1 y el número de chunks")
    if int(indice_faiss.ntotal) != len(metadata_chunks):
        raise AssertionError("FAISS y metadata no tienen la misma longitud")

    embedding = modelo_embeddings.encode(
        [pregunta],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)
    if embedding.shape[1] != indice_faiss.d:
        raise AssertionError("La consulta y el índice tienen dimensiones distintas")
    similitudes, posiciones = indice_faiss.search(
        np.ascontiguousarray(embedding), top_k
    )
    resultados = []
    for rank, (posicion, similitud) in enumerate(
        zip(posiciones[0], similitudes[0]), start=1
    ):
        if posicion < 0:
            continue
        chunk = metadata_chunks[int(posicion)]
        if int(chunk["vector_posicion"]) != int(posicion):
            raise AssertionError("La posición recuperada no coincide con la metadata")
        resultados.append(
            {
                **dict(chunk),
                "rank": rank,
                "similitud": float(similitud),
            }
        )
    return resultados


class ExtractorQAManual:
    """Adaptador QA usado por el experimento multidocumento oficial."""

    def __init__(self, modelo: str, dispositivo: str) -> None:
        import torch
        from transformers import AutoModelForQuestionAnswering, AutoTokenizer

        self._torch = torch
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
        torch = self._torch
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


def _normalizar_salida_pipeline_qa(salida: Any) -> dict[str, Any]:
    """Unifica las variantes de salida de pipelines QA de Transformers."""
    if isinstance(salida, list):
        if not salida:
            return {"answer": "", "score": 0.0, "start": 0, "end": 0}
        salida = salida[0]
    return {
        "answer": str(salida.get("answer", "")).strip(),
        "score": float(salida.get("score", 0.0)),
        "start": int(salida.get("start", 0)),
        "end": int(salida.get("end", 0)),
    }


def rag_multidocumento(
    pregunta: str,
    modelo_embeddings: Any,
    indice_faiss: Any,
    metadata_chunks: Sequence[Mapping[str, Any]],
    pipeline_qa: Any,
    top_k: int = 10,
) -> dict[str, Any]:
    """Ejecuta recuperación multidocumento y QA extractivo trazable."""
    inicio = time.perf_counter()
    recuperados = buscar_chunks_multidocumento(
        pregunta,
        modelo_embeddings,
        indice_faiss,
        metadata_chunks,
        top_k=top_k,
    )
    candidatos_qa = []
    for chunk in recuperados:
        salida = _normalizar_salida_pipeline_qa(
            pipeline_qa(
                question=pregunta,
                context=chunk["texto"],
                top_k=1,
            )
        )
        candidatos_qa.append({**chunk, **salida})

    ganador = max(candidatos_qa, key=lambda candidato: candidato["score"])
    return {
        "pregunta": pregunta,
        "respuesta": ganador["answer"],
        "score_qa": ganador["score"],
        "documento_fuente": ganador["documento"],
        "titulo_documento_fuente": ganador["titulo_documento"],
        "pagina_fuente": ganador["pagina"],
        "pagina_fin_fuente": ganador["pagina_fin"],
        "chunk_fuente": ganador["chunk_id"],
        "chunk_global_fuente": ganador["chunk_global_id"],
        "rank_fuente": ganador["rank"],
        "similitud_recuperacion": ganador["similitud"],
        "tiempo_s": time.perf_counter() - inicio,
        "recuperados": recuperados,
        "candidatos_qa": candidatos_qa,
    }


def chunk_relevante_multidocumento(
    chunk: Mapping[str, Any],
    item: Mapping[str, Any],
) -> bool:
    """Comprueba documento, página y evidencia de un chunk esperado."""
    if item.get("sin_respuesta"):
        return False
    if chunk["documento"] != item["documento_esperado"]:
        return False
    pagina = item.get("pagina_esperada")
    if pagina is not None and not (
        int(chunk["pagina_inicio"]) <= int(pagina) <= int(chunk["pagina_fin"])
    ):
        return False
    evidencias = item.get("evidencias_clave") or [item.get("evidencia", "")]
    evidencias = [str(evidencia) for evidencia in evidencias if str(evidencia)]
    if not evidencias:
        return False
    texto = normalizar_texto(str(chunk["texto"]))
    return all(normalizar_texto(evidencia) in texto for evidencia in evidencias)


def evaluar_ranking_multidocumento(
    recuperados: Sequence[Mapping[str, Any]],
    item: Mapping[str, Any],
) -> dict[str, int | None]:
    """Obtiene los primeros ranks del documento y chunk relevantes."""
    if item.get("sin_respuesta"):
        return {"rank_documento_correcto": None, "rank_chunk_correcto": None}
    rank_documento = next(
        (
            int(chunk["rank"])
            for chunk in recuperados
            if chunk["documento"] == item["documento_esperado"]
        ),
        None,
    )
    rank_chunk = next(
        (
            int(chunk["rank"])
            for chunk in recuperados
            if chunk_relevante_multidocumento(chunk, item)
        ),
        None,
    )
    return {
        "rank_documento_correcto": rank_documento,
        "rank_chunk_correcto": rank_chunk,
    }


def calcular_metricas_recuperacion(
    evaluaciones: Sequence[Mapping[str, Any]],
    valores_k: Sequence[int] = (1, 3, 5, 10),
) -> dict[str, float]:
    """Calcula Accuracy/Recall documental, Recall de chunk y MRR."""
    evaluables = [fila for fila in evaluaciones if not fila.get("sin_respuesta")]
    if not evaluables:
        raise ValueError("No existen preguntas respondibles para evaluar")
    total = len(evaluables)
    metricas: dict[str, float] = {}
    for k in valores_k:
        if k <= 0:
            raise ValueError("Los valores de K deben ser positivos")
        doc_aciertos = sum(
            fila.get("rank_documento_correcto") is not None
            and int(fila["rank_documento_correcto"]) <= k
            for fila in evaluables
        )
        chunk_aciertos = sum(
            fila.get("rank_chunk_correcto") is not None
            and int(fila["rank_chunk_correcto"]) <= k
            for fila in evaluables
        )
        metricas[f"Document Recall@{k}"] = doc_aciertos / total
        metricas[f"Chunk Recall@{k}"] = chunk_aciertos / total
    metricas["Document Accuracy@1"] = metricas["Document Recall@1"]
    metricas["MRR documento"] = sum(
        1 / int(fila["rank_documento_correcto"])
        if fila.get("rank_documento_correcto") is not None else 0.0
        for fila in evaluables
    ) / total
    metricas["MRR chunk"] = sum(
        1 / int(fila["rank_chunk_correcto"])
        if fila.get("rank_chunk_correcto") is not None else 0.0
        for fila in evaluables
    ) / total
    return metricas


def evaluar_respuesta_multidocumento(
    respuesta: str,
    item: Mapping[str, Any],
) -> tuple[bool, str]:
    """Evalúa QA y conserva explícitas las preguntas sin respuesta."""
    if item.get("sin_respuesta"):
        if not respuesta.strip() or normalizar_texto(respuesta) in {
            "sin respuesta", "no hay respuesta", "no se encuentra"
        }:
            return True, "El sistema se abstuvo ante una pregunta sin evidencia"
        return False, "El extractor produjo un span aunque el corpus no tenía evidencia"
    return evaluar_respuesta_con_variantes(
        respuesta,
        str(item["respuesta_esperada"]),
        item.get("respuestas_aceptables", ()),
    )


def clasificar_error_multidocumento(
    item: Mapping[str, Any],
    correcta: bool,
    detalle_qa: str,
    rank_documento: int | None,
    rank_chunk: int | None,
    documento_fuente: str | None = None,
    chunk_fuente_correcto: bool | None = None,
) -> str:
    """Asigna una categoría académica mutuamente excluyente al resultado."""
    if item.get("sin_respuesta"):
        return "Error tipo E: pregunta sin respuesta"
    if (
        rank_documento is None
        or documento_fuente is not None
        and documento_fuente != item.get("documento_esperado")
    ):
        return "Error tipo A: documento incorrecto"
    if rank_chunk is None or chunk_fuente_correcto is False:
        return "Error tipo B: documento correcto, chunk incorrecto"
    if correcta:
        return "Sin error"
    if "parcial" in detalle_qa.lower():
        return "Error tipo D: respuesta parcialmente correcta"
    return "Error tipo C: recuperación correcta, QA incorrecto"
