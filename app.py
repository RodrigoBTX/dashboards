from flask import Flask, render_template, request, redirect, url_for, flash, session
from db_connector import load_db_config, save_db_config, test_db_connection, execute_query_data
import os

app = Flask(__name__)
# Chave secreta obrigatória para usar flash messages (Bootstrap alerts)
app.secret_key = os.urandom(24) 

@app.route('/')
def home():
    """Verifica a configuração do DB. Redireciona para o login se não houver ou para a página de boas-vindas se houver."""
    config = load_db_config()
    if config:
        # Se a configuração existir, direciona para a página de boas-vindas
        return redirect(url_for('welcome_summary'))
    else:
        # Se a configuração não existir, abre a tela de login/configuração
        flash('Por favor, configure a ligação à base de dados para começar.', 'warning')
        return redirect(url_for('config_db'))

@app.route('/welcome')
def welcome_summary():
    """Nova página de boas-vindas com o resumo dos indicadores chave."""
    config = load_db_config()
    if not config:
        # Garante que não se pode ver o welcome sem configuração
        return redirect(url_for('config_db'))

    # DADOS DE MOCK para os cartões de resumo.
    # Você irá substituir esta parte pela lógica que busca o resumo na DB.
    summary_data = {
        "encomendas_total": {"value": "12.450", "label": "Encomendas (Ano)", "icon": "fa-shopping-cart", "color": "primary"},
        "producoes_ativas": {"value": "15", "label": "Produções Ativas", "icon": "fa-cogs", "color": "info"},
        "rececoes_efetuadas": {"value": "320", "label": "Receções (Mês)", "icon": "fa-truck-loading", "color": "success"},
        "orcamentos_abertos": {"value": "85", "label": "Orçamentos em Aberto", "icon": "fa-calculator", "color": "warning"},
    }
    
    return render_template('welcome.html', active_page='welcome', summary_data=summary_data)


@app.route('/config', methods=['GET', 'POST'])
def config_db():
    """Página e lógica para configurar a conexão com o DB."""
    if request.method == 'POST':
        dsn = request.form.get('dsn')
        db = request.form.get('db')
        user = request.form.get('user')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'test':
            # Testa a conexão
            success, message = test_db_connection(dsn, db, user, password)
            if success:
                flash(f'Sucesso: {message}', 'success')
            else:
                flash(f'Falha no Teste: {message}. Por favor, verifique os dados.', 'danger')
            # Mantém os dados no formulário após o teste
            return render_template('login.html', dsn=dsn, db=db, user=user, password=password)
            
        elif action == 'save':
            # Salva a conexão (mas testa antes, por segurança)
            success, message = test_db_connection(dsn, db, user, password)
            if success:
                if save_db_config(dsn, db, user, password):
                    flash('Configuração salva com sucesso! Acesso liberado.', 'success')
                    # Redireciona para a nova página de boas-vindas
                    return redirect(url_for('welcome_summary')) 
                else:
                    flash('Erro ao salvar o arquivo de configuração.', 'danger')
            else:
                flash(f'Não foi possível salvar: Falha na conexão: {message}', 'danger')
                
        elif action == 'cancel':
            # Se cancelar: se já houver config, volta para o welcome; senão, fica no login
            if load_db_config():
                flash('Configuração cancelada.', 'info')
                return redirect(url_for('welcome_summary'))
            else:
                 flash('Operação cancelada. Por favor, configure a ligação ou feche a aplicação.', 'info')
                 # Se não houver config, volta para a rota 'config_db' (login.html)
                 return render_template('login.html', dsn=dsn, db=db, user=user, password=password)
            
    # GET request: Carrega o formulário
    return render_template('login.html')

@app.route('/<content_type>')
def view_data(content_type):
    """
    Rota genérica para exibir dados de uma das opções do menu.
    content_type será 'encomendas', 'producao', 'orcamentos', 'rececoes', 'configuracoes'.
    """
    config = load_db_config()
    if not config and content_type != 'configuracoes':
        # Se não houver configuração, força o usuário a configurar
        return redirect(url_for('config_db'))

    # Esta é a parte que você irá adaptar no futuro:
    query_name = f'get_data_{content_type}'
    
    # Executar a query (agora retorna MOCK data)
    data = execute_query_data(query_name)

    # Passar os dados para o template para renderização (grids, gráficos, etc.)
    return render_template(
        'content_placeholder.html', 
        active_page=content_type, 
        data_content=data
    )

@app.route('/logout')
def logout():
    """Simplesmente remove a configuração atual (simulando um 'esquecer' a conexão)"""
    try:
        if os.path.exists('config.json'):
            os.remove('config.json')
            flash('Configuração de banco de dados removida com sucesso.', 'info')
    except Exception as e:
        flash(f'Erro ao tentar remover o arquivo de configuração: {e}', 'danger')
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Cria a pasta 'templates' se não existir
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    app.run(debug=True)