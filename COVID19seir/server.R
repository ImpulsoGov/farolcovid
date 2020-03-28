library(deSolve)
library(reshape)
library(googlesheets4)
sheets_deauth()
source("code/functions.R")

# ----------------------------------------------------------------------------
# Load data:
# --------------------

HospDataAll=read_sheet("https://docs.google.com/spreadsheets/d/1zZKKnZ47lqfmUGYDQuWNnzKnh-IDMy15LBaRmrBcjqE/edit#gid=1585003222",sheet="Hospital capacity")
HospDataAll=na.omit(HospDataAll)
hdata = as.data.frame(t(data.frame(HospDataAll[,c("Name","Value")], row.names="Name")))


function(input, output, session) {
  
  # Plotar curso temporal de todas as variáveis
  
  output$plot0 = renderPlotly({
   
    sim=SimSEIR(input)
    
    out.df=sim$out.df
    N=sim$N
    Ro=sim$Ro
    r=sim$r
    DoublingTime=sim$DoublingTime
    
    #combinar classes expostas para plotar
    out.df$E0=out.df$E0+out.df$E1
    out.df$E1=NULL
    out.df=rename(out.df, c(E0="E"))
    
    #reformatar dados para plotar
    out.df2=rename(out.df, c(S="Suscetíveis", E="Expostos", I0="Infectados.Assintomaticos", I1="Infectados.Leves", I2="Infectados.Graves", I3="Infectados.Críticos", R="Recuperados", D="Falecidos"))
    out=melt(out.df,id="time")
    out2=melt(out.df2,id="time")
    out$variableName=out2$variable
    out$variableLegend = paste0(out$variableName,' (',out$variable,')')
    out$variableLegend = factor(out$variableLegend, levels = unique(out[["variableLegend"]]))
    
    #criar dados para plotar total de infectados
    Comb.df=out.df
    Comb.df$I0=rowSums(out.df[,c("I0","I1","I2","I3")]) # criar total de infectados
    Comb.df=rename(Comb.df, c(I0="I"))
    Comb.df$I1=NULL
    Comb.df$I2=NULL
    Comb.df$I3=NULL
    
    Comb.df2=rename(Comb.df, c(S="Suscetíveis", E="Expostos", I="Infectados", R="Recuperados", D="Falecidos"))
    Comb=melt(Comb.df,id="time")
    Comb2=melt(Comb.df2,id="time")
    Comb$variableName=Comb2$variable
    Comb$variableLegend = paste0(Comb$variableName,' (',Comb$variable,')')
    Comb$variableLegend = factor(Comb$variableLegend, levels = unique(Comb[["variableLegend"]]))
    
    
    #plot
    
    if(input$PlotCombine=="Yes"){
      p=plot_ly(data = Comb, x=~time, y=~value, color=~variableLegend, type='scatter', mode='lines')
    }else{
      if(input$AllowAsym=="Yes"){
        p=plot_ly(data = out, x=~time, y=~value, color=~variableLegend, type='scatter', mode='lines')
      }else{
        #don't want to show the I0 class in the plot
        outSym=out[out$variable!="I0",]
        p=plot_ly(data = outSym, x=~time, y=~value, color=~variableLegend, type='scatter', mode='lines')
      }
    }
    
    p=layout(p,xaxis=list(title="Tempo desde introdução (dias)"),yaxis=list(title=paste("Número a cada",formatC(N,big.mark=",",format="f",digits=0),"pessoas"),type=input$yscale),
             annotations=list(text=HTML(paste("R", tags$sub(0),'=',formatC(Ro,digits=2)," <br>r =", formatC(r,digits=2)," por dia <br>T",tags$sub(2)," = ",formatC(DoublingTime,digits=2)," days")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="center",y=0.35, align="left"))
    
    if(input$AllowSeason=="Yes"){
      
      Ro.Season=sim$Ro.Season
      tpeak=365+input$seas.phase
      tmin=180+input$seas.phase
      #print(Ro.Season)
      #print(Ro.Season$Ro.now)
      p=layout(p,annotations=list(text=HTML(paste("R Sazonal", tags$sub(0), ": <br>R Inicial", tags$sub(0),'=',formatC(Ro.Season$Ro.now,digits=2),"<br>R Pico", tags$sub(0),'=',formatC(Ro.Season$Ro.max,digits=2),"@day",formatC(tpeak,format = "f",digits=0),"<br>R Mín.", tags$sub(0),'=',formatC(Ro.Season$Ro.min,digits=2),"@day",formatC(tmin,format = "f",digits=0))),
                                  showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="center",y=0.05, align="left"))
      
    }
    p

  })
  
  #Plotar curso temporal com uma intervenção
  
  output$plotInt = renderPlotly({
    
    sim=SimSEIR(input)
    
    out.df=sim$out.df
    N=sim$N
    Ro=sim$Ro
    r=sim$r
    DoublingTime=sim$DoublingTime
    
    #combine exposed classes for plotting
    out.df$E0=out.df$E0+out.df$E1
    out.df$E1=NULL
    out.df=rename(out.df, c(E0="E"))
    
    simInt=SimSEIRintB(input)
    
    outInt.df=simInt$out.df
    RoInt=simInt$Ro
    rInt=simInt$r
    DoublingTimeInt=simInt$DoublingTime
    
    #combine exposed classes for plotting
    outInt.df$E0=outInt.df$E0+outInt.df$E1
    outInt.df$E1=NULL
    outInt.df=rename(outInt.df, c(E0="E"))
    
    if(input$VarShowInt=="Inf"){
      
      out.df$value=rowSums(out.df[,c("E","I0","I1","I2","I3")]) # criar variável observada
      outInt.df$value=rowSums(outInt.df[,c("E","I0","I1","I2","I3")])
      
    }else if(input$VarShowInt=="Cases"){
      out.df$value=rowSums(out.df[,c("I1","I2","I3")]) # criar variável observada
      outInt.df$value=rowSums(outInt.df[,c("I1","I2","I3")])
      
    }else if(input$VarShowInt=="Hosp"){
      out.df$value=rowSums(out.df[,c("I2","I3")]) # criar variável observada
      outInt.df$value=rowSums(outInt.df[,c("I2","I3")])

    }else{

      out.df$value=out.df[,input$VarShowInt] # criar variável observada
      outInt.df$value=outInt.df[,input$VarShowInt]
      
    }
    out.df$Intervention="Padrão" # adicionar coluna de intervenção
    outInt.df$Intervention="Intervenção"
    outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
    outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
    outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
    outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
    
    
    p=plot_ly(data = outAll.sub, x=~time, y=~value, color=~Intervention, type='scatter', mode='lines',colors=c("#a50f15","#fc9272"))
    
    p=layout(p,xaxis=list(title="Tempo desde introdução (dias)"),yaxis=list(title=paste("Número a cada", formatC(N,big.mark=",",format="f",digits=0),"pessoas"),type=input$yscaleInt),
             annotations=list(text=HTML(paste("Baseline: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," dias <br><br>Intervenção: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1)," dias")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.8, align="left")
             )
    
    if(input$AllowSeason=="Yes"){
      
      Ro.Season=sim$Ro.Season
      RoInt.Season=simInt$Ro.Season
      tpeak=365+input$seas.phase
      tmin=180+input$seas.phase
      
      p=layout(p,annotations=list(text=HTML(paste0("R Sazonal", tags$sub(0), ": <br>R Inicial", tags$sub(0),'=',formatC(Ro.Season$Ro.now,digits=2),"/",formatC(RoInt.Season$Ro.now,digits=2),"<br>R Pico", tags$sub(0),'=',formatC(Ro.Season$Ro.max,digits=2),"/",formatC(RoInt.Season$Ro.max,digits=2),"<br>  @day ",formatC(tpeak,format = "f",digits=0),"<br>R Mín.", tags$sub(0),'=',formatC(Ro.Season$Ro.min,digits=2),"/",formatC(RoInt.Season$Ro.min,digits=2),"<br>  @day ",formatC(tmin,format = "f",digits=0))),
                                  showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="center",y=0, align="left"))
      
    }
    
    p
    
  })
  
  output$plotCap = renderPlotly({
    
    sim=SimSEIR(input)
    
    out.df=sim$out.df
    N=sim$N
    Ro=sim$Ro
    r=sim$r
    DoublingTime=sim$DoublingTime
    
    #combinar classes expostas para plotar
    out.df$E0=out.df$E0+out.df$E1
    out.df$E1=NULL
    out.df=rename(out.df, c(E0="E"))
    
    simInt=SimSEIRintB(input)
    
    outInt.df=simInt$out.df
    RoInt=simInt$Ro
    rInt=simInt$r
    DoublingTimeInt=simInt$DoublingTime
    
    #combinar classes expostas para plotar
    outInt.df$E0=outInt.df$E0+outInt.df$E1
    outInt.df$E1=NULL
    outInt.df=rename(outInt.df, c(E0="E"))
    
    Tmax=input$Tmax
    
    #subsetar as variáveis relevantes e adicionar uma coluna para capacidade
    capParams=SetHospCapacity(input)

    if(input$VarShowCap=="I3mv"){
      
      out.df$value=out.df[,"I3"] # criar variável observada
      outInt.df$value=outInt.df[,"I3"]
      out.df$Intervention="Padrão" # adicionar coluna de intervenção
      outInt.df$Intervention="Intervenção"
      outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
      outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
      outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
      outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
      
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["ConvVentCap"]*(N/1000), "Intervention"="Capacidade de Ventiladores \n Mecânicos Convencional")
      combData=rbind(outAll.sub,capData)
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["ContVentCap"]*(N/1000), "Intervention"="Capacidade de Ventiladores \n Mecânicos em Contigência")
      combData=rbind(combData,capData)
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["CrisisVentCap"]*(N/1000), "Intervention"="Capacidade de Ventiladores \n Mêcanicos em Emergência")
      combData=rbind(combData,capData)
      
      p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey","grey","grey"), linetypes=c("solid","solid","dash","dashdot","dot"))
      
    }else if(input$VarShowCap=="I3bed"){
      
      out.df$value=out.df[,"I3"] # criar variável observada
      outInt.df$value=outInt.df[,"I3"]
      out.df$Intervention="Padrão" # adicionar coluna de intervenção
      outInt.df$Intervention="Intervenção"
      outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
      outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
      outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
      outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
      
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailICUBeds"]*(N/1000), "Intervention"="Leitos de UTI disponíveis")
      combData=rbind(outAll.sub,capData)
      
      p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
      
    }else if(input$VarShowCap=="Hosp"){
      
      out.df$value=rowSums(out.df[,c("I2","I3")]) # criar variável observada
      outInt.df$value=rowSums(outInt.df[,c("I2","I3")])
      out.df$Intervention="Padrão" # adicionar coluna de intervenção
      outInt.df$Intervention="Intervenção"
      outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
      outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
      outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
      outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
      
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailHospBeds"]*(N/1000), "Intervention"="Leitos Disponíveis")
      combData=rbind(outAll.sub,capData)
      
      p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
      
    }else{ #CasesCap
      out.df$value=rowSums(out.df[,c("I1","I2","I3")]) # criar variável observada
      outInt.df$value=rowSums(outInt.df[,c("I1","I2","I3")])
      out.df$Intervention="Padrão" # adicionar coluna de intervenção
      outInt.df$Intervention="Intervenção"
      outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
      outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
      outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
      outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
      
      capData=data.frame("time"=seq(0, Tmax, length.out = 1e3),"value"=rep(1,1e3)*capParams["AvailHospBeds"]*(N/1000), "Intervention"="Leitos Disponíveis")
      combData=rbind(outAll.sub,capData)
      
      p=plot_ly(data = combData, x=~time, y=~value, color=~Intervention, linetype=~Intervention, type='scatter', mode='lines', colors=c("#a50f15","#fc9272","grey"), linetypes=c("solid","solid","dash"))
      
    }
    
    
    p=layout(p,xaxis=list(title="Tempo desde introdução (dias)"),yaxis=list(title=paste("Número a cada",formatC(N,big.mark=",",format="f",digits=0),"pessoas"),type=input$yscaleCap), 
             annotations=list(text=HTML(paste("Baseline: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," dias <br><br>Intervenção: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1), " dias")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.5, align="left")
    )
    
    p
    
  })
  
  # Mostrar os valores de taxa de parâmetros utilizando uma tabela HTML
  output$ParameterTable <-renderTable(
    formattedModelParameters(), hover = T,bordered = T,striped = F, digits=3
  )
  
  
  formattedModelParameters <- reactive({
    
    ParamStruct=GetModelParams(input)
    pModel=ParamStruct$pModel
    N=ParamStruct$N
    pModel.df=data.frame(as.list(pModel))
    pModel.df$N=N
    
    #Se infecção assintomática for permitida
    if(input$AllowAsym=="Yes"){
      pModel.df$b0=pModel.df$b0*N
      names(pModel.df)[names(pModel.df)=="b0"] <- "b0*N"
    }else{
      pModel.df$b0=NULL
      pModel.df$f=NULL
      pModel.df$g0=NULL
    }
    
    # Se infecção pré-sintomática for permitida
    if(input$AllowPresym=="Yes"){
      pModel.df$be=pModel.df$be*N
      names(pModel.df)[names(pModel.df)=="be"] <- "be*N"
    }else{
      pModel.df$be=NULL
      pModel.df$a1=NULL
      names(pModel.df)[names(pModel.df)=="a0"] <- "a"
    }
    
    pModel.df$b1=pModel.df$b1*N
    pModel.df$b2=pModel.df$b3*N
    pModel.df$b3=pModel.df$b3*N
    
    names(pModel.df)[names(pModel.df)=="b1"] <- "b1*N"
    names(pModel.df)[names(pModel.df)=="b2"] <- "b2*N"
    names(pModel.df)[names(pModel.df)=="b3"] <- "b3*N"
    
    if(input$AllowSeason=="Yes"){
      names(pModel.df)[names(pModel.df)=="seas.amp"] <- "Seasonal.Amplitude"
      names(pModel.df)[names(pModel.df)=="seas.phase"] <- "Seasonal.Phase"
    }else{
      pModel.df$seas.amp=NULL
      pModel.df$seas.phase=NULL
    }
    
    pModel.df=melt(pModel.df)
    colnames(pModel.df)[1]="Parameter"
    colnames(pModel.df)[2]="Value"
   
    pModel.df
    
  }) 
  
  # Mostrar a proporção inicial de casos de diferentes tipos utilizando uma tabela HTML
  output$RatioTable <-renderTable(
    formattedRatios(), hover = T,bordered = T,striped = F, digits=1
  )
  
  formattedRatios <- reactive({
    
    ParamStruct=GetModelParams(input)
    pModel=ParamStruct$pModel
    N=ParamStruct$N

    #r value and ratios
    r.out=Getr_SEIR(pModel,N)
    MaxEigenVector=r.out$MaxEigenVector
    MaxEigenVector=MaxEigenVector[1:length(MaxEigenVector)-1] #remove D:D
    
    ratios.df=data.frame(MaxEigenVector)
    colnames(ratios.df)[1]="Value"
    #ratios.df = subset(ratios.df, select=c(2,1))
    #
    ratios.df$Ratio=c("E0:D","E1:D","I0:D","I1:D","I2:D","I3:D","R:D")
    ratios.df = ratios.df[c(2,1)]
    ratios.df
    
    
  }) 
  
  # Mostrar o diagrama do modelo
  output$plot4 <- renderImage({
    filename <- normalizePath(file.path('./images',"model_diagram.png"))
    
    list(src = filename, height=200, width=500)
    
  }, deleteFile = FALSE)
  
  
  output$parameterDesc <- renderUI({
    tags$iframe(src="Parameters.html",width="100%",frameBorder="0",height="7000px")
  })
  
  output$Tutorial <- renderUI({
    tags$iframe(src="Tutorial.html",width="100%",frameBorder="0",height="5000px")
  })
  
  # Retornar a Razão de fatalidade de casos para o usuário conforme a fração de infecções graves é alterada
  
  output$CFR <- renderText({ 
    CFR=(input$ProbDeath/100)*(input$FracCritical)
    HTML(paste("<b> Razão de fatalidade de casos:</b>",CFR,"%"))
  })
  
  # ------------Definir os sliders/formulários que possuem valores dinâmicos baseados em outros sliders ----------------------
  
  #Puxar parâmetros de capacidade hospitalar padrão e criar sliders 
  output$HospBedper <- renderUI({
    numericInput("HospBedper","Total (a cada 1000 pessoas)",value = signif(hdata$HospBedper,digits=3), min = 0, step = 0.1)
  })
  output$HospBedOcc <- renderUI({
    numericInput("HospBedOcc","Ocupação (%)",value = signif(hdata$HospBedOcc,digits=3)*100, min = 0, max = 100, step = 0.1)
  })
  output$ICUBedper <- renderUI({
    numericInput("ICUBedper","Total (a cada 1000 pessoas)",value = signif(hdata$ICUBedper,digits=3), min = 0, step = 0.01)
  })
  output$ICUBedOcc <- renderUI({
    numericInput("ICUBedOcc","Ocupação (%)",value = signif(hdata$ICUBedOcc,digits=3)*100, min = 0, max = 100, step = 1)
  })
  output$IncFluOcc <- renderUI({
    numericInput("IncFluOcc","Ocupação elevada durante época de gripe sazonal (%)",value = signif(hdata$IncFluOcc,digits=3)*100, min = 0, max = 100, step = 1)
  })
  output$ConvVentCap <- renderUI({
    numericInput("ConvMVCap","Convencional",value = signif(hdata$ConvMVCap,digits=3), min = 0, step = 0.01)
  })
  output$ContVentCap <- renderUI({
    numericInput("ContMVCap","Contingência",value = signif(hdata$ContMVCap,digits=3), min = 0, step = 0.01)
  })
  output$CrisisVentCap <- renderUI({
    numericInput("CrisisMVCap","Crise",value = signif(hdata$CrisisMVCap,digits=3), min = 0, step = 0.01)
  })
  
  #garantir que fração de indivíduos em cada estágio de infecção somem 100%
  observeEvent(input$FracSevere,  {
    maxFracCritical=100-input$FracSevere
    updateSliderInput(session = session, inputId = "FracCritical", max = maxFracCritical)
  })
  
  #Garantir que a parte do período de incubação que leva a transmissão seja menor que o tempo de incubação total
  observeEvent(input$IncubPeriod,  {
    maxPresymPeriod=input$IncubPeriod
    updateSliderInput(session = session, inputId = "PresymPeriod", max = maxPresymPeriod)
  })
  
  #Garantir que intervenção não termine antes de começar, e não termine após tempo total de simulação
  #Fazer apenas para a aba de Intervenção, a aba de Capacidade vai copiar estes valores
  observeEvent(input$Tint,  {
    updateSliderInput(session = session, inputId = "Tend", min = input$Tint)
    #updateSliderInput(session = session, inputId = "TendC", min = input$Tint)
  })
  observeEvent(input$Tmax,  {
    updateSliderInput(session = session, inputId = "Tend", max = input$Tmax)
    #updateSliderInput(session = session, inputId = "TendC", max = input$Tmax)
    
    # if(input$Tmax<input$Tend){
    #   updateSliderInput(session = session, inputId = "Tend", value = input$Tmax)
    # }
    # if(input$Tmax<input$TendC){
    #   updateSliderInput(session = session, inputId = "TendC", value = input$Tmax)
    # }
    
  })
  
  #Atualizar sliders de intervenção na aba de capacidade para parear com a aba de intervenção
  observeEvent(input$Tint,  {
    updateSliderInput(session = session, inputId = "TintC", value = input$Tint)
  })
  observeEvent(input$Tend,  {
    updateSliderInput(session = session, inputId = "TendC", value = input$Tend)
  })
  observeEvent(input$s1,  {
    updateSliderInput(session = session, inputId = "s1C", value = input$s1)
  })
  observeEvent(input$s2,  {
    updateSliderInput(session = session, inputId = "s2C", value = input$s2)
  })
  observeEvent(input$s3,  {
    updateSliderInput(session = session, inputId = "s3C", value = input$s3)
  })
  observeEvent(input$s0,  {
    updateSliderInput(session = session, inputId = "s0C", value = input$s0)
  })
  
  #E vice versa
  
  observeEvent(input$TintC,  {
    updateSliderInput(session = session, inputId = "Tint", value = input$TintC)
  })
  observeEvent(input$TendC,  {
    updateSliderInput(session = session, inputId = "Tend", value = input$TendC)
  })
  observeEvent(input$s1C,  {
    updateSliderInput(session = session, inputId = "s1", value = input$s1C)
  })
  observeEvent(input$s2C,  {
    updateSliderInput(session = session, inputId = "s2", value = input$s2C)
  })
  observeEvent(input$s3C,  {
    updateSliderInput(session = session, inputId = "s3", value = input$s3C)
  })
  observeEvent(input$s0C,  {
    updateSliderInput(session = session, inputId = "s0", value = input$s0C)
  })

  # Resetar todos os parâmetros se o botão RESETAR for pressionado
  observeEvent(input$reset,{
    updateSliderInput(session,'IncubPeriod',value = 5)
    updateSliderInput(session,'DurMildInf',value = 6)
    updateSliderInput(session,'FracSevere',value = 15)
    updateSliderInput(session,'FracCritical',value = 6)
    updateSliderInput(session,'ProbDeath',value = 40)
    updateSliderInput(session,'DurHosp',value = 6)
    updateSliderInput(session,'TimeICUDeath',value = 8)
    updateSliderInput(session,'b1',value = 0.5)
    updateSliderInput(session,'b2',value = 0.1)
    updateSliderInput(session,'b3',value = 0.1)
    updateSliderInput(session,'N',value = 1000)
    updateSliderInput(session,'Tmax',value = 300)
    updateSliderInput(session,'InitInf',value = 1)
  })
   
}