import pandas as pd
import sqlite3 as sql
import os

os.makedirs("db")
dbpath = "db/banco.db"

def string_insert(str, substring, pos) -> str:
    "Insere uma substring dentro da string passada na posição passada, e retorna o resultado."
    return str[:pos] + substring + str[pos+len(substring)-1:]

def criar_tabelas() -> None:
    "Cria as tabelas de equipamentos, ferramentas e usuários, caso não existam. Passa por cada uma individualmente."

    # Criando a conexão
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Tabela de equipamentos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS equipamentos(
            nome TEXT,
            modelo TEXT PRIMARY KEY,
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
            nome TEXT,
            modelo TEXT PRIMARY KEY,
            fabricante TEXT,
            estado TEXT
        )
        """
    )

    # Tabela de usuários
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios(
            nome TEXT,
            senha TEXT,
            email TEXT UNIQUE,
            cpf INT PRIMARY KEY,
            cpf_format TEXT
        )
        """
    )

    # Salvando as alterações com commit() e fechando conexão.
    db.commit()
    db.close()

def limpar_tabelas(tabela : str) -> None:
    "Função de debug para limpar uma tabela."

    # Criando conexão e cursor
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Limpando
    cursor.execute(f"DELETE FROM {tabela}")

    # Commitando e fechando conexão
    db.commit()
    db.close()

def get_cpf() -> dict:
    "Pega um CPF via input() e o retorna um dict com o valor numérico e o valor formatado (123.456.789-09)."

    get = lambda x: input(x).strip() # Lambda para deixar o código mais limpo

    # Essa variável é o valor numérico "cru"
    cpf = get("Insira o CPF (11 dígitos), sem pontos ou hífens: ")

    while True:

        # Se passar do limite ou conter letras, a sintaxe é inválida.
        while len(cpf) != 11 or not cpf.isdigit(): 
            cpf = get("CPF inválido. Verifique se os 11 dígitos estão corretos: ")
        
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
                cpf = get("O CPF não existe. Tente novamente: ")

        else: # Se não deu certo, quebro o loop
            cpf = get("O CPF parece falso. Tente novamente: ")

def get_email() -> str:
    "Pega um email via input() e o retorna após as verificações. exemplo@dominio"

    get = lambda x: input(x).lower().strip() # Lambda para deixar o código mais limpo
    email = get("Insira seu e-mail: ")

    while True:
        # Verificando se tem um arroba só no email. Caso contrário, tem algo errado.
        if(email.count("@") == 1):
            
            # Verificando se existe local e domínio (antes/depois do @)
            atpos = email.find("@")
            if(email[:atpos] == "" or email[atpos+1:] == ""):
                email = get("E-mail inválido. Tente novamente: ")
            else:
                return email
        else:
            email = get("E-mail inválido. Tente novamente: ")
    
def novo_usuario() -> None:
    "A função vai requisitar todos os dados para criar um usuário, vai verificá-los e retornar o usuário."

    os.system("cls")
    print("Cadastrando".center(50, "-"))

    nome = ""
    while nome == "": nome = input("Nome do usuário: ")
    cpf = get_cpf()
    email = get_email()

    # Criando conexão e cursor
    db = sql.connect("db/banco.db")
    cursor = db.cursor()

    # Adicionando o usuário no banco:
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, cpf, cpf_format)
            VALUES (?, ?, ?, ?)
            """, (nome, email, cpf["num"], cpf["formato"])
        )
    except sql.IntegrityError:
        print("\nErro no registro\nCPF e/ou e-mail já foram registrados.\n")

    # Commitando e fechando a conexão
    db.commit()
    db.close()

    input("Enter para continuar...")
