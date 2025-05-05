Projeto feito para auxiliar os professores e estudantes do curso de Instrumentação Industrial na tarefa de registrar equipamentos e manutenções.
Feito pelos alunos da escola SENAI Jairo Cândido, para alunos do mesmo curso. Sob orientação dos professores Fabiano Luizon Campos e Carlos Assis Silva Aguiar.

- Artur Vidal de Almeida (backend/frontend, banco de dados e documentação)
- João Victor Apolinário de Freitas (banco de dados e documentação)

## Passos para set-up
### Dependências:
Python 3.13.2</br>
virtualenv 20.30.0</br>
pip 24.3.1 (no ambiente virtual)</br>

### Instalação
Primeiro, clone o repositório usando o link ```https://github.com/artur-vidal/projeto_instrumentacao```</br>
</br>
Crie um ambiente virtual com o nome que preferir com o comando ```python -m venv nome-do-ambiente```.</br>
Para ativar o ambiente, use o comando ```nome-do-ambiente\Scripts\activate``` dentro do diretório onde clonou o repositório.</br>
E para instalar as dependências, já com o ambiente ativado, use ```pip install -r requirements.txt```. Isso vai ler todas as dependências do projeto, que estão guardadas no arquivo requirements.txt, e instalá-las.</br>
</br>
Com todas as dependências instaladas, só é preciso abrir o servidor Streamlit usando ```streamlit run main.py``` (com o ambiente ativado).
