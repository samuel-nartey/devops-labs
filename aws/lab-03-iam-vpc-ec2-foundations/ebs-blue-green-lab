# Blue-Green Deployment with AWS Elastic Beanstalk
### Console-based guide — no CLI required (except for the final CNAME swap)

---

## What You Will Build

A **Notes Manager** web app (Node.js + Express + PostgreSQL) deployed on Elastic Beanstalk.
You will deploy **v1** as the Blue environment, make a visible change for **v2**, deploy it as
Green, then perform a **CNAME swap** — watching production traffic switch with zero downtime.

```
            ┌────────────────────────────┐
            │   yourapp.example.com       │
            │   CNAME → active env        │
            └────────────┬───────────────┘
                         │
          ┌──────────────▼──────────────┐
          │  100% traffic               │  0% (testing only)
          ▼                             ▼
  ┌───────────────┐           ┌───────────────┐
  │  BLUE (live)  │           │ GREEN (idle)  │
  │  v1 of app    │           │ v2 of app     │
  └───────┬───────┘           └───────┬───────┘
          │                           │
          └──────────┬────────────────┘
                     ▼
           ┌──────────────────┐
           │  RDS PostgreSQL  │
           │  (shared by both)│
           └──────────────────┘
```

---

## Prerequisites

- AWS account (free tier is fine)
- Basic familiarity with the AWS Console
- The app files ready on your computer (see Step 0)
- A ZIP tool (Windows built-in, macOS built-in, or 7-zip)

> **Note on the CNAME swap:** The AWS Console does NOT have a "swap environments" button.
> You have two options:
> - **Option A:** Install the EB CLI just for the one swap command (`eb swap`) — recommended
> - **Option B:** Manually update your DNS CNAME record in Route 53 — covered at the end

---

## STEP 0 — Prepare the App Files on Your Computer

Create a folder called `notes-app` on your computer and create these 4 files inside it.

---

### File 1 of 4 — `app.js`

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
  ssl:      { rejectUnauthorized: false }
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
    res.status(500).send(`<pre style="padding:2rem">DB Error: ${err.message}\n\nCheck that DB_HOST, DB_USER, DB_PASS, DB_NAME are set in EB Configuration > Software.</pre>`);
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

const PORT = process.env.PORT || 3000;
initDB()
  .then(() => app.listen(PORT, () => console.log(`Notes app running on :${PORT}`)))
  .catch(err => { console.error('Startup failed:', err); process.exit(1); });
