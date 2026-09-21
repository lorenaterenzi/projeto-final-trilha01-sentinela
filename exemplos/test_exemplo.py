"""Três testes que passam, para você começar de algum lugar.

    pytest exemplos/ -v

Repare no que eles NÃO provam. O primeiro confere que os artefatos são os
publicados. O segundo confere um contrato de forma. O terceiro confere que o
modelo não está quebrado — não que ele esteja certo.
"""
import pytest

import sentinela as sn


@pytest.fixture(scope="module")
def lote():
    return sn.dados.carregar("teste")


def test_artefatos_batem_com_o_manifest():
    """Reprodutibilidade: os dados e modelos em disco são os publicados."""
    assert sn.artefatos.verificar_manifest() == []


def test_features_preservam_linhas_e_ordem_das_colunas(lote):
    """Contrato de forma entre limpeza e engenharia de atributos."""
    limpo = sn.preprocessamento.limpar(lote)
    X = sn.features.construir(limpo)

    assert len(X) == len(limpo)
    assert tuple(X.columns) == sn.features.ORDEM_FEATURES
    assert X.notna().all().all()


def test_pipeline_devolve_decisao_binaria_para_cada_leitura(lote):
    """Ponta a ponta: entra leitura crua, sai decisão."""
    saida = sn.pipeline.executar(lote, versao="v1")

    assert len(saida) == len(sn.preprocessamento.limpar(lote))
    assert set(saida["predicao"].unique()) <= {0, 1}
    assert saida["probabilidade"].between(0.0, 1.0).all()

    # E o modelo não é um preditor constante — ele decide as duas coisas.
    assert 0 < saida["predicao"].sum() < len(saida)
