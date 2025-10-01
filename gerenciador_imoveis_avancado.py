# gerenciador_imoveis_avancado.py
import sqlite3

DATABASE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# LISTAR IMÓVEIS (DETALHES COMPLETOS)
# ==============================
def listar_imoveis(conn):
    imoveis = conn.execute("SELECT * FROM imoveis").fetchall()
    if not imoveis:
        print("\nNenhum imóvel cadastrado.\n")
        return imoveis

    print("\n=== Lista de Imóveis (detalhes completos) ===")
    for imovel in imoveis:
        print(f"\nID: {imovel['id']}")
        print(f"Título: {imovel['titulo']}")
        print(f"Descrição: {imovel['descricao']}")
        print(f"Preço: {imovel['preco']}")
        print(f"Dormitórios: {imovel['dormitorios']}")
        print(f"Banheiros: {imovel['banheiros']}")
        print(f"Vagas: {imovel['vagas']}")
        print(f"Área: {imovel['area']} m²")
        print(f"Destaque: {'Sim' if imovel['destaque'] else 'Não'}")

        fotos = imovel["fotos"].split(",") if imovel["fotos"] else []
        if fotos:
            print("Fotos:")
            for idx, foto in enumerate(fotos, start=1):
                print(f"   {idx}. {foto}")
        else:
            print("Fotos: Nenhuma cadastrada")
        print("-" * 40)
    
    print()
    return imoveis


# ==============================
# ADICIONAR IMÓVEL
# ==============================
def adicionar_imovel(conn):
    print("\n=== Adicionar Imóvel ===")
    titulo = input("Título: ")
    if titulo.lower() == "quit": return
    descricao = input("Descrição: ")
    if descricao.lower() == "quit": return
    preco = input("Preço (ex: R$ 250.000): ")
    if preco.lower() == "quit": return
    dormitorios = input("Dormitórios: ")
    if dormitorios.lower() == "quit": return
    banheiros = input("Banheiros: ")
    if banheiros.lower() == "quit": return
    vagas = input("Vagas: ")
    if vagas.lower() == "quit": return
    area = input("Área (m²): ")
    if area.lower() == "quit": return
    destaque = input("Destaque? (s/n): ").lower()
    if destaque == "quit": return

    fotos = input("Nomes das fotos separados por vírgula (ex: casa1.jpg,casa2.jpg): ")
    if fotos.lower() == "quit": return

    conn.execute("""
        INSERT INTO imoveis (titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque, fotos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, 1 if destaque == "s" else 0, fotos))
    conn.commit()
    print("✅ Imóvel adicionado com sucesso!\n")


# ==============================
# EDITAR IMÓVEL
# ==============================
def editar_imovel(conn):
    print("\n=== Editar Imóvel ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = input("Digite o ID do imóvel ou 'quit' para sair: ")
    if id_escolhido.lower() == "quit": return
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    print("\nDeixe em branco para manter o valor atual.")
    titulo = input(f"Título [{imovel['titulo']}]: ") or imovel['titulo']
    if titulo.lower() == "quit": return
    descricao = input(f"Descrição [{imovel['descricao']}]: ") or imovel['descricao']
    if descricao.lower() == "quit": return
    preco = input(f"Preço [{imovel['preco']}]: ") or imovel['preco']
    if preco.lower() == "quit": return
    dormitorios = input(f"Dormitórios [{imovel['dormitorios']}]: ") or imovel['dormitorios']
    if dormitorios.lower() == "quit": return
    banheiros = input(f"Banheiros [{imovel['banheiros']}]: ") or imovel['banheiros']
    if banheiros.lower() == "quit": return
    vagas = input(f"Vagas [{imovel['vagas']}]: ") or imovel['vagas']
    if vagas.lower() == "quit": return
    area = input(f"Área [{imovel['area']}]: ") or imovel['area']
    if area.lower() == "quit": return
    destaque = input(f"Destaque (s/n) [{ 's' if imovel['destaque'] else 'n' }]: ").lower()
    if destaque == "quit": return

    conn.execute("""
        UPDATE imoveis
        SET titulo=?, descricao=?, preco=?, dormitorios=?, banheiros=?, vagas=?, area=?, destaque=?
        WHERE id=?
    """, (titulo, descricao, preco, dormitorios, banheiros, vagas, area, 1 if destaque == "s" else 0, id_escolhido))
    conn.commit()
    print("✅ Imóvel atualizado com sucesso!\n")


# ==============================
# ATUALIZAR / REMOVER FOTOS
# ==============================
def gerenciar_fotos(conn):
    print("\n=== Atualizar / Remover Fotos ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = input("Digite o ID do imóvel ou 'quit' para sair: ")
    if id_escolhido.lower() == "quit": return
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    fotos = imovel["fotos"].split(",") if imovel["fotos"] else []
    print("\nFotos atuais:")
    if fotos:
        for idx, foto in enumerate(fotos, start=1):
            print(f"{idx}. {foto}")
    else:
        print("Nenhuma foto cadastrada.")

    print("\n1. Adicionar novas fotos")
    print("2. Remover foto existente")
    print("0. Cancelar")
    escolha = input("Escolha uma opção: ")

    if escolha == "1":
        novas_fotos = input("Digite os nomes das novas fotos (separados por vírgula): ")
        if novas_fotos.lower() == "quit": return
        fotos.extend([f.strip() for f in novas_fotos.split(",") if f.strip()])
    elif escolha == "2":
        num = input("Digite o número da foto para remover ou 'quit': ")
        if num.lower() == "quit": return
        try:
            num = int(num)
            if 1 <= num <= len(fotos):
                fotos.pop(num - 1)
            else:
                print("❌ Número inválido.")
        except ValueError:
            print("❌ Entrada inválida.")
    else:
        print("Operação cancelada.\n")
        return

    conn.execute("UPDATE imoveis SET fotos=? WHERE id=?", (",".join(fotos), id_escolhido))
    conn.commit()
    print("✅ Fotos atualizadas com sucesso!\n")


# ==============================
# DELETAR IMÓVEL
# ==============================
def deletar_imovel(conn):
    print("\n=== Deletar Imóvel ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = input("Digite o ID do imóvel ou 'quit' para sair: ")
    if id_escolhido.lower() == "quit": return
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    confirm = input(f"Tem certeza que deseja deletar o imóvel {imovel['id']} - {imovel['titulo']}? (s/n): ")
    if confirm.lower() == "s":
        conn.execute("DELETE FROM imoveis WHERE id=?", (id_escolhido,))
        conn.commit()
        print("✅ Imóvel deletado com sucesso!\n")
    else:
        print("Operação cancelada.\n")


# ==============================
# MENU PRINCIPAL
# ==============================
def main():
    conn = get_db_connection()
    while True:
        print("=== GERENCIADOR AVANÇADO DE IMÓVEIS ===")
        print("1. Listar imóveis (detalhes completos)")
        print("2. Adicionar imóvel")
        print("3. Editar imóvel")
        print("4. Atualizar / Remover fotos")
        print("5. Deletar imóvel")
        print("0. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            listar_imoveis(conn)
        elif escolha == "2":
            adicionar_imovel(conn)
        elif escolha == "3":
            editar_imovel(conn)
        elif escolha == "4":
            gerenciar_fotos(conn)
        elif escolha == "5":
            deletar_imovel(conn)
        elif escolha == "0":
            print("Saindo...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.\n")

    conn.close()

if __name__ == "__main__":
    main()
