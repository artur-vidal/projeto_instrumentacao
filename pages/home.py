import streamlit as st
from funcoes import *

# Salvando session state em outra variável
sstate = st.session_state

# Título
st.title("Página Inicial")

# Aba de cadastro
with st.expander("Cadastrar"):

    # Fazendo as áreas de input
    nome_c = st.text_input("Nome de usuário")
    senha_c = st.text_input("Senha")
    cpf_c = st.text_input("CPF (apenas números)")
    email_c = st.text_input("E-mail", placeholder="exemplo@exemplo.com")
    admin_c = st.checkbox("Administrador?")

    # Quando eu apertar o botão e checar se todos os campos estão preenchidos (menos Admin, esse não é necessário),
    # eu já tento adicionar o usuário após as checagens
    if(st.button("Cadastrar") and all([nome_c, senha_c, check_cpf(cpf_c), check_email(email_c)])):
        novo_usuario(nome_c, senha_c, cpf_c, email_c, admin_c)

# Aba de login
with st.expander("Login"):

    # Campos para pegar informações
    nome_l = st.text_input("Nome, e-mail ou CPF do usuário")
    senha_l = st.text_input("Senha", type="password")

    # Callback de login bem-sucedido
    def efetuar_login(nome, senha):
        if(login(nome, senha)):
            # Pegando o nome do usuário que eu acabei de logar
            cursor = get_connection().cursor()

            # Pegando o nome via nome, email ou cpf
            cursor.execute("SELECT nome, admin FROM usuarios WHERE nome = %s OR email = %s OR cpf = %s", (nome.upper(), check_email(nome), check_cpf(nome)))
            search = cursor.fetchone() # Pegando o usuário apenas

            # Pop-up de sucesso
            sstate.logged["user"] = search[0]
            sstate.logged["admin"] = search[1]

            # Fechando conexão
            cursor.close()
    
    if(st.button("Logar", on_click=efetuar_login, args=(nome_l, senha_l))):
        if(is_logged(sstate.logged)):
            adm_text = "" if not sstate.logged["admin"] else "ADMINISTRADOR "
            st.success(f"Entrou no usuário {sstate.logged["user"]} {adm_text}.")
        else:
            st.error("Não foi possível fazer login. Verifique se as informações inseridas estão corretas.")

if(st.button("Limpar tabela")): limpar_tabela("usuarios")
if(st.button("Mostrar no console")): mostrar_tabela("usuarios")

with st.container(border=True):
    st.header(f"Usuário logado:")

    st.caption("Nome")
    st.write(sstate.logged["user"])

    st.caption("Administrador?")
    st.write("Sim" if sstate.logged["admin"] else "Não")