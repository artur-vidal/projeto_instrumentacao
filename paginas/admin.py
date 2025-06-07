import streamlit as st
import bcrypt, time
from mysql.connector import Error
from functools import partial
from back_functions import *

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
        admin_c = st.checkbox("Administrador?")

        if st.form_submit_button("Cadastrar"):
            # Se tudo estiver preenchido, eu crio o usuário no banco
            if(all([nome_c, email_c, cpf_c])):
                if(check_email(email_c) and check_cpf(cpf_c)):
                    novo_usuario(nome_c, cpf_c, email_c, admin_c)
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

    if arquivo and st.button("Importar"): import_users(arquivo)
    
# Função para arquivar usuário
@st.dialog("Arquivar Usuário")
def arquivar():
    st.caption("Selecione o usuário para arquivar")

    # Buscando usuários e excluindo o administrador
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT id FROM usuarios WHERE enabled = TRUE AND (id != 1 AND id != %s)", (sstate.userinfo[0],))
        usuarios = [i[0] for i in cursor.fetchall()]
    close_connection()

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
        finally:
            close_connection()

# Função para desarquivar usuário
@st.dialog("Desarquivar Usuário")
def desarquivar():
    if sstate.verified:
        st.caption("Selecione o usuário para desarquivar")

        # Buscando usuários e excluindo o administrador
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE enabled = FALSE AND cpf != 00000000000")
            usuarios = [i[0] for i in cursor.fetchall()]
        close_connection()

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
            
            finally:
                close_connection()
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

# Função para redefinir senha de usuário
@st.dialog("Removendo Senha")
def remover_senha():
    user = st.text_input("Insira o e-mail ou CPF do usuário:")

    remover = st.button("Remover senha", type="primary", use_container_width=True)

    if remover:
        # Rodando query para ver se o usuário existe
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE email = %s or cpf = %s", (user, user))
            idusuario = cursor.fetchone()
        close_connection()
        
        # Se existe, eu rodo a tarefa
        if idusuario:

            if idusuario[0] != 1 and idusuario[0] != sstate.userinfo[0]:

                # Rodando query para tirar a senha
                try:
                    get_connection().start_transaction()
                    with get_connection().cursor() as cursor:
                        cursor.execute("UPDATE usuarios SET senha = NULL WHERE id = %s", (idusuario[0],))

                    get_connection().commit()

                    st.rerun()
                except Error as e:
                    get_connection().rollback()
                    print(e)
                finally:
                    close_connection()

            elif idusuario[0] == 1:
                st.warning(":warning: Não remova a senha do usuário padrão. Edite o arquivo de configuração ao invés disso.")

            elif idusuario[0] == sstate.userinfo[0]:
                st.warning(":warning: Não é possível remover a senha do usuário atual. Faça isso via outro usuário.")

        else:
            st.error("Este usuário não existe.")

# Mostrar registro de auditoria
@st.dialog("Registro de Auditoria", width="large")
def registro_auditoria():

    if os.path.exists("logs"):
        arquivos = os.listdir("logs")
        registros = []
        for i in sorted(arquivos, key=lambda x: datetime.datetime.strptime(x.split("_")[0], "%d%m%Y")):
            with open(os.path.join(LOG_DIR, i), "r") as f:
                registros.append(f.read())
        
        format_register = lambda x: x[1:11]
        lista_registros = st.selectbox("Selecione um dia", options=registros, format_func=format_register)
        st.code(lista_registros)

        # Botão de exportar
        st.download_button("Baixar esse registro", data=lista_registros, file_name=f"{format_register(lista_registros)}_log.log", icon=":material/download:")
    else:
        st.write("Não há nenhum registro.")

# Cadastro
st.button("Cadastrar novo usuário", on_click=cadastrar)
st.caption("Abre um pop-up para cadastrar um novo usuário.")

import_col1, import_col2 = st.columns([1, 2])
import_col1.button("Importar planilha de usuários", on_click=importar)

with open("assets/sheet_model.xlsx", "rb") as f:
    import_col2.download_button("Baixar modelo", data=f, file_name="Planilha de Usuários - Modelo.xlsx", type="primary", icon=":material/download:")
    
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

# Remover senha de usuário
st.button("Remover senha de usuário", on_click=remover_senha)
st.caption("Use esta opção caso um usuário esqueça a própria senha. Isso vai remover a senha dele, e o sistema vai pedir novamente para o usuário criar sua senha.")

st.divider()

# Mostrar logs
st.button("Registro de auditoria", on_click=registro_auditoria)
st.caption("Um registro contendo tudo o que é feito no aplicativo.")