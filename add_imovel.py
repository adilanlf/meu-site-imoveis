# add_imovel.py
import sqlite3

DATABASE = "database.db"

def add_imovel():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    titulo = input("Título do imóvel: ")
    descricao = input("Descrição: ")
    preco = input("Preço (ex: R$ 250.000): ")
    dormitorios = input("Dormitórios: ")
    banheiros = input("Banheiros: ")
    vagas = input("Vagas: ")
    area = input("Área (m²): ")
    destaque = input("Destaque? (s/n): ").lower() == "s"

    fotos = input("Nomes das fotos separados por vírgula (ex: casa2_1.jpg,casa2_2.jpg): ")

    c.execute("""
        INSERT INTO imoveis (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, fotos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, 1 if destaque else 0, fotos))

    conn.commit()
    conn.close()
    print("✅ Imóvel adicionado com sucesso!")

if __name__ == "__main__":
    add_imovel()
