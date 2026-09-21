"""Retreina os modelos v1 e v2 e regrava os artefatos JSON.

    python scripts/treinar.py

Só este script depende de scikit-learn — a inferência (`sentinela.modelo`) é
numpy puro. Rodar aqui é opcional: os artefatos já vêm versionados no
repositório. Regravá-los muda todos os sha256 do `manifest.json`.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from sentinela import artefatos, dados, features, preprocessamento  # noqa: E402

SEMENTE = 42

CONFIGURACOES = {
    "v1": {
        "descricao": "Linha de base em produção desde 05/2026. Floresta rasa, "
        "treinada com reponderação de classe.",
        "parametros": {
            "n_estimators": 60,
            "max_depth": 8,
            "min_samples_leaf": 25,
            "class_weight": "balanced_subsample",
        },
    },
    "v2": {
        "descricao": "Candidata a substituir a v1. Floresta mais profunda, sem "
        "reponderação de classe.",
        "parametros": {
            "n_estimators": 80,
            "max_depth": 11,
            "min_samples_leaf": 12,
            "class_weight": None,
        },
    },
}


def serializar_arvore(arvore) -> dict:
    t = arvore.tree_
    valor = np.asarray(t.value, dtype=np.float64)[:, 0, :]
    soma = valor.sum(axis=1, keepdims=True)
    soma[soma == 0.0] = 1.0
    prob = (valor / soma)[:, 1]
    folha = t.children_left == -1
    return {
        "feature": [0 if f else int(v) for f, v in zip(folha, t.feature)],
        "limiar": [0.0 if f else round(float(v), 6) for f, v in zip(folha, t.threshold)],
        "filho_esq": [int(v) for v in t.children_left],
        "filho_dir": [int(v) for v in t.children_right],
        "prob": [round(float(v), 6) for v in prob],
    }


def main() -> None:
    from sklearn.ensemble import RandomForestClassifier

    bruto = dados.carregar("treino")
    limpo = preprocessamento.limpar(bruto)

    # Tabela de risco histórico por motor, congelada a partir do treino.
    risco = limpo.groupby("id_maquina")["falha_72h"].mean().round(6).to_dict()
    caminho_risco = artefatos.caminho_artefato("risco_maquina.json")
    caminho_risco.parent.mkdir(parents=True, exist_ok=True)
    with caminho_risco.open("w", encoding="utf-8") as arquivo:
        json.dump(risco, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
    features._RISCO_CONGELADO = None  # força releitura

    X = features.construir(limpo)
    y = limpo["falha_72h"].to_numpy()

    for versao, config in CONFIGURACOES.items():
        floresta = RandomForestClassifier(
            random_state=SEMENTE, n_jobs=-1, **config["parametros"]
        )
        floresta.fit(X.to_numpy(dtype=np.float64), y)
        artefato = {
            "versao": versao,
            "descricao": config["descricao"],
            "treinado_em": dt.date.today().isoformat(),
            "semente": SEMENTE,
            "parametros": {k: v for k, v in config["parametros"].items()},
            "ordem_features": list(features.ORDEM_FEATURES),
            "arvores": [serializar_arvore(a) for a in floresta.estimators_],
        }
        caminho = artefatos.caminho_artefato(f"modelo_{versao}.json")
        conteudo = json.dumps(artefato, ensure_ascii=False, separators=(",", ":"))
        caminho.write_text(conteudo, encoding="utf-8")
        nos = sum(len(a["feature"]) for a in artefato["arvores"])
        print(f"{versao}: {len(floresta.estimators_)} arvores, {nos} nos, "
              f"{len(conteudo) / 1e6:.2f} MB")

    escrever_manifest()


def escrever_manifest() -> None:
    alvos = [
        "dados/treino.csv",
        "dados/teste.csv",
        "dados/producao.csv",
        "artefatos/modelo_v1.json",
        "artefatos/modelo_v2.json",
        "artefatos/risco_maquina.json",
    ]
    manifest = {
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "semente": SEMENTE,
        "arquivos": {a: artefatos.sha256(RAIZ / a) for a in alvos},
    }
    caminho = artefatos.caminho_artefato("manifest.json")
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(manifest, arquivo, ensure_ascii=False, indent=2)
    print(f"manifest: {len(alvos)} arquivos")


if __name__ == "__main__":
    main()
