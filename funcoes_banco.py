import sqlite3 as sql
import pandas as pd
import os, bcrypt, pathlib

if not pathlib.Path("db").exists(): os.makedirs("db") 
dbpath = "db/banco.db"

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
    
# Manipular banco
def criar_tabelas() -> None:
    """Cria as tabelas de equipamentos, ferramentas e usuários, caso não existam. Passa por cada uma individualmente.

    Equipamentos 
        - Nome (string not null)
        - Modelo (string not null primary key)
        - Fabricante (string)
        - Estado (string)
        - Tipo de Manutenção (string)
        - Ferramentas (string)
        - Periodicidade (inteiro)
    
    Ferramentas 
        - Nome (string not null)
        - Modelo (string not null primary key)
        - Fabricante (string)
        - Estado (string)

    Usuários 
        - Nome (string not null)
        - Senha (string not null)
        - Email (string not null primary key)
        - CPF (inteiro único)
        - CPF formatado (string)
    """

    # Criando a conexão
    db = sql.connect(dbpath)
    cursor = db.cursor()

    # Tabela de equipamentos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS equipamentos(
            nome TEXT NOT NULL,
            modelo TEXT NOT NULL PRIMARY KEY,
            fabricante TEXT,
            estado TEXT,
            tipo_manutencao TEXT,
            ferramentas TEXT,
            periodo_meses INT
        )
        """
    )
    
    # Tabela de ferramenta
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ferramentas(
            nome TEXT NOT NULL,
            modelo TEXT NOT NULL PRIMARY KEY,
            fabricante TEXT,
            estado TEXT
        )
        """
    )

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            email TEXT NOT NULL PRIMARY KEY,
            cpf INT UNIQUE,
            cpf_format TEXT,
            admin BOOL NOT NULL
        )
        """
    )

    # Salvando as alterações com commit() e fechando conexão.
    db.commit()
    db.close()

def limpar_tabela(tabela : str) -> None:
    "Função de debug para limpar uma tabela."

    title(f"LIMPAR TABELA \"{tabela}\"")

    # Criando conexão e cursor
    db = sql.connect(dbpath)
    cursor = db.cursor()

    # Limpando
    cursor.execute(f"DELETE FROM {tabela}")

    # Commitando e fechando conexão
    db.commit()
    db.close()

def mostrar_tabela(tabela : str) -> None:
    "Imprime a tabela escolhida no console"

    title(f"TABELA \"{tabela}\"")
    
    # Conectando
    db = sql.connect(dbpath)

    print(pd.DataFrame(pd.read_sql(f"SELECT * FROM {tabela}", db)))

    # Fechando conexão
    db.close()
    
# Funções pra usuário
def check_cpf(cpf) -> dict:
    """Pega um CPF via input() e o retorna um dict com o valor numérico e o valor formatado (123.456.789-09).
    Se for inválido, retorna None"""

    while True:

        # Depois que a formatação estiver correta, eu faço o algoritmo para verificar a validez
        sequencia = [int(cpf[i]) for i in range(9)]
        verificadores = [int(cpf[i]) for i in range(9, 11)]

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
                
                # Fazendo a versão formatada
                cpf_str = str(cpf)
                cpf_str = string_insert(cpf_str, ".", 3) # ponto 1
                cpf_str = string_insert(cpf_str, ".", 7) # ponto 2
                cpf_str = string_insert(cpf_str, "-", 11) # hífen

                return dict(num=cpf, formato=cpf_str)
            else: # Não bateu o valor, é falso
                return None

        else: # Se não deu certo, quebro o loop
            return None

def check_email(email) -> bool:
    "Pega um email via input() retorna True após validação. Retorna False se for inválido. exemplo@dominio"

    while True:
        # Verificando se tem um arroba só no email. Caso contrário, tem algo errado.
        if(email.count("@") == 1):
            
            # Verificando se existe local e domínio (antes/depois do @)
            atpos = email.find("@")
            if(email[:atpos] == "" or email[atpos+1:] == ""):
                return False
            else:
                return True
        else:
            return False
    
def novo_usuario(nome : str, senha : str, cpf : int, email : str, admin : bool) -> None:
    "A função vai requisitar todos os dados para criar um usuário, vai verificá-los e adicionar o usuário ao banco caso tudo esteja correto."

    # Criando conexão e cursor
    db = sql.connect(dbpath)
    cursor = db.cursor()

    # Adicionando o usuário no banco:
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, senha, email, cpf, cpf_format, admin)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, senha, email, cpf["num"], cpf["formato"], admin)
        )
    except sql.IntegrityError:
        print("\nErro no registro\nCPF e/ou e-mail já foram registrados.\n")

    # Commitando e fechando a conexão
    db.commit()
    db.close()

def login(usuario : str, password : str) -> bool:
    "Retorna True ou False baseado na existência do usuário (identificado por e-mail) e se a senha está correta."

    # Criando conexão pra checar os dados
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Checando se o usuário existe
    if check_email(usuario): # se for um email
        cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (usuario,))
    else: # se for um usuário
        cursor.execute("SELECT senha FROM usuarios WHERE nome = ?", (usuario,))
    search = cursor.fetchone() # Pegando o usuário apenas
    retorna = None # Valor de retorno. Faço uma variável pois quero retornar só no fim

    if search: # existe

        # Guardando a senha
        senha = search[0]

        # Descriptografando e verificando
        if bcrypt.checkpw(password.encode("utf-8"), senha): # comparo as duas séries de bytes, se forem iguais, retorna True
            retorna = True
        else:
            retorna = False
    else:
        retorna = False

    # Fechando conexão
    db.close()
    return retorna

def mudar_senha(usuario : str, password : str) -> None:
    "Muda a senha do usuário desejado. Printa um erro caso o usuário não exista. Só deve ser usada pelo administrador."

    # Conectando
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Pegando por e-mail ou nome
    inserido = ""
    if check_email(usuario): inserido = "email" # se for um email
    else: inserido = "nome" # se for um usuário

    # Executando
    cursor.execute("UPDATE usuarios SET senha = ? WHERE ? = ?", (password, inserido, usuario))

    # Fechando conexão
    db.commit()
    db.close()

# Funções de equipamento
def novo_equipamento(nome : str, modelo : str, fabricante : str, estado : str, tipo_manutencao : str, ferramentas : str, periodo : str) -> None:
    "Pede as informações e adiciona um equipamento ao banco."
    
    # Conectando e criando cursor
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Adicionando ao banco
    try:
        cursor.execute(
            """
            INSERT INTO equipamentos (nome, modelo, fabricante, estado, tipo_manutencao, ferramentas, periodo_meses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, modelo, fabricante, estado, tipo_manutencao, ferramentas, periodo)
        )
    except sql.IntegrityError:
        print("\nErro no registro\nModelo já foi registrado.\n")

    # Commitando e fechando conexão
    db.commit()
    db.close()

