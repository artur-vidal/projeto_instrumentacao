import mysql.connector as sqlconn
from mysql.connector import Error
import streamlit as st
from pathlib import Path
import os, bcrypt, datetime, uuid, re, json, openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

log_file = os.path.join(LOG_DIR, f'{datetime.datetime.now().replace(microsecond=0).strftime("%d%m%Y_log.log")}')

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

    # Representação em string
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
        close_connection()

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
        self.modifiedby : int = None
        self.modifiedwhen : datetime.datetime = None
        self.fotopath : str = None

        # Guardando uma variável com o nome do autor do equipamento
        self.nome_autor : str = None
        self.nome_modif : str = None

        # Variável que representa o estado de carregamento da classe (carregado/não carregado)
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
                        Registrado por: {self.nome_modif} (ID {self.modifiedby}),
                        Última modificação em: {self.modifiedwhen}\n
                        Caminho da foto: {self.fotopath}
                        """
            else:
                return "O equipamento ainda não foi carregado."
    
    def load_info(self):
        "Carrega do banco as informações do equipamento baseado no seu id."
        
        # Rodando query
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT nome, modelo, fabricante, estado, manutencao, periodo, registeredby, registeredwhen, modifiedby, modifiedwhen, fotopath FROM equipamentos WHERE id = %s", (self.id,))
            search = cursor.fetchone()
        close_connection()

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
            self.modifiedby = search[8]
            self.modifiedwhen = search[9]
            self.fotopath = search[10]

            self.nome_autor = get_single_info_by_id(self.registeredby, "usuarios", "nome")
            self.nome_modif = get_single_info_by_id(self.modifiedby, "usuarios", "nome")

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
        self.modifiedby : int = None
        self.modifiedwhen : datetime.datetime = None
        self.fotopath : str = None

        # Guardando uma variável com o nome do autor do equipamento
        self.nome_autor : str = None
        self.nome_modif : str = None

        # Variável que representa o estado de carregamento da classe (carregado/não carregado)
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
                        Modificado por: {self.nome_modif} (ID {self.modifiedby}),
                        Última modificação em: {self.modifiedwhen}\n
                        Caminho da foto: {self.fotopath}
                        """
            else:
                return "A ferramenta ainda não foi carregada."
            
    def load_info(self):
        "Carrega do banco as informações do equipamento baseado no seu id."
        
        # Rodando query
        with get_connection().cursor() as cursor:
            cursor.execute("SELECT nome, modelo, fabricante, specs, registeredby, registeredwhen, modifiedby, modifiedwhen, fotopath FROM ferramentas WHERE id = %s", (self.id,))
            search = cursor.fetchone()
        close_connection()

        # Guardando na classe se houver encontrado
        if search:
            self.nome = search[0]
            self.modelo = search[1]
            self.fabricante = search[2]
            self.specs = search[3]
            self.registeredby = search[4]
            self.registeredwhen = search[5]
            self.modifiedby = search[6]
            self.modifiedwhen = search[7]
            self.fotopath = search[8]

            self.nome_autor = get_single_info_by_id(self.registeredby, "usuarios", "nome")
            self.nome_modif = get_single_info_by_id(self.modifiedby, "usuarios", "nome")

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

        # Variável que representa o estado de carregamento da classe (carregado/não carregado)
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
        close_connection()
        
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

def generate_filename(extension) -> str:
    "Gera um nome de arquivo a partir de um UUID v4."
    return f"{uuid.uuid4()}{extension}"

def upload_file(file_content : bytes, file_path : str) -> None:
    "Faz o upload de um arquivo ao servidor, dentro da pasta 'uploads'."

    # Escrevendo arquivo
    # Criando pasta uploads se ela ainda não existir
    os.makedirs("uploads", exist_ok=True)

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
    close_connection()

    # Criando pastas se não existirem
    if not os.path.exists("uploads/images"): os.makedirs("uploads/images")

    count = 0

    # Apagando todas as imagens que não estiverem na lista
    for i in os.listdir("uploads/images"):
        caminho = f"uploads/images/{i}"
        if(caminho not in dirs and os.path.exists(caminho)): 
            count += 1
            os.remove(caminho)

    # Mostrando uma mensagem
    st.toast(f"{count} imagens removidas!")

