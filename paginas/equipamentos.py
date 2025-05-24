import streamlit as st
from functools import partial
from mysql.connector import Error
from back_functions import *

st.title("Equipamentos")

# Resumindo session state
sstate = st.session_state

# Construindo o dialog para editar equipamento
@st.dialog("Edição de Equipamento", width="large")
def editar_equip(equipid : int):
    # Pesquisando
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT nome, modelo, fabricante, periodo, estado, manutencao FROM equipamentos WHERE id = %s", (equipid,))
        search = cursor.fetchone()

    with st.form("edit_equip", enter_to_submit=False):

        # Campos para entrada de informação
        nome_novo = st.text_input("Nome", value=search[0])
        modelo_novo = st.text_input("Modelo", value=search[1])
        fabri_novo = st.text_input("Fabricante", value=search[2])

        opt_estado = ["Operante", "Operante com defeito", "Inoperante"]
        estado_novo = st.radio("Estado", opt_estado, index=opt_estado.index(search[4]))

        opt_manutencao = ["Preventiva", "Corretiva"]
        manutencao_novo = st.radio("Tipo de Manutenção", opt_manutencao, index=opt_manutencao.index(search[5]))
        periodo_novo = st.number_input("Periodicidade da Manutenção (meses)", min_value=1, value=search[3])

        imagem_e = st.file_uploader("Foto do equipamento", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if st.form_submit_button("Aplicar mudanças"):

            # Rodando a query para editar
            if not all([nome_novo == search[0], modelo_novo == search[1], fabri_novo == search[2], periodo_novo == search[3], estado_novo == search[4], manutencao_novo == search[5], imagem_e == None]):
                with get_connection().cursor() as cursor:
                    if imagem_e:

                        # Apagando a imagem anterior
                        cursor.execute("SELECT fotopath FROM equipamentos WHERE id = %s", (equipid,))
                        search = cursor.fetchone()

                        # Guardando no banco de dados
                        extensao = Path(imagem_e.name).suffix
                        nome_arquivo = generate_filename(extensao)
                        
                        get_connection().start_transaction()
                        try:
                            cursor.execute(
                                """
                                UPDATE equipamentos SET nome = %s, modelo = %s, fabricante = %s, estado = %s, manutencao = %s, periodo = %s, modifiedwhen = %s, fotopath = %s WHERE id = %s;
                                """, (nome_novo, modelo_novo, fabri_novo, estado_novo, manutencao_novo, periodo_novo, current_datetime(), f"uploads/images/{nome_arquivo}", equipid)
                            )
                            get_connection().commit()

                            # Fazendo o upload
                            upload_file(imagem_e.read(), f"images/{nome_arquivo}")

                            # Registrando
                            register_log(f"{sstate.userinfo[2]} editou o EQUIPAMENTO {search[0]}")

                        except:
                            get_connection().rollback()

                    else:

                        # Se não houver imagem, eu só mudo todo o resto
                        get_connection().start_transaction()
                        try:
                            cursor.execute(
                                """
                                UPDATE equipamentos SET nome = %s, modelo = %s, fabricante = %s, estado = %s, manutencao = %s, modifiedwhen = %s, periodo = %s WHERE id = %s;
                                """, (nome_novo, modelo_novo, fabri_novo, estado_novo, manutencao_novo, current_datetime(), periodo_novo, equipid)
                            )
                            get_connection().commit()

                            # Registrando
                            register_log(f"{sstate.userinfo[2]} editou o EQUIPAMENTO {search[0]}")

                        except Error:
                            get_connection().rollback()


            st.rerun()

# Construindo o dialog para remover equipamento
@st.dialog("Remover Equipamento")
def remover_equip(equipid : int):

    # Confirmação
    st.write(f"Tem certeza de que quer apagar o equipamento ***{get_single_info_by_id(equipid, "equipamentos", "nome")}***?")

    # Botões
    btn1, btn2 = st.columns(2)

    # Removendo equipamento
    if btn1.button("Sim", use_container_width=True):
        
        nome_equip = get_single_info_by_id(equipid, "equipamentos", "nome")

        try:
            get_connection().start_transaction()
            with get_connection().cursor() as cursor:
                cursor.execute("DELETE FROM equipamentos WHERE id = %s", (equipid,))
            get_connection().commit()

            # Registrando
            register_log(f"{sstate.userinfo[2]} removeu o EQUIPAMENTO {nome_equip}")

            st.rerun()
        except Error as e:
            get_connection().rollback()
            print(e)
        
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
                SELECT id FROM equipamentos WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY nome ASC
                """
            )
            search = cursor.fetchall()

        if search:
            # Faço uma lista composta pelos IDs dos equipamentos e coloco na selectbox
            equips = [i[0] for i in search]
            func = partial(get_single_info_by_id, table="equipamentos", column="nome")
            selected = st.selectbox("Lista de equipamentos", equips, key="equiplist1", format_func=func)
        else:
            selected = st.selectbox("Lista de equipamentos", None, placeholder="Nenhum equipamento.", key="equiplist1")

        st.divider()

        # Criando a classe do equipamento
        equip = Equipamento(selected)
        equip.load_info()

        # Mostrando o equipamento encontrado
        if selected:
            vizualizar_equipamento(equip)
        else:
            st.caption("Nenhum equipamento selecionado.")

# Adicionar equipamentos
with tab2:
    
    with st.form("equip", clear_on_submit=True, enter_to_submit=False):
        # Campos para entrada de informação
        nome_e = st.text_input("Nome")
        modelo_e = st.text_input("Modelo")
        fabri_e = st.text_input("Fabricante")
        estado_e = st.radio("Estado", ["Operante", "Operante com defeito", "Inoperante"])
        manutencao_e = st.radio("Tipo de Manutenção", ["Preventiva", "Corretiva"])
        periodo_e = st.number_input("Periodicidade da Manutenção (meses)", min_value=1)

        imagem_e = st.file_uploader("Foto do equipamento (opcional)", type=["png", "jpg", "jpeg", "webp", "bmp", "psd", "tiff", "avif"])

        if(st.form_submit_button("Registrar")):
            
            # Checando todos os valores
            if(all([nome_e, modelo_e, fabri_e])):
                # Registrando a imagem
                if(imagem_e):
                    extensao = Path(imagem_e.name).suffix
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
        if(sstate.userinfo[1]):
            cursor.execute("SELECT id FROM equipamentos WHERE registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY modifiedwhen ASC")
        else:
            cursor.execute(
                """
                SELECT id FROM equipamentos WHERE registeredby = %s AND registeredby IN (SELECT id FROM usuarios WHERE enabled = TRUE) ORDER BY modifiedwhen ASC
                """, (sstate.userinfo[0],)
            )
        search = cursor.fetchall()

    if search:
        # Faço uma lista composta pelos IDs dos equipamentos e coloco na selectbox
        myequips = [i[0] for i in search]
        func = partial(get_single_info_by_id, table="equipamentos", column="nome")
        myselected = st.selectbox("Lista de equipamentos", myequips, key="equiplist2", format_func=func)
    else:
        myselected = st.selectbox("Lista de equipamentos", None, placeholder="Nenhum equipamento.", key="equiplist2")

    if(sstate.userinfo[1]): st.caption("Mostrando todos os equipamentos.")

    # Botões
    btn1, btn2 = st.columns(2)
    btn1.button("Apagar este equipamento", type="primary", on_click=remover_equip if myselected else None, args=(myselected,), use_container_width=True)
    btn2.button("Editar este equipamento", on_click=editar_equip if myselected else None, args=(myselected,), use_container_width=True)
