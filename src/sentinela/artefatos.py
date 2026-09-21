"""Localização e integridade dos artefatos versionados do Sentinela."""
from __future__ import annotations

import hashlib
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DIR_DADOS = RAIZ / "dados"
DIR_ARTEFATOS = RAIZ / "artefatos"


def caminho_dados(nome: str) -> pathlib.Path:
    return DIR_DADOS / f"{nome}.csv"


def caminho_artefato(nome: str) -> pathlib.Path:
    return DIR_ARTEFATOS / nome


def sha256(caminho: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(65536), b""):
            digest.update(bloco)
    return digest.hexdigest()


def ler_manifest() -> dict:
    with caminho_artefato("manifest.json").open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def verificar_manifest() -> list[str]:
    """Devolve a lista de divergências entre o manifest e os arquivos em disco.

    Lista vazia significa que tudo bate. Útil para o primeiro teste de
    reprodutibilidade de qualquer suíte.
    """
    manifest = ler_manifest()
    problemas: list[str] = []
    for relativo, esperado in manifest["arquivos"].items():
        caminho = RAIZ / relativo
        if not caminho.exists():
            problemas.append(f"ausente: {relativo}")
            continue
        obtido = sha256(caminho)
        if obtido != esperado:
            problemas.append(f"sha256 diferente: {relativo}")
    return problemas
