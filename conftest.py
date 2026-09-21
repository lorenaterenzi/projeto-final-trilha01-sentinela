"""Deixa `import sentinela` funcionar mesmo sem `pip install -e .`.

Conveniência para rodar `pytest` recém-clonado (e no Colab). A forma
recomendada continua sendo instalar o pacote — veja o README.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))