```

---

### File 2 of 4 — `package.json`

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

---

### File 3 of 4 — `.env.example`

```bash
DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
DB_USER=notesadmin
DB_PASS=YourPass123!
DB_NAME=notesdb
APP_VERSION=v1
ENV_COLOR=blue
```

---

### File 4 of 4 — `.ebignore`

```
.env
node_modules/
.git/
*.log
```

---

### ZIP the app for upload

Select all 4 files (NOT the folder itself — select the files directly), right-click → Compress/Zip.
Name it `notes-app-v1.zip`.

```
notes-app-v1.zip
├── app.js
├── package.json
├── .env.example
└── .ebignore
```

> **Important:** Zip the FILES, not the folder. If you zip the folder, EB gets
> `notes-app/app.js` instead of `app.js` and the deploy will fail.

---

## STEP 1 — Create the RDS Database (Console)

> Do this first — the database takes ~5 minutes to become available.

1. Open the AWS Console → search **RDS** → click **RDS**
2. Click **Create database**
3. Fill in the form:

| Field | Value |
|---|---|
| Creation method | Standard create |
| Engine | PostgreSQL |
| Engine version | PostgreSQL 15.x (latest) |
| Templates | **Free tier** |
| DB instance identifier | `notes-db` |
| Master username | `notesadmin` |
| Master password | `YourPass123!` (save this) |
| Confirm password | `YourPass123!` |
| Instance class | db.t3.micro (auto-selected by Free tier) |
| Storage | 20 GiB (default) |
| Public access | **Yes** (needed so EB can reach it) |
| VPC security group | Create new → name it `notes-db-sg` |

4. Scroll down → click **Create database**
5. Wait for status to show **Available** (~5 minutes)
6. Click the `notes-db` instance → copy the **Endpoint** under "Connectivity & security"
   - It looks like: `notes-db.xxxxxxxxx.us-east-1.rds.amazonaws.com`
   - **Save this — you need it in every environment you create**

---

## STEP 2 — Create the Elastic Beanstalk Application (Console)

1. Open the AWS Console → search **Elastic Beanstalk** → click **Elastic Beanstalk**
2. Click **Create application**
3. Fill in:

| Field | Value |
|---|---|
| Application name | `notes-app` |

4. Click **Create** — this just registers the app, no environment yet

---

## STEP 3 — Deploy BLUE Environment (v1)

1. Inside the `notes-app` application page, click **Create a new environment**
2. Select **Web server environment** → click **Select**
3. Fill in:

| Field | Value |
|---|---|
| Environment name | `notes-blue` |
| Domain | Leave blank (auto-generated) |
| Platform | **Node.js** |
| Platform branch | Node.js 18 running on 64bit Amazon Linux 2023 |
| Application code | **Upload your code** |
| Source code origin | Local file → click **Choose file** → select `notes-app-v1.zip` |
| Version label | `v1` |

4. Click **Configure more options** (important — do NOT click Create yet)

5. In the configuration screen, find the **Software** card → click **Edit**
   - Scroll down to **Environment properties**
   - Add these 6 properties one by one (click **Add environment property** for each):

| Name | Value |
|---|---|
| `APP_VERSION` | `v1` |
| `ENV_COLOR` | `blue` |
| `DB_HOST` | `notes-db.xxxxxxxxx.us-east-1.rds.amazonaws.com` ← your RDS endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |

   - Click **Save**

6. Back on the Configure more options page, find the **Instances** card → click **Edit**
   - Instance type: `t3.micro`
   - Click **Save**

7. Click **Create environment** — wait ~5 minutes for the environment to launch

8. Once status shows **OK** (green tick), click the URL at the top of the environment page
   - You should see the app with a **blue header** — "v1 — BLUE environment"
   - Add a few notes to confirm the DB is working

> If you see a "DB Error" — see the Security Group fix section at the bottom of this guide.

---

## STEP 4 — Make Your v2 Change

Go back to your `notes-app` folder on your computer. Open `app.js` and make a visible change
so you can clearly see the swap happen.

**Simple change — edit the header text:**

Find this line (~line 63):
```javascript
<strong>Notes App</strong>
```
Change it to:
```javascript
<strong>Notes App ✦ v2</strong>
```

Save the file. Now re-zip the files into a new file named `notes-app-v2.zip`.

> Same as before: select the 4 files directly, compress them, name the ZIP `notes-app-v2.zip`.

---

## STEP 5 — Deploy GREEN Environment (v2)

1. Go back to **Elastic Beanstalk** → click on `notes-app`
2. Click **Create a new environment** again
3. Fill in:

| Field | Value |
|---|---|
| Environment name | `notes-green` |
| Domain | Leave blank |
| Platform | **Node.js** |
| Platform branch | Node.js 18 running on 64bit Amazon Linux 2023 |
| Application code | **Upload your code** |
| Source code origin | Local file → select `notes-app-v2.zip` |
| Version label | `v2` |

4. Click **Configure more options**

5. In **Software** → **Edit** → add the same 6 environment properties, but change two values:

| Name | Value |
|---|---|
| `APP_VERSION` | `v2` ← changed |
| `ENV_COLOR` | `green` ← changed |
| `DB_HOST` | same RDS endpoint as Blue |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |

   - Click **Save**

6. **Instances** → **Edit** → t3.micro → **Save**
7. Click **Create environment** — wait ~5 minutes

8. Once status is **OK**, click the Green environment URL
   - You should see a **green header** — "v2 — GREEN environment"
   - All the notes you added on Blue are visible here (same database!)
   - The notes show "written by v1" — created by the Blue environment

> At this point:
> - Blue URL = live production (v1, blue header)
> - Green URL = your new version (v2, green header)
> - Same DB — same notes visible on both
> - Users are still on Blue — they cannot see Green

---

## STEP 6 — The CNAME Swap

This is the blue-green moment. The AWS Console does not have a swap button, so you have
two options:

---

### Option A — Using the EB CLI (Recommended, one command)

```bash
# Install EB CLI if you haven't
pip install awsebcli --break-system-packages

# Configure AWS credentials (if not done)
aws configure

# Navigate to your notes-app folder
cd notes-app

# Initialise EB CLI pointing to your existing app (no new resources created)
eb init notes-app --platform "Node.js 18 running on 64bit Amazon Linux 2023" --region us-east-1

