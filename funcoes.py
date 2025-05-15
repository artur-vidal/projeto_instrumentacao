import mysql.connector as sqlconn
from mysql.connector import Error
import streamlit as st
import os, bcrypt, datetime, uuid, pathlib

dbconfig = {
    "host" : "localhost",
    "user" : "root",
    "password" : "senhabanco"
}

# Classes
class Usuario():
    "Guarda todas as informações de um usuário. Precisa de um ID."

    # Inicializando
    def __init__(self, id : int):
        self.id : int = id
        self.nome : str = None
        self.email : str = None
        self.cpf : str = None
        self.admin : bool = None

        self.loaded : bool = False

    def __str__(self):
        if self.loaded:
            return f"""
                    ID: {self.id}\n
                    Nome: {self.nome},\n
                    E-mail: {self.nome},\n
                    CPF: {self.nome},\n
                    Administrador: {"Sim" if self.admin else "Não"}
                    """
        else:
            return "O usuário ainda não foi carregado."

    def load_info(self):
        "Carrega do banco as informações do usuário baseado no id."
        
        # Rodando query
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT nome, email, cpf, admin FROM usuarios WHERE id = %s", (self.id,))
            search = cursor.fetchone()

        # Guardando na classe
        if search:
            self.nome = search[0]
            self.email = search[1]
            self.cpf = search[2]
            self.admin = search[3]

            self.loaded = True

class Equipamento():
    "Guarda todas as informações de um equipamento. Precisa de um ID."

    # Inicializando
    def __init__(self, id : int):
        self.id : int = id
        self.nome : str = None
        self.modelo : str = None
        self.fabricante : str = None
        self.estado : str = None
        self.manucentao : str = None
        self.periodo : int = None
        self.registeredby : int = None
        self.registeredwhen : datetime.datetime = None
        self.modifiedwhen : datetime.datetime = None
        self.fotopath : str = None

        # Guardando uma variável com o nome do autor do equipamento
        self.nome_autor : str = None

        self.loaded : bool = False

    def __str__(self):
            if self.loaded:
                return f"""
                        ID: {self.id}\n
                        Nome: {self.nome},
                        Modelo: {self.modelo},
                        Fabricante: {self.fabricante},
                        Estado: {self.estado},
                        Tipo de Manutenção: {self.manucentao},
                        Periodicidade em meses: {self.periodo}\n
                        Registrado por: {self.nome_autor} (ID {self.registeredby}),
                        Registrado em: {self.registeredwhen},
                        Última modificação em: {self.modifiedwhen}\n
                        Caminho da foto: {self.fotopath}
                        """
            else:
                return "O equipamento ainda não foi carregado."
    
    def load_info(self):
        "Carrega do banco as informações do equipamento baseado no seu id."
        
        # Rodando query
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT nome, modelo, fabricante, estado, manutencao, periodo, registeredby, registeredwhen, modifiedwhen, fotopath FROM equipamentos WHERE id = %s", (self.id,))
            search = cursor.fetchone()

        # Guardando na classe
        if search:
            self.nome = search[0]
            self.modelo = search[1]
            self.fabricante = search[2]
            self.estado = search[3]
            self.manucentao = search[4]
            self.periodo = search[5]
            self.registeredby = search[6]
            self.registeredwhen = search[7]
            self.modifiedwhen = search[8]
            self.fotopath = search[9]
            self.nome_autor = get_single_info_by_id(self.registeredby, "usuarios", "nome")

            self.loaded = True

class Ferramenta():
    "Guarda todas as informações de uma ferramenta. Precisa de um ID."

    # Inicializando
    def __init__(self, id : int):
        self.id : int = id
        self.nome : str = None
        self.modelo : str = None
        self.fabricante : str = None
        self.specs : str = None
        self.registeredby : int = None
        self.registeredwhen : datetime.datetime = None
        self.modifiedwhen : datetime.datetime = None
        self.fotopath : str = None

        # Guardando uma variável com o nome do autor do equipamento
        self.nome_autor : str = None

        self.loaded : bool = False

    def __str__(self):
            if self.loaded:
                return f"""
                        ID: {self.id}\n
                        Nome: {self.nome},\n
                        Modelo: {self.modelo},\n
                        Fabricante: {self.fabricante},\n
                        Especificações: {self.specs}\n
                        Registrado por: {self.nome_autor} (ID {self.registeredby}),
                        Registrado em: {self.registeredwhen},
                        Última modificação em: {self.modifiedwhen}\n
                        Caminho da foto: {self.fotopath}
                        """
            else:
                return "A ferramenta ainda não foi carregada."
            
    def load_info(self):
        "Carrega do banco as informações do equipamento baseado no seu id."
        
        # Rodando query
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT nome, modelo, fabricante, specs, registeredby, registeredwhen, modifiedwhen, fotopath FROM ferramentas WHERE id = %s", (self.id,))
            search = cursor.fetchone()

        # Guardando na classe se houver encontrado
        if search:
            self.nome = search[0]
            self.modelo = search[1]
            self.fabricante = search[2]
            self.specs = search[3]
            self.registeredby = search[4]
            self.registeredwhen = search[5]
            self.modifiedwhen = search[6]
            self.fotopath = search[7]
            self.nome_autor = get_single_info_by_id(self.registeredby, "usuarios", "nome")

            self.loaded = True

