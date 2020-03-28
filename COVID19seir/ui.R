library(shiny)
library(shinyWidgets)
library(plotly)

fluidPage(
  titlePanel("Modelando a propagação do COVID-19 vs Capacidade Hospitalar"),
  hr(),
  p(div(HTML("Este app é uma adaptação da <b>Cappra Institute for Data Science</b> baseada no modelo criado por <b>Alison Hill</b> (ver aba Sobre). <b>Aviso</b>: Esta simulação é voltada apenas para fins educacionais e de pesquisa e não é sua intenção ser uma ferramenta para tomada de decisões. Existem muitas incertezas e debates sobre os detalhes da infecção e transmissão do COVID-19  e existem muitas limitações a este modelo simples. Este trabalho é licenciado sob uma licença <a href=https://creativecommons.org/licenses/by-sa/4.0/> Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) </a>"))),
  
  
  sidebarLayout(
    
    sidebarPanel(
      
      fluidRow(
        column(width=6,
               
               setSliderColor(c(rep("#b2df8a", 3)), sliderId=c(8,9,10)),
               h4(div(HTML("<em>Definir parâmetros clínicos...</em>"))),
               sliderInput("IncubPeriod", "Duração do período de incubação", 0, 20, 5, step=0.5, post = " dias"),
               sliderInput("DurMildInf", "Duração de infecções leves", 0, 20, 6, step=1, post = " dias"),
               sliderInput("FracSevere", "% de infecções que são graves", 0, 100, 15, step=1, pre="%"),
               sliderInput("DurHosp", "Duração de infecções graves/hospitalização", 0, 10, 6, step=1, post = " dias"),
               sliderInput("FracCritical", "% de infecções que são críticas",0, 20, 5, step=1, pre="%"),
               sliderInput("TimeICUDeath", "Duração de infecções críticas/estadia na UTI", 0, 30, 8, step=1, post = " dias"),
               sliderInput("ProbDeath", "Taxa de mortalidade para infecções críticas", 0, 100, 40, step=1, pre="%"),
               htmlOutput("CFR"),
               br(),
               #hr()
               
               ),
        column(width=6,
               
               h4(div(HTML("<em>Definir valores de transmissão...</em>"))),
               sliderInput("b1", div(HTML("Infecções leves")), 0, 3, 0.5, step=0.01, post="/dia"),
               sliderInput("b2", div(HTML("Infecções graves")),0, 3, 0.1, step=0.01, post="/dia"),
               sliderInput("b3", div(HTML("Infecções críticas")),0, 3, 0.1, step=0.01, post="/dia"),
               radioButtons("AllowSeason", "Permitir sazonalidade na transmissão?",
                            choices = list("Sim" = "Yes","Não" = "No"),inline=TRUE, selected="No"),
               conditionalPanel(
                 condition="input.AllowSeason == 'Yes'",
                 sliderInput("seas.amp", "Amplitude da sazonalidade", 0, 100, 0, step=10, pre="%"),
                 sliderInput("seas.phase", "Dia de pico transmissional (relativo a t=0)", -365, 365, 0, step=1, post = " dias"),
               ),
               radioButtons("AllowAsym", "Permitir infecções assintomáticas?",
                            choices = list("Sim" = "Yes","Não" = "No"),inline=TRUE,selected="No"),
               conditionalPanel(
                 condition="input.AllowAsym == 'Yes'",
                 sliderInput("FracAsym", "Fração de infecções que são assintomáticas", 0, 100, 30, step=1, pre="%"),
                 sliderInput("DurAsym", "Duração de infecções assintomáticas", 1, 20, 6, step=1, post = " dias"),
                 sliderInput("b0", div(HTML("Taxa de transmissão de assintomáticos")), 0, 3, 0.5, step=0.02, post="/dia"),
               ),
                      radioButtons("AllowPresym", "Permitir transmissão pré-sintomática?",
                                   choices = list("Sim" = "Yes","Não" = "No"),inline=TRUE, selected="No"),
               conditionalPanel(
                 condition="input.AllowPresym == 'Yes'",
                 sliderInput("PresymPeriod", "Tempo antes do surgimento de sintomas onde transmissão é possível", 0, 3, 2, step=0.5, post = " dias"), #Fazer reativo
                 sliderInput("be", div(HTML("Taxa de transmissão de pré-sintomáticos")),0, 3, 0.5, step=0.02, post="/dia"),
               ),
               hr(),

        )
      ),
      h4(div(HTML("<em>Definir valores de simulação...</em>"))),
      #sliderInput("LogN", div(HTML("Tamanho populacional total (log10)")), 1, 9, 3, step=0.1),
      #htmlOutput("N"),
      column(width=5,
             numericInput("N", div(HTML("Tamanho populacional:")), value=1000, max=10^10, min=1000, step=1000)
      ),
      column(width=5,
             numericInput("InitInf","Número inicial de infectados:",value = 1, min = 1, step = 1)
      ),
      #br(),
      sliderInput("Tmax", div(HTML("Tempo Máximo")),0, 1000, 300, step=10, post=" days"),
      actionButton("reset", "Resetar Tudo"),    
      width=5
    ),
    
    mainPanel(
      
      #p(div(HTML("Test")))
      navbarPage("Resultados:",
                 
                 tabPanel("Propagação",
                          fluidPage(
                            fluidRow(
                              
                              h3("Casos previstos de COVID-19 por desfecho clínico"),
                              p(HTML("Simule o curso natural de uma epidemia de COVID-19 em uma única população sem quaisquer intervenções.")),
                              
                              plotlyOutput("plot0"),
                              br(),
                              br(),
                              column(width=6,
                                     radioButtons("yscale", "Escala do eixo Y:",
                                                  choices = list("Linear" = "linear","Log10" = "log"),inline=TRUE)
                                     ),
                              column(width=6,
                                     radioButtons("PlotCombine", "Plotar total de infectados?",
                                                  choices = list("Sim" = "Yes","Não" = "No"),inline=TRUE, selected="No")
                              ),
                              br(),
                              p(HTML("<b>Instruções ao usuário:</b> O gráfico apresenta o número esperado de indivíduos ao longo do tempo que estão infectados, recuperados suscetíveis, ou mortos. Indivíduos infectados primeiro passam por um período de exposição/incubação onde eles são assintomáticos e não infecciosos, e então migram para um estágio sintomático e infeccioso classificado pelo status clínico de infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo pode ser encontrada na aba de Descrição do Modelo. O tamanho populacional, condições iniciais, e valores de parâmetros utilizados para simular a propagação da infecção podem ser especificados através dos sliders localizados no painel a esquerda. Valores padrões dos sliders são iguais a estimativas retiradas da literatura (ver aba Fontes). Para reiniciar aos valores padrões, clique no botão <em>Resetar tudo</em> localizado na parte inferior do painel. O gráfico é interativo: Passe o mouse por cima para receber valores, duplo-clique em uma curva na legenda para isolá-la, ou clique-único para removê-la. Arrastar sobre uma extensão permite dar zoom."))
                            )
                          )
                 ),
                 
                 tabPanel("Intervenção",
                          fluidPage(
                            fluidRow(
                              h3("Redução no número previsto de casos de COVID-19 após intervenção"),
                              p(HTML("Simule a mudança na linha do tempo de casos de COVID-19 após aplicação de uma intervenção")),
                              plotlyOutput("plotInt"),
                              br(),
                              br(),
                              radioButtons("yscaleInt", "Escala do eixo Y:",
                                           choices = list("Linear" = "linear","Log10" = "log"),inline=TRUE),
                              wellPanel(
                                h4(div(HTML("<em>Definir parâmetros de intervenção...</em>"))),
                                selectInput("VarShowInt",
                                            label = "Selecione a variável a ser mostrada:",
                                            choices = c("Suscetíveis (S)"="S", "Expostos (E)"="E", "Infecções leves (I1)"="I1", "Infecções graves (I2)"="I2", "Infecções críticas (I3)"="I3", "Recuperados (R)"="R", "Mortos (D)"="D", "Todos infectados (E + all I)"="Inf","Todos sintomáticos (I1+I2+I3)"="Cases","Todos hospitalizados (I2+I3)"="Hosp"),
                                            selected = c("Cases")
                                ),
                                column(width=6,
                                         numericInput("Tint","Início da intervenção (dias):",value = 0, min = 0, step = 10)
                                         ),
                                  column(width=6,
                                         numericInput("Tend","Término da intervenção (dias):",value = 300, min = 0, step = 10)
                                         ),
                                p(HTML("<b>Tipo de intervenção: reduzir transmissão, </b> por exemplo via distanciamento social ou quarentena na comunidade (para aqueles com infecções leves) ou melhor isolamento e equipamento de proteção individual em hospitais (para aqueles com infecções mais graves). Transmissão de cada estágio clínico da infecção pode ser reduzido apenas se o usuário escolheu parâmetros de forma que esses estágios contribuam para a transmissão.")),
                                sliderInput("s1", "Redução em transmissão de infecções leves", 0, 100, 30, pre="%",step=1, animate=TRUE),
                                sliderInput("s2", "Redução em transmissão de infecções graves", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                sliderInput("s3", "Redução na taxa de transmissão de infecções críticas", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                conditionalPanel(
                                  condition="input.AllowAsym == 'Yes' || input.AllowPresym == 'Yes' ",
                                  sliderInput("s0", "Redução na taxa de transmissão de infecções pré/assintomáticas ", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                ),
                                radioButtons("RoundOne", "Arredondar valores ao inteiro mais próximo pós-intervenção?",
                                             choices = list("True" = "Sim","False" = "Não"),inline=TRUE),
                              ),
                              p(HTML("<b>Instruções ao usuário:</b> O gráfico mostra o número esperado de indivíduos ao longo do tempo que estão infectados, recuperados, suscetíveis, ou mortos ao longo do tempo, com e sem intervenção. Indivíduos infectados primeiro passam por uma fase de classificação expostos/em incubação, onde eles são assintomáticos e nao infecciosos, e então migram para um estágio sintomático e infeccioso classificado pelo status clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo pode ser encontrada na aba Descrição do Modelo. O tamanho populacional, condições iniciais e valores de parâmetros utilizados para simular a propagação da infecção podem ser especificados através dos sliders localizados no painel a esquerda. Valores padrões dos sliders são iguais a estimativas retiradas da literatura (ver aba Fontes). A intensidade e timing da intervenção é controlada pelos sliders abaixo do plot. Para reiniciar aos valores padrões, clique no botão <em>Resetar tudo</em> localizado na parte inferior do painel. O gráfico é interativo: Passe o mouse por cima para receber valores, duplo-clique em uma curva na legenda para isolá-la, ou clique-único para removê-la. Arrastar sobre uma extensão permite dar zoom."))
                            )
                          )
                 ),
                 
                 tabPanel("Capacidade",
                          fluidPage(
                            fluidRow(
                              h3("Casos COVID-19 vs Capacidade Hospitalar"),
                              p(HTML("Simule casos previstos de COVID-19 vs a capacidade do sistema hospitalar de tratar destes. O tratamento necessário depende da gravidade da doença - indivíduos com infecções 'graves' necessitam de internação e indivíduos com infecções 'críticas' normalmente necessitam de cuidado a nível de UTI e ventilação mecânica.")),
                              plotlyOutput("plotCap"),
                              br(),
                              br(),
                              radioButtons("yscaleCap", "Escala eixo Y:",
                                           choices = list("Linear" = "linear","Log10" = "log"),inline=TRUE),
                              wellPanel(
                                h4(div(HTML("<em>Definir capacidade hospitalar...</em>"))),
                                p(HTML(" Os valores padrões são para os EUA e detalhes de suas fontes são dados na aba Fontes")),
                                #Sliders para capacidade hospitalar são reativos, pois eles puxam os valores padrões de um arquivo, de modo que são definidos no arquivo server.  
                                fluidRow(
                                  p(HTML(" <b> Leitos hospitalares totais: </b>")),
                                  column(width = 6,
                                         uiOutput("HospBedper")
                                  ),
                                  column(width = 6,
                                         uiOutput("HospBedOcc")
                                  ),
                                  p(HTML(" <b> Leitos de UTI: </b>")),
                                  column(width = 6,
                                         uiOutput("ICUBedper")
                                  ),
                                  column(width = 6,
                                         uiOutput("ICUBedOcc")
                                  ),
                                  column(width = 12,
                                         uiOutput("IncFluOcc")
                                  ),
                                  p(HTML(" <b> Ventiladores mecânicos: </b>")),
                                  column(width = 4,
                                         uiOutput("ConvVentCap")
                                  ),
                                  column(width = 4,
                                         uiOutput("ContVentCap")
                                  ),
                                  column(width = 4,
                                         uiOutput("CrisisVentCap")
                                  )
                                ),
                                ),
                              wellPanel(
                                h4(div(HTML("<em>Definir parâmetros de intervenção...</em>"))),
                                selectInput("VarShowCap",
                                            label = "Selecione a variável a ser apresentada:",
                                            choices = c("Infecções Críticas (I3) vs leitos UTI"="I3bed", "Infecções Críticas (I3) vs quantidade de ventiladores"="I3mv", "Infecções Graves + Críticas (I2+I3) vs Leitos Hospitalares"="Hosp", "Todos os casos sintomáticos (I1+I2+I3) vs Leitos Hospitalares"="CasesCap"),
                                            selected = c("Hosp")
                                ),
                                column(width=6,
                                       numericInput("TintC","Início da intervenção (dias):",value = 0, min = 0, step = 10)
                                ),
                                column(width=6,
                                       numericInput("TendC","Término da intervenção (dias):",value = 300, min = 0, step = 10)
                                ),
                                p(HTML("<b>Tipo de intervenção: reduzir transmissão, </b> por exemplo via distanciamento social ou quarentena na comunidade (para aqueles com infecções leves) ou melhor isolamento e equipamento de proteção individual em hospitais (para aqueles com infecções mais graves). Transmissão de cada estágio clínico da infecção pode ser reduzido apenas se o usuário escolheu parâmetros de forma que esses estágios contribuam para a transmissão.")),
                                sliderInput("s1C", "Redução na taxa de transmissão de infecções leves ", 0, 100, 30, pre="%",step=1, animate=TRUE),
                                sliderInput("s2C", "Redução na taxa de transmissão de infecções graves ", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                sliderInput("s3C", "Redução na taxa de transmissão de infecções críticas ", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                conditionalPanel(
                                  condition="input.AllowAsym == 'Yes' || input.AllowPresym == 'Yes' ",
                                  sliderInput("s0C", "Redução de transmissão de infecções pré/assintomáticas ", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                ),
                                radioButtons("RoundOneCap", "Arredondar valores ao inteiro mais próximo pós-intervenção?",
                                             choices = list("True" = "Sim","False" = "Não"), inline=TRUE),
                              ),
                              p(HTML("<b>Instruções ao usuário:</b> O gráfico mostra o número esperado de indivíduos ao longo do tempo que estão infectados, recuperados, suscetíveis, ou mortos ao longo do tempo, com e sem intervenção. Indivíduos infectados primeiro passam por uma fase de classificação expostos/em incubação, onde eles são assintomáticos e nao infecciosos, e então migram para um estágio sintomático e infeccioso classificado pelo status clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo pode ser encontrada na aba Descrição do Modelo. O tamanho populacional, condições iniciais e valores de parâmetros utilizados para simular a propagação da infecção podem ser especificados através dos sliders localizados no painel a esquerda. Valores padrões dos sliders são iguais a estimativas retiradas da literatura (ver aba Fontes). A intensidade e timing da intervenção é controlada pelos sliders abaixo do plot. Para reiniciar aos valores padrões, clique no botão <em>Resetar tudo</em> localizado na parte inferior do painel. O gráfico é interativo: Passe o mouse por cima para receber valores, duplo-clique em uma curva na legenda para isolá-la, ou clique-único para removê-la. Arrastar sobre uma extensão permite dar zoom."))
                            )
                          )
                 ),

                 tabPanel("Descrição do Modelo", br(),
                          fluidRow(column(12,
                                          withMathJax(),
                                          h2("Descrição do Modelo"),
                                          plotOutput("plot4", height=200),
                                          includeMarkdown("SEIR.Rmd"),
                                          #h3("Equações"),
                                          br(),
                                          h2("Saída"),
                                          h3("Parâmetros de taxas do modelo dinâmico"),
                                          p(HTML("Esses parâmetros podem ser alterados utilizando os sliders nas outras abas. Os valores nessa tabela represantem os valores atuais selecionados via sliders. Note que as taxas de transmissão escolidas pelos sliders são sempre escaladas por \\(N\\), para que \\(\\beta*N\\) seja constante conforme \\(N\\) muda.")),
                                          tableOutput("ParameterTable"),br(),
                                          h3("Razões de casos durante fase de crescimento inicial"),
                                          p(HTML("Estes valores são calculados baseados nos parâmetros atuais do modelo")),
                                          tableOutput("RatioTable"),br(),
                          ))),
                 
                 tabPanel("Fontes",
                          fluidPage(
                            br(),
                            uiOutput("parameterDesc")
                          )),
                 # tabPanel("Saída",
                 #          fluidPage(
                 #            br(),
                 #            h3("Parâmetros de taxas do modelo dinâmico"),
                 #            p(HTML("Esses parâmetros podem ser alterados utilizando os sliders nas outras abas. Os valores nessa tabela represantem os valores atuais selecionados via sliders. Note que as taxas de transmissão escolidas pelos sliders são sempre escaladas por \\(N\\), para que \\(\\beta*N\\) seja constante conforme \\(N\\) muda.")),
                 #            tableOutput("ParameterTable"),br(),br(),
                 #          )),
                 tabPanel("Tutorial",
                          fluidPage(
                            br(),
                            uiOutput("Tutorial")
                            #includeMarkdown("Tutorial.Rmd")
                          )),
                 
                 tabPanel("Sobre",
                          fluidPage(
                            br(),
                            includeMarkdown("About.Rmd")
                          ))
                 
      ),
      width=7
    )
    
  )
  
)

