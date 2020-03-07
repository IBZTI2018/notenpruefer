FROM python:3.8-alpine3.10

# Update apk repo
RUN echo "https://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "https://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

# Install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

# Upgrade pip
RUN pip install --upgrade pip

# Install selenium
RUN pip install selenium

# Create a folder for our project
RUN mkdir -p /app && \
    mkdir -p /shared
WORKDIR /app

# Copy our crawler inside /app
COPY crawler.py /app 

# Run our docker-python-selenium script
ENTRYPOINT python3 crawler.py
