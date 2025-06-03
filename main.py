from back_functions import *
import streamlit as st
import atexit, bcrypt

def main():
    # Resumindo sesion state
    sstate = st.session_state

    # Criando variáveis para controlar primeira execução
    if "firstrun" not in sstate: 
        sstate.firstrun = True

    # Tentando conectar antes de carregar a página. Levanto um erro se não conseguir conectar.
    if sstate.firstrun:
        try:
            get_connection()
            close_connection()

        except Exception as e:
            st.write("Não foi possível conectar ao banco. Verifique se o banco está ativo e se o host está correto, e reinicie a página.")

            # escrevendo o erro
            st.header("Erro", divider="gray")
            st.write(e)

            # parando aqui
            st.stop()

        # Criando rodinha de carregamento
        with st.spinner("Carregando dados..."):
            
            # Criando as tabelas
            criar_tabelas()

            # Criando usuário administrador padrão com os dados do arquivo de configucação
            with open(os.path.join(CONFIG_DIR, "default_user_config.json"), "r") as f:
                default_user = json.load(f)
            
            # Inserindo usuário padrão
            try:
                get_connection().start_transaction()

                with get_connection().cursor() as cursor:

                    # Inserindo esses dados no usuário padrão. Se ele já existir, eu só atualizo ele.
                    cursor.execute(
                            """
                            INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen, enabled)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                nome = VALUES(nome),
                                senha = VALUES(senha),
                                cpf = VALUES(cpf),
                                admin = VALUES(admin),
                                createdwhen = VALUES(createdwhen),
                                enabled = VALUES(enabled)
                            """,
                            (default_user["name"], bcrypt.hashpw(default_user["password"].encode("utf-8"), bcrypt.gensalt()),
                            default_user["email"], default_user["cpf"], True, current_datetime(), True)
                    )

                    get_connection().commit()
                    
            except Error as e:
                get_connection().rollback()

                print(e)
                st.error("Ocorreu um erro ao cadastrar o usuário padrão. Veja o erro no terminal.")
            
            finally:
                close_connection()
                sstate.firstrun = False

    # Adicionando outras variáveis no session state
    if "userinfo" not in sstate:
        sstate.userinfo = tuple()
    if "logged" not in sstate:
        sstate.logged = False
    if "verified" not in sstate:
        sstate.verified = False
    
    # Páginas
    pages = {

        # Páginas básicas
        "inicial" : st.Page("paginas/home.py", title="Início"),

        # Páginas pós-login
        "equipamentos" : st.Page("paginas/equipamentos.py", title="Equipamentos"),
        "ferramentas" : st.Page("paginas/ferramentas.py", title="Ferramentas"),
        "registros" : st.Page("paginas/registros.py", title="Registros"),

        # Páginas de administrador
        "admin" : st.Page("paginas/admin.py", title="Admin")
    }

    # Páginas acessíveis
    unlogged_page_groups = {
        "Inicial" : [pages["inicial"]]
    }

    standard_page_groups = {
        "Inicial" : [pages["inicial"]],
        "Registros" : [pages["equipamentos"], pages["ferramentas"], pages["registros"]]
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
    
    # Usando um grupo reduzido se eu estiver no usuário padrão
    if sstate.logged:
        if sstate.userinfo[0] == 1:
            used_group = {
                "Inicial" : [pages["inicial"]],
                "Admin" : [pages["admin"]]
            }

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