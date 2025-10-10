#!/bin/bash
# ===========================================
# 🚀 Inicialização do Celo Imóveis (Render)
# Usa Gunicorn como servidor de produção
# ===========================================

# Define o app principal do Flask
export FLASK_APP=app.py
export FLASK_ENV=production

# Executa o Gunicorn (Render define automaticamente $PORT)
exec gunicorn -w 4 -b 0.0.0.0:$PORT app:app

