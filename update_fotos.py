import sqlite3

# Caminho do banco de dados
DATABASE = "database.db"

def atualizar_fotos(id_imovel, lista_fotos):
    """
    Atualiza a lista de fotos de um imóvel específico no banco de dados.
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    fotos_str = ",".join(lista_fotos)  # Transforma lista em string separada por vírgula

    c.execute("UPDATE imoveis SET fotos = ? WHERE id = ?", (fotos_str, id_imovel))

    conn.commit()
    conn.close()
    print(f"✅ Fotos do imóvel {id_imovel} atualizadas com sucesso!")

if __name__ == "__main__":
    # Pergunta ID do imóvel
    id_imovel = int(input("Digite o ID do imóvel que deseja atualizar: "))

    # Pergunta nomes das fotos
    fotos_input = input("Digite os nomes das fotos separados por vírgula (ex: casa2_1.jpg,casa2_2.jpg,...): ")

    # Converte para lista
    lista_fotos = [f.strip() for f in fotos_input.split(",") if f.strip()]

    atualizar_fotos(id_imovel, lista_fotos)
