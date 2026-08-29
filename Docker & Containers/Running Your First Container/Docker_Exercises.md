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


# Dockerfile Practice: Exercise 2

## What This Exercise Covers

This one is heavier than Exercise 1. It specifically tests:

- Multi-stage builds
- Build cache ordering (so you don't waste time re-running slow steps)
- Cache invalidation pitfalls (the `apt-get update` trap)
- Reducing final image size (cleaning up build-only tools, avoiding leftover cache files)

No skipping steps this time. Every requirement below maps to one of these concepts.

---

## Scenario

You have a Python app that depends on a package which needs to be **compiled from source** during installation (this happens in real life, some Python packages have C extensions). To compile it, pip needs a C compiler and some build headers, which come from installing `gcc` and `python3-dev` via `apt-get`.

Once the package is installed, though, your app does NOT need `gcc` or `python3-dev` to actually *run*. Those tools were only needed during the build.

File structure:
```
myapp/
├── app.py
├── requirements.txt
```

`requirements.txt`:
```
some-compiled-package==2.1.0
flask==3.0.0
```

## Your Task

Write a Dockerfile that meets ALL of the following requirements. Read them carefully, several of them test specific concepts on purpose.

1. **Base image:** use `python:3.12-slim` for BOTH stages.

2. **Multi-stage build, two stages:**
   - Stage 1, named `builder`: has everything needed to install the Python dependencies, including the C compiler.
   - Stage 2, the final stage: only contains what's needed to *run* the app. No compiler, no build tools, no leftover apt cache.

3. **In the `builder` stage:**
   - Install `gcc` and `python3-dev` using `apt-get`, in a way that does not leave stale package list files bloating that layer.
   - Update and install in the SAME `RUN` instruction (avoid the cache invalidation trap where `apt-get update` gets cached separately from the install).
   - Install the Python dependencies from `requirements.txt` using `pip install --no-cache-dir`.
   - Order your instructions so that if you only change `app.py` later (not `requirements.txt`), Docker does NOT need to redo the `apt-get install` or `pip install` steps.

4. **In the final stage:**
   - Do NOT install `gcc` or `python3-dev` here at all, that's the whole point of splitting stages.
   - Copy the installed Python packages over from the `builder` stage (hint: pip installs packages into a Python site-packages directory, you'll need to copy that path across with `COPY --from=builder`).
   - Copy your application code (`app.py`) in.
   - Create a non-root user and switch to it, with correct ownership on the copied files.
   - Expose port 5000.
   - Run the app in exec form.

5. **General cache discipline:**
   - Anything that changes rarely (base image, system dependency installs) should appear before anything that changes often (your actual app code).

## How to Practice

Write your full Dockerfile. mark line by line and scored out of 100,by following the requirement. same as before, checking each requirement plus best practices around caching and image size.

```dockerfile
# Write your Dockerfile ...



```

## Self-Check Before Submitting

- [ ] Do I have exactly two `FROM` lines, with the first one named via `AS builder`?
- [ ] Is `gcc`/`python3-dev` installed ONLY in the builder stage, never in the final stage?
- [ ] Did I combine `apt-get update` and `apt-get install` into one RUN, and clean up apt's lists in that same RUN?
- [ ] Did I copy `requirements.txt` and install dependencies BEFORE copying the rest of my app code, in the builder stage?
- [ ] Did I use `COPY --from=builder` to bring the installed packages into the final stage?
- [ ] Did I create a non-root user in the final stage and give it ownership of the copied files?
- [ ] Is my final CMD in exec form?
- [ ] If I only edit `app.py` and rebuild, would Docker skip re-running the slow `apt-get`/`pip install` steps? (Think through this even though you can't literally test it here.)
