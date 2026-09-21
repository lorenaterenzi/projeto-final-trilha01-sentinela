# Suíte de Testes Automatizados — Sistema Sentinela (Nortemec)

**Disciplina:** Testes Automatizados para Modelos de IA  
**Projeto Final (Trilha 1 — ML Clássico)**

---

## 1. Visão Geral
Este repositório contém a suíte externa de testes automatizados para o sistema **Sentinela** (manutenção preditiva industrial de motores elétricos). O objetivo é validar contratos de dados, estabilidade estatística, robustez adversarial e identificar defeitos do pipeline sem modificar o pacote `sentinela`.

---

## 2. Estrutura dos Testes

- `tests/test_01_preprocessamento.py`: Validação de contratos de dados, checagem de nulos e conversão de unidades (bar vs. PSI).
- `tests/test_02_features.py`: Verificação de ordenação de linhas e testes de vazamento temporal (*data leakage*).
- `tests/test_03_estatistico.py`: Avaliação de Falsos Negativos entre v1 e v2 e calibração de probabilidades.
- `tests/test_04_adversarial.py`: Testes de sensibilidade ao ruído térmico e testes contrafactuais (`id_operador`).

---

## 3. Como Executar os Testes

Para executar a suíte de testes do zero no seu computador, siga o passo a passo abaixo no terminal do VS Code:

### 1. Clonar o repositório
```powershell
git clone https://github.com/lorenaterenzi/projeto-final-trilha01-sentinela.git
cd projeto-final-trilha01-sentinela
```

### 2. Criar e ativar o ambiente virtual (Python)
- Criar o ambiente virtual na pasta venv:
```bash
python -m venv venv 
 ```

- Ativar o ambiente virtual:
``` bash
# No Windows (PowerShell):
.\venv\Scripts\activate

# No Linux ou macOS:
source venv/bin/activate
```
(Certifique-se de que o prefixo (venv) apareceu no início da linha do terminal).

### 3. Instalar o pacote Sentinela e as dependências
- Instalar o pacote sentinela em modo editável:
```bash
pip install -e .
```
- Instalar as ferramentas de teste e análise de dados:
```bash
pip install pytest pandas numpy
```
### 4. Executar a suíte completa de testes
Com o ambiente virtual ativo e as dependências instaladas:

```bash
pytest -v
```

## 4. Log de Execução da Suíte
```powershell
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 12 items

exemplos/test_exemplo.py::test_artefatos_batem_com_o_manifest PASSED      [  8%]
exemplos/test_exemplo.py::test_features_preservam_linhas_e_ordem_das_colunas PASSED [ 16%]
exemplos/test_exemplo.py::test_pipeline_devolve_decisao_binaria_para_cada_leitura PASSED [ 25%]
tests/test_01_preprocessamento.py::test_faixa_e_unidade_pressao_contrato_dados FAILED [ 33%]
tests/test_01_preprocessamento.py::test_respeito_faixa_temperatura PASSED      [ 41%]
tests/test_01_preprocessamento.py::test_sem_valores_ausentes_apos_limpeza PASSED [ 50%]
tests/test_02_features.py::test_sem_vazamento_temporal_features PASSED          [ 58%]
tests/test_02_features.py::test_invariancia_ordem_linhas_features PASSED          [ 66%]
tests/test_03_estatistico.py::test_comparacao_v1_vs_v2_falsos_negativos_criticos FAILED [ 75%]
tests/test_03_estatistico.py::test_calibracao_probabilidades PASSED                      [ 83%]
tests/test_04_adversarial.py::test_estabilidade_ruido_menor_que_sensor FAILED            [ 91%]
tests/test_04_adversarial.py::test_contrafactual_id_operador_nao_altera_decisao FAILED   [100%]

========================= 4 failed, 8 passed in 3.02s =========================
```
