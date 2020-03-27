import streamlit as st
import numpy as np, pandas as pd
from scipy.integrate import odeint
from numpy import linalg as LA
import plotly.express as px
from streamlit import caching
import model as md
import fontes as ft

st.write('Este app é uma adaptação da Cappra Institute for Data Science baseada no modelo criado pela [Alison Hill](https://alhill.shinyapps.io/COVID19seir/)')

IncubPeriod = 0

#Taxa reprodutiva padrão
def taxa_reprodutiva(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f):
    
    return N*((be/a1)+f*(b0/g0)+(1-f)*((b1/(p1+g1))+(p1/(p1+g1))*(b2/(p2+g2)+ (p2/(p2+g2))*(b3/(u+g3)))))

#Taxa reprodutiva com sazonalidade
def taxa_reprodutiva_seas(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f, SeasAmp, SeasPhase):

    Ro_now = N*((b1/(p1+g1))+(p1/(p1+g1))*(b2/(p2+g2)+ (p2/(p2+g2))*(b3/(u+g3))))*(1 + SeasAmp*np.cos(2*np.pi*(0-SeasPhase)/365))
    Ro_max = N*((b1/(p1+g1))+(p1/(p1+g1))*(b2/(p2+g2)+ (p2/(p2+g2))*(b3/(u+g3))))*(1 + SeasAmp)
    Ro_min = N*((b1/(p1+g1))+(p1/(p1+g1))*(b2/(p2+g2)+ (p2/(p2+g2))*(b3/(u+g3))))*(1 - SeasAmp)
    
    return Ro_now, Ro_max, Ro_min

#Cálculo dos parâmetros do modelo SEIR            
def params(IncubPeriod, FracMild, FracCritical, FracSevere, TimeICUDeath, CFR, DurMildInf, DurHosp, i, PresymPeriod, FracAsym, DurAsym, N):
        
        if PresymPeriod > 0:
            a1 = min(10^6,1/PresymPeriod) #Frequênca de surgimento do vírus
        else:
            a1 = 10^6
         
        if IncubPeriod > PresymPeriod:
            a0 = min(10^6, 1/(IncubPeriod - PresymPeriod)) #Frequência de incubação até possibilidade de transmissão
        else:
            a0 = 10^6
        f = FracAsym #Fração de assintomáticos
        
        g0 = 1/DurAsym #Taxa de recuperação dos assintomáticos
        
        if FracCritical==0:
            u=0
        else:
            u=(1/TimeICUDeath)*(CFR/FracCritical)
            
        g1 = (1/DurMildInf)*FracMild #Taxa de recuperação I1
        p1 =(1/DurMildInf) - g1 #Taxa de progreção I1

        g3 =(1/TimeICUDeath)-u #Taxa de recuperação I3
        
        p2 =(1/DurHosp)*(FracCritical/(FracCritical+FracSevere)) #Taxa de progressão I2
        g2 = (1/DurHosp) - p2 #Taxa de recuperação de I2

        ic=np.zeros(9) #Inicia vetor da população (cada índice para cada tipo de infectado, exposto, etc)
        ic[0]= N-i #População
        ic[1] = i #População exposta
        
        return a0, a1, u, g0, g1, g2, g3, p1, p2, f, ic
