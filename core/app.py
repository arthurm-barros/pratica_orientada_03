from flask import Flask, redirect, render_template, request, url_for, flash, session
from sqlalchemy import select

from database import SessionLocal, criar_engine
from models import Book, User, buscar_usuario_por_email

app = Flask(__name__)
app.secret_key = '1aa0f4da-f708-4794-b4f6-cb001954b004'

@app.route("/")
def index():
    _session = criar_engine()[1]
    usuarios = _session.scalars(select(User)).all()
    livros = _session.scalars(select(Book)).all()
    try:
        return render_template('index.html', usuario=session['usuario_nome'])
    except KeyError:
        return render_template('index.html')

@app.route("/usuario/novo", methods=["POST","GET"])
def new_user():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not nome:
            flash('Digite um nome para se cadastrar', 'erro')
            return redirect(url_for('new_user'))
        if not email:
            flash('Digite um email para se cadastrar', 'erro')
            return redirect(url_for('new_user'))
        if not senha:
            flash('Digite uma senha para se cadastrar', 'erro')
            return redirect(url_for('new_user'))

        session = criar_engine()[1]

        usuario = session.scalars(select(User).where(User.nome==nome)).first()
        if usuario:
            flash('Já existe um usuário com este nome', 'erro')
            return redirect(url_for('new_user'))

        usuario = session.scalars(select(User).where(User.email==email)).first()
        if usuario:
            flash('Já existe um usuário com este email', 'erro')
            return redirect(url_for('new_user'))

        usuario_novo = User(nome=nome, email=email, senha=senha)
        session.add(usuario_novo)
        session.commit()

        return redirect(url_for('login'))
    return render_template('user_form.html')


@app.route("/livros/novo", methods=["POST","GET"])
def new_book():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        titulo = request.form.get("titulo")

        if not titulo:
            flash('Insira um título para cadastrar o livro.', 'erro')
            redirect(url_for('new_book'))

        _session = criar_engine()[1]
        livro = _session.scalars(select(Book).where(Book.titulo == titulo)).first()
        if livro:
            flash('Já existe um livro com este título.', 'erro')
            return redirect(url_for('new_book'))

        livro_novo = Book(titulo=titulo, usuario_id=int(session['usuario_id']))
        _session.add(livro_novo)
        _session.commit()
        return redirect(url_for("new_book"))

    return render_template("book_form.html", usuario=session['usuario_nome'])


@app.route("/livros/listar")
def listar_livros():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    _session = criar_engine()[1]
    livros = _session.scalars(select(Book).order_by(Book.titulo)).all()
    return render_template("livros.html", livros=livros, usuario=session['usuario_nome'])


@app.route("/usuarios/listar")
def listar_usuarios():
    if 'usuario_nome' not in session:
        return redirect(url_for('login'))

    session = criar_engine()[1]
    usuarios = session.scalars(select(User).order_by(User.nome)).all()
    return render_template("index.html", usuarios=usuarios, usuario=session['usuario_nome'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email:
        flash('Insira seu email para fazer login', 'erro')
        return redirect(url_for('login'))
    if not senha:
        flash('Insira sua senha para fazer login', 'erro')
        return redirect(url_for('login'))

    usuario = buscar_usuario_por_email(email)
    if not usuario:
        flash('Nenhum usuário com estas credenciais foi encontrado', 'erro')
        return redirect('login')
    
    session['usuario_nome'] = usuario.nome
    session['usuario_id'] = usuario.id

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('usuario_nome')
    session.pop('usuario_id')
    return redirect(url_for('login'))