# Use Ubuntu 18.04 as the base image
FROM ubuntu:18.04

# Set environment variables for non-interactive apt-get
ENV DEBIAN_FRONTEND=non-interactive

# Install necessary packages and dependencies
RUN apt-get update && \
    apt-get install -y wget tar \
    && apt-get install -y \
        firefox \
        xvfb \
        libgtk-3-0 \
        libdbus-glib-1-2 \
        libxt6 \
        libxrender1 \
        libxrandr2 \
        libxss1 \
        libasound2 \
        && apt-get clean


# Set Java version and download URL
ENV JAVA_VERSION=8u211
ENV JAVA_HOME=/usr/local/java/jdk1.8.0_211

# Copy the JDK tar.gz file into the image
COPY jdk-8u211-linux-x64.tar.gz /tmp/

# Install JDK
RUN mkdir -p /usr/local/java && \
    tar -xzf /tmp/jdk-8u211-linux-x64.tar.gz -C /usr/local/java/ && \
    ln -s /usr/local/java/jdk1.8.0_211 /usr/local/java/jdk && \
    rm /tmp/jdk-8u211-linux-x64.tar.gz

# Set JAVA_HOME and update PATH
ENV PATH="$JAVA_HOME/bin:$PATH"

# Create the /app working directory and bin subdirectory
RUN mkdir -p /app/bin

# Copy the oxpath-cli.jar file into the bin directory
COPY oxpath-cli.jar /bin/

# Set the working directory
WORKDIR /app

# Set the entry point to run the jar file
ENTRYPOINT ["java", "-jar", "/bin/oxpath-cli.jar"]