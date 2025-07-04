# Usa imagem oficial do Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Expõe a porta padrão do Flask
EXPOSE 10000

# Executa o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