#Menu dos parâmetros gerais
def menu(IncubPeriod, DurMildInf, FracSevere, FracCritical, ProbDeath, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod): #Cria o menu lateral esquerdo

        st.sidebar.subheader('Parâmetros clínicos:')
        
        FracSevere1 = int(FracSevere*100)
        FracCritical1 = int(FracCritical*100)
        ProbDeath1 = int(ProbDeath*100)
        
        #Período de incubação em dias
        IncubPeriod = st.sidebar.slider("Período de incubação (em dias)", min_value=0, max_value=20, value=IncubPeriod, step=1)  
        
        #Duração de infecções leves em dias
        DurMildInf = st.sidebar.slider("Duração de infecções leves (em dias)", min_value=1, max_value=20, value=DurMildInf, step=1) 
        
        #Fração de infecções graves
        FracSevere = st.sidebar.slider("% de infecções graves", min_value=0, max_value=100, value=FracSevere1, step=1)/100 
        
        #Duração da internação em dias
        DurHosp = st.sidebar.slider("Duração da infecção grave (permanência em leito hospitalar em dias)", min_value=1, max_value=30, value=DurHosp, step=1) 
        
        #Fração de infecções críticas
        FracCritical = st.sidebar.slider("% de infecções críticas", min_value=0, max_value=100, value=FracCritical1, step=1)/100
        
        #Duração da infecção crítica / permanência na UTI em dias
        TimeICUDeath = st.sidebar.slider("Duração da infecção crítica (permanência na UTI em dias", min_value=1, max_value=30, value=TimeICUDeath, step=1) 
        
        #Fração de infecções leves
        FracMild = 1 - FracSevere - FracCritical
        st.sidebar.text("% de infecções leves = "+str(round(FracMild*100,1))+"%")
        
        #Taxa de mortalidade de casos (fração de infecções resultando em morte)
        ProbDeath = st.sidebar.slider("Taxa de mortalidade em casos críticos", min_value=0, max_value=100, value=ProbDeath1, step=1)/100
        
        CFR = ProbDeath*FracCritical
        st.sidebar.text("Taxa de mortalidade geral = "+str(round(CFR*100,1))+"%")
        
        st.sidebar.subheader('Taxas de transmissão:')
        
        #Taxa de transmissão (infecções leves)
        b1 = st.sidebar.slider("Taxa de transmissão de infecções leves por dia", min_value=0.00, max_value=3.00, value=0.5, step=0.01) 
        
        #Taxa de transmissão (infecções graves, relativa a infecção leve)
        b2 = st.sidebar.slider("Taxa de transmissão de infecções graves por dia", min_value=0.00, max_value=3.00, value=0.1, step=0.01) 
        
        #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        b3 = st.sidebar.slider("Taxa de transmissão de infecções críticas por dia", min_value=0.00, max_value=3.00, value=0.1, step=0.01) 
        
        st.sidebar.subheader('Parâmetros de infecções assintomáticas:')
        #Permitir infecções assintomáticas
        AllowAsym = st.sidebar.radio("Permitir infecções assintomáticas?", ["Não","Sim"])
        if AllowAsym=="Sim":
            #Fração de assintomáticos
            FracAsym = 0.3
            FracAsym=st.sidebar.slider("Fração de infecções assintomáticas", min_value=0, max_value=100, value=int(FracAsym*100), step=1)/100
            #Duração dos assintomáticos
            DurAsym=st.sidebar.slider("Duração de infecções assintomáticas", min_value=1, max_value=20, value=DurAsym, step=1)
            #Taxa de tranmissão
            b0 = st.sidebar.slider("Taxa de transmissão de infecções assintomáticas por dia", min_value=0.00, max_value=3.00, value=0.1, step=0.01) 
        else:
            FracAsym=0
            DurAsym=7
            b0 = 0 
        
        st.sidebar.subheader('Parâmetros de transmissões pré-sintomáticas:')
        #Permitir transmissões pré-sintomática
        AllowPresym = st.sidebar.radio("Permitir transmissões pré-sintomáticas?", ["Não","Sim"])

        if AllowPresym=="Sim":
            #Periodo de transmissão
            if IncubPeriod > 2:
                PresymPeriod=st.sidebar.slider("Tempo antes do início dos sintomas no qual a transmissão é possível", min_value=0, max_value=IncubPeriod, value=PresymPeriod, step=1)
            elif IncubPeriod == 0:
                st.sidebar.text("Periodo de incubação é zero, logo todos os expostos transmitem")
                PresymPeriod = 0
            else:
                PresymPeriod=st.sidebar.slider("Tempo antes do início dos sintomas no qual a transmissão é possível", min_value=0, max_value=IncubPeriod, value=IncubPeriod - 1, step=1)
            #Taxa de transmissão
            be = st.sidebar.slider("Taxa de transmissão pré-sintomática por dia", min_value=0.0, max_value=3.00, value=0.5, step=0.01)
        else:
            PresymPeriod=0
            be = 0
            
        st.sidebar.subheader('Parâmetros de sazonalidade:')
        #Permitir ou não a sazonalidade
        AllowSeason = st.sidebar.radio("Permitir Sazonalidade?", ["Não","Sim"])
        if AllowSeason=="Sim":
            #Amplitude da sazonlidade
            SeasAmp = st.sidebar.slider("Amplitude da sazonalidade", min_value=0, max_value=100, value=SeasAmp, step=1)/100 
            #Fase da sazonalidade
            SeasPhase = st.sidebar.slider("Amplitude da sazonalidade", min_value=-365, max_value=365, value=SeasPhase, step=1) 
        else:
            SeasAmp=0.0 
            SeasPhase=0 
        seas0=(1 + SeasAmp*np.cos(2*np.pi*SeasPhase/365)) #value of seasonality coefficient at time zero

        st.sidebar.subheader('Parâmetros da simulação:')
        #Tamanho da polulação
        N = st.sidebar.number_input(label="Tamanho da população", value=1000) 
        
        #Pessoas infectadas inicialmente
        i = st.sidebar.number_input(label="Pessoas infectadas inicialmente", value=1) 
        
        #Tempo máximo da simulação
        tmax = st.sidebar.slider("Tempo máximo da simulação em dias", min_value=0, max_value=1000, value=365, step=1)
        
        #Taxas de trnamissão percapita
        b1 = b1/(N*seas0)
        b2 = b2/(N*seas0)
        b3 = b3/(N*seas0)
        b0 = b0/(N*seas0)
        be = be/(N*seas0)
        
        return IncubPeriod, DurMildInf, FracMild, FracSevere, FracCritical, CFR, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod, seas0, b0, b1, b2, b3, be, N, i, tmax

#Menu dos parâmetros de intervenção
def intervencao(TimeStart,TimeEnd,reduc1,reduc2,reduc3,reducpre,reducasym,tmax):
        st.sidebar.subheader('Parâmetros de intervenção')
        #Início da intervenção
        TimeStart = st.sidebar.slider(label="Tempo de início da intervenção (dias)",min_value = 0, max_value = tmax, value = TimeStart, step = 1) 
        #Fim da intervenção
        TimeEnd = st.sidebar.slider(label="Tempo de fim da intervenção (dias)", min_value = 0, max_value = tmax, value = TimeEnd, step = 1) 
        #Taxa de transmissão (infecções leves)
        reduc1 = st.sidebar.slider("Redução na transmissão causada por infecções leves (%)", min_value=0, max_value=100, value=int(reduc1*100), step=1)/100   
        #Taxa de transmissão (infecções graves, relativa a infecção leve)
        reduc2 = st.sidebar.slider("Redução na transmissão causada por infecções graves (%)", min_value=0, max_value=100, value=int(reduc2*100), step=1)/100 
        #Taxa de transmissão (infecções críticas, relativa a infecção leve)
        reduc3 = st.sidebar.slider("Redução na transmissão causada por infecções críticas (%)", min_value=0, max_value=100, value=int(reduc3*100), step=1)/100
        #Redução da transmissão de assintomáticos
        reducasym = st.sidebar.slider("Redução na transmissão causada por infecções assintomáticas (%), se estiverem permitidas", min_value=0, max_value=100, value=int(reducasym*100), step = 1)/100
        #Redução da transmissão de pré-sintomáticos
        reducpre = st.sidebar.slider("Redução na transmissão causada por infecções pré sintomáticas (%), se estiverem permitidas", min_value=0, max_value=100, value=int(reducpre*100), step = 1)/100
        return TimeStart,TimeEnd,reduc1,reduc2,reduc3,reducpre, reducasym
    
