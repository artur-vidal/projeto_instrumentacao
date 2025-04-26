import pandas as pd
import mysql.connector as sqlconn
import streamlit as st
import os, bcrypt

# Utilitarios
def string_insert(str, substring, pos) -> str:
    "Insere uma substring dentro da string passada na posição passada, e retorna o resultado."
    return str[:pos] + substring + str[pos+len(substring)-1:]

def input_notnull(text = "") -> str:
    "Igual a um input(), mas não aceita valores vazios."

    var = input(text)
    while var == "": var = input(text)
    return var

def input_choice(text = "", *args : str) -> str:
    "Pega uma entrada do usuário e filtra baseado nas escolhas que ele passar."

    var = input_notnull(text)
    while var not in args: var = input_notnull(text)
    return var

def title(text : str) -> None:
    "Limpa o console e printa uma linha de título."

    os.system("cls")
    print(text.center(50, "-"))

def unlogged_redirect() -> None:
    "Redireciona o usuário até a página inicial caso ele tente entrar em alguma página que necessite de login, mas sem estar logado."

    if not is_logged(st.session_state["logged"]): st.switch_page("pages/home.py")

def not_admin_redirect() -> None:
    "Redireciona o usuário para a página inicial se ele tentar entrar em alguma aba de administrador sem ter permissão."

    if not st.session_state["logged"].get("admin"): st.switch_page("pages/home.py")
# Manipular banco
def get_connection() -> sqlconn.MySQLConnection:
    "Essa função retorna a conexão com o banco. Se não houver uma conexão feita, uma tentativa de conectar é realizada."

    # Caso a variável ainda não esteja no session state, ou a conexão não estiver sendo feita, o código tenta uma conexão com o banco.
    if "conn" not in st.session_state or not st.session_state["conn"].is_connected():
        conn = sqlconn.connect(
            host="localhost",
            user="root",
            password="senhabanco",
            database="manutencao"
        )
        st.session_state["conn"] = conn
    return st.session_state["conn"]

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
        - Ferramentas (VARCHAR(255) not null)
        - Periodicidade (INT not null)
    
    Ferramentas 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Modelo (VARCHAR(255) not null)
        - Fabricante (VARCHAR(255) not null)
        - Specs (VARCHAR(255) not null)

    Usuários 
        - ID (INT not null primary key auto_increment)
        - Nome (VARCHAR(255) not null)
        - Senha (VARCHAR(255) not null)
        - Email (VARCHAR(255) not null unique)
        - CPF (VARCHAR(11) not null unique)
        - Administrator (BOOL not null)

    Registros
        - ID (INT not unll primary key auto_increment)
        - IDusuario (INT FK (idusuario))
        - IDequipamento (INT FK (idequipamento))
        - Data (DATETIME NOT NULL)
        - Registro (VARCHAR(10000) NOT NULL)
    """

    # Criando o cursor
    cursor = get_connection().cursor()

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
            periodo INT NOT NULL
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
            specs VARCHAR(255) NOT NULL
        )
        """
    )

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            idusuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            senha VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            cpf VARCHAR(11) UNIQUE,
            admin BOOL NOT NULL
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
            registro VARCHAR(10000) NOT NULL,
            FOREIGN KEY (idusuario) REFERENCES usuarios(idusuario),
            FOREIGN KEY (idequipamento) REFERENCES equipamentos(idequipamento)
        )
        """
    )

    # Salvando as alterações com commit() e fechando o cursor.
    get_connection().commit()
    cursor.close()

def limpar_tabela(tabela : str) -> None:
    "Função de debug para limpar uma tabela."

    # Criando conexão e cursor
    cursor = get_connection().cursor()

    # Limpando
    cursor.execute(f"DELETE FROM {tabela}")

    # Commitando e fechando cursor
    get_connection().commit()
    cursor.close()

def mostrar_tabela(tabela : str) -> None:
    "Imprime a tabela escolhida no console"

    title(f"TABELA \"{tabela}\"")

    # Lendo a tabela com pandas para conseguir printar
    print(pd.DataFrame(pd.read_sql(f"SELECT * FROM {tabela}", get_connection())))
    
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
            if(email[atpos+1:] == "" or email[atpos+1] in [" ", "."]):
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

    # Criando cursor
    cursor = get_connection().cursor()

    # Hasheando senha
    senha_add = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

    # Adicionando o usuário no banco:
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, senha, email, cpf, admin)
            VALUES (%s, %s, %s, %s, %s)
            """, (nome.upper(), senha_add, email, cpf, admin)
        )
    except Exception as e:
        print(e)

    # Commitando e fechando a conexão
    get_connection().commit()
    cursor.close()

