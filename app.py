from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import sqlite3
import os
from datetime import datetime  # ✅ Import adicionado

# Configurações
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Alterar para algo seguro

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DATABASE = "database.db"

# Usuário Admin
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "senha123")

# User class para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Função para conectar ao banco
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Rota Home (com busca, filtros e ordenação)
@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()

    # parâmetros da querystring
    busca = request.args.get("busca", "").strip()
    dormitorios = request.args.get("dormitorios", "").strip()
    banheiros = request.args.get("banheiros", "").strip()
    ordenar = request.args.get("ordenar", "").strip()  # preco_asc, preco_desc, area, etc.

    where_clauses = []
    params = []

    # busca por título/descrição
    if busca:
        where_clauses.append("(titulo LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{busca}%", f"%{busca}%"])

    # filtros numéricos (>=)
    if dormitorios:
        try:
            d_min = int(dormitorios)
            where_clauses.append("COALESCE(CAST(dormitorios AS INTEGER), 0) >= ?")
            params.append(d_min)
        except ValueError:
            pass

    if banheiros:
        try:
            b_min = int(banheiros)
            where_clauses.append("COALESCE(CAST(banheiros AS INTEGER), 0) >= ?")
            params.append(b_min)
        except ValueError:
            pass

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # ordenação: lidar com preco armazenado como texto removendo R$, pontos e vírgulas
    if ordenar == "preco_asc":
        order_sql = "ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco, 'R$', ''), '.', ''), ',', '') AS INTEGER) ASC"
    elif ordenar == "preco_desc":
        order_sql = "ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco, 'R$', ''), '.', ''), ',', '') AS INTEGER) DESC"
    elif ordenar == "area":
        order_sql = "ORDER BY COALESCE(CAST(area AS INTEGER), 0) DESC"
    else:
        # padrão: mais recentes (id descendente)
        order_sql = "ORDER BY id DESC"

    query = f"SELECT * FROM imoveis {where_sql} {order_sql}"
    imoveis = conn.execute(query, params).fetchall()
    conn.close()

    current_year = datetime.now().year
    # note: seu template usa request.args.get diretamente, então não é obrigatório passar 'busca'/'ordenar'
    return render_template("index.html", imoveis=imoveis, current_year=current_year)

# Rota Detalhes do Imóvel
@app.route("/imovel/<int:id>")
def detalhes(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()
    conn.close()
    if not imovel:
        return "Imóvel não encontrado"
    fotos = imovel["fotos"].split(",") if imovel["fotos"] else []
    return render_template("detalhes.html", imovel=imovel, fotos=fotos)

# Login
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

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Área Admin
@app.route("/admin")
@login_required
def admin():
    conn = get_db_connection()
    imoveis = conn.execute("SELECT * FROM imoveis").fetchall()
    conn.close()
    return render_template("admin.html", imoveis=imoveis)

# Adicionar Imóvel
@app.route("/add", methods=["POST"])
@login_required
def add_imovel():
    titulo = request.form["titulo"]
    descricao = request.form["descricao"]
    preco = request.form["preco"]
    dormitorios = request.form.get("dormitorios", 0)
    banheiros = request.form.get("banheiros", 0)
    vagas = request.form.get("vagas", 0)
    area = request.form.get("area", "")
    destaque = 1 if request.form.get("destaque") else 0

    fotos = request.files.getlist("fotos")
    nomes_fotos = []
    for foto in fotos:
        if foto.filename:
            filename = foto.filename
            foto.save(os.path.join("static/uploads", filename))
            nomes_fotos.append(filename)

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO imoveis (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, fotos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, ",".join(nomes_fotos)))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

# Editar Imóvel
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_imovel(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        dormitorios = request.form.get("dormitorios", 0)
        banheiros = request.form.get("banheiros", 0)
        vagas = request.form.get("vagas", 0)
        area = request.form.get("area", "")
        destaque = 1 if request.form.get("destaque") else 0

        fotos = request.files.getlist("fotos")
        nomes_fotos = imovel["fotos"].split(",") if imovel["fotos"] else []

        for foto in fotos:
            if foto.filename:
                filename = foto.filename
                foto.save(os.path.join("static/uploads", filename))
                nomes_fotos.append(filename)

        conn.execute("""
            UPDATE imoveis
            SET titulo=?, descricao=?, preco=?, dormitorios=?, banheiros=?, vagas=?, area=?, destaque=?, fotos=?
            WHERE id=?
        """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, ",".join(nomes_fotos), id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))

    conn.close()
    return render_template("edit_imovel.html", imovel=imovel)

# Deletar Imóvel
@app.route("/delete/<int:id>")
@login_required
def delete_imovel(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM imoveis WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)




