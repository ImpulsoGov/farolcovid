# FarolCovid 🚦

<p align="left">
  <!-- <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a> -->
  <a href="https://github.com/ImpulsoGov/simulacovid-datasource/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/ImpulsoGov/simulacovid"></a>
  <a href=""><img alt="Master update" src="https://img.shields.io/github/last-commit/ImpulsoGov/simulacovid/master?label=last%20commit%20%28master%29"></a>
  <a href=""><img alt="Master update" src="https://img.shields.io/github/last-commit/ImpulsoGov/simulacovid/stable?label=last%20updated%20%28stable%29"></a>
  <a href=""><img alt="Deploy" src="https://img.shields.io/github/deployments/ImpulsoGov/simulacovid/simulacovid-production?label=deploy%20status%20%28stable%29"></a>
  <a href="https://hub.docker.com/repository/docker/impulsogov/farolcovid"><img alt="docker build" src="https://img.shields.io/docker/cloud/build/impulsogov/farolcovid"></a>
</p>

Ferramenta de monitoramento do risco de colapso no sistema de saúde em municípios brasileiros com a Covid-19.

_Monitoring tool & simulation of the risk of collapse in Brazilian municipalities' health system due to Covid-19._


## Fontes de dados

Os dados utilizados na ferramenta estão na nossa [API](http://datasource.coronacidades.org/br/), cujas fontes são:
- [Brasil.IO](http://brasil.io)
- [DataSUS](https://datasus.saude.gov.br/)

Veja mais detalhes na página de Metodologia da ferramenta.

## Referências metodológicas

Os modelos e respectivos códigos utilizados são baseados no trabalho de <a href="https://github.com/alsnhll/SEIR_COVID19">Alison Hill</a> e <a href="https://www.cappra.institute">Cappra Institute for Data Science</a> (modelo SEIR), e [Kevin Systrom (ritmo de contágio)](https://github.com/k-sys/covid-19/blob/master/Realtime%20R0.ipynb), além de diversos estudos utilizados na nossa metodologia:

- CDC, 2019. Severe Outcomes Among Patients with Coronavirus Disease 2019 (COVID-19) — United States, February 12–March 16, 2020. MMWR Morb Mortal Wkly Rep. ePub: 18 March 2020. DOI: http://dx.doi.org/10.15585/mmwr.mm6912e2.

- Li, R., Pei, S., Chen, B., Song, Y., Zhang, T., Yang, W., & Shaman, J., 2020. Substantial undocumented infection facilitates the rapid dissemination of novel coronavirus (SARS-CoV2). Science, 3221(March), eabb3221. DOI: https://doi.org/10.1126/science.abb3221

- Wang, C, et al. (2020) Evolving Epidemiology and Impact of Non-pharmaceutical Interventions on the Outbreak of Coronavirus Disease 2019 in Wuhan, China. DOI: https://doi.org/10.1101/2020.03.03.20030593 e pdf de apresentação https://docs.google.com/presentation/d/1-rvZs0zsXF_0Tw8TNsBxKH4V1LQQXq7Az9kDfCgZDfE/edit#slide=id.p1

- Wang, J., Zhou, M., & Liu, F., 2020. Reasons for healthcare workers becoming infected with novel coronavirus disease 2019 (COVID-19) in China. Journal of Hospital Infection. DOI: https://doi.org/10.1016/j.jhin.2020.03.002

Veja mais detalhes na página de Metodologia da ferramenta.

## 📊 Como colaborar com análises

**Estamos migrando as análises para outro repositório!** Veja mais em [`coronacidades-analysis`](https://github.com/ImpulsoGov/coronacidades-analysis) 😉


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
