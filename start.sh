#!/bin/bash
export FLASK_APP=app.py        # Diz qual arquivo é o Flask principal
export FLASK_ENV=production    # Define que é modo produção
flask run --host=0.0.0.0 --port=$PORT  # Roda o servidor Flask no Render
