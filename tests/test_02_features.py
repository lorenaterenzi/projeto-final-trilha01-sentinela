import pytest
import pandas as pd
import sentinela as sn


def test_sem_vazamento_temporal_features():
    """Garante que alterar uma leitura no FUTURO (t+1) não altere a feature no instante PASSADO (t)."""
    bruto = (
        sn.dados.carregar("teste")
        .sort_values(["id_maquina", "timestamp"])
        .reset_index(drop=True)
    )
    limpo = sn.preprocessamento.limpar(bruto)

    # pega apenas o primeiro motor
    id_primeiro_motor = limpo["id_maquina"].iloc[0]
    df_orig = limpo[limpo["id_maquina"] == id_primeiro_motor].copy()

    # features originais
    X_orig = sn.features.construir(df_orig)

    # temperatura na ÚLTIMA linha (futuro)
    df_mod = df_orig.copy()
    df_mod.iloc[-1, df_mod.columns.get_loc("temperatura_c")] += 50.0

    # recalcula as features
    X_mod = sn.features.construir(df_mod)

    # A PRIMEIRA linha (passado) não pode mudar
    diferenca = (X_orig.iloc[0] != X_mod.iloc[0]).sum()
    assert diferenca == 0, (
        "DEFEITO DETECTADO: Vazamento temporal em features.construir(). "
        "Uma alteração no futuro alterou os cálculos do passado!"
    )


def test_invariancia_ordem_linhas_features():
    """Garante que construir() devolva o resultado na mesma ordem das linhas do dataframe recebido."""
    bruto = sn.dados.carregar("teste")
    limpo = sn.preprocessamento.limpar(bruto)

    X_normal = sn.features.construir(limpo)

    # embaralha as linhas
    limpo_shuffled = limpo.sample(frac=1, random_state=42)
    X_shuffled = sn.features.construir(limpo_shuffled)

    # verifica se devolveu as mesmas linhas na ordem do de entrada
    pd.testing.assert_frame_equal(X_normal, X_shuffled.reindex(X_normal.index))