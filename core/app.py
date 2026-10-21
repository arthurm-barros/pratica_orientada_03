from flask import Flask, redirect, render_template, request, url_for, flash
from sqlalchemy import select

from database import SessionLocal, criar_engine
from models import Book, User

app = Flask(__name__)
app.secret_key = '1aa0f4da-f708-4794-b4f6-cb001954b004'

@app.route("/")
def index():
    session = criar_engine()[1]
    usuarios = session.scalars(select(User)).all()
    livros = session.scalars(select(Book)).all()
    return render_template('index.html')

@app.route("/usuario/novo", methods=["POST","GET"])
def new_user():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        if not nome:
            flash('Digite um nome para se cadastrar', 'erro')
            redirect(url_for('new_user'))
        if not email:
            flash('Digite um email para se cadastrar', 'erro')
            redirect(url_for('new_user'))
        if not senha:
            flash('Digite uma senha para se cadastrar', 'erro')
            redirect(url_for('new_user'))

        session = criar_engine()[1]

        usuario = session.scalars(select(User).where(User.nome==nome))
        if usuario:
            flash('Já existe um usuário com este nome', 'erro')
            return redirect(url_for('new_user'))

        usuario = session.scalars(select(User).where(User.email==email))
        if usuario:
            flash('Já existe um usuário com este email', 'erro')

        usuario_novo = User(nome=nome, email=email)
        session.add(usuario_novo)
        session.commit()

        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route("/livros/novo", methods=["POST","GET"])
def new_book():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        user_id = request.form.get("user_id")

        if not titulo:
            flash('Insira um título para cadastrar o livro.', 'erro')
            redirect(url_for('new_book'))
        if not user_id:
            flash('Informe um usuário para cadastrar o livro.', 'erro')
            redirect(url_for('new_book'))

        session = SessionLocal()
        livro = session.scalars(select(Book).where(Book.titulo == titulo)).first()
        if livro:
            flash('Já existe um livro com este título.', 'erro')
            return redirect(url_for('new_book'))

        livro_novo = Book(titulo=titulo, user_id=int(user_id))
        session.add(livro_novo)
        session.commit()
        return redirect(url_for("cadastro_livro"))

    return render_template("book_form.html")

@app.route("/livros/listar")
def listar_livro():
    session = criar_engine()[1]
    livros = session.scalars(select(Book).order_by(Book.titulo)).all()
    return render_template("index.html", livros=livros)


@app.route("/usuarios/listar")
def listar_usuarios():
    session = criar_engine()[1]
    usuarios = session.scalars(select(User).order_by(User.nome)).all()
    return render_template("index.html", usuarios=usuarios)


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