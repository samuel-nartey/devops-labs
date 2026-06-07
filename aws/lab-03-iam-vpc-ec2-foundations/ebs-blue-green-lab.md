# Blue-Green Deployment with AWS Elastic Beanstalk
### Console-based guide — follows the exact AWS wizard steps

---

## What You Will Build

A Notes Manager web app (Node.js + Express + PostgreSQL on RDS) deployed on Elastic Beanstalk.
You will deploy v1 as the Blue environment, make a visible change for v2, deploy it as Green,
then perform a CNAME swap — watching production traffic switch instantly with zero downtime.

```
            ┌────────────────────────────────────┐
            │  notes-blue.elasticbeanstalk.com    │
            │  (your production URL)              │
            └────────────────┬───────────────────┘
                             │ CNAME swap flips this
          ┌──────────────────▼──────────────────┐
          │  100% traffic                        │  0% (testing only)
          ▼                                      ▼
  ┌───────────────┐                    ┌───────────────┐
  │  BLUE (live)  │                    │ GREEN (idle)  │
  │  v1 of app    │                    │ v2 of app     │
  └───────┬───────┘                    └───────┬───────┘
          │                                    │
          └──────────────┬─────────────────────┘
                         ▼
               ┌──────────────────┐
               │  RDS PostgreSQL  │
               │  (shared by both)│
               └──────────────────┘
```

---

## Before You Start — Have These Ready

- Your `notes-app-v1.zip` (2 files zipped: `app.js`, `package.json`)
- AWS account with console access
- About 30–40 minutes

> You do NOT need a domain name. AWS gives every EB environment a free URL automatically
> like `notes-blue.us-east-1.elasticbeanstalk.com`. That is all you need for this exercise.

---

## The App Files

Create a folder called `notes-app` on your computer with these 2 files.

> ⚠️ **CRITICAL: Do NOT include a `.env` file in your zip.**
> Elastic Beanstalk injects environment variables directly into the process.
> A `.env` file will override your EB configuration and cause startup failures.

---

### File 1 — `app.js`

```javascript
const express = require('express');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const pool = new Pool({
  host:     process.env.DB_HOST,
  user:     process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME || 'notesdb',
  port:     5432,
  ssl:      process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
});

async function initDB() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS notes (
      id         SERIAL PRIMARY KEY,
      title      VARCHAR(255) NOT NULL,
      content    TEXT,
      version    VARCHAR(10) DEFAULT 'v1',
      created_at TIMESTAMP DEFAULT NOW()
    )
  `);
  console.log('DB initialised');
}

const html = (body, version) => `
<!DOCTYPE html><html>
<head>
  <title>Notes App ${version}</title>
  <meta charset="utf-8">
  <style>
    * { box-sizing:border-box; margin:0; padding:0 }
    body { font-family:system-ui,sans-serif; background:#f5f5f5; color:#1a1a1a }
    .header { background:${version === 'v2' ? '#0f6e56' : '#185fa5'}; color:#fff; padding:1rem 2rem; display:flex; align-items:center; gap:12px }
    .badge { background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:20px; font-size:13px }
    .container { max-width:720px; margin:2rem auto; padding:0 1rem }
    .card { background:#fff; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; border:1px solid #e0e0e0 }
    input,textarea { width:100%; padding:10px 12px; border:1px solid #ddd; border-radius:8px; font-size:14px; font-family:inherit; margin-bottom:10px }
    textarea { min-height:80px; resize:vertical }
    button { background:${version === 'v2' ? '#0f6e56' : '#185fa5'}; color:#fff; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-size:14px }
    button:hover { opacity:0.85 }
    .note-card { border-left:4px solid ${version === 'v2' ? '#0f6e56' : '#185fa5'}; padding:1rem; margin-bottom:1rem; background:#fafafa; border-radius:0 8px 8px 0 }
    .note-meta { font-size:12px; color:#888; margin-top:6px }
    .version-badge { display:inline-block; font-size:11px; padding:2px 8px; border-radius:10px; margin-left:8px; background:${version === 'v2' ? '#e1f5ee' : '#e6f1fb'}; color:${version === 'v2' ? '#0f6e56' : '#185fa5'} }
    .delete-btn { float:right; background:#e53e3e; padding:4px 12px; font-size:12px }
    h2 { font-size:18px; margin-bottom:1rem; font-weight:500 }
    .env-info { background:${version === 'v2' ? '#e1f5ee' : '#e6f1fb'}; padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:1rem }
  </style>
</head>
<body>
  <div class="header">
    <strong>Notes App</strong>
    <span class="badge">${version} — ${version === 'v2' ? 'GREEN environment' : 'BLUE environment'}</span>
  </div>
  <div class="container">${body}</div>
</body></html>`;

app.get('/health', (req, res) => {
  res.json({ status: 'ok', version: process.env.APP_VERSION || 'v1', env: process.env.ENV_COLOR || 'blue' });
});

app.get('/', async (req, res) => {
  const version = process.env.APP_VERSION || 'v1';
  try {
    const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
    const noteCards = rows.map(n => `
      <div class="note-card">
        <strong>${n.title}</strong>
        <span class="version-badge">written by ${n.version}</span>
        <form method="POST" action="/delete/${n.id}" style="display:inline;float:right">
          <button class="delete-btn" type="submit">Delete</button>
        </form>
        <p style="margin-top:8px;font-size:14px">${n.content || ''}</p>
        <div class="note-meta">ID: ${n.id} · ${new Date(n.created_at).toLocaleString()}</div>
      </div>`).join('');
    res.send(html(`
      <div class="env-info">
        Environment: <strong>${process.env.ENV_COLOR || 'blue'}</strong> &nbsp;|&nbsp;
        Version: <strong>${version}</strong> &nbsp;|&nbsp;
        DB: <strong>${process.env.DB_HOST?.split('.')[0] || 'localhost'}</strong>
      </div>
      <div class="card">
        <h2>Add a note</h2>
        <form method="POST" action="/notes">
          <input name="title" placeholder="Title" required />
          <textarea name="content" placeholder="Content..."></textarea>
          <button type="submit">Save Note</button>
        </form>
      </div>
      <div class="card">
        <h2>All Notes (${rows.length})</h2>
        ${noteCards || '<p style="color:#888;font-size:14px">No notes yet. Add one above!</p>'}
      </div>`, version));
  } catch (err) {
    res.status(500).send(`<pre style="padding:2rem">DB Error: ${err.message}\n\nCheck that all 7 environment properties are set in EB → Configuration → Software.</pre>`);
  }
});

app.post('/notes', async (req, res) => {
  const { title, content } = req.body;
  const version = process.env.APP_VERSION || 'v1';
  await pool.query('INSERT INTO notes (title, content, version) VALUES ($1, $2, $3)', [title, content, version]);
  res.redirect('/');
});

app.post('/delete/:id', async (req, res) => {
  await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
  res.redirect('/');
});

app.get('/notes', async (req, res) => {
  const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
  res.json({ version: process.env.APP_VERSION || 'v1', env: process.env.ENV_COLOR || 'blue', count: rows.length, notes: rows });
});

// ✅ CRITICAL: Must use process.env.PORT — EB sets this to 8080
// nginx proxies port 80 → 8080. Hardcoding 3000 causes 502 Bad Gateway.
const PORT = process.env.PORT || 8080;
initDB()
  .then(() => app.listen(PORT, () => console.log(`Notes app running on :${PORT}`)))
  .catch(err => { console.error('Startup failed:', err); process.exit(1); });
