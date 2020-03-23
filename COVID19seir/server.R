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
    
    #reformatar dados para plotar
    out.df2=rename(out.df, c(S="Suscetíveis",E="Expostos", I1="Infectados.Leves", I2="Infectados.Graves", 
                             I3="Infectados.Críticos", R="Recuperados", D="Falecidos"))
    out=melt(out.df,id="time")
    out2=melt(out.df2,id="time")
    out$variableName=out2$variable
    out$variableLegend = paste0(out$variableName,' (',out$variable,')')
    out$variableLegend = factor(out$variableLegend, levels = unique(out[["variableLegend"]]))
    
    #plot
    p=plot_ly(data = out, x=~time, y=~value, color=~variableLegend, type='scatter', mode='lines')

    p=layout(p,xaxis=list(title="Tempo desde introdução (dias)"),yaxis=list(title=paste("Número a cada",formatC(N,big.mark=",",format="f",digits=0),"pessoas"),type=input$yscale),
             annotations=list(text=HTML(paste("R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," dias")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="center",y=0.4, align="left"))

  })
  
  #Plotar curso temporal com uma intervenção
  
  output$plotInt = renderPlotly({
    
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
      
    }else if(input$VarShowInt=="Casos"){
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
    outAll.df=rbind(out.df,outInt.df) #combina padrão e intervenção
    outAll.sub=subset(outAll.df, select=c("time","value","Intervention")) # selecionar apenas coluna do caso
    outAll.sub$Intervention=factor(outAll.sub$Intervention) # definir intervenção como um fator
    outAll.sub=outAll.sub[with(outAll.sub,order(Intervention,time)),]
    
    
    p=plot_ly(data = outAll.sub, x=~time, y=~value, color=~Intervention, type='scatter', mode='lines',colors=c("#a50f15","#fc9272"))
    
    p=layout(p,xaxis=list(title="Tempo desde introdução (dias)"),yaxis=list(title=paste("Número a cada", formatC(N,big.mark=",",format="f",digits=0),"pessoas"),type=input$yscaleInt),
             annotations=list(text=HTML(paste("Padrão: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," dias <br><br>Intervenção: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1)," dias")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.5, align="left")
             )
    
  })
  
  output$plotCap = renderPlotly({
    
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
      outInt.df$value=outInt.df[,input$VarShowInt]
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
      out.df$value=rowSums(out.df[,c("I1","I2","I3")]) # create observed variable
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
             annotations=list(text=HTML(paste("Padrão: <br>R", tags$sub(0),'=',format(Ro,nsmall=1)," <br>r =", format(r,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTime,digits=1)," dias <br><br>Intervenção: <br>R", tags$sub(0),'=',RoInt,"<br>r =", format(rInt,digits=2)," por dia <br>T",tags$sub(2)," = ",format(DoublingTimeInt,digits=1), " dias")),
                              showarrow=FALSE,xref="paper",xanchor="left",x=1.05, yref="paper", yanchor="top",y=0.5, align="left")
    )
    
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
    
    pModel.df$b1=pModel.df$b1*N
    pModel.df$b2=pModel.df$b3*N
    pModel.df$b3=pModel.df$b3*N
    names(pModel.df)[names(pModel.df)=="b1"] <- "b1*N"
    names(pModel.df)[names(pModel.df)=="b2"] <- "b2*N"
    names(pModel.df)[names(pModel.df)=="b3"] <- "b3*N"
    
    pModel.df=melt(pModel.df)
    colnames(pModel.df)[2]="value (/day)"
    pModel.df
    
  }) 
  
  # Mostrar o diagrama do modelo
  output$plot4 <- renderImage({
    filename <- normalizePath(file.path('./images',"model_diagram.png"))
    
    list(src = filename, height=200, width=500)
    
  }, deleteFile = FALSE)
  
  # 
  url = a("Alison Hill", href="https://github.com/alsnhll/SEIR_COVID19")
  url2 = a("GitHub", href="https://github.com/alsnhll/SEIR_COVID19_BR")
  url3 = a("estudo", href="http://covid19.cappralab.com/")
  output$tab = renderUI({
    tagList("Este app é uma adaptação da Cappra Institute for Data Science baseada no modelo criado por ", url,". Os códigos deste simulador estão no ", url2," e possuem uma versão em Python usando Streamlit e outra em R usando Shiny. Contate Eduardo Santos em eduardo@cappra.com.br em caso de perguntas. Agradecimento para Alison Hill que desenvolveu a ferramenta inicial em R, Guilherme Machado e Caetano Slaviero que auxiliaram na tradução e codificação da versão em Python e também a todo o time da Cappra Institute for Data Science pelas pesquisas desenvolvidas. Quer saber mais sobre o COVID-19, confira nosso ", url3,".")

  })
  
  output$parameterDesc <- renderUI({
    tags$iframe(src="Parameters.nb.html",width="100%",frameBorder="0",height="5000px")
  })
  
  # Retornar a Razão de fatalidade de casos para o usuário conforme a $ de infecções graves é alterada
  
  output$CFR <- renderText({ 
    CFR=(input$ProbDeath/100)*(input$FracCritical)
    HTML(paste("<b> Razão de fatalidade de casos:</b>",CFR,"%"))
  })
  
  # ------------Definir os sliders/formulários que possuem valores dinâmicos baseados em outros sliders ----------------------
  
  output$N <- renderText({ 
    N=round(10^(input$LogN))
    HTML(paste("<b> N = </b>",formatC(N,big.mark=",",format="f",digits=0),""))
  })
  
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
    numericInput("CrisisMVCap","Emergência",value = signif(hdata$CrisisMVCap,digits=3), min = 0, step = 0.01)
  })
  
  #garantir que fração de indivíduos em cada estágio de infecção somem 100%
  observeEvent(input$FracSevere,  {
    maxFracCritical=100-input$FracSevere
    updateSliderInput(session = session, inputId = "FracCritical", max = maxFracCritical)
  })
  
  #Garantir que intervenção não termine antes de começar, e não termine após tempo total de simulação
  observeEvent(input$Tint,  {
    updateSliderInput(session = session, inputId = "Tend", min = input$Tint)
    updateSliderInput(session = session, inputId = "TendC", min = input$Tint)
  })
  observeEvent(input$Tmax,  {
    updateSliderInput(session = session, inputId = "Tend", max = input$Tmax)
    updateSliderInput(session = session, inputId = "TendC", max = input$Tmax)
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

  # Resetar todos os parâmetros se o botão RESETAR for pressionado
  observeEvent(input$reset,{
    updateSliderInput(session,'IncubPeriod',value = 5)
    updateSliderInput(session,'DurMildInf',value = 6)
    updateSliderInput(session,'FracSevere',value = 15)
    updateSliderInput(session,'FracCritical',value = 5)
    updateSliderInput(session,'ProbDeath',value = 40)
    updateSliderInput(session,'DurHosp',value = 4)
    updateSliderInput(session,'TimeICUDeath',value = 10)
    updateSliderInput(session,'b1',value = 0.33)
    updateSliderInput(session,'b21',value = 0)
    updateSliderInput(session,'b31',value = 0)
    updateSliderInput(session,'LogN',value = 3)
    updateSliderInput(session,'Tmax',value = 300)
    updateSliderInput(session,'InitInf',value = 1)
  })
   
}