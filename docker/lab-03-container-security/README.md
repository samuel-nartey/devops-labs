
# Securing Containers

A hands-on, beginner-friendly guide to container security. We start with insecure defaults, then progressively harden the container so each concept builds naturally on the previous one.

---

## Table of contents

1. [What you will learn](#what-you-will-learn)
2. [Repository structure](#repository-structure)
3. [Sample application](#sample-application)
4. [Step 1 — Insecure default](#step-1--insecure-default)
5. [Step 2 — Non-root user](#step-2--non-root-user)
6. [Step 3 — .dockerignore](#step-3--dockerignore)
7. [Step 4 — Multi-stage builds](#step-4--multi-stage-builds)
8. [Step 5 — Distroless images](#step-5--distroless-images)
9. [Step 6 — Runtime hardening](#step-6--runtime-hardening)
10. [Summary](#summary)

---

## What you will learn

- Why running containers as root is dangerous and what it actually means
- How to run containers as a non-root user to reduce blast radius
- Why `.dockerignore` is critical for preventing secret leaks
- How multi-stage builds reduce attack surface by separating build from runtime
- Why distroless images remove almost all attacker footholds
- How to harden containers at runtime with kernel-level constraints

---

## Repository structure

```
sample-app/
├── app.js
├── package.json
└── README.md
```

---

## Sample application

We use a minimal Node.js application so the focus stays on container behavior and security, not application complexity. The app prints the user ID running inside the container — making root vs. non-root immediately visible in the terminal output.

---

## Step 1 — Insecure default

This is how many people first encounter Docker. It works, but it is not safe for production.

> **Warning:** This step is intentionally insecure. We start here so you understand what we are fixing and why. Do not use this Dockerfile in production.

### Dockerfile

```dockerfile
# Every line here has a security problem

FROM node:25              # full OS image — large attack surface

WORKDIR /app

COPY . .               # copies everything, including .env and .git

RUN npm install        # build tools remain in the final image

EXPOSE 3000
CMD ["npm", "start"]   # runs as root — no USER specified
```

### What's wrong here

| Issue | Why it's a problem |
|---|---|
| Runs as root | App compromise gives the attacker full container control — read any file, modify anything, pivot to the host |
| Single-stage build | npm, compilers, and build tools live in the final image and can be abused by attackers |
| Copies everything | Without `.dockerignore`, `.env`, `.git` history, and dev configs get baked into the image |
| Writable filesystem | Attackers can persist files, install backdoors, and make the container their base of operations |
| No resource limits | A compromised container can exhaust all CPU and memory, taking down other services on the same host |

### Build and run

```bash
docker build -f Dockerfile -t insecure-app .
docker run -p 3000:3000 insecure-app
```

**Output:**

```
User ID: 0
```

User ID `0` means root. If an attacker exploits your app, they have immediate full control of the container.

---

## Step 2 — Non-root user

Before optimizing images, the first real security fix is to stop running your application as root. If an attacker exploits your app as root, they get full container control. If they exploit it as a non-root user, they get limited permissions — significantly reducing the damage.

> **Concept — blast radius reduction:** We cannot always prevent a vulnerability from being exploited. But we can ensure that when it is, the damage is as limited as possible. Switching to a non-root user is the highest-impact single change in this guide.

### Dockerfile.nonroot

```dockerfile
FROM node:25

WORKDIR /app

# Create a dedicated system group and user
# -r creates a system account (no home directory, lower UID)
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . .
RUN npm install

# Switch to non-root user — all subsequent commands run as appuser
USER appuser

EXPOSE 3000
CMD ["npm", "start"]
```

### Build and run

```bash
docker build -f Dockerfile.nonroot -t nonroot-app .
docker run -p 3000:3000 nonroot-app
```

**Output:**

```
User ID: 1000
```

The app now runs as a non-root user with limited system permissions.

> **Still not complete:** The image is still large, build tools remain at runtime, and we are still copying everything — including potential secrets. The next steps address all of this.

---

## Step 3 — .dockerignore

Now that we fixed *who* runs the app, we fix *what* gets copied into it. Without a `.dockerignore`, every `COPY . .` instruction transfers your entire project directory — including files that have no place in a production image.

### .dockerignore

```
# Version control — never ship git history
.git
.gitignore

# Dependencies — reinstalled fresh during build anyway
node_modules

# Secrets — CRITICAL: prevent accidental credential leaks
.env
.env.*
*.pem
*.key

# Docker and documentation — not needed at runtime
Dockerfile*
README.md
*.md
```

### Why each entry matters

| Entry | Risk prevented |
|---|---|
| `.git` | Exposes full commit history, deleted secrets, internal notes, and author metadata |
| `.env` | Contains API keys and passwords — baked into the image, they leak to anyone who pulls it |
| `node_modules` | Hundreds of MB reinstalled during `RUN npm install` anyway — redundant and slow |
| `Dockerfile*` | Reveals your infrastructure layout and base images to anyone with image access |

---

## Step 4 — Multi-stage builds

Next, we separate build-time and runtime concerns. A Dockerfile can have multiple `FROM` statements — each starts a new stage. Only the final stage ships to production. Use `COPY --from=<stage>` to bring in only what the app needs to run.

### Dockerfile.multistage

```dockerfile
# ── Build stage ──────────────────────────────────────────
# This stage installs dependencies and compiles code.
# It will NOT appear in the final shipped image.
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .


# ── Runtime stage ────────────────────────────────────────
# Only this stage ships. It contains no build tools.
FROM node:25-slim

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "app.js"]
```

### What this achieves

- `npm`, compilers, and build tooling never reach the production image
- `node:25-slim` removes many development packages from the base, reducing size and CVE exposure
- Only `app.js` and `node_modules` are copied — nothing else

---

## Step 5 — Distroless images

Now we remove almost the entire operating system from the runtime image. Google's distroless images contain only your application and its runtime dependencies — no shell, no package manager, no OS utilities. An attacker who gets in has almost nothing to work with.

### Dockerfile (multi-stage + distroless)

```dockerfile
# ── Build stage ──────────────────────────────────────────
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .


# ── Distroless runtime ───────────────────────────────────
# No shell. No package manager. No OS utilities.
FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["app.js"]
```

### Build and run

```bash
docker build -t secure-app .
docker run -p 3000:3000 secure-app
```

**Output:**

```
User ID: 65532
```

Non-root by default, with no shell available. `docker exec -it` will return an error — because there is no shell. That is intentional.

> **Debugging note:** Without a shell, `docker exec` does not work. Rely on structured logging inside your app. Never ship debug tooling to production.

---

## Step 6 — Runtime hardening

Even a perfectly hardened image needs runtime protection. These flags constrain the container's behavior at the OS level — independently of what is inside the image.

### Hardened run command

```bash
docker run \
  --read-only                      \
  --tmpfs /tmp                     \
  --cap-drop ALL                   \
  --security-opt no-new-privileges \
  --pids-limit 100                 \
  --memory 256m                    \
  --cpus 0.5                       \
  -p 3000:3000                     \
  secure-app
```

### Flag reference

| Flag | What it does |
|---|---|
| `--read-only` | Makes the entire container filesystem read-only. Attackers cannot write files, install tools, or persist malware. |
| `--tmpfs /tmp` | Mounts an in-memory temp filesystem. Apps that need to write temporary files can still do so, but data is never persisted to disk. |
| `--cap-drop ALL` | Drops all Linux capabilities — fine-grained privileges beyond root/non-root. Removes network manipulation, process inspection, and more. |
| `--security-opt no-new-privileges` | Prevents any process from gaining elevated privileges via setuid binaries. Privilege level is locked at container start. |
| `--pids-limit 100` | Caps total processes at 100. Prevents fork bomb attacks that exhaust host resources and crash co-located services. |
| `--memory 256m` | Hard memory ceiling — the kernel kills the container if it tries to exceed 256 MB. Protects the host from runaway memory consumption. |
| `--cpus 0.5` | Limits the container to half a CPU core. Prevents cryptomining or runaway processes from monopolizing host compute. |

---

## Summary

> Secure container = Secure image + Hardened runtime. Each layer builds on the previous one. Skipping any layer weakens the whole system.

| Step | What it fixes |
|---|---|
| 1 — Baseline | Establishes the insecure starting point: root, no ignore, no stages, no limits |
| 2 — Non-root user | Limits blast radius — compromise no longer means full container control |
| 3 — .dockerignore | Keeps secrets and junk out of the image; faster builds, no accidental leaks |
| 4 — Multi-stage builds | Strips build tools from the runtime image; smaller and cleaner |
| 5 — Distroless | Removes the OS; no shell, no package manager, minimal CVE surface |
| 6 — Runtime hardening | Read-only FS, dropped capabilities, resource caps — defense in depth |

### What to explore next

- **Vulnerability scanning** with [Trivy](https://github.com/aquasecurity/trivy) or [Grype](https://github.com/anchore/grype) — compare CVE counts across your image variants
- **Secrets management** with HashiCorp Vault or Kubernetes Secrets
- **Image signing and provenance** with Sigstore/Cosign
- **Kubernetes security** — RBAC, Pod Security Admission, and NetworkPolicy
- **Runtime threat detection** with Falco

---
Securing Containers – A Beginner’s Hands‑on Guide (Refactored)
This repository is a step‑by‑step, interactive tutorial that teaches you how to secure Docker containers.
We start with the most common (but insecure) way of running a container, and then gradually harden it. Each step builds on the previous one, so you always understand why a change is needed.

What’s new?

A more instructive app.js that shows both user ID and filesystem write access.

Caching layer strategies – how to make builds fast and efficient.

Build context understanding – what Docker sends to the daemon and how to control it.

Image size reduction techniques – practical commands to measure and shrink your images.

All concepts come with hands‑on terminal examples you can run immediately.

What You Will Learn (and be able to do)
By the end of this guide, you will understand and be able to apply:

Why running containers as root is dangerous – and how to switch to a non‑root user.

How .dockerignore prevents secrets and junk from entering your image.

Build context – what it is, why it matters, and how to minimise it.

Docker layer caching – ordering instructions to speed up builds by 10×.

Multi‑stage builds – keeping build tools out of your final container.

Image size reduction – from 1 GB down to <100 MB using slim, distroless, and Alpine.

Distroless images – removing the OS shell and package manager for extreme minimalism.

Runtime hardening – limiting CPU, memory, filesystem permissions, and kernel capabilities.

Each concept is demonstrated with a working Dockerfile and a live command – you will see the difference immediately.

Repository Structure
text
sample-app/
├── app.js
├── package.json
└── README.md          (you are here)
Sample Application – app.js (Enhanced)
This tiny Node.js script does two things that help us understand security:

Prints the user ID (UID) – so we know if we are root (UID 0) or a normal user.

Tries to write a test file – to demonstrate read‑only filesystem behaviour later.

javascript
const http = require('http');
const fs = require('fs');

const server = http.createServer((req, res) => {
  const uid = process.getuid ? process.getuid() : 'unknown';
  let writeStatus = 'not attempted';

  // Try to write a test file to /tmp/test.txt
  try {
    fs.writeFileSync('/tmp/test.txt', 'Security test');
    writeStatus = 'SUCCESS (writable)';
  } catch (err) {
    writeStatus = 'FAILED (read-only)';
  }

  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end(`User ID: ${uid}\nWrite test: ${writeStatus}\n`);
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
When you visit http://localhost:3000 you will see both the user ID and whether the container can write files.
That’s all – no complexity, so you can focus entirely on container security.

package.json
json
{
  "name": "secure-container-demo",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {}
}
Step 1 – The Insecure Container (What Most Beginners Do)
This is the “it works on my machine” approach. The container runs, but it is not safe for production.

📄 Dockerfile (insecure)
dockerfile
FROM node:25

WORKDIR /app
COPY . .

RUN npm install

EXPOSE 3000
CMD ["npm", "start"]
🔍 What’s wrong here? – Detailed breakdown
Issue	Why it is a problem
Runs as root	If an attacker compromises your app, they have full root privileges inside the container – they can install malware, read any file, escape to the host in some configurations.
Single‑stage build	The final image contains the entire Node.js build toolchain (gcc, make, python, etc.). Attackers can use those tools to compromise your system.
Copies everything	.git folder, local .env secrets, node_modules from your host – all baked into the image. Secrets can leak, images become huge.
Writable filesystem	By default the container can write anywhere. An attacker can drop a backdoor script and make it persistent.
No resource limits	A single runaway process can consume all host memory or CPU, crashing other containers or the host itself.
🖥️ Build and run (interactive)
Open your terminal and run:

bash
docker build -f Dockerfile -t insecure-app .
docker run -p 3000:3000 insecure-app
Now open your browser to http://localhost:3000. You will see:

text
User ID: 0
Write test: SUCCESS (writable)
0 means root – the most powerful user on any Linux system.
The container can also write files anywhere, including /tmp.

🧠 Your turn: Try to run a shell inside the container:
docker exec -it <container-id> bash
You are root! You can install new software, read host files (if mounted), and more.

Step 2 – Understand Build Context (What Docker Actually Sends)
Before fixing security, you need to understand build context – a concept that confuses many beginners.

What is build context?
When you run docker build ., the . (dot) tells Docker the build context – the directory that Docker sends to the Docker daemon.
The daemon receives all files and subdirectories inside that context (unless ignored).

Why does it matter?
Large context → slow builds, huge images, accidental secret leaks.

Small context → fast builds, less disk usage, better security.

📊 Hands‑on: See the context size
bash
# Create a large dummy file inside your project
dd if=/dev/zero of=huge-file bs=1M count=100

# Build with verbose output (note the "Sending build context" line)
docker build -t test-context .

# Output will show something like:
# Sending build context to Docker daemon  104.9MB
That 100 MB dummy file was sent to the daemon – even though your Dockerfile never uses it!

✅ Fix with .dockerignore
Create a .dockerignore file to exclude unnecessary files:

text
.git
.gitignore
node_modules
.env
Dockerfile*
README.md
huge-file
*.log
Now rebuild – the context size drops dramatically.

💡 Best practice: Always commit a .dockerignore file before your first docker build. It saves time and prevents leaks.

Step 3 – Docker Layer Caching (Speed Up Builds)
Docker builds images in layers. Each instruction (FROM, COPY, RUN) creates a new layer.
If a layer hasn’t changed since the last build, Docker reuses the cached version – this can make builds 10× faster.

❌ Inefficient ordering (cache always invalidated)
dockerfile
FROM node:25
WORKDIR /app
COPY . .          # Any change in ANY file breaks cache for all subsequent layers
RUN npm install   # Re‑runs npm install even if package.json didn't change
Every time you change a single source file, Docker re‑copies everything and re‑runs npm install. That’s slow.

✅ Cache‑optimised ordering
dockerfile
FROM node:25
WORKDIR /app

# Copy only dependency files first
COPY package.json package-lock.json* ./
RUN npm install   # Cached as long as package.json doesn't change

# Copy the rest of the source code
COPY . .

EXPOSE 3000
CMD ["npm", "start"]
Now:

If you change app.js but not package.json → npm install is reused from cache → fast rebuild.

Only the final COPY . . layer is rebuilt.

🧪 Hands‑on: See caching in action
bash
# First build (no cache)
docker build -t cache-demo .

# Make a small change to app.js (e.g., add a comment)
echo "// cache test" >> app.js

# Second build – watch the "CACHED" lines
docker build -t cache-demo .
You will see CACHED next to the RUN npm install line. That’s the cache working.

🔥 Pro tip: For package managers like npm, pip, apt, always copy package.json/requirements.txt first, install dependencies, then copy the rest.

Step 4 – Run as Non‑Root User (Reduce the Blast Radius)
Now we fix the most dangerous problem: running as root.

Why non‑root matters
Root in container → attacker gets full control of that container.

Non‑root user → attacker is limited to the permissions of that user.

Cannot install packages.

Cannot change system files.

Much harder to break out of the container.

📄 Dockerfile.nonroot
dockerfile
FROM node:25

WORKDIR /app

# Create a dedicated user and group for the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Optimise caching: copy package files first
COPY package.json package-lock.json* ./
RUN npm install

# Now copy source (owner will be root, but we'll change later)
COPY . .

# Change ownership to appuser (optional but clean)
RUN chown -R appuser:appuser /app

# Switch from root to appuser
USER appuser

EXPOSE 3000
CMD ["npm", "start"]
🖥️ Build and run
bash
docker build -f Dockerfile.nonroot -t nonroot-app .
docker run -p 3000:3000 nonroot-app
Now visit http://localhost:3000:

text
User ID: 1000
Write test: SUCCESS (writable)
Not 0 anymore! The app runs with a regular user ID (often 1000).
It can still write files because we haven’t restricted the filesystem yet.

✅ Improvement: An attacker who compromises the app cannot become root inside the container.
⚠️ But still insecure: The image is large (≈1 GB), contains build tools, a shell, and many OS utilities.

Step 5 – Reduce Image Size (Multiple Techniques)
A smaller image is more secure (fewer components = fewer vulnerabilities), faster to deploy, and cheaper to store.

Technique 1 – Use a slim base image
Replace node:25 with node:25-slim – it removes many OS packages and reduces size by ~60%.

dockerfile
FROM node:25-slim
...
Technique 2 – Clean package manager caches
If you ever install OS packages (e.g., apt-get install), always clean the cache in the same RUN layer:

dockerfile
RUN apt-get update && apt-get install -y some-package \
    && rm -rf /var/lib/apt/lists/*   # ← prevents cache bloat
Technique 3 – Use Alpine Linux (ultra‑small)
Alpine images are 5 MB base size instead of 200 MB.

dockerfile
FROM node:25-alpine
Note: Alpine uses apk instead of apt, and sometimes has compatibility issues with native modules. For many Node apps it works perfectly.

Technique 4 – Multi‑stage builds (explained next)
This is the most powerful technique – we cover it in Step 6.

📊 Hands‑on: Compare sizes
Build images with different base images and check sizes:

bash
docker build -t test-node-full -f Dockerfile.node-full .      # node:25
docker build -t test-node-slim -f Dockerfile.node-slim .      # node:25-slim
docker build -t test-node-alpine -f Dockerfile.node-alpine .  # node:25-alpine

docker images | grep test-node
Example output:

text
test-node-full    1.2GB
test-node-slim    450MB
test-node-alpine  180MB
🧠 Your turn: Try rewriting the non‑root Dockerfile using node:25-alpine. Remember Alpine uses addgroup/adduser instead of groupadd/useradd.

Step 6 – Multi‑Stage Builds (Remove Build Tools)
Now we separate the build environment from the runtime environment to slash image size and remove attack vectors.

How multi‑stage works
First stage (builder) – uses the full Node.js image with all build tools.

Installs dependencies, compiles native addons, etc.

Second stage (runtime) – uses a slim or alpine image (no build tools).

Copies only the compiled application and node_modules.

The build tools are left behind – they never appear in the final image.

📄 Dockerfile.multistage
dockerfile
# -------- BUILD STAGE --------
FROM node:25 AS builder

WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install --production   # only production deps
COPY . .

# -------- RUNTIME STAGE (slim) --------
FROM node:25-slim

WORKDIR /app
# Copy only what's needed from builder
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/app.js ./app.js

EXPOSE 3000
CMD ["node", "app.js"]
🖥️ Build and compare sizes
bash
docker build -f Dockerfile.multistage -t multistage-app .
docker images | grep -E "nonroot-app|multistage-app"
You will see that multistage-app is significantly smaller (often 200‑300 MB instead of 1 GB).

✅ Security improvements
No build tools – attackers cannot run gcc, make, or npm to install new malware.

No development dependencies – we used npm install --production.

Smaller attack surface – fewer packages = fewer vulnerabilities.

⚠️ Still not perfect: The runtime image still contains a shell (bash or sh), a package manager (apt, apk), and many system utilities.

Step 7 – Distroless Images (Minimal & Secure)
Distroless images go one step further: they contain only your application and its runtime dependencies.
No shell, no package manager, no OS tools – not even ls or cat.

Why distroless is so secure
No shell – Even if an attacker exploits your app, they cannot run commands like curl, wget, or bash.

No package manager – They cannot install new software.

No OS utilities – They cannot explore the filesystem, change permissions, or escalate privileges.

Non‑root by default – Most distroless images run with a random high UID (e.g., 65532).

📄 Dockerfile.distroless
dockerfile
# -------- BUILD STAGE (same as before) --------
FROM node:25 AS builder

WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install --production
COPY . .

# -------- RUNTIME STAGE (distroless) --------
FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["app.js"]
📝 Note: Distroless images often require you to specify the exact interpreter. Here we use the Node.js 20 distroless image from Google.

🖥️ Build and run
bash
docker build -f Dockerfile.distroless -t distroless-app .
docker run -p 3000:3000 distroless-app
Now visit http://localhost:3000:

text
User ID: 65532
Write test: SUCCESS (writable)   # still writable because we haven't added --read-only
The user is non‑root (65532). Try to “break in”:

bash
docker exec -it <container-id> sh
You will get an error: exec: "sh": executable file not found in $PATH.
There is no shell to interact with. That is a powerful security feature.

✅ Summary of image size reduction journey
Image variant	Base size	Has shell?	Has build tools?	Suitable for production?
node:25 (insecure)	~1 GB	Yes	Yes	No
node:25-slim (non‑root)	~450 MB	Yes	No	Maybe
node:25-alpine (multi‑stage)	~180 MB	Yes (busybox)	No	Yes (with care)
Distroless	~120 MB	No	No	Yes (recommended)
Step 8 – Harden the Runtime (Defense in Depth)
Even the most secure image can be misused at runtime.
Runtime hardening adds extra layers of protection when you start the container.

🔧 Hardened docker run command
bash
docker run \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 100 \
  --memory 256m \
  --cpus 0.5 \
  -p 3000:3000 \
  distroless-app
📖 Explanation of each flag (beginner friendly)
Flag	What it does	Why it helps
--read-only	Makes the entire container filesystem read‑only.	An attacker cannot write any new files (backdoors, malware, logs). Our app.js will now show Write test: FAILED (read-only).
--tmpfs /tmp:rw,noexec,nosuid,size=64m	Creates an in‑memory writable /tmp folder with extra restrictions.	Some apps need to write temporary files. This allows that without persisting data, and noexec prevents executing code from /tmp.
--cap-drop ALL	Drops all Linux capabilities (special kernel permissions).	Even if the app runs as root, it cannot perform privileged actions (e.g., change network, mount filesystems).
--security-opt no-new-privileges	Prevents the process from gaining new privileges (e.g., via setuid).	Blocks privilege escalation attacks.
--pids-limit 100	Limits the number of processes (fork bombs) to 100.	Prevents a single container from consuming all process IDs on the host.
--memory 256m	Restricts memory usage to 256 MB.	Prevents memory exhaustion attacks (OOM killer on host).
--cpus 0.5	Restricts CPU usage to half a core.	Prevents CPU starvation of other containers / host.
🖥️ Try it yourself
Run the hardened command (replace distroless-app with your actual image name).
Now visit http://localhost:3000 – you will see:

text
User ID: 65532
Write test: FAILED (read-only)
The app can no longer write files, even though it tries. That’s a great security win – if an attacker exploited your app, they couldn’t drop a backdoor file.

🧠 Experiment: Remove --read-only from the command and re‑run. The write test will succeed again. Then add --read-only back – see the difference.

Step 9 – Caching Strategies for Package Managers (Advanced but Useful)
When you use multi‑stage builds, you can also cache dependencies across builds using --mount=type=cache. This is especially useful in CI/CD pipelines.

Example with npm cache
dockerfile
# Build stage with cache mount
FROM node:25 AS builder

WORKDIR /build
COPY package.json package-lock.json* ./

# Mount a persistent cache for npm
RUN --mount=type=cache,target=/root/.npm \
    npm install --production

COPY . .
The --mount=type=cache keeps the npm cache between builds, so npm install runs faster.

For apt (Debian/Ubuntu)
dockerfile
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y some-package
For apk (Alpine)
dockerfile
RUN --mount=type=cache,target=/var/cache/apk \
    apk add --update some-package
💡 Note: BuildKit (Docker ≥18.09) is required for --mount=type=cache. Enable it with DOCKER_BUILDKIT=1 docker build ....

Final Takeaway – The Complete Picture
A secure container is not one single trick – it is the combination of:

text
Secure container = Secure image  +  Hardened runtime
Layer	What you fix	Step(s)
Build context	What files are sent to daemon?	Step 2
Layer caching	How to make builds fast and reproducible	Step 3
Image user	Who runs the app? (non‑root)	Step 4
Image size	Slim, Alpine, multi‑stage, distroless	Steps 5, 6, 7
Runtime limits	CPU, memory, filesystem, capabilities	Step 8
Build caching	Persistent package caches	Step 9
📝 Your security & optimisation checklist
Add a .dockerignore file to every project.

Order Dockerfile instructions to maximise cache reuse (copy dependencies first).

Always use a non‑root user in your Dockerfile.

Use multi‑stage builds to exclude build tools.

Prefer distroless or slim base images for production.

Run containers with --read-only, --cap-drop ALL, and resource limits.

Use --mount=type=cache in CI/CD to speed up repeated builds.

🎯 Next steps
Try to adapt these steps for a real application (Python, Go, Java).

Learn about image scanning (e.g., docker scan, Trivy) to find known vulnerabilities.

Read about secrets management (Docker secrets, environment variables, vaults).

Need help? Common beginner questions
Q: My app needs to write logs or upload files – how can I use --read-only?
A: Use --tmpfs for ephemeral writes, or mount a writable volume only for the specific directory (e.g., -v ./logs:/app/logs). The rest of the filesystem stays read‑only.

Q: Distroless images don’t have npm – how do I run npm start?
A: Use the raw Node command: CMD ["node", "app.js"]. For more complex apps, build a custom entrypoint script in the builder stage.

Q: I get permission errors with non‑root user and volumes.
A: Ensure the volume’s ownership matches the container’s user ID. Use chown in the Dockerfile or create the volume with correct permissions.

Q: Are Alpine images always better than slim?
A: Alpine is smaller, but its libc (musl) can cause issues with native Node modules. Test first. For many apps, node:*-slim is a safer trade‑off.

Q: How do I enable BuildKit for cache mounts?
A: Run export DOCKER_BUILDKIT=1 before your docker build command, or add to your shell profile.


# Securing Containers

A hands-on, beginner-friendly guide to container security. We start with insecure defaults, then progressively harden the container so each concept builds naturally on the previous one.

---

## Table of contents

1. [What you will learn](#what-you-will-learn)
2. [Repository structure](#repository-structure)
3. [Sample application](#sample-application)
4. [Step 1 — Insecure default](#step-1--insecure-default)
5. [Step 2 — Non-root user](#step-2--non-root-user)
6. [Step 3 — .dockerignore](#step-3--dockerignore)
7. [Step 4 — Multi-stage builds](#step-4--multi-stage-builds)
8. [Step 5 — Distroless images](#step-5--distroless-images)
9. [Step 6 — Runtime hardening](#step-6--runtime-hardening)
10. [Summary](#summary)

---

## What you will learn

- Why running containers as root is dangerous and what it actually means
- How to run containers as a non-root user to reduce blast radius
- Why `.dockerignore` is critical for preventing secret leaks
- How multi-stage builds reduce attack surface by separating build from runtime
- Why distroless images remove almost all attacker footholds
- How to harden containers at runtime with kernel-level constraints

---

## Repository structure

```
sample-app/
├── app.js
├── package.json
└── README.md
```

---

## Sample application

We use a minimal Node.js application so the focus stays on container behavior and security, not application complexity. The app prints the user ID running inside the container — making root vs. non-root immediately visible in the terminal output.

---

## Step 1 — Insecure default

This is how many people first encounter Docker. It works, but it is not safe for production.

> **Warning:** This step is intentionally insecure. We start here so you understand what we are fixing and why. Do not use this Dockerfile in production.

### Dockerfile

```dockerfile
# Every line here has a security problem

FROM node:25              # full OS image — large attack surface

WORKDIR /app

COPY . .               # copies everything, including .env and .git

RUN npm install        # build tools remain in the final image

EXPOSE 3000
CMD ["npm", "start"]   # runs as root — no USER specified
```

### What's wrong here

| Issue | Why it's a problem |
|---|---|
| Runs as root | App compromise gives the attacker full container control — read any file, modify anything, pivot to the host |
| Single-stage build | npm, compilers, and build tools live in the final image and can be abused by attackers |
| Copies everything | Without `.dockerignore`, `.env`, `.git` history, and dev configs get baked into the image |
| Writable filesystem | Attackers can persist files, install backdoors, and make the container their base of operations |
| No resource limits | A compromised container can exhaust all CPU and memory, taking down other services on the same host |

### Build and run

```bash
docker build -f Dockerfile -t insecure-app .
docker run -p 3000:3000 insecure-app
```

**Output:**

```
User ID: 0
```

User ID `0` means root. If an attacker exploits your app, they have immediate full control of the container.

---

## Step 2 — Non-root user

Before optimizing images, the first real security fix is to stop running your application as root. If an attacker exploits your app as root, they get full container control. If they exploit it as a non-root user, they get limited permissions — significantly reducing the damage.

> **Concept — blast radius reduction:** We cannot always prevent a vulnerability from being exploited. But we can ensure that when it is, the damage is as limited as possible. Switching to a non-root user is the highest-impact single change in this guide.

### Dockerfile.nonroot

```dockerfile
FROM node:25

WORKDIR /app

# Create a dedicated system group and user
# -r creates a system account (no home directory, lower UID)
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY . .
RUN npm install

# Switch to non-root user — all subsequent commands run as appuser
USER appuser

EXPOSE 3000
CMD ["npm", "start"]
```

### Build and run

```bash
docker build -f Dockerfile.nonroot -t nonroot-app .
docker run -p 3000:3000 nonroot-app
```

**Output:**

```
User ID: 1000
```

The app now runs as a non-root user with limited system permissions.

> **Still not complete:** The image is still large, build tools remain at runtime, and we are still copying everything — including potential secrets. The next steps address all of this.

---

## Step 3 — .dockerignore

Now that we fixed *who* runs the app, we fix *what* gets copied into it. Without a `.dockerignore`, every `COPY . .` instruction transfers your entire project directory — including files that have no place in a production image.

### .dockerignore

```
# Version control — never ship git history
.git
.gitignore

# Dependencies — reinstalled fresh during build anyway
node_modules

# Secrets — CRITICAL: prevent accidental credential leaks
.env
.env.*
*.pem
*.key

# Docker and documentation — not needed at runtime
Dockerfile*
README.md
*.md
```

### Why each entry matters

| Entry | Risk prevented |
|---|---|
| `.git` | Exposes full commit history, deleted secrets, internal notes, and author metadata |
| `.env` | Contains API keys and passwords — baked into the image, they leak to anyone who pulls it |
| `node_modules` | Hundreds of MB reinstalled during `RUN npm install` anyway — redundant and slow |
| `Dockerfile*` | Reveals your infrastructure layout and base images to anyone with image access |

---

## Step 4 — Multi-stage builds

Next, we separate build-time and runtime concerns. A Dockerfile can have multiple `FROM` statements — each starts a new stage. Only the final stage ships to production. Use `COPY --from=<stage>` to bring in only what the app needs to run.

### Dockerfile.multistage

```dockerfile
# ── Build stage ──────────────────────────────────────────
# This stage installs dependencies and compiles code.
# It will NOT appear in the final shipped image.
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .


# ── Runtime stage ────────────────────────────────────────
# Only this stage ships. It contains no build tools.
FROM node:25-slim

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "app.js"]
```

### What this achieves

- `npm`, compilers, and build tooling never reach the production image
- `node:25-slim` removes many development packages from the base, reducing size and CVE exposure
- Only `app.js` and `node_modules` are copied — nothing else

---

## Step 5 — Distroless images

Now we remove almost the entire operating system from the runtime image. Google's distroless images contain only your application and its runtime dependencies — no shell, no package manager, no OS utilities. An attacker who gets in has almost nothing to work with.

### Dockerfile (multi-stage + distroless)

```dockerfile
# ── Build stage ──────────────────────────────────────────
FROM node:25 AS builder

WORKDIR /build
COPY package.json ./
RUN npm install
COPY . .


# ── Distroless runtime ───────────────────────────────────
# No shell. No package manager. No OS utilities.
FROM gcr.io/distroless/nodejs20-debian12

WORKDIR /app
COPY --from=builder /build/app.js ./app.js
COPY --from=builder /build/node_modules ./node_modules

EXPOSE 3000
CMD ["app.js"]
```

### Build and run

```bash
docker build -t secure-app .
docker run -p 3000:3000 secure-app
```

**Output:**

```
User ID: 65532
```

Non-root by default, with no shell available. `docker exec -it` will return an error — because there is no shell. That is intentional.

> **Debugging note:** Without a shell, `docker exec` does not work. Rely on structured logging inside your app. Never ship debug tooling to production.

---

## Step 6 — Runtime hardening

Even a perfectly hardened image needs runtime protection. These flags constrain the container's behavior at the OS level — independently of what is inside the image.

### Hardened run command

```bash
docker run \
  --read-only                      \
  --tmpfs /tmp                     \
  --cap-drop ALL                   \
  --security-opt no-new-privileges \
  --pids-limit 100                 \
  --memory 256m                    \
  --cpus 0.5                       \
  -p 3000:3000                     \
  secure-app
```

### Flag reference

| Flag | What it does |
|---|---|
| `--read-only` | Makes the entire container filesystem read-only. Attackers cannot write files, install tools, or persist malware. |
| `--tmpfs /tmp` | Mounts an in-memory temp filesystem. Apps that need to write temporary files can still do so, but data is never persisted to disk. |
| `--cap-drop ALL` | Drops all Linux capabilities — fine-grained privileges beyond root/non-root. Removes network manipulation, process inspection, and more. |
| `--security-opt no-new-privileges` | Prevents any process from gaining elevated privileges via setuid binaries. Privilege level is locked at container start. |
| `--pids-limit 100` | Caps total processes at 100. Prevents fork bomb attacks that exhaust host resources and crash co-located services. |
| `--memory 256m` | Hard memory ceiling — the kernel kills the container if it tries to exceed 256 MB. Protects the host from runaway memory consumption. |
| `--cpus 0.5` | Limits the container to half a CPU core. Prevents cryptomining or runaway processes from monopolizing host compute. |

---

## Summary

> Secure container = Secure image + Hardened runtime. Each layer builds on the previous one. Skipping any layer weakens the whole system.

| Step | What it fixes |
|---|---|
| 1 — Baseline | Establishes the insecure starting point: root, no ignore, no stages, no limits |
| 2 — Non-root user | Limits blast radius — compromise no longer means full container control |
| 3 — .dockerignore | Keeps secrets and junk out of the image; faster builds, no accidental leaks |
| 4 — Multi-stage builds | Strips build tools from the runtime image; smaller and cleaner |
| 5 — Distroless | Removes the OS; no shell, no package manager, minimal CVE surface |
| 6 — Runtime hardening | Read-only FS, dropped capabilities, resource caps — defense in depth |

### What to explore next

- **Vulnerability scanning** with [Trivy](https://github.com/aquasecurity/trivy) or [Grype](https://github.com/anchore/grype) — compare CVE counts across your image variants
- **Secrets management** with HashiCorp Vault or Kubernetes Secrets
- **Image signing and provenance** with Sigstore/Cosign
- **Kubernetes security** — RBAC, Pod Security Admission, and NetworkPolicy
- **Runtime threat detection** with Falco
