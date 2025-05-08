from funcoes import *
import streamlit as st
import atexit, bcrypt

def main():
    # Resumindo sesion state
    sstate = st.session_state

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

        # Criando usuário administrador padrão
        with get_connection().cursor() as cursor:

            # Aqui eu apenas insiro o usuário padrão se ainda não existir um igual, ou seja, com o mesmo e-mail ou CPF (já que são valores únicos). A sintaxe é bem esquisita.
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen)
                SELECT %s, %s, %s, %s, %s, %s
                FROM DUAL
                WHERE NOT EXISTS (
                    SELECT 1 FROM usuarios WHERE email = %s OR cpf = %s
                )
                """,
                ("ADM", bcrypt.hashpw("adminSENAI2025".encode("utf-8"), bcrypt.gensalt()),
                "admin@admin", "00000000000", True, current_datetime(),
                "admin@admin", "00000000000")
            )

        # Adicionando outras variáveis no session state
        if "userinfo" not in sstate:
            sstate.userinfo = tuple()
        if "logged" not in sstate:
            sstate.logged = False
        
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
        if not sstate.logged: 
            used_group = unlogged_page_groups
        else:
            if sstate.userinfo[1]:
                used_group = admin_page_groups
            else:
                used_group = standard_page_groups

        # Mostrando usuário atual
        if(sstate.logged):
            with st.sidebar:
                st.write(f"Usuário: {sstate.userinfo[2]} :balloon:")


    nav = st.navigation(used_group)
    nav.run()

    # Colocando o comando de fechamento pra quando o aplicativo desligar
    atexit.register(close_connection)

if(__name__ == "__main__"):
    main()