import mysql.connector as sqlconn
from mysql.connector import Error
import streamlit as st
import os, bcrypt, datetime, uuid, pathlib

# Utilitarios
def string_insert(str, substring, pos) -> str:
    "Insere uma substring dentro da string passada na posição passada, e retorna o resultado."
    return str[:pos] + substring + str[pos+len(substring)-1:]

def input_notnull(text = "") -> str:
    "Igual a um input(), mas não aceita valores vazios."

    var = input(text)
    while var == "": var = input(text)
    return var

def input_choice(text = "", options : list = []) -> str:
    "Pega uma entrada do usuário e só aceita se for uma das escolhas que ele passar."

    var = input_notnull(text)
    while var not in options and not options == []: var = input_notnull(text)
    return var

def title(text : str) -> None:
    "Limpa o console e printa uma linha de título."

    os.system("cls")
    print(text.center(50, "-"))

def current_datetime() -> datetime.datetime:
    "Retorna a data e hora de agora, sem os microssegundos."
    return datetime.datetime.now().replace(microsecond=0)

def get_folder_name(path : str) -> str:
    "Retorna o nome da pasta em que o arquivo está."
    return os.path.basename(os.path.dirname(path))

def generate_filename(extension) -> str:
    "Gera um nome de arquivo a partir de um UUID v4"
    return f"{uuid.uuid4()}{extension}"

def upload_file(file_content : bytes, file_path : str) -> None:
    "Faz o upload de um arquivo ao servidor, dentro da pasta 'uploads'."

    # Escrevendo arquivo
    # Criando pasta uploads se ela ainda não existir
    if not pathlib.Path("uploads").exists(): os.makedirs("uploads")

    # Criando a pasta especificada
    filedir = os.path.dirname(f"uploads/{file_path}")
    if not os.path.exists(filedir): os.makedirs(filedir)

    with open(f"uploads/{file_path}", "wb") as f:
        f.write(file_content)

def limpar_imagens_inuteis():
    "Apaga todas as imagens que não estão sendo utilizadas em lugar algum da pasta uploads/imagens"

    # Fazendo várias buscas para guardar todas as imagens que estão sendo utilizadas
    dirs = []

    # Pegando todas as fotos
    with get_connection().cursor() as cursor:
        # Pesquisa
        cursor.execute(
            """
            SELECT fotopath FROM equipamentos
            UNION
            SELECT fotopath FROM ferramentas;
            """
        )
        dirs = [i[0] for i in cursor.fetchall()]

    # Apagando todas as imagens que não estiverem na lista
    for i in os.listdir("uploads/images"):
        caminho = f"uploads/images/{i}"
        if(caminho not in dirs and os.path.exists(caminho)): os.remove(caminho)

def get_name_from_equip_id(id : int):
    "Retorna o nome do equipamento passado. Usado nas selectboxes."

    with get_connection().cursor() as c:
        c.execute("SELECT nome FROM equipamentos WHERE idequipamento = %s", (id,))
        return c.fetchone()[0]

# Manipular banco
def get_connection() -> sqlconn.MySQLConnection:
    "Essa função retorna a conexão com o banco. Se não houver uma conexão feita, uma tentativa de conectar é realizada."

    sstate = st.session_state
    
    # Caso a variável ainda não esteja no session state, ou a conexão não estiver sendo feita, o código tenta uma conexão com o banco.
    if "conn" not in sstate or not sstate["conn"].is_connected():

        # Conectando
        conn = sqlconn.connect(
            host="localhost",
            user="root",
            password="senhabanco"
        )
        sstate["conn"] = conn

    # Se eu tiver conseguido a conexão, eu crio o banco e uso ele caso ainda não tenha o feito
    if sstate["conn"].is_connected():
        with sstate["conn"].cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS manutencao")
            cursor.execute("USE manutencao")

    return sstate["conn"]

def close_connection() -> None:
    "Procura a conexão atual e a encerra se estiver ativa. Ideal para rodar ao fim do programa."

    # Fechando só se a conexão estiver guardada na sessão E ativa.
    if "conn" in st.session_state:
        conn = st.session_state["conn"]
        if conn.is_connected():
            conn.close()
            print("Conexão MySQL encerrada.")
    
