# Modelagem de dados do Airbnb com aplicação de MLOps 

<img src="images/header.png" alt="mlops pipeline">

Este projeto está sendo desenvolvido como atividade prática na disciplina IMD1123 (Tópicos Especiais em Inteligência Computacional / MLOps) e visa implementar um pipeline de MLOps para modelagem preditiva de preços de imóveis do Rio de Janeiro anunciados no Airbnb (dez/2021).

As seguintes etapas serāo desenvolvidas:
- Fetch Data :heavy_check_mark:
- Pre-processing :heavy_check_mark:
- Data Checks :heavy_check_mark:
- Data Segregation (train/test splitting) :heavy_check_mark:
- Define and create a ML model
- Train and validation
- Test
- Store in Model Registry

## Requisitos

Certifique-se de atender aos seguintes requisitos:

* Ter instalado `conda 4.8.2 | Python 3.7 ou maior`.
* Ter uma máquina com `Windows | Linux | Mac`.
* Possuir uma conta [wandb](https://wandb.ai/site).

Aqui utilizamos fortemente a ferramenta [wandb](https://wandb.ai/site) para acompanhar o versionamento e os artefatos gerados em cada etapa do workflow.


## Instalação

Certifique-se que você está na pasta que contém o arquivo environment.yml quando for executar o comando no terminal.

Crie o ambiente do projeto:
```
conda env create -f environment.yml
```

Ative o ambiente criado:
```
conda activate mlops
```

## Passo-a-passo

Cada pasta contém um arquivo README com comandos que devem ser executados.

### 1- Análise exploratória de dados no jupyterlab

Na pasta *EDA*, o é gerado o artefato row_data.csv no wandb e são realizadas várias análises para conhecer melhor os dados trabalhados através de um notebook.

### 2- Pré-processamento

Na pasta *preprocessing*, é realizada a limpeza dos dados conforme a análise realizada no passo anterior.

### 3- Segregação dos dados

Na pasta *split_data*, é feita a separação de dados em treino e teste.

### 4- Checagem dos dados

Na pasta *data_checks*,realizamos testes de hipótese para checar se os dados falseiam ou falham em falsear as hipóteses levantadas.
