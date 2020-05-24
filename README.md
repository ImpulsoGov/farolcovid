# SimulaCovid

<p align="left">
<!-- <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a> -->
<a href="https://github.com/ImpulsoGov/simulacovid-datasource/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/ImpulsoGov/simulacovid"></a> <a href=""><img alt="Master update" src="https://img.shields.io/github/last-commit/ImpulsoGov/simulacovid/master?label=last%20commit%20%28master%29"></a> <a href=""><img alt="Master update" src="https://img.shields.io/github/last-commit/ImpulsoGov/simulacovid/stable?label=last%20updated%20%28stable%29"></a> <a href=""><img alt="Deploy" src="https://img.shields.io/github/deployments/ImpulsoGov/simulacovid/simulacovid-production?label=deploy%20status%20%28stable%29"></a>
</p>

Simulação do COVID-19 nos municípios brasileiros | Brazilian municipalities COVID-19 simulation.

Conteúdo e códigos baseados no repositório do <a href="https://github.com/alsnhll/SEIR_COVID19">Alison Hill</a>, e <a href="https://www.cappra.institute">Cappra Institute for Data Science</a>.

## Onde acessar?

Ambiente de testes e homologação:
- branch master -> https://simulacovid-staging.herokuapp.com/

Ambiente de produção:
- branch stable -> https://simulacovid.coronacidades.org/

## 📊 Como colaborar com análises

Todas as análises com dados da ferramenta estão em [`analysis`](/analysis). Veja como colaborar [aqui](/src/analysis/README.md)!


## ⚙️ Como executar a aplicação localmente?

Utilizando Python + Virtualenv

```bash
# Instale o 'make'
sudo apt-get install -y make

# Crie o virtualenv
make create-env

# Execute o servidor com API externa
make serve

# Execute o servidor com API local. 
# Para isso, você terá que subir a API do simulacovid-datasource
# 1. Para subir o servidor local: `make server-build-run`
# 2. Abra outro terminal e rode para subir os dados: `make loader-build-run`
make serve-local
```

Utilizando o Docker (Linux)

```bash
# Instale o Docker
curl -sSL https://get.docker.com | sudo sh

# Instale o 'make'
sudo apt-get install -y make

# Execute o servidor
# ficará disponível em http://localhost:8501/
make docker-build-run
```
