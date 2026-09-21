"""Métricas de avaliação expostas pelo Sentinela.

Deliberadamente enxuto: matriz de confusão e as quatro métricas que o painel
da manutenção acompanha. Qualquer outra métrica que a sua análise exigir você
calcula na sua própria suíte.
"""
from __future__ import annotations

import numpy as np


def matriz_confusao(y_real, y_predito) -> dict[str, int]:
    """Conta vp/vn/fp/fn tomando 1 = falha prevista/observada."""
    real = np.asarray(y_real).astype(int)
    predito = np.asarray(y_predito).astype(int)
    if real.shape != predito.shape:
        raise ValueError(f"tamanhos diferentes: {real.shape} vs {predito.shape}")
    return {
        "vp": int(np.sum((real == 1) & (predito == 1))),
        "vn": int(np.sum((real == 0) & (predito == 0))),
        "fp": int(np.sum((real == 0) & (predito == 1))),
        "fn": int(np.sum((real == 1) & (predito == 0))),
    }


def metricas(y_real, y_predito) -> dict[str, float]:
    """Acurácia, precisão, recall e F1 da classe positiva (falha)."""
    m = matriz_confusao(y_real, y_predito)
    total = m["vp"] + m["vn"] + m["fp"] + m["fn"]
    previstos = m["vp"] + m["fp"]
    reais = m["vp"] + m["fn"]
    precisao = m["vp"] / previstos if previstos else 0.0
    recall = m["vp"] / reais if reais else 0.0
    f1 = 2 * precisao * recall / (precisao + recall) if (precisao + recall) else 0.0
    return {
        "acuracia": (m["vp"] + m["vn"]) / total if total else 0.0,
        "precisao": precisao,
        "recall": recall,
        "f1": f1,
    }