# Run the swap — this exchanges the CNAMEs between Blue and Green
eb swap notes-blue --destination-name notes-green
```

Done. Your production URL now points to Green (v2).

---

### Option B — Manual DNS swap via Route 53 (no CLI needed)

This works if your domain is in Route 53. If you are using the raw `.elasticbeanstalk.com` URLs
(no custom domain), you don't need to do anything with DNS — just share the Green URL instead.

1. Open **Route 53** in the console
2. Click **Hosted zones** → click your domain
3. Find the CNAME record pointing to `notes-blue.us-east-1.elasticbeanstalk.com`
4. Click **Edit record**
5. Change the value to `notes-green.us-east-1.elasticbeanstalk.com`
6. Click **Save**

DNS propagation takes 30–60 seconds (Route 53 TTLs are short by default).

---

### Verify the swap worked

After either option, open your production URL in the browser.
You should see the **green header** and "v2 — GREEN environment".

Open the Green environment in EB Console → **Health** tab → confirm it shows OK.

---

## STEP 7 — Rollback

Something wrong with v2? Reverse the swap.

**Via EB CLI:**
```bash
eb swap notes-green --destination-name notes-blue
```

**Via Route 53 (Option B):**
Edit the CNAME record back to `notes-blue.us-east-1.elasticbeanstalk.com`.

Your production URL is back on Blue (v1) within seconds.
Blue was running the whole time — there is nothing to redeploy.

---

## STEP 8 — Teardown (Avoid Charges)

Run this when you are done. These resources cost money even when idle (~$0.06/hr total).

### Terminate EB environments (Console)

1. Go to **Elastic Beanstalk** → `notes-app`
2. Click on `notes-blue` environment
3. Actions → **Terminate environment** → type the environment name to confirm → **Terminate**
4. Repeat for `notes-green`
5. Once both are terminated, go back to the application page
6. Actions → **Delete application** → confirm

### Delete RDS (Console)

1. Go to **RDS** → **Databases**
2. Select `notes-db` → **Actions** → **Delete**
3. Uncheck "Create final snapshot"
4. Check "I acknowledge..."
5. Type `delete me` → **Delete**

### Verify everything is gone

- EB: Applications page should be empty
- RDS: Databases page should be empty
- EC2: Check that no instances remain under **Instances**

---

## Fix: "DB Error" When the App Opens

The most common issue. The RDS security group is not allowing traffic from EB.

### Fix via Console

1. Go to **RDS** → click `notes-db` → **Connectivity & security** tab
2. Under **VPC security groups**, click the security group link (e.g. `notes-db-sg`)
3. Click **Inbound rules** → **Edit inbound rules** → **Add rule**
4. Set:
   - Type: `PostgreSQL`
   - Protocol: `TCP` (auto-filled)
   - Port: `5432` (auto-filled)
   - Source: `0.0.0.0/0` (allows all — fine for practice; restrict in production)
5. Click **Save rules**
6. Go back to your EB environment → **Actions** → **Restart app server**

The app should now connect to the DB.

---

## What to Observe During the Swap

Open two browser tabs:

- **Tab 1:** Your Blue EB environment URL + `/health`
  → shows `{"status":"ok","version":"v1","env":"blue"}`

- **Tab 2:** Your Green EB environment URL + `/health`
  → shows `{"status":"ok","version":"v2","env":"green"}`

Do the swap. Then refresh Tab 1 (your production URL) — it now shows:
`{"status":"ok","version":"v2","env":"green"}`

Also notice:
- Notes added on Blue are visible on Green (shared RDS)
- Each note has a "written by v1" or "written by v2" tag
- Rollback flips it back in seconds

---

## Key Concepts

| Term | What it means in practice |
|---|---|
| Blue environment | The live EB environment users are hitting right now |
| Green environment | Second EB environment running the new version — users cannot see it yet |
| CNAME swap | Changing which EB environment URL your domain points to — this IS the deployment |
| Shared RDS | One database for both environments — no data split, no migration during swap |
| Zero downtime | The swap redirects DNS atomically, no restart, no gap in service |
| Instant rollback | Blue keeps running — reverse the swap any time in seconds |

---

## Console Navigation Cheat Sheet

| Task | Where to go |
|---|---|
| Create / view environments | Elastic Beanstalk → Applications → notes-app |
| View environment health & events | Click environment name → Health / Events tabs |
| Update environment variables | Environment → Configuration → Software → Edit |
| Deploy new version to existing env | Environment → Upload and deploy |
| View app logs | Environment → Logs → Request logs |
| View RDS endpoint | RDS → Databases → notes-db → Connectivity & security |
| Edit security group rules | EC2 → Security Groups (or via RDS / EB pages) |
| Edit DNS record | Route 53 → Hosted zones → your domain |
