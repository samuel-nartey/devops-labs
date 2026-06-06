# Blue-Green Deployment with AWS Elastic Beanstalk
### Console-based guide — follows the exact AWS wizard steps

---

## What You Will Build

A Notes Manager web app (Node.js + Express + PostgreSQL on RDS) deployed on Elastic Beanstalk.
You will deploy v1 as the Blue environment, make a visible change for v2, deploy it as Green,
then perform a CNAME swap — watching production traffic switch instantly with zero downtime.

---

## Before You Start — Have These Ready

- Your `notes-app-v1.zip` file (the 4 files zipped together)
- Your RDS endpoint (from the RDS setup below)
- Your DB password (`YourPass123!` or whatever you set)

---

## PART 1 — Create the RDS Database

> Do this first. The database takes ~5 minutes to become available.

1. AWS Console → search **RDS** → click **RDS**
2. Click **Create database**
3. Select **Standard create**
4. **Engine:** PostgreSQL
5. **Template:** Dev/Test
6. **Instance configuration:**
   - Select **Burstable classes (includes t classes)**
   - Instance type: `db.t3.micro`
7. **Settings:**
   - DB instance identifier: `notes-db`
   - Master username: `notesadmin`
   - Master password: `YourPass123!`
   - Confirm password: `YourPass123!`
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
11. Scroll to bottom → **Create database**

### After RDS is created — add the inbound rule

The security group needs a rule to allow traffic on port 5432:

1. Go to **EC2** → **Security Groups**
2. Find `notes-db-sg` → click it
3. **Inbound rules** → **Edit inbound rules** → **Add rule**
4. Set:
   - Type: `PostgreSQL`
   - Source: `Anywhere-IPv4` (`0.0.0.0/0`)
5. Click **Save rules**

### Get your RDS endpoint

1. Go to **RDS** → **Databases** → click `notes-db`
2. Under **Connectivity & security** tab, copy the **Endpoint**
3. It looks like: `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com`
4. **Save this — you need it in the EB wizard**

---

## PART 2 — Deploy the BLUE Environment (v1)

Go to **Elastic Beanstalk** → **Create application**

---

### Step 1 — Configure environment

| Field | Value |
|---|---|
| Environment tier | Web server environment |
| Application name | `notes-app` |
| Environment name | `notes-blue` |
| Domain | Leave blank (auto-generated) |
| Platform | Managed platform |
| Platform type | Node.js |
| Platform branch | Node.js 18 running on 64bit Amazon Linux 2023 |
| Platform version | (latest recommended) |
| Application code | Upload your code |
| Version label | `v1` |
| Local file | Choose file → select `notes-app-v1.zip` |
| Presets | **Single instance (free tier eligible)** |

Click **Next**

---

### Step 2 — Configure service access

| Field | Value |
|---|---|
| Service role | Create and use new service role |
| EC2 key pair | Leave blank (not needed for this exercise) |
| EC2 instance profile | Leave blank OR select existing if available |

> If you get an error about instance profile, you may need to create one:
> Go to **IAM** → **Roles** → **Create role** → **AWS service** → **EC2**
> → attach `AWSElasticBeanstalkWebTier` policy → name it `aws-elasticbeanstalk-ec2-role`
> → come back and select it here

Click **Next**

---

### Step 3 — Set up networking, database, and tags (optional)

You already created RDS separately so skip the database section here.

| Field | Value |
|---|---|
| VPC | default VPC |
| Public IP address | Activated (check the box) |
| Instance subnets | Select any available subnet |

Leave database section empty — your RDS is already running separately.

Click **Next**

---

### Step 4 — Configure instance traffic and scaling (optional)

| Field | Value |
|---|---|
| Root volume type | General Purpose (SSD) |
| Size | 10 GB |
| IMDSv1 | Leave default |
| EC2 security groups | Leave default |

Under **Environment properties** — this is where you set your DB connection:

Click **Add environment property** and add all 6 of these:

| Name | Value |
|---|---|
| `APP_VERSION` | `v1` |
| `ENV_COLOR` | `blue` |
| `DB_HOST` | `notes-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com` ← your endpoint |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next**

---

### Step 5 — Configure updates, monitoring, and logging (optional)

Leave everything as default.

Click **Next**

---

### Step 6 — Review

Look over the summary. Confirm:
- Environment name is `notes-blue`
- Platform is Node.js 18
- Your ZIP file is listed under application code
- Environment properties show your DB values

Click **Submit**

> EB will now launch. This takes 3–5 minutes. You will see events scrolling.
> Wait until the health indicator shows **OK** (green).

---

### Verify Blue is working

1. Click the URL at the top of the environment page
   - Looks like: `notes-blue.xxxxxxxxxx.us-east-1.elasticbeanstalk.com`
2. You should see the app with a **blue header** — "v1 — BLUE environment"
3. Add 2–3 notes to confirm the database is connected

> If you see "DB Error" — go back and check the RDS security group inbound rule
> (port 5432 open to 0.0.0.0/0) and that all 7 environment properties are set correctly.

---

## PART 3 — Make Your v2 Change

Go back to your `notes-app` folder on your computer. Open `app.js` and find this line (~line 63):

```javascript
<strong>Notes App</strong>
```

Change it to:

```javascript
<strong>Notes App ✦ v2</strong>
```

