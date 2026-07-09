// DevOps repos
// https://github.com/bregman-arie/devops-exercises


// ─────────────────────────────────────────────────────────────
// Core dependencies
// express  → web framework to handle HTTP routes
// os       → gives us system info like hostname
// fs       → filesystem module so we can write log files
// path     → helps build safe file paths across OS types
// ─────────────────────────────────────────────────────────────
const express = require("express");
const os      = require("os");
const fs      = require("fs");
const path    = require("path");

const app  = express();
const PORT = 3000;

// ─────────────────────────────────────────────────────────────
// LOG FILE SETUP
// __dirname  → the folder where this app.js file lives (/app)
// logFile    → full path: /app/app.log
//
// This is the file that will FAIL to create if the container
// runs as root and you switch USER without --chown on COPY.
// appuser won't have write permission on /app (owned by root).
// ─────────────────────────────────────────────────────────────
const logFile = path.join(__dirname, "app.log");

// ─────────────────────────────────────────────────────────────
// LOGGER FUNCTION
// Called on every request. Appends one line to app.log.
// appendFileSync → opens file, adds line, closes file.
//                  If file doesn't exist yet, it creates it.
// toISOString()  → produces a standard timestamp e.g.
//                  2026-04-06T13:00:00.000Z
// ─────────────────────────────────────────────────────────────
function logRequest(method, url, statusCode) {
  const timestamp = new Date().toISOString();
  const line      = `[${timestamp}] ${method} ${url} → ${statusCode}\n`;

  try {
    fs.appendFileSync(logFile, line);
  } catch (err) {
    // If writing fails (e.g. permission denied), print to console
    // so we can see the error in docker logs without crashing the app
    console.error("Could not write to log file:", err.message);
  }
}

