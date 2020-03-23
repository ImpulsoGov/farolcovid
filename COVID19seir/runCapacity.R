library(deSolve)
library(reshape)
library(googlesheets4)
sheets_deauth()
source("code/functions.R")

# Set parameters
# (in Shiny app these are input by sliders)

IncubPeriod= 5 #Período de incubação em dias
DurMildInf= 6 #Duração de infecções leves em dias
FracSevere= 15 #Fração de infecções graves
FracCritical= 5 #Fração de infecções críticas
ProbDeath= 40 #Taxa de mortalidade para infecções críticas
DurHosp= 4 #Duração de infecções graves/internações
TimeICUDeath= 10 #Duração de infecções críticas/internação em UTI
b1= 0.33 #Transmission rate (mild infections)
b21= 0 #Taxa de transmissão (infecções graves, relativo a leves)
b31= 0 #Transmission rate (infecções críticas, relativo a leves)
LogN= 3 #Tamanho populacional total (log10)
Tmax= 300 #Número inicial de infectados
InitInf= 1 #Tempo máximo
yscale="linear"

#Parâmetros de Intervenção
VarShowCap="Hosp" # Esta é a variável a ser plottada. Opções: "Critical Infections (I3) vs ICU beds"="I3bed", "Critical Infections (I3) vs ventilator capacity"="I3mv", "Severe + Critical Infections (I2+I3) vs Hospital Beds"="Hosp", "All symptomatic cases (I1+I2+I3) vs Hospital Beds"="CasesCap"
TintC = 0 #Tempo de ínicio da intervenção (dias)
TendC = 300 #Tempo de término da Intervenção (dias)
s1C=30 #Redução de transmissão de infecções leves
s2C=0 #Redução de transmissão de infecções graves
s3C = 0 #Redução de transmissão de infecções críticas
RoundOneCap = TRUE #Arredondar valores ao inteiro mais próximo pós-intervenção?"

#Parâmetros de capacidade (EUA)
HospBedper=2.8 #Leitos hospitalares disponíveis a cada 1000 pessoas 
HospBedOcc=66 # Fração de ocupação média de leitos hospitalares
ICUBedper=0.26 # Total de leitos de UTI disponíveis a cada 1000 pessoas
ICUBedOcc=68 # Fração de ocupação média de leitos de UTI
IncFluOcc=10 # acréscimo na ocupação durante época de gripe sazonal
ConvVentCap=0.062 # Capacidade convencional de ventilação mecânica, a cada 1000 pessoas
ContVentCap=0.155 # Capacidade de contingência de ventilação mecânica, a cada 1000 pessoas
CrisisVentCap=0.418 # Capacidade de crise de ventilação mecânica, a cada 1000 pessoas

#Colocar estes em uma estrutura de input
input=list("IncubPeriod"=IncubPeriod,"DurMildInf"=DurMildInf,"FracSevere"=FracSevere,"FracCritical"=FracCritical,"ProbDeath"=ProbDeath,"DurHosp"=DurHosp,"TimeICUDeath"=TimeICUDeath,"b1"=b1,"b21"=b21,"b31"=b31,"LogN"=LogN,"Tmax"=Tmax,"InitInf"=InitInf,"yscale"=yscale,"VarShowCap"=VarShowCap,"TintC"=TintC,"Tend"=TendC,"s1C"=s1C,"s2C"=s2C,"s3C"=s3C,"RoundOneCap"=RoundOneCap,"HospBedper"=HospBedper,"HospBedOcc"=HospBedOcc,"ICUBedper"=ICUBedper,"ICUBedOcc"=ICUBedOcc,"IncFluOcc"=IncFluOcc,"ConvVentCap"=ConvVentCap,"ContVentCap"=ContVentCap,"CrisisVentCap"=CrisisVentCap)

CFR=(input$ProbDeath/100)*(input$FracCritical) #Taxa de mortalidade de casos

# Rodar simulações



sim=SimSEIR(input)

out.df=sim$out.df
N=sim$N
Ro=sim$Ro
r=sim$r
DoublingTime=sim$DoublingTime

simInt=SimSEIRintB(input)

outInt.df=simInt$out.df
RoInt=simInt$Ro
rInt=simInt$r
DoublingTimeInt=simInt$DoublingTime

Tmax=input$Tmax

#subsetar as varáveis relevantes e adicionar uma coluna para capacidade
capParams=SetHospCapacity(input)

if(input$VarShowCap=="I3mv"){
  
  out.df$value=out.df[,"I3"] # criar variável observada
  outInt.df$value=outInt.df[,"I3"]
  out.df$Intervention="Padrão" # adicionar coluna de intervenção
  outInt.df$Intervention="Intervenção"
  outAll.df=rbind(out.df,outInt.df) #combinar padrão e intervenção
  outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # escolher apenas coluna do caso
  outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
  outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
  
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["ConvVentCap"]*(N/1000), "Intervention"="Conventional Mechanical \n Ventilator Capacity")
  combData=rbind(outAll.sub,capData)
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["ContVentCap"]*(N/1000), "Intervention"="Contingency Mechanical \n Ventilator Capacity")
  combData=rbind(combData,capData)
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["CrisisVentCap"]*(N/1000), "Intervention"="Crisis Mechanical \n Ventilator Capacity")
  combData=rbind(combData,capData)
  
  p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey","grey","grey"), linetypes=c("solid","solid","dash","dashdot","dot"))
  
}else if(input$VarShowCap=="I3bed"){
  
  out.df$value=out.df[,"I3"] # criar variável observada
  outInt.df$value=outInt.df[,input$VarShowInt]
  out.df$Intervention="Padrão" # adicionar coluna de intervenção
  outInt.df$Intervention="Intervenção"
  outAll.df=rbind(out.df,outInt.df) #combinar padrão e intervenção
  outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # escolher apenas coluna do caso
  outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
  outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
  
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailICUBeds"]*(N/1000), "Intervention"="Available ICU Beds")
  combData=rbind(outAll.sub,capData)
  
  p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
  
}else if(input$VarShowCap=="Hosp"){
  
  out.df$value=rowSums(out.df[,c("I2","I3")]) # criar variável observada
  outInt.df$value=rowSums(outInt.df[,c("I2","I3")])
  out.df$Intervention="Padrão" # adicionar coluna de intervenção
  outInt.df$Intervention="Intervenção"
  outAll.df=rbind(out.df,outInt.df) #combinar padrão e intervenção
  outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # escolher apenas coluna do caso
  outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
  outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
  
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailHospBeds"]*(N/1000), "Intervention"="Available Hospital Beds")
  combData=rbind(outAll.sub,capData)
  
  p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
  
}else{ #CasesCap
  out.df$value=rowSums(out.df[,c("I1","I2","I3")]) # criar variável observada
  outInt.df$value=rowSums(outInt.df[,c("I1","I2","I3")])
  out.df$Intervention="Padrão" # adicionar coluna de intervenção
  outInt.df$Intervention="Intervenção"
  outAll.df=rbind(out.df,outInt.df) #combinar padrão e intervenção
  outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # escolher apenas coluna do caso
  outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
  outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
  
  capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailHospBeds"]*(N/1000), "Intervention"="Available Hospital Beds")
  combData=rbind(outAll.sub,capData)
  
  p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
  
}


p=layout(p,xaxis=list(title="Time since introduction (days)"),yaxis=list(title=paste("Number per",formatC(N,big.mark=",",format="f",digits=0),"people"),type=input$yscaleCap), 
         annotations=list(text=HTML(paste("Baseline: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," per day <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," days <br><br>Intervention: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," per day <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1), " days")),
                          showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.5, align="left")
)
p