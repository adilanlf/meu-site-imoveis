import sqlite3
import os

UPLOADS_DIR = "static/uploads"

# Conecta ao banco
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Pede o ID do imóvel
imovel_id = input("Digite o ID do imóvel que deseja atualizar as fotos: ")

# Busca o imóvel
c.execute("SELECT fotos FROM imoveis WHERE id = ?", (imovel_id,))
imovel = c.fetchone()

if not imovel:
    print("❌ Imóvel não encontrado!")
else:
    fotos = imovel[0].split(",") if imovel[0] else []

    while True:
        print("\nFotos atuais:")
        for i, foto in enumerate(fotos, start=1):
            print(f"{i}. {foto}")

        print("\nO que deseja fazer?")
        print("1 - Adicionar fotos")
        print("2 - Remover fotos")
        print("3 - Finalizar")
        escolha = input("Escolha uma opção (1/2/3): ")

        if escolha == "1":
            novas_fotos = input("Digite os nomes das fotos a adicionar, separados por vírgula: ")
            for f in [f.strip() for f in novas_fotos.split(",")]:
                caminho_foto = os.path.join(UPLOADS_DIR, f)
                if not os.path.isfile(caminho_foto):
                    print(f"⚠ Foto {f} não encontrada na pasta {UPLOADS_DIR}, não será adicionada.")
                elif f in fotos:
                    print(f"⚠ Foto {f} já existe e não será duplicada.")
                else:
                    fotos.append(f)
                    print(f"✅ Foto {f} adicionada.")
        elif escolha == "2":
            remover = input("Digite os números das fotos a remover, separados por vírgula: ")
            try:
                indices = sorted([int(x)-1 for x in remover.split(",")], reverse=True)
                for idx in indices:
                    if 0 <= idx < len(fotos):
                        print(f"Removendo foto: {fotos[idx]}")
                        fotos.pop(idx)
                    else:
                        print(f"⚠ Índice {idx+1} inválido!")
            except ValueError:
                print("⚠ Entrada inválida!")
        elif escolha == "3":
            break
        else:
            print("⚠ Opção inválida! Tente novamente.")

    # Atualiza no banco
    c.execute("UPDATE imoveis SET fotos = ? WHERE id = ?", (",".join(fotos), imovel_id))
    conn.commit()
    print("\n✅ Fotos atualizadas com sucesso!")

conn.close()
