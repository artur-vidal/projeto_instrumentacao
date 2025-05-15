import streamlit as st
from functools import partial
from funcoes import *

st.title("Ferramentas")

# Resumindo session state
sstate = st.session_state

# Construindo o dialog para editar ferramenta
@st.dialog("Edição de Ferramenta", width="large")
def editar_ferramenta(ferrid : int):
    # Pesquisando
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT nome, modelo, fabricante, specs FROM ferramentas WHERE id = %s", (ferrid,))
        search = cursor.fetchone()

    with st.form("edit_tool", enter_to_submit=False):

        # Campos para entrada de informação
        nome_novo = st.text_input("Nome", value=search[0])
        modelo_novo = st.text_input("Modelo", value=search[1])
        fabri_novo = st.text_input("Fabricante", value=search[2])
        specs_novo = st.text_area("Especificações", value=search[3])

        imagem_f = st.file_uploader("Foto da ferramenta", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if st.form_submit_button("Aplicar mudanças"):

            # Rodando a query para editar
            # Só edito se nem todos os valores forem iguais
            if not all([nome_novo == search[0], modelo_novo == search[1], fabri_novo == search[2], specs_novo == search[3], imagem_f == None]):
                with get_connection().cursor() as cursor:
                    if imagem_f:

                        # Apagando a imagem anterior
                        cursor.execute("SELECT fotopath FROM ferramentas WHERE id = %s", (ferrid,))
                        search = cursor.fetchone()               

                        # Guardando no banco de dados
                        extensao = pathlib.Path(imagem_f.name).suffix
                        nome_arquivo = generate_filename(extensao)
                        
                        get_connection().start_transaction()
                        try:
                            cursor.execute(
                                """
                                UPDATE ferramentas SET nome = %s, modelo = %s, fabricante = %s, specs = %s, modifiedwhen = %s, fotopath = %s WHERE id = %s;
                                """, (nome_novo, modelo_novo, fabri_novo, specs_novo, current_datetime(), f"uploads/images/{nome_arquivo}", ferrid)
                            )
                            get_connection().commit()

                            # Fazendo o upload
                            upload_file(imagem_f.read(), f"images/{nome_arquivo}")
                        except Exception as e:
                            get_connection().rollback()
                            print(e)

                    else:

                        # Se não houver imagem, eu só mudo todo o resto
                        get_connection().start_transaction()
                        try:
                            cursor.execute(
                                """
                                UPDATE ferramentas SET nome = %s, modelo = %s, fabricante = %s, specs = %s, modifiedwhen = %s WHERE id = %s;
                                """, (nome_novo, modelo_novo, fabri_novo, specs_novo, current_datetime(), ferrid)
                            )
                            get_connection().commit()
                        except Exception as e:
                            get_connection().rollback()
                            print(e)

            st.rerun()

# Construindo o dialog para remover ferramenta
@st.dialog("Remover Ferramenta")
def remover_ferramenta(ferrid : int):

    # Confirmação
    st.write(f"Tem certeza de que quer apagar o equipamento ***{get_single_info_by_id(ferrid, "ferramentas", "nome")}***?")

    # Botões
    btn1, btn2 = st.columns(2)

    # Removendo ferramenta
    if btn1.button("Sim", use_container_width=True):
        with get_connection().cursor() as cursor:
            cursor.execute("DELETE FROM ferramentas WHERE id = %s", (ferrid,))
            get_connection().commit()
        
        st.rerun()

    # Fechando dialog
    if btn2.button("Não", use_container_width=True): 
        st.rerun()

# Criando as abas
tab1, tab2, tab3 = st.tabs(["Registradas", "Registrar Nova", "Editar"])

# Procurar ferramentas
with tab1:
    with st.container(border=True):
        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM ferramentas WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY nome ASC
                """
            )
            search = cursor.fetchall()

        if search:
            # Faço uma lista composta pelos IDs das ferramentas e coloco na selectbox
            tools = [i[0] for i in search]
            func = partial(get_single_info_by_id, table="ferramentas", column="nome")
            selected = st.selectbox("Lista de ferramentas", tools, key="toollist1", format_func=func)
        else:
            selected = st.selectbox("Lista de ferramentas", None, placeholder="Nenhuma equipamento ferramenta.", key="toollist1")

        st.divider()

        # Criando a classe da ferramenta
        tool = Ferramenta(selected)
        tool.load_info()

        # Mostrando o equipamento encontrado
        if selected:
            vizualizar_ferramenta(tool)
        else:
            st.caption("Nenhuma ferramenta selecionada.")

# Adicionar equipamentos
with tab2:
    
    with st.form("equip", clear_on_submit=True, enter_to_submit=False):
        # Campos para entrada de informação
        nome_f = st.text_input("Nome")
        modelo_f = st.text_input("Modelo")
        fabri_f = st.text_input("Fabricante")
        specs_f = st.text_area("Especificações")

        imagem_e = st.file_uploader("Foto da ferramenta (opcional)", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if(st.form_submit_button("Registrar")):
            
            # Checando todos os valores
            if(all([nome_f, modelo_f, fabri_f, specs_f])):
                # Registrando a imagem
                if(imagem_e):
                    extensao = pathlib.Path(imagem_e.name).suffix
                    nome_arquivo = generate_filename(extensao)

                    # Registrando o resto
                    novo_ferramenta(nome_f, modelo_f, fabri_f, specs_f, (imagem_e.read(), f"images/{nome_arquivo}"))
                else:  
                    novo_ferramenta(nome_f, modelo_f, fabri_f, specs_f)

                st.rerun()
            else:
                st.warning("Preencha todos os campos.")

# Equipamentos do usuário
with tab3:
    with get_connection().cursor() as cursor:
        if(sstate.userinfo[1]):
            cursor.execute("SELECT id FROM ferramentas WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY modifiedwhen ASC")
        else:
            cursor.execute(
                """
                SELECT id FROM ferramentas WHERE registeredby = %s AND WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY modifiedwhen ASC
                """, (sstate.userinfo[0],)
            )
        search = cursor.fetchall()

    if search:
        # Faço uma lista composta pelos IDs das ferramentas e coloco na selectbox
        mytools = [i[0] for i in search]
        func = partial(get_single_info_by_id, table="ferramentas", column="nome")
        myselected = st.selectbox("Lista de ferramentas", mytools, key="toollist2", format_func=func)
    else:
        myselected = st.selectbox("Lista de ferramentas", None, placeholder="Nenhum equipamento.", key="toollist2")

    if(sstate.userinfo[1]): st.caption("Mostrando todos os equipamentos.")

    # Botões
    btn1, btn2 = st.columns(2)
    btn1.button("Apagar esta ferramenta", type="primary", on_click=remover_ferramenta if myselected else None, args=(myselected,), use_container_width=True)
    btn2.button("Editar esta ferramenta", on_click=editar_ferramenta if myselected else None, args=(myselected,), use_container_width=True)
