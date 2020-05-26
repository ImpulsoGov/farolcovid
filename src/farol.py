import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image



def main():

    st.header("""Níveis de Risco: como saber se estou no controle da Covid-19?""")

    st.write("""
    <span>
                Até que uma vacina ou tratamento sejam encontrados para a Covid-19, 
                será necessário <strong>controlar a quantidade de pessoas infectadas, para ter 
                certeza de que o sistema de saúde terá capacidade de atender a todas e
                todos e não venha a colapsar.</strong><br><br>
                Depois de um primeiro momento de mitigação da Covid-19 nos estados e municípios 
                brasileiros, passamos a uma nova fase da resposta à pandemia, quando será necessário 
                avaliar, a cada momento, qual a abordagem mais adequada para seu município ou estado, 
                de acordo com informações sobre a dinâmica de transmissão da doença e sua capacidade de resposta.<br><br>
                Enquanto muitas cidades já convivem com um número alto de casos diagnosticados, outros municípios ainda não 
                registram internações ou óbitos por Covid-19. Tampouco o "pico" do número de casos e óbitos será atingido ao 
                mesmo tempo em todo o território.<br><br>
                Ainda que haja medidas indicadas para todas as situações, como os protocolos de higienização e a adoção de um 
                espaço de segurança entre as pessoas em espaços compartilhados, em um país de dimensões continentais como o Brasil, 
                a resposta à pandemia do coronavírus precisa considerar a capacidade hospitalar de cada região e o momento onde cada 
                um se encontra na evolução da doença.<br><br>
                </span><br><br>
    """,
    unsafe_allow_html=True,
    )

    st.subheader("Níveis de risco de colapso do sistema de saúde")

    st.write("""
    <span>
                Inspirados pelo <a href="https://distanciamentocontrolado.rs.gov.br/">modelo do Rio Grande do Sul</a>, 
                desenvolvemos um sistema de níveis de risco de colapso do sistema de saúde, seja por um ritmo 
                de contágio mais elevado ou por uma baixa capacidade do sistema em si.<br><br>
                A classificação em níveis de risco é <strong>dinâmica</strong>, indicando que ela muda conforme os indicadores das cidades 
                e municípios são atualizados, diariamente. Portanto, aconselhamos que seja feito um acompanhamento frequente 
                do Farol Covid por parte de gestores.<br><br>
                Esses números podem, ainda, ser uma importante ferramenta para comunicação com os cidadãos, servindo de embasamento 
                e justificativa para a tomada de decisão adequada a cada realidade local. O público, em geral, também pode utilizar 
                esses números para engajar o poder público em um debate informado sobre quais são as melhores políticas para sua cidade ou Estado.<br><br>
                Para desenvolver os níveis de risco do Farol Covid, avaliamos três indicadores-chave:<br><br>
                <ul>
                    <li><strong>Ritmo de contágio,</strong> que traduz para quantas pessoas cada pessoa doente transmitirá a doença. 
                    Ele é calculado por meio de uma atualização do estimador do número efetivo de reprodução da Covid-19, a partir do 
                    número de novos casos registrados por dia. O Ritmo de contágio indica qual é o cenário futuro esperado para a doença. 
                    Para mais informações de como esse número é calculado, acesse nossa metodologia do estimador de $$R_t$$ na aba à esquerda.</li>
                    <li><strong>Taxa de subnotificação,</strong> que estima a quantidade de pessoas doentes que não são diagnosticadas. Ela é calculada considerando 
                    uma taxa de mortalidade padrão de 2% e estimando quantos casos teriam que estar ativos para produzir o número de mortos registrados 
                    naquele estado ou município. É um indicador da necessidade de realizar mais testes na população. Para mais informações sobre como esse 
                    número é calculado, acesse nossa metodologia na aba à esquerda.</li>
                    <li><strong>Capacidade hospitalar,</strong> que reporta a estimativa do número de dias até que todos os leitos da rede de saúde disponíveis 
                    para Covid-19 estarão ocupados. Ela é feita utilizando o modelo do SimulaCovid calibrado com o ritmo de contágio atual. É um 
                    indicador do tempo que o gestor pode ter para reagir, caso venha a registrar um aumento inesperado no número de casos. Para 
                    mais informações sobre como esse número é calculado, acesse nossa metodologia do modelo na aba à esquerda.</li>
                </ul>
                Ainda não há estudos científicos que indiquem a relação exata entre a Taxa de Isolamento e o seu impacto no Ritmo de 
                Contágio para municípios brasileiros; portanto, essa versão do Farol Covid informa ao gestor público qual é o nível de 
                isolamento social, mas não o inclui no cálculo para classificação de níveis de risco.<br><br>
                <figure>
                <img src="https://drive.google.com/file/d/1kWmvFDhgQokZtTn3PDV4O2h17umPnIeG/view" alt="img" class="ilustracao_cenarios">
                </figure>
                Avaliamos se os três indicadores-chave estão bons, insatisfatórios ou ruins, avaliamos suas tendências 
                (se estão crescendo, estáveis ou diminuindo) e então classificamos o município ou estado no nível de risco 
                equivalente: baixo, médio ou alto risco de colapso do sistema de saúde.<br><br>
                Os indicadores são avaliados da seguinte forma:<br><br>
                <ul>
                    <li><strong>Ritmo de Contágio</strong><br><br>
                    <ul>
                        <li><strong style="color:green">Bom</strong>: < 1, indicando que cada pessoa doente infecta menos de uma nova pessoa;</li>
                        <li><strong style="color:yellow">Insatisfatório</strong>: entre 1 e 1.2, indicando o início de um comportamento exponencial de crescimento do número de pessoas doentes;</li>
                        <li><strong style="color:red">Ruim</strong>: > 1.2, indicando que há um crescimento exponencial do número de pessoas sendo infectadas.</li>
                    </ul>
                         </li>
                    <li><strong>Tendência do ritmo de contágio</strong><br><br>
                    <ul>
                        <li><strong style="color:green">Descendo</strong>: A taxa reportada há 10 dias é menor do que aquela reportada 17 dias atrás, indicando que o ritmo de contágio pode ter continuado a cair nos últimos 10 dias;</li>
                        <li><strong style="color:yellow">Estável</strong>: A taxa reportada há 10 dias é 0.9 a 1.1 vezes aquela reportada 17 dias atrás, indicando que o ritmo de contágio pode ter se mantido semelhante nos últimos 10 dias;</li>
                        <li><strong style="color:red">Subindo</strong>: A taxa reportada há 10 dias é maior do que aquela reportada 17 dias atrás, indicando que o ritmo de contágio tenha continuado a subir nos últimos 10 dias.</li>
                    </ul> </li>
                    <li><strong>Taxa de subnotificação</strong><br><br>
                    <ul>
                         <li><strong style="color:green">Bom</strong>: < 50%, indicando que o número de casos registrados não está tão distante do esperado quando comparado com o número de mortos. Aceitamos esse limite de 50% pois pode ser o caso da mortalidade ser mais alta naquele município ou estado por um padrão de vulnerabilidade da população;</li>
                        <li><strong style="color:yellow">Insatisfatório</strong>: entre 50 e 70%, indicando que o número de casos registrados está distante do esperado quando comparado com o número de mortos;</li>
                        <li><strong style="color:red">Ruim</strong>: > 70%. Indica que o número de casos registrados está muito pequeno quando comparado com o número de mortos confirmados com Covid-19. Indica que há falta de testagem.</li>
                    </ul> </li>
                    <li><strong>Capacidade Hospitalar</strong><br><br>
                    <ul>
                        <li><strong style="color:green">Bom</strong>: > 60 dias até que todos os leitos estejam ocupados com pacientes com Covid-19, indicando que o poder público terá tempo para organizar uma resposta caso o número de casos venha a crescer de modo inesperado;</li>
                        <li><strong style="color:yellow">Insatisfatório</strong>: entre 30 e 60 dias até que todos os leitos estejam ocupados com pacientes com Covid-19;</li>
                        <li><strong style="color:red">Ruim</strong>: < 30 até que todos os leitos estejam ocupados com pacientes com Covid-19, indicando que o gestor terá pouco tempo de reação antes do colapso do sistema de saúde, caso haja um crescimento inesperado no número de casos.</li>
                    </ul> </li>
                </ul>
    </span><br>
    """,
    unsafe_allow_html=True,
    )
    st.subheader(
        "Regras de classificação para os níveis de risco")
    st.write("""
    <span>
        <strong style="color:green">Nível de Risco Baixo</strong>  se satisfizer todos os seguintes requisitos:<br><br>
            <ul>
                <li><strong>Ritmo de contágio</strong> <strong style="color:green">Bom</strong> ($$Rt$$ < 1.0), 
                    indicando que o número de pessoas doentes está decrescendo;</li>
                <li><strong>Ritmo de contágio em tendência </strong><strong style="color:yellow"> estável</strong> <strong> ou</strong>
                     </strong><strong style="color:green">queda</strong>, indicando que esperamos que o ritmo de contágio não retomará 
                     uma trajetória ascendente;</li>
                <li><strong>Subnotificação em nível </strong><strong style="color:green">Bom</strong> (< 50%), 
                    indicando haver um bom nível de testagem da população;</li>
                <li><strong>Capacidade hospitalar em nível </strong><strong style="color:green">Bom</strong> (maior que 60 dias) 
                    ou Insatisfatório (entre 30 e 60 dias), indicando que o sistema de saúde tem capacidade de ser reorganizado 
                    antes de atingir capacidade, caso haja um crescimento inesperado no número de casos.</li>
            </ul>
        <strong style="color:red">Nível de Alto Baixo</strong>  se satisfizer todos os seguintes requisitos:<br><br>
            <ul>
                <li><strong>Ritmo de contágio</strong> <strong style="color:red">Ruim</strong> ($$Rt$$ > 1.2), 
                    indicando que ainda há um crescimento exponencial da doença na cidade ou estado;</li>
                <li><strong>Ritmo de contágio em tendência </strong><strong style="color:red"> subindo</strong>, indicando que esperamos 
                    que o ritmo de contágio esteja atualmente maior do que o reportado;</li>
                <li><strong>Subnotificação</strong><strong style="color:red">Ruim</strong>  (> 70%), indicando que esperamos haver um número de 
                    infectados maior do que o registrado;</li>
                <li><strong>Capacidade hospitalar em nível </strong><strong style="color:red">Ruim</strong> (< 30 dias), indicando que não há 
                    tempo de reação para evitar o colapso do sistema de saúde</li>
            </ul>
        Os demais casos que tiverem todos os indicadores são considerados de <strong>Nível de Risco Médio</strong>, como, por exemplo:
            <ul>
                <li>Ritmo de contágio <strong style="color:green">Bom</strong> (< 1.0), mas com subnotificação em nível <strong style="color:Yellow">Insatisfatório</strong> 
                    (entre 50 e 70%), pois pode ser que o ritmo de contágio seja apenas reflexo de testagem insuficiente.
                </li>
            </ul>
        Caso o município não conte com algum dos indicadores, mostramos o número correspondente para o nível estatal. 
        Nesse caso, ele não terá classificação de risco. <br><br>
        Confira abaixo a distribuição dos municípios e estados brasileiros de acordo com os diferentes indicadores. <br><br>
    </span>
    """,
    unsafe_allow_html=True,
    )

    st.write(
        """
        <span>
        <br><br>
            <strong>INSERIR PLOT DA DISTRIBUIÇÃO DOS MUNICÍPIOS NOS INDICADORES</strong><br>
            <strong>INSERIR PLOT DA DISTRIBUIÇÃO DOS ESTADOS NOS INDICADORES</strong>
        <br><br>
        </span>
        """,
    unsafe_allow_html=True,
    
    )

    st.subheader(
        "Essas métricas são suficientes?")


    st.write(
        """
        <span>
            Não. Desenvolvemos os níveis de risco do Farol Covid com informações disponíveis online. É um primeiro passo para o 
            gestor orientar sua tomada de decisão de maneira informada, orientado por dados que o atualizam tanto sobre o estágio 
            de evolução da doença em seu estado ou município quanto sua capacidade de resposta. <br><br>
            O gestor público, entretanto, conta com uma riqueza maior de informações que deve ser utilizada na formulação de respostas 
            adequadas à sua realidade. Informações como a quantidade de testes realizados, a taxa de pessoas que testam positivo e o tempo 
            médio de internação são outros fatores importantes para a tomada de decisão. Estamos à disposição para apoiar o gestor público 
            a aprofundar a análise para seu estado ou município, de forma inteiramente gratuita. Entre em contato pelo Coronacidades.org! <br><br>
        </span>
        """,
    unsafe_allow_html=True,
    
    )
    st.subheader(
        "Referências e inspirações")
    st.write(
        """
        <span>
         Rio Grande do Sul, <a href="https://distanciamentocontrolado.rs.gov.br/">Modelo de Distanciamento Controlado</a><br>
         <a href="https://covidactnow.org/">COVID ActNow</a><br>
         <a href="https://blog.covidactnow.org/modeling-metrics-critical-to-reopen-safely/">A Dashboard to Help America Open Safely</a>
         </span>
        """,
    unsafe_allow_html=True,
    
    )

if __name__ == "__main__":
    main()


