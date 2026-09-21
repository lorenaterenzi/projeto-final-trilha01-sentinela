"""Pipeline ponta a ponta: leituras cruas -> ordens de manutenção."""
from __future__ import annotations

import pandas as pd

from . import features, modelo, preprocessamento
from .modelo import LIMIAR_PADRAO


def executar(
    df: pd.DataFrame,
    versao: str = "v1",
    limiar: float = LIMIAR_PADRAO,
) -> pd.DataFrame:
    """Roda limpeza -> features -> modelo sobre um lote de leituras cruas.

    Devolve um quadro com `id_maquina`, `timestamp`, `probabilidade` e
    `predicao` (1 = abrir ordem de manutenção preventiva). Se o lote vier
    rotulado, `falha_72h` é propagada para facilitar a avaliação.
    """
    limpo = preprocessamento.limpar(df)
    X = features.construir(limpo)
    modelo_carregado = modelo.carregar(versao)

    saida = pd.DataFrame(
        {
            "id_maquina": limpo["id_maquina"],
            "timestamp": limpo["timestamp"],
            "probabilidade": modelo_carregado.prever_proba(X),
        }
    )
    saida["predicao"] = (saida["probabilidade"] >= limiar).astype(int)
    if "falha_72h" in limpo.columns:
        saida["falha_72h"] = limpo["falha_72h"].astype(int)
    return saida
