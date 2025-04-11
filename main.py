from funcoes_banco import *

def main():
    criar_tabelas()

    # Pegando os comandos
    while True:
        os.system("cls")
        print("DATABASE".center(50, "-"))
        comando = input("1. novo usuario\n2. ver tabela\n3. limpar tabela\n4. sair\n")
        while comando not in ["1", "2", "3", "4"]:
            comando = input("Inválido. Tente novamente:")
        
        match comando:
            case "1":
                novo_usuario()
            case "2":
                # Printando
                os.system("cls")

                # Conectando
                db = sql.connect("db/banco.db")

                print("BANCO ATUAL".center(50, "-"))
                print(pd.DataFrame(pd.read_sql("SELECT * FROM usuarios", db)))

                # Fechando conexão
                db.close()

                input("Enter para continuar...")
            case "3":
                os.system("cls")
                print("Limpar tabela".center(50, "-"))
                limpar_tabelas("usuarios")
                print("Tabela limpa.")
                input("Enter para continuar...")
            case "4":
                break

if(__name__ == "__main__"): 
    main()