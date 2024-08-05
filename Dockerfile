# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory to /app
RUN mkdir -p /index

# Copy file needed and setup work directory
COPY ./src /index
WORKDIR /index

# Install Pipenv
RUN pip install -U pipenv

# Install dependencies using Pipenv
RUN pipenv install --deploy

# Expose port 8080 for Gunicorn
EXPOSE 8080

# Run Gunicorn
CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:8080", "index:index"]