```

---

### File 2 — `package.json`

```json
{
  "name": "notes-app",
  "version": "1.0.0",
  "description": "Blue-Green deployment demo",
  "main": "app.js",
  "scripts": { "start": "node app.js" },
  "engines": { "node": ">=18.0.0" },
  "dependencies": {
    "dotenv": "^16.0.0",
    "express": "^4.18.0",
    "pg": "^8.11.0"
  }
}
```
### File 4 of 4 — `.ebignore`

```
.env
node_modules/
.git/
*.log
```

---


---

### ZIP the files

Select **only these 2 files** (NOT the folder, NOT a `.env` file) → right-click → Compress to ZIP →
name it `notes-app-v1.zip`

```
notes-app-v1.zip
  ├── app.js
  └── package.json
```

> ❌ Do NOT include `node_modules/`, `.env`, or any other files.
> EB runs `npm install` automatically on the server.
> A `.env` file will silently override your EB environment properties and break the app.

---

## PART 1 — Create the RDS Database

> Do this first. It takes ~5 minutes to become available.

1. AWS Console → search **RDS** → **Create database**
2. **Creation method:** Standard create
3. **Engine:** PostgreSQL
4. **Template:** Dev/Test
5. **Instance configuration:**
   - Select **Burstable classes (includes t classes)**
   - Instance type: `db.t3.micro`
6. **Settings:**
   - DB instance identifier: `notes-db`
   - Master username: `notesadmin`
   - Master password: `YourPass123!`
   - Confirm password: `YourPass123!`
7. **Initial database name:** `notesdb`

   > ⚠️ **Set this field.** If left blank, RDS creates no database and the app will fail
   > with `database "notesdb" does not exist` even if connectivity is fine.

8. **Storage:**
   - Storage type: `gp2`
   - Allocated storage: `20` GiB
   - Uncheck **Enable storage autoscaling**
9. **Connectivity:**
   - VPC: default
   - Public access: **Yes**
   - VPC security group: **Create new**
   - New security group name: `notes-db-sg`
   - Availability zone: No preference
10. **Database authentication:** Password authentication
11. Click **Create database** → wait ~5 minutes for status **Available**

---

### Add the inbound rule to the security group

After the database is created, open port 5432:

1. **EC2** → **Security Groups** → find `notes-db-sg` → click it
2. **Inbound rules** → **Edit inbound rules** → **Add rule**

| Field | Value |
|---|---|
| Type | PostgreSQL |
| Protocol | TCP (auto-filled) |
| Port | 5432 (auto-filled) |
| Source | Anywhere-IPv4 `0.0.0.0/0` |

3. Click **Save rules**

> ⚠️ Without this rule the app will fail with `ETIMEDOUT` on port 5432 — even if your
> VPC and subnets are correct.

---

### Copy the RDS endpoint

1. **RDS** → **Databases** → click `notes-db`
2. **Connectivity & security** tab → copy the **Endpoint**
3. Looks like: `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com`
4. Save this — you paste it as `DB_HOST` in the EB wizard

---

### Verify the database exists (and create it manually if needed)

Do this before deploying to EB — it saves you from debugging a 502 later.

**Step 1 — Open AWS CloudShell**

Click the CloudShell icon (`>_`) in the top navigation bar of the AWS Console.

**Step 2 — Install the PostgreSQL client**

```bash
sudo yum install -y postgresql15
```

**Step 3 — Connect to RDS**

Replace `YOUR_RDS_ENDPOINT` with your actual endpoint:

```bash
psql -h YOUR_RDS_ENDPOINT -U notesadmin -d postgres
```

Enter your password when prompted: `YourPass123!`

**Step 4 — Check if the database exists**

```sql
SELECT datname FROM pg_database;
```

You should see `notesdb` in the list. If you do, type `\q` to exit and proceed to Part 2.

```
   datname
-----------
 notesdb        <- should be here
 postgres
 template1
 template0
```

**Step 5 — If `notesdb` is NOT in the list, create it manually**

```sql
CREATE DATABASE notesdb;
```

You should see `CREATE DATABASE`. Verify it was created:

```sql
SELECT datname FROM pg_database;
```

Then exit psql:

```sql
\q
```

> You can also do this without entering the interactive prompt — one single command:
> ```bash
> psql -h YOUR_RDS_ENDPOINT -U notesadmin -d postgres -c "CREATE DATABASE notesdb;"
> ```

---

## PART 2 — Deploy the BLUE Environment (v1)

**Elastic Beanstalk** → **Create application**

---

### Step 1 — Configure environment

| Field | Value |
|---|---|
| Environment tier | Web server environment |
| Application name | `notes-app` |
| Environment name | `notes-blue` |
| Domain | Leave blank (auto-generated) |
| Platform | Managed platform → Node.js |
| Platform branch | Node.js 20 running on 64bit Amazon Linux 2023 |
| Platform version | Latest recommended |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | Choose file → `notes-app-v1.zip` |
| Presets | **Single instance (free tier eligible)** |

> ℹ️ Node.js 18 has been retired from the EB platform list. Use **Node.js 20** —
> it is fully compatible with this app.

Click **Next**

---

### Step 2 — Configure service access

| Field | Value |
|---|---|
| Service role | Create and use new service role |
| EC2 key pair | Leave blank |
| EC2 instance profile | Select existing or create one (see note below) |

> If no instance profile exists in the dropdown, create one:
> **IAM** → **Roles** → **Create role** → **AWS service** → **EC2**
> → attach policy `AWSElasticBeanstalkWebTier`
> → name it `aws-elasticbeanstalk-ec2-role` → **Create role**
> → come back and select it here

Click **Next**

---

### Step 3 — Set up networking, database, and tags

| Field | Value |
|---|---|
| VPC | Select the default VPC |
| Public IP address | **Enabled** |
| Instance subnets | Tick any one subnet |
| Database | Leave **Enable database unchecked** — RDS was already created in Part 1 |

Click **Next**

---

### Step 4 — Configure instance traffic and scaling

| Field | Value |
|---|---|
| EC2 security groups | Leave blank (EB creates one automatically) |
| Environment type | Single instance |
| Instance types | `t3.micro` |

Scroll down to **Environment properties** — add all 7:

| Name | Value |
|---|---|
| `APP_VERSION` | `v1` |
| `ENV_COLOR` | `blue` |
| `DB_HOST` | `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com` ← your exact endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

> ⚠️ Copy the `DB_HOST` endpoint exactly — no `https://`, no trailing slash,
> no extra spaces. Even one wrong character causes a timeout.

Click **Next**

---

### Step 5 — Configure updates, monitoring, and logging

Leave everything as default. Click **Next**

---

### Step 6 — Review

Confirm:
- Environment name: `notes-blue`
- Platform: Node.js 20
- ZIP file listed under application code
- 7 environment properties visible

Click **Submit** → wait 3–5 minutes → health shows **OK** (green tick)

---

### Verify Blue is working

1. Click the URL at the top of the environment page
2. You should see the app with a **blue header** — "v1 — BLUE environment"
3. Add 2–3 notes to confirm the database is saving data

---

## PART 3 — Make Your v2 Change

Open `app.js` on your computer. Find this line (~line 63):

```javascript
<strong>Notes App</strong>
```

Change it to:

```javascript
<strong>Notes App ✦ v2</strong>
```

Save the file. Select the same 2 files again, zip them into `notes-app-v2.zip`.

---

## PART 4 — Deploy the GREEN Environment (v2)

**Elastic Beanstalk** → click `notes-app` → **Create a new environment**

Follow the same 6 steps as Part 2 with only these differences:

### Step 1 — Configure environment

| Field | Value |
|---|---|
| Environment name | `notes-green` ← changed |
| Version label | `v2` ← changed |
| Local file | `notes-app-v2.zip` ← changed |

Everything else identical. Click **Next** through Steps 2 and 3.

### Step 4 — Environment properties

Same 7 properties but change two values:

| Name | Value |
|---|---|
| `APP_VERSION` | `v2` ← changed |
| `ENV_COLOR` | `green` ← changed |
| `DB_HOST` | same RDS endpoint as Blue |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next** → **Next** → **Submit**. Wait 3–5 minutes for Green to launch.

