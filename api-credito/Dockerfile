FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apk add --no-cache \
    gcc musl-dev postgresql-dev libffi-dev openssl-dev curl tzdata && \
    cp /usr/share/zoneinfo/America/Fortaleza /etc/localtime && \
    echo "America/Fortaleza" > /etc/timezone && \
    apk del tzdata

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]