import streamlit as st
import pandas as pd

def main():
    pic = open('imgs/model_graph', 'r').read()
    st.image(pic, use_column_width=True, caption=None)
    
    st.write("""
    Esta ferramenta utiliza uma variação do modelo epidemiológico SEIR para estimar a demanda
    por leitos hospitalares e ventiladores nos municípios brasileiros. 
    Trabalhamos com 3 estratégias distintas, baseados na resposta do governo 
    e da sociedade em relação a medidas de restrição de contato. Cada 
    estratégia está associada a uma taxa de infecção distinta da Covid-19 
    (quantas novas pessoas serão infectadas por uma pessoa que já está doente,
    ao longo da evolução de seu quadro)  As taxas foram estimadas por estudos
    em diferentes momentos. Assim, ao indicar quando cada uma entrará em 
    vigor no município selecionado, é possível simular a evolução da doença
    associada à sequência de estratégias indicada.

    O objetivo do simulador é chamar atenção para o potencial impacto de 
    políticas públicas desenhadas para responder à crise e contribuir com a 
    elaboração de cenários para os processos decisórios locais diante da 
    expansão da Covid-19 no Brasil. Ressaltamos, porém, que cada cidade possui 
    dinâmicas de circulação e contato social próprias, além de particularidades 
    demográficas e disponibilidade de equipamentos de saúde. Por isso, preferimos 
    trabalhar com margens de erro e calcular janelas temporais.

    Pelo pouco tempo de circulação, ainda não há números de referência 
    estabelecidos sobre a transmissão do vírus SARS COV-2, o "Coronavírus." 
    A partir de dados brasileiros de referência de transmissão, pretendemos 
    elaborar nova versão da ferramenta. A análise também não considera o 
    desenvolvimento de medidas de mitigação como vacinas e medicamentos anti-virais.
    """)

    st.header('Fonte de Dados')

    st.write("""
    Os dados iniciais utilizados na ferramenta foram coletados de:
    """)

    st.table(pd.DataFrame([
    {'Dado': 'Projeção de População',
    'Fonte': 'IBGE',
    'Data de Coleta': '2020-03-29',
    'URL': 'https://www.ibge.gov.br/apps/populacao/projecao/'},
    {'Dado': 'Leitos por Município',
    'Fonte': 'DATASUS CNES',
    'Data de Coleta': '2020-03-29',
    'URL': 'http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/leiintbr.def'},
    {'Dado': 'Ventiladores por município',
    'Fonte': 'DATASUS CNES',
    'Data de Coleta': '2020-03-29',
    'URL': 'http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/equipobr.def'},
    {'Dado': 'Projeção de População',
    'Fonte': 'Brasil.io',
    'Data de Coleta': 'Diariamente',
    'URL': 'https://brasil.io/dataset/covid19/boletim'},
    ]))

    st.write("""
    Para essa versão, também integraremos dados atualizados enviados pelos 
    nossos Embaixadores. Este será devidamente identificado como sendo contribuição 
    do Embaixador ou como input do programa - quando a pessoa preferir colaborar 
    de maneira anônima. Para ser um embaixador, inscreva-se [aqui](https://forms.gle/iPFE7T6Wrq4JzoEw9)

    A quantidade de leitos por municípios soma tanto leitos hospitalares da rede 
    do Sistema Único de Saúde quanto da rede não-SUS. Avaliamos que ambas estariam 
    envolvidas no esforço de resposta à crise. Para usar por base apenas a rede 
    SUS, seria necessário filtrar a população SUS-dependente de cada município.

    O número de leitos que usamos como base para nossos cálculos inclui leitos 
    complementares. Retiramos os de tratamento intensivo, já que nossa medida 
    de possibilidade de adaptação para essa modalidade é a disponibilidade de 
    ventiladores. 

    Consideramos, na simulação inicial, que apenas 20% dos leitos registrados 
    no Cadastro Nacional de Estabelecimentos Hospitalares estariam disponíveis 
    para alocação de pacientes da Covid-19 que necessitem de internação. Esse 
    número cai dentro do parâmetro recomendado pela Agência Nacional de Saúde 
    Suplementar (ANS), de manutenção da taxa de ocupação de hospitalar entre 
    75 e 85%, ainda que saibamos que há grande variação nesse percentual nas 
    realidades locais de cada município (ANS, 2012). 

    Caso um percentual maior ou menor esteja alocado para pacientes com Covid-19, 
    é possível ajustar a quantidade de leitos alocados para a simulação final.

    Para municípios que não tem casos confirmados em boletins oficiais, conforme 
    reportado no Brasil.io, simulamos os números a partir do primeiro caso. 
    Isso quer dizer que, ao selecionar unidades de análise mais altas, portanto, 
    como as regionais de saúde ou os estados, você está simulando um cenário 
    onde todos os municípios têm ao menos um caso confirmado. O mesmo ocorre com 
    simulações ao nível da regional de saúde - que consideram haver ao menos um 
    caso ativo em cada cidade.

    Os números de casos confirmados são atualizados diariamente, depois da 
    atualização no Brasil.io, que busca suas informações em boletins epidemiológicos 
    estaduais 

    Sabemos que há diferenças entre os números divulgados pelos estados e aqueles 
    publicados pela gestão municipal. Por isso, permitimos que o gestor também 
    ajuste esse número na hora da simulação. Isso também permite ao gestor somar 
    o número de casos suspeitos, que ainda aguardam confirmação. Esse número 
    também pode ser reportado em nosso programa de [Embaixadores](https://forms.gle/iPFE7T6Wrq4JzoEw9)
    e será devidamente creditado quando esta for a fonte.
    """
    )

    st.header("EM CONSTRUÇÃO...")

    st.header("MODELO")
    st.write("""
    Utilizamos um modelo epidemiológico compartimental, baseado no modelo SEIR 
    clássico, para descrever a disseminação e progressão clínica do COVID-19. 
    Uma boa cartilha para esse tipo de modelo está disponível na [Wikipedia 
    (em inglês)](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology). 
    É importante rastrear os diferentes resultados clínicos da infecção, uma 
    vez que eles exigem níveis diferentes de recursos de saúde para cuidar e 
    podem ser testados e isolados em taxas diferentes. Susceptível ($S$) 
    indivíduos infectados começam em uma classe $E$ exposta, onde são 
    assintomáticos e não transmitem infecção. A taxa de progressão do estágio 
    exposto para o estágio infectado $I$, onde o indivíduo é sintomático e 
    infeccioso, ocorre a uma taxa. As descrições clínicas dos diferentes 
    estágios da infecção são fornecidas abaixo. Os indivíduos infectados 
    começam com infecção leve ($I_1$), da qual eles se recuperam, na taxa 
    $γ_1$ ou progredir para infecção grave ($I_2$), à taxa $p_1$. A infecção 
    grave resolve na taxa $γ_2$ ou progride para um estágio crítico ($I_3$) na 
    taxa $p_2$. Indivíduos com infecção crítica se recuperam na taxa $γ_3$ e 
    morra na taxa $μ$. Os indivíduos recuperados são rastreados pela classe 
    $R$ e são assumidos como protegidos contra reinfecções por toda a vida. Os
    indivíduos podem transmitir a infecção em qualquer estágio, embora com 
    taxas diferentes. A taxa de transmissão no estágio $i$ é descrito por $β_i$.""")
    st.write('### Equações')
    st.latex("\dot{S} = - β_1 I_1 S_1 - β_2 I_2 S_2 - β_3 I_3 S_3")
    st.latex("\dot{E} = β_1 I_1 S_1 + β_2 I_2 S_2 + β_3 I_3 S_3 - aE")
    st.latex("\dot{I_1} = aE - γ_1 I_1 - p_1 I_1")
    st.latex("\dot{I_2} = p_1 I_1 - γ_2 I_2 - p_2 I_2")
    st.latex("\dot{I_3} = p_2 I_2 - γ_3 I_3 - p_3 I_3")
    st.latex("\dot{R} = γ_1 I_1 + γ_2 I_2 + γ_3 I_3")
    st.latex("\dot{D} = μ I_3")
        
    st.write("""### Variáveis
* $S$: Indivíduos Suscetíveis
* $E$: Indivíduos Expostos - infectados, mas ainda não infecciosos ou sintomáticos
* $I_i$: Indivíduos infectados na classe de gravidade $i$. A gravidade aumenta com $i$ e assumimos que os indivíduos devem passar por todas as classes anteriores
  * $I_1$: Infecção leve (hospitalização não é necessária) - Mild Infection
  * $I_2$: Infecção grave (hospitalização necessária) - Severe infection
  * $I_3$: Infecção crítica (cuidados na UTI necessária) - Critical infection
* $R$: Indivíduos que se recuperaram da doença e agora estão imunes
* $D$: Indivíduos mortos
* $N=S+E+I_1+I_2+I_3+R+D$ Tamanho total da população (constante)

### Parâmetros
* $βi$ taxa na qual indivíduos infectados da classe $I_i$ entram em contato com suscetíveis e os infectam
* $a$ taxa de progressão da classe exposta para a infectada
* $\gamma_i$ taxa na qual indivíduos infectados da classe $I_i$ se recuperam da doença e se tornam imunes
* $p_i$ taxa na qual indivíduos infectados da classe $I_i$ avançam para a classe $I_{I + 1}$
* $\mu$ taxa de mortalidade de indivíduos na fase mais grave da doença

Todas as taxas são por dia

### Estágios clínicos
* Infecção leve - Esses indivíduos apresentam sintomas como febre e tosse e podem apresentar pneumonia leve. A hospitalização não é necessária (embora em muitos países esses indivíduos também sejam hospitalizados)
* Infecção grave - Esses indivíduos apresentam pneumonia mais grave que causa dispnéia, frequência respiratória <30 / min, saturação sanguínea de oxigênio <93%, pressão parcial de oxigênio arterial para fração da razão inspirada de oxigênio <300 e / ou infiltrações pulmonares> 50% dentro de 24 a 48 horas. Hospitalização e oxigênio suplementar são geralmente necessários.
* Infecção crítica - Esses indivíduos apresentam insuficiência respiratória, choque séptico e / ou disfunção ou falha de múltiplos órgãos. O tratamento em uma UTI, geralmente com ventilação mecânica, é necessário.

### Relacionando observações clínicas aos parâmetros do modelo
Para determinar os parâmetros do modelo consistentes com os dados clínicos atuais, coletamos os seguintes valores a partir dos valores do controle deslizante escolhidos pelo usuário e, em seguida, usamos as fórmulas abaixo para relacioná-los aos parâmetros de taxa no modelo. Observe que as entradas do controle deslizante para intervalos de tempo são durações médias.

* IncubPeriod: período médio de incubação, dias
* DurMildInf: duração média de infecções leves, dias
* FracMild: fração média de infecções (sintomáticas) que são leves
* FracSevere: fração média de infecções (sintomáticas) graves
* FracCritical: fração média de infecções (sintomáticas) críticas
* CFR: Taxa de mortalidade de casos (fração de infecções que eventualmente resultam em morte)
* DurHosp: Duração média da hospitalização para indivíduos com infecção grave / crítica, dias
* TimeICUDeath: Tempo médio de internação na UTI até o óbito, dias

(Nota g=$γ$)""")
        
    st.code("""a=1/IncubPeriod

g1=(1/DurMildInf)*FracMild
p1=(1/DurMildInf)-g1

p2=(1/DurHosp)*(FracCritical/(FracSevere+FracCritical))
g2=(1/DurHosp)-p2

u=(1/TimeICUDeath)*(CFR/FracCritical)
g3=(1/TimeICUDeath)-u""")
        
    st.write("""
### Taxa Básica de reprodução

Ideia: $R_0$ é a soma de: 
* 1.  o número médio de infecções secundárias geradas de um indivíduo em estágio $I_1$
* 2.  a probabilidade de um indivíduo infectado progredir para $I_2$ multiplicado pelo número médio de infecções secundárias geradas a partir de um indivíduo em estágio $I_2$
* 3.  a probabilidade de um indivíduo infectado progredir para $I_3$ multiplicado pelo número médio de infecções secundárias geradas a partir de um indivíduo em estágio$I_3$""")

    st.latex("R_0 = N \\frac{β_1}{p_1 + γ_1} + \\frac{p_1}{p_1 + γ_1} \\left (\\frac{Nβ_2}{p_2 + γ_2} + \\frac{p_2}{p_2 + γ_2}\\frac{Nβ_3}{μ + γ_3}\\right )")
    st.latex(" = N \\frac{1}{p_1 + γ_1} \\left (β_1+\\frac{p_1}{p_2 + γ_2}\\left (β_2+β_3\\frac{p_2}{μ + γ_3}\\right )\\right )")
        
    st.write("""Cálculos usando a matriz de próxima geração fornecem os mesmos resultados.

### Taxa de crescimento epidêmico precoce
No início da epidemia, antes do esgotamento dos suscetíveis, a epidemia cresce a uma taxa exponencial $r$, que também pode ser descrito com o tempo de duplicação $T_2=ln(2)/r$. Durante esta fase, todas as classes infectadas crescem na mesma proporção entre si e nas mortes e indivíduos recuperados. O número acumulado de infecções que ocorreram desde o início do surto também cresce na mesma proporção. Essa taxa pode ser calculada a partir do valor próprio dominante do sistema linearizado de equações no limite em que $S = N$.

Durante esta fase de crescimento exponencial inicial, haverá uma proporção fixa de indivíduos entre qualquer par de compartimentos. Essa taxa esperada pode ser usada para estimar a quantidade de subnotificação de dados. Por exemplo, podemos pensar que todas as mortes são relatadas, mas que algumas infecções leves podem não ser relatadas, uma vez que esses pacientes podem não procurar atendimento médico ou podem não ser priorizados para o teste. Essas proporções têm valores esperados no modelo para um conjunto fixo de parâmetros. Eles podem ser calculados encontrando o vetor próprio correspondente ao valor próprio dominante ($r$) para o sistema linearizado descrito acima. As razões que divergem desses valores sugerem: a) subnotificação de casos relativos a óbitos ou b) diferenças locais nos parâmetros clínicos da progressão da doença. As razões esperadas são:""")
    st.latex("\\frac{I_3}{D} = \\frac{r}{μ}")
    st.latex("\\frac{I_2}{D} = \\frac{(μ+γ_3+r)}{p_2}\\frac{r}{μ}")
    st.latex("\\frac{I_1}{D} = \\frac{(p_2+γ_2+r)}{p_1}\\frac{(μ+γ_3+r)}{p_2}\\frac{r}{μ}")
    st.latex("\\frac{Total de sintomáticos}{D} = \\sum{I_i} = \\frac{r}{μ}\\left [1+\\frac{(p_2+γ_2+r)}{p_1}\\right ]")
    st.latex("\\frac{E}{D} = \\frac{(p_1+γ_1+r)}{a}\\frac{(p_2+γ_2+r)}{p_1}\\frac{(μ+γ_3+r)}{p_2}\\frac{r}{μ}")
    st.write("""### Premissas
* Este modelo é formulado como um sistema de equações diferenciais e, portanto, o resultado representa os valores esperados de cada quantidade. Ele não leva em consideração eventos estocásticos ou relata a variação esperada nas variáveis, que podem ser grandes.
* Os indivíduos devem passar por um estágio leve antes de atingir um estágio grave ou crítico
* Os indivíduos devem passar por um estágio grave antes de atingir um estágio crítico
* Somente indivíduos em um estágio crítico morrem
* Todos os indivíduos têm taxas de transmissão e suscetibilidade à infecção iguais

### Atualizações
#### 27 de Março de 2020

* O modelo agora inclui a possibilidade de infecção assintomática. Depois de deixar o $E$ classe, uma fração $f$ indivíduos desenvolvem infecção assintomática (digite $I_0$ classe), enquanto a fração restante $1-f$ desenvolver infecção sintomática (digite $I_1$ classe). A infecção assintomática nunca progride para estágios mais graves. A taxa de recuperação da infecção assintomática é $γ_0$. Indivíduos infectados assintomáticos podem transmitir a outros na taxa $β_0$. Os controles deslizantes originais que controlam as frações de infecções leves versus graves versus críticas agora têm a interpretação como sendo a fração de infecções sintomáticas que entram em cada um desses estágios.
* O modelo agora também inclui a possibilidade de indivíduos expostos que ainda não desenvolveram sintomas ainda poderem transmitir o vírus ("transmissão pré-sintomática"). Para modelar isso, dividimos o $E$ classe em duas classes separadas, $E_0$ (sem sintomas ou transmissão) e $E_1$ (sem sintomas, mas pode transmitir). A taxa de saída de $E_0$ é $a_0$ e de $E_1$ é $a_1$.
* Agora incluímos a opção de sazonalidade nas taxas de transmissão. Todas as taxas de transmissão são modificadas por um fator $σ(t)=1+ϵcos(2π(t-ϕ))$ onde $ϵ∈ [0,1]$ é a amplitude relativa das oscilações sazonais e e $ϕ∈ [-∞, ∞]$ é a fase e determina o tempo (em anos) do pico na transmissão em relação ao tempo em que a simulação começa. Os valores que o usuário insere para as taxas de transmissão são interpretados como as taxas no tempo zero da simulação. Esta entrada será igual ao pico de transmissão se $ϕ=0$, como a transmissão mínima de se $ϕ=365/4∼90$ e como a transmissão no tempo médio se $ϕ=365/2∼180$, por exemplo.

As equações atualizadas do modelo são""")
    st.latex("\\dot{S}=-(β_eE_1+β_0I_0+β_1I_1+β_2I_2+β_3I_3)Sσ(t)")
    st.latex("\\dot{E_0}=-(β_eE_1+β_0I_0+β_1I_1+β_2I_2+β_3I_3)Sσ(t)-a_0E_0")
    st.latex("\\dot{E_1}=a_0E_0-a_1E")
    st.latex("\\dot{I_0}=fa_1E_1-γ_0I_0")
    st.latex("\\dot{I_1}=(1-f)a_1E_1-(γ_1p_1)I_1")
    st.latex("\\dot{I_2}=p_1I_1-(γ_2p_2)I_2")
    st.latex("\\dot{I_3}=p_2I_2-(γ_3μ)I_3")
    st.latex("\\dot{R}=γ_0I_0+γ_1I_1+γ_2I_2+γ_3I_3")
    st.latex("\\dot{D}=μI_3")
    st.write("""As entradas deslizantes extras são

FracAsym: Fração de todas as infecções assintomáticas
PresymPeriod: Duração da fase infecciosa do período de incubação
DurAsym: Duração da infecção assintomática
E a fórmula para extrair as constantes de taxa dessas entradas é""")
    st.code("""a1=1/PresymPeriod
a0=(IncubPeriod-PresymPeriod)^(-1)
f=FracAsym
g0=1/DurAsym""")
    st.write("""A taxa reprodutiva básica torna-se""")
    st.latex("R_0=N\\left [\\frac{β_e}{a_1}+f\\frac{β_0}{γ_0}+(1-f)\\frac{1}{p_1+γ_1}\\left (β_1+\\frac{p_1}{p_2+γ_2}\\left (β_2+β_3\\frac{p_2}{μ+γ_3}\\right )\\right )\\right ]")
    st.write("""### Parâmetros de taxa do modelo dinâmico
Esses parâmetros podem ser alterados usando os controles deslizantes das outras guias. Os valores nesta tabela representam os valores atuais escolhidos pelos controles deslizantes. Observe que as taxas de transmissão escolhidas pelos controles deslizantes são sempre dimensionadas por $N$, de modo que $β * N$ é constante conforme $N$ alterar.""")
    parametros = pd.DataFrame({"variável":['b1*N','b2*N','b3*N','a','g1','g2','g3','p1','p2','u','N'],"valor (/dia)":[0.5,0.1,0.1,0.200,0.133,0.125,0.075,0.033,0.042,0.050,1000.000]})
    st.table(parametros)
    st.write("""### Proporções de casos durante a fase inicial de crescimento
Esses valores são calculados com base nos parâmetros atuais do modelo""")
    fase_inicial = pd.DataFrame({"Razão":['E0:D','E1:D','I0:D','I1:D','I2:D','I3:D','R:D'],"Valor":[239.7,0.0,0.0,157.7,17.3,2.7,170.3]})
    st.table(fase_inicial)
        
if __name__ == "__main__":
    main()
    