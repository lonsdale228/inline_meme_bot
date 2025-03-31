FROM python:3.12.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /bot/requirements.txt

COPY .  /app

CMD ["python", "main.py"]