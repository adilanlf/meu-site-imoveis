# gerenciador_imoveis_avancado.py
import sqlite3
import sys  # necessário para encerrar o programa

DATABASE = "database.db"

# ==============================
# 🔧 Conexão com o Banco
# ==============================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# ⚙️ Funções Utilitárias
# ==============================
def safe_input(prompt):
    """
    Input seguro — digite 'quit' para encerrar o programa a qualquer momento.
    """
    valor = input(prompt)
    if valor.strip().lower() == "quit":
        print("\n🚪 Saindo do gerenciador de imóveis...\n")
        sys.exit()
    return valor

def has_column(conn, table, column):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = {r["name"] for r in rows}
    return column in cols

def parse_fotos(fotos_str):
    if not fotos_str:
        return []
    return [f.strip() for f in fotos_str.split(",") if f.strip()]

def join_fotos(fotos_list):
    return ",".join([f for f in fotos_list if f])

def input_multilinha(prompt):
    print(prompt)
    print("Dica: cole seu texto completo e digite 'fim' em uma linha nova para encerrar.")
    linhas = []
    while True:
        linha = input()
        if linha.strip().lower() == "quit":
            print("\n🚪 Saindo do gerenciador de imóveis...\n")
            sys.exit()
        if linha.strip().lower() == "fim":
            break
        linhas.append(linha)
    return "\n".join(linhas)

# ==============================
# 📋 Listar Imóveis
# ==============================
def listar_imoveis(conn):
    imoveis = conn.execute("SELECT * FROM imoveis ORDER BY id").fetchall()
    if not imoveis:
        print("\nNenhum imóvel cadastrado.\n")
        return imoveis

    tem_html = has_column(conn, "imoveis", "descricao_html")

    print("\n=== Lista de Imóveis (detalhes completos) ===")
    for imovel in imoveis:
        print(f"\nID: {imovel['id']}")
        print(f"Título: {imovel['titulo']}")
        print(f"Descrição curta: {imovel['descricao']}")
        if tem_html:
            tem = "Sim" if (imovel['descricao_html'] or '').strip() else "Não"
            print(f"Descrição rica (descricao_html): {tem}")
        print(f"Preço: {imovel['preco']}")
        print(f"Dormitórios: {imovel['dormitorios']}")
        print(f"Banheiros: {imovel['banheiros']}")
        print(f"Vagas: {imovel['vagas']}")
        print(f"Área: {imovel['area']}")
        print(f"Destaque: {'Sim' if imovel['destaque'] else 'Não'}")

        fotos = parse_fotos(imovel["fotos"])
        if fotos:
            print("Fotos:")
            for idx, foto in enumerate(fotos, start=1):
                print(f"  {idx}. {foto}")
        else:
            print("Fotos: Nenhuma cadastrada")
        print("-" * 40)
    print()
    return imoveis

# ==============================
# ➕ Adicionar Imóvel
# ==============================
def adicionar_imovel(conn):
    print("\n=== Adicionar Imóvel ===")
    titulo = safe_input("Título: ")
    descricao = safe_input("Descrição curta (resumo): ")

    tem_html = has_column(conn, "imoveis", "descricao_html")
    descricao_html = ""
    if tem_html:
        descricao_html = input_multilinha("\nAgora cole a descrição completa com formatação (emojis, <br>, etc).")

    preco = safe_input("Preço (ex: R$ 250.000): ")
    dormitorios = safe_input("Dormitórios: ")
    banheiros = safe_input("Banheiros: ")
    vagas = safe_input("Vagas: ")
    area = safe_input("Área (m²): ")
    destaque = safe_input("Destaque? (s/n): ").lower()
    destaque_val = 1 if destaque == "s" else 0
    fotos = safe_input("Nomes das fotos (separados por vírgula, ex: casa1.jpg,casa2.jpg): ")

    cols = ["titulo", "descricao", "preco", "dormitorios", "banheiros", "vagas", "area", "destaque", "fotos"]
    vals = [titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque_val, fotos]

    if tem_html:
        cols.insert(2, "descricao_html")
        vals.insert(2, descricao_html)

    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO imoveis ({','.join(cols)}) VALUES ({placeholders})"
    conn.execute(sql, vals)
    conn.commit()
    print("✅ Imóvel adicionado com sucesso!\n")

