Markdown
#  Docker, GitHub & DevSecOps: Beginner Hands-On Lab

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/<your-username>/<your-repo>/docker-build-push.yml?branch=main&style=flat-square&label=Build%2C%20Scan%2C%20Push)](https://github.com/<your-username>/<your-repo>/actions)
![Docker Pulls](https://img.shields.io/docker/pulls/<your-dockerhub-username>/my-web-app?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

> A complete, copy‑paste‑ready walkthrough for learning Docker, Docker Hub, and DevSecOps automation with GitHub Actions. 
> **Read everything!** Each command, flag, and line of code is explained – you will understand *why*, not just *how*.

---

##  Overview

In this lab you will:

- Pull and inspect a public container image from Docker Hub
- Build your own web application (Flask + HTML + JSON health endpoint)
- Write a secure, production‑grade `Dockerfile`
- Push your image to Docker Hub, then pull and run it anywhere
- Share your image so that classmates can run it on their machines
- Automate the whole workflow with a **security‑first** GitHub Actions pipeline (scanning with Trivy, smoke testing)

Everything is designed for **entry‑level DevSecOps** learners. You will work exactly like a real‑world team: generating access tokens, tagging images with personal identifiers, scanning for vulnerabilities, and verifying builds.

---

## 📑 Table of Contents

1. [Prerequisites & Toolbox](#-prerequisites--toolbox)
2. [Generating a Docker Hub Access Token](#-generating-a-docker-hub-access-token)
3. [Phase 0 – Pull and Inspect a Public Container](#-phase-0--pull-and-inspect-a-public-container)
4. [Phase 1 – Build, Push, Pull & Share Your Own Image](#-phase-1--build-push-pull--share-your-own-image)
   - [1. Create the Web Application](#1-create-the-web-application)
   - [2. Write a Secure Dockerfile](#2-write-a-secure-dockerfile)
   - [3. Build & Test Locally](#3-build--test-locally)
   - [4. Push to Docker Hub](#4-push-to-docker-hub)
   - [5. Pull Your Own Image](#5-pull-your-own-image)
   - [6. Share with Others](#6-share-with-others)
5. [Phase 2 – Automate with a DevSecOps Pipeline (GitHub Actions)](#-phase-2--automate-with-a-devsecops-pipeline-github-actions)
   - [1. Set Up Your GitHub Repository](#1-set-up-your-github-repository)
   - [2. Add Secrets to GitHub](#2-add-secrets-to-github)
   - [3. The Workflow File](#3-the-workflow-file)
   - [4. Trigger the Pipeline](#4-trigger-the-pipeline)
   - [5. Pull the Automatically Built Image](#5-pull-the-automatically-built-image)
6. [Clean Up](#-clean-up)
7. [Final Reflections](#-final-reflections)
8. [Contributing / License](#-contributing--license)

---

##  Prerequisites & Toolbox

Verify you have all tools installed. The table includes a quick check command and links if you need to install.

| Tool | Check version | Install help |
|------|---------------|--------------|
| Git | `git --version` | [git-scm.com](https://git-scm.com/) |
| Docker | `docker --version` | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| GitHub account | login at github.com | [github.com](https://github.com) |
| Docker Hub account | login at hub.docker.com | [hub.docker.com](https://hub.docker.com) – sign up if needed |
| Code editor | – | [VS Code](https://code.visualstudio.com/) recommended |

The only missing piece is your **Docker Hub personal access token**. You’ll generate it in the next step.

---

##  Generating a Docker Hub Access Token

1. Open [hub.docker.com](https://hub.docker.com) and log in.
2. Click your avatar → **Account Settings** → **Security** → **New Access Token**.
3. Give it a description: `lab-token`.
4. Select **Read & Write** permissions (necessary for pushing images).
5. Click **Generate** and **copy the token immediately**. You won’t see it again!

<details>
<summary> Why an access token instead of your password?</summary>
Tokens can be scoped to specific permissions, rotated independently, and revoked without changing your main password. If a token leaks, the impact is limited. This is a fundamental supply‑chain security practice.
</details>

Store the token safely – you’ll use it for `docker login` and later as a GitHub secret.

---

##  Phase 0 – Pull and Inspect a Public Container

You’ll first act as a consumer: pull an existing Nginx image, run it, and access it in your browser.  
*Every command, flag, and argument is explained.*

```bash
# ==============================================
# docker pull <image>:<tag>
# Downloads the image layers from Docker Hub.
# 'nginx' is the repository, 'alpine' is a lightweight variant.
# ==============================================
docker pull nginx:alpine

# ==============================================
# docker run -d -p 8080:80 --name my-nginx nginx:alpine
# -d          → Detached mode – run container in background.
# -p 8080:80  → Publish port: map host port 8080 to container port 80 (host:container).
# --name my-nginx → Give the container a custom name for easier management.
# nginx:alpine → The image we want to instantiate.
# ==============================================
docker run -d -p 8080:80 --name my-nginx nginx:alpine

# List running containers
docker ps

# View the logs (stdout/stderr) of your container
docker logs my-nginx

# ==============================================
# docker rm -f my-nginx
# -f  → Force remove: stops the container if running before deleting it.
# ==============================================
docker rm -f my-nginx
Open your browser to http://localhost:8080 – you should see the Nginx welcome page.

<details> <summary> Observation: What just happened?</summary> You downloaded a ready‑made filesystem (an image) that someone else built and published. The `run` command created an isolated process (a container) from that image. Port mapping made it reachable from your browser. This is the fundamental “pull → run” flow you’ll repeat with your own image. </details>
 Phase 1 – Build, Push, Pull & Share Your Own Image
Now you’ll become the image creator and share your work with classmates.

1. Create the Web Application
Create a new project folder and add the following files.
The code is deliberately heavily commented so that every line makes sense.

app.py

python
# Import necessary modules.
# Flask: the web framework.
# render_template: sends HTML files.
# jsonify: converts Python dictionaries to JSON responses.
# os: reads environment variables.
# datetime: provides current UTC time.
from flask import Flask, render_template, jsonify
import os, datetime

# Create the Flask application instance.
app = Flask(__name__)

# Read the APP_NODE environment variable; default to 'developer'.
# This separates configuration from code (12‑factor app principle).
APP_NODE = os.environ.get("APP_NODE", "developer")

# Home page route.
# The 'node' value is passed into the HTML template and replaced by Jinja2.
@app.route("/")
def home():
    return render_template("index.html", node=APP_NODE)

# Health check endpoint – used by orchestrators (Docker HEALTHCHECK, Kubernetes probes).
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",                   # Simple status string.
        "node": APP_NODE,                      # Identifies the responding instance.
        "time": datetime.datetime.utcnow().isoformat() + "Z"  # UTC timestamp.
    })

# Only start the development server when the script is run directly.
# host='0.0.0.0' makes Flask listen on all network interfaces inside the container.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
templates/index.html

html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome</title>
</head>
<!-- Inline styles for a clean look. -->
<body style="font-family: sans-serif; text-align: center; padding-top: 5rem;">
    <!-- Jinja2 template syntax: {{ node }} will be replaced with the value from Flask. -->
    <h1>Hello from <span style="color: #2b6cb0;">{{ node }}</span></h1>
    <p>This container is alive and running!</p>
</body>
</html>
requirements.txt

text
# Pin Flask version 3.0.0 for reproducible builds.
flask==3.0.0
<details> <summary> Why use an environment variable for the node name?</summary> It externalises configuration. In production you could inject the pod name, hostname, or any identifier without rebuilding the image. This is a basic but crucial practice for portable containers. </details>
2. Write a Secure Dockerfile
Create a file named Dockerfile (no extension). Read the comments – they explain every instruction.

dockerfile
# ---- Minimal, secure production image ----
# Base image: official Python 3.11, slim variant (smaller attack surface).
FROM python:3.11-slim

# LABEL instructions: key=value metadata for documentation and tooling.
LABEL maintainer="your-name@example.com"
LABEL version="1.0.0"
LABEL description="Simple Flask web app for Docker/GitHub Actions lab"

# Create a non‑root system group and user.
# groupadd -r creates a system group. useradd -r creates a system user.
# Running as non-root limits damage if the application is compromised.
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory – all following commands will run inside /app.
WORKDIR /app

# Copy ONLY the requirements file first. This optimises build caching:
# If requirements.txt hasn’t changed, the pip install layer will be reused.
COPY requirements.txt .

# Install Python dependencies.
# --no-cache-dir: don’t store downloaded packages (reduces image size).
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image.
# The '.' means the whole build context (current directory).
COPY . .

# Change ownership of the application directory to the non‑root user.
# This allows the app to write logs/temp files inside the container.
RUN chown -R appuser:appuser /app

# Switch to the non‑root user for all subsequent instructions.
# This applies to CMD as well, so the process runs with limited privileges.
USER appuser

# Document that the container listens on port 5000 (informational, not a port mapping).
EXPOSE 5000

# HEALTHCHECK instruction: tells Docker how to check if the container is still alive.
# --interval=30s   Check every 30 seconds.
# --timeout=3s     The check must finish within 3 seconds.
# --start-period=5s  Wait 5 seconds before starting checks (Flask needs time to start).
# --retries=3      If 3 consecutive checks fail, mark container unhealthy.
# The CMD uses curl to call the /health endpoint; exit 1 on failure.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Default command to run when the container starts.
# The exec form ["python", "app.py"] runs the process directly (no shell),
# which means Unix signals (SIGTERM, SIGKILL) are forwarded correctly.
CMD ["python", "app.py"]
.dockerignore (prevent unwanted files from entering the image)

text
__pycache__
*.pyc
*.pyo
.git
.env
*.md
Dockerfile
.dockerignore
<details> <summary>🛡️Why a non‑root user?</summary> If an attacker compromises the application running as root, they might break out of the container to the host. A non‑root user respects the principle of least privilege. It’s a mandatory security hardening requirement in many organisations. </details><details> <summary>⚡ Why copy requirements.txt first, then install, then copy the rest?</summary> Docker caches each layer. If `requirements.txt` hasn’t changed, the `pip install` layer is reused, dramatically speeding up builds. Code changes alone won’t invalidate the dependency cache. This ordering is a fundamental optimisation for CI pipelines. </details>
3. Build & Test Locally
Run these commands in your project folder.

bash
# ==============================================
# docker build -t my-web-app .
# -t my-web-app  → Tag the resulting image with the name 'my-web-app'.
# The final '.' is the build context – the directory we send to the Docker daemon.
# ==============================================
docker build -t my-web-app .

# ==============================================
# docker run -d -p 5000:5000 --name webapp-test my-web-app
# -d              → Detached mode (background).
# -p 5000:5000    → Map host port 5000 to container port 5000.
# --name webapp-test → Name our container so we can easily refer to it.
# my-web-app     → The image we built.
# ==============================================
docker run -d -p 5000:5000 --name webapp-test my-web-app
Visit http://localhost:5000 and http://localhost:5000/health in your browser.
Stop and remove the container when finished:

bash
docker rm -f webapp-test
4. Push to Docker Hub
Authenticate with the access token, tag your image, and push it.
Replace your-dockerhub-username with your actual username.

bash
# Log in: the -u flag specifies the username.
# The command will prompt for a password – paste your access token (not your Docker Hub password).
docker login -u your-dockerhub-username

# ==============================================
# docker tag my-web-app your-dockerhub-username/my-web-app:v1.0.0-john
# This does NOT create a new image; it adds a new tag (an alias) to the same image ID.
# The format is: <local-image> <remote-repository>:<tag>
# The convention <version>-<yourname> makes images personally traceable.
# ==============================================
docker tag my-web-app your-dockerhub-username/my-web-app:v1.0.0-john

# Push the tagged image to Docker Hub.
# This uploads all layers that aren’t already present in the registry.
docker push your-dockerhub-username/my-web-app:v1.0.0-john
<details> <summary> Why do we need to tag before pushing?</summary> The tag tells Docker the full remote address: `docker.io/your-dockerhub-username/my-web-app:v1.0.0-john`. Without it, Docker wouldn’t know where to store the image. </details>
5. Pull Your Own Image
Now act as a new user who doesn’t have the image locally. Delete your local copy, pull from Docker Hub, and run it.

bash
# Remove the local image (if it exists – ignore errors).
docker rmi your-dockerhub-username/my-web-app:v1.0.0-john

# Pull the image – downloads all layers from the registry.
docker pull your-dockerhub-username/my-web-app:v1.0.0-john

# Run a container from the freshly pulled image, mapping port 5000.
docker run -d -p 5000:5000 --name pulled-app your-dockerhub-username/my-web-app:v1.0.0-john
Test the endpoints again to confirm the image works identically to your local build.

6. Share with Others
Make sure your Docker Hub repository is public (you can change visibility on the web interface if needed).
Share your image tag (e.g. your-dockerhub-username/my-web-app:v1.0.0-john) with classmates.
They can run:

bash
docker pull your-dockerhub-username/my-web-app:v1.0.0-john
docker run -d -p 5000:5000 your-dockerhub-username/my-web-app:v1.0.0-john
They will see your personalised greeting and health endpoint – this simulates a real‑world scenario where teams share containerised services via a registry.

<details> <summary> What if the repository is private and a classmate tries to pull?</summary> Docker Hub will reject the request with an authentication error because anonymous pulls are only allowed for public repositories. In a corporate environment you would use a private registry with appropriate access controls. </details>

 Phase 2 – Automate with a DevSecOps Pipeline (GitHub Actions)
You will now build a CI/CD workflow that runs on every push to main. It will:

Build the image

Scan it for vulnerabilities (Trivy)

Push it to Docker Hub only if the scan passes

Pull the image and run a smoke test to verify it works

1. Set Up Your GitHub Repository
Initialise git, connect to GitHub, and push your code.

bash
git init                         # Create a new Git repository
git add .                        # Stage all files
git commit -m "Initial commit: Flask app, Dockerfile, and workflow"  # First commit
git branch -M main               # Rename default branch to 'main'
git remote add origin https://github.com/your-github-username/your-repo.git  # Link to remote
git push -u origin main          # Push code; -u sets upstream tracking
2. Add Secrets to GitHub
Secrets are encrypted environment variables used in workflows. Never hard‑code credentials.

On your GitHub repository page, go to Settings → Secrets and variables → Actions.

Click New repository secret.

Add two secrets:

DOCKERHUB_USERNAME – your Docker Hub username.

DOCKERHUB_TOKEN – the access token you generated earlier.

The workflow will reference them as ${{ secrets.DOCKERHUB_USERNAME }} and ${{ secrets.DOCKERHUB_TOKEN }}.

3. The Workflow File
Create .github/workflows/docker-build-push.yml with the following content.
The YAML file is annotated line‑by‑line – read every comment.

yaml
# The name of the workflow that appears in the GitHub Actions UI.
name: Build, Scan, Push and Verify Docker Image

# --- Triggers ---
# This workflow runs on pushes to the main branch and on pull requests targeting main.
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

# Environment variables that are available to all jobs below.
env:
  DOCKER_HUB_USER: ${{ secrets.DOCKERHUB_USERNAME }}   # From GitHub secrets
  IMAGE_NAME: my-web-app
  TAG_SUFFIX: john                                      # ← CHANGE THIS TO YOUR NAME/ID

jobs:
  # The job identifier (can be any string) – it will create a single job on the runner.
  build-scan-push-verify:
    runs-on: ubuntu-latest                              # Use the latest Ubuntu runner

    steps:
      # Step 1: Checkout the repository so the runner has access to the code.
      - name: Checkout repository
        uses: actions/checkout@v4                        # Official checkout action

      # Step 2: Log in to Docker Hub using the stored secrets.
      - name: Log in to Docker Hub
        uses: docker/login-action@v3                     # Pre‑built action for Docker login
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Step 3: Build the image and load it into the local Docker daemon (no push yet).
      - name: Build Docker image (load locally, do not push yet)
        uses: docker/build-push-action@v5                # Official build‑push action
        with:
          context: .                                     # Build context is current dir
          load: true                                     # Load image into local Docker daemon (needed for scanning)
          push: false                                    # Do NOT push to registry now
          tags: |                                        # Multiline: supply two tags
            ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:v1.0.0-${{ env.TAG_SUFFIX }}
            ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:latest

      # Step 4: Scan the local image for vulnerabilities with Trivy.
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@0.20.0           # Official Trivy action
        with:
          image-ref: "${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:v1.0.0-${{ env.TAG_SUFFIX }}"
          format: 'table'                                # Human‑readable table in logs
          exit-code: '1'                                 # Fail the step if any vulnerabilities are found
          ignore-unfixed: true                           # Only alert if a fix is NOT available
          severity: 'HIGH,CRITICAL'                      # Only fail on these levels

      # Step 5: Push the image to Docker Hub, but only if the previous step passed.
      # The if condition ensures we never push a vulnerable image.
      - name: Push Docker image to Hub
        if: success()                                    # Only run if all previous steps succeeded
        run: |
          docker push ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:v1.0.0-${{ env.TAG_SUFFIX }}
          docker push ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:latest

      # Step 6: Pull the uploaded image and run a smoke test to verify it works.
      - name: Pull image and run smoke tests
        if: success(
        run: |
          echo "Pulling image..."
          docker pull ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:v1.0.0-${{ env.TAG_SUFFIX }}

          echo "Starting test container..."
          docker run -d -p 5000:5000 --name verify-container \
            ${{ env.DOCKER_HUB_USER }}/${{ env.IMAGE_NAME }}:v1.0.0-${{ env.TAG_SUFFIX }}

          # Give Flask a few seconds to start.
          sleep 

          # Test the /health endpoint. curl -f fails on HTTP errors.
          echo "Testing /health endpoint..."
          curl -f http://localhost:5000/health || (echo "Health check failed!" && exit 1)

          # Test the home page – ensure it contains the word 'hello' (case‑insensitive).
          echo "Testing / endpoint..."
          curl -s http://localhost:5000/ | grep -i "hello" || (echo "Home page missing greeting!" && exit 1)

          echAl smoke tests passed"

      # Step 7: Clean up the test container, whether earlier steps passed or failed.
      # if: always() ensures it runs even if the smoke tests fail.
      - name: Remove test container
        if: always()
        run: docker rm -f verify-container || true       # '|| true' prevents step failure if container doesn't exist
4. Trigger the Pipeline
Commit and push the workflow file to main:

bash
git add .github/workflows/docker-build-push.yml
git commit -m "Add DevSecOps CI pipeline"
git push
Go to your repository’s Actions tab. You’ll see the workflow running.
Click on it to watch each step. If Trivy reports a HIGH/CRITICAL vulnerability, the job will fail – that’s intentional. You would then update your base image or dependencies and push again.

5. Pull the Automatically Built Image
After a successful pipeline run, you and your classmates can pull the exact image produced by the CI system:

bash
docker pull your-dockerhub-username/my-web-app:v1.0.0-john
docker run -d -p 5000:5000 your-dockerhub-username/my-web-app:v1.0.0-john
It should behave exactly like your manual build – now you have an automated, security‑gated supply chain.

 Clean Up
Remove all images and containers created during the lab:

bash
# Force remove all running and stopped containers.
# docker ps -aq lists all container IDs; 2>/dev/null suppresses “no containers” errors.
docker rm -f $(docker ps -aq) 2>/dev/null

# Remove the lab images (forcefully, ignore errors if they don’t exist).
docker rmi my-web-app your-dockerhub-username/my-web-app:v1.0.0-john nginx:alpine 2>/dev/null
 Final Reflections
Work through these questions after the hands‑on part. Click to reveal answers.

What is the difference between a container image and a running container?

<details> <summary>Answer</summary> An image is a read‑only template with all the filesystem layers and metadata. A container is a running instance of that image with an additional writable layer and an isolated process. </details>
Why did we include a .dockerignore? Give a concrete example of what could go wrong without it.

<details> <summary>Answer</summary> `.dockerignore` prevents unnecessary or sensitive files from being copied into the image. Without it, you might accidentally include your entire `.git` directory, local `.env` files containing secrets, or editor artifacts – inflating image size and potentially exposing credentials. </details>
In the GitHub Actions workflow, why if: success() on the push step and if: always() on the cleanup step?

<details> <summary>Answer</summary> `success()` ensures we never push an image that hasn’t passed all previous steps, especially the vulnerability scan. `always()` guarantees the test container is cleaned up even if smoke tests fail, preventing leftover processes on the runner. </details>
If you wanted to deploy this image to Kubernetes, what additional pipeline steps would you add?
(Open discussion – talk with your trainer.)

How could you further secure the supply chain of this image?

<details> <summary>Answer</summary> Sign the image with Cosign, pin base image digests instead of tags, generate a Software Bill of Materials (SBOM), and verify signatures at deployment time. These practices provide integrity guarantees and are increasingly required in regulated industries. </details>
 Contributing / License
This project is intended for learning. Feel free to fork, extend, and share.
Licensed under MIT – see LICENSE for details
https://img.shields.io/badge/Lab%2520completed:-Manual%2520build%E2%86%92Push%E2%86%92Pull%E2%86%92Automation-blue?style=flat-square

Happy DevSecOps learning!
