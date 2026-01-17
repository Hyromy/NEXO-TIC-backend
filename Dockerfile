FROM python:3.12-slim

RUN useradd --create-home --shell /bin/bash app

WORKDIR /home/app

COPY --chown=app:app requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

USER app

COPY --chown=app:app . .

EXPOSE 8000

CMD ["sh", "-c", "\
    set -o errexit && \
    python manage.py collectstatic --no-input --clear && \
    python manage.py migrate --no-input && \
    gunicorn project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --worker-class gthread \
        --threads 4 \
        --worker-tmp-dir /dev/shm \
        --timeout 120 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
"]
