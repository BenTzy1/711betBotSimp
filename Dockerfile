# Use the official Python image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the contents of the current directory to the working directory in the container
COPY . /app/

# Install Nixpacks dependencies and activate virtual environment
RUN python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install nixpacks && nix-env -if .nixpacks/nixpkgs-5148520bfab61f99fd25fb9ff7bfbb50dad3c9db.nix && nix-collect-garbage -d

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose any necessary ports (if your application requires it)
# EXPOSE <port_number>

# Command to run the application
CMD ["python", "main.py"]
