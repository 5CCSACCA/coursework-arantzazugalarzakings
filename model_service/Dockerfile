# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Suppress tokenizer parallelism warning
ENV TOKENIZERS_PARALLELISM=false

# Copy all application files
COPY . /app

# Expose the service port
EXPOSE 8000

# Set the default command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
