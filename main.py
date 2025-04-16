from funcoes import *
import streamlit as st

def main():
    criar_tabelas()

    # Páginas
    pages = {
        "inicial" : st.Page("pages/home.py", title="Registros"),
        "login" : st.Page("pages/login.py", title="Login"),
        "cadastro" : st.Page("pages/cadastro.py", title="Cadastro")
    }

    page_groups = {
        "Inicial" : [pages["inicial"], pages["cadastro"], pages["login"]]
    }

    # Adicionando variáveis no session state
    sstate = st.session_state
    if "user" not in sstate:
        sstate.user = None
    if "password" not in sstate:
        sstate.password = None

    nav = st.navigation(page_groups, position="hidden")
    nav.run()

if(__name__ == "__main__"):
    main()