import streamlit as st
import pandas as pd
from utils import make_clickable

def main():

    st.header("Simulação de Demanda Hospilatar")

    st.write('v1.1')
    
    st.subheader("Resumo")

    st.write(
        """
        Esta ferramenta utiliza uma variação do modelo epidemiológico SEIR para estimar a demanda por leitos hospitalares e ventiladores nos municípios brasileiros de pacientes com Covid-19. 
        Permitimos a simulação do impacto de 3 estratégias de contenção da transmissão na sociedade, baseados na resposta do governo e da sociedade.  
        Cada estratégia está associada a um número básico de reprodução distinto da Covid-19 (aproximadamente o número de novas pessoas infectadas por uma pessoa que já está doente). 
        As taxas foram estimadas por estudo da evolução da transmissão em Wuhan, na China, sob diferentes políticas de restrição de contato, protocolos de tratamento e de testagem. 
        Assim, ao indicar quando cada uma entrará em vigor no município selecionado, é possível simular a evolução da doença associada à sequência de estratégias indicada.
        """
    )

    st.subheader("Cálculo")

    st.write(
        """
        Queremos calcular em quantos dias a demanda por equipamentos hospitalares devido ao Covid-19 passará a oferta. 
        Neste caso, os equipamentos hospitalares $(e)$ são dividios em leitos $(l)$, necessários para casos severos da doença,
        e ventiladores $(v)$, necessários para casos críticos.

        A demanda por equipamento $$\mathcal{D}^e(t)$$ é dada pelo número de casos graves e críticos em $t$, que por sua vez é estimado através de um modelo epidemiológico. 
        A oferta $$\mathcal{O}^e(t)$$ é determinada pelo número de equipamentos que o município tem a disposição para pacientes de Covid-19. 
        Essa também é dinâmica pois os municípios estão, por exemplo, construindo leitos e remanejando cirurgias. 
        
        A capacidade é atingida quando $$\mathcal{D}^e(t) = \mathcal{O}^e(t)$$. Logo, buscamos obter o menor $$t$$ no qual essa igualdade é satisfeita.
        """
    )

    st.latex('t^* = min \{t [dias] : \mathcal{D}^e(t) = \mathcal{O}^e(t)\}')

    st.write(
        """
        A demanda está em função dos **estados populacionais**, **parâmetros da doença** e **parâmetros da reação do governo e sociedade**. 
        Os estados populacionais dependem da população do município e qual estágio de contágio está a doença. Os parâmetro da doença dizem respeito a transmissibilidade e ao tempo de progressão dos diferentes estágios da doença. 
        Os parâmetros reação do governo e sociedade são relacionados ao tempo de testagem, taxa de subnotificação e cobertura da vacinação, que por sua vez influenciam determinados parâmetros da doença. 
        Por exemplo, a transmissibilidade da doença pode variar de acordo com o nível de distanciamento social. 
        A taxa básica de reprodução ($$R_0$$), em especial, é dependente da transmissibilidade da doença, e portanto, da reação do governo e sociedade. 
        
        Neste exercício, com a escolha de diferentes estratégias, são escolhidos diferentes $$R_0$$. 
        Esses valores foram baseados nas estimativas realizadas em Wuhan dada as diferentes estratégias adotadas pelo governo local [(Wang et. al, 2020 [1])](https://www.medrxiv.org/content/10.1101/2020.03.03.20030593v1). 
        Assim, podemos projetar diferentes curvas de demanda dada a população do município. 
        As próximas duas seções, Capacidade Hospitalar e Modelo Epidemiológico, apresentam os modelos para a oferta e demanda de equipamentos hospitalares. 
        Finalmente, a seção Fontes de Dados mostra de onde extraímos os dados e como estamos nos organizando para atualizar a oferta de equipamentos hospitalares.
        """
    )

    st.header("Capacidade Hospitalar (Oferta)")

    st.write(
        """
        Os equipamentos hospitalares que consideramos para esse exercício são os ventiladores e leitos hospitalares. 
        
        - **Leitos**
        
        A quantidade de leitos por municípios soma tanto leitos hospitalares da rede do Sistema Único de Saúde quanto da rede não-SUS. 
        Avaliamos que ambas estariam envolvidas no esforço de resposta à crise. 
        Para usar por base apenas a rede SUS, seria necessário filtrar a população SUS-dependente de cada município.

        O número de leitos utilizado inclui leitos complementares. 
        Retiramos os de tratamento intensivo, já que nossa medida de possibilidade de adaptação para essa modalidade são os equipamentos. 

        Consideramos, na simulação inicial, que apenas $20\%$ dos leitos registrados no Cadastro Nacional de Estabelecimentos Hospitalares 
        estariam disponíveis para alocação de pacientes da Covid-19 que necessitem de internação. 
        Esse número está dentro do parâmetro recomendado pela Agência Nacional de Saúde Suplementar (ANS), 
        de manutenção da taxa de ocupação de hospitalar entre $75\%$ e $85\%$, 
        ainda que saibamos que há grande variação nesse percentual nas realidades locais de cada município (ANS, 2012).

        Caso um percentual maior ou menor esteja alocado para pacientes com Covid-19, é possível ajustar a quantidade de leitos alocados para a simulação.

        - **Ventiladores**
        ...

        Caso um percentual maior ou menor esteja alocado para pacientes com Covid-19, é possível ajustar a quantidade de ventiladores alocados para a simulação.

        """
    )

    st.header("Modelo epidemiológico (Demanda)")    

    st.subheader("Sobre o modelo")

    st.write("""
    Utilizamos o modelo epidemiológico SEIR (Suscetíveis, Expostos, Infectados e Removidos) adaptado segundo o 
    modelo desenvolvido por [Alison Hill](https://alhill.shinyapps.io/COVID19seir/) para calcular a disseminação e 
    evolução clínica do COVID-19. De acordo com esse modelo, uma população é dividida em diferentes estados populacionais, 
    grupos mutuamente excludentes de indivíduos:

    - Suscetíveis ($S$): aqueles que não têm imunidade à doença, estes se tornam expostos à doença a uma taxa $\\beta_i$ 
    devido ao contato com indivíduos infetados $I_i$;
    
    - Expostos ($E$): aqueles que entram em contato com a doença e desenvolvem ou não sintomas, mas ainda não transmitem infecção.
    Esses indivíduos expostos progridem para o primeiro estágio de infecção ($I_1$), leve, a uma taxa $\sigma$.
    
    - Infectados ($I$): são aqueles que desenvolvem sintomas e transmitem a doença a uma taxa $\\beta_i$. Os casos de infecção são separados em diferentes estágios de gravidade:
      - Leve ($I_1$): aquele que não necessita de hospitalização, progride para o estado severo a uma taxa $p_1$, ou se recupera a uma taxa $\gamma_1$;
      - Severo ($I_2$): aquele que necessita de hospitalização, progride para o estado crítico a uma taxa $p_1$, ou se recupera a uma taxa $\gamma_2$;
      - Grave ($I_3$): aquele que além de hospitalização, necessita de tratamento intensivo com equipamento de ventiladores. 
      Chegando ao caso grave, o indivíduo pode se recuperar a uma taxa $\gamma_3$ ou o quadro pode levar à morte com uma taxa $\mu$;
    
    - Recuperados ($R$): aqueles que, após o curso da doença, se recuperam e desenvolvem imunidade - não retornam ao estado suscetível.
    - Mortos ($D$): indivíduos que morrem pelo agravamento da infecção.
""")

    pic = open('imgs/model_graph', 'r').read()
    st.image(pic, use_column_width=True, caption=None)
    st.write('*Fonte: [Alison Hill](https://alhill.shinyapps.io/COVID19seir/)*')

    st.write('Conforme a descrição acima, o conjunto de equações que determina a dinâmica do modelo é dado por:')
    st.latex("\\frac{dS}{dt} = - (β_1 I_1 + β_2 I_2 + β_3 I_3) S")
    st.latex("\\frac{dE}{dt} = (β_1 I_1 + β_2 I_2 + β_3 I_3) S - \sigma E")
    st.latex("\\frac{dI_1}{dt} = \sigma E - (γ_1 + p_1) I_1")
    st.latex("\\frac{dI_2}{dt} = p_1 I_1 - (γ_2 + p_2) I_2")
    st.latex("\\frac{dI_3}{dt} = p_2 I_2 - (γ_3 + p_3) I_3")
    st.latex("\\frac{dR}{dt} = γ_1 I_1 + γ_2 I_2 + γ_3 I_3")
    st.latex("\\frac{dD}{dt} = μ I_3")

    st.subheader('Parâmetros da doença')

    st.write('- **Número básico de reprodução ($R0$)**')
    st.write(
        """
        O número básico de reprodução da doença nos remete ao número médio de pessoas que uma pessoa doente consegue infectar. 
        Esse é um número característico da doença, que costuma ser estimado de forma retroativa conforme o avanço da doença. 
        Para simular diferentes estratégias, utilizamos $R0s$ estimados em Wuhan no estudo de [(Wang et. al, 2020 [1])](https://www.medrxiv.org/content/10.1101/2020.03.03.20030593v1) para cada medida adotada pelo governo local.
        """)

    st.write('- **Taxas de progressão ($p_i, \\sigma$) e mortalidade ($\\mu$)**')
    st.write(
        """
        As taxas de progressão da doença representam o grau no qual um indivíduo avança nos estados de infecção da doença. 
        Inicialmente, um indivíduo exposto avança para o primeiro estado de infeção, leve ($I_1$) a uma taxa $\\sigma$.
        Uma vez infectado, o indivíduo progride para estados mais graves da doença a uma taxa $p_1$ - de leve para severo - 
        e $p_2$ - de severo para crítico. Assume-se que a infecção avança gradualmente, ou seja, uma infeção leve deve passar 
        pelo estado severo para chegar ao crítico. Por fim, os casos críticos acarretam na morte de indivíduos a uma taxa $\\mu$.
        """
    )

    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1wvg1KFWZp4WhYVI4Gw_82bL_je_2WZHNLCcSnx95MTI/gviz/tq?tqx=out:csv&sheet=Taxas_de_progressao')
    df.index = ['' for i in range(len(df))]
    st.table(df)


    st.write('- **Taxas de recuperação ($\\gamma_i$)**')
    st.write(
        """
        As taxas de recuperação da doença representam o grau no qual um indivíduo se recupera em qualquer estado de gravidade.
        Assume-se que, uma vez recuperado, esse indivíduo não contrai mais a doença, não retornando ao estado de suscetível.
        """
    )

    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1wvg1KFWZp4WhYVI4Gw_82bL_je_2WZHNLCcSnx95MTI/gviz/tq?tqx=out:csv&sheet=Taxas_de_recuperacao')
    df.index = ['' for i in range(len(df))]
    st.table(df)

    st.write('- **Taxas de transmissão ($\\beta_i$)**')
    st.write(
        """
        As taxas de transmissão dizem respeito ao potencial de infecção de indivíduos infectados em contato a indivíduos suscetíveis.
        Para casos severos ($\\beta_2$) e críticos ($\\beta_3$), as taxas de transmissão desses indivíduos são referentes 
        à transmissão interna nos hospitais, de pacientes para profissionais da saúde. Segundo estudos realizados na China 
        e Itália [(Wang et. al, 2020 [2])](https://doi.org/10.1016/j.jhin.2020.03.002), esse grupo é afetado de forma desproporcional, 
        sendo observado cerca de $5\%$ e $10\%$ de profissionais da saúde dentre o total de casos notificados, respectivamente.
        """)


    st.write("- **Cálculo das taxas**")

    st.write(
        """
        As taxas não são observadas diretamente. Logo, utilizamos parâmetros observados na literatura para o cálculo das mesmas.
        Os parâmetros de referência são descritos na tabela abaixo.
        """)

    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1wvg1KFWZp4WhYVI4Gw_82bL_je_2WZHNLCcSnx95MTI/export?format=csv&id').fillna('-')# .set_index('Descrição', drop=True)
    df.index = ['' for i in range(len(df))]
    st.table(df)


    st.subheader('Parâmetros de reação da sociedade e governo')
    
    st.write(
    """
    - **Subnotificação ($$\\alpha$$)**

    Ainda não temos relatórios sobre a subnotificação de casos de Covid-19 no Brasil. 
    Estudos consultados variam ao abordar a questão: [(Wang et. al, 2020 [1])](https://www.medrxiv.org/content/10.1101/2020.03.03.20030593v1) consideram subnotificação de $50\%$ (2020), 
    enquanto  [Li et al. (2020)](?) calculam que apenas $14\%$ dos casos de pessoas infectadas foram reportados, 
    com intervalo de confiança de $10-18\%$. Os dois artigos consideram que casos não-notificados não tem sintomas graves e que não serão hospitalizados.

    O protocolo de testagem no Brasil submete somente aquelas pessoas com sintomas graves o suficiente para buscarem um hospital. 
    Além disso, há crescente documentação da falta de testes para todos os que chegam com suspeita de coronavírus. 
    O protocolo técnico de tratamento médico é o mesmo, independente do diagnóstico preciso. 
    Porém, isso quer dizer que nem todos os casos não-notificados no Brasil são leves ou moderados: 
    podem haver pessoas sendo hospitalizadas com Covid-19 mas que não são testadas e, por isso, não constam no registro. 
    Têm sido recorrentes, inclusive, relatos sobre o aumento atípico no número de internações por doenças respiratórias.

    Por isso, ainda que tenhamos montado a estrutura do modelo para incluir uma taxa de notificação, 
    consideramos a mesma como 1, de maneira a não diminuir a pressão sobre o sistema de saúde causado pelo percentual 
    de casos notificados que precisam de hospitalização.

    - **Tempo de diagnóstico ($$\\tau$$)**

    O tempo de diagnóstico é o tempo entre a execução do teste até o resultado. 
    Esse tempo varia de acordo com a capacidade do estado e clínicas privadas de realizar testes em escala. 
    Mas, varia com o tipo de teste que é feito. 
    O tempo de diagnóstico é importante pois ele é o ‘atraso’ em que estamos inicializando o modelo. 
    Por exemplo, se o tempo de diagnóstico é de 1 semana, então os casos confirmados hoje, são, 
    na verdade pacientes que estavam apresentando sintomas há uma semana. 
    Dependendo do tempo de diagnóstico, pacientes podem estar recuperados ou mortos até a doença ser confirmada.
    Portanto, essa variável nos diz quão atualizado estão os dados com relação à situação real da doença no município.
    """)
    
    st.subheader("Inicialização dos estados")
    st.write(
        """
        Para simular a evolução da doença, determinamos os valores iniciais de cada estado populacional do modelo.
        """)

    st.write(
        """
        - **Infectados (I)**: o total de infectados inicialmente é dado pelo número de casos ativos, $I_0$.
        A fonte utilizada atualmente reporta o número acumulado e novos casos e mortes por dia. Portanto,
        é necessário calcular o número de casos ativos. Dado o tempo de progressão da doença ($\delta T$), 
        os casos ativos serão a soma dos novos casos reportados no intervalo $t_i - \delta T$ e $t_i$, onde $t_i$ é o dia
        de início da simulação. Assim, se $I^t$ é o número de novos casos reportados em $t$, o número de casos ativos é dado por
        $I(0) = \sum_{t=t_i - \delta T}^{t_i} I^t$.

        Considerando $\delta T$ como a soma do tempo de progressão dos casos leve, severo e crítico.

        Esse total é separado pela estimativa do percentual de indivíduos em cada estágio de gravidade da 
        doença: segundo [CDC(2020)](https://www.cdc.gov/mmwr/volumes/69/wr/mm6912e2.htm?s_cid=mm6912e2_w), a quantidade de casos severos 
        ($I_2$) e críticos ($I_3$) é dada por $12\%$ e $2.5\%$ dos total de infectados, respectivamente, 
        sendo os demais $85.5\%$ casos leves ($I_1$).
        """
    )

    st.latex("I_1(0) = \\frac{\gamma_1}{\gamma_1 + p_1} I(0)")
    st.latex("I_2(0) = \\frac{\gamma_2}{\gamma_2 + p_2} I(0)")
    st.latex("I_3(0) = \\frac{\gamma_3}{\gamma_3 + \mu} I(0)")
    st.latex("\\text{sendo }\\frac{\gamma_1}{\gamma_1 + p_1} + \\frac{\gamma_2}{\gamma_2 + p_2} + \\frac{\gamma_3}{\gamma_3 + \mu} = 1")

    st.write(
            """
        Para municípios que não possuem casos confirmados em boletins oficiais, conforme 
        reportado no Brasil.io, simulamos os números a partir do primeiro caso. 
        Isso quer dizer que, ao selecionar unidades de análise mais altas, portanto, 
        como as regionais de saúde ou os estados, você está simulando um cenário 
        onde todos os municípios têm ao menos um caso confirmado.
            """
    )

    st.write(
        """
        - **Expostos (E)**: dado o número inicial de infectados leves ($I_1$) calculado acima, calculamos $E(0)$ 
        discretizando a equação $\\frac{dI_1}{dt}$ em $t=1$, conforme mostrado abaixo. Dado que o número de casos 
        dobra a cada 3 dias **(??)**, aproximamos $I_1(1) \\approx \sqrt[3]{2} \\times I(0) \\approx 1.26 I(0)$.
        """
    )
    # st.latex("I_1(1) - I_1(0) = \sigma E(0) - \gamma I_1(0) \\rightarrow E(0) =\\frac{ I_1(1) + (\gamma - 1)I_1(0)}{\sigma}")
    st.latex("E(0) \\approx \\frac{ I(1) - I(0)}{\sigma} \\approx \\frac{0.26}{\sigma} \\times I(0)")


    st.write(
        """
        - **Mortos (D)**: iniciamos esse estado com o total de mortes reportado pelo município com os dados do Brasil.io.

        - **Recuperados (R)**: sabendo o acumulado histórico de casos, o número mortes ($D$) e o número de casos ativos ($I(0)$),
        então $R = \sum_{t=t_0}^{t_i} - I(0) - D$
        
        - **Suscetíveis (S)**: o número de indivíduos suscetíveis inicial é dado pelo restante da polucação do município
        que não se encontra em nenhum dos estados acima.
        """
    )

    st.latex("S(0) = N - I(0) - E(0) - R(0) - D(0)")

    st.subheader("Simulação das estratégias")

    st.write(
        """
        Como dito acima, as estratégias se diferenciam pela taxa de reprodução atribuída a cada uma. Conforme o estudo de 
        As estimações de [(Wang et. al, 2020 [1])](https://www.medrxiv.org/content/10.1101/2020.03.03.20030593v1) com dados empíricos 
        da disseminação da COVID-19 em Wuhan no período de pouco mais de um mês estão dispostas abaixo.
        """
    )

    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1wvg1KFWZp4WhYVI4Gw_82bL_je_2WZHNLCcSnx95MTI/gviz/tq?tqx=out:csv&sheet=Taxas_de_reproducao')# .set_index('Descrição', drop=True)
    df.index = ['' for i in range(len(df))]
    st.table(df)

    st.write("""
        Optamos por adotar as números básicos de reprodução reportadas em Wang et al. (2020) por ser estudo realizado com base em análise epidemiológica 
        de 26.000 casos de Covid-19 diagnosticados. Ainda que haja problemas com a analogia entre dinâmicas de contágio e aderência a decretos 
        públicos entre o Brasil e a China, escolhemos essa referência por ela ter sido calculada a partir de dados observados, não sendo resultante de simulação, 
        como Ferguson et al. (2020). Essa também é uma análise que secciona os R0 de acordo com as políticas públicas adotadas no período, 
        possibilitando que façamos a simulação desses diferentes cenários para os municípios brasileiros. 
        Entretanto, ainda não se tem certeza de que a mudança na velocidade da infecção da população se deveu apenas às mudanças políticas, 
        embora pelo tamanho das intervenções isso seja muito provável.
        """)
    
    st.header('Fonte de Dados')
    st.write("""
    Os dados iniciais utilizados na ferramenta foram coletados de:
    """)

    df = pd.read_csv('https://docs.google.com/spreadsheets/d/1wvg1KFWZp4WhYVI4Gw_82bL_je_2WZHNLCcSnx95MTI/gviz/tq?tqx=out:csv&sheet=Fontes')

    # link is the column with hyperlinks
    df['Fonte'] = df[['URL', 'Fonte']].apply(lambda row: make_clickable(row['Fonte'], row['URL']), 1)
    st.write(df.drop('URL', axis=1).to_html(escape=False), unsafe_allow_html=True)

    st.subheader('Programa de Embaixadores')
    st.write("""
    Para essa versão, também integraremos dados atualizados enviados pelos 
    nossos Embaixadores. Este será devidamente identificado como sendo contribuição 
    do Embaixador ou como input do programa - quando a pessoa preferir colaborar 
    de maneira anônima. 
    
    **Para se tornar um embaixador, inscreva-se [aqui](https://forms.gle/iPFE7T6Wrq4JzoEw9)**
    """
    )
        
if __name__ == "__main__":
    main()
    