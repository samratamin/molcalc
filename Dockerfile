# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y git make libxrender-dev && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Makefile and scripts, and run the setup targets
COPY Makefile .
COPY scripts/ scripts/
RUN make ppqm
RUN make setup_assets

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 6543

# Define the command to run the application
CMD ["python", "wsgi.py"]
