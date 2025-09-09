# Use the latest version of Python 3.10 as the base image
FROM python:3.10-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive


# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && apt-get clean


# Install system dependencies required for Playwright and browsers
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libdbus-1-3 \
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxfixes3 \
    libexpat1 \
    libxext6 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# Install Playwright and set up its browser dependencies
RUN pip install playwright \
    && playwright install

# Install the dr-web-engine package
RUN pip install dr-web-engine

# Copy any local scripts or files (if needed) to the container
# COPY . /app

# Command to run the dr-web-engine (replace with your actual command if it differs)
ENTRYPOINT ["dr-web-engine"]