#Simulação com intevenção
def simulacao(TimeStart, TimeEnd, tmax, i, N, a0, a1, b0, be, b1, b2, b3, b0Int, beInt, b1Int, b2Int, b3Int, g0, g1, g2, g3, p1, p2 , u, names, f, AllowAsym, AllowPresym, SeasAmp, SeasPhase):

    if TimeEnd>TimeStart: #Se há intervenção
            if TimeStart > 0: #Se a intervenção começa após o dia 0
                #Simulação sem intervenção (antes do início da intervenção)
                ic = np.zeros(9) #Inicia vetor da população (cada índice para cada tipo de infectado, exposto, etc)
                ic[0] = N-i #População sucetível = tamanho da população
                ic[1] = i #População exposta
                tvec = np.arange(0,TimeStart,0.1) #A simulação sem intervenção termina em t = TimeStart
                sim_sem_int_1 = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
                ic = sim_sem_int_1[-1] #Salva a população atual
                
                #Criando DataFrame
                df_sim_com_int = pd.DataFrame(sim_sem_int_1, columns = names)
                df_sim_com_int['Tempo (dias)'] = tvec
                df_sim_com_int['Simulação'] = 'Com intervenção'
            
                #Simulação após o início da intervenção
                tvec=np.arange(TimeStart,TimeEnd,0.1)
                sim_com_int = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,beInt,b0Int,b1Int,b2Int,b3Int,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
                ic = sim_com_int[-1] #Salva população atual
                #Criando DataFrame
                df_aux = pd.DataFrame(sim_com_int, columns = names)
                df_aux['Tempo (dias)'] = tvec
                df_aux['Simulação'] = 'Com intervenção'
                #Append dataframe
                df_sim_com_int = df_sim_com_int.append(df_aux)
                
                if TimeEnd < tmax: #Se a intervenção termina antes do tempo final
                    tvec = np.arange(TimeEnd,tmax,0.1) #A simulação sem intervenção termina em t = TimeStart
                    #Simulação sem intervenção (após o fim da intervenção)
                    sim_sem_int_2 = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
                    #Criando dataframe
                    df_aux = pd.DataFrame(sim_sem_int_2, columns = names)
                    df_aux['Tempo (dias)'] = tvec
                    df_aux['Simulação'] = 'Com intervenção'
                    #Append dataframe
                    df_sim_com_int = df_sim_com_int.append(df_aux)
                    
                    
            elif TimeStart == 0: #Se a intervenção começa no dia 0
                ic = np.zeros(9) #Inicia vetor da população (cada índice para cada tipo de infectado, exposto, etc)
                ic[0] = N - i #População sucetível = tamanho da população
                ic[1] = i
                tvec=np.arange(0,TimeEnd,0.1)
                sim_com_int = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,beInt,b0Int,b1Int,b2Int,b3Int,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
                ic = sim_com_int[-1]
                df_sim_com_int = pd.DataFrame(sim_com_int, columns = names)
                df_sim_com_int['Tempo (dias)'] = tvec
                df_sim_com_int['Simulação'] = 'Com intervenção'
                #sim = sim_com_int
                if TimeEnd < tmax: #Se a intervenção termina antes do tempo final
                    tvec = np.arange(TimeEnd,tmax,0.1) #A simulação sem intervenção termina em t = TimeStart
                    #Simulação sem intervenção (após o fim da intervenção)
                    sim_sem_int_2 = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
                   #Criando dataframe
                    df_aux = pd.DataFrame(sim_sem_int_2, columns = names)
                    df_aux['Tempo (dias)'] = tvec
                    df_aux['Simulação'] = 'Com intervenção'
                    df_sim_com_int = df_sim_com_int.append(df_aux)       
            return df_sim_com_int
    

