"""Modelo de risco de falha — inferência em numpy puro.

Os modelos são florestas de decisão serializadas em JSON (arrays de nós). A
inferência não depende de scikit-learn: os mesmos artefatos produzem os mesmos
números em qualquer máquina, hoje e daqui a dois anos. scikit-learn só é
necessário para *retreinar* (ver `scripts/treinar.py`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import artefatos
from .features import ORDEM_FEATURES

VERSOES = ("v1", "v2")
LIMIAR_PADRAO = 0.5

_CACHE: dict[str, "Modelo"] = {}


@dataclass(frozen=True)
class Arvore:
    feature: np.ndarray
    limiar: np.ndarray
    filho_esq: np.ndarray
    filho_dir: np.ndarray
    prob: np.ndarray

    def prever_proba(self, X: np.ndarray) -> np.ndarray:
        no = np.zeros(len(X), dtype=np.int32)
        ativos = self.filho_esq[no] != -1
        while ativos.any():
            idx = np.nonzero(ativos)[0]
            atual = no[idx]
            vai_esquerda = X[idx, self.feature[atual]] <= self.limiar[atual]
            no[idx] = np.where(vai_esquerda, self.filho_esq[atual], self.filho_dir[atual])
            ativos = self.filho_esq[no] != -1
        return self.prob[no]


class Modelo:
    """Floresta de decisão treinada para prever falha nas próximas 72 horas."""

    def __init__(self, dados: dict):
        self.versao: str = dados["versao"]
        self.descricao: str = dados.get("descricao", "")
        self.ordem_features: tuple[str, ...] = tuple(dados["ordem_features"])
        self.arvores = [
            Arvore(
                feature=np.asarray(a["feature"], dtype=np.int32),
                limiar=np.asarray(a["limiar"], dtype=np.float64),
                filho_esq=np.asarray(a["filho_esq"], dtype=np.int32),
                filho_dir=np.asarray(a["filho_dir"], dtype=np.int32),
                prob=np.asarray(a["prob"], dtype=np.float64),
            )
            for a in dados["arvores"]
        ]

    # -- entrada -----------------------------------------------------------
    def _matriz(self, X) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            faltando = set(self.ordem_features) - set(X.columns)
            if faltando:
                raise ValueError(f"features ausentes: {sorted(faltando)}")
            X = X[list(self.ordem_features)].to_numpy(dtype=np.float64)
        else:
            X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2 or X.shape[1] != len(self.ordem_features):
            raise ValueError(
                f"esperado (n, {len(self.ordem_features)}), recebido {getattr(X, 'shape', None)}"
            )
        if not np.isfinite(X).all():
            raise ValueError("features contêm NaN ou infinito")
        return X

    # -- predição ----------------------------------------------------------
    def prever_proba(self, X) -> np.ndarray:
        """Probabilidade de falha nas próximas 72h, uma por linha."""
        matriz = self._matriz(X)
        acumulado = np.zeros(len(matriz))
        for arvore in self.arvores:
            acumulado += arvore.prever_proba(matriz)
        return acumulado / len(self.arvores)

    def prever(self, X, limiar: float = LIMIAR_PADRAO) -> np.ndarray:
        """Decisão binária: 1 = abrir ordem de manutenção preventiva."""
        return (self.prever_proba(X) >= limiar).astype(int)

    def prever_registro(self, registro: dict, limiar: float = LIMIAR_PADRAO) -> int:
        """Atalho para prever uma leitura só, a partir de um dicionário de features.

        É o caminho usado pelo painel da sala de controle, que recebe um
        registro por vez.
        """
        vetor = np.array([float(valor) for valor in registro.values()], dtype=np.float64)
        if vetor.size != len(self.ordem_features):
            raise ValueError(
                f"esperadas {len(self.ordem_features)} features, recebidas {vetor.size}"
            )
        return int(self.prever(vetor.reshape(1, -1), limiar=limiar)[0])


def carregar(versao: str = "v1") -> Modelo:
    """Carrega um dos modelos versionados ('v1' ou 'v2')."""
    if versao not in VERSOES:
        raise ValueError(f"versão desconhecida: {versao!r}; use uma de {VERSOES}")
    if versao not in _CACHE:
        caminho = artefatos.caminho_artefato(f"modelo_{versao}.json")
        with caminho.open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        modelo = Modelo(dados)
        if tuple(modelo.ordem_features) != tuple(ORDEM_FEATURES):
            raise ValueError("artefato fora de sincronia com features.ORDEM_FEATURES")
        _CACHE[versao] = modelo
    return _CACHE[versao]