class Registro():
    "Guarda todas as informações sobre um registro. Precisa de um ID."

    # Inicializando
    def __init__(self, id):
        self.id : int = id
        self.registeredby : int = None
        self.idequipamento : int = None
        self.data : datetime.datetime = None
        self.registro : str = None
        self.fotos : list[str] = None

        # Guardando o nome do autor e do equipamento
        self.nome_autor : str = None
        self.nome_equipamento : str = None

        self.loaded : bool = False

    def __str__(self):
            if self.loaded:
                return f"""
                        ID: {self.id}\n
                        Autor: {self.nome_autor} (ID {self.registeredby}),
                        Equipamento: {self.nome_equipamento} (ID {self.idequipamento}),
                        Registrado em: {self.data}\n
                        Caminhos de imagem: {self.fotos}\n
                        Registro: {self.registro}
                        """
            else:
                return "O registro ainda não foi carregada."
            
    def load_info(self):
        # Rodando queries
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT registeredby, idequipamento, data, registro FROM registros WHERE id = %s", (self.id,))
            infosearch = cursor.fetchone()

            # Pegando as fotos
            cursor.execute("SELECT fotopath FROM fotos_registros WHERE idregistro = %s", (self.id,))
            fotosearch = cursor.fetchall()
        
        # Adicionando informações
        if infosearch:
            self.registeredby = infosearch[0]
            self.idequipamento = infosearch[1]
            self.data = infosearch[2]
            self.registro = infosearch[3]

            self.nome_autor = get_single_info_by_id(self.registeredby, "usuarios", "nome")
            self.nome_equipamento = get_single_info_by_id(self.idequipamento, "equipamentos", "nome")

            self.loaded = True

            if fotosearch:
                self.fotos = [i[0] for i in fotosearch]

# Utilitarios
def string_insert(str, substring, pos) -> str:
    "Insere uma substring dentro da string passada na posição passada, e retorna o resultado."
    return str[:pos] + substring + str[pos+len(substring)-1:]

def format_time(time : datetime.datetime) -> str:
    "Formata a data em formato 'dia/mês/ano às hora:minuto:segundo'"
    return time.strftime("%d/%m/%Y às %H:%M:%S")

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

def limpar_imagens_inuteis() -> None:
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
            SELECT fotopath FROM ferramentas
            UNION
            SELECT fotopath FROM fotos_registros
            """
        )
        dirs = [i[0] for i in cursor.fetchall()]

    # Apagando todas as imagens que não estiverem na lista
    for i in os.listdir("uploads/images"):
        caminho = f"uploads/images/{i}"
        if(caminho not in dirs and os.path.exists(caminho)): os.remove(caminho)

def get_single_info_by_id(id : int, table : str, column : str):
    "Retorna um dado baseado no id especificado."

    with get_connection().cursor() as cursor:
        cursor.execute(f"SELECT {column} FROM {table} WHERE id = %s", (id,))
        search = cursor.fetchone()
        return search[0] if search else None

# Manipular banco
def get_connection() -> sqlconn.MySQLConnection:
    "Essa função retorna a conexão com o banco. Se não houver uma conexão feita, uma tentativa de conectar é realizada."

    sstate = st.session_state
    
    # Caso a variável ainda não esteja no session state, ou a conexão não estiver sendo feita, o código tenta uma conexão com o banco.
    if "conn" not in sstate or not sstate["conn"].is_connected():

        # Conectando
        conn = sqlconn.connect(**dbconfig)
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
        - Registro (VARCHAR(10000) not null)
    """

    # Criando o cursor
    cursor = get_connection().cursor()

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            senha VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            cpf VARCHAR(11) NOT NULL UNIQUE,
            admin BOOL NOT NULL,
            createdwhen DATETIME NOT NULL,
            enabled BOOL NOT NULL
        )
        """
    )

    # Tabela de equipamentos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS equipamentos(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
            FOREIGN KEY (registeredby) REFERENCES usuarios(id)
        )
        """
    )
    
    # Tabela de ferramenta
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ferramentas(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            modelo VARCHAR(255) NOT NULL,
            fabricante VARCHAR(255) NOT NULL,
            specs VARCHAR(2048) NOT NULL,
            registeredby INT NOT NULL,
            registeredwhen DATETIME NOT NULL,
            modifiedwhen DATETIME NOT NULL,
            fotopath VARCHAR(100),
            FOREIGN KEY (registeredby) REFERENCES usuarios(id)
        )
        """
    )

    # Tabela de registros
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registros(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            registeredby INT NOT NULL,
            idequipamento INT,
            data DATETIME NOT NULL,
            registro VARCHAR(2000),
            FOREIGN KEY (registeredby) REFERENCES usuarios(id),
            FOREIGN KEY (idequipamento) REFERENCES equipamentos(id)
        )
        """
    )

    # Tabela das fotos de registros
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fotos_registros(
            idregistro INT NOT NULL,
            fotopath VARCHAR(100)
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
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nome.upper(), senha_add, email, cpf, admin, current_datetime(), True)
            )
        get_connection().commit()
    except Error as e:
        get_connection().rollback()
        print(e)