#Modelo SEIR
def seir(y,t,a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase): 
        
    dy=[0, #Sucetiveis y[0]
        0, #Expostos y[1]
        0, #Expostos transmissores y[2]
        0, #I0 - Assintomáticos y[3]
        0, #I1 - Leves y[4]
        0, #I2 - Graves y[5]
        0, #I3 - Críticos y[6]
        0, #Recuperados y[7]
        0] #Mortos y[8]
    
    S = y[0] #Sucetiveis y[0]
    E0 = y[1] #Expostos y[1]
    E1 = y[2] #Expostos transmissores y[2]
    I0 = y[3] #I0 - Assintomáticos y[3]
    I1 = y[4] #I1 - Leves y[4]
    I2 = y[5] #I2 - Graves y[5]
    I3 = y[6] #I3 - Críticos y[6]
    R = y[7] #Recuperados y[7]
    D = y[8] #Mortos y[8]
    
    seas=(1 + SeasAmp*np.cos(2*np.pi*(t-SeasPhase)/365))
    
    dy[0] = -(be*E1 + b0*I0 + b1*I1 +b2*I2 + b3*I3)*S*seas #Variação de sucetíveis
    
    dy[1] = (be*E1 + b0*I0 + b1*I1 + b2*I2 + b3*I3)*S*seas - a0*E0 #Variação de expostos não transmissores
    
    if AllowPresym == 'Sim': #Se os pré-sintomáticos transmitem   
        dy[2] = a0*E0 - a1*E1 #Variação de pré-sintomáticos transmissores
        if AllowAsym == 'Sim': #Se há assintomáticos
            dy[3] = f*a1*E1 - g0*I0 #Variação de assintomáticos
            dy[4] = (1-f)*a1*E1 - g1*I1 - p1*I1 #Variação de casos leves
        else: #Se não há assintomáticos
            dy[3] = 0 #Variação de assintomáticos é zero
            dy[4] = (1-f)*a1*E1 - g1*I1 - p1*I1 #Variação de casos leves
    else: #Se os pré-sintomáticos não transmitem
        dy[2] = 0 #Variação de pré-sintomáticos transmissores é zero
        if AllowAsym == 'Sim': #Se há assintomáticos
            dy[3] = f*a0*E0 - g0*I0 #Variação de assintomáticos
            dy[4] = (1-f)*a0*E0 - g1*I1 - p1*I1 #Variação de casos leves
        else:#Se não há
            dy[3] = 0 #Variação de assintomáticos é zero
            dy[4] = (1-f)*a0*E0 - g1*I1 - p1*I1 #Variação de casos leves
 
    dy[5] = p1*I1-g2*I2-p2*I2 #Variação de casos graves
    
    dy[6] = p2*I2-g3*I3-u*I3 #Variação de casos críticos
    
    dy[7] = g0*I0+g1*I1+g2*I2+g3*I3 #Variação de recuperados
    
    dy[8] = u*I3 #Variação de mortos
    
    return dy

def new_growth_rate(g0,g1,g2,g3,p1,p2,be,b0,b1,b2,b3,u,a0,a1,N,f): #Growth rate após o update
    
    JacobianMat=np.array([
                 [-a0, N*be, N*b0, N*b1, N*b2, N*b3, 0, 0],
                 [a0, -a1, 0, 0, 0, 0, 0, 0],
                 [0, a1*f, -g0, 0, 0, 0, 0, 0],
                 [0, a1 - a1*f, 0, -p1-g1, 0, 0, 0, 0],
                 [0, 0, 0, p1, -p2-g2, 0, 0, 0],
                 [0, 0, 0, 0, p2, -u-g3, 0, 0],
                 [0, 0, g0, g1, g2, g3 , 0, 0],
                 [0, 0, 0, 0, 0, u, 0, 0]
                ])
    
    eig = LA.eig(JacobianMat)
    eigvalue = eig[0].real
    eigvector = eig[1]
    
    r = max(eigvalue)
    
    MaxEigenVector=eigvector.T[np.argmax(eigvalue)]
    MaxEigenVector=MaxEigenVector/MaxEigenVector[len(MaxEigenVector)-1]
    MaxEigenVector=MaxEigenVector.real
    DoublingTime=np.log(2)/r
    
    return r, DoublingTime