---

### Verify Green is working

1. Click the Green environment URL
2. You should see a **green header** — "v2 — GREEN environment"
3. All notes you added on Blue are visible here — same RDS database

---

## PART 5 — The CNAME Swap

### Option A — Console (Recommended)

No CLI needed. Do it directly in the AWS Console:

1. **Elastic Beanstalk** → `notes-app` → click `notes-blue`
2. Click **Actions** → **Swap environment domain**
3. In the dialog, select `notes-green` as the destination environment
4. Click **Swap**

The swap is instant. No redeployment happens.

### Option B — EB CLI

If you prefer the terminal:

**Install EB CLI**
```bash
pip install awsebcli --break-system-packages
```

**Configure AWS credentials**
```bash
aws configure
# AWS Access Key ID: <your key>
# AWS Secret Access Key: <your secret>
# Default region: us-east-1
# Default output format: json
```

**Initialise the EB CLI**
```bash
cd path/to/notes-app

eb init notes-app --platform node.js-20 --region us-east-1
```

> ⚠️ Use `node.js-20` (short form). Node.js 18 has been retired from the platform list.

**Run the swap**
```bash
eb swap notes-blue --destination_name notes-green
```

> ⚠️ Use `--destination_name` with an **underscore**, not a hyphen.
> `--destination-name` throws an `unrecognized arguments` error.

---

### What just happened

```
BEFORE swap:
  notes-blue.xxxxxx.elasticbeanstalk.com  → serves v1 (blue header)
  notes-green.xxxxxx.elasticbeanstalk.com → serves v2 (green header)

AFTER swap:
  notes-blue.xxxxxx.elasticbeanstalk.com  → now serves v2 (green header) ✓
  notes-green.xxxxxx.elasticbeanstalk.com → now serves v1 (blue header)
```

Open the Blue URL — it now shows the green header and "v2". Zero downtime.

---

## PART 6 — Rollback

### Option A — Console

1. **Elastic Beanstalk** → `notes-app` → click `notes-green`
2. **Actions** → **Swap environment domain**
3. Select `notes-blue` as the destination → **Swap**

### Option B — CLI

```bash
eb swap notes-green --destination_name notes-blue
```

Open the Blue URL — it shows the blue header and v1 again.

---

## PART 7 — Teardown

Always do this when finished. These resources charge by the hour.

### Terminate EB environments

1. **Elastic Beanstalk** → `notes-app`
2. Click `notes-blue` → **Actions** → **Terminate environment** → confirm
3. Click `notes-green` → **Actions** → **Terminate environment** → confirm
4. Once both terminated → **Actions** → **Delete application** → confirm

### Delete RDS

1. **RDS** → **Databases** → select `notes-db`
2. **Actions** → **Delete**
3. Uncheck "Create final snapshot"
4. Check "I acknowledge..."
5. Type `delete me` → **Delete**

### Clean up security group

1. **EC2** → **Security Groups**
2. Select `notes-db-sg` → **Actions** → **Delete security groups**

---

## What to Observe During the Swap

Open two browser tabs before running the swap:

- **Tab 1:** `notes-blue.xxxxxx.elasticbeanstalk.com/health`
  → shows `{"status":"ok","version":"v1","env":"blue"}`

- **Tab 2:** `notes-green.xxxxxx.elasticbeanstalk.com/health`
  → shows `{"status":"ok","version":"v2","env":"green"}`

Run `eb swap`. Refresh Tab 1 — it now shows `{"version":"v2","env":"green"}`.
The header colour on Tab 1 changes from blue to green.
Notes are still there — the database never moved.

---

## Troubleshooting

| Problem | Root Cause | Fix |
|---|---|---|
| 502 Bad Gateway | App not listening on port 8080 | Ensure `app.listen(process.env.PORT \|\| 8080)` — never hardcode 3000 |
| `ETIMEDOUT` on port 5432 | RDS security group missing inbound rule | EC2 → Security Groups → `notes-db-sg` → add PostgreSQL / 5432 / 0.0.0.0/0 |
| `database "notesdb" does not exist` | Initial DB name not set during RDS creation | Set **Initial database name** to `notesdb` when creating RDS, or connect via psql and run `CREATE DATABASE notesdb;` |
| App crashes silently, no new log lines | `.env` file in zip overriding EB env properties | Remove `.env` from zip entirely — only include `app.js` and `package.json` |
| `DB_HOST` wrong value | Copied placeholder instead of real endpoint | Go to RDS → `notes-db` → Connectivity & security → copy endpoint exactly |
| `eb init` platform not found | Node.js 18 retired | Use `--platform node.js-20` |
| `eb swap` unrecognized argument | Wrong flag syntax | Use `--destination_name` (underscore, not hyphen) |
| Environment stuck in Degraded/Severe | Various — check logs | EB → Logs → Request last 100 lines → read `web.stdout.log` |

---

## Cost for This Exercise

| Resource | Rate | 3 hours |
|---|---|---|
| 2x EB t3.micro instances | ~$0.02/hr each | ~$0.12 |
| RDS db.t3.micro | ~$0.02/hr | ~$0.06 |
| **Total** | | **~$0.18** |

Always run Part 7 (teardown) when done.


# Elastic Beanstalk Deployment Strategies Lab
### Console-based guide — step by step, no CLI required

---

## What You Will Build

The same Notes Manager app from the Blue-Green lab (Node.js + Express + PostgreSQL on RDS),
reused to practice every Elastic Beanstalk deployment strategy one by one.

You will deploy **v1**, make a small visible change for **v2**, then update the environment
using each strategy and watch exactly what happens to your instances and your users.

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT STRATEGIES OVERVIEW                  │
├─────────────────────┬────────────┬─────────────┬────────────────┤
│ Strategy            │ Downtime   │ Extra Cost  │ Rollback       │
├─────────────────────┼────────────┼─────────────┼────────────────┤
│ All at Once         │ YES        │ None        │ Manual redeploy│
│ Rolling             │ No         │ None        │ Manual redeploy│
│ Rolling w/ Add'l    │ No         │ Small/temp  │ Manual redeploy│
│ Immutable           │ No         │ High/temp   │ Auto-terminate │
└─────────────────────┴────────────┴─────────────┴────────────────┘
```

> **How to use this lab**
> Each strategy is its own independent section (Parts 3–6).
> You do Part 1 (RDS) and Part 2 (app files) once. Then you work through each strategy
> in order, or jump to the one you want to practise.

---

## Before You Start — Have These Ready

- AWS account with console access
- About 2 hours total (30 min per strategy)
- No CLI, no terminal, no local tools needed — everything is done in the AWS Console

---

## The App Files

You need two versions of the app. Create a folder called `notes-app` on your computer.

> ⚠️ **CRITICAL: Do NOT include a `.env` file in any zip.**
> Elastic Beanstalk injects environment variables directly into the process.
> A `.env` file will override your EB configuration and break the app silently.

---

### `app.js` — Version 1

This is the **original version** you deploy first. It has a blue theme with a banner that
clearly says "PRE-UPDATE — Version 1 is live". When you see this, you know the update has
not happened yet (or has been rolled back).

```javascript
const express = require('express');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const pool = new Pool({
  host:     process.env.DB_HOST,
  user:     process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME || 'notesdb',
  port:     5432,
  ssl:      process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
});

