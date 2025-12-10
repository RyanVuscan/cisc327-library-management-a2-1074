# Initiliaze lightweight python
FROM python:3.11-slim

# Set working dir.
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py


# Installing required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code over
COPY . .

# Run on port 5000
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]