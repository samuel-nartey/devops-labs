Exercise 1: Dockerize a simple Python app

The scenario:
You have a small Python Flask app with this structure:

myapp/
├── app.py
├── requirements.txt

requirements.txt contains:

flask==3.0.0

app.py runs a web server that listens on port 5000.

Your task: write a Dockerfile that meets ALL of these requirements:

Uses python:3.12-slim as the base image
Sets /app as the working directory inside the container
Copies requirements.txt in first, installs dependencies, THEN copies the rest of the app code (for caching reasons — you know why now)
Installs the pip dependencies with --no-cache-dir
Documents that the container listens on port 5000
Creates and switches to a non-root user before running the app
Runs the app using exec form, as python app.py
