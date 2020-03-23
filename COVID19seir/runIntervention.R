library(deSolve)
library(reshape)
source("code/functions.R")

# Set parameters
# (in Shiny app these are input by sliders)

IncubPeriod= 5 #Período de incubação em dias
DurMildInf= 6 #Duração de infecções leves em dias
FracSevere= 15 #Fração de infecções graves
FracCritical= 5 #Fração de infecções críticas
ProbDeath= 40 #Taxa de mortalidade para infecções críticas
DurHosp= 4 #Duração de infecções graves/internações
TimeICUDeath= 10 # de infecções críticas/internação em UTI
b1= 0.33 #Taxa de transmissão (infecções leves)
b21= 0 #Taxa de transmissão (infecções graves, relativo a leves)
b31= 0 #Taxa de transmissão (infecções críticas, relativo a leves)
LogN= 3 #Tamanho populacional total (log10)
Tmax= 300 #Número inicial de infectados
InitInf= 1 #Tempo máximo
yscale="linear"

#Parâmetros de Intervenção
VarShowInt="Cases" #This is the variable to be plotted. Pptions "E", "I1", "I2", "I3", "R", "D", "All infected (E+I1+I2+I3)"="Inf","All symptomatic (I1+I2+I3)"="Cases","All hospitalized (I2+I3)"="Hosp"
Tint = 0 #Tempo de ínicio da intervenção (dias)
Tend = 300 #Tempo de término da Intervenção (dias)
s1=30 #Redução de transmissão de infecções leves
s2=0 #Redução de transmissão de infecções graves
s3 = 0 #Redução de transmissão de infecções críticas
RoundOne = TRUE #Arredondar valores ao inteiro mais próximo pós-intervenção?"

#Colocar estes em uma estrutura de input
input=list("IncubPeriod"=IncubPeriod,"DurMildInf"=DurMildInf,"FracSevere"=FracSevere,"FracCritical"=FracCritical,"ProbDeath"=ProbDeath,"DurHosp"=DurHosp,"TimeICUDeath"=TimeICUDeath,"b1"=b1,"b21"=b21,"b31"=b31,"LogN"=LogN,"Tmax"=Tmax,"InitInf"=InitInf,"yscale"=yscale,"VarShowInt"=VarShowInt,"Tint"=Tint,"Tend"=Tend,"s1"=s1,"s2"=s2,"s3"=s3,"RoundOne"=RoundOne)

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

if(input$VarShowInt=="Inf"){
  
  out.df$value=rowSums(out.df[,c("E", "I1","I2","I3")]) # criar variável observada
  outInt.df$value=rowSums(outInt.df[,c("E", "I1","I2","I3")])
  
}else if(input$VarShowInt=="Cases"){
  out.df$value=rowSums(out.df[,c("I1","I2","I3")]) # criar variável observada
  outInt.df$value=rowSums(outInt.df[,c("I1","I2","I3")])
  
}else if(input$VarShowInt=="Hosp"){
  out.df$value=rowSums(out.df[,c("I2","I3")]) # criar variável observada
  outInt.df$value=rowSums(outInt.df[,c("I2","I3")])
  out.df$Intervention="Padrão" # adicionar coluna de intervenção
  
}else{
  
  out.df$value=out.df[,input$VarShowInt] # criar variável observada
  outInt.df$value=outInt.df[,input$VarShowInt]
  
}
out.df$Intervention="Padrão" # adicionar coluna de intervenção
outInt.df$Intervention="Intervenção"
outAll.df=rbind(out.df,outInt.df) #combine baseline and intervention
outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # escolher apenas coluna do caso
outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]


p=plot_ly(data = outAll.sub, x=~time, y=~value, color=~Intervention, type='scatter', mode='lines',colors=c("#a50f15","#fc9272"))

p=layout(p,xaxis=list(title="Time since introduction (days)"),yaxis=list(title=paste("Number per", formatC(N,big.mark=",",format="f",digits=0),"people"),type=input$yscaleInt),
         annotations=list(text=HTML(paste("Baseline: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," per day <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," days <br><br>Intervention: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," per day <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1)," days")),
                          showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.5, align="left")
)

p