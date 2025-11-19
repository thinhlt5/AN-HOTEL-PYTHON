FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y python3-tk
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]   