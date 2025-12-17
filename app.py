from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import send_from_directory
# Importar a função de execução de query do db_connector
from db_connector import load_db_config, save_db_config, test_db_connection, execute_query_data
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# ----------------------------------------------------------------------
# ROTAS ESTÁTICAS E DE CONFIGURAÇÃO (Sem Alterações)
# ----------------------------------------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    config = load_db_config()
    if config:
        return redirect(url_for('welcome_summary'))
    else:
        flash('Por favor, configure a ligação à base de dados para começar.', 'warning')
        return redirect(url_for('config_db'))

@app.route('/welcome')
def welcome_summary():
    config = load_db_config()
    if not config:
        return redirect(url_for('config_db'))

    # BUSCA OS VALORES REAIS DA DB para as queries de resumo
    encomendas_parcial_count = execute_query_data('query_encomendas_aberto')
    encomendas_total_count = execute_query_data('query_encomendas_total')
    rececoes_aberto_count = execute_query_data('query_rececoes_aberto')
    producoes_ativas_count = execute_query_data('query_producoes_ativas')
    orcamentos_abertos_count = execute_query_data('query_orcamentos_aberto')

    # DADOS DE RESUMO para os cartões.
    summary_data = {
        "encomendas_parcial": {
            "value": f"{encomendas_parcial_count}", 
            "label": "Enc. em Aberto/Por Satisfazer", 
            "icon": "fa-clipboard-list", 
            "color": "info",
            "detail_url": url_for('view_data', content_type='encomendas', detail='parcial')
        },
        "encomendas_total": {
            "value": f"{encomendas_total_count}", 
            "label": "Encomendas (Ano)", 
            "icon": "fa-shopping-cart", 
            "color": "primary",
            "detail_url": url_for('view_data', content_type='encomendas', detail='total')
        },
        "producoes_ativas": {
            "value": f"{producoes_ativas_count}", 
            "label": "Produções Ativas", 
            "icon": "fa-cogs", 
            "color": "success",
            "detail_url": url_for('view_data', content_type='producao') 
        },
        "rececoes_abertas": {
            "value": f"{rececoes_aberto_count}", 
            "label": "Receções em Aberto (Ano)", 
            "icon": "fa-truck-loading", 
            "color": "warning",
            "detail_url": url_for('view_data', content_type='rececoes') 
        },
        "orcamentos_abertos": {
            "value": f"{orcamentos_abertos_count}", 
            "label": "Orçamentos em Aberto", 
            "icon": "fa-calculator", 
            "color": "secondary",
            "detail_url": url_for('view_data', content_type='orcamentos') 
        },
    }
    
    return render_template('welcome.html', active_page='welcome', summary_data=summary_data)

@app.route('/config', methods=['GET', 'POST'])
def config_db():
    # ... (Lógica da configuração omitida para brevidade, mas permanece igual)
    if request.method == 'POST':
        dsn = request.form.get('dsn')
        db = request.form.get('db')
        user = request.form.get('user')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'test':
            success, message = test_db_connection(dsn, db, user, password)
            if success:
                flash(f'Sucesso: {message}', 'success')
            else:
                flash(f'Falha no Teste: {message}. Por favor, verifique os dados.', 'danger')
            return render_template('login.html', dsn=dsn, db=db, user=user, password=password)
            
        elif action == 'save':
            success, message = test_db_connection(dsn, db, user, password)
            if success:
                if save_db_config(dsn, db, user, password):
                    flash('Configuração salva com sucesso! Acesso liberado.', 'success')
                    return redirect(url_for('welcome_summary')) 
                else:
                    flash('Erro ao salvar o arquivo de configuração.', 'danger')
            else:
                flash(f'Não foi possível salvar: Falha na conexão: {message}', 'danger')
                
        elif action == 'cancel':
            if load_db_config():
                flash('Configuração cancelada.', 'info')
                return redirect(url_for('welcome_summary'))
            else:
                flash('Operação cancelada. Por favor, configure a ligação ou feche a aplicação.', 'info')
                return render_template('login.html', dsn=dsn, db=db, user=user, password=password)
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    flash('Sessão encerrada.', 'info')
    return render_template('close_tab.html')

