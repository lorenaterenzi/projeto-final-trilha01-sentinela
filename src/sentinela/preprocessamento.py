"""Limpeza das leituras cruas do historiador.

Primeira etapa do pipeline: tipos, faltantes e normalização de rótulos.
Depois daqui, `features.construir` assume que o quadro está limpo.
"""
from __future__ import annotations

import pandas as pd

VIBRACAO_PADRAO = 0.0
RPM_MINIMO = 1.0


def limpar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa um lote de leituras. Não modifica o quadro de entrada."""
    limpo = df.copy()

    limpo["timestamp"] = pd.to_datetime(limpo["timestamp"])
    limpo["id_maquina"] = limpo["id_maquina"].astype(str).str.strip().str.upper()
    limpo["id_operador"] = limpo["id_operador"].astype(str).str.strip().str.upper()
    limpo["unidade_pressao"] = limpo["unidade_pressao"].astype(str).str.strip().str.lower()

    # Motor parado não é leitura válida: o historiador registra a linha, mas
    # não há o que prever enquanto o eixo não gira.
    limpo = limpo[limpo["rpm"] >= RPM_MINIMO]

    # O sensor de vibração tem dropout conhecido. Preenchemos o buraco para
    # que a janela móvel não propague NaN pelo lote inteiro.
    limpo["vibracao_rms"] = limpo["vibracao_rms"].fillna(VIBRACAO_PADRAO)

    limpo["turno"] = limpo["turno"].astype(int)
    limpo["idade_equipamento_meses"] = limpo["idade_equipamento_meses"].astype(int)
    limpo["operador_cod"] = (
        limpo["id_operador"].str.extract(r"(\d+)", expand=False).astype(int)
    )

    return limpo.reset_index(drop=True)
