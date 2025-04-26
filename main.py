from funcoes import *
import streamlit as st
import atexit

def main():
    # Criando as tabelas
    criar_tabelas()

    # Resumindo sesion state
    sstate = st.session_state

    # Páginas
    pages = {

        # Páginas básicas
        "inicial" : st.Page("pages/home.py", title="Registros"),
        "sobre" : st.Page("pages/sobre.py", title="Sobre Nós"),

        # Páginas pós-login
        "equipamentos" : st.Page("pages/teste.py", title="Testes"),

        # Páginas de administrador
        "admin" : st.Page("pages/admin.py", title="Admin")
    }

    # Páginas acessíveis
    unlogged_page_groups = {
        "Inicial" : [pages["inicial"], pages["sobre"]]
    }

    standard_page_groups = {
        "Inicial" : [pages["inicial"], pages["sobre"]],
        "Registros" : [pages["equipamentos"]]
    }

    admin_page_groups = standard_page_groups.copy() # Crio uma cópia das páginas padrão para adicionar as novas
    admin_page_groups.update(
        {
            "Administrador" : [pages["admin"]]
        }
    )

    # Adicionando outras variáveis no session state
    if "logged" not in sstate:
        sstate.logged = dict(user=None, admin=None)

    # Vendo qual grupo de páginas utilizar
    used_group = None
    if not is_logged(sstate["logged"]): 
        used_group = unlogged_page_groups
    else:
        if sstate["logged"].get("admin"):
            used_group = admin_page_groups
        else:
            used_group = standard_page_groups
    
    try:
        nav = st.navigation(used_group)
        nav.run()
    except:
        print("Nenhum grupo encontrado")

    # Colocando o comando de fechamento pra quando o aplicativo desligar
    atexit.register(close_connection)

if(__name__ == "__main__"):
    main()