# 1. Base Image: Official lightweight Python
FROM python:3.11-slim

# 2. Environment Variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# 3. Set Work Directory
WORKDIR /app

# 4. Install System Dependencies (if needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Code
COPY . .

# 7. Expose API Port
EXPOSE 8000

# 8. Start Command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]