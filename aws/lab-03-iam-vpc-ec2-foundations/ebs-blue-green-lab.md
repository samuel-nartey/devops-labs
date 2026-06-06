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