// ─────────────────────────────────────────────────────────────
// HOME ROUTE  →  GET /
// Serves the main HTML page.
// Template literals (backticks) let us embed JS variables
// directly into the HTML string using ${...}
// ─────────────────────────────────────────────────────────────
app.get("/", (req, res) => {

  // Gather runtime info to display on the page
  const hostname  = os.hostname();           // container ID or name
  const uid       = process.getuid();        // user running the process (0 = root, bad!)
  const platform  = os.platform();           // linux
  const nodeVer   = process.version;         // e.g. v20.11.0
  const uptime    = Math.floor(process.uptime()); // seconds since app started
  const memory    = (process.memoryUsage().rss / 1024 / 1024).toFixed(1); // MB

  // Read the current log file contents to display on the page.
  // If the file doesn't exist yet (first request), show a placeholder.
  let logContents = "No log entries yet.";
  try {
    logContents = fs.readFileSync(logFile, "utf8") || "No log entries yet.";
  } catch {
    logContents = "Log file not created yet — this is the first request!";
  }

  // Log this request BEFORE sending the response
  // so it appears in the log shown on the page
  logRequest(req.method, req.url, 200);

  // Re-read the log after writing so the page shows the latest entry
  try {
    logContents = fs.readFileSync(logFile, "utf8");
  } catch {
    logContents = "Could not read log file.";
  }

  // Send back the full HTML page as a string
  res.status(200).send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Container Security Lab</title>

  <!-- Google Fonts: Syne (headings) + JetBrains Mono (code/log) -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet" />

  <style>
    /* ── RESET & BASE ─────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    /* CSS custom properties — change these to retheme everything */
    :root {
      --bg:        #0a0e17;        /* deep navy background          */
      --surface:   #111827;        /* card / panel background       */
      --border:    #1f2d45;        /* subtle borders                */
      --accent:    #00d4ff;        /* cyan highlight                */
      --accent2:   #ff6b35;        /* orange for warnings/uid=0     */
      --green:     #00ff88;        /* green for healthy status      */
      --text:      #e2e8f0;        /* primary text                  */
      --muted:     #64748b;        /* secondary / label text        */
      --font-head: 'Syne', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-head);
      min-height: 100vh;
      /* subtle grid pattern in background */
      background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
    }

    /* ── LAYOUT ───────────────────────────────────────── */
    .wrapper {
      max-width: 900px;
      margin: 0 auto;
      padding: 48px 24px 80px;
    }

    /* ── HEADER ───────────────────────────────────────── */
    header {
      border-bottom: 1px solid var(--border);
      padding-bottom: 32px;
      margin-bottom: 40px;
    }

    .tag {
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 4px 10px;
      border-radius: 2px;
      margin-bottom: 16px;
      /* subtle glow on the tag */
      box-shadow: 0 0 12px rgba(0,212,255,0.2);
    }

    h1 {
      font-size: clamp(1.6rem, 4vw, 2.4rem);
      font-weight: 800;
      line-height: 1.2;
      color: #fff;
    }

    h1 span { color: var(--accent); }

    .subtitle {
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.95rem;
      font-weight: 400;
    }

    .subtitle a {
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: border-color 0.2s;
    }
    .subtitle a:hover { border-color: var(--accent); }

    /* ── GRID of STAT CARDS ───────────────────────────── */
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 20px;
      position: relative;
      overflow: hidden;
      /* top coloured bar */
    }

    /* thin accent bar at top of each card */
    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: var(--accent);
    }

    /* warning card — orange accent for UID=0 (root) */
    .card.warn::before { background: var(--accent2); }
    .card.warn .card-value { color: var(--accent2); }

    /* good card — green for healthy */
    .card.good::before { background: var(--green); }
    .card.good .card-value { color: var(--green); }

    .card-label {
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }

    .card-value {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--accent);
      word-break: break-all;
    }

    /* ── SECURITY NOTE ────────────────────────────────── */
    .security-note {
      background: rgba(255, 107, 53, 0.08);
      border: 1px solid rgba(255, 107, 53, 0.3);
      border-radius: 6px;
      padding: 16px 20px;
      margin-bottom: 32px;
      font-family: var(--font-mono);
      font-size: 0.82rem;
      color: var(--accent2);
      line-height: 1.6;
    }

    .security-note strong { display: block; margin-bottom: 4px; font-size: 0.9rem; }

    /* ── LOG PANEL ────────────────────────────────────── */
    .log-panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      margin-bottom: 32px;
    }

    .log-header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 20px;
      border-bottom: 1px solid var(--border);
      background: rgba(0,212,255,0.04);
    }

    /* three dots like a terminal titlebar */
    .dot { width: 10px; height: 10px; border-radius: 50%; }
    .dot.r { background: #ff5f57; }
    .dot.y { background: #ffbd2e; }
    .dot.g { background: #28c840; }

    .log-title {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--muted);
      margin-left: 4px;
    }

    /* the log text area */
    .log-body {
      padding: 20px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      line-height: 1.8;
      color: #94a3b8;
      white-space: pre-wrap;       /* preserve line breaks */
      word-break: break-all;
      max-height: 260px;
      overflow-y: auto;            /* scroll if many entries */
      /* custom thin scrollbar */
      scrollbar-width: thin;
      scrollbar-color: var(--border) transparent;
    }

    /* highlight the timestamp in each log line */
    .log-body { color: #64748b; }

    /* ── FOOTER ───────────────────────────────────────── */
    footer {
      border-top: 1px solid var(--border);
      padding-top: 24px;
      font-size: 0.82rem;
      color: var(--muted);
      font-family: var(--font-mono);
    }

    footer a { color: var(--accent); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="wrapper">

  <!-- ── HEADER ───────────────────────────────────────── -->
  <header>
    <div class="tag">Container Security Lab</div>
    <h1>Hello from <span>Bismark</span></h1>
    <p class="subtitle">
      AWS Community Builder &amp; DevSecOps Facilitator &mdash;
      <a href="https://github.com/samuel-nartey/devops-labs" target="_blank">
        50+ Docker Projects on GitHub
      </a>
    </p>
  </header>

  <!-- ── STAT CARDS ────────────────────────────────────── -->
  <!--
    Each card shows one piece of runtime info.
    The "warn" class turns orange — used when UID is 0 (root),
    which is a security risk you are practising to fix.
  -->
  <div class="cards">

    <div class="card">
      <div class="card-label">Hostname</div>
      <!-- os.hostname() returns the container ID in Docker -->
      <div class="card-value">${hostname}</div>
    </div>

    <div class="card ${uid === 0 ? "warn" : "good"}">
      <div class="card-label">Running as UID</div>
      <!--
        UID 0 = root (dangerous — card turns orange).
        Any other UID = non-root user (good — card turns green).
        This is the core lesson of the containerization module.
      -->
      <div class="card-value">${uid === 0 ? "0 (root)" : uid}</div>
    </div>

    <div class="card">
      <div class="card-label">Platform</div>
      <div class="card-value">${platform}</div>
    </div>

    <div class="card">
      <div class="card-label">Node Version</div>
      <div class="card-value">${nodeVer}</div>
    </div>

    <div class="card">
      <div class="card-label">Uptime</div>
      <div class="card-value">${uptime}s</div>
    </div>

    <div class="card">
      <div class="card-label">Memory (RSS)</div>
      <div class="card-value">${memory} MB</div>
    </div>

  </div>

  <!-- ── SECURITY NOTE ─────────────────────────────────── -->
  <!--
    Shown only when the process is running as root (UID 0).
    This is a visual reminder of what you are practising to fix.
    In production you would remove this block or keep it for
    educational display.
  -->
  ${uid === 0 ? `
  <div class="security-note">
    <strong>Security Warning</strong>
    This container is running as root (UID 0). If an attacker gains access,
    they can potentially escape to the host. Add a non-root user in your
    Dockerfile and use the USER directive to fix this.
  </div>
  ` : `
  <div class="security-note" style="border-color:rgba(0,255,136,0.3);background:rgba(0,255,136,0.06);color:var(--green)">
    <strong>Good — Running as non-root (UID ${uid})</strong>
    The container is running as a non-root user. This reduces the blast
    radius if an attacker gains access to this container.
  </div>
  `}

  <!-- ── REQUEST LOG PANEL ──────────────────────────────── -->
  <!--
    This panel displays the contents of /app/app.log.
    Every GET / request appends one line to that file.
    If the container runs as root without --chown, appuser
    cannot write to this file and the app crashes on requests.
    That is the practical failure scenario you are studying.
  -->
  <div class="log-panel">
    <div class="log-header">
      <!-- terminal-style dots, purely decorative -->
      <div class="dot r"></div>
      <div class="dot y"></div>
      <div class="dot g"></div>
      <span class="log-title">/app/app.log &mdash; live request log</span>
    </div>
    <!--
      pre-wrap keeps the line breaks from the log file.
      Each line was written by logRequest() above.
    -->
    <div class="log-body">${logContents}</div>
  </div>

  <!-- ── FOOTER ────────────────────────────────────────── -->
  <footer>
    Part of the <strong>Container Security Module</strong> &mdash;
    <a href="https://github.com/samuel-nartey/devops-labs" target="_blank">
      github.com/samuel-nartey/devops-labs
    </a>
  </footer>

</div>
</body>
</html>`);
});

// ─────────────────────────────────────────────────────────────
// HEALTH CHECK ROUTE  →  GET /health
// Used by Docker / Kubernetes to check if the app is alive.
// Returns 200 OK with plain text. No logging needed here —
// health checks are called frequently and would flood the log.
// ─────────────────────────────────────────────────────────────
app.get("/health", (req, res) => {
  res.status(200).send("OK");
});

// ─────────────────────────────────────────────────────────────
// START THE SERVER
// Binds to 0.0.0.0 so it is reachable from outside the container.
// console.log prints to stdout — visible via: docker logs <container>
// ─────────────────────────────────────────────────────────────
app.listen(PORT, "0.0.0.0", () => {
  console.log(`App running on port ${PORT}`);
  console.log(`Logging requests to: ${logFile}`);
  console.log(`Running as UID: ${process.getuid()}`);
});
