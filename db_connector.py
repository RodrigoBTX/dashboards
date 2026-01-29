import json
import os
import pyodbc 

# --- Configurações e Arquivo ---

CONFIG_FILE = 'config.json'

def load_db_config():
    """Carrega as credenciais de conexão do arquivo config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_db_config(dsn, db, user, password):
    """Guarda as credenciais de conexão no arquivo config.json."""
    config = {
        'dsn': dsn,
        'db': db,
        'user': user,
        'password': password
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return True
    except Exception:
        return False

# --- Conexão e Queries ---

def test_db_connection(dsn, db, user, password):
    """Tenta estabelecer a conexão com a DB (REAL)."""
    if not dsn or not db or not user:
        return False, "Dados de conexão incompletos."
    
    # LÓGICA REAL COM pyodbc
    try:
        conn_str = f'DSN={dsn};DATABASE={db};UID={user};PWD={password if password else ""}'
        conn = pyodbc.connect(conn_str)
        conn.close()
        return True, "Conexão testada e bem-sucedida!"
    except Exception as e:
        # Se falhar, retorna a mensagem de erro da exceção pyodbc
        return False, str(e)

# ----------------------------------------------------------------------
# QUERIES DE CONTAGEM (RESUMO)
# ----------------------------------------------------------------------

QUERY_ENCOMENDAS_ABERTO_PARCIAL = """
SELECT COUNT(DISTINCT bi.bostamp) n_dossiers
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
INNER JOIN bi (NOLOCK) ON bo.bostamp = bi.bostamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo.fechada = 0
    AND bo2.anulado = 0
    AND bi.qtt > bi.qtt2
"""

QUERY_ENCOMENDAS_TOTAL_ANO = """
SELECT COUNT(1) n_dossiers
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo2.anulado = 0
"""

QUERY_RECECOES_ABERTO = """
SELECT COUNT(1) n_dossiers
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
WHERE 
    bo.ndos = 47
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo.fechada = 0
    AND bo2.anulado = 0
"""

QUERY_PRODUCOES_ATIVAS = """
exec sp_prod_ativ 
"""

QUERY_ORCAMENTOS_ABERTO = """
SELECT COUNT(1) n_dossiers
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
WHERE 
    bo.ndos = 3
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo.fechada = 0
    AND bo2.anulado = 0
"""

# ----------------------------------------------------------------------
# QUERIES DE DETALHE (GRIDS)
# ----------------------------------------------------------------------

QUERY_ENCOMENDAS_PARCIAL_DETALHE = """
SELECT bo.obrano AS "Nº dossier", bo.nome AS "Cliente", bo.no AS "Nº Cliente", bo.obranome AS "V/Req", CONVERT(VARCHAR, bo.dataobra, 103) AS "Data"
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
INNER JOIN bi (NOLOCK) ON bo.bostamp = bi.bostamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo.fechada = 0
    AND bo2.anulado = 0
    AND bi.qtt > bi.qtt2
GROUP BY bo.obrano, bo.nome, bo.no, bo.obranome, bo.dataobra
ORDER BY bo.dataobra ASC
"""

QUERY_ENCOMENDAS_TOTAL_DETALHE = """
SELECT bo.obrano AS "Nº dossier", bo.nome AS "Cliente", bo.no AS "Nº Cliente", bo.obranome AS "V/Req", CONVERT(VARCHAR, bo.dataobra, 103) AS "Data"
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo2.anulado = 0
ORDER BY bo.dataobra ASC
"""


# ----------------------------------------------------------------------
# QUERIES DE GRÁFICO (AGREGAÇÃO)
# ----------------------------------------------------------------------

# Query para Gráfico: Total de Encomendas do Ano por Cliente
QUERY_ENCOMENDAS_POR_CLIENTE_TOTAL = """
SELECT TOP 10
    bo.nome AS "Cliente", 
    COUNT(1) AS "Nº Encomendas"
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo2.anulado = 0
GROUP BY bo.nome
ORDER BY "Nº Encomendas" DESC
"""

# Query para Gráfico: Encomendas Por Satisfazer (em Aberto) por Cliente
QUERY_ENCOMENDAS_POR_CLIENTE_ABERTO = """
SELECT TOP 10
    bo.nome AS "Cliente", 
    COUNT(1) AS "Nº Encomendas"
