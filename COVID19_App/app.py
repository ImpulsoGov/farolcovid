import streamlit as st
import numpy as np, pandas as pd
from scipy.integrate import odeint
import plotly.express as px

# pic = "https://images.squarespace-cdn.com/content/5ba6af29a0cd27664cbd406b/1559413487296-DE0H6R3P8Y1Q3XZ97JWK/01.jpg?format=100w&content-type=image%2Fjpeg"
# st.image(pic, use_column_width=False, width=100, caption=None)

st.write('Este app é uma adaptação da Cappra Institute for Data Science baseada no modelo criado pelo [Alison Hill](https://github.com/alsnhll/SEIR_COVID19)')

def param(IncubPeriod,DurMildInf, FracMild1, FracSevere1, FracCritical1, CFR1, TimeICUDeath, DurHosp):
    st.sidebar.subheader('Definir parâmetros clínicos ...')
    IncubPeriod = st.sidebar.slider("Período de incubação em dias", min_value=1, max_value=20, value=IncubPeriod, step=1)  #Período de incubação em dias
    DurMildInf = st.sidebar.slider("Duração de infecções leves em dias", min_value=1, max_value=20, value=DurMildInf, step=1) #Duração de infecções leves em dias
    FracMild1 = st.sidebar.slider("Fração de infecções leves", min_value=0, max_value=100, value=FracMild1, step=1)  #Fração de infecções leves
    FracSevere1 = FracMild = st.sidebar.slider("Fração de infecções graves", min_value=0, max_value=100, value=FracSevere1, step=1) #Fração de infecções graves
    FracCritical1 = st.sidebar.slider("Fração de infecções críticas", min_value=0, max_value=100, value=FracCritical1, step=1) #Fração de infecções críticas
    CFR1 = st.sidebar.slider("Taxa de mortalidade de casos (fração de infecções resultando em morte)", min_value=0, max_value=100, value=CFR1, step=1) #Taxa de mortalidade de casos (fração de infecções resultando em morte)
    TimeICUDeath = st.sidebar.slider("Tempo de internação na UTI até a morte em dias", min_value=1, max_value=90, value=TimeICUDeath, step=1) #Tempo de internação na UTI até a morte em dias
    DurHosp = st.sidebar.slider("Duração da internação em dias", min_value=1, max_value=90, value=DurHosp, step=1) #Duração da internação em dias
        
    st.sidebar.subheader('Definir parâmetros de transmissão ...')
    return 'ok'

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

def main():
    pic = "https://images.squarespace-cdn.com/content/5c4ca9b7cef372b39c3d9aab/1575161958793-CFM6738ESA4DNTKF0SQI/CAPPRA_PRIORITARIO_BRANCO.png?content-type=image%2Fpng"
    st.sidebar.image(pic, use_column_width=False, width=100, caption=None)