def login(usuario : str | int, password : str | bytes) -> bool:
    "Retorna True ou False baseado na existência do usuário (identificado por e-mail, nome ou cpf) e se a senha está correta."

    # Criando conexão pra checar os dados
    cursor = get_connection().cursor()

    # Checando se o usuário existe
    cursor.execute("SELECT senha FROM usuarios WHERE nome = %s OR email = %s OR cpf = %s", (usuario.upper(), usuario, usuario))
    search = cursor.fetchone() # Pegando o usuário apenas
    retorno = None # Valor de retorno. Faço uma variável pois quero retornar só no fim

    if search: # algo foi encontrado

        # Guardando a senha
        senha = search[0]

        # Descriptografando e verificando
        # comparo as duas séries de bytes, se forem iguais, retorna True
        if bcrypt.checkpw(password.encode("utf-8"), senha.encode("utf-8")): 
            retorno = True
        else:
            retorno = False
    else:
        retorno = False
    
    # Fechando cursor
    cursor.close()

    return retorno

def mudar_senha(usuario : str, password : str) -> None:
    "Muda a senha do usuário desejado. Printa um erro caso o usuário não exista. Só deve ser usada pelo administrador."

    # Conectando
    cursor = get_connection().cursor()

    # Pegando por e-mail ou nome
    inserido = "nome"
    if check_email(usuario): inserido = "email" # se for um email
    elif check_cpf(usuario): inserido = "cpf" # se for um usuário

    # Executando
    cursor.execute("UPDATE usuarios SET senha = %s WHERE %s = %s", (password, inserido, usuario))

    # Fechando conexão
    cursor.commit()
    cursor.close()

def is_logged(user_session_state : dict) -> bool:
    "Retorna True se todos os valores estiverem preenchidos."
    return None not in user_session_state.values()

# Funções de equipamento
def novo_equipamento(nome : str, modelo : str, fabricante : str, estado : str, manutencao : str, periodo : int) -> None:
    "Pede as informações e adiciona um equipamento ao banco."
    
    # Conectando e criando cursor
    cursor = get_connection().cursor()

    # Adicionando ao banco
    try:
        cursor.execute(
            """
            INSERT INTO equipamentos (nome, modelo, fabricante, estado, manutencao, periodo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, modelo, fabricante, estado, manutencao, periodo)
        )
    except Exception as e:
        print(e)

    # Commitando e fechando conexão
    get_connection().commit()
    cursor.close()

def achar_equipamentos(equip : str) -> tuple | None:
    "Pede ao usuário que insira o ID ou nome do modelo, procura esse equipamento na tabela e o retorna. Caso não encontre, retorna None."

    # Conectando
    cursor = get_connection().cursor()
    # As porcentagem dizem ao MySQL para procurar qualquer texto que CONTENHA essa string.
    termo_pesquisa = f"%{equip}%".lower() # lower() para padronizar a pesquisa

    if(equip.isdigit()): # É um ID
        cursor.execute("SELECT * FROM equipamentos WHERE idequipamento = %s ORDER BY nome ASC", (int(equip),))
    else: # É outra coisa

        # O like permite a busca por contenção de texto
        cursor.execute(
            """
            SELECT * FROM equipamentos 
            WHERE LOWER(nome) LIKE %s OR LOWER(modelo) LIKE %s OR LOWER(fabricante) LIKE %s OR LOWER(estado) LIKE %s
            ORDER BY nome ASC
            """,
            (termo_pesquisa, termo_pesquisa, termo_pesquisa, termo_pesquisa)
    )
    search = cursor.fetchall() # Guardando a busca

    # Desconectando
    cursor.close()

    return search

# Funções de ferramenta
def novo_ferramenta(nome : str, modelo : str, fabricante : str, specs : str) -> None:
    "Pede as informações e adiciona a ferramenta ao banco."
    
    # Conectando e criando cursor
    cursor =  get_connection().cursor()

    # Adicionando ao banco
    try:
        cursor.execute(
            """
            INSERT INTO ferramentas (nome, modelo, fabricante, specs)
            VALUES (%s, %s, %s, %s)
            """, (nome, modelo, fabricante, specs)
        )
    except Exception as e:
        print(e)

    # Commitando e fechando cursor
    get_connection().commit()
    cursor.close()

def achar_ferramentas(ferramenta : str) -> tuple | None:
    "Pede ao usuário que insira o ID ou nome do modelo, procura essa ferramenta na tabela e a retorna. Caso não encontre, retorna None."

    # Conectando
    cursor = get_connection().cursor()

    # Criando termo de pesquisa por contenção de texto
    termo_pesquisa = f"%{ferramenta}%"

    if(ferramenta.isdigit()): # É um ID
        # Buscando e ordenando por ordem crescente
        cursor.execute("SELECT * FROM equipamentos WHERE idequipamento = %s ORDER BY nome ASC", (int(ferramenta),))
    else: # É outra coisa

        # O like permite a busca por contenção de texto
        cursor.execute(
            """
            SELECT * FROM equipamentos 
            WHERE LOWER(nome) LIKE %s OR LOWER(modelo) LIKE %s OR LOWER(fabricante) LIKE %s OR LOWER(specs) LIKE %s
            ORDER BY nome ASC
            """,
            (termo_pesquisa, termo_pesquisa, termo_pesquisa, termo_pesquisa)
    )
    search = cursor.fetchall()

    # Desconectando
    cursor.close()

    return search

if __name__ == "__main__":
    ...