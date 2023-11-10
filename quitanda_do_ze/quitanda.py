from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandaiv"

usuario = "igor"
senha = "quitanda@123"
login = False

if session:
    session.clear()

@app.route('/')
def index():
    iniciar_db() #CHAMANDO O BD
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template('index.html', produtos=produtos, title=title)

def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db() #CHAMANDO O BD
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")

@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM produtos WHERE id = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

@app.route("/cadastro",methods=["post"])
def cadastro():
    if verifica_sessao():
        titulo=request.form['titulo']
        conteudo=request.form['conteudo']
        preco=request.form['preco']
        imagem=request.files['imagem']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+titulo+'.png'
        imagem.save("static/img/produtos/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (titulo, conteudo, preco, imagem) VALUES (?, ?, ?, ?)',(titulo,conteudo,preco,filename))
        conexao.commit()
        conexao.close()
        return redirect("/login")
    else:
        return redirect("/adm")
    
@app.route("/cadprodutos")
def cadprodutos():
        if verifica_sessao():
            title = "Cadastro de produtos"
            return render_template("cadprodutos.html", title=title)
        else:
            return redirect("/login")

@app.route("/login")
def login():
    title = "Login"
    return render_template("login.html", title=title)

@app.route("/acesso", methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

#CONEXÃO COM BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.bd")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

@app.route("/editar/<id>")
def editar(id):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id = ?',(id,)).fetchall()
        conexao.close()
        title = "Edição de produtos"
        return render_template("editar.html", produtos=produtos, title=title)
    else:
        return redirect("/login")
    
@app.route("/editproduto", methods=['POST'])
def editproduto():
    id = request.form['id']
    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    preco = request.form['preco']
    imagem = request.files['imagem']
    id_foto=str(uuid.uuid4().hex)
    filename=id_foto+titulo+'.png'
    imagem.save("static/img/produtos/"+filename)
    conexao = conecta_database()
    conexao.execute('UPDATE posts SET titulo = ?, conteudo = ?, preco = ?, imagem = ? WHERE id  = ?', (titulo,conteudo,preco,filename,id))
    conexao.commit()
    conexao.close()
    return redirect('/')

@app.route("/busca",methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE titulo LIKE "%" || ? || "%"',(busca,)).fetchall()
    return render_template("home.html", produtos=produtos)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

if __name__ == '__main__':
    app.run(debug=True)