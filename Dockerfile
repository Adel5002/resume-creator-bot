FROM python:3.12-slim


# Create app workspace
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    wget gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 fonts-liberation libu2f-udev xdg-utils

# Install Playwright + Chromium
RUN pip install --upgrade pip
RUN pip install playwright
RUN playwright install chromium

# Copy project
COPY . .

# Install project dependencies from pyproject.toml
RUN pip install -e .
