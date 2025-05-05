import streamlit as st
import time
from mysql.connector import Error
from funcoes import *

st.title("Equipamentos")

# Resumindo session state
sstate = st.session_state

# Construindo o dialog para editar equipamento
@st.dialog("Edição de Equipamento", width="large")
def editar_equip(equipid : int):
    # Pesquisando
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT nome, modelo, fabricante, periodo FROM equipamentos WHERE idequipamento = %s", (equipid,))
        search = cursor.fetchone()

    with st.form("edit_equip"):

        # Campos para entrada de informação
        nome_novo = st.text_input("Nome", placeholder=search[0])
        modelo_novo = st.text_input("Modelo", placeholder=search[1])
        fabri_novo = st.text_input("Fabricante", placeholder=search[2])
        estado_novo = st.radio("Estado", ["Operante", "Inoperante"])
        manutencao_novo = st.radio("Tipo de Manutenção", ["Preventiva", "Corretiva"])
        periodo_novo = st.number_input("Periodicidade da Manutenção (meses)", min_value=0, value=search[3])

        imagem_e = st.file_uploader("Foto do equipamento", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if st.form_submit_button("Aplicar mudanças"):

            # Adiciono os valores novos só se eles forem de fato algo
            nome_add = nome_novo if nome_novo else search[0]
            modelo_add = modelo_novo if modelo_novo else search[1]
            fabri_add = fabri_novo if fabri_novo else search[2]
            periodo_add = periodo_novo if periodo_novo else search[3]

            # Rodando a query para editar
            with get_connection().cursor() as cursor:
                if imagem_e:

                    # Apagando a imagem anterior
                    cursor.execute("SELECT fotopath FROM equipamentos WHERE idequipamento = %s", (equipid,))
                    search = cursor.fetchone()
                    
                    with st.spinner(None):
                        time.sleep(3)
                        st.write(search)
                    
                    os.remove(search[0])

                    # Guardando no banco de dados
                    extensao = pathlib.Path(imagem_e.name).suffix
                    nome_arquivo = f"images/{generate_filename(extensao)}"
                    
                    get_connection().start_transaction()
                    try:
                        cursor.execute(
                            """
                            UPDATE equipamentos SET nome = %s, modelo = %s, fabricante = %s, estado = %s, manutencao = %s, periodo = %s, modifiedwhen = %s, fotopath = %s WHERE idequipamento = %s;
                            """, (nome_add, modelo_add, fabri_add, estado_novo, manutencao_novo, periodo_add, current_datetime(), f"uploads/images/{nome_arquivo}", equipid)
                        )
                        get_connection().commit()

                        # Fazendo o upload
                        upload_file(imagem_e.read(), nome_arquivo)
                    except:
                        get_connection().rollback()

                else:

                    # Se não houver imagem, eu só mudo todo o resto
                    get_connection().start_transaction()
                    try:
                        cursor.execute(
                            """
                            UPDATE equipamentos SET nome = %s, modelo = %s, fabricante = %s, estado = %s, manutencao = %s, modifiedwhen = %s, periodo = %s WHERE idequipamento = %s;
                            """, (nome_add, modelo_add, fabri_add, estado_novo, manutencao_novo, current_datetime(), periodo_add, equipid)
                        )
                        get_connection().commit()
                    except Error:
                        get_connection().rollback


            st.rerun()

# Construindo o dialog para remover equipamento
@st.dialog("Remover Equipamento")
def remover_equip(equipid : int):

    # Confirmação
    st.write(f"Tem certeza de que quer apagar o equipamento ***{get_name_from_equip_id(equipid,)}***?")

    # Botões
    btn1, btn2 = st.columns(2)

    # Removendo equipamento
    if btn1.button("Sim", use_container_width=True):
        with get_connection().cursor() as cursor:
            cursor.execute("DELETE FROM equipamentos WHERE idequipamento = %s", (equipid,))
            get_connection().commit()
        
        st.rerun()

    # Fechando dialog
    if btn2.button("Não", use_container_width=True): 
        st.rerun()

# Criando as abas
tab1, tab2, tab3 = st.tabs(["Registrados", "Registrar Novo", "Editar"])

# Procurar equipamentos
with tab1:
    with st.container(border=True):
        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                SELECT idequipamento FROM equipamentos
                """
            )
            search = cursor.fetchall()

        if search:
            # Faço uma lista composta pelos IDs dos equipamentos e coloco na selectbox
            equips = [i[0] for i in search]
            selected = st.selectbox("Lista de equipamentos", equips, key="equiplist1", format_func=get_name_from_equip_id)
        else:
            selected = st.selectbox("Lista de equipamentos", None, placeholder="Nenhum equipamento.", key="equiplist1")

        st.divider()

        # Exibindo tudo sobre o equipamento selecionado
        cursor = get_connection().cursor()
        cursor.execute("SELECT * FROM equipamentos WHERE idequipamento = %s", (selected,))
        search = cursor.fetchone()

        # Mostrando o equipamento encontrado
        if search:
            vizualizar_equipamento(search)
        else:
            st.caption("Nenhum equipamento selecionado.")
        
        # Fechando cursor
        cursor.close()

# Adicionar equipamentos
with tab2:
    
    with st.form("equip"):
        # Campos para entrada de informação
        nome_e = st.text_input("Nome")
        modelo_e = st.text_input("Modelo")
        fabri_e = st.text_input("Fabricante")
        estado_e = st.radio("Estado", ["Operante", "Inoperante"])
        manutencao_e = st.radio("Tipo de Manutenção", ["Preventiva", "Corretiva"])
        periodo_e = st.number_input("Periodicidade da Manutenção (meses)", min_value=0, value=0)

        imagem_e = st.file_uploader("Foto do equipamento (opcional)", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if(st.form_submit_button("Registrar")):
            
            # Checando todos os valores
            if(all([nome_e, modelo_e, fabri_e, estado_e, manutencao_e, periodo_e])):
                # Registrando a imagem
                if(imagem_e):
                    extensao = pathlib.Path(imagem_e.name).suffix
                    nome_arquivo = generate_filename(extensao)

                    # Registrando o resto
                    novo_equipamento(nome_e, modelo_e, fabri_e, estado_e, manutencao_e, periodo_e, (imagem_e.read(), f"images/{nome_arquivo}"))
                else:  
                    novo_equipamento(nome_e, modelo_e, fabri_e, estado_e, manutencao_e, periodo_e)

                st.rerun()
            else:
                st.warning("Preencha todos os campos.")

# Equipamentos do usuário
with tab3:
    with get_connection().cursor() as cursor:
        cursor.execute(
            """
            SELECT idequipamento FROM equipamentos WHERE registeredby = %s
            """, (sstate.userinfo[0],)
        )
        search = cursor.fetchall()

    if search:
        # Faço uma lista composta pelos IDs dos equipamentos e coloco na selectbox
        myequips = [i[0] for i in search]
        myselected = st.selectbox("Lista de equipamentos", myequips, key="equiplist2", format_func=get_name_from_equip_id)
    else:
        myselected = st.selectbox("Lista de equipamentos", None, placeholder="Nenhum equipamento.", key="equiplist2")

    # Botões
    btn1, btn2 = st.columns(2)
    btn1.button("Apagar este equipamento", type="primary", on_click=remover_equip if myselected else None, args=(myselected,), use_container_width=True)
    btn2.button("Editar este equipamento", on_click=editar_equip if myselected else None, args=(myselected,), use_container_width=True)
