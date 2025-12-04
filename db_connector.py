import json
import os
import pyodbc # Importa pyodbc, necessário para conectar ao MS SQL Server

# Define o caminho para o arquivo de configuração, assumindo que está no mesmo diretório
CONFIG_FILE = 'config.json'

def load_db_config():
    """Carrega as configurações de conexão do arquivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Verifica se todas as chaves obrigatórias têm valores não vazios
            if all(config.get(k) for k in ["DSN", "DATABASE", "USER", "PASSWORD"]):
                return config
            return None # Retorna None se o arquivo existir, mas estiver vazio/incompleto
    except Exception as e:
        print(f"Erro ao carregar a configuração do DB: {e}")
        return None

def save_db_config(dsn, db, user, password):
    """Salva as configurações de conexão no arquivo JSON."""
    config = {
        "DSN": dsn,
        "DATABASE": db,
        "USER": user,
        "PASSWORD": password
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar a configuração do DB: {e}")
        return False

def test_db_connection(dsn, db, user, password):
    """Tenta estabelecer uma conexão com o SQL Server usando pyodbc."""
    try:
        # A string de conexão típica para um DSN (Data Source Name)
        conn_str = (
            f'DSN={dsn};'
            f'DATABASE={db};'
            f'UID={user};'
            f'PWD={password}'
        )
        
        # Tenta conectar. O timeout evita que a aplicação fique travada.
        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        return True, "Conexão estabelecida com sucesso!"
        
    except pyodbc.Error as ex:
        # Captura exceções específicas do pyodbc
        sqlstate = ex.args[0]
        # Aqui você pode analisar o código de erro do SQL
        if sqlstate == '28000':
            return False, "Erro de autenticação: Nome de usuário ou senha inválidos."
        else:
            return False, f"Falha na conexão: {ex}"
    except Exception as e:
        # Captura outros erros (ex: DSN não encontrado, pyodbc não instalado)
        return False, f"Erro inesperado durante o teste de conexão: {e}"

def execute_query_data(query_or_sp, params=None):
    """
    Função Placeholder para executar queries ou Stored Procedures (SPs).
    
    A implementação REAL exigirá:
    1. Carregar a configuração do DB.
    2. Estabelecer a conexão.
    3. Criar um cursor e executar a query/SP.
    4. Fetch dos resultados.
    5. Fechar conexão.
    
    Por enquanto, retorna dados de MOCK para garantir que a aplicação web funcione.
    """
    if 'encomendas' in query_or_sp.lower():
        # Exemplo de dados de MOCK para a seção 'Encomendas'
        return {
            "title": "Análise de Encomendas (MOCK)",
            "data": [
                {"Mês": "Jan", "Valor Total": 150000, "Itens": 4500},
                {"Mês": "Fev", "Valor Total": 180000, "Itens": 5200},
                {"Mês": "Mar", "Valor Total": 165000, "Itens": 4800},
            ]
        }
    elif 'producao' in query_or_sp.lower():
        return {
            "title": "Eficiência de Produção (MOCK)",
            "data": [
                {"Linha": "A", "Horas Paradas": 15, "Produzido": 9800},
                {"Linha": "B", "Horas Paradas": 8, "Produzido": 12500},
            ]
        }
    
    return {"title": "Dados de MOCK Genéricos", "data": [{"Status": "OK", "Detalhe": "Nenhuma query específica encontrada."}]}