from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import sqlite3
import os

# Configurações
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DATABASE = "database.db"

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "senha123")

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    imoveis = conn.execute("SELECT * FROM imoveis").fetchall()
    conn.close()
    return render_template("index.html", imoveis=imoveis)

@app.route("/imovel/<int:id>")
def detalhes(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()
    conn.close()
    if not imovel:
        return "Imóvel não encontrado"
    fotos = imovel["fotos"].split(",") if imovel["fotos"] else []
    return render_template("detalhes.html", imovel=imovel, fotos=fotos)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = User(id=1)
            login_user(user)
            return redirect(url_for("admin"))
        else:
            flash("Usuário ou senha incorretos")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/admin")
@login_required
def admin():
    conn = get_db_connection()
    imoveis = conn.execute("SELECT * FROM imoveis").fetchall()
    conn.close()
    return render_template("admin.html", imoveis=imoveis)

@app.route("/add", methods=["POST"])
@login_required
def add_imovel():
    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    preco = request.form["preco"]
    
    fotos = request.files.getlist("fotos")
    nomes_fotos = []
    for foto in fotos:
        if foto.filename:
            filename = foto.filename
            foto.save(os.path.join(UPLOAD_FOLDER, filename))
            nomes_fotos.append(filename)
    
    conn = get_db_connection()
    conn.execute("INSERT INTO imoveis (titulo, descricao, preco, fotos) VALUES (?, ?, ?, ?)",
                 (titulo, descricao, preco, ",".join(nomes_fotos)))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_imovel(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()

    if not imovel:
        conn.close()
        return "Imóvel não encontrado"

    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]

        # Fotos antigas
        fotos_antigas = imovel["fotos"].split(",") if imovel["fotos"] else []
        remover = request.form.getlist("remover_fotos")
        fotos_restantes = [f for f in fotos_antigas if f not in remover]

        # Remover fisicamente as fotos marcadas
        for foto in remover:
            caminho_foto = os.path.join(UPLOAD_FOLDER, foto)
            if os.path.exists(caminho_foto):
                os.remove(caminho_foto)

        # Novas fotos
        fotos_novas = request.files.getlist("fotos")
        for foto in fotos_novas:
            if foto.filename:
                filename = foto.filename
                foto.save(os.path.join(UPLOAD_FOLDER, filename))
                fotos_restantes.append(filename)

        conn.execute("UPDATE imoveis SET titulo=?, descricao=?, preco=?, fotos=? WHERE id=?",
                     (titulo, descricao, preco, ",".join(fotos_restantes), id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))

    conn.close()
    return render_template("edit.html", imovel=imovel)

@app.route("/delete/<int:id>")
@login_required
def delete_imovel(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()

    if imovel and imovel["fotos"]:
        for foto in imovel["fotos"].split(","):
            caminho_foto = os.path.join(UPLOAD_FOLDER, foto)
            if os.path.exists(caminho_foto):
                os.remove(caminho_foto)

    conn.execute("DELETE FROM imoveis WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE imoveis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                preco TEXT NOT NULL,
                fotos TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    app.run(debug=True)
