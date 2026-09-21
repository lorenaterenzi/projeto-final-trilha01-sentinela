# Guia do aluno — Projeto Final, Trilha 1 (ML clássico)

---

## 1. O que você entrega

**a) Um repositório (ou notebook organizado) com a sua suíte de testes.**
Ele importa o pacote `sentinela` e testa o sistema de fora. Sugestão de
estrutura:

```
minha-suite/
  README.md            como rodar (é avaliado — critério 3)
  requirements.txt
  tests/
    test_preprocessamento.py
    test_features.py
    test_modelo.py
    test_estatistico.py
    test_adversarial.py
    test_pipeline.py
  relatorio.md         ou relatorio.pdf
```

**b) Um relatório.** O que você testou, **por quê**, e o que a suíte
encontrou — com **pelo menos uma falha real** do sistema, documentada. Inclua
evidência da suíte rodando (log do `pytest` colado, ou saída do notebook):
como não há apresentação, o relatório é o único lugar onde isso aparece.

---

## 2. Os três blocos obrigatórios da trilha

A rubrica cobra os três. Aqui está onde cada um encosta no Sentinela.

### Bloco A — Testes unitários do pipeline

Alvos: `preprocessamento.limpar` e `features.construir`.

Perguntas que rendem teste:

- `limpar()` promete tipos, faltantes tratados e rótulos normalizados. Ele
  cumpre? O que ele faz com um valor ausente — e esse valor faz sentido
  **fisicamente**, dada a ficha técnica do sensor no README?
- A ficha técnica declara faixas e unidades de operação. Os dados respeitam o
  contrato? Todas as colunas? (dica: valide `dados/`, não só o código)
- `features.construir` calcula janelas móveis por motor. Uma janela móvel tem
  uma propriedade que **precisa** valer sempre: o valor no instante `t` só pode
  depender de leituras até `t`. Como você escreve um teste que verifica isso?
- `construir()` recebe o quadro em qualquer ordem e promete devolver na ordem
  de entrada. Verifique. Embaralhe as linhas e compare.
- As features são funções determinísticas do lote? Rodar sobre um recorte e
  sobre o lote inteiro dá o mesmo valor para as linhas em comum?
- `Modelo.prever_registro` recebe um dicionário. Que contrato ele assume sobre
  esse dicionário — e o que acontece se você o violar sem perceber?

### Bloco B — Testes estatísticos

Alvos: `modelo`, `avaliacao`, e os três conjuntos de dados.

- A prevalência da classe positiva é de ~15% no teste. Um modelo que **nunca**
  prevê falha acerta 84,4% das vezes. A acurácia responde à pergunta da
  manutenção? Qual métrica responde?
- A v2 tem +3,5 pp de acurácia sobre a v1. Isso é uma melhoria? Prove — com
  intervalo de confiança (bootstrap) ou teste pareado (McNemar), não com dois
  números soltos. E veja **todas** as métricas antes de concluir: numa planta,
  um falso negativo é um motor queimado; um falso positivo é uma equipe
  deslocada à toa. Os dois custam a mesma coisa?
- O limiar é `0.5` porque alguém escreveu `0.5`. É o limiar certo? Varra o
  limiar e mostre o que acontece com precisão e recall.
- A probabilidade que o modelo devolve é uma probabilidade de verdade? Agrupe
  as predições por faixa e compare a probabilidade média prevista com a
  frequência de falha observada naquela faixa.
- O conjunto `producao` é posterior ao `teste`. As distribuições de entrada são
  as mesmas? Cuidado: **comparar médias pode não bastar.** Duas distribuições
  com a mesma média podem ser muito diferentes.

### Bloco C — Testes adversariais

Alvo: robustez das decisões.

- O sensor de temperatura tem ruído de ±1,0 °C (README). Uma perturbação
  **menor que o ruído do próprio sensor** pode mudar a decisão? Meça a taxa.
  Se pode, o que isso significa para uma ordem de manutenção?
- Perturbe uma feature por vez e descubra de quais o modelo mais depende.
  Alguma dessas dependências é **causalmente ilegítima** — uma variável que só
  tem aquele valor porque alguém já sabia da falha?
- Testes contrafactuais: pegue uma linha, mude **um único campo** que não
  deveria alterar o estado físico do motor, e verifique se a decisão se manteve.
  Quais campos entram nessa categoria?
- Casos-limite: leituras fora da faixa da ficha técnica, valores repetidos,
  lote com um motor só, lote com uma linha só.

---

Um defeito bem documentado tem quatro partes:

1. **O teste que falha** (código, executável)
2. **A evidência medida** — o número, não a impressão ("perturbar 0,4 °C muda
   1,3% das decisões", não "o modelo parece instável")
3. **A causa raiz** — o mecanismo, não o sintoma
4. **O impacto na planta** — o que isso custa para a manutenção da Nortemec

---

## 4. Regras

- **Não edite o pacote `sentinela`.** Você é o time de testes. Um defeito se
  documenta com um teste que falha, não com um commit que o some.
- **Corrigir é opcional e vale ponto** — mas só se vier acompanhado do teste
  que falhava antes da correção. Se for corrigir, faça em um patch/branch
  separado e explique no relatório. A ordem importa: primeiro o teste que
  falha, depois a correção que o faz passar.
- **Testes que passam também contam.** Parte do sistema está correta. Uma suíte
  que só tem testes vermelhos não distingue sinal de ruído.
- Individual ou em grupo, como no enunciado. Grupo declara os integrantes no
  relatório e todos participam do código.
- Ferramentas externas (Great Expectations, Deepchecks, Evidently, Fairlearn,
  Hypothesis, scipy) são bem-vindas, não obrigatórias, e não substituem
  entender a pergunta. Ver `00-material-de-consulta.md`.

---

## 5. Por onde começar

1. Rode `pytest exemplos/ -v` e confira que passa.
2. Rode o pipeline nos três conjuntos e anote acurácia, precisão, recall e F1
   de v1 e v2. Guarde essa tabela: é a linha de base de tudo.
3. Abra `dados/treino.csv` e confronte cada coluna com a ficha técnica do
   README. Escreva um teste para cada regra do contrato que der para checar.
4. Leia `features.py` inteiro, devagar, com a pergunta: *"o valor da linha `t`
   pode depender de alguma coisa que só se sabe depois de `t`?"*
5. Só então comece a escrever a suíte de verdade.

---
