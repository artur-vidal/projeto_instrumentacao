from funcoes_banco import *
import pandas as pd

def main():
    criar_tabelas()

    # Pegando os comandos
    while True:
        os.system("cls")
        print("DATABASE".center(50, "-"))
        comando = input("1. novo usuario\n2. fazer login\n3. ver banco\n4. limpar banco\n5. sair\n")
        while comando not in ["1", "2", "3", "4", "5"]:
            comando = input("Inválido. Tente novamente:")
        
        match comando:
            case "1":
                novo_usuario()
            case "2":
                os.system("cls")
                print("LOGIN".center(50, "-"))

                # Pegando valores
                email = input("E-mail: ")
                while email == "": email = input("E-mail: ")

                senha = input("Senha: ")
                while senha == "": senha = input("Senha: ")

                # Rodando função
                if login(email, senha):
                    
                    # Conexão pra printar o usuário
                    db = sql.connect(dbpath)
                    cursor = db.cursor()
                    cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (email,))
                    user = cursor.fetchone()[0] # Pegando o usuário da busca

                    print(f"{user} logado com sucesso!")

                    # Fechando
                    db.close()
                else:
                    print("Login falhou. Verifique se o e-mail e senha estão corretos.")
                
                input("Enter para continuar...")

            case "3":
                # Printando
                os.system("cls")

                # Conectando
                db = sql.connect(dbpath)

                print("BANCO ATUAL".center(50, "-"))
                print(pd.DataFrame(pd.read_sql("SELECT * FROM usuarios", db)))

                # Fechando conexão
                db.close()

                input("Enter para continuar...")
            case "4":
                os.system("cls")
                print("Limpar tabela".center(50, "-"))
                limpar_tabelas("usuarios")
                print("Tabela limpa.")
                input("Enter para continuar...")
            case "5":
                break

if(__name__ == "__main__"): 
    main()