# Use the latest version of Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && apt-get clean

# Install Playwright and set up its browser dependencies
RUN pip install playwright \
    && playwright install

# Install the dr-web-engine package
RUN pip install dr-web-engine

# Copy any local scripts or files (if needed) to the container
# COPY . /app

# Command to run the dr-web-engine (replace with your actual command if it differs)
CMD ["dr-web-engine"]