def get_single_info_by_id(id : int, table : str, column : str):
    "Retorna um dado baseado no id especificado."

    retorno = None
    try:
        with get_connection().cursor() as cursor:
            cursor.execute(f"SELECT {column} FROM {table} WHERE id = %s", (id,))
            search = cursor.fetchone()
            if search: retorno = search[0]
    except Error as e:
        print(e)
    finally:
        close_connection()
        return retorno

def register_log(log : str) -> None:
    "Registra um log no arquivo do dia, em /logs."

    os.makedirs("logs", exist_ok=True)

    with open(log_file, "a+") as f:
        f.write(f"[{current_datetime().strftime("%d-%m-%Y | %H:%M:%S")}] {log}\n")

# Manipular banco
def get_connection() -> sqlconn.MySQLConnection:
    "Essa função retorna a conexão com o banco. Se não houver uma conexão feita, uma tentativa de conectar é realizada."

    sstate = st.session_state
    
    # Caso a variável ainda não esteja no session state, ou a conexão não estiver sendo feita, o código tenta uma conexão com o banco.
    if "conn" not in sstate or not sstate["conn"].is_connected():

        # Lendo o arquivo de configuração e guardando na variável
        with open(os.path.join(CONFIG_DIR, "config_banco.json")) as config:
            dbconfig = json.load(config)
        
        # Conectando com as informações da variável descompactada
        sstate["conn"] = sqlconn.connect(**dbconfig)
        print("Conexão MySQL iniciada.")

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

    Usuários 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Senha (VARCHAR(255) not null)
        - Email (VARCHAR(255) not null unique)
        - CPF (VARCHAR(11) not null unique)
        - Administrator (BOOL not null)
        - Criado em (DATETIME not null)
        - Ativo (BOOL not null)

    Equipamentos 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Modelo (VARCHAR(255) not null)
        - Fabricante (VARCHAR(255) not null)
        - Estado (VARCHAR(255) not null)
        - Tipo de Manutenção (VARCHAR(255) not null)
        - Periodicidade (INT not null)
        - Registrado por (INT FK usuarios(id) not null)
        - Registrado em (DATETIME not null)
        - Modificado por (INT FK usuarios(id) not null)
        - Modificado em (DATETIME not null)
        - Caminho da Foto (VARCHAR(100))
    
    Ferramentas 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Modelo (VARCHAR(255) not null)
        - Fabricante (VARCHAR(255) not null)
        - Specs (VARCHAR(255) not null)
        - Registrado por (INT FK usuarios(id) not null)
        - Registrado em (DATETIME not null)
        - Modificado por (INT FK usuarios(id) not null)
        - Modificado em (DATETIME not null) 
        - Caminho da Foto (VARCHAR(100))

    Registros
        - ID (INT not unll primary key auto_increment)
        - Autor (INT FK usuarios(id))
        - IDequipamento (INT FK equipamentos(id))
        - Data (DATETIME not null)
        - Registro (VARCHAR(2000) not null)
    
    Fotos dos Registros
        - IDregistro (INT FK registros(id) not null)
        - Caminho (VARCHAR(100) not null)
    """

    try:
        get_connection().start_transaction()
        with get_connection().cursor() as cursor:
            # Tabela de usuários
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios(
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    senha VARCHAR(255),
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
                    modifiedby INT NOT NULL,
                    modifiedwhen DATETIME NOT NULL,
                    fotopath VARCHAR(100),
                    FOREIGN KEY (registeredby) REFERENCES usuarios(id),
                    FOREIGN KEY (modifiedby) REFERENCES usuarios(id)
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
                    modifiedby INT NOT NULL,
                    modifiedwhen DATETIME NOT NULL,
                    fotopath VARCHAR(100),
                    FOREIGN KEY (registeredby) REFERENCES usuarios(id),
                    FOREIGN KEY (modifiedby) REFERENCES usuarios(id)
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
    except Error as e:
        get_connection().rollback()
        print(e)
    finally:
        close_connection()

# Funções pra usuário
def check_cpf(cpf : int) -> int | None:
    "Pega um CPF via input() e o retorna se for válido. Caso contrário, retorna None"

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
    "Pega um email e o retorna após validação. Retorna None se for inválido. exemplo@dominio.com"

    # Usando regex para validar o email

    # Primeiro pedaço - pode conter letras minúsculas, maiúsculas, dígitos, ponto, underline e hífen
    # Segundo pedaço (pós @) - pode conter letras minúsculas, maiúsculas, dígitos, ponto, underline e hífen
    # Terceiro pedaço (depois do último ponto) - pode conter apenas letras minúsculas ou maiúsculas
    valido = re.search(r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", email)
    return bool(valido)

def format_cpf(cpf : str) -> str:
    "Formata um CPF com os traços e hífens."

    # Fazendo a versão formatada
    cpf_format = str(cpf)
    cpf_format = string_insert(cpf_format, ".", 3) # ponto 1
    cpf_format = string_insert(cpf_format, ".", 7) # ponto 2
    cpf_format = string_insert(cpf_format, "-", 11) # hífen

    return cpf_format

def novo_usuario(nome : str, cpf : str, email : str, admin : bool) -> None:
    "A função vai requisitar todos os dados para criar um usuário e adicionará-o ao banco."

    # Adicionando o usuário no banco
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen, enabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nome.upper(), None, email, cpf, admin, current_datetime(), True)
            )
        get_connection().commit()

        register_log(f"Usuário '{nome.upper()}' criado por {st.session_state.userinfo[2].upper()}")
    except Error as e:
        get_connection().rollback()
        print(e)
    finally:
        close_connection()

def login(usuario : str, password : str | bytes) -> bool:
    "Retorna True ou False baseado na existência do usuário (identificado por e-mail, nome ou cpf) e se a senha está correta."

    # Checando se o usuário existe
    with get_connection().cursor() as cursor:
        cursor.execute("SELECT senha, enabled FROM usuarios WHERE email = %s OR cpf = %s", (usuario, usuario))
        search = cursor.fetchone() # Pegando o usuário apenas
    close_connection()

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

    # Registrando
    register_log(f"{st.session_state.userinfo[2]} fez LOGOUT")

    # Limpando sessão
    st.session_state.userinfo = tuple()
    st.session_state.logged = False

@st.dialog("Definir Senha")
def set_password_dialog(user):

    with st.form("set-pass"):
        # Criando text input com observação
        senha = st.text_input("Insira a senha do seu usuário:red[*] (mínimo 8 caracteres)", type="password")
        st.caption(":red[*]A senha só poderá ser definida novamente com ajuda do administrador.")

        senha_confirma = st.text_input("Confirme a senha:", type="password")

        # Variável que permite a alteração das senhas
        pode_registrar = senha != None and len(senha) >= 8 and senha == senha_confirma

        # Mostrando textos para o usuário
        texto = st.empty()
        with texto:   
            if (senha != None and senha != "") and (senha_confirma != None and senha_confirma != "") and len(senha) >= 8:     
                if senha == senha_confirma: st.success("As senhas batem.", icon=":material/check:")   
                else: st.error("As senhas estão diferentes.", icon=":material/close:")
        
        # Espaço pra erro
        erro_area = st.empty()

        # Botão de definir, rodo a query pra atualizar a senha daquele usuário
        if st.form_submit_button("Definir", use_container_width=True):
            if len(senha) < 8:
                # Avisando se a senha for muito pequena
                with erro_area:
                    st.error("Insira uma senha com 8 ou mais caracteres.")
            elif pode_registrar:
                # Rodando query
                try:
                    get_connection().start_transaction()

                    with get_connection().cursor() as cursor:
                        cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s OR cpf = %s", (bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()), user, user))

                    get_connection().commit()
                    st.rerun()
                except Error as e:
                    get_connection().rollback()
                    print(e)
                finally:
                    close_connection()

# Funções de equipamento
def novo_equipamento(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : int, foto : tuple | None = None) -> None:
    "Pede as informações e adiciona um equipamento ao banco. A tupla no argumento foto deve ser composta por (arquivo em bytes, diretório)."
    
    # Adicionando ao banco
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO equipamentos (nome, modelo, fabricante, estado, manutencao, periodo, registeredby, registeredwhen, modifiedby, modifiedwhen, fotopath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, modelo, fabricante, estado, manutencao, periodo, st.session_state.userinfo[0], current_datetime(), st.session_state.userinfo[0], current_datetime(), f"uploads/{foto[1]}" if foto else None)
            )
        get_connection().commit()

        register_log(f"Usuário {st.session_state.userinfo[2]} registrou EQUIPAMENTO {nome}")

        # Se tem alguma foto, eu faço upload dela.
        if(foto): upload_file(foto[0], foto[1]) 
    except Error as e:
        get_connection().rollback()
        print(e)
    finally:
        close_connection()

def show_basic_equip_info(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : str) -> None:
    "Exibe as informações básicas do equipamento."
    
    col1, col2, col3 = st.columns(3, border=True)
    
    col1.write(f"Nome: {nome}")
    col1.write(f"Modelo: {modelo}")

    col2.write(f"Fabricante: {fabricante}")
    col2.write(f"Estado: {estado}")

    col3.write(f"Manutenção: {manutencao}")
    if periodo > 1: col3.write(f"Periodicidade: {periodo} em {periodo} meses") # Se o período for maior que 1, exibo no formato X em X meses.
    else: col3.write("Periodicidade: Todo mês") # Se for 1, escrevo "Todo mês"

def vizualizar_equipamento(equip : Equipamento) -> None:
    "Função que mostra as informações do equipamento especificado com a busca."

    # Exibindo foto se ela existir
    if equip.fotopath: 
        # Usando colunas para centralizar a imagem
        try:
            lcol, mcol, rcol = st.columns([.2, .6, .2])
            mcol.image(equip.fotopath, use_container_width=True)
        except Exception as e:
            st.error(":warning: Não foi possível carregar a imagem.")
            print(e)
    
    show_basic_equip_info(equip.nome, equip.modelo, equip.fabricante, equip.estado, equip.manucentao, equip.periodo)

    # Se não, eu mostro que não tem nenhuma.
    if not equip.fotopath: 
        st.caption("Nenhuma imagem encontrada.")
        st.divider()

    # Mostrando informações de edição/registro
    if st.session_state.userinfo[1]:
        cm_cols = st.columns(2, border=True)
        cm_cols[0].write(f"Registrado por: {equip.nome_autor}")
        cm_cols[0].write(f"Registrado em: {format_time(equip.registeredwhen)}")

        cm_cols[1].write(f"Modificado por: {equip.nome_modif}")
        cm_cols[1].write(f"Modificado em: {format_time(equip.modifiedwhen)}")
    else:
        st.write(f"Registrado por: {equip.nome_autor}")
        st.write(f"Registrado em: {format_time(equip.registeredwhen)}")
        
# Funções de ferramenta
def novo_ferramenta(nome : str, modelo : str, fabricante : str, specs : str, foto : tuple | None = None) -> None:
    "Pede as informações e adiciona a ferramenta ao banco. A tupla da foto deve conter (arquivo em bytes, diretório)"
    
    # Adicionando ao banco
    try:
        get_connection().start_transaction()

        with get_connection().cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ferramentas (nome, modelo, fabricante, specs, registeredby, registeredwhen, modifiedby, modifiedwhen, fotopath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, modelo, fabricante, specs, st.session_state.userinfo[0], current_datetime(), st.session_state.userinfo[0], current_datetime(), f"uploads/{foto[1]}" if foto else None)
            )
        get_connection().commit()

        register_log(f"Usuário {st.session_state.userinfo[2]} registrou FERRAMENTA {nome}")

        # Se tem uma foto, eu faço upload dela.
        if(foto): upload_file(foto[0], foto[1])
    except Error as e:
        get_connection().rollback()
        print(e)
    finally:
        close_connection()

def show_basic_tool_info(nome : str, modelo : str, fabricante : str, specs : str) -> None:
    "Exibe as informações básicas do equipamento."

    st.subheader("Informações", divider="gray")
    st.text(f"Nome: {nome}\nModelo: {modelo}\nFabricante: {fabricante}")
    
    st.subheader("Especificações", divider="gray")
    st.text(specs)
    
def vizualizar_ferramenta(tool : Ferramenta) -> None:
    "Função que mostra as informações da ferramenta especificado com a busca."

    # Exibindo com layout de foto se houver uma
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
    # Se não houver foto, exibindo layout padrão
    else:
        with st.container(border=True):
            show_basic_tool_info(tool.nome, tool.modelo, tool.fabricante, tool.specs)
            st.caption("Nenhuma imagem encontrada.")

    # Mostrando informações de edição/registro
    if st.session_state.userinfo[1]:
        cm_cols = st.columns(2, border=True)
        cm_cols[0].write(f"Registrado por: {tool.nome_autor}")
        cm_cols[0].write(f"Registrado em: {format_time(tool.registeredwhen)}")

        cm_cols[1].write(f"Modificado por: {tool.nome_modif}")
        cm_cols[1].write(f"Modificado em: {format_time(tool.modifiedwhen)}")
    else:
        st.write(f"Registrado por: {tool.nome_autor}")
        st.write(f"Registrado em: {format_time(tool.registeredwhen)}")

# Funções de registros
def novo_registro(idequipamento : int, registro : str, fotos : list[tuple[int, int]] | None = None) -> None:
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

            if fotos:
                # Fazendo uma lista de tuplas com os valores necessários pra colocar na tabela de fotos
                fotos_add = [(cursor.lastrowid, f"uploads/{i[1]}") for i in fotos]
                cursor.executemany(
                    """
                    INSERT INTO fotos_registros (idregistro, fotopath)
                    VALUES (%s, %s)
                    """, (fotos_add)
                )

        get_connection().commit()

        register_log(f"Usuário {st.session_state.userinfo[2]} registrou MANUTENÇÃO para EQUIPAMENTO {get_single_info_by_id(idequipamento, "equipamentos", "nome")}")

        # Fazendo upload das fotos
        if fotos:
            for i in fotos:
                upload_file(i[0], f"{i[1]}")

    except Error as e:
        get_connection().rollback()
        print(e)
    
    finally:
        close_connection()

def vizualizar_registro(registro : Registro) -> None:
    "Exibe todas as informações sobre o registro com o ID especificado."

    # Layout das informações
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

# Funções de importação
def import_users(excel_file_bytes : bytes, rows : int = 10) -> None:
    "Lê todos os dados de usuários de uma planilha e os adiciona após validação."

    # Carregando a planilha
    planilha = openpyxl.load_workbook(excel_file_bytes)

    # Guardando a página em uma variável (primeira página)
    users_sheet = planilha[planilha.sheetnames[0]]

    # Guardando os usuários em uma lista
    # 0 - Nome, 1 - Email, 2 - CPF, 3 - Senha, 4 - Admin
    users = []
    for row in users_sheet.iter_rows(min_row=2, max_row=2+rows):
        info = [row[i].value for i in range(5)]
        if all(info[:4]) and info[4] is not None:
            users.append(info)

    # FAZENDO VERIFICAÇÕES
    # Validação de Síntaxe e Duplicatas
    user_amount = len(users)
    emails, cpfs = set(), set() # O tamanho desses dois sets tem que ser igual à quantidade de usuários

    valid = True # Se torna False no momento em que alguma verificação falha
    error_results = [] # Guarda as mensagens de erro

    # Iterando
    for i in range(len(users)):
        emails.add(users[i][1])
        cpfs.add(users[i][2])

        if not check_email(users[i][1]):
            valid = False
            error_results.append(f"E-mail inválido na ***linha {i + 2}***.")

        if not check_cpf(users[i][2]):
            valid = False
            error_results.append(f"CPF inválido na ***linha {i + 2}***.")

    # Verificando tamanho
    if not len(emails) == user_amount: 
        valid = False
        error_results.append("Há algum e-mail duplicado na planilha.")
    if not len(cpfs) == user_amount: 
        valid = False
        error_results.append("Há algum CPF duplicado na planilha.")

    # Rodando tarefas
    if valid:
        
        # Guardando os dados para a query em uma lista
        users_add = []
        for user in users:
            # Nome, Senha, E-mail, CPF, Admin, Data de criação, Ativado
            users_add.append([user[0].upper(), bcrypt.hashpw(user[3].encode("utf-8"), bcrypt.gensalt()), user[1], user[2], user[4], current_datetime(), True])

        # Transação
        try:
            get_connection().start_transaction()

            with get_connection().cursor() as cursor:
                cursor.executemany("INSERT INTO usuarios (nome, senha, email, cpf, admin, createdwhen, enabled) VALUES (%s, %s, %s, %s, %s, %s, %s)", users_add)

            get_connection().commit()

            # Mensagenzinha de sucesso :D
            st.success("Usuários cadastrados com sucesso!")
        except Error as e:
            get_connection().rollback()

            # Notificando erro
            st.error("Ocorreu um erro durante o cadastro.")
            print(e)
        finally:
            close_connection()

    # Printando erros caso algum tenha ocorrido
    else:
        for i in error_results: st.error(i)