
FROM python:3.9

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere requirements.txt und installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere alle anderen Dateien
COPY . .

# Exponiere Port 8080
EXPOSE 8080

# Setze Umgebungsvariablen für Flask
ENV FLASK_APP=app.py
ENV PORT=8080

# Starte Gunicorn-Server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]