Save the file. Now select the same 4 files again, zip them into a new file named
`notes-app-v2.zip`.

---

## PART 4 — Deploy the GREEN Environment (v2)

Go to **Elastic Beanstalk** → click on `notes-app` → **Create a new environment**

Follow the same 6 steps as Part 2 with these differences:

---

### Step 1 — Configure environment

| Field | Value |
|---|---|
| Environment name | `notes-green` ← changed |
| Version label | `v2` ← changed |
| Local file | `notes-app-v2.zip` ← changed |
| Presets | Single instance |

Everything else the same. Click **Next**

---

### Step 2 — Configure service access

Same as before. Click **Next**

---

### Step 3 — Networking (optional)

Same as before — skip database section. Click **Next**

---

### Step 4 — Instance traffic and scaling (optional)

Same environment properties but change two values:

| Name | Value |
|---|---|
| `APP_VERSION` | `v2` ← changed |
| `ENV_COLOR` | `green` ← changed |
| `DB_HOST` | same RDS endpoint as Blue |
| `DB_USER` | `notesadmin` |
| `DB_PASS` | `YourPass123!` |
| `DB_NAME` | `notesdb` |
| `DB_SSL` | `true` |

Click **Next**

---

### Step 5 — Monitoring (optional)

Leave as default. Click **Next**

---

### Step 6 — Review

Confirm environment name is `notes-green` → Click **Submit**

Wait 3–5 minutes for Green to launch.

---

### Verify Green is working

1. Click the Green environment URL
2. You should see a **green header** — "v2 — GREEN environment"
3. All notes you added on Blue are visible here — same database!
4. Notes show "written by v1" — they were created by the Blue environment

> At this point:
> - Blue URL = live (v1, blue header) — this is what users would see
> - Green URL = your new version (v2, green header) — only you can see it
> - Same RDS database — same data in both environments

---

## PART 5 — The CNAME Swap

The AWS Console does not have a swap button for Elastic Beanstalk.
You need the EB CLI for this one command.

### Install EB CLI (Windows)

```bash
pip install awsebcli --break-system-packages
```

Or if pip is not available:
```bash
pip3 install awsebcli
```

Verify:
```bash
eb --version
```

### Configure AWS credentials

```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Region: us-east-1
# Output format: json
```

### Run the swap

```bash
# Navigate to your notes-app folder
cd C:\Users\USER\OneDrive\Desktop\Practise_Hands-on\devops-labs\AWS\notes-app

# Point EB CLI at your existing app (no new resources created)
eb init notes-app --platform "Node.js 18 running on 64bit Amazon Linux 2023" --region us-east-1

# THE swap command
eb swap notes-blue --destination-name notes-green
```

### What just happened

```
BEFORE swap:
  notes-blue.xxxxxx.elasticbeanstalk.com  → serves v1 (Blue)
  notes-green.xxxxxx.elasticbeanstalk.com → serves v2 (Green)

AFTER swap:
  notes-blue.xxxxxx.elasticbeanstalk.com  → now serves v2 ✓
  notes-green.xxxxxx.elasticbeanstalk.com → now serves v1
```

Open the Blue URL in your browser — it now shows the **green header** and "v2".
The swap is instant. Zero downtime.

---

## PART 6 — Rollback

Something wrong with v2? One command to go back:

```bash
eb swap notes-green --destination-name notes-blue
```

Open the Blue URL again — it shows the **blue header** and "v1".
Blue was running the whole time — nothing to redeploy.

---

## PART 7 — Teardown

**Always do this when finished — these resources charge by the hour.**

### Terminate EB environments (Console)

1. **Elastic Beanstalk** → `notes-app`
2. Click `notes-blue` → **Actions** → **Terminate environment** → confirm
3. Click `notes-green` → **Actions** → **Terminate environment** → confirm
4. Once both terminated → **Actions** → **Delete application** → confirm

### Delete RDS (Console)

1. **RDS** → **Databases** → select `notes-db`
2. **Actions** → **Delete**
3. Uncheck "Create final snapshot"
4. Check "I acknowledge..."
5. Type `delete me` → **Delete**

### Check EC2 (Console)

1. **EC2** → **Instances**
2. Confirm no instances are running
3. **EC2** → **Security Groups** → delete `notes-db-sg`

---

## Troubleshooting

### "DB Error" when the app opens
- Check RDS security group has inbound rule: PostgreSQL / TCP / 5432 / 0.0.0.0/0
- Check all 7 environment properties are set in EB → Configuration → Software
- EB environment → Actions → Restart app server

### EB environment stuck in "Degraded" or "Severe"
- Click the environment → **Logs** → **Request last 100 lines**
- Look for the actual error message
- Most common cause: wrong DB_HOST value in environment properties

### `eb swap` says environment not found
- Make sure you ran `eb init notes-app` first
- Check region matches: `eb init notes-app --region us-east-1`

---

## What to Observe During the Swap

Open two browser tabs before running the swap:

- **Tab 1:** Blue URL → `/health` → shows `{"version":"v1","env":"blue"}`
- **Tab 2:** Green URL → `/health` → shows `{"version":"v2","env":"green"}`

Run `eb swap`. Refresh Tab 1 — it now shows `{"version":"v2","env":"green"}`.

The header colour on Tab 1 changes from blue to green.
All your notes are still there — the database never moved.
