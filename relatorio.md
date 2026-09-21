# Relatório Técnico de Avaliação e Testes Automatizados — Sistema Sentinela

**Trilha:** 1 — ML Clássico (Manutenção Preditiva Industrial)  

---

## 1. Resumo Executivo
Este relatório apresenta os resultados da avaliação de qualidade, integridade de dados, estabilidade estatística e robustez do sistema **Sentinela**. A suíte de testes desenvolvida identificou falhas operacionais e conceituais críticas no pipeline de dados e na transição do modelo v1 para o modelo candidato v2.

---

## 2. Análise dos Defeitos Encontrados por Bloco

### Bloco A — Testes Unitários do Pipeline (`test_01_preprocessamento.py` e `test_02_features.py`)
1. **Incompatibilidade de Unidades no Contrato de Dados (Pressão):**
   - **Achado:** A coluna `pressao` no conjunto de `treino` apresentou valor máximo de $65{,}32$, indicando a presença de medições em **PSI** sem a devida conversão para **bar** ($3{,}0$ a $4{,}5 \text{ bar}$, conforme contrato do sensor).
   - **Impacto:** O pipeline passa dados fora da escala física esperada para o modelo, distorcendo a inferência.

### Bloco B — Testes Estatísticos (`test_03_estatistico.py`)
1. **Explosão de Falsos Negativos na Promoção do Modelo v2:**
   - **Achado:** No conjunto de teste ($4.200$ linhas), o modelo **v1** gerou **38 Falsos Negativos**, enquanto o modelo candidato **v2** gerou **122 Falsos Negativos**.
   - **Causa Raiz:** O modelo v2 foi treinado sem reponderação de classe (`class_weight`), otimizando a acurácia global ao custo de ignorar a classe rara de falha ($\approx 15\%$).
   - **Impacto Industrial:** A promoção da v2 causaria a quebra sem aviso de 84 motores adicionais no período, gerando prejuízos operacionais gravíssimos.

### Bloco C — Testes Adversariais (`test_04_adversarial.py`)
1. **Instabilidade por Ruído Inferior à Tolerância do Sensor:**
   - **Achado:** Uma variação sutil de $+0{,}3 \text{ °C}$ na temperatura (menor que o ruído especificado do sensor de $\pm 1{,}0 \text{ °C}$) alterou a decisão de manutenção em **44 motores** ($1{,}05\%$ das predições).
   - **Impacto:** Ordens de manutenção preventiva seriam emitidas ou canceladas por conta de ruído térmico irrelevante.

2. **Viés Causal Espúrio (`id_operador`):**
   - **Achado:** A alteração exclusiva do atributo `id_operador` para `OP-12` alterou **18 predições** de falha em motores com parâmetros físicos idênticos.
   - **Impacto:** A decisão do modelo depende do operador registrado no turno, caracterizando dependência causalmente ilegítima.

---

## 3. Documentação Detalhada do Defeito Crítico Selecionado

* **Falha Documentada:** *Aumento Expressivo de Falsos Negativos no Modelo v2 (Inviabilidade de Deploy).*
* **Teste de Código:** `tests/test_03_estatistico.py::test_comparacao_v1_vs_v2_falsos_negativos_criticos`
* **Evidência Medida:** O número de Falsos Negativos subiu de 38 (v1) para 122 (v2), representando um aumento de $221\%$ em falhas não detectadas.
* **Causa Raiz:** Ausência de tratamento de desbalanceamento de classes no treinamento do modelo v2.
* **Impacto Operacional:** Riscos de queima de motores na linha de produção da Nortemec e prejuízos operacionais elevados.