# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install Git
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV NAME World

# Expose the port that FastAPI will run on
EXPOSE 8100

# Run service.py when the container launches
CMD ["python", "test/service.py"]
