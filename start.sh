#!/bin/bash
# ===========================================
# 🚀 Inicialização profissional do Flask com Gunicorn
# ===========================================

# Define o app principal (Flask)
export FLASK_APP=app.py

# Define ambiente de produção
export FLASK_ENV=production

# Garante que as variáveis .env sejam carregadas
set -a
source .env
set +a

# Executa com Gunicorn (servidor WSGI profissional)
# -w 4 → usa 4 workers (bons para apps leves)
# -b 0.0.0.0:$PORT → usa a porta do Render
# --timeout 120 → evita quedas em requisições longas
exec gunicorn -w 4 -b 0.0.0.0:$PORT app:app --timeout 120