def main(IncubPeriod):
    pic = "https://images.squarespace-cdn.com/content/5c4ca9b7cef372b39c3d9aab/1575161958793-CFM6738ESA4DNTKF0SQI/CAPPRA_PRIORITARIO_BRANCO.png?content-type=image%2Fpng"
    st.sidebar.image(pic, use_column_width=False, width=100, caption=None)
    page = st.sidebar.selectbox("Simulações", ["Progressão do COVID19","Com Intervenção","Capacidade Hospitalar","Descição do Modelo","Fontes","Código","Tutorial"])

    if page == "Descição do Modelo":
        if __name__ == "__main__":
            md.main()
        
    elif page == "Progressão do COVID19":        
        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 6
            FracSevere = 0.15
            FracCritical = 0.05
            FracMild = 1 - FracSevere - FracCritical
            ProbDeath = 0.4
            TimeICUDeath = 10
            DurHosp = 4
            tmax = 365
            i = 1
            TimeStart = 0
            TimeEnd = tmax
            AllowSeason = 'Não'
            SeasAmp = 0
            SeasPhase = 0
            AllowAsym = 'Não'
            FracAsym = 0
            DurAsym = 6
            AllowPresym = 'Não'
            PresymPeriod = 2
            
        st.title("Casos previstos de COVID-19 por resultado clínico")
        st.subheader('Simule o curso natural de uma epidemia de COVID-19 em uma única população sem nenhuma intervenção.')
        
        my_slot1 = st.empty()
        my_slot2 = st.empty()        
        my_slot3 = st.empty()
        
        #Menu
        IncubPeriod, DurMildInf, FracMild, FracSevere, FracCritical, CFR, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod, seas0, b0, b1, b2, b3, be, N, i, tmax = menu(IncubPeriod, DurMildInf, FracSevere, FracCritical, ProbDeath, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod)    

        #Parâmetros do SEIR
        a0, a1, u, g0, g1, g2, g3, p1, p2, f, ic = params(IncubPeriod, FracMild, FracCritical, FracSevere, TimeICUDeath, CFR, DurMildInf, DurHosp, i, PresymPeriod, FracAsym, DurAsym, N)
        
        #Taxa reprodutiva e valores de crescimento
        if AllowSeason:
            R0 = taxa_reprodutiva_seas(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f, SeasAmp, SeasPhase)[0]
        else:
            R0 = taxa_reprodutiva(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f)
            
        (r,DoublingTime) = new_growth_rate(g0,g1,g2,g3,p1,p2,be,b0,b1,b2,b3,u,a0,a1,N,f)
        
        my_slot2.text("R\N{SUBSCRIPT ZERO} = {0:4.1f} \nr = {1:4.1f} por dia \nt\N{SUBSCRIPT TWO} = {2:4.1f}".format(R0,r,DoublingTime))

        #Simulação
        tvec=np.arange(0,tmax,0.1)
        soln=odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))

        #Criação do dataframe
        data = []
        names = ["Sucetíveis (S)","Expostos (E0)","Pré-sintomáticos (E1)","Assintomáticos (I0)","Inf. Leve (I1)","Inf. Grave (I2)","Inf. Crítico (I3)","Recuperado (R)","Morto (D)"]
        for x in range(0, len(tvec)):
            for y in range(0, len(soln[x])):
                data.append([tvec[x],names[y],soln[x][y]])
        y_index = 'Número por ' + str(N) +' pessoas'
        df = pd.DataFrame(data,columns=['Tempo (dias)','legenda',y_index])
        
        if AllowAsym == 'Não':
            df = df[df['legenda'] != "Assintomáticos (I0)"]
        if AllowPresym == 'Não':
            df = df[df['legenda'] != "Pré-sintomáticos (E1)"]
        
        yscale = "Linear"
        def covid19_1(yscale):
            if yscale == 'Log':
                fig = px.line(df, x="Tempo (dias)", y=y_index, color='legenda', log_y=True)
            else:
                fig = px.line(df, x="Tempo (dias)", y=y_index, color='legenda')
            return my_slot1.plotly_chart(fig)
        
        yscale = my_slot3.radio("Escala do eixo Y", ["Linear", "Log"])
        covid19_1(yscale)
                        
        st.write('''**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo. O tamanho da população, a condição inicial e os valores dos parâmetros usados para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). Para redefinir os valores padrão, clique no botão Redefinir tudo, localizado na parte inferior do painel. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.
        
### Variáveis
* $S$: Indivíduos Suscetíveis
* $E_0$: Indivíduos Expostos - infectados, em estágio pré-sintomático mas não transmite o vírus
* $E_1$: Indivíduos Expostos - infectados, em estágio pré-sintomático mas transmite o vírus
* $I_i$: Indivíduos infectados na classe de gravidade $i$. A gravidade aumenta com $i$ e assumimos que os indivíduos devem passar por todas as classes anteriores
  * $I_0$: Infecção assintomática (hospitalização não é necessária)
  * $I_1$: Infecção leve (hospitalização não é necessária)
  * $I_2$: Infecção grave (hospitalização necessária)
  * $I_3$: Infecção crítica (cuidados na UTI necessária)
* $R$: Indivíduos que se recuperaram da doença e agora estão imunes
* $D$: Indivíduos mortos
* $N = S + E_0 + E_1 + I+0 + I_1 + I_2 + I_3 + R + D$ Tamanho total da população (constante)

Os indivíduos $E_1$ e $I_0$ estão desativados na simulação, mas podem ser ativados no painel lateral esquerdo.''')
        
    elif page == "Com Intervenção":
        st.title('Previsão de redução do COVID-19 após adoção de medidas de intervenção como distanciamento social')
        st.subheader('Simule a mudança do avanço da epidemia de COVID-19 em uma única população com medidas de redução de transmissão (distanciamento social, quarentena, etc).')
        st.write('Os parâmetros de redução de transmissão podem ser modificados no painel lateral esquerdo.')
        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 6
            FracSevere = 0.15
            FracCritical = 0.05
            FracMild = 1 - FracSevere - FracCritical
            ProbDeath = 0.4
            TimeICUDeath = 10
            DurHosp = 4
            tmax=365
            i=1
            variable = 'I3'
            TimeStart = 0
            TimeEnd = tmax
            reduc1 = 0.3
            reduc2 = 0
            reduc3 = 0
            reducasym = 0
            reducpre = 0
            AllowSeason = 'Não'
            SeasAmp = 0
            SeasPhase = 0
            AllowAsym = 'Não'
            FracAsym = 0.3
            DurAsym = 7
            AllowPresym = 'Não'
            PresymPeriod = 2

        #Menu de interveção
        TimeStart, TimeEnd, reduc1, reduc2, reduc3, reducpre, reducasym = intervencao(TimeStart,TimeEnd,reduc1,reduc2,reduc3,reducpre,reducasym, tmax)
        
        #Menu
        IncubPeriod, DurMildInf, FracMild, FracSevere, FracCritical, CFR, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod, seas0, b0, b1, b2, b3, be, N, i, tmax = menu(IncubPeriod, DurMildInf, FracSevere, FracCritical, ProbDeath, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod)            

        names = ["Sucetíveis (S)","Expostos (E0)","Pré-sintomáticos (E1)","Assintomáticos (I0)","Inf. Leve (I1)","Inf. Grave (I2)","Inf. Crítico (I3)","Recuperado (R)","Morto (D)"]
        if AllowAsym == 'Não':
            names.remove("Assintomáticos (I0)")
        if AllowPresym == 'Não':
            names.remove("Pré-sintomáticos (E1)")

        #Menu de seleção
        st.subheader('Selecione a variável que deseja visualizar:')
        variable = st.selectbox("", names)
        
        my_slot1 = st.empty()
        my_slot2 = st.empty()        
        my_slot3 = st.empty()        
        my_slot4 = st.empty()        
        my_slot5 = st.empty()        
        my_slot6 = st.empty()        
        my_slot7 = st.empty()        
        my_slot8 = st.empty()        
        my_slot9 = st.empty()        
        my_slot10 = st.empty()
        my_slot11 = st.empty()
        my_slot12 = st.empty()
   
        #Parâmetros do SEIR
        a0, a1, u, g0, g1, g2, g3, p1, p2, f, ic = params(IncubPeriod, FracMild, FracCritical, FracSevere, TimeICUDeath, CFR, DurMildInf, DurHosp, i, PresymPeriod, FracAsym, DurAsym, N)

        #Calculo das taxas de transmissão durante a intervenção
        b1Int = (1 - reduc1)*b1
        b2Int = (1 - reduc2)*b2
        b3Int = (1 - reduc3)*b3
        beInt = (1 - reducpre)*be
        b0Int = (1 - reducasym)*b0

        tvec=np.arange(0,tmax,0.1)
        soln=odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
        
        names = ["Sucetíveis (S)","Expostos (E0)","Pré-sintomáticos (E1)","Assintomáticos (I0)","Inf. Leve (I1)","Inf. Grave (I2)","Inf. Crítico (I3)","Recuperado (R)","Morto (D)"]
