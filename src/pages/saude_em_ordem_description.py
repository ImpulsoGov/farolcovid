import streamlit as st
import amplitude
import utils


def main(session_state):
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.safe_log_event(
        "opened saude_em_ordem_description", session_state, is_new_page=True
    )
    st.header("""Saúde em Ordem""")
    st.subheader("""1. Introdução""")
    st.write(
        """
    Essa ferramenta propõe que a ordem de retomada econômica nas cidades e estados brasileiros seja guiada por critérios objetivos. Poderiam ser observadas uma série de dimensões sócio-econômicas, como a quantidade de pessoas impactadas e critérios de desigualdade de renda e de gênero, conforme sugerido pela Vital Strategies.  No Saúde em Ordem, seguindo modelo do Grupo Técnico de Atividade Econômica do Comitê de Dados da Secretaria de Planejamento, Orçamento e Gestão do Estado do Rio Grande do Sul, consideramos dois desses critérios -- setores que proporcionam menores riscos à saúde pública e maior importância econômica por outro. 
    
    Cabe esclarecer que o momento de iniciar a retomada da economia é definido pelo Nível de Risco (ver Farol Covid para saber se é o caso do seu município). Sugerimos que a retomada comece apenas quando ele esteja baixo e que os indicadores sejam revisados a cada 14 dias. De todo modo, é fundamental planejar este processo para que quando chegue o momento não haja confusão e dúvidas.
    
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
    
    Por fim, como gostaríamos de ter uma medida de segurança e não uma medida de risco, aplica-se a seguinte transformação monotônica:"""
    )

    st.latex("S_i=100-R_i")
    st.write(
        """
    em que $$R_i$$ é a nossa medida de risco e $$S_i$$ é a medidade de segurança. Desse modo a medida de segurança varia entre 100 (atividade mais segura) e 0 (atividade menos segura).
    
    Cabe ressaltar que consideramos uma atividade como mais segura se ela exige menos proximidade entre indivíduos e expõe menos os trabalhadores a doenças e infecções.
    
    Ao analisarmos os microdados da PNAD-Covid do IBGE, nota-se que a prevalência de sintomas da Covid-19 é maior entre a população informal do que para a população formal, como mostramos na tabela abaixo. De maneira geral, a presença desses sintomas é 15% maior entre os informais, de modo que aumentamos o risco de contágio para esses indivíduos em 15%."""
    )
    gen_table()
    st.write(
        """
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


def gen_table():
    st.write(
        """
        <style type="text/css">
        .tg  {border-collapse:collapse;border-spacing:0;}
        .tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
        overflow:hidden;padding:10px 5px;word-break:normal;}
        .tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
        font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
        .tg .tg-ywcv{background-color:#ffe784;text-align:right;vertical-align:top}
        .tg .tg-1wig{font-weight:bold;text-align:left;vertical-align:top}
        .tg .tg-73b2{background-color:#e9e482;text-align:right;vertical-align:top}
        .tg .tg-xlz7{background-color:#f8696b;border-color:inherit;text-align:right;vertical-align:top}
        .tg .tg-i6ea{background-color:#f8696b;text-align:right;vertical-align:top}
        .tg .tg-2adx{background-color:#fb9474;text-align:right;vertical-align:top}
        .tg .tg-oljo{background-color:#fb9374;text-align:right;vertical-align:top}
        .tg .tg-mc3u{background-color:#c7da80;text-align:right;vertical-align:top}
        .tg .tg-28u1{background-color:#ccdc81;text-align:right;vertical-align:top}
        .tg .tg-te1u{background-color:#f8e983;text-align:right;vertical-align:top}
        .tg .tg-lqy6{text-align:right;vertical-align:top}
        .tg .tg-jh8w{background-color:#fcb279;text-align:right;vertical-align:top}
        .tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}
        .tg .tg-7btt{border-color:inherit;font-weight:bold;text-align:center;vertical-align:top}
        .tg .tg-amwm{font-weight:bold;text-align:center;vertical-align:top}
        .tg .tg-fymr{border-color:inherit;font-weight:bold;text-align:left;vertical-align:top}
        .tg .tg-0lax{text-align:left;vertical-align:top}
        .tg .tg-3i13{background-color:#63be7b;border-color:inherit;text-align:right;vertical-align:top}
        .tg .tg-4cwk{background-color:#63be7b;text-align:right;vertical-align:top}
        .tg .tg-balj{background-color:#ffdc81;text-align:right;vertical-align:top}
        .tg .tg-405e{background-color:#77c47c;text-align:right;vertical-align:top}
        </style>
        <table class="tg" style="undefined;table-layout: fixed; width: 509px;margin:auto;">
        <colgroup>
        <col style="width: 168px">
        <col style="width: 98px">
        <col style="width: 93px">
        <col style="width: 150px">
        </colgroup>
        <thead>
        <tr>
            <th class="tg-0pky"></th>
            <th class="tg-7btt">Informal</th>
            <th class="tg-7btt">Formal</th>
            <th class="tg-amwm">Diferença entre Informal e Formal</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td class="tg-fymr">Número de Individuos</td>
            <td class="tg-0lax">33.148.871</td>
            <td class="tg-0pky">52.230.690</td>
            <td class="tg-0lax"></td>
        </tr>
        <tr>
            <td class="tg-fymr">Febre</td>
            <td class="tg-xlz7">3,0%</td>
            <td class="tg-3i13">2,4%</td>
            <td class="tg-oljo">25,4%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Tosse</td>
            <td class="tg-i6ea">4,2%</td>
            <td class="tg-4cwk">3,7%</td>
            <td class="tg-73b2">12,3%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dor de garganta</td>
            <td class="tg-i6ea">3,4%</td>
            <td class="tg-4cwk">3,1%</td>
            <td class="tg-mc3u">9,2%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dificuldade de respirar</td>
            <td class="tg-i6ea">2,0%</td>
            <td class="tg-4cwk">1,7%</td>
            <td class="tg-balj">16,3%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dor de cabeça</td>
            <td class="tg-i6ea">7,1%</td>
            <td class="tg-4cwk">7,0%</td>
            <td class="tg-405e">2,0%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dor peito</td>
            <td class="tg-i6ea">1,7%</td>
            <td class="tg-4cwk">1,3%</td>
            <td class="tg-2adx">25,3%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Nausea<br></td>
            <td class="tg-i6ea">1,4%</td>
            <td class="tg-4cwk">1,3%</td>
            <td class="tg-28u1">9,7%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Nariz entupido</td>
            <td class="tg-i6ea">5,0%</td>
            <td class="tg-4cwk">5,0%</td>
            <td class="tg-4cwk">0,1%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Fadiga</td>
            <td class="tg-i6ea">2,4%</td>
            <td class="tg-4cwk">2,1%</td>
            <td class="tg-ywcv">14,9%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dor nos olhos</td>
            <td class="tg-i6ea">2,0%</td>
            <td class="tg-4cwk">1,6%</td>
            <td class="tg-jh8w">21,5%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Perda de paladar</td>
            <td class="tg-i6ea">2,6%</td>
            <td class="tg-4cwk">2,0%</td>
            <td class="tg-i6ea">30,7%</td>
        </tr>
        <tr>
            <td class="tg-1wig">Dor muscular</td>
            <td class="tg-i6ea">4,3%</td>
            <td class="tg-4cwk">3,8%</td>
            <td class="tg-te1u">13,8%</td>
        </tr>
        <tr>
            <td class="tg-0lax"></td>
            <td class="tg-0lax"></td>
            <td class="tg-0lax"></td>
            <td class="tg-lqy6"><span style="font-weight:bold">15,1%</span></td>
        </tr>
        </tbody>
        </table>""",
        unsafe_allow_html=True,
    )

