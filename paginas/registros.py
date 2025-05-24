import streamlit as st
from back_functions import *
from functools import partial

st.title("Registros")

# Resumindo session state
sstate = st.session_state

# Criando as abas
tab1, tab2 = st.tabs(["Registros", "Novo Registro"])

# Colocando a função de buscar equipamentos no cache
def load_equips():
    with get_connection().cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM equipamentos WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY nome ASC
            """
        )
        search = cursor.fetchall()
    
    return [i[0] for i in search] if search else None

# Vizualizar Registros
with tab1:
    with st.container(border=True):
        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM registros WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY data ASC
                """
            )
            search = cursor.fetchall()

        if search:
            # Faço uma lista composta pelos IDs dos registros e coloco na selectbox
            regs = [i[0] for i in search]
            selected = st.selectbox("Lista de registros", regs, key="reglist1", format_func=lambda x: f"Registro Nº{x}")
        else:
            selected = st.selectbox("Lista de registros", None, placeholder="Nenhum registro.", key="reglist1")

        st.divider()

        # Criando a classe do equipamento
        reg = Registro(selected)
        reg.load_info()

        # Mostrando o equipamento encontrado
        if selected:
            vizualizar_registro(reg)
        else:
            st.caption("Nenhum registro selecionado.")

# Adicionar registro
with tab2:
    with st.form("registro", clear_on_submit=True, enter_to_submit=False):

        func = partial(get_single_info_by_id, table="equipamentos", column="nome")
        equip_r = st.selectbox("Selecione o equipamento", load_equips(), format_func=func)

        registro_r = st.text_area("Digite seu registro")
        fotos_r = st.file_uploader("Adicione foto(s) do equipamento (opcional)", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"], accept_multiple_files=True)

        if st.form_submit_button("Adicionar Registro"):
            
            if all([equip_r, registro_r]):
                if fotos_r:
                    fotos_add = []
                    for i in fotos_r:
                        extensao = Path(i.name).suffix
                        nome_arquivo = generate_filename(extensao)
                        fotos_add.append((i.read(), f"images/{nome_arquivo}"))
                    
                    novo_registro(equip_r, registro_r, fotos_add)
                else:
                    novo_registro(equip_r, registro_r)

                st.rerun()