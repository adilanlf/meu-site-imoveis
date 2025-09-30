import sqlite3

# Conecta ao banco
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Pede o ID do imóvel
imovel_id = input("Digite o ID do imóvel que deseja editar: ")

# Busca o imóvel atual
c.execute("SELECT * FROM imoveis WHERE id = ?", (imovel_id,))
imovel = c.fetchone()

if not imovel:
    print("❌ Imóvel não encontrado!")
else:
    print("\nImóvel atual:")
    print(f"Título: {imovel[1]}")
    print(f"Descrição: {imovel[2]}")
    print(f"Preço: {imovel[3]}")
    print(f"Fotos: {imovel[4]}")

    # Pede novos valores
    novo_titulo = input("Novo título (enter para manter): ") or imovel[1]
    nova_descricao = input("Nova descrição (enter para manter): ") or imovel[2]
    novo_preco = input("Novo preço (enter para manter): ") or imovel[3]

    # Atualiza no banco
    c.execute("""
        UPDATE imoveis
        SET titulo = ?, descricao = ?, preco = ?
        WHERE id = ?
    """, (novo_titulo, nova_descricao, novo_preco, imovel_id))

    conn.commit()
    print("\n✅ Imóvel atualizado com sucesso!")

conn.close()