#     page = st.sidebar.selectbox("Simulações", ["Descição do Modelo","Progressão do COVID19","Com medidas de distanciamento social"])
    page = st.sidebar.selectbox("Simulações", ["Descição do Modelo","Progressão do COVID19"])
    IncubPeriod = 5
    DurMildInf = 10
    FracMild1 = 80
    FracSevere1 = 15
    FracCritical1 = 5
    CFR1 = 2
    TimeICUDeath = 7
    DurHosp = 11
    FracMild = FracMild1/100 #conversão em porcentagem
    FracSevere = FracSevere1/100 #conversão em porcentagem
    FracCritical = FracCritical1/100 #conversão em porcentagem
    CFR = CFR1/100 #conversão em porcentagem
    
    N=1000
    b=np.zeros(4) #beta
    g=np.zeros(4) #gamma
    p=np.zeros(3)

    a=1/IncubPeriod

    u=(1/TimeICUDeath)*(CFR/FracCritical)
    g[3]=(1/TimeICUDeath)-u

    p[2]=(1/DurHosp)*(FracCritical/(FracCritical+FracSevere))
    g[2]=(1/DurHosp)-p[2]

    g[1]=(1/DurMildInf)*FracMild
    p[1]=(1/DurMildInf)-g[1]
    
    tmax=365
    tvec=np.arange(0,tmax,0.1)
    ic=np.zeros(6)
    ic[0]=1

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
        st.title("Casos previstos de COVID-19 por resultado clínico")
        st.subheader('Simule o curso natural de uma epidemia de COVID-19 em uma única população sem nenhuma intervenção.')
        menu = param(IncubPeriod,DurMildInf, FracMild1, FracSevere1, FracCritical1, CFR1, TimeICUDeath, DurHosp)

        #b=2e-4*np.ones(4) # todas as etapas transmitem igualmente
        b=2.5e-4*np.array([0,1,0,0]) # casos hospitalizados não transmitem

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
            return st.plotly_chart(fig)
        
        
        yscale = st.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
        
        (r,DoublingTime)=growth_rate(tvec,soln,10,20,1)
        
        st.write("R\N{SUBSCRIPT ZERO} = {0:4.1f}".format(R0))
        st.write("r = {0:4.1f} por dia".format(r))
        st.write("t\N{SUBSCRIPT TWO} = {0:4.1f}".format(DoublingTime))
        
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
        
    elif page == "Com medidas de distanciamento social":
        st.title('Repetindo, mas com medidas de distanciamento social que reduz a taxa de transmissão')
        st.subheader('Simule a mudança do avanço da epidemia de COVID-19 em uma única população com medidas de distânciamento social (ficando em casa).')
        menu = param(IncubPeriod,DurMildInf, FracMild1, FracSevere1, FracCritical1, CFR1, TimeICUDeath, DurHosp)

        bSlow=0.6*b
        R0Slow=N*((bSlow[1]/(p[1]+g[1]))+(p[1]/(p[1]+g[1]))*(bSlow[2]/(p[2]+g[2])+(p[2]/(p[2]+g[2]))*(bSlow[3]/(u+g[3]))))

        solnSlow=odeint(seir,ic,tvec,args=(bSlow,a,g,p,u,N))
        solnSlow=np.hstack((N-np.sum(solnSlow,axis=1,keepdims=True),solnSlow))

        data1 = []
        names = ["Sucetíveis","Expostos","Infecção Leve","Infecção grave","Infecção crítica","R","D"]
        for x in range(0, len(tvec)):
            for y in range(0, len(solnSlow[x])):
                data1.append([tvec[x],names[y],solnSlow[x][y]])

        df = pd.DataFrame(data1,columns=['Tempo (dias)','legenda','Número por 1000 Pessoas'])
        yscale = "Linear"
        def covid19_1(yscale):
            if yscale == 'Log':
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda', log_y=True)
            else:
                fig = px.line(df, x="Tempo (dias)", y="Número por 1000 Pessoas", color='legenda')
            return st.plotly_chart(fig)
        
        
        yscale = st.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
        
        (r,DoublingTime)=growth_rate(tvec,solnSlow,30,40,1)
        
        st.write("R\N{SUBSCRIPT ZERO} = {0:4.1f}".format(R0Slow))
        st.write("r = {0:4.1f} por dia".format(r))
        st.write("t\N{SUBSCRIPT TWO} = {0:4.1f}".format(DoublingTime))
        
        st.write("A taxa de crescimento epidêmico é {0:4.2f} por dia e o tempo de duplicação é de {1:4.1f} dias ".format(r,DoublingTime))
        
        st.write('''**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo, com e sem intervenção. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo. O tamanho da população, a condição inicial e os valores dos parâmetros usados ​​para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). A força e o tempo da intervenção são controlados pelos controles deslizantes abaixo do gráfico. Para redefinir os valores padrão, clique no botão Redefinir tudo, localizado na parte inferior do painel. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.''')


if __name__ == "__main__":
    main()
    
