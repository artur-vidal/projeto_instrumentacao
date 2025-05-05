import streamlit as st
from funcoes import *

st.title("Painel do Administrador")

# Cadastrar novo usuário
@st.dialog("cadastro")
def cadastrar():
    with st.form("cadastro"):
        
        # Campos de entrada de dados
        nome_c = st.text_input("Nome do usuário")
        email_c = st.text_input("E-mail")
        cpf_c = st.text_input("CPF", max_chars=11)
        senha_c = st.text_input("Senha", type="password")
        admin_c = st.checkbox("Administrador?")

        if st.form_submit_button("Cadastrar"):
            if(all([nome_c, email_c, cpf_c, senha_c])):
                if(check_email(email_c) and check_cpf(cpf_c)):
                    novo_usuario(nome_c, senha_c, cpf_c, email_c, admin_c)
                    st.rerun()
                else:
                    st.error("O e-mail ou CPF é inválido. Use valores reais.")
            else:
                st.warning("Preencha todos os campos.")

st.button("Cadastrar novo usuário", on_click=cadastrar)
st.caption("Abre um pop-up para cadastrar um novo usuário.")

# Limpar imagens inutilizadas
botao = st.button("Limpar imagens inutilizadas", on_click=limpar_imagens_inuteis)
st.caption("Apaga as imagens (ou outros arquivos) salvas que não estão sendo usadas em lugar algum.")