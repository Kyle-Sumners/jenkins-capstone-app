FROM python:3.14.7-slim

ENV FLASK_APP=app.py
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser
USER appuser
EXPOSE 5000
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]