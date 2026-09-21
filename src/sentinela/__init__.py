"""Sentinela — manutenção preditiva de motores industriais (Nortemec).

Prevê se um motor elétrico vai falhar nas próximas 72 horas a partir de
leituras horárias de sensores.

    import sentinela as sn

    bruto = sn.dados.carregar("teste")
    saida = sn.pipeline.executar(bruto, versao="v1")
    print(sn.avaliacao.metricas(saida["falha_72h"], saida["predicao"]))
"""
from . import artefatos, avaliacao, dados, features, modelo, pipeline, preprocessamento

__all__ = [
    "artefatos",
    "avaliacao",
    "dados",
    "features",
    "modelo",
    "pipeline",
    "preprocessamento",
]

__version__ = "1.0.0"
