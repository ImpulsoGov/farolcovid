import numpy as np, pandas as pd
from scipy.integrate import odeint
from numpy import linalg as LA

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