def achar_equipamento(equip : str) -> None:
    "Pede ao usuário que insira o ID ou nome do modelo, e procura esse equipamento na tabela."

    # Conectando
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    if(equip.isdigit()): # É um ID
        equip = int(equip) # Convertendo pra inteiro
        cursor.execute("SELECT * FROM equipamentos WHERE rowid = ?", (equip,))
    else: # É modelo
        cursor.execute("SELECT * FROM equipamentos WHERE modelo = ?", (equip,))
    search = cursor.fetchone() # Guardando a busca

    if search:
        # Rodando pelos valores encontrados e printando
        for i in search: print(i)
    else:
        print("Equipamento não foi encontrado.")

    # Desconectando
    db.close()

# Funções de ferramenta
def novo_ferramenta(nome : str, modelo : str, fabricante : str, estado : str) -> None:
    "Pede as informações e adiciona a ferramenta ao banco."
    
    # Conectando e criando cursor
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Adicionando ao banco
    try:
        cursor.execute(
            """
            INSERT INTO ferramentas (nome, modelo, fabricante, estado)
            VALUES (?, ?, ?, ?)
            """, (nome, modelo, fabricante, estado)
        )
    except sql.IntegrityError:
        print("\nErro no registro\nModelo já foi registrado.\n")

    # Commitando e fechando conexão
    db.commit()
    db.close()

def achar_ferramenta(ferramenta : str) -> None:
    "Pede ao usuário que insira o ID ou nome do modelo, e procura essa ferramenta na tabela."

    # Conectando
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    if(ferramenta.isdigit()): # É um ID
        ferramenta = int(ferramenta) # Convertendo pra inteiro
        cursor.execute("SELECT * FROM ferramentas WHERE rowid = ?", (ferramenta,))
    else: # É modelo
        cursor.execute("SELECT * FROM ferramentas WHERE modelo = ?", (ferramenta,))
    search = cursor.fetchone() # Guardando a busca

    if search:
        # Rodando pelos valores encontrados e printando
        for i in search: print(i)
    else:
        print("Ferramenta não foi encontrada.")

    # Desconectando
    db.close()

if __name__ == "__main__":
    ...