# Full Python image with standard library
FROM python:3.13-slim

# Install system packages (needed for full stdlib)
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-venv \
    python3-lib2to3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start the bot
CMD ["python", "bot.py"]
