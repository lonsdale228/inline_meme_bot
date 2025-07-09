FROM python:3.12.9-slim

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ffmpeg ca-certificates \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY .  /app

CMD ["python", "main.py"]