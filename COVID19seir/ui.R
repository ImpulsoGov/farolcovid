library(shiny)
library(shinyWidgets)
library(plotly)

fluidPage(
  titlePanel("Modelando a propagação do COVID-19 vs Capacidade Hospitalar"),
  hr(),
  p(div(HTML("Aviso: Esta simulação é voltada apenas para fins educacionais e de pesquisa e não é sua intenção ser uma ferramenta para tomada de decisões. Existem muitas incertezas e debates sobre os detalhes da infecção e transmissão do COVID-19  e existem muitas limitações a este modelo simples. Este trabalho é licenciado sob uma licença <a href=https://creativecommons.org/licenses/by-sa/4.0/> Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) </a>"))),
  
  
  sidebarLayout(
    
    sidebarPanel(
      
      setSliderColor(c(rep("#b2df8a", 3)), sliderId=c(8,9,10)),
      h4(div(HTML("<em>Definir parâmetros clínicos...</em>"))),
      sliderInput("IncubPeriod", "Duração do período de incubação", 0, 20, 5, step=0.5, post = " dias"),
      sliderInput("DurMildInf", "Duração de infecções leves", 0, 20, 6, step=1, post = " dias"),
      sliderInput("FracSevere", "% de infecções que são graves", 0, 100, 15, step=1, pre="%"),
      sliderInput("FracCritical", "% de infecções que são críticas",0, 20, 5, step=1, pre="%"),
      #uiOutput("FracCriticalSlider"),
      #sliderInput("CFR", "Taxa de Mortalidade", 0, 100, 2, step=5, pre="%"),
      sliderInput("ProbDeath", "Taxa de mortalidade para infecções críticas", 0, 100, 40, step=1, pre="%"),
      htmlOutput("CFR"),
      br(),
      sliderInput("DurHosp", "Duração de infecção grave/hospitalização", 0, 10, 4, step=1, post = " dias"),
      sliderInput("TimeICUDeath", "Duração infecção crítica/estadia na UTI", 0, 30, 10, step=1, post = " dias"),
      hr(),
      h4(div(HTML("<em>Deifinir valores de transmissão...</em>"))),
      sliderInput("b1", div(HTML("Taxa de transmissão (infecções leves)")), 0, 3, 0.33, step=0.02),
      sliderInput("b21", div(HTML("Taxa de transmissão (infecções graves, relativas a leves)")),0, 2, 0, step=0.1),
      sliderInput("b31", div(HTML("Taxa de transmissão (infecções criticas, relativas a leves)")), 0, 2, 0, step=0.1),
      hr(),
      h4(div(HTML("<em>Definir valores de simulação...</em>"))),
      sliderInput("LogN", div(HTML("Tamanho populacional total (log10)")), 1, 9, 3, step=0.1),
      htmlOutput("N"),
      br(),
      numericInput("InitInf","# inicial de infectados:",value = 1, min = 1, step = 1),
      sliderInput("Tmax", div(HTML("Tempo máximo")),0, 1000, 300, step=10, post=" dias"),
      actionButton("reset", "Resetar tudo")
      
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
                              radioButtons("yscale", "Escala do eixo Y:",
                                           choices = list("Linear" = "linear","Log10" = "log"),inline=TRUE),
                              p(HTML("")),
                              p(HTML("<b>Instruções ao usuário:</b> O gráfico apresenta o número esperado de indivíduos ao longo do tempo que estão infectados, recuperados suscetíveis, ou mortos. Indivíduos infectados primeiro passam por um período de exposição/incubação onde eles são assintomáticos e não infecciosos, e então migram para um estágio sintomático e infeccioso classificado pelo status clínico de infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo pode ser encontrada na aba de Descrição do Modelo. O tamanho populacional, condições iniciais, e valores de parâmetros utilizados para simular a propagação da infecção podem ser especificados através dos sliders localizados no painel a esquerda. Valores padrões dos sliders são iguais a estimativas retiradas da literatura (ver aba Fontes). Para reiniciar aos valores padrões, clique no botão <em>Resetar tudo</em> localizado na parte inferior do painel. O gráfico é interativo: Passe o mouse por cima para receber valores, duplo-clique em uma curva na legenda para isolá-la, ou clique-único para removê-la. Arrastar sobre uma extensão permite dar zoom."))
                            )
                          )
                 ),
                 
                 tabPanel("Intervenção",
                          fluidPage(
                            fluidRow(
                              h3("Redução no # previsto de COVID-19 após intervenção"),
                              p(HTML("Simule a mudança na linha do tempo de casos de COVID-19 após aplicação de uma intervenção")),
                              plotlyOutput("plotInt"),
                              br(),
                              br(),
                              radioButtons("yscaleInt", "Y axis scale:",
                                           choices = list("Linear" = "linear","Log10" = "log"),inline=TRUE),
                              wellPanel(
                                h4(div(HTML("<em>Definir parâmetros de intervenção...</em>"))),
                                selectInput("VarShowInt",
                                            label = "Selecione a variável a ser mostrada:",
                                            choices = c("Suscetíveis (S)"="S", "Expostos (E)"="E", "Infecções leves (I1)"="I1", "Infecções graves (I2)"="I2", "Infecções críticas (I3)"="I3", "Recuperados (R)"="R", "Mortos (D)"="D", "Todos infectados (E+I1+I2+I3)"="Inf","Todos sintomáticos (I1+I2+I3)"="Cases","Todos hospitalizados (I2+I3)"="Hosp"),
                                            selected = c("I3")
                                ),
                                numericInput("Tint","Inicio da intervenção (dias):",value = 0, min = 0, step = 10),
                                numericInput("Tend","Termino da intervenção (dias):",value = 300, min = 0, step = 10),
                                p(HTML("<b>Tipo de intervenção: reduzir transmissão, </b> por exemplo via distanciamento social ou quarentena na comunidade (para aqueles com infecções leves) ou melhor isolamento e equipamento de proteção individual em hospitais (para aqueles com infecções mais graves). Transmissão de cada estágio clínico da infecção pode ser reduzido apenas se o usuário escolheu parâmetros de forma que esses estágios contribuam para a transmissão.")),
                                sliderInput("s1", "Redução em transmissão de infecções leves", 0, 100, 30, pre="%",step=1, animate=TRUE),
                                sliderInput("s2", "Redução em transmissão de infecções graves", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                sliderInput("s3", "Redução na taxa de transmissão de infecções críticas", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                radioButtons("RoundOne", "Arredondar valores ao inteiro mais próximo pós-intervenção?",
                                             choices = list("True" = "True","False" = "False"),inline=TRUE),
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
                              radioButtons("yscaleCap", "Y axis scale:",
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
                                  p(HTML(" <b> ICU beds: </b>")),
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
                                            selected = c("CasesCap")
                                ),
                                numericInput("TintC","Início da intervenção (dias):",value = 0, min = 0, step = 10),
                                numericInput("TendC","Término da intervenção (dias):",value = 300, min = 0, step = 10),
                                p(HTML("<b>Tipo de intervenção: reduzir transmissão, </b> por exemplo via distanciamento social ou quarentena na comunidade (para aqueles com infecções leves) ou melhor isolamento e equipamento de proteção individual em hospitais (para aqueles com infecções mais graves). Transmissão de cada estágio clínico da infecção pode ser reduzido apenas se o usuário escolheu parâmetros de forma que esses estágios contribuam para a transmissão.")),
                                sliderInput("s1", "Redução em transmissão de infecções leves", 0, 100, 30, pre="%",step=1, animate=TRUE),
                                sliderInput("s2", "Redução em transmissão de infecções graves", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                sliderInput("s3", "Redução na taxa de transmissão de infecções críticas", 0, 100, 0, pre="%",step=1, animate=TRUE),
                                radioButtons("RoundOne", "Arredondar valores ao inteiro mais próximo pós-intervenção?",
                                             choices = list("True" = "True","False" = "False"), inline=TRUE),
                              ),
                              p(HTML("<b>Instruções ao usuário:</b> O gráfico mostra o número esperado de indivíduos ao longo do tempo que estão infectados, recuperados, suscetíveis, ou mortos ao longo do tempo, com e sem intervenção. Indivíduos infectados primeiro passam por uma fase de classificação expostos/em incubação, onde eles são assintomáticos e nao infecciosos, e então migram para um estágio sintomático e infeccioso classificado pelo status clínico da infecção (leve, grave ou crítica). Uma descrição mais detalhada do modelo pode ser encontrada na aba Descrição do Modelo. O tamanho populacional, condições iniciais e valores de parâmetros utilizados para simular a propagação da infecção podem ser especificados através dos sliders localizados no painel a esquerda. Valores padrões dos sliders são iguais a estimativas retiradas da literatura (ver aba Fontes). A intensidade e timing da intervenção é controlada pelos sliders abaixo do plot. Para reiniciar aos valores padrões, clique no botão <em>Resetar tudo</em> localizado na parte inferior do painel. O gráfico é interativo: Passe o mouse por cima para receber valores, duplo-clique em uma curva na legenda para isolá-la, ou clique-único para removê-la. Arrastar sobre uma extensão permite dar zoom."))
                            )
                          )
                 ),

                 tabPanel("Descrição do Modelo", br(),
                          fluidRow(column(12,
                                          plotOutput("plot4", height=200),
                                          withMathJax(),
                                          includeMarkdown("SEIR.Rmd"),
                                          #h3("Equations"),br(),
                                          #helpText('An irrational number \\(\\sqrt{2}\\) and a fraction $$1-\\frac{1}{2}$$, $$a$$'),
                                          #includeMarkdown("SEIR.Rmd"),
                                          h3("Parâmetros de taxas do modelo dinâmico"),
                                          p(HTML("Esses parâmetros podem ser alterados utilizando os sliders nas outras abas. Os valores nessa tabela represantem os valores atuais selecionados via sliders. Note que as taxas de transmissão escolidas pelos sliders são sempre escaladas por \\(N\\), para que \\(\\beta*N\\) seja constante conforme \\(N\\) muda.")),
                                          tableOutput("ParameterTable"),br(),br(),
                          ))),
                 
                 tabPanel("Fontes",
                          fluidPage(
                            br(),
                            uiOutput("parameterDesc")
                          )),
                 
                 tabPanel("Código",
                          fluidPage(
                            br(),
                            uiOutput("tab")
                            
                          ))
                 
      )
      
    )
    
  )
  
)

