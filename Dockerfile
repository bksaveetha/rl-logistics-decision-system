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

# ================= EXPOSE PORT =================
EXPOSE 7860

# ================= ENV VARIABLES =================
ENV PYTHONUNBUFFERED=1

# ================= RUN APP =================
CMD bash -c "uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port=7860 --server.address=0.0.0.0"