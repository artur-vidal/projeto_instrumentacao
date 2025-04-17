from funcoes import *
import streamlit as st

def main():
    criar_tabelas()

    # Páginas
    pages = {
        "inicial" : st.Page("pages/home.py", title="Registros"),
        "teste" : st.Page("pages/teste.py", title="Testes")
    }

    page_groups = {
        "Inicial" : [pages["inicial"], pages["teste"]]
    }

    # Adicionando variáveis no session state
    sstate = st.session_state
    if "logged" not in sstate:
        sstate.logged = dict(user=None, password=None, admin=None)

    nav = st.navigation(page_groups, position="sidebar" if is_logged(sstate.logged) else "hidden")
    nav.run()

if(__name__ == "__main__"):
    main()