"""Carga dos conjuntos de leituras de sensores da planta."""
from __future__ import annotations

import pandas as pd

from . import artefatos

CONJUNTOS = ("treino", "teste", "producao")

COLUNAS = (
    "timestamp",
    "id_maquina",
    "idade_equipamento_meses",
    "id_operador",
    "turno",
    "temperatura_c",
    "vibracao_rms",
    "pressao",
    "unidade_pressao",
    "corrente_a",
    "rpm",
    "horas_operacao",
    "falha_72h",
)

ALVO = "falha_72h"


def carregar(nome: str = "treino") -> pd.DataFrame:
    """Carrega um dos conjuntos: 'treino', 'teste' ou 'producao'.

    Devolve o DataFrame cru, exatamente como saiu do historiador da planta —
    sem limpeza, sem conversão de tipo além do que o pandas infere sozinho.
    """
    if nome not in CONJUNTOS:
        raise ValueError(f"conjunto desconhecido: {nome!r}; use um de {CONJUNTOS}")
    return pd.read_csv(artefatos.caminho_dados(nome))
