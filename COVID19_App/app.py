import streamlit as st
import numpy as np, pandas as pd
from scipy.integrate import odeint
import plotly.express as px

# pic = "https://images.squarespace-cdn.com/content/5ba6af29a0cd27664cbd406b/1559413487296-DE0H6R3P8Y1Q3XZ97JWK/01.jpg?format=100w&content-type=image%2Fjpeg"
# st.image(pic, use_column_width=False, width=100, caption=None)

st.write('Este app é uma adaptação da Cappra Institute for Data Science baseada no modelo criado pelo [Alison Hill](https://github.com/alsnhll/SEIR_COVID19)')

def seir(y,t,b,a,g,p,u,N): 
            dy=[0,0,0,0,0,0]
            S=N-sum(y);
            dy[0]=np.dot(b[1:3],y[1:3])*S-a*y[0] # E
            dy[1]= a*y[0]-(g[1]+p[1])*y[1] #I1
            dy[2]= p[1]*y[1] -(g[2]+p[2])*y[2] #I2
            dy[3]= p[2]*y[2] -(g[3]+u)*y[3] #I3
            dy[4]= np.dot(g[1:3],y[1:3]) #R
            dy[5]=u*y[3] #D

            return dy

def growth_rate(tvec,soln,t1,t2,i):
            i1=np.where(tvec==t1)[0][0]
            i2=np.where(tvec==t2)[0][0]
            r=(np.log(soln[i2,1])-np.log(soln[i1,1]))/(t2-t1)
            DoublingTime=np.log(2)/r

            return r, DoublingTime

IncubPeriod = 0
#b=np.zeros(4) #beta
b=np.array([0,0.33,0,0])
g=np.zeros(4) #gamma
p=np.zeros(3)

def main(IncubPeriod,b,g,p):
    pic = "https://images.squarespace-cdn.com/content/5c4ca9b7cef372b39c3d9aab/1575161958793-CFM6738ESA4DNTKF0SQI/CAPPRA_PRIORITARIO_BRANCO.png?content-type=image%2Fpng"
    st.sidebar.image(pic, use_column_width=False, width=100, caption=None)
    page = st.sidebar.selectbox("Simulações", ["Descição do Modelo","Progressão do COVID19","Com medidas de distanciamento social", 'teste'])
