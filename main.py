from funcoes import *
import streamlit as st
import atexit

def main():
    # Resumindo sesion state
    sstate = st.session_state

    # Definindo tamanho máximo de arquivo
    
    # Tentando conectar antes de carregar a página. Levanto um erro se não conseguir conectar.
    try:
        get_connection()
    except Exception as e:
        st.write("Não foi possível conectar ao banco em localhost:3306. Verifique se a conexão está aberta, e reinicie a página.")

        # escrevendo o erro
        st.header("Erro", divider="gray")
        st.write(e)

        # parando aqui
        st.stop()

    # Criando rodinha de carregamento
    with st.spinner("Carregando página..."):
        
        # Criando as tabelas
        criar_tabelas()

        # Adicionando outras variáveis no session state
        if "logged" not in sstate:
            sstate.logged = dict(user=None, admin=None)
        
        # Páginas
        pages = {

            # Páginas básicas
            "inicial" : st.Page("paginas/home.py", title="Início"),

            # Páginas pós-login
            "equipamentos" : st.Page("paginas/equipamentos.py", title="Equipamentos"),

            # Páginas de administrador
            "admin" : st.Page("paginas/admin.py", title="Admin")
        }

        # Páginas acessíveis
        unlogged_page_groups = {
            "Inicial" : [pages["inicial"]]
        }

        standard_page_groups = {
            "Inicial" : [pages["inicial"]],
            "Registros" : [pages["equipamentos"]]
        }

        admin_page_groups = standard_page_groups.copy() # Crio uma cópia das páginas padrão para adicionar as novas
        admin_page_groups.update(
            {
                "Administrador" : [pages["admin"]]
            }
        )

        # Vendo qual grupo de páginas utilizar
        used_group = None
        if not is_logged(sstate["logged"]): 
            used_group = unlogged_page_groups
        else:
            if sstate["logged"].get("admin"):
                used_group = admin_page_groups
            else:
                used_group = standard_page_groups

    nav = st.navigation(used_group)
    nav.run()

    # Colocando o comando de fechamento pra quando o aplicativo desligar
    atexit.register(close_connection)

if(__name__ == "__main__"):
    main()