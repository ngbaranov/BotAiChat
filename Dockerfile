# Лёгкая база
FROM python:3.12-slim

# Системные зависимости (включая tzdata для корректного времени)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

# Часовой пояс (по желанию можно переопределить в compose)
ENV TZ=Europe/Moscow \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создаём пользователя без root
RUN useradd -m appuser

WORKDIR /app

# Сначала зависимости — кэш слоёв будет работать эффективнее
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY . .

# Права
RUN chown -R appuser:appuser /app
USER appuser

# healthcheck на порт нам не нужен (long polling), сделаем простой python -m compileall
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -m compileall -q . || exit 1

# tini корректно обрабатывает сигналы (graceful shutdown)
ENTRYPOINT ["/usr/bin/tini", "--"]

# Запуск
CMD ["python", "main.py"]
