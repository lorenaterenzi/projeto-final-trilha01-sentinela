import pytest
import sentinela as sn


def test_estabilidade_ruido_menor_que_sensor():
    """Testa se uma perturbação de 0.3 °C (menor que o ruído do sensor de 1.0 °C) altera a decisão."""
    bruto = sn.dados.carregar("teste")
    saida_orig = sn.pipeline.executar(bruto, versao="v1")

    # Aplica perturbação sutil de +0.3 °C
    bruto_ruido = bruto.copy()
    bruto_ruido["temperatura_c"] += 0.3
    saida_ruido = sn.pipeline.executar(bruto_ruido, versao="v1")

    mudancas = (saida_orig["predicao"] != saida_ruido["predicao"]).sum()
    taxa_mudanca = mudancas / len(bruto)

    # Exige que menos de 1% das decisões mude por um ruído tão pequeno
    assert taxa_mudanca < 0.01, (
        f"INSTABILIDADE ADVERSARIAL: Perturbação de 0.3 °C alterou {taxa_mudanca*100:.2f}% "
        f"das decisões de manutenção ({mudancas} motores afetados)."
    )


def test_contrafactual_id_operador_nao_altera_decisao():
    """Garante que trocar o operador responsável (atributo não-físico) não altere a predição."""
    bruto = sn.dados.carregar("teste")
    saida_orig = sn.pipeline.executar(bruto, versao="v1")

    # Força a troca do id_operador de todos para OP-12
    bruto_mod = bruto.copy()
    bruto_mod["id_operador"] = "OP-12"
    saida_mod = sn.pipeline.executar(bruto_mod, versao="v1")

    diferencas = (saida_orig["predicao"] != saida_mod["predicao"]).sum()
    assert diferencas == 0, (
        f"DEFEITO DE VIÉS CAUSAL: Mudar o id_operador alterou {diferencas} predições de falha!"
    )