
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

def main():
    page = st.sidebar.radio("Menu", ["COVID19 no seu Município", "Metodologia","Análises", "Quem somos?"])

    if page == "Metodologia":
        if __name__ == "__main__":
            md.main()

    elif page == "COVID19 no seu Município":        
          if __name__ == "__main__":
            sm.main()    

    elif page == "Análises": 
          if __name__ == "__main__":
            anal.main()

    elif page == "Quem somos?":        
          if __name__ == "__main__":
            tm.main()               
            
 
if __name__ == "__main__":
    main()
    

