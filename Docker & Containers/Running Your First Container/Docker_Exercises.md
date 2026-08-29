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
# Write your Dockerfile .........



```

## Self-Check Before Submitting or making it yourself

Before you submit your answer, ask yourself:

- [ ] Did I pick the right base image and tag?
- [ ] Is WORKDIR set before I try to COPY or RUN anything that depends on it?
- [ ] Did I copy `requirements.txt` separately from the rest of the code, in the right order?
- [ ] Did I use the `--no-cache-dir` flag on the pip install line?
- [ ] Did I add an EXPOSE line with the correct port?
- [ ] Did I create a non-root user and switch to it with USER, before the final CMD?
- [ ] Is my final CMD written in exec form (JSON array), not shell form?



# Dockerfile Practice: Exercise 1b

## What This Exercise Covers

Same difficulty level as Exercise 1. Different language, same core concepts, to help them stick: WORKDIR, copy-order caching, dependency install flags, EXPOSE, non-root USER, exec form CMD.

## Scenario

You have a small Node.js app with this file structure:

```
myapp/
├── server.js
├── package.json
```

`package.json` contains a couple of dependencies (like `express`).

`server.js` runs a web server that listens on port 3000.

## Your Task

Write a Dockerfile that meets ALL of the following requirements:

1. Uses `node:20-slim` as the base image
2. Sets `/app` as the working directory inside the container
3. Copies `package.json` in first, installs dependencies, THEN copies the rest of the app code (for caching reasons)
4. Installs the npm dependencies using `npm install --omit=dev` (skips dev-only dependencies, keeping the image leaner)
5. Documents that the container listens on port 3000
6. Creates a non-root user, gives it ownership of the app files, and switches to it before running the app
7. Runs the app using exec form, as `node server.js`

## How to Practice

Write your Dockerfile.Marked out of 100 against each requirement, same as before.

```dockerfile
# Write your Dockerfile 



```

## Self-Check Before Submitting or marking it yourself

- [ ] Did I pick the right base image and tag?
- [ ] Is WORKDIR set before I try to COPY or RUN anything that depends on it?
- [ ] Did I copy `package.json` separately from the rest of the code, in the right order?
- [ ] Did I use `--omit=dev` on the npm install line?
- [ ] Did I add an EXPOSE line with the correct port?
- [ ] Did I create the non-root user BEFORE referencing it in any `--chown`, and BEFORE the final `USER` instruction?
- [ ] Are the copied files actually owned by the non-root user, not root?
- [ ] Is my final CMD written in exec form (JSON array), not shell form?
