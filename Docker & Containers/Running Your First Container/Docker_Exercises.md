# Dockerfile Practice: Exercise 1

## Scenario

You have a small Python Flask app with this file structure:

```
myapp/
├── app.py
├── requirements.txt
```

`requirements.txt` contains:
```
flask==3.0.0
```

`app.py` runs a web server that listens on port 5000.

## Your Task

Write a Dockerfile for this app that meets ALL of the following requirements:

1. Uses `python:3.12-slim` as the base image
2. Sets `/app` as the working directory inside the container
3. Copies `requirements.txt` in first, installs dependencies, THEN copies the rest of the app code (for build caching reasons)
4. Installs the pip dependencies with `--no-cache-dir`
5. Documents that the container listens on port 5000
6. Creates and switches to a non-root user before running the app
7. Runs the app using exec form, as `python app.py`

## How to Practice

Write your Dockerfile below (or in your own editor), then it will be checked line by line against each of the 7 requirements above.

```dockerfile
# Write your Dockerfile here



```

## Self-Check Before Submitting

Before you submit your answer, ask yourself:

- [ ] Did I pick the right base image and tag?
- [ ] Is WORKDIR set before I try to COPY or RUN anything that depends on it?
- [ ] Did I copy `requirements.txt` separately from the rest of the code, in the right order?
- [ ] Did I use the `--no-cache-dir` flag on the pip install line?
- [ ] Did I add an EXPOSE line with the correct port?
- [ ] Did I create a non-root user and switch to it with USER, before the final CMD?
- [ ] Is my final CMD written in exec form (JSON array), not shell form?
