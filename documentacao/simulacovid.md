# Trajetória

## Links
v0 (DataStudio): https://datastudio.google.com/u/0/reporting/d8e3c475-fd12-4a3c-a4a7-4172fad41815/page/CgQm

## Ideia maluca: 17/03/2020
A ideia surgiu com a Ana Paula se perguntando porque ninguém ainda estava fazendo ferramentas para cálculo da capacidade do sistema de saúde.  
Porém , começou a se concretizar após uma conversa com o João Carabetta criando o [primeiro rascunho do simulador no Colab](https://colab.research.google.com/drive/1LiEj5S1AT403aFS9Yobf2dGUMaorq6jl#forceEdit=true&amp;sandboxMode=true) com um modelo simples SIR (Suscetiveis, Infectados e Recuperados) para ambos se convencerem que era a hora de voltar para o Brasil.

Arquivos:

Ideia inicial: https://medium.com/@joschabach/flattening-the-curve-is-a-deadly-delusion-eea324fe9727

Código do 1º rascunho: https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/



## Lançamento v0 (DataStudio): 29/03/2020
Uma vez convencido João Abreu sobre o potencial de uma ferramenta como essa, entraram no time a Fernanda e Diego apoiando no desenvolvimento/modelagem, Henrique e Sarah nas capturas de dados de leitos e entendimento da área (Sarah trabalha no Hospital Einstein). Nossa primeira versão saiu em um final de semana direto no DataStudio. Para colocar de pé nós:

Coletamos e armazenamos no Google Cloud os dados de leitos e ventiladores do CNES; casos e mortes do Brasil.io; e população do IBGE

Adaptamos para o [modelo SEIR da Alison Hill](https://drive.google.com/file/d/1wsoce_EyPeL0saQk6z45_sWG1JB9j9gk/view), utilizando parâmetros levantados por ela num compilado de diversos estudos, e considerando grupos de infectados  de demanda hospitalar (I1 - leves; I2 - severos/enfermaria; I3 - graves/ventiladores). 

Adicionamos a visão de 3 simulações possíveis com base no artigo de [Wang, C, et al. (2020)](https://www.medrxiv.org/content/10.1101/2020.03.03.20030593v1) sobre variação na taxa de contágio com 3 diferentes intervenções governamentais (isolamento parcial, lockdown e sem política de isolamento). 

Levantamos também outros artigos e modelos para embasar as mudanças no simulador, vide [metodologia](https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit#heading=h.12xk5raf9rty).

Arquivos:

Metodologia: https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/ 

Outras inspirações: http://gabgoh.github.io/COVID/index.html (Epidemic Calculator)



## Lançamento v1 (Streamlit): [08/04/2020 (stable) *](https://github.com/ImpulsoGov/farolcovid/pull/35)
Vimos que valia a pena investir na ideia, mas continuar no DataStudio limitava a flexibilidade de mudanças, impedindo a melhoria da experiência de usuário. Surgiu então o Saru na história, nosso expert em FE/UX, que nos ajudou a montar um site oficial para o SimulaCovid. Foram algumas semanas para todo o processo, mas muita coisa feita:

O Saru criou inicialmente um mock no Figma o qual usamos para o FE da ferramenta

Montamos todo o backend utilizando o Streamlit e publicamos o código no Github. 

Pouco tempo depois [(final de abril)](https://github.com/ImpulsoGov/farolcovid/pull/83) criamos também a nossa API de dados para alimentar a aplicação com os dados antes salvos no Drive. Estes passaram a ser atualizados na API de 15 em 15 minutos.



## Lançamento v1.1 (FarolCovid): [10/06/2020 (stable) *](https://github.com/ImpulsoGov/farolcovid/pull/140)
Nesta nova versão do Simula mudamos as 3 simulações que tínhamos antes, com 3 diferentes ritmos de contágio, para uma única simulação com o ritmo de contágio calculado a nível local. Assim como antes, usamos o intervalo de confiança de 95% para indicar o melhor cenário (menor Rt, limite inferior) e o pior cenário (maior Rt, limite superior) dadas as mesmas informações passadas pelo(a) gestor(a).

Além disso, alteramos valores de capacidade hospitalar, como segue na metodologia do SimulaCovid v1.1 disponível no Farol:

"Dada a evolução do Covid nos município e estados brasileiros desde a versão anterior da metodologia,  e a resposta dos governos com a construção e obtenção de novos recursos hospitalares, modificamos também o percentual de leitos e ventiladores SUS e não-SUS disponíveis para a Covid de 20% para 50%. Os leitos disponíveis para Covid considerados são os tipos de leitos cirúrgicos, clínicos e hospital-dia. Atualizamos os dados de leitos e ventiladores com base na última versão do DataSUS de abril/2020. "



## Lançamento v1.2 (Farol v2.0): [01/09/2020 (stable) *](https://github.com/ImpulsoGov/farolcovid/pull/193)
As atualizações do SimulaCovid v1.3 foram incorporadas a um conjunto maior de atualizações para o lançamento do FarolCovid v.2. Desde início de junho, o SimulaCovid já tinha deixado de ser o carro-chefe do site, e passou a ser um produto agregado. 

As grandes mudanças foram:

Passarmos a considerar o cálculo de casos estimados ativos e adicionarmos isso no modelo; 

Alteramos ventiladores para leitos UTI como demanda hospitalar de casos críticos (I3);

Considerar o cálculo par apenas regionais de saúde e estados, e não mais municípios, dado que os leitos UTI são concentrados nos pólos das regiões de saúde de cada estado.

Junto a isto, também alterarmos metodologia da taxa de contágio (Rt) para um modelo em R, EpiEstim, mas posteriormente revertemos esta alteração por se apresentar um modelo muito sensível a pequenas oscilações no número de casos diários.



## Ajustes v1.3 (Parâmetros locais): [12/09/2020 *](https://github.com/ImpulsoGov/farolcovid/pull/204)
Alteramos os parâmetros de hospitalização e mortalidade utilizados do compilado de estudos feito pela Alison Hill para parâmetros mais refinados. Estes parâmetros são calculados com base na distribuição etária de cada estado/regional de saúde e a probabilidade de hospitalização de cada faixa derivadas do estudo de [Verity et. al (2019)](https://www.medrxiv.org/content/10.1101/2020.03.09.20033357v1), também utilizado para o cálculo da taxa de subnotificação de casos.

Arquivos:

Notebook de teste dos novos parâmetros: https://github.com/ImpulsoGov/internal_analysis/blob/master/seir_model/analysis_20200909.ipynb 

* Todas as alterações estão descritas também em src/pages/model_description.py no link da respectiva data.



## Problemas enfrentados
Desde final de 2020 notamos que o modelo passou a calcular valores muito abaixo do que observamos na realidade - dizemos que o modelo estava "sobrehospitalizando" a projeção de casos de Covid-19. Isso foi observado primeiramente nas estimativas dos estados que sempre indicavam + de 30 dias (novo normal) para atingir da capacidade máxima de leitos UTI. Além dessa observação, vimos em outros modelos e pesquisas que muitos deixaram de performar bem devido a alterações de tratamento (positivamente uma melhoria) e na própria disseminação do vírus que mudaram o comportamento da evolução dos quadros hospitalares.

Coletamos os dados de ocupação dos 27 estados para validação, mas conseguimos somente 3 estados com dados históricos para testar nossa hipótese.

Arquivos:

Levantamento de dados de ocupação de leitos enfermaria e UTI dos estados: https://docs.google.com/spreadsheets/d/1xYqjrdxiUCt8rF-6A6xg3BRkrHW6PHVCTwvFC9uIPjs/edit?usp=sharing 

Notebook e dados utilizados para verificação da sobrehospitalização: https://github.com/ImpulsoGov/internal_analysis/tree/master/seir_model/review_20201214 
