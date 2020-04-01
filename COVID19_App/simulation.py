import streamlit as st

def main():
        st.title("SimulaCovid")
        st.subheader('Como seu município pode se preparar para a Covid-19')
        

        st.write('## SimulaCovid é um simulador da demanda por leitos hospitalares e ventiladores.')        

        st.write('''
*Usando dados do DataSUS e de casos confirmados, ele estima por quantos dias - até o limite de 90 - 
durará o estoque desses equipamentos em cada município. Ao explorar diferentes estratégias de resposta 
à crise, a ferramenta permite que gestores públicos simulem abordagens e planejem seu curso de ação para 
evitar o colapso do sistema.*
        ''')


        st.write('''
Confira nossa metodologia e o github do projeto. Acesse nossas Perguntas Frequentes.
        ''')

        st.write('## Qual a situação do seu município?')     

        st.write('### Selecione seu município ao lado para gerar as projeções')

        st.selectbox('Município', ['Campinas'])


        st.write('# <CASOS CONFIRMADOS>')
        st.write('# <MORTES CONFIRMADAS>')

        st.write('''
**Fonte:** Brasil.IO atualizado diariamente com base em boletins das secretarias de saúde publicados.
        ''')

        st.write('''
**Lembramos que podem existir casos não diagnosticados em sua cidade.** Sugerimos que consulte o
 Checklist para orientações específicas sobre o que fazer antes do primeiro caso diagnosticado.
        ''')

        st.write('''
### Seu município tem a seguinte **capacidade hospitalar:**
        ''')

        st.write('# <LEITOS>')
        st.write('# <VENTILADORES>')

        st.write('''
Fonte: DATASUS CNes, Fevereiro 2020. Incluímos leitos hospitalares da rede SUS 
e não-SUS. Para excluir a última categoria, precisaríamos estimar também a 
opulação susdependente. Para mais informações, confira nossa metodologia.
        ''')


        st.write('''
A maioria das pessoas que contraem Covid-19, conseguem se recuperar em casa - 
mas uma parte irá desenvolver sintomas graves e precisará de internação em 
leitos hospitalares. Outros terão sintomas críticos e precisarão de ventiladores 
mecânicos e tratamento intensivo (UTI). Apesar de serem necessários outros 
insumos, esses têm sido fatores limitantes na resposta à crise.
        ''')

        st.write('''
### Assumiremos que 20% destes poderão ser destinados a pacientes com Covid-19 
(você poderá ajustar abaixo). Caso seu município conte apenas com atitudes 
individuais, **sem políticas de restrição de contato, estima-se que....**
        ''')

        st.write('# <DDAY LEITOS WORST>')
        st.write('# <DDAY VENTILADORES WORST>')

        st.write('''
### Caso o município decrete hoje o isolamento social, **fechando comércios e 
suspendendo transporte público, além de quarentena para doentes, estima-se que...**
        ''')

        st.write('# <DDAY LEITOS BEST>')
        st.write('# <DDAY VENTILADORES BEST>')

        st.write('# E como me preparo?')

        st.write("""
Em Wuhan, na China, onde foi registrado o primeiro caso de Covid-19, o governo 
eagiu em fases para controlar a transmissão da doença, expandir sua capacidade 
de tratar casos graves e críticos e aliviar a pressão no sistema de saúde pública.

Este modelo se baseia na sequência de estratégias apresentadas abaixo (veja Metodologia):        
""")

        st.write("""
**ESTRATÉGIA 1:** Mais pessoas escutam falar da Covid-19, com o início da 
confirmação de casos. Algumas começam a tomar precauções individuais, mas 
nenhuma medida de restrição de contato é adotada pelas autoridades.     
""")

        st.write("""
**ESTRATÉGIA 2:** O governo decreta o fechamento das fronteiras e do comércio 
não-essencial, além de restringir o transporte público e toda circulação não 
estritamente necessária (medidas de restrição) - tomando porém medidas para 
garantir o abastecimento de alimentos e remédios nas cidades. O uso de máscaras
 em espaços públicos se torna obrigatório. Casos confirmados e suspeitos de 
 Covid-19 são isolados em suas casas.   
""")

        st.write("""
**ESTRATÉGIA 2:** O governo amplia a capacidade de testes e proíbe estritamente
 o movimento das pessoas não-autorizadas (lockdown), com forte monitoramento, 
 mas sem prejuízo ao abastecimetno das cidades de ítens essenciais. Casos 
 confirmados são isolados em hospitais, escolas e hotéis designados. 
 Profissionais de saúde recebem equipamentos de proteção individual adequados 
 e alojamento, para evitar infecção de suas famílias. 
""")

        st.write("""
A Estratégia 3 exigiu um esforço coordenado entre governo e sociedade: foram 
parceiros no investimento em expansão de leitos e fornecimento de equipamentos 
de saúde. Ao reduzir a transmissão e expandir a capacidade de tratamento, a 
cidade conseguiu "virar a curva."
""")

        st.write("""
## Simule o impacto de estratégias semelhantes na capacidade o sistema de saúde em sua cidade:
""")


        st.write("""
## Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?
""")
        st.number_input('Dias:', 0, 90, 90, key='strategy2')

        st.write("""
## Em quantos dias você quer acionar a Estratégia 3, lockdown?
""")

        st.number_input('Dias:', 0, 90, 90, key='strategy3')

        st.write("""
## A partir desses números, ajuste a capacidade que será alocada na intervenção:?
""")

        st.write("""
## Mude o percentual de leitos destinados aos pacientes com Covid-19:
""")
        st.number_input('Leitos:', 0, None, 90)

        st.write("""
## Mude o percentual de ventiladores destinados aos pacientes com Covid-19:
""")

        st.number_input('Ventiladores:', 0, None, 90)

        st.write("""
# <Simulador da demanda hospitalar>
""")


        st.write("""
A presente ferramenta, voluntária, parte de estudos referenciados já 
publicados e considera os dados de saúde pública dos municípios brasileiros 
disponibilizados no DataSus.
""")

        st.write("""
Os cenários projetados são meramente indicativos e dependem de variáveis
 que aqui não podem ser consideradas. Trata-se de mera contribuição à 
 elaboração de cenários por parte dos municípios e não configura qualquer 
 obrigação ou responsabilidade perante as decisões efetivadas. Saiba mais em 
 nossa metodologia.
""")

        st.write("""
Estamos em constante desenvolvimento e queremos ouvir sua opinião sobre a 
ferramenta - caso tenha sugestões ou comentários, entre em contato via o chat 
ao lado. Caso seja gestor público e necessite de apoio para preparo de seu 
município, acesse a Checklist e confira o site do CoronaCidades.
""")

        st.write("""
Esta plataforma foi desenvolvida por:

João Carabetta, Mestre em Matemática Aplicada pela FGV
Fernanda Scovino, Graduada em Matemática Aplicada pela FGV
Diego Oliveira, Mestre em Física Aplicada pela Unicamp
Ana Paula Pellegrino, Doutoranda em Ciência Política da Georgetown University
""")

        st.write("""
    < IMAGE IMPULSO >
""")

        st.write("""
   com colaboração de:

Fátima Marinho, Doutora em Epidemiologia e Medicina Preventiva pela USP e 
professora da Faculdade de Medicina da Universidade de Minas Gerais
Sarah Barros Leal, Médica e Mestranda em Saúde Global na University College London
H. F. Barbosa, Mestre em Relações Internacionais pela Universidade da Califórnia, San Diego
Teresa Soter, mestranda em Sociologia na Oxford University

Toda a documentação da ferramenta está disponível aqui.
""")

        st.write("""
    < IMAGES IMPULSO ARAPYAU CORONACIDADES>
""")

        
if __name__ == "__main__":
    main()