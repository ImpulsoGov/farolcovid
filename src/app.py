
# coding=utf-8
import streamlit as st
import yaml

import plotly.express as px
from streamlit import caching

# Pages
import model_description as md
import team as tm
import simulation as sm
import data_analysis as anal
import central
import risk_description as rd
import rt_description as rt

def main():
    page = st.sidebar.radio("Menu", ["FarolCovid", "Análises", "Níveis de Risco","Estimando Ritmo de Contágio",  "Metodologia SimulaCovid", "Quem somos?"]) # "Central COVID19", 

    if page == "Metodologia SimulaCovid":
        if __name__ == "__main__":
            md.main()

    elif page == "FarolCovid":        
          if __name__ == "__main__":
            sm.main()    

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
    

