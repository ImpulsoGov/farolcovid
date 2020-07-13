import streamlit as st
import amplitude
import utils


def main():
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.log_event("opened saude_em_ordem_description")
    st.header("""Saúde em Ordem""")
    st.subheader("""1. Introdução""")
    st.write(
        """
    Idealmente, gostaríamos que todo processo de retomada gradual econômica começasse pela reabertura daqueles setores que proporcionam menores riscos à saúde pública por um lado, e maior importância econômica por outro. Assim, se em um primeiro momento o trade-off entre saúde e economia não existe pois são os indicadores de saúde que devem indicar se é, ou não, o momento certo para iniciar um processo de retomada, uma vez iniciado este processo, a tensão entre saúde e economia passa a existir.

    Cabe aqui esclarecer que quem define se é o momento de retomada da economia são os indicadores de saúde (ver Farol Covid para saber se é o caso do seu município). De todo modo, é fundamental planejar este processo para que quando chegue o momento não haja confusão e dúvidas. A ideia aqui é apresentar uma metodologia desenvolvida no âmbito do Grupo Técnico de Atividade Econômica do Comitê de Dados da Secretaria de Planejamento, Orçamento e Gestão do Estado do Rio Grande do Sul para ordenar os setores econômicos do estado em fases de abertura de acordo com seu risco de contágio e sua importância econômica.

    O modelo aqui apresentado traz algumas variações em relação ao modelo utilizado no Rio Grande do Sul por estar desenhado pensando em sua utilização para todos os estados da federação e levar em consideração também informações sobre o mercado de trabalho informal.
    """
    )
    st.subheader("2. Dados")
    st.write(
        """
    Para a construção dessa ferramenta utilizamos bases de dados públicas e o trabalho realizado pela equipe do Grupo Técnico de Atividade Econômica da Seplag-RS. 
    
    Os dados utilizados para dimensionar a massa salarial do mercado de trabalho formal são da Secretaria Especial de Previdência e Trabalho do Ministério da Economia e são provenientes dos microdados da Relação Anual de Informações Sociais (RAIS) de 2019. Para acessar o mercado de trabalho informal foram utilizados os microdados da Pesquisa Nacional Domiciliar Contínua de 2019 do IBGE.
    
    Para calcularmos o índice de segurança foram utilizados dados do Departamento Americano de Trabalho e Emprego referentes à pesquisa *Occupational Information Network* (O*Net). Essa pesquisa traz características das ocupações e do contexto em que estão inseridas.

    """
    )
    st.subheader("3. Metodologia")
    st.write(
        """
    #### a. índice de importância econômica

    Como medida de importância econômica utiliza-se a massa salarial setorial, que representa a soma de todos os salários pagos em um mês para os trabalhadores de casa setor da economia. A escolha dessa variável para representar a importância econômica de uma atividade se deve principalmente a dois fatores: em primeiro lugar é uma variável que reflete bem o impacto econômico de uma atividade na sociedade e em segundo lugar as informações necessárias para a construção de tal variável são públicas e disponíveis na RAIS e na PNADc.
    
    Cabe, todavia, destacar um aspecto negativo da escolha desta variável. Ao priorizarmos setores com maior massa salarial no processo de retomada econômica estamos potencialmente priorizando aqueles setores que mais empregam, de modo que é necessário que sejam adotados protocolos específicos para garantir que a mobilidade desses indivíduos no espaço urbano não gere situações que favoreçam o contágio.
    
    Como a RAIS reporta os dados de todos os trabalhadores formais do país, é possível calcular a média dos salários de cada ocupação em cada atividade de modo que a massa salarial é na verdade é a multiplicação dos salários de cada ocupação naquela atividade ponderada pelo número de empregados daquela ocupação que trabalham naquela atividade.
    
    Os dados da RAIS trazem informações sobre o mercado de trabalho formal por ocupação e atividade. Então é possível saber, potencialmente para cada município brasileiro, o número de empregados de cada ocupação e setor e sua remuneração. Todavia, sabemos que a informalidade ainda é um problema relevante em muitos estados brasileiros. Assim, utilizando os dados da PNADc estimamos a informalidade e a remuneração média por atividade e UF. 
    
    Para realizar esta estimação, os dados da PNADc, que é uma pesquisa amostral, foram expandidos utilizando os pesos populacionais de cada observação fornecidos pelo IBGE. Para cada atividade e Estado, foram considerados empregados informais aqueles que satisfizessem pelo menos uma das seguintes condições:

    - Empregado no setor privado sem carteira de trabalho assinada
    - Empregado doméstico sem carteira de trabalho assinada
    - Trabalhador familiar auxiliar
    - Empregador sem CNPJ
    - Conta própria sem CNPJ

    De modo a considerar, para cada atividade, os setores formal e informal do mercado de trabalho de cada estado o número de trabalhadores informais com base na PNADc foi somado ao número de trabalhadores formais da RAIS. Da mesma maneira, a massa salarial considerada é a soma dos valores do mercado de trabalho formal e informal.
    
    Para o cálculo referente às regionais de saúde, faz-se a análise por municípios, que são agrupados em regionais de saúde. No caso da informalidade, utiliza-se a taxa de informalidade por atividade do estado em que a regional se encontra.

    #### b. índice de segurança

    Para construir uma medida que representasse o risco de funcionamento de cada atividade recorremos à pesquisa O\*NET que traz informações sobre a exposição da ocupação a doenças e infecções e intensidade e extensão de contatos físicos no ambiente de trabalho. Assim, as ocupações americanas foram classificadas de acordo com o risco de contágio que proporcionam com base na metodologia desenvolvida por Lima et al (2020) e Gamio (2020). Todavia, como as ocupações americanas estão codificadas usando o *Standard Occupational Classification* foi necessário utilizar o método desenvolvido por Sulzbach (2020) para realizar a tradução dessa classificação para o Código de Ocupações Brasileiras.
    
    Assim, chega-se a uma medida de risco para cada ocupação e para calcular o risco de cada atividade faz-se uma média do risco das ocupações naquela atividade ponderada pelo número de trabalhadores de cada ocupação. Portanto a medida de risco de uma atividade é específica para cada Estado, uma vez que a distribuição de ocupações por atividade varia de Estado para Estado.
    
    Por fim, como gostaríamos de ter uma medida de segurança e não uma medida de risco, aplica-se a seguinte transformação monotônica:

    $$S_i=100-R_i$$

    em que $$R_i$$ é a nossa medida de risco e $$S_i$$ é a medidade de segurança. Desse modo a medida de segurança varia entre 100 (atividade mais segura) e 0 (atividade menos segura).
    
    Cabe ressaltar que consideramos uma atividade como mais segura se ela exige menos proximidade entre indivíduos e expõe menos os trabalhadores a doenças e infecções.
    
    ### c. Ordenamento setorial

    A partir das duas dimensões descritas acima e seguindo o que foi proposto pelo Grupo Técnico de Atividade Econômica da Seplag-RS, o índice de ordenamento setorial é construído a partir de uma média geométrica que pondera essas duas dimensões de acordo com a preferência do *policymaker*, que atribui um peso entre zero e um à uma das dimensões e o peso complementar à outra dimensão.
    """
    )
    st.subheader("Referências")
    st.write(
        """
    G. Stein, V. N. Sulzbach and Lazzari. Nota Técnica sobre o Índice Setorial para Distanciamento Controlado. Technical report, 2020
    
    Lazaro Gamio. The workers who face the greatest coronavirus risk, 2020. https://www.nytimes.com/interactive/2020/03/15/business/economy/coronavirus-worker-risk.html.
    
    Y. O. de Lima, D. M. Costa, and J. M. de Souza. Covid-19: Risco de contágio por ocupação no Brasil: Nota metodológica. Technical report, 2020. 
    
    Vanessa Neumann Sulzbach. Essays on Labor Market Polarization in Brazil. Unpublished PhD’s Thesis, 2020. 
    """
    )
