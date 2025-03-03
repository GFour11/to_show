FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONPATH=/app

COPY . .
RUN playwright install --with-deps

RUN chmod +x /app/entrypoint_london.sh /app/entrypoint_netherlands.sh

USER pwuser

CMD ["sh", "-c", "python $SCRIPT_PATH"]
