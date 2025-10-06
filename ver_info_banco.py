# ===========================================
# 🧾 VER INFORMAÇÕES DO BANCO DE DADOS
# ===========================================
# Função: Mostrar último ID cadastrado, contador interno e total de imóveis
# Autor: Adilan (Celo Imóveis)
# ===========================================

import sqlite3

# Caminho do banco de dados local
DATABASE = "database.db"

def ver_info_banco():
    """Mostra informações importantes sobre a tabela 'imoveis'."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        print("\n🔍 Analisando banco de dados...\n")

        # Total de registros atuais
        cursor.execute("SELECT COUNT(*) FROM imoveis")
        total = cursor.fetchone()[0]

        # Último ID existente (em uso)
        cursor.execute("SELECT MAX(id) FROM imoveis")
        ultimo_id = cursor.fetchone()[0]

        # Contador interno (sqlite_sequence)
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='imoveis'")
        seq = cursor.fetchone()

        print("📘 INFORMAÇÕES DO BANCO DE DADOS:")
        print("────────────────────────────────────")
        print(f"🏠 Total de imóveis cadastrados: {total}")

        if ultimo_id:
            print(f"🆔 Último ID existente: {ultimo_id}")
        else:
            print("🆔 Nenhum imóvel cadastrado ainda.")

        if seq:
            print(f"⚙️ Contador interno (sqlite_sequence): {seq[0]}")
            print(f"📈 Próximo ID previsto: {seq[0] + 1}")
        else:
            print("⚠️ Nenhum contador encontrado (provável banco novo).")

        print("────────────────────────────────────\n")

    except Exception as e:
        print(f"❌ Erro ao acessar o banco: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    ver_info_banco()
