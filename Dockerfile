FROM python:3.12-slim

WORKDIR /app

# Installer uv (gestionnaire de paquets, identique à celui utilisé en local/CI)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copier uniquement les fichiers de dépendances d'abord (optimisation de cache Docker)
COPY pyproject.toml uv.lock ./

# Installer uniquement les dépendances de production (pas --dev)
RUN uv sync --frozen --no-dev

# Copier le reste du code applicatif nécessaire à l'exécution
COPY api/ ./api/
COPY src/ ./src/
COPY database/ ./database/
COPY models/ ./models/

# Render fournit dynamiquement le port via la variable d'environnement $PORT
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uv run --no-sync uvicorn api.main:app --host 0.0.0.0 --port $PORT"]