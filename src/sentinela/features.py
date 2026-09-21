"""Engenharia de atributos do Sentinela.

Transforma leituras limpas (uma linha por motor por hora) nas 13 colunas que
o modelo consome. As janelas móveis são calculadas por motor, respeitando a
ordem cronológica de cada um — o quadro de entrada pode vir em qualquer ordem.
"""
from __future__ import annotations

import json

import pandas as pd

from . import artefatos

JANELA_CURTA = 6  # horas
JANELA_LONGA = 24  # horas
OPERADOR_SENIOR = "OP-07"

ORDEM_FEATURES = (
    "temp_media_6h",
    "temp_max_24h",
    "delta_temp_24h",
    "vib_media_6h",
    "vib_max_24h",
    "corrente_media_6h",
    "pressao",
    "rpm",
    "idade_equipamento_meses",
    "horas_operacao",
    "maquina_risco",
    "operador_senior",
    "turno",
)

_RISCO_CONGELADO: dict[str, float] | None = None


def risco_congelado() -> dict[str, float]:
    """Tabela de risco histórico por motor, versionada em artefatos/."""
    global _RISCO_CONGELADO
    if _RISCO_CONGELADO is None:
        caminho = artefatos.caminho_artefato("risco_maquina.json")
        with caminho.open(encoding="utf-8") as arquivo:
            _RISCO_CONGELADO = json.load(arquivo)
    return _RISCO_CONGELADO


def _risco_por_maquina(df: pd.DataFrame) -> pd.Series:
    """Risco histórico do motor, usado como atributo categórico numérico.

    Quando o lote já vem rotulado, recalculamos o risco no próprio lote para
    refletir o comportamento mais recente da planta; sem rótulo, caímos na
    tabela congelada.
    """
    if "falha_72h" in df.columns:
        return df.groupby("id_maquina")["falha_72h"].transform("mean").astype(float)
    congelado = risco_congelado()
    padrao = sum(congelado.values()) / len(congelado)
    return df["id_maquina"].map(congelado).fillna(padrao).astype(float)


def construir(df: pd.DataFrame) -> pd.DataFrame:
    """Constrói as features a partir de um quadro já limpo.

    Devolve um DataFrame com as colunas de `ORDEM_FEATURES`, nessa ordem,
    preservando o índice do quadro de entrada.
    """
    faltando = {"id_maquina", "timestamp", "temperatura_c", "vibracao_rms"} - set(df.columns)
    if faltando:
        raise ValueError(f"colunas ausentes para construir features: {sorted(faltando)}")

    ordenado = df.sort_values(["id_maquina", "timestamp"])
    por_maquina = ordenado.groupby("id_maquina", sort=False)

    saida = pd.DataFrame(index=ordenado.index)

    temperatura = por_maquina["temperatura_c"]
    saida["temp_media_6h"] = temperatura.transform(
        lambda s: s.rolling(JANELA_CURTA, center=True, min_periods=1).mean()
    )
    saida["temp_max_24h"] = temperatura.transform(
        lambda s: s.rolling(JANELA_LONGA, min_periods=1).max()
    )
    saida["delta_temp_24h"] = temperatura.transform(
        lambda s: s - s.shift(JANELA_LONGA)
    ).fillna(0.0)

    vibracao = por_maquina["vibracao_rms"]
    saida["vib_media_6h"] = vibracao.transform(
        lambda s: s.rolling(JANELA_CURTA, min_periods=1).mean()
    )
    saida["vib_max_24h"] = vibracao.transform(
        lambda s: s.rolling(JANELA_LONGA, min_periods=1).max()
    )

    saida["corrente_media_6h"] = por_maquina["corrente_a"].transform(
        lambda s: s.rolling(JANELA_CURTA, min_periods=1).mean()
    )

    saida["pressao"] = ordenado["pressao"].astype(float)
    saida["rpm"] = ordenado["rpm"].astype(float)
    saida["idade_equipamento_meses"] = ordenado["idade_equipamento_meses"].astype(float)
    saida["horas_operacao"] = ordenado["horas_operacao"].astype(float)
    saida["maquina_risco"] = _risco_por_maquina(ordenado)
    # O técnico sênior (OP-07) é escalado para os motores mais críticos da
    # planta; a equipe de manutenção pediu essa marcação explícita.
    saida["operador_senior"] = (ordenado["id_operador"] == OPERADOR_SENIOR).astype(float)
    saida["turno"] = ordenado["turno"].astype(float)

    return saida.loc[df.index, list(ORDEM_FEATURES)]
