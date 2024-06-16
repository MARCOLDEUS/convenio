from flask import Flask,render_template,redirect,request,flash,url_for,send_file, jsonify
import mysql.connector
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy
import win32api
import win32print
from sqlalchemy import create_engine, inspect, text
import os
from datetime import datetime


''' entra cmd mysql (mysql -h localhost -u root -p) '''
''''detela os produtos adicionados no carrinho(DELETE FROM carrinho;)'''

app= Flask(__name__)
app.config['SECRET_KET']= 'MAR'

# Configuração do banco de dados MySQL   
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'tabela_prod',
}

#tela de login 
@app.route('/')
def login():
    criar_banco_de_dados()
    return render_template("tela_entrada.html")

def criar_banco_de_dados():
    db_tabela = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': '',
}
    try:
        cunn = mysql.connector.connect(**db_tabela)
        cursor = cunn.cursor()
        
        # Criar o banco de dados se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS tabela_prod")
        cunn.commit()

        # Usar o banco de dados 'tabela_prod'
        cursor.execute("USE tabela_prod")

        # Criar tabela 'produtos_comprados' se não existir
        cursor.execute('''CREATE TABLE IF NOT EXISTS produtos_comprados (
                           id INT NOT NULL AUTO_INCREMENT,
                           codigo VARCHAR(60),
                           ncm VARCHAR(10),
                           descricao VARCHAR(60),
                           preco float(10, 2),
                           categoria VARCHAR(60),
                           quantidade float(10, 2),
                           PRIMARY KEY (id)
                           );''')
        # Criar tabela 'produtos' se não existir
        cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                           id INT NOT NULL AUTO_INCREMENT,
                           codigo VARCHAR(60),
                           ncm VARCHAR(10),
                           descricao VARCHAR(60),
                           preco float(10, 2),
                           categoria VARCHAR(60),
                           quantidade float(10, 2),
                           PRIMARY KEY (id)
                           );''')
        # Criar tabela 'carrinho' se não existir
        cursor.execute('''CREATE TABLE IF NOT EXISTS carrinho (
                           id INT NOT NULL AUTO_INCREMENT,
                           codigo VARCHAR(60),
                           ncm VARCHAR(10),
                           descricao VARCHAR(60),
                           preco float(10, 2),
                           categoria VARCHAR(60),
                           quantidade float(10, 2),                          
                           PRIMARY KEY (id)
                           );''')
        cunn.commit()
        
            
        
        print("Tabelas e banco de dados criados com sucesso")
        return "Tabelas e banco de dados criados com sucesso"
    except False as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return f"Erro ao conectar ao MySQL: {e}"
    finally:
        if cursor:
            cursor.close()
        if cunn:
            cunn.close()
    
    
@app.route('/login', methods=['POST'])
def tela_ent():
    nome= request.form.get('usuario')
    senha= request.form.get('senha')
    
    if nome =='convenio' and senha == '123':
        return render_template("convenio.html")
    else:
        #flash('usuario ou senha invalido \n por favor tenti novamente')
        return redirect('/')
    

#imprime a tabela carrinho
def get_data_from_mysql():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM carrinho")

        data = cursor.fetchall()

        cursor.close()
        connection.close()

        return data
    
    except Exception as e:
        print("Erro ao buscar dados do MySQL:", e)
        return None
# Função para gerar o PDF
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="nota fiscal", ln=True, align="C")
    pdf.cell(200, 10, ln=True)  # Adiciona espaço em branco

    # Cabeçalho da tabela
    pdf.cell(28, 10, "ID", 1)
    pdf.cell(28, 10, "codigo", 1)
    pdf.cell(28, 10, "ncm", 1)
    pdf.cell(28, 10, "Descrição", 1)
    pdf.cell(28, 10, "Preço", 1)
    pdf.cell(28, 10, "categoria", 1)
    pdf.cell(28, 10, "Quantidade", 1)
    pdf.ln()

     # Adiciona os dados da tabela
    total_price = 0
    for row in data:
        for item in row:
            pdf.cell(28, 10, str(item), 1)
        price_total = float(row[4]) * float(row[6])  # Calcula o preço total (quantidade * preço)
        total_price += price_total
        pdf.ln()

    # Adiciona o preço total
    pdf.cell(200, 10, txt="valor das total: R$ {:.2f}".format(total_price), ln=True, align="R")

    # Adiciona o horário atual
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.cell(200, 10, txt="Horário da compra: {}".format(current_time), ln=True, align="R")

    pdf_file = "tabela.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_file)  # Caminho absoluto do arquivo PDF
    pdf.output(pdf_path)
    return pdf_path
#imprime a tabela produtos
@app.route('/alterar_dd', methods=['GET', 'POST'])
def pdf_produtos():
    # Obtém os dados do MySQL
    data = pfd_prod_dd()

    if data:
         # Gera o PDF
        pdf_file = generate_pdf_tabela(data)

        
        # Retorna o PDF para download
        return send_file(pdf_file, as_attachment=True)

@app.route('/produtos_comprados_pdf', methods=['GET', 'POST'])
def pfd_prod_produtos_comprados():
    # Obtém os dados do MySQL
    data = recuperar_produtos_comprad()

    if data:
         # Gera o PDF
        pdf_file = generate_pdf_tabela(data)

        
        # Retorna o PDF para download
        return send_file(pdf_file, as_attachment=True)
# Função para verificar se o produto já existe no banco de dados
def verificar_carrinho_existente(id, descricao, preco):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carrinho WHERE id=%s AND descricao=%s AND preco=%s", (id, descricao, preco))
        produto = cursor.fetchone()
        return produto is not None
    except mysql.connector.Error as err:
        print("Erro ao verificar produto existente:", err)
        return False
    finally:
        if conn:
            conn.close()

        
        # Retorna o PDF para download
        return send_file( as_attachment=True)

def pfd_prod_dd():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM produtos")

        data = cursor.fetchall()

        cursor.close()
        connection.close()

        return data
    except Exception as e:
        print("Erro ao buscar dados do MySQL:", e)
        return None
       
# Função para gerar o PDF
def generate_pdf_tabela(data):
    pdf = FPDF()
    pdf.add_page()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="nota fiscal", ln=True, align="C")
    pdf.cell(200, 10, ln=True)  # Adiciona espaço em branco

    # Cabeçalho da tabela
    pdf.cell(28, 10, "ID", 1)
    pdf.cell(28, 10, "codigo", 1)
    pdf.cell(28, 10, "ncm", 1)
    pdf.cell(28, 10, "Descrição", 1)
    pdf.cell(28, 10, "Preço", 1)
    pdf.cell(28, 10, "categoria", 1)
    pdf.cell(28, 10, "Quantidade", 1)
    pdf.ln()

    # Adiciona os dados da tabela
    total_price = 0
    for row in data:
        for item in row:
            pdf.cell(28, 10, str(item), 1)
        price_total = float(row[4]) * float(row[6])  # Calcula o preço total (quantidade * preço)
        total_price += price_total
        pdf.ln()

    # Adiciona o preço total
    pdf.cell(200, 10, txt="valor das mercadorias: R$ {:.2f}".format(total_price), ln=True, align="R")

    # Adiciona o horário atual
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.cell(200, 10, txt="Horário da compra: {}".format(current_time), ln=True, align="R")

    pdf_file = "nota fiscal.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_file)  # Caminho absoluto do arquivo PDF
    pdf.output(pdf_path)
    return pdf_path

# Função para verificar se o produto já existe no banco de dados
def verificar_carrinho_existente(id, descricao, preco):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carrinho WHERE id=%s AND descricao=%s AND preco=%s", (id, descricao, preco))
        produto = cursor.fetchone()
        return produto is not None
    except mysql.connector.Error as err:
        print("Erro ao verificar produto existente:", err)
        return False
    finally:
        if conn:
            conn.close()
            
def verificar_produtos_existente(id, descricao, preco):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id=%s AND descricao=%s AND preco=%s", (id, descricao, preco))
        produto = cursor.fetchone()
        return produto is not None
    except mysql.connector.Error as err:
        print("Erro ao verificar produto existente:", err)
        return False
    finally:
        if conn:
            conn.close()            
        
# Função para recuperar todos os registros da tabela "carrinho"
def recuperar_registros():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produto_d = cursor.fetchall()
    conn.close()
    return produto_d
# Função para recuperar todos os registros da tabela "carrinho"
def recuperar_registros():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carrinho")
    registros = cursor.fetchall()
    conn.close()
    return registros
# Função para recuperar todos os registros da tabela "produtos_comprados"
def recuperar_produtos_comprad():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos_comprados")
    comprados = cursor.fetchall()
    conn.close()
    return comprados
#deleta os produtos comprados
@app.route('/deletar_produtos_comprados', methods=['post'])
def delete_from():
    conn = mysql.connector.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # Executa a consulta SQL
            cursor.execute("DELETE FROM produtos_comprados")
            conn.commit()
    finally:
        conn.close()
    return redirect(url_for("produtos_comprados"))
#deleta os produtos do carrinho
def delete_from_carrinho():
    conn = mysql.connector.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # Executa a consulta SQL
            cursor.execute("DELETE FROM carrinho")
            conn.commit()
    finally:
        conn.close()
#soma a quantidade do carrinho com o preco
def recuperar_quantidade():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantidade) * SUM(preco) FROM carrinho")
    quant = cursor.fetchall()
    conn.close()
    return quant[:4]

def obter_produtos():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos")
        produto = cursor.fetchall()
        return produto
    except mysql.connector.Error as err:
        print("Erro ao obter produtos:", err)
    finally:
        if connection:
            connection.close()
            
# Função para realizar a consulta no banco de dados
def consultar_produto(descricao):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE descricao LIKE %s", (f'%{descricao}%',))
    produtos_c = cursor.fetchall()
    conn.close()
    return produtos_c

#abrira a tela de vendas ,tera a opiscao de cadastar produtos ou alterar e vender    
@app.route('/convenio', methods=['GET', 'POST'])
def convenio():
    quants = recuperar_quantidade()
    registros = recuperar_registros()
    produto_c = None
    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        if nome_produto:
            produto_c = consultar_produto(nome_produto)
    
    produto = obter_produtos()
    return render_template('convenio.html', produto=produto, produto_c=produto_c, registros=registros, quants=quants)

@app.route("/adiciona_carrinho", methods=['POST','GET'])
def ad_carrinho():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    id = request.form.get('id')
    codigo = request.form.get('codigo')
    descricao = request.form.get('nome')
    preco = request.form.get('preco')
    ncm = request.form.get('ncm')
    categoria = request.form.get('categoria')
    quantidade = request.form.get('quantidade')
    
    #sistema de cadastra ao carrinho de produtos
    if request.method == "POST":
      selected_option = request.form['a']
    if selected_option == 'carrinho':
        if verificar_carrinho_existente(id, descricao, preco):
        # Se o produto já existir, atualize apenas a quantidade
         try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("UPDATE carrinho SET quantidade = quantidade + %s WHERE id = %s AND descricao = %s AND preco = %s  AND ncm = %s AND codigo = %s AND categoria = %s", (quantidade, id, descricao, preco,ncm,codigo,categoria))
            print("carrinho atualizado")
            conn.commit()
         except mysql.connector.Error as err:
            print("Erro ao atualizar quantidade do produto do carrinho:", err) 
         finally:
            if conn:
                conn.close()    
        else:
        # Se o produto não existir, insira-o na tabela

            # Verifica se o id não é 'None' antes de inserir
            if id is not None:
                print("cadastrado no carrinho")
                cursor.execute(f"INSERT INTO carrinho (id,descricao,preco,quantidade,ncm,codigo,categoria) VALUES ('{id}','{descricao}','{preco}','{quantidade}','{ncm}','{codigo}','{categoria}')")
                conn.commit()
            else:
                print("Erro: produto nao cadastrado no carrinho") 
    return redirect(url_for('convenio'))

@app.route('/ad',methods=['POST'])
def consu_produto():
    descricao = request.form.get('nome_produto_dd')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE descricao LIKE %s", (f'%{descricao}%',))
    produtos_dd = cursor.fetchall()
    conn.close()
    return render_template('alterar_dd.html',produtos_dd=produtos_dd)

@app.route('/alterar')
def alterar_p():
    # Conecta ao banco de dados MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # Executa a consulta SQL para obter os dados da tabela
    cursor.execute("SELECT * FROM produtos")

    # Obtém todas as linhas do resultado
    rows = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Renderiza a página HTML com os dados da tabela
    return render_template('alterar_dd.html', rows=rows)

@app.route('/altera_p',methods=['POST'])
def alterar(): 
    return redirect(url_for("alterar_p"))

@app.route("/ad_prod_dd", methods=['POST','GET'])
def ad_prod_dd():
 id = request.form.get('id')
 codigo = request.form.get('codigo')
 descricao = request.form.get('nome')
 preco = request.form.get('preco')
 ncm = request.form.get('ncm')
 quantidade = request.form.get('quantidade')

 try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos SET quantidade = %s, descricao = %s, preco = %s, ncm = %s, codigo = %s WHERE id = %s """, (quantidade, descricao, preco, ncm, codigo, id))
    conn.commit()
    print("Produto atualizado com sucesso")
 except mysql.connector.Error as err:
    print("Erro ao atualizar o produto:", err)
 finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

    return redirect(url_for('alterar_p'))

#atualiza a tabela produtos-comprados se o produto ja exite sera atualizado
def produtos_comp():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Consulta para buscar todos os produtos do carrinho
        query_carrinho = """
        SELECT id, codigo, ncm, descricao, preco, quantidade
        FROM carrinho;
        """
        cursor.execute(query_carrinho)
        produtos_carrinho = cursor.fetchall()

        for produto in produtos_carrinho:
            id, codigo, ncm, descricao, preco, quantidade = produto

            # Verificar se o produto existe na tabela produtos_comprados
            query_verificar = """
            SELECT id, quantidade
            FROM produtos_comprados
            WHERE codigo = %s;
            """
            cursor.execute(query_verificar, (codigo,))
            resultado = cursor.fetchone()

            if resultado:
                # Produto existe, atualizar a quantidade
                id_prod_comprados, quantidade_existente = resultado
                nova_quantidade = quantidade_existente + quantidade

                query_atualizar = """
                UPDATE produtos_comprados
                SET quantidade = %s
                WHERE id = %s;
                """
                cursor.execute(query_atualizar, (nova_quantidade, id_prod_comprados))
                print('produtos comprados adicionados %s', descricao)
            else:
                # Produto não existe, inserir um novo registro
                query_inserir = """
                INSERT INTO produtos_comprados (codigo, ncm, descricao, preco, quantidade)
                VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(query_inserir, (codigo, ncm, descricao, preco, quantidade))
                print('produtos comprados atualizado %s', descricao)

        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Produtos atualizados com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cadastro',methods=['POST'])
def cadastro():
    return redirect(url_for("cadas_p"))

'''cadastra novos produtos ao banco de dados'''
@app.route('/cad')
def cadas_p():
    return render_template("cadastro.html")

@app.route('/produtos_comprados',methods=['POST'])
def produtos_comprados():
    # Conectando ao banco de dados MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Executando a consulta para obter os produtos comprados
    cursor.execute("SELECT * FROM produtos_comprados")
    produtos = cursor.fetchall()

    # Fechando a conexão com o banco de dados
    cursor.close()
    conn.close()

    # Renderizando o template e passando os produtos
    return render_template('produtos_comprados.html', produtos=produtos)

@app.route('/delet',methods=['POST'])
def deletar_prod_carrinho():
    delete_from_carrinho()
    return redirect(url_for("convenio"))


#imprime o arquivo pdf dos produtos do carrinho
def print_document():
    try:
        # Caminho para o arquivo PDF
        pdf_path = os.path.join('static', 'tabela.pdf')
        if os.path.exists(pdf_path):
            # Comando para imprimir o PDF
            win32api.ShellExecute(
                0,
                "print",
                pdf_path,
                None,
                ".",
                0
            )
            flash('Documento enviado para a impressora com sucesso!', 'success')
        else:
            flash('Arquivo não encontrado.', 'error')
    except Exception as e:
        flash(f'Erro ao tentar imprimir o documento: {e}', 'error')

#sistema que finaliza a compra criando uma pasta pdf "tabela" e deletando todso os produtos
@app.route('/final',methods=['POST'])
def deletar_carrinho():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM carrinho")
        carrinho = cursor.fetchall()

        for item in carrinho:
            id = item['id']
            codigo = item['codigo']
            ncm = item['ncm']
            descricao = item['descricao']
            preco = item['preco']
            quantidade = item['quantidade']
            categoria = item['categoria']

            cursor.execute(
                "UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s AND codigo = %s AND categoria = %s AND ncm = %s AND preco = %s AND descricao = %s",
                (quantidade, id, codigo, categoria, ncm, preco, descricao)
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    data = get_data_from_mysql()

    if data:
        # Gera o PDF
        pdf_file = generate_pdf(data)
        produtos_comprados()
        if pdf_file:
            produtos_comp()
            # Exclui registros do carrinho
            delete_from_carrinho()
            # Retorna o PDF para download
            return send_file(pdf_file, as_attachment=True)
        else:
            flash('Erro ao gerar o PDF.', 'error')
    else:
        flash('Erro ao obter dados do MySQL.', 'error')
        return "Erro ao obter dados do MySQL"


#quarda o valor codigo e a descricao do produto
@app.route("/entrar", methods=['POST','GET'])
def mostar():
 
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    categoria = request.form.get('p')
    id =request.form.get('line')
    ncm =request.form.get('linencm')
    codig = request.form.get('lineEdit')
    descricao = request.form.get('lineEdit_2')
    preco = request.form.get('lineEdit_3')
    quantidade = int(request.form.get('lineEdit_4'))
 

 
 #sistema de inpementacao de produtos no estoque
    if request.method == "POST":
     selected_option = request.form['p']
    if selected_option=='tempeiros':
       categoria= "tempeiros"
       cursor.execute(f"INSERT INTO produtos (id,ncm,codigo,descricao,preco,categoria,quantidade) VALUES ('{id}','{ncm}','{codig}','{descricao}','{preco}','{categoria}','{quantidade}')")
       conn.commit()
          
       return "produto cadastrado com sucesso"
          
    elif selected_option== 'alimentos':
      categoria= "alimentos"
      cursor.execute(f"INSERT INTO produtos (id,ncm,codigo,descricao,preco,categoria,quantidade) VALUES ('{id}','{ncm}','{codig}','{descricao}','{preco}','{categoria}','{quantidade}')")
      conn.commit()
          
      return "produto cadastrado com sucesso"

#Funcao para buscar informacoes do produto pela descricao
def buscar_produto(descricao_produto):
    try:
        connection= mysql.connector.connect(**db_config)
        cursor=  connection.cursor(dictionary=True)
        
        #consultar SQL para buscar o produto pelo descricao
        query= "SELECT id,nome, preco, categoria, quantidade FROM tabela_prod WHERE descricao = %s"
        cursor.execute(query, (descricao_produto,))
        produto = cursor.fetchone()
        
        return produto
    
    except Exception as e:
        print("Erro ao buscar produto:", e)
        return None
    
    finally:
        if connection:
            connection.close()
            
# Rota para lidar com a busca do produto
@app.route('/buscar_produto', methods=['POST'])
def buscar():
    nome_produto = request.form['nome_produto']
    produto = buscar_produto(nome_produto)
    
    if produto:
        return redirect('produto.html', produto=produto)
    else:
        return redirect('/')
    



    
if __name__ == "__main__":
    app.run(debug=True)    
