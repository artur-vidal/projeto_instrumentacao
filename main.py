from funcoes_banco import *

def menu_usuario() -> None:
    "Menu de usuários. Debug."

    while True:
        title("USUÁRIOS")

        # Pegando comando
        comando = input("1. novo usuario\n2. fazer login\n3. mostrar tabela\n4. limpar tabela\n5. voltar\n")

        match comando:
            case "1":
                title("CADASTRANDO")
                novo_usuario()
                input("Enter para continuar...")
            case "2":
                title("LOGIN")

                # Pegando valores
                email = input_notnull("E-mail: ")
                senha = input_notnull("Senha: ")

                # Rodando função
                if login(email, senha):
                    
                    # Conexão pra printar o usuário
                    db = sql.connect(dbpath)
                    cursor = db.cursor()
                    cursor.execute("SELECT nome, admin FROM usuarios WHERE email = ?", (email,)) # Buscando usuário
                    search = cursor.fetchone()

                    user = search[0] # Pegando o usuário da busca
                    adm = search[1] # Checando se é administrador

                    adm_str = ""
                    if adm: adm_str = "<ADMINISTRADOR> "
                    print(f"{user} {adm_str}logado com sucesso!")

                    # Fechando
                    db.close()
                else:
                    print("Login falhou. Verifique se o e-mail e senha estão corretos.")
                
                input("Enter para continuar...")
            case "3":
                mostrar_tabela("usuarios")
                input("Enter para continuar...")
            case "4":
                limpar_tabela("usuarios")
                print("Tabela limpa.")
                input("Enter para continuar...")
            case "5":
                break

def menu_equipamento() -> None:
    "Menu para registrar equipamentos." 

    while True:
        title("EQUIPAMENTOS")

        # Pegando comando
        comando = input("1. novo equipamento\n2. achar equipamento\n3. mostrar tabela\n4. limpar tabela\n5. voltar\n")
        
        # Rodando comando
        match comando:
            case "1":
                title("CADASTRANDO EQUIPAMENTO")
                novo_equipamento()
                input("Enter para continuar...")
            case "2":
                title("PESQUISAR EQUIPAMENTO")
                achar_equipamento()
                input("Enter para continuar...")
            case "3":
                mostrar_tabela("equipamentos")
                input("Enter para continuar...")
            case "4":
                limpar_tabela("equipamentos")
                print("Tabela limpa.")
                input("Enter para continuar...") 
            case "5":
                break

def menu_ferramenta() -> None:
    "Menu para registrar ferramentas."

    while True:
        title("FERRAMENTAS")

        # Pegando comando
        comando = input("1. nova ferramenta\n2. achar ferramenta\n3. mostrar tabela\n4. limpar tabela\n5. voltar\n")
        
        # Rodando comando
        match comando:
            case "1":
                title("CADASTRANDO FERRAMENTA")
                novo_ferramenta()
                input("Enter para continuar...")
            case "2":
                title("PESQUISAR FERRAMENTA")
                achar_ferramenta()
                input("Enter para continuar...")
            case "3":
                mostrar_tabela("ferramentas")
                input("Enter para continuar...")
            case "4":
                limpar_tabela("ferramentas")
                print("Tabela limpa.")
                input("Enter para continuar...") 
            case "5":
                break

def main():
    criar_tabelas()

    # Pegando os comandos
    while True:
        os.system("cls")
        print("DATABASE".center(50, "-"))
        comando = input("1. menu de usuarios\n2. menu de equipamentos\n3. menu de ferramentas\n4. sair\n")
        
        match comando:
            case "1":
                menu_usuario()
            case "2":
                menu_equipamento()
            case "3":
                menu_ferramenta()
            case "4":
                break

if(__name__ == "__main__"): 
    main()