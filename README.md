Dashboards Kalipso (Flask + MSSQL)

Esta é uma aplicação web leve construída com Flask e Bootstrap 5, projetada para servir como um dashboard de consulta de análises de dados do Microsoft SQL Server (MSSQL).

🚀 Como Iniciar

1. Estrutura de Pastas

Certifique-se de que a sua estrutura de diretórios está correta:

dashboards_py/
├── app.py
├── db_connector.py
├── config.json
├── .gitignore
├── README.md
└── templates/
    ├── base.html
    ├── welcome.html
    ├── login.html
    └── content_placeholder.html


2. Instalação de Dependências

Você precisará do Python e das bibliotecas Flask e pyodbc.

# Recomendado: Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Linux/macOS
.\venv\Scripts\activate   # No Windows

# Instale as bibliotecas
pip install Flask pyodbc


3. Configuração do SQL Server

A primeira vez que a aplicação for iniciada, ela irá redirecionar para a página de configuração.

Você deve ter um DSN (Data Source Name) configurado no seu sistema operacional que aponte para o seu MSSQL Server.

Preencha os campos DSN, Base de Dados, Utilizador e Palavra-passe.

Use o botão "Testar Ligação" para validar.

Use o botão "Guardar" para salvar as credenciais no arquivo local config.json (que está no .gitignore).

4. Executar a Aplicação

Inicie o servidor de desenvolvimento do Flask:

python app.py


Acesse a aplicação no seu navegador: http://127.0.0.1:5000/

🛠️ Como Adicionar Queries Reais

Para ligar a aplicação aos seus dados reais, edite o arquivo db_connector.py. Você deve substituir a lógica de MOCK (dados simulados) dentro das funções de busca de dados pela execução real de queries pyodbc.

Exemplo (dentro de db_connector.py):

# Mude a função test_db_connection e execute_query_data para usar o pyodbc real.
# execute_query_data(query_or_sp, params=None):

def execute_query_data(query_or_sp, params=None):
    # Lógica para obter a conexão
    # config = load_db_config()
    # conn = pyodbc.connect(...)
    # cursor = conn.cursor()
    
    # ... aqui você executa sua query ou SP usando o cursor
    
    # Exemplo: cursor.execute("SELECT Mês, Total FROM Vendas_Gerais")
    # results = cursor.fetchall()
    
    # ... e retorna os dados
    
    # POR ENQUANTO, CONTINUA O MOCK PARA GARANTIR O FUNCIONAMENTO DA ESTRUTURA
    if 'encomendas' in query_or_sp.lower():
        # ... retorna dados de MOCK ...
        pass
    # ...
