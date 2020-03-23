library(deSolve)
library(reshape)
source("code/functions.R")

# Definir parâmetros
# (no app Shiny estes são colocados pelos sliders)

IncubPeriod= 5 #Período de incubação em dias
DurMildInf= 6 #Duração de infecções leves em dias
FracSevere= 15 Fração de infecções graves
FracCritical= 5 Fração de infecções críticas
ProbDeath= 40 #Taxa de mortalidade para infecções críticas
DurHosp= 4 #Duração de infecções graves/hospitalização
TimeICUDeath= 10 #Duração de infecções críticas/Internação em UTI
b1= 0.33 #Taxa de transmissão (infecções leves)
b21= 0 #Taxa de transmissão (infecções graves, relativo a leves)
b31= 0 #Taxa de transmissão (infecções críticas, relativo a leves)
LogN= 3 #Tamanho populacional total (log10)
Tmax= 300 #Número inicial de infectados
InitInf= 1 #Tempo máximo
yscale="linear"

#Colocar estes em uma estrutura de input
input=list("IncubPeriod"=IncubPeriod,"DurMildInf"=DurMildInf,"FracSevere"=FracSevere,"FracCritical"=FracCritical,"ProbDeath"=ProbDeath,"DurHosp"=DurHosp,"TimeICUDeath"=TimeICUDeath,"b1"=b1,"b21"=b21,"b31"=b31,"LogN"=LogN,"Tmax"=Tmax,"InitInf"=InitInf,"yscale"=yscale)

CFR=(input$ProbDeath/100)*(input$FracCritical) #Razão de fatalidade de casos

# Rodar simulações

sim=SimSEIR(input)

out.df=sim$out.df
N=sim$N
Ro=sim$Ro
r=sim$r
DoublingTime=sim$DoublingTime

#reformatar dados para plotar
out.df2=rename(out.df, c(S="Suscetíveis",E="Expostos", I1="Infectados.Leves", I2="Infectados.Graves", 
                         I3="Infectados.Críticos", R="Recuperados", D="Óbitos"))
out=melt(out.df,id="time")
out2=melt(out.df2,id="time")
out$variableName=out2$variable
out$variableLegend = paste0(out$variableName,' (',out$variable,')')
out$variableLegend = factor(out$variableLegend, levels = unique(out[["variableLegend"]]))

#plot
p=plot_ly(data = out, x=~time, y=~value, color=~variableLegend, type='scatter', mode='lines')

p=layout(p,xaxis=list(title="Time since introduction (days)"),yaxis=list(title=paste("Number per",formatC(N,big.mark=",",format="f",digits=0),"people"),type=input$yscale),
         annotations=list(text=HTML(paste("R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," per day <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," days")),
                          showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="center",y=0.4, align="left"))
p
