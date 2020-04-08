
# coding=utf-8
import streamlit as st
import yaml

import plotly.express as px
from streamlit import caching

import model_description as md
import fontes as ft
import simulation as sm
from models import Logo

def main():
    #TODO adjust logo src
    pic = Logo.IMPULSO.value
    st.sidebar.image(pic, use_column_width=False, width=100, caption=None)
    page = st.sidebar.selectbox("Menu", ["COVID19 no seu Município","Descição do Modelo","Fontes"])

    if page == "Descição do Modelo":
        if __name__ == "__main__":
            md.main()

    elif page=="Fontes":
        if __name__ == "__main__":
            ft.main()
        
    elif page == "COVID19 no seu Município":        
          if __name__ == "__main__":
            sm.main()          
            
 
if __name__ == "__main__":
    main()
    