#########  Simulação sem intervenção #########################################################
        tvec=np.arange(0,tmax,0.1)
        sim_sem_int = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
        #Criando dataframe
        df_sim_sem_int = pd.DataFrame(sim_sem_int, columns = names)
        df_sim_sem_int['Tempo (dias)'] = tvec
        df_sim_sem_int['Simulação'] = 'Sem intervenção'
#############################################################################################
        
        #Simulação com intervenção
        df_sim_com_int = simulacao(TimeStart, TimeEnd, tmax, i, N, a0, a1, b0, be, b1, b2 , b3, b0Int, beInt, b1Int, b2Int, b3Int, g0, g1, g2, g3, p1, p2, u, names, f, AllowAsym, AllowPresym, SeasAmp, SeasPhase)
        y_index = 'Número por ' + str(N) +' pessoas'
        df_sim_com_int = df_sim_com_int.drop_duplicates(subset = ['Tempo (dias)'], keep = 'first')
        df_sem = pd.melt(df_sim_sem_int[['Tempo (dias)',variable]], id_vars = ['Tempo (dias)'], value_name = y_index, var_name = 'Legenda')
        df_sem['Legenda'] = df_sem['Legenda'] + ' (Sem intervenção)' 
        df_com = pd.melt(df_sim_com_int[['Tempo (dias)',variable]], id_vars = ['Tempo (dias)'], value_name = y_index, var_name = 'Legenda')
        df_com['Legenda'] = df_com['Legenda'] + ' (Com intervenção)'

        #Junta dataframes
        df = df_sem.append(df_com)
        
        if AllowAsym == 'Não':
            df = df[df['Legenda'] != "Assintomáticos (I0)"]
        if AllowPresym == 'Não':
            df = df[df['Legenda'] != "Pré-sintomáticos (E1)"]
        
        yscale = "Linear"
        yscale = st.radio("Escala do eixo Y", ["Linear", "Log"])
        
        #Plot
        if yscale == 'Log':
            fig = px.line(df, x="Tempo (dias)", y=y_index, log_y=True, color = 'Legenda')
                
        else:
            fig = px.line(df, x="Tempo (dias)", y=y_index, color = 'Legenda')
        my_slot1.plotly_chart(fig)
        
        #Cálculo da taxa reprodutiva e etc    
        if AllowSeason:
            R0 = taxa_reprodutiva_seas(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f, SeasAmp, SeasPhase)[0]
            R0Int = taxa_reprodutiva_seas(N, beInt, b0Int, b1Int, b2Int, b3Int, p1, p2, g0, g1, g2, g3, a1, u, f, SeasAmp, SeasPhase)[0]
        else:
            R0 = taxa_reprodutiva(N, be, b0, b1, b2, b3, p1, p2, g0, g1, g2, g3, a1, u, f)
            R0 = taxa_reprodutiva(N, beInt, b0Int, b1Int, b2Int, b3Int, p1, p2, g0, g1, g2, g3, a1, u, f)

            
        (r,DoublingTime) = new_growth_rate(g0,g1,g2,g3,p1,p2,be,b0,b1,b2,b3,u,a0,a1,N,f)
        (rInt,DoublingTimeInt) = new_growth_rate(g0,g1,g2,g3,p1,p2,beInt,b0Int,b1Int,b2Int,b3Int,u,a0,a1,N,f)
        
        Stat = pd.DataFrame({'Sem intervenção':[R0,r,DoublingTime],'Com intervenção':[R0Int,rInt,DoublingTimeInt]}, index=['R\N{SUBSCRIPT ZERO}','r (por dia)','t\N{SUBSCRIPT TWO}'])
        st.table(Stat)
        st.write("**- Sem intervenção**: A taxa de crescimento epidêmico é **{0:4.2f} por dia**; o tempo de duplicação é **{1:4.1f} dias**".format(r,DoublingTime))
        st.write("**- Com intervenção**: A taxa de crescimento epidêmico é **{0:4.2f} por dia**; o tempo de duplicação é **{1:4.1f} dias**".format(rInt,DoublingTimeInt))
        
        st.write("""**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo, com e sem intervenção. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo.""")
        st.write("""O tamanho da população, a condição inicial e os valores dos parâmetros usados para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). A força e o tempo da intervenção são controlados pelos controles deslizantes abaixo do gráfico. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.""")
        
    elif page == "Capacidade Hospitalar":
        st.title('Casos COVID-19 vs capacidade de assistência médica')
        st.subheader('''Simule casos previstos do COVID-19 versus a capacidade do sistema de saúde de cuidar deles. Os cuidados necessários dependem da gravidade da doença: indivíduos com infecção "grave" requerem hospitalização e indivíduos com infecção "crítica" requerem cuidados na UTI e ventilação mecânica.''')
        st.write('Os parâmetros de redução de transmissão podem ser modificados no painel lateral esquerdo.')

        if IncubPeriod == 0:
            IncubPeriod = 5
            DurMildInf = 6
            FracSevere = 0.15
            FracCritical = 0.05
            FracMild = 1 - FracSevere - FracCritical
            ProbDeath = 0.4
            TimeICUDeath = 10
            DurHosp = 4
            tmax=365
            i=1
            variable = 'Todos casos sintomáticos (l1,l2,l3) vs Leitos de hospital e UTI'
            TimeStart = 0
            TimeEnd = tmax
            reduc1 = 0.3
            reduc2 = 0
            reduc3 = 0
            reducasym = 0
            reducpre = 0
            AllowSeason = 'Não'
            SeasAmp = 0
            SeasPhase = 0
            AllowAsym = 'Não'
            FracAsym = 0.3
            DurAsym = 7
            AllowPresym = 'Não'
            PresymPeriod = 2

        #Menu de seleção    
        varnames = ['Todos casos sintomáticos (l1,l2,l3) vs Leitos de hospital + UTI',
                 'Casos graves (l2) e críticos (l3) vs Leitos de hospital + UTI',
                 'Infecções críticas (l3) vs Leitos na UTI',
                'Infecções críticas (l3) vs Capacidade de ventilação']
        st.subheader('Selecione a variável que deseja visualizar:')
        variable = st.selectbox("", varnames)
        
        my_slot1 = st.empty()
        my_slot2 = st.empty()
        my_slot3 = st.empty()
        my_slot4 = st.empty()
        my_slot5 = st.empty()
        my_slot6 = st.empty()
        my_slot7 = st.empty()
        my_slot8 = st.empty()
        my_slot9 = st.empty()
        my_slot10 = st.empty()
        my_slot11 = st.empty()
        my_slot12 = st.empty()
        
        
        TimeStart, TimeEnd, reduc1, reduc2, reduc3, reducpre, reducasym = intervencao(TimeStart,TimeEnd,reduc1,reduc2,reduc3,reducpre,reducasym, tmax)
        
        IncubPeriod, DurMildInf, FracMild, FracSevere, FracCritical, CFR, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod, seas0, b0, b1, b2, b3, be, N, i, tmax = menu(IncubPeriod, DurMildInf, FracSevere, FracCritical, ProbDeath, DurHosp, TimeICUDeath, AllowSeason, SeasAmp, SeasPhase, AllowAsym, FracAsym, DurAsym, AllowPresym, PresymPeriod)     
           
        
        st.subheader('Capacidade do sistema de saúde')
        AvailHospBeds=st.number_input(label="Leitos hospitalares disponíveis (por mil pessoas)", value=1.95)*N/1000 #Available hospital beds per 1000 ppl in BR based on total beds and occupancy
        AvailICUBeds=st.number_input(label="Leitos na UTI disponíveis (por mil pessoas)", value=0.137)*N/1000 #Available ICU beds per 1000 ppl in BR, based on total beds and occupancy. Only counts adult not neonatal/pediatric beds
        ConvVentCap=st.number_input(label="Pacientes que podem ser ventilados em protocolos convencionais (por mil pessoas)", value=0.062)*N/1000 #Estimated excess # of patients who could be ventilated in US (per 1000 ppl) using conventional protocols
        ContVentCap=st.number_input(label="Pacientes que podem ser ventilados em protocolo de contingência (por mil pessoas)", value=0.15)*N/1000 #Estimated excess # of patients who could be ventilated in US (per 1000 ppl) using contingency protocols
        CrisisVentCap=st.number_input(label="Pacientes que podem ser ventilados em protocolo de crise (por mil pessoas)", value=0.24)*N/1000 #Estimated excess # of patients who could be ventilated in US (per 1000 ppl) using crisis protocols
       
        a0, a1, u, g0, g1, g2, g3, p1, p2, f, ic = params(IncubPeriod, FracMild, FracCritical, FracSevere, TimeICUDeath, CFR, DurMildInf, DurHosp, i, PresymPeriod, FracAsym, DurAsym, N)

        b1Int = (1 - reduc1)*b1
        b2Int = (1 - reduc2)*b2
        b3Int = (1 - reduc3)*b3
        beInt = max(0,(1 - reducpre)*be)
        b0Int = max(0,(1 - reducasym)*b0) 
        
        names = ["Sucetíveis (S)","Expostos (E1)","Pré-sintomáticos (E1)","Assintomáticos (I0)","Inf. Leve (I1)","Inf. Grave (I2)","Inf. Crítico (I3)","Recuperado (R)","Morto (D)"]

