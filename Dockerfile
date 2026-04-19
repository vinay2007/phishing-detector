# Use Python 3.11 Slim as the base image
FROM python:3.11-slim

# Step 1: Install system dependencies for Playwright (Headless Browsers)
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Step 2: Set the working directory
WORKDIR /app

# Step 3: Copy requirements and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Install Playwright browsers (Specifically Chromium)
RUN playwright install chromium
RUN playwright install-deps chromium

# Step 5: Copy all project files to the container
COPY . .

# Step 6: Create necessary folders for models and data
RUN mkdir -p models/hf_pretrained data

# Step 7: Expose port 7860 (The standard port for Hugging Face Spaces)
EXPOSE 7860

# Step 8: Launch the API
# We use uvicorn to run our api.py:app
CMD ["python", "api.py"]
