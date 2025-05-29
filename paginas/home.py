import streamlit as st
from back_functions import *

# Salvando session state em outra variável
sstate = st.session_state

# Função para abrir o dialog de mudar senha
def open_set_pass_dialog(user):
    
    # Vendo se o usuário existe
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM usuarios WHERE email = %s OR cpf = %s)", (user, user))
        if cursor.fetchone()[0]: set_password_dialog(user)

# Título (centralizado com CSS)
st.markdown("<h1 style='text-align: center;'>Página Inicial</h1>", unsafe_allow_html=True)
st.divider()

if(sstate.logged):

    # Mostrando usuário logado
    st.markdown("<p style='display: flex; justify-content: center; margin: 0; color: gray;'>Logado em:</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='display: flex; justify-content: center; margin-bottom: 2rem;'>{sstate.userinfo[2]}</h1>", unsafe_allow_html=True)
    st.button("Sair", use_container_width=True, on_click=logout)
    
    if sstate.userinfo[0] == 1: # usuário ADMIN
        st.warning(":warning: Você está no usuário administrador padrão. Crie um usuário na aba \"Admin\" antes de utilizar as funções do site.")
else:

    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)

    with st.form("login", border=False):

        usuario = st.text_input("E-mail ou CPF", key="userlogin")
        senha = st.text_input("Senha", type="password", key="passlogin")

        cols = st.columns([.175, .3, .525])
        cols[1].caption("Se você ainda não tem uma senha, apenas insira seu usuário e clique no botão.")
        if cols[0].form_submit_button("Fazer login"):
            
            # Checando se esse usuário existe e, posteriormente, se tem uma senha
            with get_connection().cursor() as cursor:
                cursor.execute("SELECT senha FROM usuarios WHERE email = %s OR cpf = %s", (usuario, usuario))
                search = cursor.fetchone()
                has_password = bool(search[0]) if search else None

            # Faço as verificações todos os campos forem preenchidos
            if(has_password and all([usuario, senha])):
                
                # Verificando se é e-mail ou CPF
                if(check_email(usuario) or check_cpf(usuario)):
                    
                    # Tentando fazer login
                    if(login(usuario, senha)):
                        
                        # Buscando os dados desse usuário
                        with get_connection().cursor() as cursor:
                            cursor.execute("SELECT id, admin, nome FROM usuarios WHERE email = %s OR cpf = %s", (usuario, usuario))
                            search = cursor.fetchone()

                        # Guardando no session state
                        sstate.userinfo = search
                        sstate.logged = True

                        # Registrando isso
                        register_log(f"{sstate.userinfo[2]} fez login")
                        
                        # Mensagem de login
                        # adm_text = "" if not search[1] else " ADMINISTRADOR"
                        # st.success(f"Logado no usuário {search[2]}{adm_text}.")
                        # with st.spinner(""):
                        #     time.sleep(3)
                        
                        st.rerun()
                    
                    else:

                        st.error("Não foi possível fazer login. Verifique todas as informações.")

                # Se o dado estiver inválido, eu dou um erro
                else:
                    st.error("Seu e-mail ou CPF inserido é inválido. Verifique se as informações estão corretas.")
            
            elif has_password == False:
                open_set_pass_dialog(usuario)

            # Se faltarem campos a serem preenchidos, eu aviso o usuário
            elif not all([usuario, senha]):
                st.warning("Preencha todos os campos")

            elif has_password == None:
                st.error("Não foi possível fazer login. Verifique todas as informações.")
            
# Botão de sobre nós
# Criando o dialog de "sobre nós"
@st.dialog("Sobre Nós", width="large")
def about():
    st.markdown(
        """
        Nós somos Artur Vidal de Almeida e João Victor Apolinário de Freitas, alunos do curso de Técnico em Desenvolvimento de Sistemas, na escola SENAI Jairo Cândido. 
        
        Desenvolvemos este projeto com o objetivo de ajudar o curso de Técnico em Instrumentação Industrial. Nosso foco é fazer uma interface fácil de utilizar para registrar todos os seus equipamentos, manutenções e ferramentas, criando soluções que possam facilitar o aprendizado e melhorar a experiência dos alunos e professores.

        Este projeto foi pensado com dedicação, juntamente com os professores Fabiano Luizon Campos e Carlos Assis Silva Aguiar, direcionado ao professor Everton do curso de Instrumentação. Esperamos que nosso projeto possa ser útil para todos.

        Esse aplicativo é de uso público, então, sinta-se livre para utilizá-lo para as mais diversas situações.

        Obrigado por apoiar nosso trabalho! :balloon:
        """
    )

st.divider()
st.button("Sobre Nós", type="primary", on_click=about, use_container_width=True)