# ----------------------------------------------------------------------
# ROTAS API REMOVIDAS (para usar o carregamento síncrono)
# ----------------------------------------------------------------------
# Nota: As rotas /api/get_details/<detail_type> e /api/get_chart_data/<chart_type>
# foram removidas para forçar o carregamento síncrono dos dados.


# ----------------------------------------------------------------------
# ROTA view_data MODIFICADA (Carregamento Síncrono)
# ----------------------------------------------------------------------
@app.route('/<content_type>')
def view_data(content_type):
    """
    Rota genérica para exibir dados.
    Agora, para 'encomendas', os dados são carregados aqui (sincronamente)
    e passados para o template.
    """
    config = load_db_config()
    if not config and content_type != 'configuracoes':
        return redirect(url_for('config_db'))

    # Verifica se há um parâmetro de detalhe na URL (e.g., ?detail=parcial)
    detail_type = request.args.get('detail', 'total') # Default para 'total'

    # ----------------------------------------------------------------------
    # LÓGICA DE CARREGAMENTO DE DADOS SÍNCRONA PARA ENCOMENDAS
    # ----------------------------------------------------------------------
    if content_type == 'encomendas':
        
        # 1. Determina o tipo de query para o Gráfico
        chart_type = 'aberto' if detail_type == 'parcial' else 'total'
        
        try:
            # 2. Executa a query para o Detalhe (Grelha)
            print(f"Flask Log: A carregar dados detalhados: {detail_type}")
            grid_data = execute_query_data('get_data_encomendas', params={'detail_type': detail_type})
            
            # 3. Executa a query para o Gráfico
            print(f"Flask Log: A carregar dados do gráfico: {chart_type}")
            chart_data = execute_query_data('get_data_encomendas_por_cliente', params={'chart_type': chart_type})
            
        except Exception as e:
            # Em caso de falha de DB, mostra um erro
            print(f"Flask Log: ERRO AO BUSCAR DADOS DO DB: {e}")
            flash('Erro ao ligar à base de dados para obter o detalhe. Verifique a consola do servidor.', 'danger')
            grid_data = []
            chart_data = []


        title_map = {
            'parcial': "Encomendas em Aberto/Parcialmente Satisfeitas",
            'total': "Encomendas Totais (Ano)",
        }
        page_title = title_map.get(detail_type, "Detalhe de Encomendas") 

        # Passa os dados diretamente para o template (SÍNCRONO)
        return render_template(
            'content_placeholder.html', 
            active_page=content_type, 
            page_title=page_title,
            grid_data=grid_data, # NOVO: Dados da grelha
            chart_data=chart_data # NOVO: Dados do gráfico
        )
    
    # Lógica para outras rotas (producao, orcamentos, etc.) que ainda usam a lógica síncrona:
    else:
        # Lógica de carregamento de dados para outras páginas (Produção, Receções, etc.)
        # ... (Omitida para brevidade, permanece a sua lógica original)
        params = {'detail_type': detail_type} if detail_type else None
        query_name = f'get_data_{content_type}'
        data = execute_query_data(query_name, params=params)

        title_map = {
            'producao': "Ordens de Fabrico",
            'orcamentos': "Orçamentos",
            'rececoes': "Receções de Mercadoria",
        }
        page_title = title_map.get(content_type, content_type.capitalize())

        return render_template(
            'content_placeholder.html', 
            active_page=content_type, 
            data_content={'data': data, 'title': page_title}, 
            page_title=page_title 
        )


if __name__ == '__main__':
    # Cria as pastas 'templates' e 'static' se não existirem
    if not os.path.exists('templates'):
        os.makedirs('templates')
    if not os.path.exists('static'):
        os.makedirs('static')
        
    app.run(debug=True)