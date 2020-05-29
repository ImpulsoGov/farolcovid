# Como fazer análises

**⚠️ Todos os passos abaixos devem ser seguidos em ordem para garantir a estabilidade do app! ⚠️**

1️⃣ [Criar um branch para suas análises](#1-criando-seu-branch)

2️⃣ [Ativar o ambiente virtual de modelagem](#2-ativando-ambiente-de-modelagem)

3️⃣ [Criar seu notebook em `analysis`](#3-criando-seu-notebook)

4️⃣ [Puxar os dados da API](#4-puxando-dados-da-api)

5️⃣ [Subir sua análise no repo via _pull request_](#5-subindo-análise-no-repositório)

## 1. Criando seu branch

Depois de clonar o repositório no seu computador, crie uma branch para desenvolver suas análises.

```bash
$ git checkout -b analysis_[usuario] # ex: git checkout -b analysis_fernandascovino
```

Caso já tenha passado um tempo que você criou o branch e queira subir outro notebook, lembre-se puxar as atualizações do `master` para seu branch:

```bash
$ git checkout analysis_[usuario] # ex: git checkout -b analysis_fernandascovino

$ git pull

$ git merge master

# Para checar as mudanças
$ git status
```

💬 Concentre suas análises nesse branch para evitar problemas de versionamento

## 2. Ativando ambiente de modelagem

```bash
# Instale o 'make'
$ sudo apt-get install -y make

# Crie o virtualenv
$ make create-env-analysis

# Ative o ambiente
$ . venvanalysis/bin/activate

# Abra o jupyter
$ jupyter notebook

# Mude o kernel do notebook para venvanalysis
```

## 3. Criando seu notebook

*Todos os notebooks devem estar na pasta `analysis`*. Para subir o notebook no repositório, o mesmo deve ter:

- Nomeclatuta: `[country]_[unit]_[content].ipynb` 
> ex: `br_states_rt_forecasting.ipynb`

- Primeira célula deve conter a descrição do notebook!

## 4. Puxando dados da API

Todos os dados da API podem ser acessados aqui: http://datasource.coronacidades.org:7000/v1/, veja a lista de tabelas [aqui](https://github.com/ImpulsoGov/simulacovid-datasource/blob/master/README.md).

⚠️ **Nunca suba tabelas para o repositório!** ⚠️

- Caso você use outros arquivos na sua análise, coloque dentro da pasta `analysis/data/raw`
- Caso você gere arquivos na sua análise, coloque dentro da pasta `analysis/data/output`


## 5. Subindo análise no repositório

Tudo pronto para mostrar suas análises para outr@s colaborador@s? Então, no sua cópia local, adicione os arquivos para criar o _pull request_:

```bash
# Veja o que você mudou, e verifique se você está na sua branch!
$ git status

# Adicione o notebook no track
$ git add analysis/[nome do notebook] # ex: git add analysis/br_states_rt_forecasting.ipynb

# Adicione uma msg sobre sua analise
$ git commit -m "[breve msg esplicando o que foi feito]" # ex: git commit -m "add analise de forecasting da taxa de contagio em ufs"

# Envie seu notebook para o GitHub subindo o seu branch!
$ git push --set-upstream origin analysis_[usuario] # ex: git push --set-upstream origin analysis_fernandascovino

```

Depois de dar `push`, você verá no GitHub um aviso em amarelo que seu branch foi modificado. Lá terá um botão para `Create pull request` - pronto!