async function initDB() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS notes (
      id         SERIAL PRIMARY KEY,
      title      VARCHAR(255) NOT NULL,
      content    TEXT,
      version    VARCHAR(10) DEFAULT 'v1',
      created_at TIMESTAMP DEFAULT NOW()
    )
  `);
  console.log('DB initialised');
}

const html = (body) => `
<!DOCTYPE html><html>
<head>
  <title>Notes App — v1</title>
  <meta charset="utf-8">
  <style>
    * { box-sizing:border-box; margin:0; padding:0 }
    body { font-family:system-ui,sans-serif; background:#eef4fb; color:#1a1a1a }

    /* ── VERSION BANNER ── */
    .version-banner {
      background:#1a56a0;
      color:#fff;
      text-align:center;
      padding:14px 20px;
      font-size:17px;
      font-weight:700;
      letter-spacing:0.5px;
      border-bottom:4px solid #0d3d78;
    }
    .version-banner .tag {
      display:inline-block;
      background:#fff;
      color:#1a56a0;
      font-size:12px;
      font-weight:800;
      padding:3px 10px;
      border-radius:20px;
      margin-left:10px;
      letter-spacing:1px;
      text-transform:uppercase;
      vertical-align:middle;
    }

    .header { background:#185fa5; color:#fff; padding:0.75rem 2rem; display:flex; align-items:center; gap:12px }
    .header-badge { background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:20px; font-size:13px }
    .container { max-width:720px; margin:2rem auto; padding:0 1rem }
    .card { background:#fff; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; border:1px solid #cde0f5 }
    .info-bar { background:#ddeeff; border:1px solid #b0ccee; border-radius:8px; padding:10px 14px; font-size:13px; margin-bottom:1.2rem; color:#1a3a5c }
    input,textarea { width:100%; padding:10px 12px; border:1px solid #c5d9ef; border-radius:8px; font-size:14px; font-family:inherit; margin-bottom:10px }
    textarea { min-height:80px; resize:vertical }
    button { background:#185fa5; color:#fff; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-size:14px }
    button:hover { opacity:0.85 }
    .note-card { border-left:5px solid #185fa5; padding:1rem; margin-bottom:1rem; background:#f4f9ff; border-radius:0 8px 8px 0 }
    .note-meta { font-size:12px; color:#7a90a8; margin-top:6px }
    .ver-chip { display:inline-block; font-size:11px; padding:2px 8px; border-radius:10px; margin-left:8px; background:#d6eaff; color:#185fa5; font-weight:600 }
    .delete-btn { float:right; background:#e53e3e; padding:4px 12px; font-size:12px; border-radius:6px }
    h2 { font-size:17px; margin-bottom:1rem; font-weight:600; color:#1a3a5c }
  </style>
</head>
<body>

  <!-- ★ VERSION BANNER — the first thing anyone sees ★ -->
  <div class="version-banner">
    🔵 PRE-UPDATE &nbsp;—&nbsp; Version 1 is live
    <span class="tag">v1</span>
  </div>

  <div class="header">
    <strong>Notes App</strong>
    <span class="header-badge">Deployment Strategies Demo</span>
  </div>
  <div class="container">${body}</div>
</body></html>`;

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    version: 'v1',
    banner: 'PRE-UPDATE — Version 1 is live',
    strategy: process.env.DEPLOY_STRATEGY || 'unknown',
    instance: process.env.HOSTNAME || 'unknown'
  });
});

app.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
    const noteCards = rows.map(n => `
      <div class="note-card">
        <strong>${n.title}</strong>
        <span class="ver-chip">saved by ${n.version}</span>
        <form method="POST" action="/delete/${n.id}" style="display:inline;float:right">
          <button class="delete-btn" type="submit">Delete</button>
        </form>
        <p style="margin-top:8px;font-size:14px">${n.content || ''}</p>
        <div class="note-meta">ID: ${n.id} · ${new Date(n.created_at).toLocaleString()}</div>
      </div>`).join('');
    res.send(html(`
      <div class="info-bar">
        🖥️ Instance: <strong>${process.env.HOSTNAME || 'unknown'}</strong>
        &nbsp;|&nbsp; Strategy: <strong>${process.env.DEPLOY_STRATEGY || 'unknown'}</strong>
        &nbsp;|&nbsp; Version: <strong>v1</strong>
      </div>
      <div class="card">
        <h2>Add a note</h2>
        <form method="POST" action="/notes">
          <input name="title" placeholder="Title" required />
          <textarea name="content" placeholder="Content..."></textarea>
          <button type="submit">Save Note</button>
        </form>
      </div>
      <div class="card">
        <h2>All Notes (${rows.length})</h2>
        ${noteCards || '<p style="color:#7a90a8;font-size:14px">No notes yet. Add one above!</p>'}
      </div>`));
  } catch (err) {
    res.status(500).send(`<pre style="padding:2rem">DB Error: ${err.message}\n\nCheck all 8 environment properties are set in EB → Configuration → Software.</pre>`);
  }
});

app.post('/notes', async (req, res) => {
  const { title, content } = req.body;
  await pool.query('INSERT INTO notes (title, content, version) VALUES ($1, $2, $3)', [title, content, 'v1']);
  res.redirect('/');
});

app.post('/delete/:id', async (req, res) => {
  await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
  res.redirect('/');
});

app.get('/notes', async (req, res) => {
  const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
  res.json({ version: 'v1', count: rows.length, notes: rows });
});

const PORT = process.env.PORT || 8080;
initDB()
  .then(() => app.listen(PORT, () => console.log('Notes app v1 running on :' + PORT)))
  .catch(err => { console.error('Startup failed:', err); process.exit(1); });
```

---

### `app.js` — Version 2

This is the **updated version** you deploy to trigger the strategy. It has a green theme
with a banner that clearly says "POST-UPDATE — Version 2 deployed successfully". The moment
you see this on any instance, the update has reached that instance.

```javascript
const express = require('express');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const pool = new Pool({
  host:     process.env.DB_HOST,
  user:     process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME || 'notesdb',
  port:     5432,
  ssl:      process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
});

async function initDB() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS notes (
      id         SERIAL PRIMARY KEY,
      title      VARCHAR(255) NOT NULL,
      content    TEXT,
      version    VARCHAR(10) DEFAULT 'v1',
      created_at TIMESTAMP DEFAULT NOW()
    )
  `);
  console.log('DB initialised');
}

const html = (body) => `
<!DOCTYPE html><html>
<head>
  <title>Notes App — v2</title>
  <meta charset="utf-8">
  <style>
    * { box-sizing:border-box; margin:0; padding:0 }
    body { font-family:system-ui,sans-serif; background:#edfbf4; color:#1a1a1a }

    /* ── VERSION BANNER ── */
    .version-banner {
      background:#0f6e56;
      color:#fff;
      text-align:center;
      padding:14px 20px;
      font-size:17px;
      font-weight:700;
      letter-spacing:0.5px;
      border-bottom:4px solid #094d3b;
    }
    .version-banner .tag {
      display:inline-block;
      background:#fff;
      color:#0f6e56;
      font-size:12px;
      font-weight:800;
      padding:3px 10px;
      border-radius:20px;
      margin-left:10px;
      letter-spacing:1px;
      text-transform:uppercase;
      vertical-align:middle;
    }

    .header { background:#0f6e56; color:#fff; padding:0.75rem 2rem; display:flex; align-items:center; gap:12px }
    .header-badge { background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:20px; font-size:13px }
    .container { max-width:720px; margin:2rem auto; padding:0 1rem }
    .card { background:#fff; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; border:1px solid #b2e8d4 }
    .info-bar { background:#d4f5e6; border:1px solid #8dd4b4; border-radius:8px; padding:10px 14px; font-size:13px; margin-bottom:1.2rem; color:#0a3d2b }
    input,textarea { width:100%; padding:10px 12px; border:1px solid #9dd6be; border-radius:8px; font-size:14px; font-family:inherit; margin-bottom:10px }
    textarea { min-height:80px; resize:vertical }
    button { background:#0f6e56; color:#fff; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-size:14px }
    button:hover { opacity:0.85 }
    .note-card { border-left:5px solid #0f6e56; padding:1rem; margin-bottom:1rem; background:#f0fdf6; border-radius:0 8px 8px 0 }
    .note-meta { font-size:12px; color:#5a8a74; margin-top:6px }
    .ver-chip { display:inline-block; font-size:11px; padding:2px 8px; border-radius:10px; margin-left:8px; background:#c2f0dc; color:#0f6e56; font-weight:600 }
    .delete-btn { float:right; background:#e53e3e; padding:4px 12px; font-size:12px; border-radius:6px }
    h2 { font-size:17px; margin-bottom:1rem; font-weight:600; color:#0a3d2b }
  </style>
</head>
<body>

  <!-- ★ VERSION BANNER — immediately shows this instance has been updated ★ -->
  <div class="version-banner">
    🟢 POST-UPDATE &nbsp;—&nbsp; Version 2 deployed successfully ✦
    <span class="tag">v2</span>
  </div>

  <div class="header">
    <strong>Notes App ✦ v2</strong>
    <span class="header-badge">Deployment Strategies Demo</span>
  </div>
  <div class="container">${body}</div>
</body></html>`;

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    version: 'v2',
    banner: 'POST-UPDATE — Version 2 deployed successfully',
    strategy: process.env.DEPLOY_STRATEGY || 'unknown',
    instance: process.env.HOSTNAME || 'unknown'
  });
});

app.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
    const noteCards = rows.map(n => `
      <div class="note-card">
        <strong>${n.title}</strong>
        <span class="ver-chip">saved by ${n.version}</span>
        <form method="POST" action="/delete/${n.id}" style="display:inline;float:right">
          <button class="delete-btn" type="submit">Delete</button>
        </form>
        <p style="margin-top:8px;font-size:14px">${n.content || ''}</p>
        <div class="note-meta">ID: ${n.id} · ${new Date(n.created_at).toLocaleString()}</div>
      </div>`).join('');
    res.send(html(`
      <div class="info-bar">
        🖥️ Instance: <strong>${process.env.HOSTNAME || 'unknown'}</strong>
        &nbsp;|&nbsp; Strategy: <strong>${process.env.DEPLOY_STRATEGY || 'unknown'}</strong>
        &nbsp;|&nbsp; Version: <strong>v2</strong>
      </div>
      <div class="card">
        <h2>Add a note</h2>
        <form method="POST" action="/notes">
          <input name="title" placeholder="Title" required />
          <textarea name="content" placeholder="Content..."></textarea>
          <button type="submit">Save Note</button>
        </form>
      </div>
      <div class="card">
        <h2>All Notes (${rows.length})</h2>
        ${noteCards || '<p style="color:#5a8a74;font-size:14px">No notes yet. Add one above!</p>'}
      </div>`));
  } catch (err) {
    res.status(500).send(`<pre style="padding:2rem">DB Error: ${err.message}\n\nCheck all 8 environment properties are set in EB → Configuration → Software.</pre>`);
  }
});

app.post('/notes', async (req, res) => {
  const { title, content } = req.body;
  await pool.query('INSERT INTO notes (title, content, version) VALUES ($1, $2, $3)', [title, content, 'v2']);
  res.redirect('/');
});

app.post('/delete/:id', async (req, res) => {
  await pool.query('DELETE FROM notes WHERE id = $1', [req.params.id]);
  res.redirect('/');
});

app.get('/notes', async (req, res) => {
  const { rows } = await pool.query('SELECT * FROM notes ORDER BY created_at DESC');
  res.json({ version: 'v2', count: rows.length, notes: rows });
});

const PORT = process.env.PORT || 8080;
initDB()
  .then(() => app.listen(PORT, () => console.log('Notes app v2 running on :' + PORT)))
  .catch(err => { console.error('Startup failed:', err); process.exit(1); });
```

---

### `package.json` (same for both versions)

```json
{
  "name": "notes-app",
  "version": "1.0.0",
  "description": "EB deployment strategies demo",
  "main": "app.js",
  "scripts": { "start": "node app.js" },
  "engines": { "node": ">=18.0.0" },
  "dependencies": {
    "dotenv": "^16.0.0",
    "express": "^4.18.0",
    "pg": "^8.11.0"
  }
}
```

---

### What the banners look like

| When you see this... | It means... |
|---|---|
| 🔵 **PRE-UPDATE — Version 1 is live** (blue page) | This instance has NOT been updated yet |
| 🟢 **POST-UPDATE — Version 2 deployed successfully** (green page) | This instance HAS been updated |

During a **Rolling** or **Rolling with Additional Batch** deployment, keep refreshing the
app URL. You will catch moments where one refresh shows the blue banner (hit a v1 instance)
and the very next refresh shows the green banner (hit a v2 instance). That mixed-version
window is what makes those strategies different from Immutable.

During **All at Once**, you will see the blue banner, then errors or a blank page, then
the green banner — the downtime window happened in between.

During **Immutable**, you will see the blue banner 100% of the time right up until the
cutover, then the green banner 100% of the time after. No mixing.

---

### ZIP the files

You need two ZIP files. Each contains **only 2 files** — `app.js` and `package.json`.

```
notes-app-v1.zip          notes-app-v2.zip
  ├── app.js                ├── app.js   (with green header + v2 text)
  └── package.json          └── package.json
```

> ❌ Do NOT include `node_modules/`, `.env`, or any other files.
> EB runs `npm install` automatically on the server.

---

## PART 1 — Create the RDS Database

> Do this once. All four strategy environments share the same database.
> It takes ~5 minutes to become available. Start it first, then read ahead while you wait.

### Step 1 — Create the database

1. AWS Console → search **RDS** → click **Create database**
2. **Creation method:** Standard create
3. **Engine:** PostgreSQL
4. **Template:** Dev/Test
5. **Instance configuration:**
   - Select **Burstable classes (includes t classes)**
   - Instance type: `db.t3.micro`
6. **Settings:**
   - DB instance identifier: `notes-db`
   - Master username: `notesadmin`
   - Master password: `YourPass123!`
   - Confirm password: `YourPass123!`
7. **Initial database name:** `notesdb`

   > ⚠️ You MUST fill this field. If left blank, RDS creates no database and
   > the app fails with `database "notesdb" does not exist`.

8. **Storage:**
   - Storage type: `gp2`
   - Allocated storage: `20` GiB
   - Uncheck **Enable storage autoscaling**
9. **Connectivity:**
   - VPC: default
   - Public access: **Yes**
   - VPC security group: **Create new**
   - New security group name: `notes-db-sg`
   - Availability zone: No preference
10. **Database authentication:** Password authentication
11. Click **Create database** → wait ~5 minutes for status **Available**

---

### Step 2 — Open port 5432 on the security group

1. **EC2** → **Security Groups** → find `notes-db-sg` → click it
2. **Inbound rules** → **Edit inbound rules** → **Add rule**

| Field | Value |
|---|---|
| Type | PostgreSQL |
| Protocol | TCP (auto-filled) |
| Port | 5432 (auto-filled) |
| Source | Anywhere-IPv4 `0.0.0.0/0` |

3. Click **Save rules**

> ⚠️ Without this rule the app will fail with `ETIMEDOUT` on port 5432 every time.

---

### Step 3 — Copy the RDS endpoint

1. **RDS** → **Databases** → click `notes-db`
2. **Connectivity & security** tab → copy the **Endpoint**
3. It looks like: `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com`
4. Save this somewhere — you will paste it as `DB_HOST` in every environment you create

---

### Step 4 — Verify the database exists

1. In the AWS Console top nav bar, click the **CloudShell icon** (`>_`)
2. A terminal opens in your browser — no local setup needed
3. Run:
   ```bash
   sudo yum install -y postgresql15
   ```
4. Connect to RDS (replace `YOUR_RDS_ENDPOINT` with your actual endpoint):
   ```bash
   psql -h YOUR_RDS_ENDPOINT -U notesadmin -d postgres
   ```
   Enter password: `YourPass123!`
5. Check the database exists:
   ```sql
   SELECT datname FROM pg_database;
   ```
   You should see `notesdb` in the list. If you do, type `\q` and proceed.

6. If `notesdb` is NOT there, create it:
   ```sql
   CREATE DATABASE notesdb;
   \q
   ```

---

## PART 2 — Create the Shared IAM Instance Profile

> You only need to do this once. Every EB environment uses the same role.

If you completed the Blue-Green lab, this role already exists — skip to Part 3.

1. AWS Console → **IAM** → **Roles** → **Create role**
2. **Trusted entity type:** AWS service
3. **Use case:** EC2
4. Click **Next**
5. Search for and attach: `AWSElasticBeanstalkWebTier`
6. Click **Next**
7. Role name: `aws-elasticbeanstalk-ec2-role`
8. Click **Create role**

---

## PART 3 — Strategy 1: All at Once

### What this strategy does

Every instance is updated **at the same time**. While the update is happening, your
application is briefly offline. This is the fastest and cheapest method but causes downtime.

```
BEFORE:   [v1] [v1] [v1]   ← all three instances serving traffic

DURING:   [ ↓] [ ↓] [ ↓]   ← ALL instances updating simultaneously
          (app is unreachable for ~1–2 minutes here)

AFTER:    [v2] [v2] [v2]   ← all three instances running the new version
```

**When to use it:** Development and test environments only. Never in production.

---

### Step 1 — Create the application

1. AWS Console → search **Elastic Beanstalk** → click **Create application**

| Field | Value |
|---|---|
| Environment tier | Web server environment |
| Application name | `notes-deployment-strategies` |
| Environment name | `notes-all-at-once` |
| Domain | Leave blank (auto-generated) |
| Platform | Managed platform → Node.js |
| Platform branch | Node.js 20 running on 64bit Amazon Linux 2023 |
| Platform version | Latest recommended |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | Choose file → `notes-app-v1.zip` |
| Presets | **High availability** |

> ⚠️ You MUST select **High availability** here. This creates a load balancer and
> an Auto Scaling Group with multiple instances, which is required to demonstrate
> rolling strategies properly. "Single instance" only gives you one EC2 instance.

Click **Next**

---

### Step 2 — Service access

| Field | Value |
|---|---|
| Service role | Create and use new service role |
| EC2 key pair | Leave blank |
| EC2 instance profile | `aws-elasticbeanstalk-ec2-role` |

Click **Next**

---

### Step 3 — Networking, database, and tags

| Field | Value |
|---|---|
| VPC | Select the default VPC |
| Public IP address | **Enabled** |
| Instance subnets | Tick **at least two** subnets (required for load balancer) |
| Database | Leave **Enable database unchecked** |

Click **Next**

---

### Step 4 — Instance traffic and scaling

| Field | Value |
|---|---|
| Load balancer type | Application Load Balancer |
| Minimum instances | `3` |
| Maximum instances | `3` |
| Instance types | `t3.micro` |

> Setting both Min and Max to 3 gives you exactly 3 instances so you can clearly
> see batch behaviour during deployments.

Scroll down to **Deployment preferences** and set:

| Field | Value |
|---|---|
| Deployment policy | **All at once** |

Scroll down to **Environment properties** — add all 8:

| Name | Value |
|---|---|
| `PORT` | `8080` |
| `APP_VERSION` | `v1` |
| `DEPLOY_STRATEGY` | `all-at-once` |
| `DB_HOST` | `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com` ← your endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next**

---

### Step 5 — Updates, monitoring, and logging

Leave everything as default. Click **Next**

---

### Step 6 — Review and submit

Confirm:
- Environment name: `notes-all-at-once`
- Deployment policy: All at once
- 3 instances minimum and maximum
- 8 environment properties visible

Click **Submit** → wait **5–8 minutes** for the environment to launch.

When the health indicator turns **green (OK)**, proceed.

---

### Step 7 — Verify v1 is running

1. Click the URL at the top of the environment page
2. You should see the app with a **blue header** — "Notes App — v1"
3. Add 2–3 notes to confirm the database connection works

---

### Step 8 — Watch what happens during the update

Before deploying v2, open a second browser tab to your app's URL. Keep both tabs visible.
You will watch the app go offline and come back up.

---

### Step 9 — Deploy v2 (All at Once)

1. In the `notes-all-at-once` environment, click **Upload and deploy**
2. Choose file → `notes-app-v2.zip`
3. Version label: `v2`
4. Click **Deploy**

**What to observe:**
- The environment health turns **Grey (Updating)** — all 3 instances restart simultaneously
- If you refresh your app tab, you will get connection errors or a blank page for ~1–2 minutes
- When health returns to **Green**, refresh your app — the header is now green "Notes App — v2 ✦ Updated!"
- Your notes are still there — the database never moved

---

### Step 10 — Rollback (All at Once)

There is no automatic rollback. You simply redeploy the previous version the same way.

1. **Upload and deploy** → `notes-app-v1.zip` → version label `v1-rollback` → **Deploy**
2. The same downtime window occurs again during rollback

> **Key lesson:** All at Once is the simplest strategy but every deployment and every
> rollback costs you downtime. Acceptable in dev. Never acceptable in production.

---

## PART 4 — Strategy 2: Rolling

### What this strategy does

Instances are updated in **small batches**. Only one batch is offline at a time, so the
rest of the fleet keeps serving traffic. The app stays up, but at reduced capacity.

```
BEFORE:   [v1] [v1] [v1]   ← full capacity serving v1

BATCH 1:  [ ↓] [v1] [v1]   ← 1 instance updating (33% capacity gone)
          [v2] [v1] [v1]   ← batch 1 done; v1 and v2 both serving

BATCH 2:  [v2] [ ↓] [v1]   ← next instance updating
          [v2] [v2] [v1]   ← batch 2 done

BATCH 3:  [v2] [v2] [ ↓]   ← last instance updating
AFTER:    [v2] [v2] [v2]   ← full capacity, all on v2
```

**Important:** During the update, some users get v1 responses and some get v2 responses
depending on which instance the load balancer sends them to. This is called a
**mixed-version window**.

**When to use it:** Production environments where some capacity reduction is acceptable
and you want zero deployment cost.

---

### Step 1 — Create a new environment for this strategy

You are creating a fresh environment inside the same application (`notes-deployment-strategies`).

1. **Elastic Beanstalk** → click `notes-deployment-strategies` → **Create new environment**

| Field | Value |
|---|---|
| Environment tier | Web server environment |
| Environment name | `notes-rolling` |
| Domain | Leave blank |
| Platform | Node.js 20 running on 64bit Amazon Linux 2023 |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | `notes-app-v1.zip` |
| Presets | **High availability** |

Click **Next**

---

### Step 2 — Service access

Same as before:

| Field | Value |
|---|---|
| EC2 instance profile | `aws-elasticbeanstalk-ec2-role` |

Click **Next** → **Next** (skip networking — same defaults)

---

### Step 3 — Instance traffic and scaling

| Field | Value |
|---|---|
| Load balancer type | Application Load Balancer |
| Minimum instances | `3` |
| Maximum instances | `3` |
| Instance types | `t3.micro` |

Scroll down to **Deployment preferences** and set:

| Field | Value |
|---|---|
| Deployment policy | **Rolling** |
| Batch size type | Fixed |
| Batch size | `1` |

> **What "batch size 1" means:** EB updates one instance at a time. With 3 instances,
> there are 3 batches. You get the most visible step-by-step behaviour this way.

Scroll down to **Environment properties** — same 8 properties as before but change two:

| Name | Value |
|---|---|
| `PORT` | `8080` |
| `APP_VERSION` | `v1` |
| `DEPLOY_STRATEGY` | `rolling` ← changed |
| `DB_HOST` | ← your endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next** → **Next** → **Submit**. Wait 5–8 minutes for health to go green.

---

### Step 4 — Verify v1 and add notes

1. Click the URL → confirm blue header, "Notes App — v1"
2. Add 3–4 notes so you have data to observe during the update

---

### Step 5 — Watch what happens during a rolling update

Open your app URL in one browser tab. Keep it open and ready to refresh.

1. In the `notes-rolling` environment, click **Upload and deploy**
2. Choose file → `notes-app-v2.zip`
3. Version label: `v2`
4. Click **Deploy**

**What to observe while it runs:**

- The environment health goes to **Grey (Updating)**
- In the EB console, click **Health** in the left menu — you will see a table of your
  3 instances with their individual statuses
- One instance at a time shows **Pending** while the others stay **OK**
- If you keep refreshing your app URL, most requests succeed — but occasionally
  you may see the green v2 header appear before the deployment is complete
  (that is the mixed-version window — you hit a v2 instance)
- Capacity stays at 2 out of 3 instances minimum during each batch

After the deployment:
- All instances show **OK** and green
- App URL always returns the green v2 header

---

### Step 6 — Rollback (Rolling)

Same process — redeploy v1 using Upload and deploy.

1. **Upload and deploy** → `notes-app-v1.zip` → version label `v1-rollback` → **Deploy**
2. The rolling process runs in reverse — one instance at a time switches back to v1
3. No downtime during rollback either

> **Key lesson:** Rolling gives you zero downtime with zero extra cost. The trade-off is
> reduced capacity during the update and a brief period where both versions are live.

---

## PART 5 — Strategy 3: Rolling with Additional Batch

### What this strategy does

This is Rolling with one important improvement. Before the update starts, EB launches
a brand-new **extra batch** of instances running v2. Only after those are healthy does
it start replacing the original instances one batch at a time. Your fleet stays at
**full capacity the entire time** — you never lose a single instance from serving traffic.

```
BEFORE:         [v1] [v1] [v1]              ← 3 instances, full capacity

STEP 1 — Extra  [v1] [v1] [v1] [v2]        ← 1 extra instance launched first
batch launched:  serving traffic ↑   ↑ warming up

STEP 2 — Batch: [v2] [v1] [v1] [v2]        ← original batch 1 replaced
                [v2] [v2] [v1] [v2]        ← batch 2 replaced
                [v2] [v2] [v2] [v2]        ← batch 3 replaced

STEP 3 — Clean: [v2] [v2] [v2]             ← extra instance terminated
```

**When to use it:** High-traffic production where you cannot afford to lose any capacity,
but can tolerate a small temporary cost for the extra instances.

---

### Step 1 — Create a new environment

1. **Elastic Beanstalk** → `notes-deployment-strategies` → **Create new environment**

| Field | Value |
|---|---|
| Environment name | `notes-rolling-extra` |
| Platform | Node.js 20 running on 64bit Amazon Linux 2023 |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | `notes-app-v1.zip` |
| Presets | **High availability** |

Click **Next** → **Next** (keep networking defaults)

---

### Step 2 — Instance traffic and scaling

| Field | Value |
|---|---|
| Load balancer type | Application Load Balancer |
| Minimum instances | `3` |
| Maximum instances | `6` |
| Instance types | `t3.micro` |

> ⚠️ Maximum must be higher than Minimum. EB needs room above your normal instance count
> to launch the extra batch. If Max = Min = 3, the extra batch cannot launch and the
> deployment fails. Setting Max to 6 gives EB room to temporarily run up to 6 instances.

Scroll down to **Deployment preferences** and set:

| Field | Value |
|---|---|
| Deployment policy | **Rolling with additional batch** |
| Batch size type | Fixed |
| Batch size | `1` |

Scroll down to **Environment properties** — same 8 properties, change `DEPLOY_STRATEGY`:

| Name | Value |
|---|---|
| `PORT` | `8080` |
| `APP_VERSION` | `v1` |
| `DEPLOY_STRATEGY` | `rolling-with-extra-batch` ← changed |
| `DB_HOST` | ← your endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next** → **Next** → **Submit**. Wait 5–8 minutes.

---

### Step 3 — Verify v1 and add notes

Click the URL → confirm blue header. Add some notes.

---

### Step 4 — Watch the instance count change

This is the most visually interesting part of this strategy.

1. Before deploying, go to **Health** in the left menu
2. Count the instances — you should see exactly 3
3. Now deploy v2:

   **Upload and deploy** → `notes-app-v2.zip` → version label `v2` → **Deploy**

4. Keep refreshing the **Health** page

**What to observe:**
- Shortly after deployment starts, the instance count **rises to 4** — the extra batch
  has launched and EB is warming it up before touching your existing fleet
- Then the original instances start updating one by one
- At every point, at least 3 instances are healthy and serving traffic — capacity never drops
- After all 3 originals are updated, the extra instance is terminated and you are back to 3

> Go to **EC2 → Instances** in another tab and refresh it during the deployment.
> You will literally see a 4th instance appear and disappear.

---

### Step 5 — Rollback (Rolling with Additional Batch)

1. **Upload and deploy** → `notes-app-v1.zip` → version label `v1-rollback` → **Deploy**
2. The same full-capacity rolling process happens in reverse

> **Key lesson:** This strategy is ideal when you must maintain 100% capacity at all times.
> The extra instance costs a few cents for the 5–10 minutes it runs. Worth it for
> high-traffic apps.

---

## PART 6 — Strategy 4: Immutable

### What this strategy does

This is the safest strategy. Instead of modifying your existing instances, EB launches
a **completely separate, brand-new Auto Scaling Group** with fresh instances running v2.
Your original instances keep serving 100% of production traffic the whole time.
Only after every single new instance passes health checks does EB move traffic to them
and terminate the old ones.

```
PHASE 1 — Original ASG serving 100% traffic:
  [v1] [v1] [v1]

PHASE 2 — New ASG launching in parallel (NOT serving traffic yet):
  [v1] [v1] [v1]  |  [v2] [v2] [v2]
  ↑ live traffic      ↑ warming up, health checks running

PHASE 3 — All new instances healthy, added to load balancer:
  [v1] [v1] [v1]  +  [v2] [v2] [v2]
  (brief moment where both serve traffic)

PHASE 4 — Old instances drained and terminated:
                      [v2] [v2] [v2]
                      ↑ 100% traffic, deployment complete
```

**The key safety property:** If anything goes wrong during Phase 2 or Phase 3 — the new
instances fail health checks, the app crashes, a bug is found — you click **Abort** and
the new ASG is instantly terminated. Your original v1 instances never stopped serving traffic.

**When to use it:** Mission-critical production where even a brief reduced-capacity window
is unacceptable and you need an instant abort option.

---

### Step 1 — Create a new environment

1. **Elastic Beanstalk** → `notes-deployment-strategies` → **Create new environment**

| Field | Value |
|---|---|
| Environment name | `notes-immutable` |
| Platform | Node.js 20 running on 64bit Amazon Linux 2023 |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | `notes-app-v1.zip` |
| Presets | **High availability** |

Click **Next** → **Next** (keep networking defaults)

---

### Step 2 — Instance traffic and scaling

| Field | Value |
|---|---|
| Load balancer type | Application Load Balancer |
| Minimum instances | `2` |
| Maximum instances | `4` |
| Instance types | `t3.micro` |

> We use 2 instances here instead of 3 to keep the cost of the immutable deployment down.
> During the update, EB doubles the fleet (2 → 4), then returns to 2. Using 3 would
> temporarily create 6 instances.

Scroll down to **Deployment preferences** and set:

| Field | Value |
|---|---|
| Deployment policy | **Immutable** |

Scroll down to **Environment properties** — same 8 properties, change `DEPLOY_STRATEGY`:

| Name | Value |
|---|---|
| `PORT` | `8080` |
| `APP_VERSION` | `v1` |
| `DEPLOY_STRATEGY` | `immutable` ← changed |
| `DB_HOST` | ← your endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next** → **Next** → **Submit**. Wait 5–8 minutes.

---

### Step 3 — Verify v1 and add notes

Click the URL → confirm blue header. Add a few notes.

---

### Step 4 — Open EC2 to watch the new ASG appear

Before deploying, go to **EC2 → Auto Scaling Groups** in a separate browser tab.
Note the current ASG name for this environment — it will have a name like
`awseb-e-xxxxxxxxxx-stack-AWSEBAutoScalingGroup`.

Now deploy v2:

**Upload and deploy** → `notes-app-v2.zip` → version label `v2` → **Deploy**

**What to observe in EC2 Auto Scaling Groups:**
- A brand new ASG appears alongside the original one
- The new ASG starts with 1 instance (EB health-checks a single instance first)
- Once that instance passes, the rest of the new ASG fills up to match your original count
- The original ASG shows its instances being terminated one by one
- The new ASG becomes the only one remaining

**What to observe in Elastic Beanstalk:**
- Environment health goes to **Grey (Updating)**
- Click **Health** in the left menu — you will see the original instances AND new instances
- New instances appear with a `*` or a different launch time
- The app URL keeps working throughout — never goes down

---

### Step 5 — Test the abort / instant rollback

The immutable strategy's biggest advantage is the ability to **abort mid-deployment**
with zero impact on users. Let's practise this.

1. Start another deployment:
   **Upload and deploy** → `notes-app-v1.zip` → version label `v1-test-abort` → **Deploy**

2. Wait about 60 seconds — the new ASG is launching but not yet serving traffic

3. Click **Actions** → **Abort current operation**

4. Confirm the abort

**What happens:**
- The new ASG and all its instances are terminated immediately
- Your original instances (running the current version) keep serving traffic without interruption
- The environment returns to Green health within 1–2 minutes
- No users experienced any disruption

> This is fundamentally different from Rolling or All at Once — with those strategies,
> aborting mid-deployment leaves your fleet in a mixed state. With Immutable, aborting
> is always clean.

---

### Step 6 — Normal rollback (post-deployment)

If you have already completed the deployment to v2 and want to go back to v1:

1. **Upload and deploy** → `notes-app-v1.zip` → version label `v1-rollback` → **Deploy**
2. A new immutable deployment runs — a fresh ASG with v1 is launched, tested, then swapped in
3. The v2 ASG is terminated once the v1 ASG is healthy

> **Key lesson:** Immutable costs the most temporarily (double instances for 5–10 minutes)
> but is the only strategy where a deployment problem never touches production traffic.
> The abort button is a genuine emergency brake.

---

## PART 7 — Understanding What You Just Observed

Now that you have run all four strategies, here is what each one demonstrated:

### The downtime difference

With **All at Once**, you saw the app become unreachable when you refreshed during
the update. That is the cost of simplicity — all instances down at the same time.

With the other three strategies, the app kept responding throughout. The load balancer
always had at least one healthy instance to route traffic to.

### The capacity difference

With **Rolling**, you had 2 out of 3 instances serving traffic during each batch update.
Your total capacity dropped by 33% during the rolling window.

With **Rolling with Additional Batch**, you had 3 out of 4+ instances serving traffic
at all times. Capacity never dropped below your normal fleet size.

With **Immutable**, you had your full original fleet serving traffic right up until the
new fleet was completely healthy and ready. Capacity never changed.

### The rollback difference

With **All at Once**, **Rolling**, and **Rolling with Additional Batch**, rollback means
running another deployment. If the bad version caused a crash, your instances may be in
an inconsistent state.

With **Immutable**, you can abort before the new ASG ever touches production traffic.
The rollback is not a redeployment — it is a cancellation. Nothing bad ever happened
to your running instances.

### Mixed-version window

With **Rolling** and **Rolling with Additional Batch**, there is a period where some
instances run v1 and some run v2. If your app makes database schema changes, API changes,
or any change that is not backward-compatible, this window is dangerous.

**Immutable** avoids this entirely — traffic is either 100% v1 or 100% v2. There is no
in-between state from a user's perspective.

---

## PART 8 — Teardown

> ⚠️ Always do this when you are finished. EC2 instances, load balancers, and RDS
> charge by the hour.

### Terminate all EB environments

1. **Elastic Beanstalk** → click `notes-deployment-strategies`
2. For each environment (`notes-all-at-once`, `notes-rolling`, `notes-rolling-extra`, `notes-immutable`):
   - Click the environment name
   - **Actions** → **Terminate environment**
   - Type the environment name to confirm → click **Terminate**
3. Wait for all environments to finish terminating
4. Back on the application page → **Actions** → **Delete application** → confirm

### Delete RDS

1. **RDS** → **Databases** → tick `notes-db`
2. **Actions** → **Delete**
3. Uncheck "Create final snapshot"
4. Check "I acknowledge..."
5. Type `delete me` → click **Delete**

### Clean up security group

1. **EC2** → **Security Groups**
2. Select `notes-db-sg` → **Actions** → **Delete security groups**

---

## Troubleshooting

| Problem | Root Cause | Fix |
|---|---|---|
| 502 Bad Gateway on app load | App not listening on port 8080 | Confirm `process.env.PORT \|\| 8080` in app.js. Never hardcode 3000. |
| `ETIMEDOUT` connecting to DB | Missing inbound rule on security group | EC2 → Security Groups → `notes-db-sg` → add PostgreSQL / 5432 / 0.0.0.0/0 |
| `database "notesdb" does not exist` | Initial DB name not set when creating RDS | Connect via CloudShell psql and run `CREATE DATABASE notesdb;` |
| App crashes silently, env stays red | `.env` file in zip overriding EB env vars | Remove `.env` — zip must only contain `app.js` and `package.json` |
| High availability preset not showing | You are on the wrong wizard screen | Make sure you selected "Web server environment" as environment tier |
| Deployment stuck in "Updating" >15 min | Instance failing health checks | EB → Logs → Last 100 lines → check `web.stdout.log` for the error |
| Rolling with Additional Batch fails | Max instances = Min instances | Increase Max instances — EB needs headroom above Min to launch the extra batch |
| Immutable deployment fails to start | Not enough EC2 capacity in region | Try a different instance type (t3.small) or a different availability zone |
| Environment stuck in Severe/Degraded | Various | EB → Logs → Request last 100 lines → read the error in `web.stdout.log` |

---

## Cost for This Lab

| Resource | Rate | ~4 hours total |
|---|---|---|
| 4 × load balancers | ~$0.02/hr each | ~$0.32 |
| 3 instances per env × 4 envs | ~$0.01/hr each (t3.micro) | ~$0.48 |
| RDS db.t3.micro | ~$0.02/hr | ~$0.08 |
| Extra instances (temp, Rolling + Immutable) | ~$0.01 each | ~$0.10 |
| **Total** | | **~$1.00** |

Run Part 8 (teardown) as soon as you are done to stop charges.

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│              CHOOSING THE RIGHT STRATEGY                            │
├──────────────────────────┬──────────────────────────────────────────┤
│ You are deploying to...  │ Use this strategy                        │
├──────────────────────────┼──────────────────────────────────────────┤
│ Local / dev environment  │ All at Once — fast, simple, free         │
│ Production, low traffic  │ Rolling — no downtime, no extra cost     │
│ Production, high traffic │ Rolling with Additional Batch            │
│ Critical / regulated app │ Immutable — safest abort mechanism       │
└──────────────────────────┴──────────────────────────────────────────┘
```