FROM bo (NOLOCK)
INNER JOIN bo2 (NOLOCK) ON bo.bostamp = bo2.bo2stamp
INNER JOIN bi (NOLOCK) ON bo.bostamp = bi.bostamp
WHERE 
    bo.ndos = 1
    AND YEAR(bo.dataobra) = YEAR(GETDATE())
    AND bo2.anulado = 0
    AND bi.qtt > bi.qtt2 -- Quantidade encomendada > Quantidade satisfeita (Aberta)
GROUP BY bo.nome
ORDER BY "Nº Encomendas" DESC
"""


def _execute_single_value_query(query_sql):
    """Função auxiliar para executar uma query que retorna um único valor de contagem."""
    config = load_db_config()
    if not config:
        return 0
    try:
        conn_str = f'DSN={config["dsn"]};DATABASE={config["db"]};UID={config["user"]};PWD={config["password"]}'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Executa a query/SP
        cursor.execute(query_sql)
        # Tenta obter o resultado da primeira linha e primeira coluna
        result = cursor.fetchone()
        conn.close()
        # Retorna o resultado ou 0 se não houver resultado
        return result[0] if result and result[0] is not None else 0
    except Exception as e:
        print(f"Erro ao executar query de contagem: {e}")
        # Retorna 0 em caso de erro
        return 0

def _execute_detailed_query(query_sql):
    """Função auxiliar para executar uma query que retorna múltiplas linhas e colunas (para o grid)."""
    config = load_db_config()
    if not config:
        return []
    try:
        conn_str = f'DSN={config["dsn"]};DATABASE={config["db"]};UID={config["user"]};PWD={config["password"]}'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute(query_sql)
        columns = [column[0] for column in cursor.description]
        
        # Converte as linhas em uma lista de dicionários (para fácil renderização no Flask)
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.close()
        return results
    except Exception as e:
        print(f"Erro ao executar query de detalhe: {e}")
        return []


def execute_query_data(query_name, params=None):
    """
    Executa uma query ou SP e retorna os dados. Usa lógica REAL para as queries de resumo e detalhe.
    """
    
    # --- LÓGICA REAL para as Queries de Resumo (Contagem) ---
    if query_name == 'query_encomendas_aberto':
        return _execute_single_value_query(QUERY_ENCOMENDAS_ABERTO_PARCIAL)
    
    elif query_name == 'query_encomendas_total':
        return _execute_single_value_query(QUERY_ENCOMENDAS_TOTAL_ANO)

    elif query_name == 'query_rececoes_aberto':
        return _execute_single_value_query(QUERY_RECECOES_ABERTO)

    elif query_name == 'query_producoes_ativas':
        return _execute_single_value_query(QUERY_PRODUCOES_ATIVAS)
    
    elif query_name == 'query_orcamentos_aberto':
        return _execute_single_value_query(QUERY_ORCAMENTOS_ABERTO)

    # --- LÓGICA REAL para as Queries de Detalhe (Grid) ---
    elif query_name == 'get_data_encomendas':
        detail_type = params.get('detail_type') if params else None
        
        if detail_type == 'parcial':
            return _execute_detailed_query(QUERY_ENCOMENDAS_PARCIAL_DETALHE)
        elif detail_type == 'total':
            return _execute_detailed_query(QUERY_ENCOMENDAS_TOTAL_DETALHE)
        else:
            return _execute_detailed_query(QUERY_ENCOMENDAS_PARCIAL_DETALHE)
            
    # --- NOVO: LÓGICA REAL para o Gráfico (Agregação) ---
    elif query_name == 'get_data_encomendas_por_cliente':
        # Esta lógica agora recebe 'chart_type' (total ou aberto) via params
        chart_type = params.get('chart_type') if params else None
        
        if chart_type == 'aberto':
            print("A executar query de gráfico para Encomendas Abertas por Cliente...")
            return _execute_detailed_query(QUERY_ENCOMENDAS_POR_CLIENTE_ABERTO)
        else:
            # Padrão é Total
            print("A executar query de gráfico para Encomendas Totais por Cliente...")
            return _execute_detailed_query(QUERY_ENCOMENDAS_POR_CLIENTE_TOTAL)

    # --- Fallback
    else:
        # Se a query não for reconhecida ou não for implementada
        print(f"Alerta: Query '{query_name}' não implementada ou reconhecida.")
        return []
