FROM python:3.10-slim

# Evita buffer nos logs do Python
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia apenas o requirements para instalar dependências primeiro (cache)
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Comando para rodar a aplicação
CMD ["python", "main.py"]
