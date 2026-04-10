# ================= BASE IMAGE =================
FROM python:3.11-slim

# ================= WORKDIR =================
WORKDIR /app

# ================= SYSTEM DEPENDENCIES =================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ================= COPY FILES =================
COPY . /app

# ================= INSTALL PYTHON DEPENDENCIES =================
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install uv
RUN uv sync

# ================= EXPOSE PORT =================
EXPOSE 7860

# ================= ENV VARIABLES =================
ENV PYTHONUNBUFFERED=1

# ================= RUN APP =================
MD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]