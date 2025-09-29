import sqlite3

DB_NAME = "database.db"

# Conecta ao banco
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Adiciona os novos campos se ainda não existirem
try:
    c.execute("ALTER TABLE imoveis ADD COLUMN dormitorios INTEGER DEFAULT 0")
    print("Campo 'dormitorios' adicionado.")
except:
    print("Campo 'dormitorios' já existe.")

try:
    c.execute("ALTER TABLE imoveis ADD COLUMN banheiros INTEGER DEFAULT 0")
    print("Campo 'banheiros' adicionado.")
except:
    print("Campo 'banheiros' já existe.")

try:
    c.execute("ALTER TABLE imoveis ADD COLUMN vagas INTEGER DEFAULT 0")
    print("Campo 'vagas' adicionado.")
except:
    print("Campo 'vagas' já existe.")

try:
    c.execute("ALTER TABLE imoveis ADD COLUMN area INTEGER DEFAULT 0")
    print("Campo 'area' adicionado.")
except:
    print("Campo 'area' já existe.")

try:
    c.execute("ALTER TABLE imoveis ADD COLUMN destaque INTEGER DEFAULT 0")
    print("Campo 'destaque' adicionado.")
except:
    print("Campo 'destaque' já existe.")

# Salva alterações
conn.commit()
conn.close()

print("Banco atualizado com sucesso!")
