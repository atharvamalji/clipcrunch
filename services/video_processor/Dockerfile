# Use lightweight Python 3.12 Alpine image
FROM python:3.12-alpine

# Install ffmpeg and other minimal dependencies
RUN apk update && apk add --no-cache ffmpeg

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy chunker worker script
COPY processor.py .

# Command to run the chunker service
CMD ["python", "processor.py"]