def login(usuario : str | int, password : str | bytes) -> bool:
    "Retorna True ou False baseado na existência do usuário (identificado por e-mail, nome ou cpf) e se a senha está correta."

    # Checando se o usuário existe
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT senha, enabled FROM usuarios WHERE email = %s OR cpf = %s", (usuario, usuario))
        search = cursor.fetchone() # Pegando o usuário apenas

    if search: # algo foi encontrado
        if search[1]: # está ativado
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

def logout() -> None:
    "Sai do usuário atual."

    st.session_state.userinfo = tuple()
    st.session_state.logged = False

# Funções de equipamento
def novo_equipamento(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : int, foto : tuple | None = None) -> None:
    "Pede as informações e adiciona um equipamento ao banco. A tupla no argumento foto deve ser composta por (arquivo em bytes, diretório)."
    
    # Adicionando ao banco
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO equipamentos (nome, modelo, fabricante, estado, manutencao, periodo, registeredby, registeredwhen, modifiedwhen, fotopath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, modelo, fabricante, estado, manutencao, periodo, st.session_state.userinfo[0], current_datetime(), current_datetime(), f"uploads/{foto[1]}" if foto else None)
            )
        get_connection().commit()
        if(foto): upload_file(foto[0], foto[1])
    except Error as e:
        get_connection().rollback()
        print(e)

def show_basic_equip_info(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : str) -> None:
    "Exibe as informações básicas do equipamento."
    
    # Aplicando sombrinha em baixo das colunas
    col1, col2, col3 = st.columns(3, border=True)
    
    col1.write(f"Nome: {nome}")
    col1.write(f"Modelo: {modelo}")

    col2.write(f"Fabricante: {fabricante}")
    col2.write(f"Estado: {estado}")

    col3.write(f"Manutenção: {manutencao}")
    if periodo > 1: col3.write(f"Periodicidade: {periodo} em {periodo} {"mês" if periodo == 1 else "meses"}")
    else: col3.write("Periodicidade: Todo mês")

def vizualizar_equipamento(equip : Equipamento):
    "Função que mostra as informações do equipamento especificado com a busca."

    if equip.fotopath: 
        # Usando colunas para centralizar a imagem
        try:
            lcol, mcol, rcol = st.columns([.2, .6, .2])
            mcol.image(equip.fotopath, use_container_width=True)
        except Exception as e:
            st.error(":warning: Não foi possível carregar a imagem.")
            print(e)
    
    show_basic_equip_info(equip.nome, equip.modelo, equip.fabricante, equip.estado, equip.manucentao, equip.periodo)
    if not equip.fotopath: 
        st.caption("Nenhuma imagem encontrada.")
        st.divider()

    # Pesquisando nome de quem registrou e mostrando
    st.write(f"Registrado por: {equip.nome_autor}")
    st.write(f"Registrado em: {format_time(equip.registeredwhen)}")
    st.write(f"Modificado em: {format_time(equip.modifiedwhen)}")
        
# Funções de ferramenta
def novo_ferramenta(nome : str, modelo : str, fabricante : str, specs : str, foto : tuple | None = None) -> None:
    "Pede as informações e adiciona a ferramenta ao banco. A tupla da foto deve conter (arquivo em bytes, diretório)"
    
    # Adicionando ao banco
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ferramentas (nome, modelo, fabricante, specs, registeredby, registeredwhen, modifiedwhen, fotopath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, modelo, fabricante, specs, st.session_state.userinfo[0], current_datetime(), current_datetime(), f"uploads/{foto[1]}" if foto else None)
            )
        get_connection().commit()
        if(foto): upload_file(foto[0], foto[1])
    except Error as e:
        get_connection().rollback()
        print(e)

