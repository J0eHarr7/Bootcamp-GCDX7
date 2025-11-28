FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 5000

# CRITICAL: multi-threaded / multi-worker server → RACE CONDITIONS
CMD ["gunicorn","--preload", "-w", "1", "--threads", "20", "-b", "0.0.0.0:5000", "app:app"]
