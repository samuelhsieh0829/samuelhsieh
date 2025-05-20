# Use a Python base image
FROM python:3.11.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
# RUN apt-get update && \ 
#     apt-get install -y ffmpeg gcc portaudio19-dev && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Copy bot files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the bot
CMD ["python", "main.py"]