import streamlit as st
import utils
import os

def genHeader(active):
    """ 
    This is a function that returns the "Footer" session 
    
    """
    if os.getenv("IS_HEROKU") == "TRUE":
        urlpath = os.getenv("urlpath")
    elif os.getenv("IS_DEV") == "TRUE":
        urlpath = 'http://localhost:8501/'
    else:
        urlpath = 'https://farolcovid.coronacidades.org/'

    if active=="1":
        st.write(
            f"""
            <div class="conteudo" id="navbar">
            <a>&nbsp;</a>
			<a href="{urlpath}?page=FarolCovid">Início</a>
            <a class="active" href="{urlpath}?page=Modelos%2C+limita%C3%A7%C3%B5es+e+fontes">Modelos, limitações e fontes</a>
            <a href="{urlpath}?page=Quem+somos%3F">Quem somos?</a>
            <a href="{urlpath}?page=Estudo+Vacina%C3%A7%C3%A3o">Estudo Vacinação</a>
            <a href="{urlpath}?page=Vacin%C3%B4metro">Vacinômetro</a>
            </div>
            """,
        unsafe_allow_html=True,
        )
    elif active=="2":
        st.write(
            f"""
            <div class="conteudo" id="navbar">
            <a>&nbsp;</a>
			<a href="{urlpath}?page=FarolCovid">Início</a>
            <a href="{urlpath}?page=Modelos%2C+limita%C3%A7%C3%B5es+e+fontes">Modelos, limitações e fontes</a>
            <a class="active" href="{urlpath}?page=Quem+somos%3F">Quem somos?</a>
            <a href="{urlpath}?page=Estudo+Vacina%C3%A7%C3%A3o">Estudo Vacinação</a>
            <a href="{urlpath}?page=Vacin%C3%B4metro">Vacinômetro</a>
            </div>
            """,
        unsafe_allow_html=True,
        )
    elif active=="3":
        st.write(
            f"""
            <div class="conteudo" id="navbar">
			<a>&nbsp;</a>
            <a href="{urlpath}?page=FarolCovid">Início</a>
            <a href="{urlpath}?page=Modelos%2C+limita%C3%A7%C3%B5es+e+fontes">Modelos, limitações e fontes</a>
            <a href="{urlpath}?page=Quem+somos%3F">Quem somos?</a>
            <a class="active" href="{urlpath}?page=Estudo+Vacina%C3%A7%C3%A3o">Estudo Vacinação</a>
            <a href="{urlpath}?page=Vacin%C3%B4metro">Vacinômetro</a>
            </div>
        """,
        unsafe_allow_html=True,
        )
    elif active=="4":
        st.write(
            f"""
            <div class="conteudo" id="navbar">
			<a>&nbsp;</a>
            <a href="{urlpath}?page=FarolCovid">Início</a>
            <a href="{urlpath}?page=Modelos%2C+limita%C3%A7%C3%B5es+e+fontes">Modelos, limitações e fontes</a>
            <a href="{urlpath}?page=Quem+somos%3F">Quem somos?</a>
            <a href="{urlpath}?page=Estudo+Vacina%C3%A7%C3%A3o">Estudo Vacinação</a>
            <a class="active" href="{urlpath}?page=Vacin%C3%B4metro">Vacinômetro</a>
            </div>
        """,
        unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
