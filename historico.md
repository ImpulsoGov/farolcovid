# Histórico de Versões

## Lançamento v1.0: [29/05/2020 (github)](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2FImpulsoGov%2Ffarolcovid%2Fpull%2F120&sa=D&sntz=1&usg=AFQjCNEuTelAPKoViAjDio182ynQ2XfnUg)
Muitos e muitos rascunhos no Figma, pesquisa com gestores e especialistas para desenharmos os indicadores de acompanhamento da pandemia: junto ao SimulaCovid, adicionamos os cálculos de taxa de subnotificação e ritmo de contágio para criar o conjunto de indicadores de monitoramento da crise de Covid-19 em estados e municípios.

Ritmo de contágio: modelo bayesiano (vide metodologia no Farol)

Taxa de subnotificação: fazíamos o cálculo mais simples com base numa estimativa de ~2% de mortalidade de pessoas infectadas sintomáticas, e assim estima-se o total esperado de casos dado o número de mortes observado e a taxa de mortalidade.

Adicionamento à ferramenta também o índice de isolamento social da inloco porém, por falta de literatura e valores de referência, optamos por não torná-lo classificatório.

Arquivos:

Rascunhos de textos e imagens do Farol: https://docs.google.com/document/d/1JtTWaAkulzJUvMpNcMCUL33U0JZE3xcB

Metodologia de classificação Farol v1: https://docs.google.com/document/d/1kKwyw-hqz7beUYzHiPUouD_AnwAqYSIc

Metodologia de cálculo do Rt: https://docs.google.com/document/d/1limihgnYca59MJKH1W_6C7b8vDt-3JoY

## Lançamento v2.0 (Níveis de alerta): [01/09/2020 (github)](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2FImpulsoGov%2Ffarolcovid%2Fpull%2F204&sa=D&sntz=1&usg=AFQjCNH9h17uoUaZPJGZB62MASgUBWghGQ)
Esta versão teve muitas mudanças em si mesma. A maior de todas, revimos os nossos indicadores com base na metodologia de Níveis de Alerta adaptada da Vital Strategies. Mudamos de 3 indicadores classificatórios para 4, e definimos a qual dimensão cada indicador responde:*

Situação da doença (novo): média móvel de novos casos por 100mil hab.

Controle da doença: Ritmo de contágio

Capacidade hospitalar: Projeção de dias para atingir a capacidade máxima de leitos UTI (ver mais alterações em SimulaCovid)

Controle da doença: taxa de subnotificação, melhorada com metodologia em parceria ao Instituto Serrapilheira/ModCovid.

* Veja a metodologia de cada indicador na página Métodos, limitações e fontes do Farol

Além disso tivemos a adição dos mapas clicáveis, inspirados no CovidActNow (e insistência do João Abreu haha), para seleção de estados e municípios. A confecção do mapa também demorou bem mais do que imaginávamos dada a limitação de não ter suporte a JavaScript na versão do Streamlit usada (v0.60). Logo, criamos a nossa versão "hackeada" do Streamlit, com algumas alterações como essa.

 O mapa facilitou a visualização mas também causou um desconforto de início por expor a situação grave de disseminação no país - todos os estados em nível alto ou altíssimo, a maioria das cidades também. Como foram muitas mudanças de uma vez nessa versão, tivemos algumas reações de surpresa e reclamações quanto às alterações. Fica de aprendizado planejar bem as mudanças na ferramenta e deixar pré-avisado aos usuários elas.

Arquivos:

Documento sobre mudanças v2, dúvidas internas e de gestores: https://docs.google.com/document/d/1k-Udxm4Sxik3GRBVaM7qCJvdVrINIAqLrkI55JyCM4w

Documento de metodologia v2: https://docs.google.com/document/d/1XhFybPNJA6LCjzd5xg-2RNh-muHzaEDVRkhvUVTO4SY/edit?usp=sharing 

Notebook de revisão de mudanças v2 (internal_analysis): farolcovid_versions/draft_farol2.ipynb 

Tutorial de alterações no Streamlit: https://docs.google.com/document/d/1bJh2Tk76E2TP7X9HZYajOM21FLln_keD7H6Yq8tgq9g/edit?usp=sharing 



## Ajustes v2.1: [12/09/2020 (github)](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2FImpulsoGov%2Ffarolcovid%2Fpull%2F204&sa=D&sntz=1&usg=AFQjCNH9h17uoUaZPJGZB62MASgUBWghGQ)
Ajustamos os parâmetros do SimulaCovid, passando a usar taxa de hospitalização e mortalidade específicos com base na distribuição etária da população local (vide SimulaCovid) que já estávamos usando na taxa de subnotificação. Revertemos também o modelo de taxa de contágio (Rt) do EpiEstim para o anterior (bayesiano) pois o EpiEstim se mostrou muito sensível a pequenas variações nos casos diários.

Poucos dias (22/09) depois alteramos o front-end e atualizamos a metodologia com os pontos acima (ver pull request).

Arquivos:

Notebook de revisão de mudanças v2.1 (internal_analysis): farolcovid_versions/draft_farol_v2_review_20200915.ipynb 


## Ajustes v2.2: [18/12/2020 (github)](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2FImpulsoGov%2Ffarolcovid%2Fpull%2F230&sa=D&sntz=1&usg=AFQjCNFyp6cc8SfVS7xVeIlna4zpEP0w2w)
Com os problemas observados nos cálculos de projeção do SimulaCovid, decidimos trocar o indicador de capacidade para leitos UTI por 100 mil habitantes. Este indicador é mais estático (os dados de leitos atualizam mensalmente no DataSus/CNES) e portanto mais conservador do que a projeção dinâmica que usávamos. 

O problema de projeção ainda está em aberto (vide SimulaCovid).

Arquivos:

Valores de referência leitos UTI /100mil hab: https://docs.google.com/spreadsheets/u/1/d/1MKFOHRCSg4KMx5Newi7TYCrjtNyPwMQ38GE1wQ6as70