#     page = st.sidebar.selectbox("Simulações", ["Descição do Modelo","Progressão do COVID19"])

    if page == "Descição do Modelo":
        st.header("MODELO")
        st.write("""### Equações

\begin{equation}
\begin{split}
\dot{S} &= -\beta_1 I_1 S -\beta_2 I_2 S - \beta_3 I_3 S\\
\dot{E} &=\beta_1 I_1 S +\beta_2 I_2 S + \beta_3 I_3 S - a E \\
\dot{I_1} &= a E - \gamma_1 I_1 - p_1 I_1 \\
\dot{I_2} &= p_1 I_1 -\gamma_2 I_2 - p_2 I_2 \\
\dot{I_3} & = p_2 I_2 -\gamma_3 I_3 - \mu I_3 \\
\dot{R} & = \gamma_1 I_1 + \gamma_2 I_2 + \gamma_3 I_3 \\
\dot{D} & = \mu I_3
\end{split}
\end{equation}

### Variáveis
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
* $\beta_i$ taxa na qual indivíduos infectados da classe $I_i$ entram em contato com suscetíveis e os infectam
* $a$ taxa de progressão da classe exposta para a infectada
* $\gamma_i$ taxa na qual indivíduos infectados da classe $I_i$ se recuperam da doença e se tornam imunes
* $p_i$ taxa na qual indivíduos infectados da classe $I_i$ avançam para a classe $I_{I + 1}$
* $\mu$ taxa de mortalidade de indivíduos na fase mais grave da doença

### Taxa Básica de reprodução

Ideia: $R_0$ é a soma de: 
1.  o número médio de infecções secundárias geradas de um indivíduo em estágio $I_1$
2.  a probabilidade de um indivíduo infectado progredir para $I_2$ multiplicado pelo número médio de infecções secundárias geradas a partir de um indivíduo em estágio $I_2$
3.  a probabilidade de um indivíduo infectado progredir para $I_3$ multiplicado pelo número médio de infecções secundárias geradas a partir de um indivíduo em estágio$I_3$

\begin{equation}
\begin{split}
R_0 & = N\frac{\beta_1}{p_1+\gamma_1} + \frac{p_1}{p_1 + \gamma_1} \left( \frac{N \beta_2}{p_2+\gamma_2} + \frac{p_2}{p_2 + \gamma_2} \frac{N \beta_3}{\mu+\gamma_3}\right)\\
&= N\frac{\beta_1}{p_1+\gamma_1} \left(1 + \frac{p_1}{p_2 + \gamma_2}\frac{\beta_2}{\beta_1} \left( 1 + \frac{p_2}{\mu + \gamma_3} \frac{\beta_3}{\beta_2} \right) \right)
\end{split}
\end{equation}""")
        #st.write(df)
    elif page == "Progressão do COVID19":        
        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 10
            FracMild1 = 80
            FracSevere1 = 15
            FracCritical1 = 5
            CFR1 = 2
            TimeICUDeath = 7
            DurHosp = 11
            tmax=365
            i=1
        else:
            IncubPeriod = IncubPeriod
            DurMildInf = DurMildInf
            FracMild1 = FracMild1
            FracSevere1 = FracSevere1
            FracCritical1 = FracCritical1
            CFR1 = CFR1
            TimeICUDeath = TimeICUDeath
            DurHosp = DurHosp
            tmax=tmax
            i=i

        st.title("Casos previstos de COVID-19 por resultado clínico")
        st.subheader('Simule o curso natural de uma epidemia de COVID-19 em uma única população sem nenhuma intervenção.')
        
        my_slot1 = st.empty()
        # Appends an empty slot to the app. We'll use this later.

        my_slot2 = st.empty()
        # Appends another empty slot.
        
        my_slot3 = st.empty()
        # Appends another empty slot.
        
        #MENU
        st.sidebar.subheader('Definir parâmetros clínicos ...')
        IncubPeriod = st.sidebar.slider("Período de incubação em dias", min_value=1, max_value=20, value=IncubPeriod, step=1)  #Período de incubação em dias
        DurMildInf = st.sidebar.slider("Duração de infecções leves em dias", min_value=1, max_value=20, value=DurMildInf, step=1) #Duração de infecções leves em dias
        FracMild1 = st.sidebar.slider("Fração de infecções leves", min_value=0, max_value=100, value=FracMild1, step=1)  #Fração de infecções leves
        FracSevere1 = FracMild = st.sidebar.slider("Fração de infecções graves", min_value=0, max_value=100, value=FracSevere1, step=1) #Fração de infecções graves
        FracCritical1 = st.sidebar.slider("Fração de infecções críticas", min_value=0, max_value=100, value=FracCritical1, step=1) #Fração de infecções críticas
        CFR1 = st.sidebar.slider("Taxa de mortalidade de casos (fração de infecções resultando em morte)", min_value=0, max_value=100, value=CFR1, step=1) #Taxa de mortalidade de casos (fração de infecções resultando em morte)
        TimeICUDeath = st.sidebar.slider("Tempo de internação na UTI até a morte em dias", min_value=1, max_value=20, value=TimeICUDeath, step=1) #Tempo de internação na UTI até a morte em dias
        DurHosp = st.sidebar.slider("Duração da internação em dias", min_value=1, max_value=90, value=DurHosp, step=1) #Duração da internação em dias
        
        FracMild = FracMild1/100 #conversão em porcentagem
        FracSevere = FracSevere1/100 #conversão em porcentagem
        FracCritical = FracCritical1/100 #conversão em porcentagem
        CFR = CFR1/100 #conversão em porcentagem
        st.sidebar.subheader('Definir parâmetros de transmissão ...')
        b11 = st.sidebar.slider("Taxa de transmissão (infecções leves)", min_value=0, max_value=100, value=33, step=1) #Taxa de transmissão (infecções leves)
        b21 = st.sidebar.slider("Taxa de transmissão (infecções graves, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções graves, relativa a infecção leve)
        b31 = st.sidebar.slider("Taxa de transmissão (infecções críticas, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        st.sidebar.subheader('Parâmetros da simulação ...')
        N = st.sidebar.number_input(label="Tamanho da população", value=1000) #Tamanho da polulação
        i = st.sidebar.number_input(label="Pessoas infectadas inicialmente", value=1) #Pessoas infectadas inicialmente
        tmax = st.sidebar.slider("Tempo máximo da simulação em dias", min_value=0, max_value=1000, value=365, step=1) #Tempo máximo da simulação
        
        b1 = (b11/100)/N #conversão em porcentagem
        b2 = (b21/100)/N #conversão em porcentagem
        b3 = (b31/100)/N #conversão em porcentagem

        a=1/IncubPeriod

        u=(1/TimeICUDeath)*(CFR/FracCritical)
        g[3]=(1/TimeICUDeath)-u

        p[2]=(1/DurHosp)*(FracCritical/(FracCritical+FracSevere))
        g[2]=(1/DurHosp)-p[2]

        g[1]=(1/DurMildInf)*FracMild
        p[1]=(1/DurMildInf)-g[1]

#         tmax=365
        tvec=np.arange(0,tmax,0.1)
        ic=np.zeros(6)
        ic[0]=i


        
        #b=2e-4*np.ones(4) # todas as etapas transmitem igualmente
#         b=2.5e-4*np.array([0,1,0,0]) # casos hospitalizados não transmitem
        b=np.array([0,b1,b2,b3])
        #b=2.5e-4*b # casos hospitalizados não transmitem

        #Calcula a taxa reprodutiva básica
        R0=N*((b[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1]))*(b[2]/(p[2]+g[2])+(p[2]/(p[2]+g[2]))*(b[3]/(u+g[3]))))

        soln=odeint(seir,ic,tvec,args=(b,a,g,p,u,N))
        soln=np.hstack((N-np.sum(soln,axis=1,keepdims=True),soln))

        data = []
        names = ["S","E","I1","I2","I3","R","D"]
        for x in range(0, len(tvec)):
            for y in range(0, len(soln[x])):
                data.append([tvec[x],names[y],soln[x][y]])

        df = pd.DataFrame(data,columns=['Tempo (dias)','legenda','Número por 1000 Pessoas'])
        yscale = "Linear"
        def covid19_1(yscale):
            if yscale == 'Log':
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda', log_y=True)
            else:
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda')
            return my_slot1.plotly_chart(fig)
        
        yscale = my_slot3.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
        
        (r,DoublingTime)=growth_rate(tvec,soln,10,20,1)
        
        my_slot2.text("R\N{SUBSCRIPT ZERO} = {0:4.1f} \nr = {1:4.1f} por dia \nt\N{SUBSCRIPT TWO} = {2:4.1f}".format(R0,r,DoublingTime))
#         st.write("r = {0:4.1f} por dia".format(r))
#         st.write("t\N{SUBSCRIPT TWO} = {0:4.1f}".format(DoublingTime))
        
        st.write("A taxa de crescimento epidêmico é {0:4.2f} por dia e o tempo de duplicação é de {1:4.1f} dias ".format(r,DoublingTime))
        
        st.write('''**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo. O tamanho da população, a condição inicial e os valores dos parâmetros usados para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). Para redefinir os valores padrão, clique no botão Redefinir tudo, localizado na parte inferior do painel. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.
        
### Variáveis
* $S$: Indivíduos Suscetíveis
* $E$: Indivíduos Expostos - infectados, mas ainda não infecciosos ou sintomáticos
* $I_i$: Indivíduos infectados na classe de gravidade $i$. A gravidade aumenta com $i$ e assumimos que os indivíduos devem passar por todas as classes anteriores
  * $I_1$: Infecção leve (hospitalização não é necessária) - Mild Infection
  * $I_2$: Infecção grave (hospitalização necessária) - Severe infection
  * $I_3$: Infecção crítica (cuidados na UTI necessária) - Critical infection
* $R$: Indivíduos que se recuperaram da doença e agora estão imunes
* $D$: Indivíduos mortos
* $N=S+E+I_1+I_2+I_3+R+D$ Tamanho total da população (constante)''')
        
    elif page == "Progressão do COVID19 com intervenção":
        st.title('Comparação do crescimento da epidemia com e sem intervenção de medidas de distanciamento social')
        st.subheader('Simule a mudança do avanço da epidemia de COVID-19 em uma única população com medidas de distânciamento social (ficando em casa).')
        
        my_slot1 = st.empty()
        # Appends an empty slot to the app. We'll use this later.

        my_slot2 = st.empty()
        # Appends another empty slot.
        
        my_slot3 = st.empty()
        # Appends another empty slot.
        
        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 10
            FracMild1 = 80
            FracSevere1 = 15
            FracCritical1 = 5
            CFR1 = 2
            TimeICUDeath = 7
            DurHosp = 11
            tmax=365
            i=1
        else:
            IncubPeriod = IncubPeriod
            DurMildInf = DurMildInf
            FracMild1 = FracMild1
            FracSevere1 = FracSevere1
            FracCritical1 = FracCritical1
            CFR1 = CFR1
            TimeICUDeath = TimeICUDeath
            DurHosp = DurHosp
            tmax=tmax
            i=i

        
        st.sidebar.subheader('Definir parâmetros clínicos ...')
        IncubPeriod = st.sidebar.slider("Período de incubação em dias", min_value=1, max_value=20, value=IncubPeriod, step=1)  #Período de incubação em dias
        DurMildInf = st.sidebar.slider("Duração de infecções leves em dias", min_value=1, max_value=20, value=DurMildInf, step=1) #Duração de infecções leves em dias
        FracMild1 = st.sidebar.slider("Fração de infecções leves", min_value=0, max_value=100, value=FracMild1, step=1)  #Fração de infecções leves
        FracSevere1 = FracMild = st.sidebar.slider("Fração de infecções graves", min_value=0, max_value=100, value=FracSevere1, step=1) #Fração de infecções graves
        FracCritical1 = st.sidebar.slider("Fração de infecções críticas", min_value=0, max_value=100, value=FracCritical1, step=1) #Fração de infecções críticas
        CFR1 = st.sidebar.slider("Taxa de mortalidade de casos (fração de infecções resultando em morte)", min_value=0, max_value=100, value=CFR1, step=1) #Taxa de mortalidade de casos (fração de infecções resultando em morte)
        TimeICUDeath = st.sidebar.slider("Tempo de internação na UTI até a morte em dias", min_value=1, max_value=20, value=TimeICUDeath, step=1) #Tempo de internação na UTI até a morte em dias
        DurHosp = st.sidebar.slider("Duração da internação em dias", min_value=1, max_value=90, value=DurHosp, step=1) #Duração da internação em dias
        
        FracMild = FracMild1/100 #conversão em porcentagem
        FracSevere = FracSevere1/100 #conversão em porcentagem
        FracCritical = FracCritical1/100 #conversão em porcentagem
        CFR = CFR1/100 #conversão em porcentagem
        st.sidebar.subheader('Definir parâmetros de transmissão ...')
        b11 = st.sidebar.slider("Taxa de transmissão (infecções leves)", min_value=0, max_value=100, value=33, step=1) #Taxa de transmissão (infecções leves)
        b21 = st.sidebar.slider("Taxa de transmissão (infecções graves, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções graves, relativa a infecção leve)
        b31 = st.sidebar.slider("Taxa de transmissão (infecções críticas, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        
        st.sidebar.subheader('Parâmetros da simulação ...')
        N = st.sidebar.number_input(label="Tamanho da população", value=1000) #Tamanho da polulação
        i = st.sidebar.number_input(label="Pessoas infectadas inicialmente", value=1) #Pessoas infectadas inicialmente
        tmax = st.sidebar.slider("Tempo máximo da simulação em dias", min_value=0, max_value=1000, value=365, step=1) #Tempo máximo da simulação
        
#         b1 = (b11/100)/N #conversão em porcentagem
#         b2 = (b21/100)/N #conversão em porcentagem
#         b3 = (b31/100)/N #conversão em porcentagem
        
        a=1/IncubPeriod

        u=(1/TimeICUDeath)*(CFR/FracCritical)
        g[3]=(1/TimeICUDeath)-u

        p[2]=(1/DurHosp)*(FracCritical/(FracCritical+FracSevere))
        g[2]=(1/DurHosp)-p[2]

        g[1]=(1/DurMildInf)*FracMild
        p[1]=(1/DurMildInf)-g[1]

#         tmax=365
        tvec=np.arange(0,tmax,0.1)
        ic=np.zeros(6)
        ic[0]=i
        
        b=np.array([0,b1,b2,b3])
        bSlow=0.6*b
        R0Slow=N*((bSlow[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1]))*(bSlow[2]/(p[2]+g[2])+(p[2]/(p[2]+g[2]))*(bSlow[3]/(u+g[3]))))

        solnSlow=odeint(seir,ic,tvec,args=(bSlow,a,g,p,u,N))
        solnSlow=np.hstack((N-np.sum(solnSlow,axis=1,keepdims=True),solnSlow))

        data1 = []
        names = ["S","E","I1","I2","I3","R","D"]
        for x in range(0, len(tvec)):
            for y in range(0, len(solnSlow[x])):
                data1.append([tvec[x],names[y],solnSlow[x][y]])

        df1 = pd.DataFrame(data1,columns=['Tempo (dias)','legenda','Número por 1000 Pessoas'])

        yscale = "Linear"
        def covid19_1(yscale):
            if yscale == 'Log':
                fig = px.line(df1, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda', log_y=True)
            else:
                fig = px.line(df1, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda')
            return my_slot1.plotly_chart(fig)
        
        
        yscale = my_slot3.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
        
        (r,DoublingTime)=growth_rate(tvec,solnSlow,30,40,i)
        
        my_slot2.text("R\N{SUBSCRIPT ZERO} = {0:4.1f} \nr = {0:4.1f} por dia \nt\N{SUBSCRIPT TWO} = {0:4.1f}".format(R0Slow,r,DoublingTime))
        
        st.write("A taxa de crescimento epidêmico é {0:4.2f} por dia e o tempo de duplicação é de {1:4.1f} dias ".format(r,DoublingTime))
        
        st.write('''**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo, com e sem intervenção. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo. O tamanho da população, a condição inicial e os valores dos parâmetros usados ​​para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). A força e o tempo da intervenção são controlados pelos controles deslizantes abaixo do gráfico. Para redefinir os valores padrão, clique no botão Redefinir tudo, localizado na parte inferior do painel. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.''')
    
    elif page == "Com medidas de distanciamento social":
        st.title('Previsão de redução do COVID-19 após adoção de medidas de distanciamento social')
        st.subheader('Simule a mudança do avanço da epidemia de COVID-19 em uma única população com medidas de distânciamento social (ficando em casa).')
        
        my_slot1 = st.empty()
        # Appends an empty slot to the app. We'll use this later.

        my_slot2 = st.empty()
        # Appends another empty slot.
        
        my_slot3 = st.empty()
        # Appends another empty slot.
        
        my_slot4 = st.empty()
        # Appends another empty slot.
        
        my_slot5 = st.empty()
        # Appends another empty slot.
        
        my_slot6 = st.empty()
        # Appends another empty slot.
        
        my_slot7 = st.empty()
        # Appends another empty slot.
        
        my_slot8 = st.empty()
        # Appends another empty slot.
        
        my_slot9 = st.empty()
        # Appends another empty slot.
        
        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 10
            FracMild1 = 80
            FracSevere1 = 15
            FracCritical1 = 5
            CFR1 = 2
            TimeICUDeath = 7
            DurHosp = 11
            tmax=365
            i=1
            variable = 0
        else:
            IncubPeriod = IncubPeriod
            DurMildInf = DurMildInf
            FracMild1 = FracMild1
            FracSevere1 = FracSevere1
            FracCritical1 = FracCritical1
            CFR1 = CFR1
            TimeICUDeath = TimeICUDeath
            DurHosp = DurHosp
            tmax=tmax
            i=i
            variable = variable

        
        st.sidebar.subheader('Definir parâmetros clínicos ...')
        IncubPeriod = st.sidebar.slider("Período de incubação em dias", min_value=1, max_value=20, value=IncubPeriod, step=1)  #Período de incubação em dias
        DurMildInf = st.sidebar.slider("Duração de infecções leves em dias", min_value=1, max_value=20, value=DurMildInf, step=1) #Duração de infecções leves em dias
        FracMild1 = st.sidebar.slider("Fração de infecções leves", min_value=0, max_value=100, value=FracMild1, step=1)  #Fração de infecções leves
        FracSevere1 = FracMild = st.sidebar.slider("Fração de infecções graves", min_value=0, max_value=100, value=FracSevere1, step=1) #Fração de infecções graves
        FracCritical1 = st.sidebar.slider("Fração de infecções críticas", min_value=0, max_value=100, value=FracCritical1, step=1) #Fração de infecções críticas
        CFR1 = st.sidebar.slider("Taxa de mortalidade de casos (fração de infecções resultando em morte)", min_value=0, max_value=100, value=CFR1, step=1) #Taxa de mortalidade de casos (fração de infecções resultando em morte)
        TimeICUDeath = st.sidebar.slider("Tempo de internação na UTI até a morte em dias", min_value=1, max_value=20, value=TimeICUDeath, step=1) #Tempo de internação na UTI até a morte em dias
        DurHosp = st.sidebar.slider("Duração da internação em dias", min_value=1, max_value=90, value=DurHosp, step=1) #Duração da internação em dias
        
        FracMild = FracMild1/100 #conversão em porcentagem
        FracSevere = FracSevere1/100 #conversão em porcentagem
        FracCritical = FracCritical1/100 #conversão em porcentagem
        CFR = CFR1/100 #conversão em porcentagem
        st.sidebar.subheader('Definir parâmetros de transmissão ...')
#         b11 = st.sidebar.slider("Taxa de transmissão (infecções leves)", min_value=0, max_value=100, value=33, step=1) #Taxa de transmissão (infecções leves)
#         b21 = st.sidebar.slider("Taxa de transmissão (infecções graves, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções graves, relativa a infecção leve)
#         b31 = st.sidebar.slider("Taxa de transmissão (infecções críticas, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        b11 = st.sidebar.slider("Taxa de transmissão (infecções leves)", min_value=0.00, max_value=3.00, value=0.33, step=0.01) #Taxa de transmissão (infecções leves)
        b21 = st.sidebar.slider("Taxa de transmissão (infecções graves, relativa a infecção leve)", min_value=0.00, max_value=2.00, value=0.00, step=0.01) #Taxa de transmissão (infecções graves, relativa a infecção leve)
        b31 = st.sidebar.slider("Taxa de transmissão (infecções críticas, relativa a infecção leve)", min_value=0.00, max_value=2.00, value=0.00, step=0.01) #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        
        st.sidebar.subheader('Parâmetros da simulação ...')
        N = st.sidebar.number_input(label="Tamanho da população", value=1000) #Tamanho da polulação
        i = st.sidebar.number_input(label="Pessoas infectadas inicialmente", value=1) #Pessoas infectadas inicialmente
        tmax = st.sidebar.slider("Tempo máximo da simulação em dias", min_value=0, max_value=1000, value=365, step=1) #Tempo máximo da simulação
        
        reduc11 = my_slot7.slider("Redução na transmissão (infecções leves)", min_value=0, max_value=100, value=30, step=1) #Taxa de transmissão (infecções leves)
        reduc21 = my_slot8.slider("Redução na transmissão (infecções graves, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções graves, relativa a infecção leve)
        reduc31 = my_slot9.slider("Redução na transmissão (infecções críticas, relativa a infecção leve)", min_value=0, max_value=100, value=0, step=1) #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        
        reduc1 = reduc11/100 #conversão em porcentagem
        reduc2 = reduc21/100 #conversão em porcentagem
        reduc3 = reduc31/100 #conversão em porcentagem
        
#         b1 = (b11/100)/N #conversão em porcentagem
#         b2 = (b21/100)/N #conversão em porcentagem
#         b3 = (b31/100)/N #conversão em porcentagem
        b1 = b11/N #conversão em porcentagem
        b2 = b21/N #conversão em porcentagem
        b3 = b31/N #conversão em porcentagem
        
        a=1/IncubPeriod

        u=(1/TimeICUDeath)*(CFR/FracCritical)
        g[3]=(1/TimeICUDeath)-u

        p[2]=(1/DurHosp)*(FracCritical/(FracCritical+FracSevere))
        g[2]=(1/DurHosp)-p[2]

        g[1]=(1/DurMildInf)*FracMild
        p[1]=(1/DurMildInf)-g[1]

#         tmax=365
        tvec=np.arange(0,tmax,0.1)
        ic=np.zeros(6)
        ic[0]=i
        
        b=np.array([0,b1,b2,b3])
        bSlow=np.array([0,(1-reduc1)*b1,(1-reduc2)*b2,(1-reduc3)*b3])
#         bSlow=(1-reduc1)*b
        
        #Calcula a taxa reprodutiva básica
        R0=N*((b[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1]))*(b[2]/(p[2]+g[2])+(p[2]/(p[2]+g[2]))*(b[3]/(u+g[3]))))
        R0Slow=N*((bSlow[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1]))*(bSlow[2]/(p[2]+g[2])+(p[2]/(p[2]+g[2]))*(bSlow[3]/(u+g[3]))))
        
        soln=odeint(seir,ic,tvec,args=(b,a,g,p,u,N))
        soln=np.hstack((N-np.sum(soln,axis=1,keepdims=True),soln))
        solnSlow=odeint(seir,ic,tvec,args=(bSlow,a,g,p,u,N))
        solnSlow=np.hstack((N-np.sum(solnSlow,axis=1,keepdims=True),solnSlow))
        
        data = []
        data1 = []
        names = ["S","E","I1","I2","I3","R","D"]
        for x in range(0, len(tvec)):
            for y in range(0, len(solnSlow[x])):
                data.append([tvec[x],names[y],soln[x][y]])
                data1.append([tvec[x],names[y],solnSlow[x][y]])
        
        variable = my_slot4.selectbox("Selecione a variável que deseja ver", names)
        
        
        df = pd.DataFrame(data,columns=['Tempo (dias)','legenda','Número por 1000 Pessoas'])
        df1 = pd.DataFrame(data1,columns=['Tempo (dias)','legenda','Número por 1000 Pessoas'])
        
        if variable ==0:
            df = df[(df['legenda']=='I1') | (df['legenda']=='I2') | (df['legenda']=='I3')].groupby('Tempo (dias)').sum()
            df.reset_index(inplace=True)

            df1 = df1[(df1['legenda']=='I1') | (df1['legenda']=='I2') | (df1['legenda']=='I3')].groupby('Tempo (dias)').sum()
            df1.reset_index(inplace=True)
        else:
            df = df[(df['legenda']==variable)]
            df1 = df1[(df1['legenda']==variable)]
        
        
        yscale = "Linear"
        def covid19_1(yscale):
            if yscale == 'Log':
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas", log_y=True)
                fig2 = px.line(df1, x="Tempo (dias)", y="Número por 1000 Pessoas", log_y=True)
                fig.add_trace(fig2.data[0])
            else:
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas")
                fig2 = px.line(df1, x="Tempo (dias)", y="Número por 1000 Pessoas")
                fig.add_trace(fig2.data[0])
            return my_slot1.plotly_chart(fig)
        
        
        yscale = my_slot3.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
        
        (r,DoublingTime)=growth_rate(tvec,soln,30,40,i)
        (rSlow,DoublingTimeSlow)=growth_rate(tvec,solnSlow,30,40,i)
        
        Stat = pd.DataFrame({'Linha base':[R0,r,DoublingTime],'Com distanciamento social':[R0Slow,rSlow,DoublingTimeSlow]},columns=['Linha base', 'Com distanciamento social'], index=['R\N{SUBSCRIPT ZERO}','r (por dia)','t\N{SUBSCRIPT TWO}'])
        my_slot2.table(Stat)
        #my_slot2.text("Linha Base \nR\N{SUBSCRIPT ZERO} = {0:4.1f} \nr = {1:4.1f} por dia \nt\N{SUBSCRIPT TWO} = {2:4.1f}".format(R0,r,DoublingTime))
        #my_slot3.text("R\N{SUBSCRIPT ZERO} = {0:4.1f} \nr = {1:4.1f} por dia \nt\N{SUBSCRIPT TWO} = {2:4.1f}".format(R0Slow,rSlow,DoublingTimeSlow))
        
        st.write("A taxa de crescimento epidêmico é {0:4.2f} por dia e o tempo de duplicação é de {1:4.1f} dias ".format(r,DoublingTime))
        
        my_slot6.text('''Tipo de intervenção: redução da transmissão, por exemplo, através de distanciamento social ou quarentena na comunidade (para aqueles com infecção leve) ou melhor isolamento e desgaste de proteção pessoal em hospitais (para aqueles com infecção mais grave). A transmissão de cada um dos estágios clínicos da infecção só pode ser reduzida se o usuário tiver escolhido parâmetros para que esses estágios contribuam para a transmissão.''')
        
        st.write('''**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo, com e sem intervenção. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo. O tamanho da população, a condição inicial e os valores dos parâmetros usados ​​para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). A força e o tempo da intervenção são controlados pelos controles deslizantes abaixo do gráfico. Para redefinir os valores padrão, clique no botão Redefinir tudo, localizado na parte inferior do painel. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.''')


        
    elif page == "teste":
        st.text('This will appear first')
        # Appends some text to the app.

        my_slot1 = st.empty()
        # Appends an empty slot to the app. We'll use this later.

        my_slot2 = st.empty()
        # Appends another empty slot.

        st.text('This will appear last')
        # Appends some more text to the app.

        my_slot1.text('This will appear second')
        # Replaces the first empty slot with a text string.

        my_slot2.line_chart(np.random.randn(20, 2))
        # Replaces the second empty slot with a chart.


if __name__ == "__main__":
    main(IncubPeriod,b,g,p)
    
