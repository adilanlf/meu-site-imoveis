import sqlite3

DB_NAME = "database.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# ===== CAMPOS EXISTENTES =====
def add_column(nome, tipo):
    try:
        c.execute(f"ALTER TABLE imoveis ADD COLUMN {nome} {tipo}")
        print(f"✅ Campo '{nome}' adicionado.")
    except Exception:
        print(f"⚠️  Campo '{nome}' já existe.")

add_column("dormitorios", "INTEGER DEFAULT 0")
add_column("banheiros", "INTEGER DEFAULT 0")
add_column("vagas", "INTEGER DEFAULT 0")
add_column("area", "TEXT DEFAULT ''")
add_column("destaque", "INTEGER DEFAULT 0")
add_column("descricao_html", "TEXT DEFAULT ''")

conn.commit()
conn.close()
print("\n🏁 Banco atualizado com sucesso!")

