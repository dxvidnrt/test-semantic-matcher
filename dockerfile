# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install Git and docker-compose
RUN apt-get update && apt-get install -y git && apt-get install -y docker-compose
#docker-compose needs to be installed (maybe in local subfolders?)

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
CMD ["python", "main/start_all.py"]

#Probably not needed when requirements are in test_cases
