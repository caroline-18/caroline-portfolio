FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=dummy-secret-key-for-build python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "ai_skincare_dupe_finder.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]