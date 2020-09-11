import streamlit as st
import amplitude
import utils
from PIL import Image
from pages import model_description, rt_description, saude_em_ordem_description


def main(session_state):
    # Analytics
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.safe_log_event(
        "opened saude_em_ordem_description", session_state, is_new_page=True
    )

    # Layout
    utils.localCSS("style.css")

    utils.genHeroSection(
        title1="Farol",
        title2="Covid",
        subtitle="Entenda a metodologia da ferramenta.",
        logo="https://i.imgur.com/CkYDPR7.png",
        header=True,
    )

    st.write(
        """
        <div class="base-wrapper flex flex-column" style="background-color: rgb(0, 144, 167);">
            <div class="white-span header p1" style="font-size:30px;">MODELOS, LIMITAÇÕES E FONTES</div>
        </div><br><br>
        """,
        unsafe_allow_html=True,
    )

    # NIVEIS DE ALERTA
    st.write(
        """<div class="base-wrapper primary-span">
            <span class="section-header">NÍVEIS DE ALERTA (FAROLCOVID): Como saber se estou no controle da Covid-19?</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Intro
    st.write(
        f"""<div class="base-wrapper">Até que uma vacina ou tratamento definitivos sejam encontrados para a Covid-19, será
            necessário <b>controlar a quantidade de pessoas infectadas</b> e a <b>disponibilidade de
            recursos do sistema de saúde</b>, para ter certeza de que todos(as) receberão o
            tratamento necessário, <b>sem que o sistema venha a colapsar.</b> Depois de um primeiro
            momento de mitigação da Covid-19 nos estados e municípios brasileiros, passamos a uma
            nova fase de resposta à pandemia: a de supressão da doença. Nela, é necessário avaliar
            periodicamente qual o cenário e quais as ações mais adequada para a cidade, regional de
            saúde ou estado, de acordo com indicadores sobre a dinâmica de transmissão da doença e
            sua capacidade de resposta.<br><br> É a partir dessa avaliação que políticas de
            resposta à Covid-19 devem ser calibradas: <b>o objetivo é chegar no "novo normal," onde
            a situação está sob controle.</b> Para auxiliar a população e os gestores públicos nessa
            tarefa, desenvolvemos uma classificação em Níveis de Alerta, baseada em 4 eixos,
            correspondentes a perguntas-chave que devem ser respondidas por quem está tomando
            decisões sobre resposta à pandemia. Cada pergunta é respondida através de um indicador
            de referência:<br><br>
            <span class="subsection-header">Situação da Covid-19: Qual a incidência da doença na minha população?</span><br>
            <b>Indicador</b>: Novos casos por 100k habitantes (média móvel 7 dias).<br>
            <b>Qual sua tendência?</b> Aumentando, estabilizando ou diminuindo?<br><br>
            <span class="subsection-header">Controle da Covid-19: Estamos conseguindo frear o surgimento de novos casos?</span><br>
            <b>Indicador</b>: Taxa de contágio (Número efetivo de Reprodução - R_t)<br>
            <b>Qual sua tendência?</b>Aumentado, estabilizando ou diminuindo?<br><br>
            <span class="subsection-header">Capacidade do sistema: Como está a capacidade de resposta do sistema de saúde? </span><br>
            <b>Indicador</b>: Dias até atingir ocupação total de leitos enfermaria<br>
            <b>Qual sua tendência?</b> Aumentado, estabilizando ou diminuindo?<br><br>
            <span class="subsection-header">Confiança nos dados: Quão representativo são os casos oficialmente identificados 
            frente ao total de casos esperados?</span><br>
            <b>Indicador</b>: Taxa de subnotificação<br>
            <b>Qual sua tendência?</b> Aumentado, estabilizando ou diminuindo?<br><br>
            É importante notar que a classificação em níveis de alerta é <b>dinâmica</b>, ou seja,
            <b>muda conforme os indicadores das cidades e municípios são atualizados diariamente</b>.
            Portanto, aconselhamos que seja feito um acompanhamento frequente do FarolCovid por parte
            de gestores. Esses números podem, ainda, ser uma importante ferramenta para comunicação com
            os cidadãos, servindo de embasamento e justificativa para a tomada de decisão adequada a
            cada realidade local. O público, em geral, também pode utilizar esses números para engajar o
            poder público em um debate informado sobre quais são as melhores políticas para sua cidade,
            regional ou e estado.<br><br><br>
            <span class="subsection-header"><b>Como os Indicadores-Chave são avaliados?</b></span><br>
            Avaliamos os indicadores-chave em 4 níveis crescentes de risco: <strong style="color:#0090A7">Novo Normal</strong>, 
            <strong style="color:#F7B500">Moderado</strong>, <strong style="color:#F77800">Alto</strong> ou
            <strong style="color:#F02C2E">Altíssimo</strong>, e também suas tendências (se estão diminuindo,
            estabilizando ou crescendo). 
            A classificação de cada indicador segue a tabela de valores de referência abaixo. Após analisar cada indicador, classificamos 
            o município, regional ou estado no nível de alerta <b>equivalente ao mais alto entre os de cada indicador individual</b>. 
            Caso o município não conte com algum dos indicadores, mostramos o número correspondente para o nível regional. 
            Nesse caso, ele não terá classificação de risco.
            </div>""",
        unsafe_allow_html=True,
    )

    # Valores de referência
    st.write(
        """<div class="base-wrapper"><div style="margin: 10px 10px 10px 10px;">
            <div class="info-div-table">
            <table class="info-table">
            <tbody>
                <tr>
                    <td class="grey-bg"><strong>Dimensão</strong></td>
                    <td class="grey-bg"><strong>Indicador</strong></td>
                    <td class="grey-bg"><strong>Novo Normal</strong></td>
                    <td class="grey-bg"><strong>Risco Moderado</strong></td>
                    <td class="grey-bg"><strong>Risco Alto</strong></td>
                    <td class="grey-bg"><strong>Risco Altíssimo</strong></td>
                </tr>
                <tr>
                    <td rowspan="2">
                    <p><span>Situação da doença</span></p><br/>
                    </td>
                    <td><span>Novos casos diários (Média móvel 7 dias)</span></td>
                    <td class="light-blue-bg bold"><span>x&lt;=3.7</span></td>
                    <td class="light-yellow-bg bold"><span>3.7&lt;x&lt;=12.5</span></td>
                    <td class="light-orange-bg bold"><span>12.5&lt;=x&lt;=27.4</span></td>
                    <td class="light-red-bg bold"><span>x &gt;= 27.4</span></td>
                </tr>
                <tr>
                    <td><span>Tendência de novos casos diários</span></td>
                    <td class="lightgrey-bg" colspan="4"><span>Se crescendo*, mover para o nível mais alto</span></td>
                </tr>
                <tr>
                    <td><span>Controle da doença</span></td>
                    <td><span>Número de reprodução efetiva</span></td>
                    <td class="light-blue-bg bold"><span>&lt;0.5</span></td>
                    <td class="light-yellow-bg bold"><span>&lt;0.5 - 1&gt;</span></td>
                    <td class="light-orange-bg bold"><span>&lt;1 - 1.2&gt;</span>&nbsp;</td>
                    <td class="light-red-bg bold"><span>&gt;1.2</span></td>
                </tr>
                <tr>
                    <td><span>Capacidade de respostas do sistema de saúde</span></td>
                    <td><span>Projeção de tempo para ocupação total de leitos enfermaria</span></td>
                    <td class="light-blue-bg bold">60 - 90 dias</td>
                    <td class="light-yellow-bg bold"><span>30 - 60 dias</span></td>
                    <td class="light-orange-bg bold"><span>15 - 30 dias</span></td>
                    <td class="light-red-bg bold"><span>0 - 15 dias</span></td>
                </tr>
                <tr>
                    <td><span>Confiança dos dados</span></td>
                    <td><span>Subnotificação (casos <b>não</b> diagnosticados a cada 10 infectados)</span></td>
                    <td class="light-blue-bg bold"><span>4&gt;=x&gt;0</span></td>
                    <td class="light-yellow-bg bold"><span>6&gt;=x&gt;4</span></td>
                    <td class="light-orange-bg bold"><span>7&gt;=x&gt;6</span></td>
                    <td class="light-red-bg bold"><span>10&gt;=x&gt;=7</span></td>
                </tr>
            </tbody>
            </table>
            </div>
            <div style="font-size: 14px">
                * Como determinamos a tendência:
                <ul class="sub"> 
                    <li> Crescendo: caso o aumento de novos casos esteja acontecendo por pelo menos 5 dias. </li>
                    <li> Descrescendo: caso a diminuição de novos casos esteja acontecendo por pelo menos 14 dias. </li>
                    <li> Estabilizando: qualquer outra mudança. </li>
                </ul>
            </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Limitação
    st.write(
        """<div class="base-wrapper"><span class="subsection-header"><b>Essas métricas são suficientes?</b></span><br>
        <b>Não.</b><br><br>Desenvolvemos os níveis de alerta do FarolCovid com dados públicos e abertos, disponíveis
        online. É um primeiro passo para o gestor orientar sua tomada de decisão de maneira informada,
        orientado por dados que o atualizam tanto sobre o estágio de evolução da doença em seu local 
        quanto sua capacidade de resposta. O gestor público, entretanto, conta com uma riqueza
        maior de informações que deve ser utilizada na formulação de respostas adequadas à sua realidade.
        Informações como a quantidade de testes realizados, a taxa de pessoas que testam positivo e o tempo
        médio de internação são outros fatores importantes para a tomada de decisão. Estamos à disposição
        para apoiar o gestor público a aprofundar a análise para seu estado ou município, de forma
        inteiramente gratuita. <a class="github-link" href="https://coronacidades.org/fale-conosco/>Entre em contato pelo Coronacidades.org</a>!
        </div>""",
        unsafe_allow_html=True,
    )

    # Detalhes
    st.write(
        """<div class="base-wrapper"><span class="subsection-header"><b>Detalhes da distribuição dos indicadores-chave</b></span><br>
        Para ilustrar as classificações dos indicadores, geramos os gráficos das distribuições de cada indicador 
        (diagonal) e as distribuições por pares de indicadores (em cada eixo) abaixo, para cidades, regionais e estados.
        </div>""",
        unsafe_allow_html=True,
    )

    # st.image(
    #     Image.open("imgs/cities_indicators_202009.png"),
    #     use_column_width=True,
    #     caption="Distribuição de indicadores-chaves para cidades (retrato de 1/set/2020. Cada ponto representa uma cidade, os eixos x e y trazem os valores dos indicadores-chaves para aquela cidade. Na diagonal segue o histograma do indicador-chave.",
    # )

    # st.write("<br><br>", unsafe_allow_html=True)

    # st.image(
    #     Image.open("imgs/states_indicators_202009.png"),
    #     use_column_width=True,
    #     caption="Distribuição de indicadores-chaves para regionais de saúde (retrato de 1/set/2020). Cada ponto representa uma estado, os eixos x e y trazem os valores dos indicadores-chaves para aquela cidade. Na diagonal segue o histograma do indicador-chave.",
    # )

    # st.image(
    #     Image.open("imgs/states_indicators_202009.png"),
    #     use_column_width=True,
    #     caption="Distribuição de indicadores-chaves para estados (retrato de 1/set/2020). Cada ponto representa uma estado, os eixos x e y trazem os valores dos indicadores-chaves para aquela cidade. Na diagonal segue o histograma do indicador-chave.",
    # )

    st.write(
        """<div class="base-wrapper primary-span">
            <span class="section-header">CÁLCULO E CLASSIFICAÇÃO DE INDICADORES</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    indicador = st.radio(
        "Selecione abaixo o indicador para ver a descrição em detalhe:",
        [
            "SITUAÇÃO DA DOENÇA: Média móvel de novos casos por 100 mil habitantes",
            "CONTROLE DA DOENÇA: Taxa de contágio (Rt)",
            "CAPACIDADE DO SISTEMA: Dias até atingir ocupação total de leitos enfermaria",
            "CONFIANÇA NOS DADOS: Taxa de subnotificação de casos",
        ],
    )

    if (
        indicador
        == "SITUAÇÃO DA DOENÇA: Média móvel de novos casos por 100 mil habitantes"
    ):
        st.write(
            """<div class="base-wrapper primary-span">
                <span class="section-header">SITUAÇÃO DA DOENÇA: Média móvel de novos casos por 100 mil habitantes</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            """<div class="base-wrapper">
            <span class="subsection-header"><b>Como saber o quão crítico é o nível de novos casos?</b></span><br> 
            Para responder essa pergunta precisamos entender como vem evoluindo a incidência dos casos na
            população ao longo do tempo e onde estamos nessa curva. Logo, os valores de referência para a
            classificação dos níveis de alerta foram definidos com base na série histórica de novos casos de
            Covid-19 nas capitais brasileiras, por maior consistência no reporte de casos e também maior período
            de tempo transcorrido desde o 1º caso. 
            Como calculamos os valores de referência?  Dada a série histórica, com a média móvel semanal de
            novos casos diários por 100mil habitantes das capitais, separamos a distribuição de novos casos por
            dia das capitais em 4 intervalos traduzidos nos quartis:<br>
            <li>Novo normal (Q1): máximo dentre 25% dos menores valores de novos casos diários;</li>
            <li>Moderado (Q2):máximo dentre 50% dos menores valores de novos casos diários;</li>
            <li>Alto (Q3): máximo dentre 75% dosmenores valores de novos casos diários; </li>
            <li>Altíssimo: todos os valores acima do classificado para alto.</li><br>
            O valor final é dado pela média dos quartis das capitais. Tomemos o exemplo de Aracaju: abaixo temos
            a distribuição da média de novos casos até 30/08/2020. Até esta data, 25% dos dias tiveram uma média
            de até 1.7 por 100 mil habitantes (novo normal); 50% dos dias tiveram uma média até de 22.7
            (moderado); e 75% foram abaixo de 61.3 (alto - os valores acima deste são considerados altíssimo).
            </div>""",
            unsafe_allow_html=True,
        )

        st.image(
            Image.open("imgs/new_cases_aracaju_20200830.png"),
            use_column_width=True,
            caption="Distribuição da média móvel semanal de novos casos por 100mil habitantes em Aracaju (retrato de 30/ago/2020).",
        )

        st.write(
            """<div class="base-wrapper">
            A distribuição de todas as capitais abaixo reflete parte da variação local de
            intensidade e progressão da doença em diferentes localidades do Brasil. A média dos
            quartis de todas as capitais nos fornece os valores de referência utilizados para a
            classificação da Situação da doença - novo normal até 3.7 (Q1); moderado até 12.5 (Q2);
            alto até 27.4 (Q3); altíssimo acima de 27.4.
            </div>""",
            unsafe_allow_html=True,
        )

        st.image(
            Image.open("imgs/new_cases_capitals_20200830.png"),
            use_column_width=True,
            caption="Distribuição da média móvel semanal de novos casos por 100mil habitantes para todas as capitais (retrato de 30/ago/2020).",
        )

        st.write(
            """<div class="base-wrapper">
            <span class="subsection-header"><b>LIMITAÇÕES</b></span><br> 
            <li>Utilizamos dados abertos de casos reportados - ou seja, as datas são do reporte do caso e não do
            início dos sintomas. Como sabemos que existe um  atraso entre o início dos sintomas e a inserção do
            resultado do teste no sistema, os valores não traduzem fielmente a realidade do dia de hoje.</li>
            <li>Existe viés de seleção atrelado ao período de evolução da doença que não observamos ainda. Isso ocorre
            pois nenhuma das capitais extinguiram o número de novos casos diários até a 30/08/2020. Caso a
            tendência seja somente de diminuição do número de casos a partir de hoje, por exemplo, os valores de
            referência estariam superestimados.</li>
            <li> Existe também viés de seleção relacionado ao porte das capitais. 
            Por um lado, estas possuem maior densidade populacional, o que aumenta a chance de terem
            maior número de casos, mas por outro lado, também possuem maior infraestrutura para resposta à
            crise. Estas foram escolhidas por ter uma maior estabilidade no reporte dos casos e maior número de
            testes RT-PCR dentre os testes realizados (que indica a presença ativa do vírus no organismo).</li>
            </div>""",
            unsafe_allow_html=True,
        )

    if indicador == "CONFIANÇA NOS DADOS: Taxa de subnotificação de casos":

        st.write(
            """<div class="base-wrapper primary-span">
                <span class="section-header">CONFIANÇA NOS DADOS: Taxa de subnotificação de casos</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            """<div class="base-wrapper">
                <span class="subsection-header"><b>O que é?</b></span><br> 
                Um modelo de subnotificação é uma ferramenta estatística utilizada para auxiliar a compreensão da
                real situação de infectados num determinado local, pois os dados de casos reportados não refletem
                perfeitamente a realidade, uma vez que há - por diversas razões - casos não identificados
                oficialmente. Alguns dos fatores que aumentam o grau de subnotificação são a falta de testagem
                massiva na população; detecção de casos somente após apresentação de sintomas; e a própria
                característica da doença de existirem infectados assintomáticos, que são transmissores ainda que em
                menor escala (WHO, 2020).
                <br><br><span class="subsection-header"><b>Como foi desenvolvido?</b></span><br> 
                O modelo de subnotificação do grupo de pesquisa <a class="github-link" href='http://www.cemeai.icmc.usp.br/ModCovid19/'>ModCovid</a> 
                foi desenvolvido inicialmente para ajudar a determinar o estágio da epidemia em Aracaju e Maceió.
                <br><br><span class="subsection-header"><b>Por que é importante?</b></span><br> 
                Para a evolução da epidemia numa região precisamos descobrir quantos novos casos de infecção são
                gerados a cada dia, a partir de um certo momento no tempo. Porém, sabemos que a medição desses casos
                é deficiente, principalmente por gargalos na testagem de Covid-19 em nosso país. Portanto,
                calculamos um número corrigido de casos a partir de comparações com proporções esperadas de mortes
                para casos, conforme a literatura nascente sobre a dinâmica da Covid-19 em diferentes populações.
                Isso nos permite planejar novas ações de combate à disseminação, sua ordem de prioridade e
                preparação para novos leitos de atendimento.
                <br><br><span class="subsection-header"><b>Como o modelo funciona?</b></span><br> 
                Fazemos uma regressão a partir do número de mortos reportados por Covid-19 para estimar o número
                de casos de pessoas infectadas 14 dias compatível com aquela quantidade de mortes. Ao compará-lo com
                a quantidade de casos registrados, calculamos a taxa de subnotificação correspondente. O período de
                14 dias é um tempo médio aproximado para a evolução da doença do momento da infecção até o
                falecimento de um indivíduo (Alison, 2020).
                <br><br><span class="subsection-header"><b>Como é feito o cálculo</b></span><br> 
                Utilizando uma <a class="github-link" href="https://www.inf.ufsc.br/~andre.zibetti/probabilidade/binomial_negativa.html">distribuição binomial negativa</a> 
                como modelo probabilístico, o cálculo gera o número de casos positivos que seriam esperados dado o número mortes observadas.
                A distribuição modela a probabilidade de que um número  de novos infectados possa falecer 14 dias
                após de ter se tornado infeccioso, dado o total de mortes até a data () e a taxa de mortalidade por
                infecção (IFR). A taxa de mortalidade por infecção (IFR) das regiões é calculada utilizando IFRs por
                faixa etária estimados em Hubei, segundo Verity, Robert, et al. (2020)[1], e obtém-se a IFR total da
                região ponderada pela população em cada faixa com os dados da População Residente (CNES - 2019).<br><br>
                Selecionamos a série histórica de mortes da região a partir da 15a morte e com pelo menos 15 dias
                desde o 1o caso, de maneira a garantir significância estatística. Dado o total de mortes  e a IFR,
                realizamos 100.000 simulações para cada data da série e os casos estimados são dados pelo valor
                médio da distribuição gerada.
                <br><br><span class="subsection-header"><b>LIMITES E CONSIDERAÇÕES SOBRE O MODELO</b></span><br> 
                <li>Existe atraso na confirmação do diagnóstico de mortes por Covid-19, logo a data do reporte não
                reflete a data real de quando ocorreu o óbito. Isso significa que estamos olhando muitas vezes para
                um retrato do passado e não de agora. Quanto maior o atraso no reporte, menos ajustada está a taxa
                de subnotificação à realidade atual.</li>
                <li>Existe subnotificação de mortes que ocorrem fora do ambiente
                hospitalar, que podem influenciar sensivelmente as estimativas. Quem morre de Covid-19 em casa não é
                necessariamente reportado nas estatísticas de óbito por Covid e portanto leva a subestimarmos o
                tamanho da subnotificação.</li>
                <li>Existem inconsistências no reporte de mortes por Covid-19. Há uma
                superestimação da subnotificação atrelada à protocolos de notificação independente da causa
                principal da morte ser Covid-19.</li>
                <br>Outras opções para a estimação de infecciosos podem ser o uso de
                pacientes com Síndrome Respiratória Aguda Grave (SRAG), pacientes em leitos hospitalares de
                retaguarda e pacientes internados em leitos de UTI. Essas estratégias, porém, podem ser ainda mais
                imprecisas, uma vez que há uma grande incerteza envolvendo questões básicas como o número total de
                leitos disponíveis (SUS e particulares), etiologia dos casos de SRAG e disponibilidade local de
                UTIs. Neste momento, com uma amostragem relativamente pequena no início da epidemia, a estimação
                dos infecciosos usando a série histórica dos mortos se mostra a melhor opção. Reiteramos que dados
                de testagem massiva e estruturada em modelos estatísticos e probabilísticos são essenciais para o
                controle da evolução da doença em um futuro próximo.
                </div>""",
            unsafe_allow_html=True,
        )

    if indicador == "CONTROLE DA DOENÇA: Taxa de contágio (Rt)":

        st.write(
            """<div class="base-wrapper primary-span">
                <span class="section-header">CONTROLE DA DOENÇA: Taxa de contágio (Rt)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rt_description.main(session_state)

        # st.write(
        #     """<div class="base-wrapper">
        #     <span class="subsection-header"><b>O que é?</b></span><br> 
        #     O número de reprodução efetivo (Rt) traduz a quantidade de pessoas que cada pessoa
        #     doente infectará em determinado intervalo de tempo.  Já o número básico de reprodução
        #     (<i>R0</i>) da uma doença traduz qual a dinâmica de contágio de todo o curso de transmissão em
        #     determinado grupo populacional, sendo, portanto, fixo para a doença. Mas a quantidade de
        #     novas infecções geradas por cada pessoa varia ao longo do tempo: se, no início, há menos
        #     pessoas imunes, ele tende a ser mais alto; enquanto, tudo mais constante, o aumento da
        #     imunidade na população se traduzirá em um número menor de novas infecções. Igualmente,
        #     mudanças de comportamento - como a redução de contato entre pessoas ou uso de máscaras, no
        #     caso de doenças transmitidas por vias áreas, como a Covid-19 - também influenciam o número
        #     de novas infecções.<br><br> A Covid-19 chegou em momentos distintos em cada cidade brasileira e
        #     a sociedade também reagiu de maneira diferente em cada uma delas. Portanto, medir o
        #     <i>Rt</i>, traduzindo o <i>R0</i> para o momento específico no qual cada local se encontra, a
        #     nível municipal e estadual, traz informações importantes sobre a taxa de contágio da doença.
        #     Enquanto o <i>R0</i> é um número geral, portanto, o  então é calculado para cada local e
        #     momento no tempo. Por exemplo, um <i>Rt</i> maior do que 1 indica que, mantendo-se o
        #     comportamento e intervenções ativas até aquele dia, ainda há tendência de crescimento
        #     exponencial da doença naquela população. Esperamos que cada pessoa infectada naquele momento
        #     infectará mais de uma pessoa no futuro - gerando uma curva de contágio que se acelera
        #     rapidamente. Já um <i>Rt</i> abaixo de 1 se traduz na expectativa de que o número de novas infecções 
        #     vai diminuir ao longo do tempo, indicando que a situação está sob controle se todas as medidas e
        #     comportamentos forem mantidos.<br><br>Uma boa notícia: por causa da mudança de comportamento, o
        #     <i>Rt</i> tende a ser menor que o <i>R0</i>, como explicam os desenvolvedores do
        #     <i>CovidActNow</i>. Calculá-lo também nos permite, portanto, comparar qual seria a evolução
        #     do contágio da Covid-19 caso medidas restritivas de contato e contágio não tivessem sido
        #     adotadas.<br> Medir diretamente o número efetivo de reprodução da Covid-19 não é possível.
        #     Porém, podemos estimar o número de reprodução instantâneo (<i>Rt</i>) mais provável pelo
        #     número de novos casos por dia.<br><br>
        #     <span class="subsection-header"><b>Como funciona o modelo?</b></span><br> 
        #     O modelo utilizado para o cálculo do Rt foi desenvolvido por Cori et.
        #     al (2013) e implementado no pacote <i>EpiEstim</i>, podendo ser utilizado no R (linguagem de
        #     programação) ou no Excel. Ele toma como entrada a série de casos da doença na população e
        #     estima o Rt utilizando um modelo bayesiano. Esse modelo estima a distribuição a posteriori
        #     do Rt dado o número de casos ativos no tempo <i>t</i> e a infectividadde da doença no local.
        #     A infectividade pode ser entendida como a probabilidade de um indivíduo infectar pessoas o
        #     momento de evolução da doenca no qual se encontra - por exemplo, um indivíduo com Covid no
        #     4º dia de sintomas é mais infeccioso que o um indivíduo no 15º dia.  Esse valor não é
        #     observado, portanto, é estimado pela distribuição esperada do tempo de geração da doença
        #     (intevalo serial) - que é o tempo esperado entre uma pessoa apresentar os sintomas e uma
        #     pessoa contaminada por esta passar a apresentar os sintomas da doença. Esse número para a
        #     Covid hoje segue uma distribuição com média de 4.7 e desvio padrão de 2.9 (Hiroshi, 2020).<br><br>
        #     Dada a série de novos casos por dia, e a média e desvio padrão do intervalo serial, o modelo
        #     então estima o valor mais provável do número de reprodução básica da doença no tempo
        #     <i>t</i> e os respectivos intervalos de confiança. Utilizamos o intevalo de 95% de confiança
        #     para reportar as estimativas.
        #     </div>""",
        #     unsafe_allow_html=True,
        # )

    if (
        indicador
        == "CAPACIDADE DO SISTEMA: Dias até atingir ocupação total de leitos enfermaria"
    ):

        st.write(
            """<div class="base-wrapper">Ver metodologia do SimulaCovid: a capacidade hospitalar é projetada com os dados mais recentes da doença no município, regional ou estado.
                </div>""",
            unsafe_allow_html=True,
        )

    st.write(
        """<div class="base-wrapper primary-span">
            <span class="section-header">FERRAMENTAS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ferramenta = st.radio(
        "Selecione abaixo uma das ferramenta para ver mais detalhes:",
        ["FarolCovid (acima)", "SimulaCovid", "Saúde em Ordem",],
    )

    if ferramenta == "FarolCovid (acima)":
        pass

    if ferramenta == "Saúde em Ordem":
        st.write(
            """<div class="base-wrapper primary-span">
                <span class="section-header">SAÚDE EM ORDEM</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        saude_em_ordem_description.main(session_state)

    if ferramenta == "SimulaCovid":
        st.write(
            """<div class="base-wrapper primary-span">
                <span class="section-header">SIMULACOVID: Modelo Epidemiológico</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        model_description.main(session_state)

    st.write(
        """<div class="base-wrapper primary-span">
            <span class="section-header">FONTES DE DADOS</span>
        </div>""",
        unsafe_allow_html=True,
    )

    gen_table()

    st.write(
        """<div class="base-wrapper primary-span">
            <span class="section-header">REFERÊNCIAS</span>
        </div>""",
        unsafe_allow_html=True,
    )

    st.write(
        """<div class="base-wrapper">
        Agência Nacional de Saúde Suplementar, 2012. Taxa de Ocupação Operacional Geral. Disponível em:
        http://www.ans.gov.br/images/stories/prestadores/E-EFI-03.pdf <br> <br>CDC, 2019. Severe Outcomes
        Among Patients with Coronavirus Disease 2019 (COVID-19) — United States, February 12–March 16, 2020.
        MMWR Morb Mortal Wkly Rep. ePub: 18 March 2020. DOI: http://dx.doi.org/10.15585/mmwr.mm6912e2.<br>
        <br>G. Stein, V. N. Sulzbach and Lazzari. Nota Técnica sobre o Índice Setorial para Distanciamento
        Controlado.  Technical report, 2020<br> <br>Cori, A., Ferguson, N.M., Fraser, C. and Cauchemez, S., 2013. A new framework and software to estimate time-varying reproduction numbers during epidemics. American journal of epidemiology, 178(9), pp.1505-1512. 
        <br> <br> Hill, A, 2020. Model Description. Modelling COVID-19 Spread vs
        Healthcare Capacity. Disponível em: https://alhill.shinyapps.io/COVID19seir/<br> <br>Lazaro Gamio.
        The workers who face the greatest coronavirus risk, 2020.
        https://www.nytimes.com/interactive/2020/03/15/business/economy/coronavirus-worker-risk.html.<br> <br>
        Li, R., Pei, S., Chen, B., Song, Y., Zhang, T., Yang, W., & Shaman, J., 2020. Substantial
        undocumented infection facilitates the rapid dissemination of novel coronavirus (SARS-CoV2).
        Science, 3221(March), eabb3221. DOI: https://doi.org/10.1126/science.abb3221<br> <br>Max Roser, Hannah
        Ritchie, Esteban Ortiz-Ospina and Joe Hasell (2020) - "Coronavirus Disease (COVID-19)". Published
        online at OurWorldInData.org. Retrieved from: 'https://ourworldindata.org/coronavirus' [Online
        Resource]<br> <br>Ministério da Saúde do Brasil, 2020. Boletim Diário. 28 mar. 2020. Disponível em:
        https://www.saude.gov.br/images/pdf/2020/marco/28/28.03%20-%20COVID.pdf
        <br> <br>Nishiura, Hiroshi, Natalie M. Linton, and Andrei R. Akhmetzhanov. "Serial interval of novel coronavirus (COVID-19) infections." International journal of infectious diseases (2020).<br> <br>Vanessa Neumann Sulzbach.
        Essays on Labor Market Polarization in Brazil. Unpublished PhD’s Thesis, 2020.<br> <br>Verity, Robert, et
        al. "Estimates of the severity of coronavirus disease 2019: a model-based analysis." The Lancet
        infectious diseases (2020). Disponível em:
        https://www.medrxiv.org/content/10.1101/2020.03.09.20033357v1 <br> <br>Walker, P.G., Whittaker, C., Watson,
        O., Baguelin, M., Ainslie, K.E.C., Bhatia, S., Bhatt, S., Boonyasiri, A., Boyd, O., Cattarino, L.
        and Cucunubá, Z., 2020. The global impact of COVID-19 and strategies for mitigation and suppression.
        Imperial College London, doi: https://doi. org/10.25561/77735. <br> <br>[1] Wang, C, et al. (2020) Evolving
        Epidemiology and Impact of Non-pharmaceutical Interventions on the Outbreak of Coronavirus Disease
        2019 in Wuhan, China. DOI: https://doi.org/10.1101/2020.03.03.20030593 e pdf de apresentação
        https://docs.google.com/presentation/d/1-rvZs0zsXF_0Tw8TNsBxKH4V1LQQXq7Az9kDfCgZDfE/edit#slide=id.p1
        <br> <br>[2] Wang, J., Zhou, M., & Liu, F., 2020. Reasons for healthcare workers becoming infected with novel
        coronavirus disease 2019 (COVID-19) in China. Journal of Hospital Infection. DOI:
        https://doi.org/10.1016/j.jhin.2020.03.002 <br> <br>Y. O. de Lima, D. M. Costa, and J. M. de Souza. Covid-19:
        Risco de contágio por ocupação no Brasil: Nota metodológica. Technical report, 2020.
        <br>
        </div>""",
        unsafe_allow_html=True,
    )


def gen_table():
    st.write(
        """
        <style type="text/css">
        .tg  {border-collapse:collapse;border-spacing:0;}
        </style>
        <table class="tg" style="undefined;table-layout: fixed; width: 1000px;margin:auto;">
        <colgroup>
        <col style="width: 98px">
        <col style="width: 93px">
        <col style="width: 150px">
        </colgroup>
        <thead>
        <tr>
            <th class="tg-7btt">Dado</th>
            <th class="tg-7btt">Fonte</th>
            <th class="tg-amwm">Data de coleta</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td class="tg-fymr">População residente por município e regional de saúde</td>
            <td class="tg-0lax"><a class="github-link" href="https://www.ibge.gov.br/apps/populacao/projecao/">IBGE</a></td>
            <td class="tg-0pky">Dados referentes a 2019. Atualizado diariamente.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Leitos comuns por regional de saúde (clínicos + cirúrgicos  + hospital-dia)</td>
            <td class="tg-0lax"><a class="github-link" href="http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/leiintbr.def">Cadastro Nacional de Estabelecimentos de Saúde (DATASUS CNES)</a></td>
            <td class="tg-0pky">Dados referentes a junho/2020. Atualizado diariamente.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Leitos UTI por regional de saúde</td>
            <td class="tg-0lax"><a class="github-link" href="http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/leiutibr.def">Cadastro Nacional de Estabelecimentos de Saúde (DATASUS CNES)</a></td>
            <td class="tg-0pky">Dados referentes a junho/2020. Atualizado diariamente.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Casos e mortes confirmados por município (dados coletados das secretarias de saúde estaduais)</td>
            <td class="tg-0lax"><a class="github-link" href="https://brasil.io/dataset/covid19/boletim">Brasil.io</a></td>
            <td class="tg-0pky">Atualizado diariamente.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Estimativa do número de pessoas com sintomas de síndrome gripal no mercado formal e informal</td>
            <td class="tg-0lax"><a class="github-link" href="https://covid19.ibge.gov.br/pnad-covid/">PNAD Covid</a></td>
            <td class="tg-0pky">Dados referentes a 16/07/2020.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Exposição da ocupação a doenças e infecções e intensidade e extensão de contatos físicos no ambiente de trabalho</td>
            <td class="tg-0lax"><a class="github-link" href="https://www.onetonline.org/">The Occupational Information Network (O*NET)</a></td>
            <td class="tg-0pky">Acesso indireto através do trabalho desenvolvido com o governo do Rio Grande do Sul (RS).</td>
        </tr>
        <tr>
            <td class="tg-fymr">Estimativa do número de empregados de cada ocupação e sua remuneração no setor informal</td>
            <td class="tg-0lax"><a class="github-link" href="">Pesquisa Nacional Domiciliar Contínua (PNADc)</a></td>
            <td class="tg-0pky">Divulgação anual. Última atualização: 2019.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Número de empregados de cada ocupação e sua remuneração no setor formal</td>
            <td class="tg-0lax"><a class="github-link" href="https://www.onetonline.org/">Relação Anual de Informações Sociais (RAIS)</a></td>
            <td class="tg-0pky">Divulgação anual. Última atualização: 2019.</td>
        </tr>
        <tr>
            <td class="tg-fymr">Índice de Isolamento social inLoco dos municípios e estados brasileiros</td>
            <td class="tg-0lax"><a class="github-link" href="https://www.onetonline.org/">inLoco</a></td>
            <td class="tg-0pky">Atualizado diariamente.</td>
        </tr>
        </tr>
        </tbody>
        </table>""",
        unsafe_allow_html=True,
    )
