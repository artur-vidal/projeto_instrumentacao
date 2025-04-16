import streamlit as st
import sqlite3 as sql
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
    if(st.button("Cadastrar") and all([nome_c, senha_c, cpf_c, email_c])):
        try:
            cpf_c = check_cpf(cpf_c)
            novo_usuario(nome_c, senha_c, cpf_c, email_c, admin_c)
        except:
            st.error("O CPF não é numérico.")

# Aba de login
with st.expander("Login"):

    # Campos para pegar informações
    nome_l = st.text_input("Nome, e-mail ou CPF do usuário")
    senha_l = st.text_input("Senha", type="password")

    if(st.button("Logar")): 
        if(login(nome_l, senha_l)):
            # Pegando o nome do usuário que eu acabei de logar
            db = sql.connect("db/banco.db") 
            cursor = db.cursor()

            # Pegando o nome via nome, email ou cpf
            cursor.execute("SELECT nome FROM usuarios WHERE nome = ? OR email = ? OR cpf = ?", (nome_l, check_email(nome_l), check_cpf(nome_l)))
            search = cursor.fetchone() # Pegando o usuário apenas

            # Pop-up de sucesso
            st.success(f"Usuário \"{search[0]}\" logado com sucesso!")
            sstate.user = nome_l
            sstate.password = senha_l
        else:
            st.error("Não foi possível fazer login. Verifique se as informações inseridas estão corretas.")

if(st.button("Limpar tabela")): limpar_tabela("usuarios")
if(st.button("Mostrar no console")): mostrar_tabela("usuarios")

st.write(f"Usuário logado: {sstate.user}")