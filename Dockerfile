# Use an official Python runtime as a base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the .env file is present inside the container
COPY .env /app/.env

# Expose the port Django runs on
EXPOSE 8000

# Define the command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
