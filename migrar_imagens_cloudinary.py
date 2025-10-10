# ===========================================
# ☁️ MIGRAÇÃO AUTOMÁTICA DE IMAGENS PARA CLOUDINARY (com relatório)
# ===========================================
# Autor: Adilan (Celo Imóveis)
# Descrição:
#   - Envia automaticamente todas as imagens locais (static/uploads)
#     para o Cloudinary e atualiza o banco de dados SQLite.
#   - Gera um relatório com totais, sucessos e falhas.
# ===========================================

import os
import sqlite3
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# ===========================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ===========================================
load_dotenv()
DATABASE = "database.db"
UPLOAD_FOLDER = "static/uploads"

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# ===========================================
# 🧩 FUNÇÕES AUXILIARES
# ===========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def upload_image_to_cloudinary(file_path, folder="celoimoveis"):
    """Envia imagem para o Cloudinary e retorna a URL segura"""
    try:
        result = cloudinary.uploader.upload(file_path, folder=folder)
        return result["secure_url"]
    except Exception as e:
        print(f"❌ Erro ao enviar {file_path}: {e}")
        return None

# ===========================================
# 🚀 FUNÇÃO PRINCIPAL
# ===========================================
def migrar_imagens():
    print("\n📤 Iniciando migração de imagens para Cloudinary...\n")

    conn = get_db_connection()
    imoveis = conn.execute("SELECT id, fotos FROM imoveis").fetchall()

    total_imoveis = len(imoveis)
    total_fotos = 0
    ja_em_cloudinary = 0
    enviadas = 0
    falhas = 0

    for imovel in imoveis:
        if not imovel["fotos"]:
            continue

        fotos = [f.strip() for f in imovel["fotos"].split(",") if f.strip()]
        novas_fotos = []

        for foto in fotos:
            total_fotos += 1

            # Mantém URLs que já estão no Cloudinary
            if foto.startswith("http"):
                ja_em_cloudinary += 1
                novas_fotos.append(foto)
                continue

            local_path = os.path.join(UPLOAD_FOLDER, foto)
            if not os.path.exists(local_path):
                print(f"⚠️ Imagem não encontrada: {local_path}")
                falhas += 1
                continue

            print(f"⬆️ Enviando {foto} ...")
            url = upload_image_to_cloudinary(local_path)
            if url:
                enviadas += 1
                novas_fotos.append(url)
            else:
                falhas += 1
                novas_fotos.append(foto)

        # Atualiza banco
        conn.execute("UPDATE imoveis SET fotos=? WHERE id=?", (",".join(novas_fotos), imovel["id"]))
        conn.commit()

    conn.close()

    # ===========================================
    # 🧾 RELATÓRIO FINAL
    # ===========================================
    print("\n📊 RELATÓRIO DE MIGRAÇÃO")
    print("────────────────────────────────────")
    print(f"🏠 Imóveis processados: {total_imoveis}")
    print(f"🖼️ Total de fotos analisadas: {total_fotos}")
    print(f"☁️ Já no Cloudinary: {ja_em_cloudinary}")
    print(f"🚀 Enviadas agora: {enviadas}")
    print(f"⚠️ Falhas ou ausentes: {falhas}")
    print("────────────────────────────────────")
    print("\n🌎 Migração concluída com sucesso!\n")

# ===========================================
# ▶️ EXECUÇÃO
# ===========================================
if __name__ == "__main__":
    migrar_imagens()
