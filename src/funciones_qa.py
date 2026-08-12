"""Funciones reutilizables para los experimentos de QA y RAG.

El módulo contiene únicamente transformaciones deterministas y utilidades
independientes del estado del notebook. La carga de modelos y la ejecución de
los experimentos permanecen visibles en ``LaboratorioML.ipynb``.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


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