#########  Simulação sem intervenção #########################################################
        tvec=np.arange(0,tmax,0.1)
        sim_sem_int = odeint(seir,ic,tvec,args=(a0,a1,g0,g1,g2,g3,p1,p2,u,be,b0,b1,b2,b3,f, AllowPresym, AllowAsym, SeasAmp, SeasPhase))
        #Criando dataframe
        df_sim_sem_int = pd.DataFrame(sim_sem_int, columns = names)
        df_sim_sem_int['Tempo (dias)'] = tvec
        df_sim_sem_int['Simulação'] = 'Sem intervenção'
#############################################################################################
        
        #Simulação com intervenção
        df_sim_com_int = simulacao(TimeStart, TimeEnd, tmax, i, N, a0, a1, b0, be, b1, b2 , b3, b0Int, beInt, b1Int, b2Int, b3Int, g0, g1, g2, g3, p1, p2, u, names, f, AllowAsym, AllowPresym, SeasAmp, SeasPhase)
        y_index = 'Número por ' + str(N) +' pessoas'  

        #Plots
        if variable == 'Todos casos sintomáticos (l1,l2,l3) vs Leitos de hospital + UTI':
            df_sim_com_int[y_index] = df_sim_com_int["Inf. Leve (I1)"] + df_sim_com_int["Inf. Grave (I2)"] + df_sim_com_int["Inf. Crítico (I3)"]
            df_sim_sem_int[y_index] = df_sim_sem_int["Inf. Leve (I1)"] + df_sim_sem_int["Inf. Grave (I2)"] + df_sim_sem_int["Inf. Crítico (I3)"]
            df = df_sim_sem_int[['Tempo (dias)',y_index, 'Simulação']].append(df_sim_com_int[['Tempo (dias)',y_index, 'Simulação']])
            
            data1 = []
            for x in range(0, tmax):
                data1.append([x,'Leitos hospitalares + UTI',AvailHospBeds + AvailICUBeds])
                
            df = df.append(pd.DataFrame(data1, columns = ['Tempo (dias)','Simulação',y_index]))
            
        elif variable == 'Casos graves (l2) e críticos (l3) vs Leitos de hospital + UTI':
            df_sim_com_int[y_index] = df_sim_com_int["Inf. Grave (I2)"] + df_sim_com_int["Inf. Crítico (I3)"]
            df_sim_sem_int[y_index] = df_sim_sem_int["Inf. Grave (I2)"] + df_sim_sem_int["Inf. Crítico (I3)"]
            df = df_sim_sem_int[['Tempo (dias)',y_index, 'Simulação']].append(df_sim_com_int[['Tempo (dias)',y_index, 'Simulação']])
            
            data1 = []
            for x in range(0, tmax):
                data1.append([x,'Leitos hospitalares + UTI',AvailHospBeds + AvailICUBeds])
                
            df = df.append(pd.DataFrame(data1, columns = ['Tempo (dias)','Simulação',y_index]))

        elif variable == 'Infecções críticas (l3) vs Leitos na UTI':
            df_sim_com_int[y_index] = df_sim_com_int["Inf. Crítico (I3)"]
            df_sim_sem_int[y_index] = df_sim_sem_int["Inf. Crítico (I3)"]
            df = df_sim_sem_int[['Tempo (dias)',y_index, 'Simulação']].append(df_sim_com_int[['Tempo (dias)',y_index, 'Simulação']])
            
            data1 = []
            for x in range(0, tmax):
                data1.append([x,'Leitos da UTI',AvailICUBeds])
                
            df = df.append(pd.DataFrame(data1, columns = ['Tempo (dias)','Simulação',y_index]))
        
        elif variable == 'Infecções críticas (l3) vs Capacidade de ventilação':
            df_sim_com_int[y_index] = df_sim_com_int["Inf. Crítico (I3)"]
            df_sim_sem_int[y_index] = df_sim_sem_int["Inf. Crítico (I3)"]
            df = df_sim_sem_int[['Tempo (dias)',y_index, 'Simulação']].append(df_sim_com_int[['Tempo (dias)',y_index, 'Simulação']])
            
            data1 = []
            data2 = []
            data3 = []
            for x in range(0, tmax):
                data1.append([x,'Ventilação em protocolos convencionais',ConvVentCap])
                data2.append([x,'Ventilação em protocolo de convenção',ContVentCap])
                data3.append([x,'Ventilação em protocolo de crise',CrisisVentCap])
                
            df = df.append(pd.DataFrame(data1, columns = ['Tempo (dias)','Simulação',y_index]))
            df = df.append(pd.DataFrame(data2, columns = ['Tempo (dias)','Simulação',y_index]))
            df = df.append(pd.DataFrame(data3, columns = ['Tempo (dias)','Simulação',y_index]))
            
        fig = px.line(df, x="Tempo (dias)", y=y_index, color = 'Simulação')
        my_slot1.plotly_chart(fig)

        
        st.write("""**Instruções para o usuário:** O gráfico mostra o número esperado de indivíduos infectados, recuperados, suscetíveis ou mortos ao longo do tempo, com e sem intervenção. Os indivíduos infectados passam primeiro por uma fase exposta / incubação, onde são assintomáticos e não infecciosos, e depois passam para um estágio sintomático e de infecções classificados pelo estado clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo é fornecida na guia Descrição do Modelo.""")
        st.write("""O tamanho da população, a condição inicial e os valores dos parâmetros usados para simular a propagação da infecção podem ser especificados através dos controles deslizantes localizados no painel esquerdo. Os valores padrão do controle deslizante são iguais às estimativas extraídas da literatura (consulte a guia Fontes). A força e o tempo da intervenção são controlados pelos controles deslizantes abaixo do gráfico. O gráfico é interativo: passe o mouse sobre ele para obter valores, clique duas vezes em uma curva na legenda para isolá-la ou clique duas vezes para removê-la. Arrastar sobre um intervalo permite aplicar zoom.""")
        
    elif page=="Fontes":
        if __name__ == "__main__":
            ft.main()
            
    elif page == "Código":
        st.write("""Os códigos deste simulador estão no [GitHub](https://github.com/dumsantos/SEIR_COVID19_BR) e possuem uma versão em Python usando Streamlit e outra em R usando Shiny. Contate eduardo@cappra.com.br em caso de perguntas.

Agradecimento para Alison Hill que desenvolveu a ferramenta inicial em R, [Guilherme Machado](https://www.linkedin.com/in/guilhermermachado/) e [Caetano Slaviero](https://www.linkedin.com/in/caetanoslaviero/) que auxiliaram na tradução e codificação da versão em Python e também a todo o time da Cappra Institute for Data Science pelas pesquisas desenvolvidas.

Quer saber mais sobre o COVID-19, confira nosso [estudo](http://covid19.cappralab.com).""")
        
    elif page == "Tutorial":
        st.write("""Em construção""")
        


if __name__ == "__main__":
    main(IncubPeriod)
    

