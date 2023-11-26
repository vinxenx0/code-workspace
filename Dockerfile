# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install python3-venv and create a virtual environment
RUN apt-get update && \
    apt-get install -y python3-venv && \
    python3 -m venv .venv && \
    chmod +x .venv/bin/activate

# Activate the virtual environment and install required packages
RUN /app/.venv/bin/python -m pip install --upgrade pip
RUN /app/.venv/bin/pip install -r requeriments.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=run.py

# Run app.py when the container launches
CMD ["/app/.venv/bin/flask", "run", "--host=0.0.0.0"]