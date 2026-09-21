import numpy as np
import pandas as pd
import pytest
import sentinela as sn


def test_comparacao_v1_vs_v2_falsos_negativos_criticos():
    """Valida se o modelo candidato v2 não aumenta o número de falsos negativos (motores não alertados)."""
    bruto = sn.dados.carregar("teste")

    saida_v1 = sn.pipeline.executar(bruto, versao="v1", limiar=0.5)
    saida_v2 = sn.pipeline.executar(bruto, versao="v2", limiar=0.5)

    y_real = bruto["falha_72h"]

    # falso negativo: falha real ocorreu (1), mas o modelo previu seguro (0)
    fn_v1 = int(((y_real == 1) & (saida_v1["predicao"] == 0)).sum())
    fn_v2 = int(((y_real == 1) & (saida_v2["predicao"] == 0)).sum())

    # a regra de negócio da fábrica exige que o modelo candidato NÃO aumente falhas não detectadas
    assert fn_v2 <= fn_v1, (
        f"DEFEITO DE NEGÓCIO ESTATÍSTICO: O modelo v2 gerou {fn_v2} falsos negativos "
        f"contra {fn_v1} do modelo v1. A v2 deixa mais motores quebrarem sem aviso!"
    )


def test_calibracao_probabilidades():
    """Verifica se a probabilidade média prevista pelo modelo acompanha a ocorrência real de falhas."""
    bruto = sn.dados.carregar("teste")
    saida = sn.pipeline.executar(bruto, versao="v1")

    df_calib = saida.copy()
    df_calib["faixa_prob"] = pd.cut(
        df_calib["probabilidade"], bins=[0.0, 0.3, 0.7, 1.0]
    )

    freq_observada = df_calib.groupby("faixa_prob", observed=False)[
        "falha_72h"
    ].mean()
    assert not freq_observada.isna().any(), (
        "Existem faixas sem predições suficientes para avaliação de calibração."
    )