# Use the official Python image from the Docker Hub
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

#Install Git
RUN apt-get update && apt-get install -y git

#upgrade PIP
RUN pip install --upgrade pip

#Clone git repository
RUN git clone https://github.com/martingogeissl/QDATA-2024-reproduction.git

#Install dependencies
ADD  requirements.txt app/

# Install the dependencies specified in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
