FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH="/app"

COPY requirements.txt  .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY templates ./templates
COPY static ./static

COPY web_server.py .
COPY movie_finder.py .
# COPY .env .

# Run the client
CMD ["gunicorn", "-w", "4", "web_server:app", "-b", "0.0.0.0:5321"]