# ==============================
# ✏️ Editar Imóvel
# ==============================
def editar_imovel(conn):
    print("\n=== Editar Imóvel ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = safe_input("Digite o ID do imóvel: ")
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    tem_html = has_column(conn, "imoveis", "descricao_html")

    print("\nDeixe em branco para manter o valor atual.")
    titulo = safe_input(f"Título [{imovel['titulo']}]: ") or imovel['titulo']
    descricao = safe_input(f"Descrição curta [{imovel['descricao']}]: ") or imovel['descricao']

    if tem_html:
        print("Atualizar descrição completa (descricao_html)? (s/n)")
        if safe_input("").strip().lower() == "s":
            descricao_html = input_multilinha("Cole o novo texto (digite 'fim' para encerrar):")
        else:
            descricao_html = imovel['descricao_html']
    else:
        descricao_html = None

    preco = safe_input(f"Preço [{imovel['preco']}]: ") or imovel['preco']
    dormitorios = safe_input(f"Dormitórios [{imovel['dormitorios']}]: ") or imovel['dormitorios']
    banheiros = safe_input(f"Banheiros [{imovel['banheiros']}]: ") or imovel['banheiros']
    vagas = safe_input(f"Vagas [{imovel['vagas']}]: ") or imovel['vagas']
    area = safe_input(f"Área [{imovel['area']}]: ") or imovel['area']
    destaque = safe_input(f"Destaque (s/n) [{'s' if imovel['destaque'] else 'n'}]: ").lower()
    destaque_val = 1 if destaque == "s" else 0
    novas_fotos = safe_input("Fotos (deixe vazio para manter as atuais): ").strip()
    fotos_final = novas_fotos if novas_fotos else imovel['fotos']

    sets = ["titulo=?", "descricao=?", "preco=?", "dormitorios=?", "banheiros=?", "vagas=?", "area=?", "destaque=?", "fotos=?"]
    vals = [titulo, descricao, preco, dormitorios, banheiros, vagas, area, destaque_val, fotos_final]

    if tem_html:
        sets.insert(2, "descricao_html=?")
        vals.insert(2, descricao_html)

    sql = f"UPDATE imoveis SET {', '.join(sets)} WHERE id=?"
    vals.append(id_escolhido)
    conn.execute(sql, vals)
    conn.commit()
    print("✅ Imóvel atualizado com sucesso!\n")

# ==============================
# 🖼️ Gerenciar Fotos
# ==============================
def gerenciar_fotos(conn):
    print("\n=== Atualizar / Remover Fotos ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = safe_input("Digite o ID do imóvel: ")
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    fotos = parse_fotos(imovel["fotos"])
    print("\nFotos atuais:")
    if fotos:
        for idx, foto in enumerate(fotos, start=1):
            print(f"{idx}. {foto}")
    else:
        print("Nenhuma foto cadastrada.")

    print("\n1. Adicionar novas fotos")
    print("2. Remover foto(s) existente(s)")
    print("0. Cancelar")
    escolha = safe_input("Escolha uma opção: ")

    if escolha == "1":
        novas = safe_input("Digite os nomes das novas fotos (separados por vírgula): ")
        for f in parse_fotos(novas):
            if f not in fotos:
                fotos.append(f)
        print("✅ Fotos adicionadas.")
    elif escolha == "2":
        if not fotos:
            print("Não há fotos para remover.")
            return
        alvos = safe_input("Digite o(s) número(s) da(s) foto(s) para remover (ex: 1,3,4): ")
        try:
            indices = sorted({int(n.strip()) for n in alvos.split(',') if n.strip()}, reverse=True)
            for idx in indices:
                if 1 <= idx <= len(fotos):
                    fotos.pop(idx - 1)
            print("✅ Remoção concluída.")
        except ValueError:
            print("❌ Entrada inválida.")
            return
    else:
        print("Operação cancelada.\n")
        return

    conn.execute("UPDATE imoveis SET fotos=? WHERE id=?", (join_fotos(fotos), id_escolhido))
    conn.commit()
    print("✅ Fotos atualizadas com sucesso!\n")

# ==============================
# ❌ Deletar Imóvel
# ==============================
def deletar_imovel(conn):
    print("\n=== Deletar Imóvel ===")
    imoveis = listar_imoveis(conn)
    if not imoveis: return

    id_escolhido = safe_input("Digite o ID do imóvel: ")
    imovel = conn.execute("SELECT * FROM imoveis WHERE id=?", (id_escolhido,)).fetchone()
    if not imovel:
        print("❌ Imóvel não encontrado.\n")
        return

    confirm = safe_input(f"Tem certeza que deseja deletar o imóvel {imovel['id']} - {imovel['titulo']}? (s/n): ")
    if confirm.lower() == "s":
        conn.execute("DELETE FROM imoveis WHERE id=?", (id_escolhido,))
        conn.commit()
        print("✅ Imóvel deletado com sucesso!\n")
    else:
        print("Operação cancelada.\n")

# ==============================
# 🏠 Menu Principal
# ==============================
def main():
    conn = get_db_connection()
    print("💡 Dica: digite 'quit' em qualquer momento para sair do sistema.")
    while True:
        print("\n=== GERENCIADOR AVANÇADO DE IMÓVEIS ===")
        print("1. Listar imóveis (detalhes completos)")
        print("2. Adicionar imóvel")
        print("3. Editar imóvel")
        print("4. Atualizar / Remover fotos")
        print("5. Deletar imóvel")
        print("0. Sair")
        escolha = safe_input("Escolha uma opção: ")

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


