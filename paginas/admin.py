import streamlit as st
import bcrypt, time
from mysql.connector import Error
from functools import partial
from funcoes import *

st.title("Painel do Administrador")

st.divider()

# Resumindo session state
sstate = st.session_state

# Cadastrar novo usuário
@st.dialog("Cadastro")
def cadastrar():
    with st.form("cadastro"):
        
        # Campos de entrada de dados
        nome_c = st.text_input("Nome do usuário")
        email_c = st.text_input("E-mail")
        cpf_c = st.text_input("CPF", max_chars=11)
        senha_c = st.text_input("Senha", type="password")
        admin_c = st.checkbox("Administrador?")

        if st.form_submit_button("Cadastrar"):
            # Se tudo estiver preenchido, eu crio o usuário no banco
            if(all([nome_c, email_c, cpf_c, senha_c])):
                if(check_email(email_c) and check_cpf(cpf_c)):
                    novo_usuario(nome_c, senha_c, cpf_c, email_c, admin_c)
                    st.rerun()
                else:
                    # Erro se a validação não der certo
                    st.error("O e-mail ou CPF é inválido. Use valores reais.")
            else:
                st.warning("Preencha todos os campos.")

# Importar usuários
@st.dialog("Importação")
def importar():
    arquivo = st.file_uploader("Selecione sua planilha", type="xlsx")
    st.caption("Caso altere a planilha, é necessário carregar o arquivo novamente.")
    qtd = st.slider("Deseja registrar quantos usuários?", 10, 50, step=5)

    if arquivo:
        if st.button("Importar"):
            import_users(arquivo, qtd)
    
# Função para arquivar usuário
@st.dialog("Arquivar Usuário")
def arquivar():
    st.caption("Selecione o usuário para arquivar")

    # Buscando usuários e excluindo o administrador
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT id FROM usuarios WHERE enabled = TRUE AND cpf != 00000000000")
        usuarios = [i[0] for i in cursor.fetchall()]

    # Fazendo a lista
    func = partial(get_single_info_by_id, table="usuarios", column="nome")
    lista_usuarios = st.selectbox("Usuários", options=usuarios, format_func=func)

    # Arquivando esse usuário
    if(st.button("Arquivar")):
        get_connection().start_transaction()
        try:
            with get_connection().cursor() as cursor:
                cursor.execute("UPDATE usuarios SET enabled = FALSE WHERE id = %s", (lista_usuarios,))
                get_connection().commit()

                st.success("Arquivado!")
                with st.spinner("Saindo..."):
                    time.sleep(1)
                    st.rerun()

        except Error as e:
            get_connection().rollback()
            print(e)
            st.error("Ocorreu um erro ao arquivar o usuário. Cheque o console para verificar.")

# Função para desarquivar usuário
@st.dialog("Desarquivar Usuário")
def desarquivar():
    if sstate.verified:
        st.caption("Selecione o usuário para desarquivar")

        # Buscando usuários e excluindo o administrador
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE enabled = FALSE AND cpf != 00000000000")
            usuarios = [i[0] for i in cursor.fetchall()]

        # Fazendo a lista
        func = partial(get_single_info_by_id, table="usuarios", column="nome")
        lista_usuarios = st.selectbox("Usuários", options=usuarios, format_func=func)

        # Desarquivando esse usuário
        if(st.button("Desarquivar")):
            get_connection().start_transaction()
            try:
                with get_connection().cursor() as cursor:
                    cursor.execute("UPDATE usuarios SET enabled = TRUE WHERE id = %s", (lista_usuarios,))
                    get_connection().commit()

                    st.success("Desarquivado!")
                    with st.spinner("Saindo..."): 
                        time.sleep(1)
                        sstate.verified = False
                        st.rerun()

            except Error as e:
                get_connection().rollback()
                print(e)
                st.error("Ocorreu um erro ao desarquivar o usuário. Cheque o console para verificar.")
    else:
        with st.form("verify", border=False):
            senha = st.text_input("Digite sua senha para verificação.", type="password")

            if st.form_submit_button("Verificar"):
                with get_connection().cursor() as cursor:
                    cursor.execute("SELECT senha FROM usuarios WHERE id = %s", (sstate.userinfo[0],))
                    senha_hash = cursor.fetchone()[0]

                # Checando valores
                if bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8")): 
                    sstate.verified = True
                    st.rerun(scope="fragment")
                else:
                    st.error("Senha incorreta. Verifique se inseriu a senha correta.")

# Cadastro
st.button("Cadastrar novo usuário", on_click=cadastrar)
st.caption("Abre um pop-up para cadastrar um novo usuário.")

import_col1, import_col2 = st.columns([1, 2])
import_col1.button("Importar planilha de usuários", on_click=importar)

with open("assets/sheet_model.xlsx", "rb") as f:
    import_col2.download_button("Baixar modelo", data=f, file_name="Planilha de Usuários - Modelo.xlsx", type="primary")
    
st.caption("Selecione uma planilha em excel para importar os usuários dentro dela. Ela deve seguir o modelo padronizado disponível a seguir.")
st.caption("O modelo pode ser encontrado em assets/sheet_model.xlsx caso precise modificá-lo, mas note que uma mudança no **layout** pode gerar erros, então é aconselhada apenas a mudança de cores ou fontes.")

# Paro de renderizar a partir daqui se o usuário for o admin
if sstate.userinfo[0] == 1: st.stop()

st.divider()

# Limpar imagens inutilizadas
st.button("Limpar imagens inutilizadas", on_click=limpar_imagens_inuteis)
st.caption("Apaga as imagens salvas em 'uploads/images/' que não estão sendo usadas em lugar algum.")

st.divider()

# Arquivar usuário
st.button("Arquivar usuário", on_click=arquivar)
st.caption("Selecione um usuário para arquivar. Isso vai essencialmente desabilitá-lo, mas pode ser desarquivado a qualquer momento.")

# Desarquivar usuário
st.button("Desarquivar usuário", on_click=desarquivar)
st.caption("Selecione um usuário para desarquivar. Isso vai reabilitá-lo, fazendo com que seus registros apareçam novamente.")