def criar_tabelas() -> None:
    """Cria as tabelas de equipamentos, ferramentas e usuários, caso não existam. Passa por cada uma individualmente.

    Equipamentos 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Modelo (VARCHAR(255) not null)
        - Fabricante (VARCHAR(255) not null)
        - Estado (VARCHAR(255) not null)
        - Tipo de Manutenção (VARCHAR(255) not null)
        - Periodicidade (INT not null)
        - Registrado por (INT not null)
        - Registrado em (DATETIME not null)
        - Modificado em (DATETIME not null)
        - Caminho da Foto (VARCHAR(40))
    
    Ferramentas 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Modelo (VARCHAR(255) not null)
        - Fabricante (VARCHAR(255) not null)
        - Specs (VARCHAR(255) not null)
        - Registrado por (INT not null)
        - Registrado em (DATETIME not null)
        - Modificado em (DATETIME not null) 
        - Caminho da Foto (VARCHAR(40))

    Usuários 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Senha (VARCHAR(255) not null)
        - Email (VARCHAR(255) not null unique)
        - CPF (VARCHAR(11) not null unique)
        - Administrator (BOOL not null)
        - Criado em (DATETIME not null)

    Registros
        - ID (INT not unll primary key auto_increment)
        - IDusuario (INT FK (idusuario))
        - IDequipamento (INT FK (idequipamento))
        - Data (DATETIME not null)
        - Prazo (DATETIME not null)
        - Registro (VARCHAR(10000) not null)
    """

    # Criando o cursor
    cursor = get_connection().cursor()

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            idusuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            senha VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            cpf VARCHAR(11) NOT NULL UNIQUE,
            admin BOOL NOT NULL,
            createdwhen DATETIME NOT NULL
        )
        """
    )

    # Tabela de equipamentos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS equipamentos(
            idequipamento INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            modelo VARCHAR(255) NOT NULL,
            fabricante VARCHAR(255) NOT NULL,
            estado VARCHAR(255) NOT NULL,
            manutencao VARCHAR(255) NOT NULL,
            periodo INT NOT NULL,
            registeredby INT NOT NULL,
            registeredwhen DATETIME NOT NULL,
            modifiedwhen DATETIME NOT NULL,
            fotopath VARCHAR(100),
            FOREIGN KEY (registeredby) REFERENCES usuarios(idusuario)
        )
        """
    )
    
    # Tabela de ferramenta
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ferramentas(
            idferramenta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            modelo VARCHAR(255) NOT NULL,
            fabricante VARCHAR(255) NOT NULL,
            specs VARCHAR(255) NOT NULL,
            registeredby INT NOT NULL,
            registeredwhen DATETIME NOT NULL,
            modifiedwhen DATETIME NOT NULL,
            fotopath VARCHAR(100),
            FOREIGN KEY (registeredby) REFERENCES usuarios(idusuario)
        )
        """
    )

    # Tabela de registros
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registros(
            idregistro INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            idusuario INT,
            idequipamento INT,
            data DATETIME NOT NULL,
            prazo DATETIME NOT NULL,
            registropath VARCHAR(100) NOT NULL,
            FOREIGN KEY (idusuario) REFERENCES usuarios(idusuario),
            FOREIGN KEY (idequipamento) REFERENCES equipamentos(idequipamento)
        )
        """
    )

    # Salvando as alterações com commit() e fechando o cursor.
    get_connection().commit()
    cursor.close()

# Funções pra usuário
def check_cpf(cpf : int) -> int | None:
    """Pega um CPF via input() e o retorna um dict com o valor numérico e o valor formatado (123.456.789-09).
    Se for inválido, retorna None"""

    cpf_str = str(cpf)

    while True:
        # Checagens pré-validação
        if(len(cpf_str) == 11 and cpf_str.isdigit()):
            # Depois que a formatação estiver correta, eu faço o algoritmo para verificar a validez
            sequencia = [int(cpf_str[i]) for i in range(9)]
            verificadores = [int(cpf_str[i]) for i in range(9, 11)]

            # PRIMEIRO DÍGITO
            soma = 0
            for i in range(1, 10): # Loop incluisivo de 1 a 9
                soma += sequencia[i-1] * i
            soma = soma % 11 if soma % 11 != 10 else 0 # Se o resto não for 10, eu o mantenho. Se não, igualo a 0.
            
            # Se está tudo certo
            if(soma == verificadores[0]):

                # Tirando o primeiro verificador e colocando direto na sequencia
                sequencia.append(verificadores.pop(0))

                # SEGUNDO DÍGITO (se o primeiro for correto)
                soma = 0
                for i in range(10): # Loop inclusivo de 0 a 9
                    soma += sequencia[i] * i
                soma = soma % 11 if soma % 11 != 10 else 0 # Se o resto não for 10, eu o mantenho. Se não, igualo a 0.

                if(soma == verificadores[0]): # O segundo dígito tá certo, então, é válido!
                    return cpf
                else: # Não bateu o valor, é falso
                    return None

            else: # Se não deu certo, quebro o loop
                return None
            
        else:
            return None
        
def check_email(email : str) -> str | None:
    "Pega um email e o retorna após validação. Retorna None se for inválido. exemplo@dominio"

    while True:
        # Verificando se tem um arroba só no email. Caso contrário, tem algo errado.
        if(email.count("@") == 1):
            
            # Verificando se existe local e domínio (antes/depois do @)
            atpos = email.find("@")

            # Checando se a parte pós-arroba existe ou não começa com espaço ou ponto
            if(email[atpos+1:] == "" or email[atpos+1] in [" ", "."] or email[-1] in [" ", "."]):
                return None
            else:
                return email
        else:
            return None

