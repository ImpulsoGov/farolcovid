# SimulaCovid

Simulação do COVID-19 nos municípios brasileiros | Brazilian municipalities COVID-19 simuation.

Conteúdo e códigos baseados no repositório do <a href="https://github.com/alsnhll/SEIR_COVID19">Alison Hill</a>, e <a href="https://www.cappra.institute">Cappra Institute for Data Science</a>.

## Onde acessar?

Ambiente de testes e homologação:
- branch master -> https://simulacovid-staging.herokuapp.com/

Ambiente de produção:
- branch stable -> https://simulacovid.coronacidades.org/

## Como executar localmente?

Utilizando Python + Virtualenv

```bash
# Instale o 'make'
sudo apt-get install -y make

# Crie o virtualenv
make create-env

# Execute o servidor
make serve
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