def show_basic_tool_info(nome : str, modelo : str, fabricante : str, specs : str) -> None:
    "Exibe as informações básicas do equipamento."

    st.subheader("Informações", divider="gray")
    st.text(f"Nome: {nome}\nModelo: {modelo}\nFabricante: {fabricante}")
    
    st.subheader("Especificações", divider="gray")
    st.text(specs)
    
def vizualizar_ferramenta(tool : Ferramenta):
    "Função que mostra as informações da ferramenta especificado com a busca."

    if(tool.fotopath):
        col1, col2 = st.columns(2, border=True, vertical_alignment="center")

        with col1:
            # Usando colunas para centralizar a imagem
            try:
                st.image(tool.fotopath, use_container_width=True)
            except Exception as e:
                st.error(":warning: Não foi possível carregar a imagem.")
                print(e)
        
        with col2:
            show_basic_tool_info(tool.nome, tool.modelo, tool.fabricante, tool.specs)
    else:
        with st.container(border=True):
            show_basic_tool_info(tool.nome, tool.modelo, tool.fabricante, tool.specs)
            st.caption("Nenhuma imagem encontrada.")

    # Pesquisando nome de quem registrou e mostrando
    st.write(f"Registrado por: {tool.nome_autor}")
    st.write(f"Registrado em: {format_time(tool.registeredwhen)}")
    st.write(f"Modificado em: {format_time(tool.modifiedwhen)}")

# Funções de registros
def novo_registro(idequipamento : int, registro : str, fotos : list[tuple[int, int]] | None = None):
    "Pede as informações e adiciona um registro ao banco. A lista deve conter apenas tuplas, compostas por (arquivo em bytes, diretório)"

    # Adicionando registro
    try:
        get_connection().start_transaction()
        
        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO registros (registeredby, idequipamento, data, registro)
                VALUES (%s, %s, %s, %s)
                """, (st.session_state.userinfo[0], idequipamento, current_datetime(), registro)
            )

            # Fazendo uma lista de tuplas com os valores pra colocar na tabela de fotos
            fotos_add = [(cursor.lastrowid, f"uploads/{i[1]}") for i in fotos]
            cursor.executemany(
                """
                INSERT INTO fotos_registros (idregistro, fotopath)
                VALUES (%s, %s)
                """, (fotos_add)
            )
        get_connection().commit()

        # Fazendo upload das fotos
        for i in fotos:
            upload_file(i[0], f"{i[1]}")

    except Error as e:
        get_connection().rollback()
        print(e)

def vizualizar_registro(registro : Registro):
    "Exibe todas as informações sobre o registro com o ID especificado."

    infocol1, infocol2 = st.columns([4, 6])

    with infocol1:
        st.subheader("Informações:", divider="gray")
        st.write(f"Autor: {registro.nome_autor}")
        st.write(f"Equipamento: {registro.nome_equipamento}")
        st.write(f"Registrado em: {format_time(registro.data)}")

    with infocol2:
        st.subheader("Registro:", divider="gray")
        st.text(registro.registro)

    st.divider()

    # Mostrando imagens
    if registro.fotos:
        try:
            # Aplicando sombrinha em baixo das imagens, e centralizando conteúdo nos containers
            st.markdown(
                """
                <style>
                [data-testid="stImage"] {
                    box-shadow: rgb(0 0 0 / 20%) 0px 2px 1px -1px, rgb(0 0 0 / 14%) 0px 1px 1px 0px, rgb(0 0 0 / 12%) 0px 1px 3px 0px;
                    border-radius: 15px;
                    padding: 10%;
                } 
                </style>
                """, unsafe_allow_html=True
            )

            cols = 3
            imgcols = [i for i in st.columns(cols)]
            qtd_fotos = len(registro.fotos)

            # Renderizando em colunas diferentes dependendo da quantidade de imagens
            if qtd_fotos == 1:
                imgcols[1].image(registro.fotos[0])
            elif qtd_fotos == 2:
                imgcols[0].image(registro.fotos[0])
                imgcols[2].image(registro.fotos[1])
            else:
                for i in range(qtd_fotos):
                    imgcols[i % cols].image(registro.fotos[i])

        except Exception as e:
            st.error(":warning: Não foi possível carregar a imagem.")
            print(e)
    else:
        st.caption("Este registro não contém fotos.")