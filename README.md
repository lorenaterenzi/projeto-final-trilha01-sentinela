# Sentinela — manutenção preditiva de motores industriais

Sistema-alvo da **Trilha 1 (ML clássico)** do Projeto Final da disciplina
*Testes Automatizados para Modelos de IA* — IEC PUC Minas.

O Sentinela é o modelo que a manutenção da **Nortemec** usa para decidir se
abre uma ordem de manutenção preventiva num motor elétrico. Ele responde a uma
pergunta só:

> este motor vai falhar nas próximas 72 horas?

A entrada são leituras horárias de sensores. A saída é uma probabilidade e uma
decisão binária. **Está em produção desde maio de 2026** e ninguém nunca
escreveu um teste para ele.

**Você não vai construir este sistema. Você vai testá-lo.**

---

## Instalação

Precisa de Python 3.10+.

```bash
git clone https://github.com/felipehp/sentinela-nortemec.git sentinela
cd sentinela
pip install -e .
pip install pytest
```

No Google Colab:

```python
!git clone https://github.com/felipehp/sentinela-nortemec.git sentinela
%cd sentinela
!pip install -e . -q
```

Confira:

```python
import sentinela as sn

bruto = sn.dados.carregar("teste")
saida = sn.pipeline.executar(bruto, versao="v1")
print(sn.avaliacao.metricas(saida["falha_72h"], saida["predicao"]))
```

A inferência é **numpy puro** — os modelos são JSON, não pickle. Você não
precisa de scikit-learn para nada, exceto se quiser retreinar
(`pip install scikit-learn && python scripts/treinar.py`, opcional).

Se preferir não instalar nada, `pytest` rodado da raiz deste repositório já
enxerga o pacote (há um `conftest.py` que põe `src/` no `sys.path`).

---

## Os dados

Três conjuntos, em `dados/`, recortados em janelas de tempo consecutivas da
mesma planta:

| conjunto | período | linhas | o que é |
|---|---|---|---|
| `treino` | dias 1–28 | 16.800 | usado para treinar os modelos v1 e v2 |
| `teste` | dias 29–35 | 4.200 | usado para reportar o desempenho |
| `producao` | dias 36–42 | 4.200 | lote que rodou em produção, rotulado depois pela equipe |

25 motores, uma leitura por motor por hora.

> Os dados são **sintéticos**, gerados por um simulador da planta. O simulador
> **não** acompanha este repositório, de propósito: descobrir como os dados se
> comportam faz parte do trabalho. Nada aqui é apresentado como dado real de
> uma empresa real.

### Ficha técnica dos sensores (contrato de dados da planta)

| coluna | unidade | faixa de operação | observação |
|---|---|---|---|
| `temperatura_c` | °C | 45 – 95 | ruído do sensor: **± 1,0 °C** |
| `vibracao_rms` | mm/s | 1,2 – 8,0 | o sensor tem *dropout* conhecido; a leitura vem vazia |
| `pressao` | ver `unidade_pressao` | 3,0 – 4,5 bar | alguns CLPs da planta reportam em **psi** (1 bar = 14,5038 psi) |
| `corrente_a` | A | 12 – 30 | |
| `rpm` | rpm | 1.650 – 1.800 | leitura com o eixo parado não é medição válida |
| `idade_equipamento_meses` | meses | 6 – 180 | |
| `id_operador` | — | `OP-01`..`OP-12` | operador responsável pelo turno |
| `turno` | — | 1, 2, 3 | |
| `falha_72h` | — | 0 ou 1 | **alvo**: houve falha nas 72 h seguintes |

---

## Os modelos

Duas versões, ambas florestas de decisão, em `artefatos/`:

- **`v1`** — linha de base, em produção desde maio/2026. Floresta rasa,
  treinada com reponderação de classe.
- **`v2`** — candidata a substituir a v1. Floresta mais profunda, sem
  reponderação. **Ganhou +3,5 pontos percentuais de acurácia no conjunto de
  teste**, e por isso a equipe pretende promovê-la.

O limiar de decisão é `0.5` em todo o sistema.

---

## Interface pública

É isto que a sua suíte tem para segurar. Cada função é uma costura testável.

```python
import sentinela as sn

# --- dados ----------------------------------------------------------------
bruto = sn.dados.carregar("treino")        # "treino" | "teste" | "producao"

# --- etapas do pipeline ---------------------------------------------------
limpo = sn.preprocessamento.limpar(bruto)  # tipos, faltantes, normalização
X     = sn.features.construir(limpo)       # as 13 features, na ordem do modelo
sn.features.ORDEM_FEATURES                 # a ordem canônica

# --- modelo ---------------------------------------------------------------
modelo = sn.modelo.carregar("v1")          # "v1" | "v2"
modelo.prever_proba(X)                     # probabilidade por linha
modelo.prever(X, limiar=0.5)               # decisão binária
modelo.prever_registro({...})              # uma leitura só (painel da sala de controle)

# --- ponta a ponta --------------------------------------------------------
saida = sn.pipeline.executar(bruto, versao="v1", limiar=0.5)
# colunas: id_maquina, timestamp, probabilidade, predicao [, falha_72h]

# --- avaliação ------------------------------------------------------------
sn.avaliacao.matriz_confusao(y_real, y_predito)   # vp, vn, fp, fn
sn.avaliacao.metricas(y_real, y_predito)          # acurácia, precisão, recall, f1

# --- integridade ----------------------------------------------------------
sn.artefatos.verificar_manifest()          # [] quando dados e modelos batem com o manifest
```

`avaliacao` expõe só o que o painel da manutenção acompanha. Qualquer métrica
além dessas — PR-AUC, curva de calibração, intervalo de confiança, teste de
drift — você calcula na sua própria suíte. Isso é de propósito.

---

## Primeiro teste

Em `exemplos/test_exemplo.py` há três testes que passam. Rode:

```bash
pytest exemplos/ -v
```

Use como ponto de partida — e note que eles não provam quase nada. O trabalho
começa onde eles param.

---

## O que a Nortemec te contratou para fazer

Escrever a suíte de testes que este sistema nunca teve, e dizer o que ela
encontrou. **O sistema tem defeitos reais.** Alguns aparecem em cinco minutos;
outros só aparecem para quem formula uma hipótese e desenha o teste que a
mata.

Leia **`guia-do-aluno.md`** para o que entregar, como é avaliado e por onde
começar.

**Regra de ouro:** não edite o pacote `sentinela`. Você é o time de testes, não
o time de desenvolvimento. Um defeito encontrado se documenta com um teste que
falha — não com um `git commit` que o esconde.
