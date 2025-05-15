import streamlit as st
import time
from funcoes import *

# Salvando session state em outra variável
sstate = st.session_state

# Título (centralizado com CSS)
st.markdown("<h1 style='display: flex; justify-content: center;'>Página Inicial</h1>", unsafe_allow_html=True)
st.divider()

if(sstate.logged):
    st.markdown("<p style='display: flex; justify-content: center; margin: 0; color: gray;'>Logado em:</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='display: flex; justify-content: center; margin-bottom: 2rem;'>{sstate.userinfo[2]}</h1>", unsafe_allow_html=True)
    st.button("Sair", use_container_width=True, on_click=logout)
    
    if sstate.userinfo[0] == 1: # usuário ADMIN
        st.warning(":warning: Você está no usuário administrador padrão. Crie um usuário na aba \"Admin\" antes de utilizar as funções do site.")
else:
    with st.form("login", border=False):
        st.markdown("<h3 style='display: flex; justify-content: center;'>Login</h3>", unsafe_allow_html=True)

        usuario = st.text_input("E-mail ou CPF", key="userlogin")
        senha = st.text_input("Senha", type="password", key="passlogin")

        if st.form_submit_button("Fazer login"):

            # Faço as verificações todos os campos forem preenchidos
            if(all([usuario, senha])):

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
            # Se faltarem campos a serem preenchidos, eu aviso o usuário
            else:
                st.warning("Preencha todos os campos")

# Botão de sobre nós
# Criando o dialog de "sobre nós"
@st.dialog("Sobre Nós", width="large")
def about():
    st.markdown(
        """
        Nós somos Artur Vidal de Almeida e João Victor Apolinário de Freitas, alunos do curso de Técnico em Desenvolvimento de Sistemas. Juntos, desenvolvemos este projeto com o objetivo de ajudar o curso de Técnico em Instrumentação Industrial. Nosso foco é fazer uma interface fácil de utilizar para registrar todos os seus equipamentos, manutenções e ferramentas, criando soluções que possam facilitar o aprendizado e melhorar a experiência dos alunos e professores.

        Este projeto foi pensado com dedicação, juntamente com os professores Fabiano Luizon Campos e Carlos Assis Silva Aguiar, para o professor Everton do curso de Instrumentação. Esperamos que nosso projeto possa ser útil para todos.

        Obrigado por apoiar nosso trabalho! :balloon:
        """
    )

st.divider()
st.button("Sobre Nós", type="primary", on_click=about, use_container_width=True)