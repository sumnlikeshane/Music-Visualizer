# Use Python 3.12 slim as the base image
FROM python:3.12-slim

# Install required dependencies (including libGL)
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set the environment variable to specify the Flask app
ENV FLASK_APP=app.py

# Expose the port that the app will run on
EXPOSE 8080

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
