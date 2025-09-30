import sqlite3

# Conecta ao banco
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Pede o ID do imóvel
imovel_id = input("Digite o ID do imóvel que deseja editar: ")

# Busca o imóvel
c.execute("SELECT titulo, descricao, preco FROM imoveis WHERE id = ?", (imovel_id,))
imovel = c.fetchone()

if not imovel:
    print("❌ Imóvel não encontrado!")
else:
    titulo, descricao, preco = imovel

    while True:
        print("\nInformações atuais do imóvel:")
        print(f"1. Título: {titulo}")
        print(f"2. Descrição: {descricao}")
        print(f"3. Preço: {preco}")
        print("4. Finalizar edição")
        
        opcao = input("Escolha o campo que deseja editar (1/2/3/4): ")

        if opcao == "1":
            novo_titulo = input("Digite o novo título (ou pressione Enter para manter): ")
            if novo_titulo.strip():
                titulo = novo_titulo.strip()
                print(f"✅ Título atualizado para: {titulo}")
        elif opcao == "2":
            nova_descricao = input("Digite a nova descrição (ou pressione Enter para manter): ")
            if nova_descricao.strip():
                descricao = nova_descricao.strip()
                print("✅ Descrição atualizada.")
        elif opcao == "3":
            novo_preco = input("Digite o novo preço (ou pressione Enter para manter): ")
            if novo_preco.strip():
                preco = novo_preco.strip()
                print(f"✅ Preço atualizado para: {preco}")
        elif opcao == "4":
            break
        else:
            print("⚠ Opção inválida! Tente novamente.")

    # Atualiza no banco
    c.execute("UPDATE imoveis SET titulo = ?, descricao = ?, preco = ? WHERE id = ?",
              (titulo, descricao, preco, imovel_id))
    conn.commit()
    print("\n✅ Imóvel atualizado com sucesso!")

conn.close()
