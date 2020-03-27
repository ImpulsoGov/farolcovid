import streamlit as st
import pandas as pd

def main():
    st.write("""## Descrição e fontes para parâmetros de simulação
#### Estrutura do modelo
A estrutura básica do modelo é inspirada em muitos estudos sobre a progressão clínica natural da infecção por COVID-19. Para um bom resumo, consulte (Wu e McGoogan 2020). Os indivíduos infectados não desenvolvem sintomas graves imediatamente, mas passam primeiro pelas fases mais leves da infecção. Em alguns estudos, o que chamamos de infecções _leves_ são agrupadas em duas categorias diferentes, _leve_ e _moderada_, em que indivíduos com infecção _moderada_ apresentam sinais radiográficos de pneumonia leve. Esses casos _leves_ e _moderados_ ocorrem em proporções aproximadamente iguais (por exemplo, ver P. Yang et al. (2020)). Há algum debate sobre o papel da transmissão pré-sintomática (que ocorre no estágio exposto) e a infecção e transmissão assintomáticas do COVID-19. A versão atual do modelo não inclui esses efeitos.

#### Parâmetros do modelo dinâmico
O comportamento do modelo dinâmico é determinado por um conjunto de parâmetros de taxa, incluindo as taxas de transmissão $β_i$, a progressão classifica um e $p_i$, as taxas de recuperação $γ_i$ e a taxa de mortalidade $μ$. Embora essas taxas em si geralmente não sejam medidas diretamente nos estudos, outras quantidades mensuráveis podem ser usadas para recuperar esses parâmetros de taxa.

O tempo gasto na classe exposta é chamado de _período de incubação_ e geralmente é considerado igual ao tempo entre a exposição a uma fonte infectada e o desenvolvimento de sintomas. No modelo, o período médio de incubação é de $1 / a$.

O período infeccioso é o tempo durante o qual um indivíduo pode transmitir a outros. Em nosso modelo, há potencialmente três períodos infecciosos diferentes, ocorrendo durante cada estágio clínico da infecção ($I_1$,$I_2$,$I_3$) Precisamos saber a duração de cada uma dessas etapas. Acreditamos que é provável que um indivíduo seja mais infeccioso durante o estágio de infecção leve, quando ainda estaria na comunidade e se sentindo bem o suficiente para interagir com outros, mas no modelo também há a opção de transmissão nos outros estágios, por exemplo, transmissão de pacientes hospitalizados para seus profissionais de saúde. Em nível populacional, esperamos que a maior parte da transmissão ocorra a partir desses indivíduos com infecção leve, uma vez que a maioria dos pacientes não progride além desse estágio. Para o COVID-19, podemos estimar a duração do primeiro estágio de
a) a duração dos sintomas leves, b) o tempo desde o início dos sintomas até a hospitalização (por exemplo, progresso para o estágio grave) ou c) a duração do derramamento viral por escarro ou esfregaços na garganta, d) o intervalo serial entre o início dos sintomas em um caso índice e um caso secundário que eles infectam. No modelo, as quantidades a) -c) são iguais a $1 / (p_1 + γ_1)$, enquanto d) é $1 / a + (1/2) 1 / (p_1 + γ_1)$. Essas estimativas convergem em valores semelhantes para $p_1 + γ_1$. A probabilidade de progredir para o estágio grave é igual à proporção de todas as infecções que acabam sendo graves ou críticas e deve ser igual à combinação de parâmetros $p_1 / (p_1 + γ_1)$.

Indivíduos com infecção grave ($I_2$) requerem hospitalização. A duração das infecções graves, que podem ser relatadas como o tempo entre a internação e a recuperação de indivíduos que não progrediram para o estágio crítico, ou o tempo entre a internação e a internação na UTI (uma vez que casos críticos requerem cuidados no nível da UTI), para os parâmetros do modelo $1 / (p_2 + γ_2)$. Como não existem estimativas diretas dessa duração, utilizamos estimativas do tempo total desde o início dos sintomas até a admissão na UTI (por exemplo, duração combinada de infecção leve + grave) e subtraímos a duração inferida da infecção leve. Em seguida, usamos a probabilidade observada de progredir para infecção crítica, igual à proporção de infecções críticas para críticas + graves, que é igual a $p_2 / (p_2 + γ_2)$, para resolver separadamente $p_2$ e $γ_2$. No estágio crítico da infecção ($I_3$) Cuidados na UTI, geralmente com ventilação mecânica, são necessários. A duração deste estágio da infecção, p. o tempo entre a admissão na UTI e a recuperação ou morte é igual a $1 / (γ_3 + μ)$, mas nem sempre são relatados. Em vez disso, os estudos geralmente relatam o tempo total desde a internação até a morte, o que pode aproximar a soma da duração dos estágios grave e crítico. Assim, subtraindo a duração de $I_2$, a duração de $I_3$ pode ser estimado. A taxa de fatalidade de casos observados (CFR) descreve a fração de todos os indivíduos infectados sintomáticos que eventualmente morrem. Como os indivíduos precisam progredir para a infecção crítica para morrer, a probabilidade condicional de alguém na fase crítica morrer ou se recuperar é dada pelo CFR dividido pela fração de todas as infecções graves. Isso deve ser igual à combinação de parâmetros do modelo $μ / (γ_3 + μ)$.

A Tabela 1 resume as fontes de literatura que usamos para estimar os valores padrão para todos esses parâmetros do modelo. Os usuários podem escolher seus próprios valores com base em outros estudos ou contextos regionais específicos.""")
        
    data = [{'Quantidade': 'Período de incubação',
  'Parâmetro': '1/a',
  'Valor': '5 dias',
  'Fonte': '(Li et al. 2020 ; Linton et al. 2020; Lauer et al. 2020; Bi et al. 2020; Sanche et al. 2020)'},
 {'Quantidade': 'Proporção de infecções leves',
  'Parâmetro': 'γ1/(p1+γ1)',
  'Valor': '81%',
  'Fonte': '(Wu and McGoogan 2020; P. Yang et al. 2020; Liu et al. 2020)'},
 {'Quantidade': 'Duração de infecções leves',
  'Parâmetro': '1/(p1+γ1)',
  'Valor': '6 dias',
  'Fonte': 'Viral shedding: (Woelfel et al. 2020), Time from symptoms to hospitalization: (Sanche et al. 2020; Tindale et al. 2020)'},
 {'Quantidade': 'Proporção de infecções graves',
  'Parâmetro': 'γ1/(p1+γ1)',
  'Valor': '14%',
  'Fonte': '(Wu and McGoogan 2020; P. Yang et al. 2020)'},
 {'Quantidade': 'Tempo desde os sintomas até a internação na UTI',
  'Parâmetro': '-',
  'Valor': '10 dias',
  'Fonte': '(Huang et al. 2020; X. Yang et al. 2020; Liu et al. 2020)'},
 {'Quantidade': 'Duração da infecção grave',
  'Parâmetro': '1/(p2+γ2)',
  'Valor': '4 dias',
  'Fonte': '[Time from symptoms to ICU admit] - [Duration of mild infections]'},
 {'Quantidade': 'Proporção de infecções críticas',
  'Parâmetro': '% Severe\n×p2/(p2+γ2)',
  'Valor': '6%',
  'Fonte': '(Wu and McGoogan 2020; P. Yang et al. 2020; Liu et al. 2020)'},
 {'Quantidade': 'Tempo desde a internação até a morte',
  'Parâmetro': '-',
  'Valor': '14 dias',
  'Fonte': '(Sanche et al. 2020; Linton et al. 2020)'},
 {'Quantidade': 'Durante uma infecção crítica',
  'Parâmetro': '1/(μ+γ3)',
  'Valor': '10 dias',
  'Fonte': '[Time from hospital admit to death] - [Duration of severe infections]'},
 {'Quantidade': 'Razão de fatalidade de casos',
  'Parâmetro': '% Critical\n×μ/(μ+γ3)',
  'Valor': '2%',
  'Fonte': '(Wu and McGoogan 2020; Russell 2020; Riou et al. 2020; Baud et al. 2020)'}]
    df_param = pd.DataFrame(data)
    st.table(df_param)
        
    st.text('Tabela 1: Parâmetros estimados para progressão clínica do COVID-19 e fontes da literatura')
    st.write("""As taxas de transmissão são geralmente impossíveis de observar ou estimar diretamente. Em vez disso, esses valores podem ser recuperados observando a taxa de crescimento exponencial inicial ($r$) de uma epidemia e escolhendo taxas de transmissão que recriam essas observações. O crescimento dos surtos de COVID-19 variou muito entre as configurações e ao longo do tempo. Alguns valores relatados na literatura estão na Tabela 2. O cálculo automatizado em tempo real das taxas de crescimento para diferentes países está disponível no [CITE]. Os valores padrão para a simulação estão atualmente configurados para corresponder a uma situação com $r$ = [ADDDD]. Como padrão, assumimos que apenas $β1> 0$
  (por exemplo, sem transmissão hospitalar).""")
        
    data1=[{'Taxa de contagio r': 0.1,
  'Tempo de duplicação': 6.9,
  'Localização': 'Wuhan',
  'Datas': 'Early January',
  'Fonte': '(Li et al. 2020)'},
 {'Taxa de contagio r': 0.25,
  'Tempo de duplicação': 2.8,
  'Localização': 'Wuhan',
  'Datas': 'January',
  'Fonte': '(Zhao, Chen, and Small 2020)'},
 {'Taxa de contagio r': 0.3,
  'Tempo de duplicação': 2.3,
  'Localização': 'Wuhan',
  'Datas': 'January',
  'Fonte': '(Sanche et al. 2020)'},
 {'Taxa de contagio r': 0.5,
  'Tempo de duplicação': 1.4,
  'Localização': 'Itália',
  'Datas': '24 de Fev',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.17,
  'Tempo de duplicação': 4.1,
  'Localização': 'Itália',
  'Datas': '9 de Mar',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.3,
  'Tempo de duplicação': 2.3,
  'Localização': 'Irã',
  'Datas': '2 de Mar',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.5,
  'Tempo de duplicação': 1.4,
  'Localização': 'Espanha',
  'Datas': '29 de Fev',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.2,
  'Tempo de duplicação': 3.5,
  'Localização': 'Espanha',
  'Datas': '9 de Mar',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.2,
  'Tempo de duplicação': 3.5,
  'Localização': 'França',
  'Datas': '9 de Mar',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.2,
  'Tempo de duplicação': 3.5,
  'Localização': 'Coréia do Sul',
  'Datas': '24 de Fev',
  'Fonte': '(Abbott 2020)'},
 {'Taxa de contagio r': 0.5,
  'Tempo de duplicação': 1.4,
  'Localização': 'Reino Unido',
  'Datas': '2 de Mar',
  'Fonte': '(Abbott 2020)'}]
        
    df_tax = pd.DataFrame(data1)
    st.table(df_tax)
        
    st.text('Tabela 2: Taxas de crescimento precoce da epidemia observadas $r$ em diferentes configurações, juntamente com os tempos de duplicação correspondentes. Existem muitas outras configurações nas quais as taxas de crescimento agora estão próximas de zero.')
        
    st.write("""#### Parâmetros de capacidade do hospital
Um dos maiores perigos de uma epidemia generalizada de COVID-19 é a tensão que isso poderia causar aos recursos hospitalares, uma vez que indivíduos com infecção grave e crítica requerem cuidados hospitalares. O estágio crítico da infecção requer ventilação mecânica, que é o nível de cuidados na UTI. A infecção grave pode ser tratada em uma enfermaria hospitalar regular. Indivíduos com infecção leve não necessitam de hospitalização e podem se recuperar em casa sozinhos. No entanto, em muitos países, esses indivíduos também foram hospitalizados, provavelmente como uma maneira de isolá-los e reduzir a transmissão, além de monitorá-los quanto à progressão para estágios mais agressivos da doença.

Os parâmetros padrão de capacidade hospitalar são estimados para os EUA e expressos como recursos per capita. Os leitos hospitalares disponíveis (em enfermarias regulares ou no piso da UTI) dependem do número total de leitos existentes e do nível de ocupação. Durante a temporada de gripe (meses de inverno), os níveis de ocupação são geralmente mais altos. Relatamos o número de camas _disponíveis_ (por exemplo, desocupadas) de ambos os tipos (Tabela 3). Estudos na literatura de preparação para pandemia examinaram como a capacidade de fornecer ventilação mecânica durante um surto de patógeno respiratório poderia ser expandida além da capacidade tradicional do leito de UTI (também conhecida como _capacidade convencional_) usando ventiladores armazenados em estoque, equipe hospitalar não especializada e adaptação retroativa outros quartos de hospital (Ajao et al. 2015). Esses níveis de entrega expandidos são chamados de capacidade de _contingência_ e _crise_.""")
        
    data2=[{'Quantidade r': 'Leitos hospitalares',
  'Total': '900.000',
  'Por 1.000 pessoas': '2.8',
  'País': 'EUA',
  'Fonte': '(National Center for Health Statistics 2017)'},
 {'Quantidade r': 'Occupação',
  'Total': '66%',
  'Por 1.000 pessoas': '',
  'País': 'EUA',
  'Fonte': '(National Center for Health Statistics 2017)'},
 {'Quantidade r': 'Leitos de UTI',
  'Total': '80.000',
  'Por 1.000 pessoas': '0.26',
  'País': 'EUA',
  'Fonte': '(Critical Care Medicine (SCCM) 2010)'},
 {'Quantidade r': 'Ocupação',
  'Total': '68%',
  'Por 1.000 pessoas': '',
  'País': 'EUA',
  'Fonte': '(Critical Care Medicine (SCCM) 2010)'},
 {'Quantidade r': 'Aumento durante a temporada de gripe',
  'Total': '7%',
  'Por 1.000 pessoas': '',
  'País': 'EUA',
  'Fonte': '(Ajao et al. 2015)'},
 {'Quantidade r': 'Leitos hospitalares disponíveis',
  'Total': '264.000',
  'Por 1.000 pessoas': '0.82',
  'País': 'EUA',
  'Fonte': 'From above'},
 {'Quantidade r': 'Leitos de UTI disponíveis',
  'Total': '22.000',
  'Por 1.000 pessoas': '0.071',
  'País': 'EUA',
  'Fonte': 'From above'},
 {'Quantidade r': 'Capacidade de ventilação mecânica convencional',
  'Total': '20.000',
  'Por 1.000 pessoas': '0.062',
  'País': 'EUA',
  'Fonte': '(Ajao et al. 2015)'},
 {'Quantidade r': 'Capacidade de ventilação mecânica de contingência',
  'Total': '50.000',
  'Por 1.000 pessoas': '0.15',
  'País': 'EUA',
  'Fonte': '(Ajao et al. 2015)'},
 {'Quantidade r': 'Capacidade de ventilação mecânica crítica',
  'Total': '135.000',
  'Por 1.000 pessoas': '0.24',
  'País': 'EUA',
  'Fonte': '(Ajao et al. 2015)'}]
    df_capa_US = pd.DataFrame(data2)
    st.table(df_capa_US)
        
    data3=[{'Quantidade r': 'Leitos hospitalares',
  'Total': '426.388',
  'Por 1.000 pessoas': '1.95',
  'País': 'BR',
  'Fonte': '(Data SUS 2020)'},
 {'Quantidade r': 'Occupação',
  'Total': '75%',
  'Por 1.000 pessoas': '',
  'País': 'BR',
  'Fonte': '(ANS 2012)'},
 {'Quantidade r': 'Leitos de UTI',
  'Total': '41.741 Totais\n28.638 Adultos',
  'Por 1.000 pessoas': '0.137',
  'País': 'BR',
  'Fonte': '(PEBMed 2018)'},
 {'Quantidade r': 'Ocupação',
  'Total': '75%',
  'Por 1.000 pessoas': '',
  'País': 'BR',
  'Fonte': '(ANS 2012)'},
 {'Quantidade r': 'Aumento durante a temporada de gripe',
  'Total': '10%',
  'Por 1.000 pessoas': '',
  'País': 'BR',
  'Fonte': '(ANS 2012)'}]
    df_capa_BR = pd.DataFrame(data3)
    st.table(df_capa_BR)
        
    st.text('Tabela 3. Capacidade hospitalar. Os valores são apenas para camas de adultos.')
        
    st.write("""### Referências
        
**Parâmetros Brasil:**

Federação Brasileira de Hospitais. 2019. "Cenário dos Hospitais Brasileiros 2019" http://fbh.com.br/wp-content/uploads/2019/05/CenarioDosHospitaisNoBrasil2019_10maio2019_web.pdf
Data SUS. 2020. "CNES - RECURSOS FÍSICOS - HOSPITALAR - LEITOS DE INTERNAÇÃO - BRASIL" http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/leiintbr.def
Portal PEDMed. 2018. "Brasil tem 2 leitos de UTI para cada 10 mil habitantes" https://pebmed.com.br/brasil-tem-2-leitos-de-uti-para-cada-10-mil-habitantes/
ANS. 2012. "Taxa de Ocupação Operacional Geral" http://www.ans.gov.br/images/stories/prestadores/E-EFI-01.pdf

**Simulador, parâmetros e modelo:**

Abbott, Sam. 2020. “Temporal Variation in Transmission During the COVID-19 Outbreak.” CMMID Repository. https://cmmid.github.io/topics/covid19/current-patterns-transmission/global-time-varying-transmission.html.

Ajao, Adebola, Scott V. Nystrom, Lisa M. Koonin, Anita Patel, David R. Howell, Prasith Baccam, Tim Lant, Eileen Malatino, Margaret Chamberlin, and Martin I. Meltzer. 2015. “Assessing the Capacity of the Healthcare System to Use Additional Mechanical Ventilators During a Large-Scale Public Health Emergency (PHE).” Disaster Medicine and Public Health Preparedness 9 (6): 634–41. https://doi.org/10.1017/dmp.2015.105.

Baud, David, Xiaolong Qi, Karin Nielsen-Saines, Didier Musso, Leo Pomar, and Guillaume Favre. 2020. “Real Estimates of Mortality Following COVID-19 Infection.” The Lancet Infectious Diseases 0 (0). https://doi.org/10.1016/S1473-3099(20)30195-X.

Bi, Qifang, Yongsheng Wu, Shujiang Mei, Chenfei Ye, Xuan Zou, Zhen Zhang, Xiaojian Liu, et al. 2020. “Epidemiology and Transmission of COVID-19 in Shenzhen China: Analysis of 391 Cases and 1,286 of Their Close Contacts.” medRxiv, March, 2020.03.03.20028423. https://doi.org/10.1101/2020.03.03.20028423.

Critical Care Medicine (SCCM), Society of. 2010. “SCCM Critical Care Statistics.” https://sccm.org/Communications/Critical-Care-Statistics.

Huang, Chaolin, Yeming Wang, Xingwang Li, Lili Ren, Jianping Zhao, Yi Hu, Li Zhang, et al. 2020. “Clinical Features of Patients Infected with 2019 Novel Coronavirus in Wuhan, China.” The Lancet 395 (10223): 497–506. https://doi.org/10.1016/S0140-6736(20)30183-5.

Lauer, Stephen A., Kyra H. Grantz, Qifang Bi, Forrest K. Jones, Qulu Zheng, Hannah Meredith, Andrew S. Azman, Nicholas G. Reich, and Justin Lessler. 2020. “The Incubation Period of 2019-nCoV from Publicly Reported Confirmed Cases: Estimation and Application.” medRxiv, February, 2020.02.02.20020016. https://doi.org/10.1101/2020.02.02.20020016.

Li, Qun, Xuhua Guan, Peng Wu, Xiaoye Wang, Lei Zhou, Yeqing Tong, Ruiqi Ren, et al. 2020. “Early Transmission Dynamics in Wuhan, China, of Novel Coronavirus-Infected Pneumonia.” New England Journal of Medicine 0 (0): null. https://doi.org/10.1056/NEJMoa2001316.

Linton, Natalie M., Tetsuro Kobayashi, Yichi Yang, Katsuma Hayashi, Andrei R. Akhmetzhanov, Sung-mok Jung, Baoyin Yuan, Ryo Kinoshita, and Hiroshi Nishiura. 2020. “Incubation Period and Other Epidemiological Characteristics of 2019 Novel Coronavirus Infections with Right Truncation: A Statistical Analysis of Publicly Available Case Data.” Journal of Clinical Medicine 9 (2): 538. https://doi.org/10.3390/jcm9020538.

Liu, Jingyuan, Yao Liu, Pan Xiang, Lin Pu, Haofeng Xiong, Chuansheng Li, Ming Zhang, et al. 2020. “Neutrophil-to-Lymphocyte Ratio Predicts Severe Illness Patients with 2019 Novel Coronavirus in the Early Stage.” medRxiv, February, 2020.02.10.20021584. https://doi.org/10.1101/2020.02.10.20021584.

National Center for Health Statistics. 2017. “Table 89. Hospitals, Beds, and Occupancy Rates, by Type of Ownership and Size of Hospital: United States, Selected Years 1975-2015.”

Riou, Julien, Anthony Hauser, Michel J. Counotte, and Christian L. Althaus. 2020. “Adjusted Age-Specific Case Fatality Ratio During the COVID-19 Epidemic in Hubei, China, January and February 2020.” medRxiv, March. https://doi.org/10.1101/2020.03.04.20031104.

Russell, Timothy W. 2020. “Estimating the Infection and Case Fatality Ratio for COVID-19 Using Age-Adjusted Data from the Outbreak on the Diamond Princess Cruise Ship.” CMMID Repository. https://cmmid.github.io/topics/covid19/severity/diamond_cruise_cfr_estimates.html.

Sanche, Steven, Yen Ting Lin, Chonggang Xu, Ethan Romero-Severson, Nick Hengartner, and Ruian Ke. 2020. “The Novel Coronavirus, 2019-nCoV, Is Highly Contagious and More Infectious Than Initially Estimated.” medRxiv, February, 2020.02.07.20021154. https://doi.org/10.1101/2020.02.07.20021154.

Tindale, Lauren, Michelle Coombe, Jessica E. Stockdale, Emma Garlock, Wing Yin Venus Lau, Manu Saraswat, Yen-Hsiang Brian Lee, et al. 2020. “Transmission Interval Estimates Suggest Pre-Symptomatic Spread of COVID-19.” medRxiv, March, 2020.03.03.20029983. https://doi.org/10.1101/2020.03.03.20029983.

Woelfel, Roman, Victor Max Corman, Wolfgang Guggemos, Michael Seilmaier, Sabine Zange, Marcel A. Mueller, Daniela Niemeyer, et al. 2020. “Clinical Presentation and Virological Assessment of Hospitalized Cases of Coronavirus Disease 2019 in a Travel-Associated Transmission Cluster.” medRxiv, March, 2020.03.05.20030502. https://doi.org/10.1101/2020.03.05.20030502.

Wu, Zunyou, and Jennifer M. McGoogan. 2020. “Characteristics of and Important Lessons from the Coronavirus Disease 2019 (COVID-19) Outbreak in China: Summary of a Report of 72 314 Cases from the Chinese Center for Disease Control and Prevention.” JAMA, February. https://doi.org/10.1001/jama.2020.2648.

Yang, Penghui, Yibo Ding, Zhe Xu, Rui Pu, Ping Li, Jin Yan, Jiluo Liu, et al. 2020. “Epidemiological and Clinical Features of COVID-19 Patients with and Without Pneumonia in Beijing, China.” medRxiv, March, 2020.02.28.20028068. https://doi.org/10.1101/2020.02.28.20028068.

Yang, Xiaobo, Yuan Yu, Jiqian Xu, Huaqing Shu, Jia’an Xia, Hong Liu, Yongran Wu, et al. 2020. “Clinical Course and Outcomes of Critically Ill Patients with SARS-CoV-2 Pneumonia in Wuhan, China: A Single-Centered, Retrospective, Observational Study.” The Lancet Respiratory Medicine 0 (0). https://doi.org/10.1016/S2213-2600(20)30079-5.

Zhao, Qingyuan, Yang Chen, and Dylan S. Small. 2020. “Analysis of the Epidemic Growth of the Early 2019-nCoV Outbreak Using Internationally Confirmed Cases.” medRxiv, February, 2020.02.06.20020941. https://doi.org/10.1101/2020.02.06.20020941.""")