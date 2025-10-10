# ===========================================
# 🏠 Celo Imóveis - Aplicação Flask com Cloudinary
# ===========================================
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from datetime import datetime
from dotenv import load_dotenv
import sqlite3
import os
import cloudinary
import cloudinary.uploader

# ===========================================
# ⚙️ Configurações Iniciais
# ===========================================
load_dotenv()

app = Flask(__name__)

# 🔐 Segurança
app.secret_key = os.getenv("SECRET_KEY")

# 🗄️ Banco de dados
DATABASE = "database.db"

# 👤 Credenciais admin
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ☁️ Configuração Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# ===========================================
# 🔑 Flask-Login
# ===========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ===========================================
# 🗄️ Banco de Dados
# ===========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ===========================================
# 🏠 Página Inicial
# ===========================================
@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()

    busca = request.args.get("busca", "").strip()
    ordenar = request.args.get("ordenar", "").strip()
    destaque = request.args.get("destaque", "").strip()

    where_clauses = []
    params = []

    if busca:
        where_clauses.append("(titulo LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{busca}%", f"%{busca}%"])

    if destaque == "1":
        where_clauses.append("destaque = 1")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    if ordenar == "preco_asc":
        order_sql = "ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco, 'R$', ''), '.', ''), ',', '') AS INTEGER) ASC"
    elif ordenar == "preco_desc":
        order_sql = "ORDER BY CAST(REPLACE(REPLACE(REPLACE(preco, 'R$', ''), '.', ''), ',', '') AS INTEGER) DESC"
    else:
        order_sql = "ORDER BY id DESC"

    query = f"SELECT * FROM imoveis {where_sql} {order_sql}"
    imoveis = conn.execute(query, params).fetchall()
    conn.close()

    current_year = datetime.now().year
    return render_template("index.html", imoveis=imoveis, current_year=current_year)

# ===========================================
# 🏘️ Detalhes do Imóvel
# ===========================================
@app.route("/imovel/<int:id>")
def detalhes(id):
    conn = get_db_connection()
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id,)).fetchone()
    conn.close()
    if not imovel:
        return "Imóvel não encontrado"

    fotos = []
    if imovel["fotos"]:
        for f in imovel["fotos"].split(","):
            if f.startswith("http"):  # Se for Cloudinary
                fotos.append(f)
            else:  # Se for local (antigo)
                fotos.append(url_for("static", filename=f"uploads/{f}"))

    return render_template("detalhes.html", imovel=imovel, fotos=fotos)

# ===========================================
# 🔐 Login / Logout
# ===========================================
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
            flash("Usuário ou senha incorretos", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ===========================================
# ⚙️ Painel Admin
# ===========================================
@app.route("/admin")
@login_required
def admin():
    conn = get_db_connection()
    imoveis = conn.execute("SELECT * FROM imoveis").fetchall()
    conn.close()
    return render_template("admin.html", imoveis=imoveis)

# ===========================================
# ➕ Adicionar Imóvel (com upload no Cloudinary)
# ===========================================
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
    urls_fotos = []

    for foto in fotos:
        if foto.filename:
            try:
                # Upload direto para Cloudinary
                upload = cloudinary.uploader.upload(foto, folder="celoimoveis")
                urls_fotos.append(upload["secure_url"])
            except Exception as e:
                print("⚠️ Erro no upload Cloudinary:", e)
                # fallback local se falhar
                path_local = os.path.join("static/uploads", foto.filename)
                foto.save(path_local)
                urls_fotos.append(foto.filename)

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO imoveis (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, fotos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, ",".join(urls_fotos)))
    conn.commit()
    conn.close()
    flash("🏠 Imóvel adicionado com sucesso!", "info")
    return redirect(url_for("admin"))

# ===========================================
# ✏️ Editar Imóvel
# ===========================================
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

        novas_fotos = request.files.getlist("fotos")
        fotos_existentes = imovel["fotos"].split(",") if imovel["fotos"] else []

        for foto in novas_fotos:
            if foto.filename:
                upload = cloudinary.uploader.upload(foto, folder="celoimoveis")
                fotos_existentes.append(upload["secure_url"])

        conn.execute("""
            UPDATE imoveis
            SET titulo=?, descricao=?, preco=?, dormitorios=?, banheiros=?, vagas=?, area=?, destaque=?, fotos=?
            WHERE id=?
        """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, ",".join(fotos_existentes), id))
        conn.commit()
        conn.close()
        flash("✅ Imóvel atualizado com sucesso!", "info")
        return redirect(url_for("admin"))

    conn.close()
    return render_template("edit_imovel.html", imovel=imovel)

# ===========================================
# ❌ Deletar Imóvel
# ===========================================
@app.route("/delete/<int:id>")
@login_required
def delete_imovel(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM imoveis WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Imóvel removido!", "warning")
    return redirect(url_for("admin"))

# ===========================================
# 🚀 Inicialização
# ===========================================
if __name__ == "__main__":
    app.run(debug=True)