def format_cpf(cpf : int | str):
    "Formata um CPF com os traços e hífens."

    # Fazendo a versão formatada
    cpf_format = str(cpf)
    cpf_format = string_insert(cpf_format, ".", 3) # ponto 1
    cpf_format = string_insert(cpf_format, ".", 7) # ponto 2
    cpf_format = string_insert(cpf_format, "-", 11) # hífen

    return cpf_format

def novo_usuario(nome : str, senha : str, cpf : str, email : str, admin : bool) -> None:
    "A função vai requisitar todos os dados para criar um usuário e adicionará-o ao banco."

    # Hasheando senha
    senha_add = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

    # Adicionando o usuário no banco
    get_connection().start_transaction()
    with get_connection().cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome.upper(), senha_add, email, cpf, admin, current_datetime())
            )
            get_connection().commit()
        except Error as e:
            get_connection().rollback()

def login(usuario : str | int, password : str | bytes) -> bool:
    "Retorna True ou False baseado na existência do usuário (identificado por e-mail, nome ou cpf) e se a senha está correta."

    # Checando se o usuário existe
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT senha FROM usuarios WHERE email = %s OR cpf = %s", (usuario, usuario))
        search = cursor.fetchone() # Pegando o usuário apenas

    if search: # algo foi encontrado

        # Guardando a senha
        senha = search[0]

        # Descriptografando e verificando
        # comparo as duas séries de bytes, se forem iguais, retorna True
        if bcrypt.checkpw(password.encode("utf-8"), senha.encode("utf-8")): 
            return True
        else:
            return False
    else:
        return False

# Funções de equipamento
def novo_equipamento(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : int, foto : tuple | None = None) -> None:
    "Pede as informações e adiciona um equipamento ao banco. A tupla no argumento foto deve ser composta por (arquivo em bytes, diretório)."
    
    # Conectando e criando cursor
    cursor = get_connection().cursor()
    
    # Adicionando ao banco
    get_connection().start_transaction()
    with get_connection().cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO equipamentos (nome, modelo, fabricante, estado, manutencao, periodo, registeredby, registeredwhen, modifiedwhen, fotopath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, modelo, fabricante, estado, manutencao, periodo, st.session_state.userinfo[0], current_datetime(), current_datetime(), f"uploads/{foto[1]}")
            )
            get_connection().commit()
            if(foto): upload_file(foto[0], foto[1])
        except Error as e:
            get_connection().rollback()

def vizualizar_equipamento(search : tuple):
    "Função que mostra as informações do equipamento especificado com a busca."

    # ID [0] - Nome[1] - Modelo [2] - Fabricante [3] - Estado[4] - Manutenção [5] - Periodo [6] - Registrado por [7] - Registrado em [8] - Última modificação [9] - Caminho da imagem [10]

    if search[10]: 
        # Usando colunas para centralizar a imagem
        try:
            lcol, mcol, rcol = st.columns([.2, .6, .2])
            mcol.image(search[10], use_container_width=True)
        except Exception as e:
            st.error(":warning: Não foi possível carregar a imagem.")
            print(e)

    col1, col2, col3 = st.columns(3,border=True)
    with col1:
        st.write(f"Nome: {search[1]}")
        st.write(f"Modelo: {search[2]}")
    
    with col2:
        st.write(f"Fabricante: {search[3]}")
        st.write(f"Estado: {search[4]}")

    with col3:
        st.write(f"Manutenção: {search[5]}")
        st.write(f"Periodicidade: {search[6]} meses")
    
    # Pesquisando nome de quem registrou e mostrando
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT nome FROM usuarios WHERE idusuario = %s", (search[7],))
        autor = cursor.fetchone()[0]
    st.write(f"Registrado por: {autor}")
    st.write(f"Registrado em: {search[8]}")
    st.write(f"Modificado em: {search[9]}")
        
# Funções de ferramenta
def novo_ferramenta(nome : str, modelo : str, fabricante : str, specs : str) -> None:
    "Pede as informações e adiciona a ferramenta ao banco."
    
    # Conectando e criando cursor
    cursor =  get_connection().cursor()

    # Adicionando ao banco
    get_connection().start_transaction()

    try:
        cursor.execute(
            """
            INSERT INTO ferramentas (nome, modelo, fabricante, specs)
            VALUES (%s, %s, %s, %s)
            """, (nome, modelo, fabricante, specs)
        )
        get_connection().commit()
    except Error as e:
        get_connection().rollback()
    finally:
        # Commitando e fechando cursor
        cursor.close()
