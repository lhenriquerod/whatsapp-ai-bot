# Use imagem oficial do Python
FROM python:3.10-slim

# Defina diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto
COPY . .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "main.py"]
