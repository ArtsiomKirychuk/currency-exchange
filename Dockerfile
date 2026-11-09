FROM python:3.14
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
COPY tests ./tests
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]