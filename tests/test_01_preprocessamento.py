import pytest
import sentinela as sn


def test_faixa_e_unidade_pressao_contrato_dados():
    """Valida se há leituras de pressão em PSI nos dados sem a devida conversão para bar."""
    for conjunto in ["treino", "teste", "producao"]:
        bruto = sn.dados.carregar(conjunto)
        pressao_max = bruto["pressao"].max()
        # O contrato especifica bar [3.0, 4.5]. Se houver valores acima de 10, é indicador de PSI.
        assert pressao_max <= 10.0, (
            f"DEFEITO DETECTADO: Coluna 'pressao' no conjunto '{conjunto}' possui valor máximo "
            f"de {pressao_max:.2f}, indicando ausência de conversão de PSI para bar."
        )


def test_respeito_faixa_temperatura():
    """Garante que a temperatura operacional esteja no intervalo esperado do contrato."""
    bruto = sn.dados.carregar("teste")
    assert bruto["temperatura_c"].between(
        40.0, 100.0
    ).all(), "Temperaturas fora dos limites do contrato de dados."


def test_sem_valores_ausentes_apos_limpeza():
    """Garante que o pré-processamento trate e remova nulos."""
    bruto = sn.dados.carregar("teste")
    limpo = sn.preprocessamento.limpar(bruto)
    assert (
        limpo.isna().sum().sum() == 0
    ), "Encontrados valores nulos (NaN) após preprocessamento.limpar()."