
# coding=utf-8
import streamlit as st
import yaml

import plotly.express as px
from streamlit import caching

# Pages
import pages.model_description as md
import pages.team as tm
import pages.simulacovid as sm
import pages.data_analysis as anal
import pages.farolcovid as fc
import pages.risk_description as rd
import pages.rt_description as rt

def main():
    page = st.sidebar.radio("Menu", ["FarolCovid", "Análises", "Níveis de Risco","Estimando Ritmo de Contágio",  "Metodologia SimulaCovid", "Quem somos?"]) # "Central COVID19", 

    if page == "Metodologia SimulaCovid":
        if __name__ == "__main__":
            md.main()

    elif page == "FarolCovid":        
          if __name__ == "__main__":
            fc.main()    

    elif page == "Análises": 
          if __name__ == "__main__":
            anal.main()

    elif page == "Quem somos?":        
          if __name__ == "__main__":
            tm.main()    

    elif page == "Níveis de Risco": 
          if __name__ == "__main__":
            rd.main()

    elif page == "Estimando Ritmo de Contágio": 
          if __name__ == "__main__":
            rt.main()  
            
 
if __name__ == "__main__":
    main()
    

