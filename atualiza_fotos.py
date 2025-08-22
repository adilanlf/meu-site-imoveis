import sqlite3

# Conecta ao banco
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Atualiza as fotos da casa 1
c.execute("""
UPDATE imoveis
SET fotos = 'casa1_1.jpg,casa1_2.jpg,casa1_3.jpg,casa1_4.jpg,casa1_5.jpg,casa1_6.jpg,casa1_7.jpg,casa1_8.jpg,casa1_9.jpg,casa1_10.jpg'
WHERE id = 1
""")

# Salva alterações e fecha conexão
conn.commit()
conn.close()
print("Fotos da casa 1 atualizadas!")
