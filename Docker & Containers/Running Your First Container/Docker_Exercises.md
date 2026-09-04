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


# Practice Set: Exercises 2 to 5

Same format as Exercise 1: a scenario, a requirements checklist, then a fully commented solution. Each one uses a different language on purpose, so the same Dockerfile instructions get practiced against different ecosystem quirks (different package managers, different base image families, and in two cases, multi-stage builds).

---

## Exercise 2: Dockerize a Node.js (Express) app

**The scenario:**

```
myapp/
├── server.js
├── package.json
```

`package.json` lists `express` as a dependency. `server.js` listens on port 3000.

**Your task:** write a Dockerfile that meets ALL of these requirements:

1. Uses `node:20-alpine` as the base image
2. Sets `/usr/src/app` as the working directory
3. Copies `package.json` (and `package-lock.json`) in first, installs dependencies, THEN copies the rest of the app code
4. Installs dependencies with `npm ci --omit=dev` instead of `npm install` (reproducible, production-only install)
5. Documents that the container listens on port 3000
6. Creates and switches to a non-root user before running the app (note: Alpine doesn't have `useradd`, it uses `addgroup` / `adduser`)
7. Runs the app using exec form, as `node server.js`

**Solution:**

```dockerfile
# Small base image: Alpine Linux + Node 20. Good default for production Node images.
FROM node:20-alpine

# All following instructions run from this directory inside the container
WORKDIR /usr/src/app

# Copy ONLY the dependency manifests first. This is the same caching trick as
# Exercise 1: the "npm ci" layer below only re-runs when these files change,
# not every time application source code changes.
COPY package.json package-lock.json ./

# npm ci (not npm install) does a clean, reproducible install strictly from
# package-lock.json. --omit=dev skips devDependencies, which have no business
# being in a production image.
RUN npm ci --omit=dev

# Now copy the rest of the application source
COPY . .

# Document the port the app listens on. Does not publish it, just documents it.
EXPOSE 3000

# Alpine images use addgroup/adduser instead of groupadd/useradd.
# -S = system account, -G = add to this group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Switch to the non-root user before the app runs
USER appuser

# Exec form: runs node directly as PID 1, so it receives signals like SIGTERM correctly
CMD ["node", "server.js"]
```

---

## Exercise 3: Dockerize a Go app (multi-stage build)

**The scenario:**

```
myapp/
├── main.go
├── go.mod
├── go.sum
```

A compiled Go HTTP server listening on port 8080. Go compiles to a single static binary, which makes it a good app to introduce **multi-stage builds**: use one image to compile the code, and a second, much smaller image to actually run it.

**Your task:** write a Dockerfile that meets ALL of these requirements:

1. Uses a `golang:1.22` build stage to compile the app
2. Uses `gcr.io/distroless/static-debian12` as the final, minimal runtime stage
3. Sets `/app` as the working directory in the build stage
4. Copies `go.mod` and `go.sum` in first, downloads modules, THEN copies the rest of the source
5. Builds a statically linked binary (`CGO_ENABLED=0`)
6. Copies ONLY the compiled binary into the final stage, nothing else from the build stage
7. Documents that the container listens on port 8080
8. Runs as a non-root user in the final stage (the distroless `nonroot` variant already ships a built-in non-root user, no `useradd` needed)
9. Runs the binary using exec form

**Solution:**

```dockerfile
# ---------- Stage 1: build ----------
# This stage has the full Go toolchain, but none of it ships in the final image
FROM golang:1.22 AS builder

WORKDIR /app

# Copy dependency files first. "go mod download" only re-runs when go.mod or
# go.sum actually change, not on every source code edit.
COPY go.mod go.sum ./
RUN go mod download

# Now copy the actual source code
COPY . .

# CGO_ENABLED=0 produces a fully static binary with no C library dependencies,
# which is required for it to run on a minimal image like distroless that has
# no shared libraries at all. GOOS=linux makes the target explicit regardless
# of what OS you're building on.
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .

# ---------- Stage 2: run ----------
# distroless images contain almost nothing: no shell, no package manager, no
# extra binaries. Massive reduction in attack surface compared to a full OS
# base image. The ":nonroot" tag also ships a non-root user out of the box.
FROM gcr.io/distroless/static-debian12:nonroot

WORKDIR /app

# Copy ONLY the compiled binary from the builder stage. Nothing else from
# that build stage makes it into the final image.
COPY --from=builder /app/server /app/server

EXPOSE 8080

# distroless:nonroot already runs as a non-root user by default, but being
# explicit here documents the intent for anyone reading the file
USER nonroot:nonroot

# Exec form. Note: there's no shell in this image, so shell form
# ("CMD /app/server") would fail outright, exec form is the only option that works.
CMD ["/app/server"]
```

---

## Exercise 4: Dockerize a Java Spring Boot app (Maven multi-stage build)

**The scenario:**

```
myapp/
├── pom.xml
├── src/
│   └── main/java/...
```

A Spring Boot app that builds into an executable jar and listens on port 8080. Same multi-stage idea as Exercise 3, but with a build tool (Maven) in the picture instead of a single compile command.

**Your task:** write a Dockerfile that meets ALL of these requirements:

1. Uses a `maven:3.9-eclipse-temurin-17` build stage to build the jar
2. Uses `eclipse-temurin:17-jre-alpine` as the final, minimal runtime stage
3. Sets `/build` as the working directory in the build stage
4. Copies `pom.xml` in first and downloads dependencies offline, THEN copies the rest of the source (caching, same idea as Exercises 1 to 3, applied to Maven's local repo)
5. Packages the app, skipping tests during the image build (`-DskipTests`)
6. Copies ONLY the built jar into the final stage
7. Documents that the container listens on port 8080
8. Creates and switches to a non-root user in the final stage
9. Runs the jar using exec form

**Solution:**

```dockerfile
# ---------- Stage 1: build ----------
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Copy only the pom first. "dependency:go-offline" pre-downloads every
# dependency Maven will need. This layer is cached and skipped on rebuilds
# unless pom.xml itself changes, so editing a .java file doesn't trigger a
# full re-download of the internet.
COPY pom.xml .
RUN mvn dependency:go-offline

# Now copy the actual source
COPY src ./src

# Build the jar. -DskipTests keeps the image build fast; tests belong in CI,
# not in the Docker build step.
RUN mvn package -DskipTests

# ---------- Stage 2: run ----------
# JRE only, not the full JDK, and Alpine keeps it small. We don't need a
# compiler or build tools to run an already-built jar.
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Alpine syntax again: addgroup/adduser, not groupadd/useradd
RUN addgroup -S spring && adduser -S spring -G spring

# Copy ONLY the built jar out of the builder stage. The wildcard picks up
# whatever version Maven produced without hardcoding the jar's exact name.
COPY --from=builder /build/target/*.jar /app/app.jar

EXPOSE 8080

USER spring

# Exec form
CMD ["java", "-jar", "/app/app.jar"]
```

---

## Exercise 5: Dockerize a Ruby (Sinatra) app

**The scenario:**

```
myapp/
├── app.rb
├── Gemfile
├── Gemfile.lock
```

A small Sinatra web app listening on port 4567. Single-stage, like Exercise 1 and 2, to close the set out on the same pattern the lab started with.

**Your task:** write a Dockerfile that meets ALL of these requirements:

1. Uses `ruby:3.3-slim` as the base image
2. Sets `/app` as the working directory
3. Copies `Gemfile` and `Gemfile.lock` in first, installs gems, THEN copies the rest of the app code
4. Installs gems with `bundle install --deployment --without development test`
5. Documents that the container listens on port 4567
6. Creates and switches to a non-root user before running the app
7. Runs the app using exec form, as `ruby app.rb`

**Solution:**

```dockerfile
FROM ruby:3.3-slim

WORKDIR /app

# Same caching pattern as every exercise above: copy only the gem manifests
# first, so "bundle install" is only re-run when a gem actually changes
COPY Gemfile Gemfile.lock ./

# --deployment enforces that Gemfile.lock is respected exactly, no silent
# version drift. --without development test skips gems this image will
# never need at runtime.
RUN bundle install --deployment --without development test

# Now copy the rest of the app
COPY . .

EXPOSE 4567

# Debian-based image (ruby:3.3-slim), so this is useradd syntax, same family
# as Exercise 1's Python image but different from the Alpine-based Exercises
# 2 and 4
RUN useradd --create-home appuser
USER appuser

CMD ["ruby", "app.rb"]
```

---

## Recurring pattern across all five exercises

Worth calling out explicitly to the class: every solution above follows the same four moves, just with different tooling per language.

1. **Copy manifest before source.** `requirements.txt`, `package.json`, `go.mod`, `pom.xml`, `Gemfile`, always copied and installed before the rest of the app, for layer caching.
2. **Minimal base image.** `slim`, `alpine`, or `distroless`, never the full default image, to keep the attack surface and image size down.
3. **Non-root user, created before it's referenced.** The exact command changes (`useradd` vs `addgroup`/`adduser` vs a built-in distroless user), but the ordering rule is the same: the user must exist before anything tries to use it.
4. **Exec form for the final `CMD`/`ENTRYPOINT`.** So the app runs as PID 1 and receives container signals correctly.
