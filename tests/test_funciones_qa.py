"""Pruebas deterministas para metadata y métricas multidocumento."""

from __future__ import annotations

import unittest

from src.funciones_qa import (
    calcular_metricas_recuperacion,
    chunk_relevante_multidocumento,
    clasificar_error_multidocumento,
    crear_chunks_multidocumento,
    evaluar_ranking_multidocumento,
    evaluar_respuesta_multidocumento,
    validar_metadata_chunks,
)


class PruebasRAGMultidocumento(unittest.TestCase):
    def setUp(self) -> None:
        self.documentos = [
            {
                "documento_id": 1,
                "documento": "a.pdf",
                "titulo_documento": "Documento A",
                "texto": "alpha evidencia correcta",
                "paginas": [{"pagina": 1, "inicio": 0, "fin": 25}],
            },
            {
                "documento_id": 2,
                "documento": "b.pdf",
                "titulo_documento": "Documento B",
                "texto": "beta distractor semántico",
                "paginas": [{"pagina": 1, "inicio": 0, "fin": 24}],
            },
        ]

    def test_metadata_global_alineada(self) -> None:
        chunks = crear_chunks_multidocumento(
            self.documentos, chunk_size=12, overlap=0
        )
        self.assertEqual(len(chunks), 5)
        self.assertEqual(
            [chunk["vector_posicion"] for chunk in chunks], list(range(5))
        )
        self.assertEqual(
            [chunk["chunk_global_id"] for chunk in chunks], [1, 2, 3, 4, 5]
        )
        self.assertEqual({chunk["documento"] for chunk in chunks}, {"a.pdf", "b.pdf"})
        self.assertEqual(validar_metadata_chunks(chunks)["chunks"], 5)

    def test_ranking_documento_y_chunk_son_metricas_distintas(self) -> None:
        item = {
            "documento_esperado": "a.pdf",
            "pagina_esperada": 1,
            "evidencia": "evidencia correcta",
            "sin_respuesta": False,
        }
        recuperados = [
            {
                "rank": 1,
                "documento": "b.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "texto": "distractor",
            },
            {
                "rank": 2,
                "documento": "a.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "texto": "otro texto del documento",
            },
            {
                "rank": 3,
                "documento": "a.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "texto": "aquí está la evidencia correcta",
            },
        ]
        ranking = evaluar_ranking_multidocumento(recuperados, item)
        self.assertEqual(ranking["rank_documento_correcto"], 2)
        self.assertEqual(ranking["rank_chunk_correcto"], 3)
        self.assertTrue(chunk_relevante_multidocumento(recuperados[2], item))

    def test_metricas_excluyen_preguntas_sin_respuesta(self) -> None:
        filas = [
            {
                "rank_documento_correcto": 1,
                "rank_chunk_correcto": 3,
                "sin_respuesta": False,
            },
            {
                "rank_documento_correcto": 2,
                "rank_chunk_correcto": None,
                "sin_respuesta": False,
            },
            {
                "rank_documento_correcto": None,
                "rank_chunk_correcto": None,
                "sin_respuesta": True,
            },
        ]
        metricas = calcular_metricas_recuperacion(filas, (1, 3))
        self.assertEqual(metricas["Document Recall@1"], 0.5)
        self.assertEqual(metricas["Document Recall@3"], 1.0)
        self.assertEqual(metricas["Chunk Recall@1"], 0.0)
        self.assertEqual(metricas["Chunk Recall@3"], 0.5)
        self.assertAlmostEqual(metricas["MRR documento"], 0.75)
        self.assertAlmostEqual(metricas["MRR chunk"], 1 / 6)

    def test_pregunta_sin_respuesta_no_premia_alucinacion(self) -> None:
        item = {
            "sin_respuesta": True,
            "respuesta_esperada": "SIN_RESPUESTA",
        }
        correcta, _ = evaluar_respuesta_multidocumento("cuarenta horas", item)
        self.assertFalse(correcta)
        categoria = clasificar_error_multidocumento(
            item, correcta, "span inventado", None, None
        )
        self.assertIn("tipo E", categoria)


if __name__ == "__main__":
    unittest.main()
