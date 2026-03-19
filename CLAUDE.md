# Enigma

Simulateur de machine Enigma. Stack : FastAPI + Jinja2 + TailwindCSS CDN + Alpine.js.

## Dev local

```bash
ENV=dev uvicorn main:app --reload --port 8008 --app-dir app/backend
```

## Structure

- `app/backend/enigma_core.py` : logique Enigma pure Python (rotors, plugboard, reflecteur)
- `app/backend/routers/api.py` : API JSON (encrypt-letter, encrypt-text, configurations)
- `app/backend/routers/pages.py` : pages HTML
- `app/backend/templates/` : Jinja2 (base.html + index.html + components/)
- `app/backend/static/` : CSS skeuomorphe + JS Alpine.js

## Port

8008 (dev et prod)

## Architecture

- **Stateless** : le client envoie la config complète à chaque requête
- **enigma_core.py** est pur Python, pas de dépendances externes
- Le signal_path retourné par l'API permet la visualisation du trajet du signal
- Base de données SQLite pour sauvegarder les configurations utilisateur
