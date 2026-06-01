# 🛡️ Let's Learn Linux — Episode 1
### *A DevSecOps Field Assignment | CypherCore Systems Bootcamp*

---

> **"You don't need to memorise every command. You need to understand why each one exists — because on a live server at 2 AM, there's no Google."**
> — Samuel Nartey, Lead Facilitator, ParoCyber DevSecOps Bootcamp

---

## 📖 How This Works

This assignment follows one day in the life of **Kofi Mensah**, a Junior DevSecOps Trainee at CypherCore Systems. His inline manager **Abena Asante** gives him real tasks — she never tells him which command to run. That part is on him.

**You are Kofi. Read the scenario. Figure out the command. Execute it. Document everything.**

---

## 🧑‍💼 The Team

| | |
|---|---|
| **Abena Asante** | Senior DevSecOps Engineer. Kofi's manager. She gives tasks, not answers. |
| **Kofi Mensah** | Junior DevSecOps Trainee — 3 weeks in. That's you. |

---

## 🗂️ Submission Requirements

| Item | Detail |
|---|---|
| **GitHub Repo** | `lets-learn-linux-1` (public) |
| **Files** | `answers.md` + `screenshots/` folder |
| **LinkedIn Post** | Required — see Section 7 |
| **Deadline** | **12 June 2026 — 12:00 AM (Midnight) PROMPT** |

---

## 📊 Marks Allocation

| Section | Questions | Marks |
|---|---|---|
| Section 1 — Orient Yourself | Q1 – Q3 | 10 |
| Section 2 — Build the Environment | Q4 – Q7 | 15 |
| Section 3 — Write and Read Files | Q8 – Q11 | 20 |
| Section 4 — Move and Clean Up | Q12 – Q14 | 10 |
| Section 5 — Links and Inodes | Q15 – Q18 | 20 |
| Section 6 — Data Streams and Redirection | Q19 – Q21 | 15 |
| GitHub Organisation | Structure, named files, commit history | 5 |
| LinkedIn Post | Posted with repo link and correct tags | 5 |
| **TOTAL** | | **100** |

> ⚠️ One-line answers lose marks. Explain your reasoning — "it worked" is not an answer.

---
---

# 🟢 SECTION 1 — Orient Yourself *(10 marks)*

---

*Monday. 8:47 AM. Kofi walks in — new badge, new laptop. Abena is already at her desk with three terminals open.*

**Abena:** "Kofi — whenever you land on a server you've never touched, there are three things you find out first: where you are, who you're logged in as, and what system you're on. Show me you know how to do that."

---

### Q1 *(3 marks)*

**Task:** Print your current directory, your username, and full OS and kernel details — three separate commands.

📸 Screenshot all three outputs together.

> **answers.md:** What does each command tell you? Why does a DevSecOps engineer run these three things first when SSHing into an unknown server — especially regarding kernel CVEs?

---

**Abena:** "Good. Now — Linux organises everything into a standard structure. Look at it before you create a single file today."

---

### Q2 *(4 marks)*

**Task:** List the contents of the root directory — the very top of the Linux filesystem.

> **answers.md:** Pick five directories from the output and explain each one's purpose. What is the Filesystem Hierarchy Standard (FHS) and why does it exist? What breaks on a shared production server without it?

---

**Abena:** "One more thing. Linux hides files in plain sight. Make sure you can see everything."

---

### Q3 *(3 marks)*

**Task:** List your home directory twice — once the default way, then again revealing hidden files with full details (permissions, ownership, size).

> **answers.md:** What is different between the two outputs? What makes a file hidden in Linux — is it a special type? Name two real hidden files found in a home directory and explain what they do.

---
---

# 🟡 SECTION 2 — Build the Environment *(15 marks)*

---

*9:15 AM. Abena slides a sticky note across the desk:*

```
~/projects/cyphercore/
    ├── configs/
    ├── logs/
    │   ├── access/
    │   ├── errors/
    │   └── archive/
    └── reports/
```

**Abena:** "New client onboarding. Their pipeline expects this exact structure or the scripts fail. Build it — in the terminal. You have until the 10 AM standup."

**Kofi:** "Do I create them one by one?"

**Abena:** "Figure it out."

---

### Q4 *(5 marks)*

**Task:** Create the entire structure above in a single command — including all nested subdirectories. Then display the full tree to verify. 📸 Screenshot the tree.

> 💡 **Hint:** Look up the `-p` flag for `mkdir` and research **brace expansion** in bash.

> **answers.md:** Which flag did you use and what does it do? What is brace expansion and how did it help here? Could you have done this without it — and would you want to?

---

*Abena checks his screen.*

**Abena:** "Good. Now — the pipeline also expects certain files to exist in those directories, even if empty. Placeholder files. If they're missing, scripts fail on first run."

---

### Q5 *(4 marks)*

**Task:** Create these five empty files in a single command:
`configs/app.conf`, `configs/db.conf`, `logs/access/access.log`, `logs/errors/error.log`, `reports/weekly_report.txt`

> **answers.md:** What does this command *actually* do beyond creating files? What happens if you run it on an existing file? Check `ls -l` before and after — what changes? Why does this behaviour matter in automation scripts?

---

### Q6 *(3 marks)*

**Task:** List `~/projects/cyphercore/configs/` in long format with human-readable file sizes.

> **answers.md:** What do the file sizes tell you about the files you just created? Break down the permission string on one file — explain every character group. What does the `-h` flag add?

---

### Q7 *(3 marks)*

**Task:** Display the full tree of `~/projects/cyphercore` again. 📸 Screenshot it.

> **answers.md:** How is `tree` different from `ls -R`? When would a DevSecOps engineer run `tree` on a live server — what would they be looking for?

---
---

# 🟡 SECTION 3 — Write and Read Files *(20 marks)*

---

*9:42 AM. Abena's phone buzzes.*

**Abena:** "Staging just threw errors. I need you to simulate what their application logs look like so we can practice triaging them."

She hands Kofi a notepad with three log lines:

```
2025-06-02 08:14:33 INFO  Application started successfully
2025-06-02 08:14:55 WARN  High memory usage detected: 87%
2025-06-02 08:15:10 ERROR Database connection timeout — retrying (attempt 1/3)
```

**Abena:** "Put those into the access log. One at a time. Do not overwrite the file."

---

### Q8 *(5 marks)*

**Task:** Write each of the three log lines into `logs/access/access.log` using `echo`, appending each one. Read the file back to confirm all three lines exist. 📸 Screenshot.

> **answers.md:** What is the difference between `>` and `>>`? Prove it — re-run the first echo with `>` instead of `>>`, then read the file. What happened? Restore the file. Why is confusing these two operators dangerous in a production log rotation script?

---

*Kofi finishes. Abena glances over.*

**Abena:** "Now read it. Both commands I showed you last week."

---

### Q9 *(4 marks)*

**Task:** Display the access log using two different reading commands — one from top to bottom, one from bottom to top.

> **answers.md:** What is the difference between the two? In a real incident, a log has 80,000 lines and the most recent events are at the bottom — which do you reach for first? What third command shows only the last 10 lines? (Research if needed.)

---

**Abena:** "Now the error log — four lines. Don't use echo four times. Write it the way you'd write it in a script."

She gives Kofi the entries:

```
2025-06-02 08:15:10 ERROR    Database connection timeout — retrying (attempt 1/3)
2025-06-02 08:15:13 ERROR    Database connection timeout — retrying (attempt 2/3)
2025-06-02 08:15:16 CRITICAL Database connection failed — all retries exhausted
2025-06-02 08:15:16 CRITICAL Triggering failover to secondary DB at 10.0.0.52
```

---

### Q10 *(6 marks)*

**Task:** Use heredoc notation to append all four lines into `logs/errors/error.log` in one operation. Read it back and 📸 screenshot.

> 💡 **Hint:** A heredoc starts with `<<` and a delimiter word (e.g. `EOF`). Everything between the opening and closing delimiter is written as-is. The closing delimiter must be alone on its line.

> **answers.md:**
> 1. What is a heredoc and what does it solve over multiple `echo` commands?
> 2. What is the difference between `'EOF'` (quoted) and `EOF` (unquoted)? Set a variable `DBNAME=cyphercore` and test both — screenshot the outputs and explain what you observe.
> 3. Why might someone on a compromised server prefer heredoc over opening `nano` or `vim`? What forensic traces does each method leave?

---

### Q11 *(5 marks)*

**Task:** Open the error log using two different pager commands. Navigate and quit each one.

> **answers.md:** Key differences between the two? Which loads the entire file into memory first? On a server with 512MB RAM and a 3GB log — which do you use? List three keyboard shortcuts for `less`: how to search, jump to the end, and quit.

---
---

# 🟡 SECTION 4 — Move and Clean Up *(10 marks)*

---

*10:05 AM. Standup is done.*

**Abena:** "Environment gets handed to staging this afternoon. Archive the error log with today's date in the filename, rename the access log with the date too, and remove any empty directories that shouldn't be there. Clean handover."

---

### Q12 *(4 marks)*

**Task:**
- Copy the error log to the archive folder as `error_2025-06-02.log`
- Rename the access log to `access_2025-06-02.log`

> **answers.md:** Fundamental difference between the two commands used? After renaming — does the original filename still exist? Verify with `ls` and 📸 screenshot. Does copying a large file duplicate all data on disk immediately?

---

### Q13 *(3 marks)*

**Task:**
- Create an empty directory `reports/temp_drafts`
- Remove it using the command designed for empty directories
- Attempt to remove the entire `logs/` directory using that same command

> **answers.md:** What happened when you tried to remove `logs/`? Why? Difference between `rmdir` and `rm -r`? What makes `rm -rf` dangerous and what rule should every engineer follow before running it?

---

### Q14 *(3 marks)*

**Task:** Display the full tree of `~/projects/cyphercore`. 📸 Screenshot.

> **answers.md:** Does the structure match Abena's original sticky note? Why does a clean, predictable directory structure matter for automation scripts, log agents, and security monitoring tools?

---
---

# 🔴 SECTION 5 — Links and Inodes *(20 marks)*

---

*2:00 PM. Abena drops into the chair beside Kofi.*

**Abena:** "This is what most juniors skip — and then they get confused in forensic investigations. Links. Do you know the difference between hard and soft?"

**Kofi:** "I've used `ln -s` for shortcuts."

**Abena:** "But do you know what it *is* at the filesystem level?"

She sketches on the whiteboard:

```
INODE TABLE
┌────────────┬─────────────────────┐
│  Inode 47  │  data: [block A, B] │  ← actual file content
└────────────┴─────────────────────┘
       ↑                 ↑
   db.conf         db_hardlink.conf
  (a name)          (another name)

Both names → same inode. Data survives as long as one name points to it.
```

**Abena:** "A filename is just a pointer to an inode. Hard links are extra pointers to the same inode. Soft links point to a filename — not an inode. That difference matters more than you think."

---

### Q15 *(5 marks)*

**Task:**
- Write three lines into `configs/db.conf`: `DB_HOST=10.0.0.10`, `DB_PORT=5432`, `DB_NAME=cyphercore_prod`
- Create a hard link to it in the same directory named `db_hardlink.conf`
- List the configs directory showing inode numbers alongside full file details

📸 Screenshot the output.

> 💡 **Hint:** The flag that shows inode numbers with `ls -l` is `-i`.

> **answers.md:** What do you notice about the inode numbers of both files? What does the link count (third column) represent? What is an inode in your own words?

---

### Q16 *(5 marks)*

**Task:** Delete the original `db.conf`. Then read the hard link file.

📸 Screenshot.

> **answers.md:** Is the data still there? Explain why using inodes and link counts. What would need to happen for the data to be permanently deleted? Check `ls -li` again — what changed in the link count? How could an attacker use hard links to hide data on a compromised system?

---

### Q17 *(5 marks)*

**Task:**
- Write some content into `configs/app.conf`
- Create a symbolic link to it inside `~/projects/cyphercore/` named `app_config_link`
- List `~/projects/cyphercore/` showing full details including link targets
- Delete the original `app.conf` and try to read the symlink

📸 Screenshot both the listing and the failed read.

> **answers.md:** What character in the listing identifies a symbolic link? What happened when you read the broken link — what is this called? Why does a dangling symlink in a deployment pipeline cause failures that are hard to debug at 2 AM?

---

### Q18 *(5 marks)*

> **answers.md** — fill in this table from your experiments. No guessing:

| Property | Hard Link | Soft Link |
|---|---|---|
| Shares inode with original? | | |
| Works across different filesystems? | | |
| Survives deletion of original? | | |
| Can link to a directory? | | |
| Shows as `l` in `ls -la`? | | |
| Detectable by matching inodes in `ls -li`? | | |

> After the table: one real-server use case for a hard link and one for a soft link in a DevSecOps context.

---
---

# 🔴 SECTION 6 — Data Streams and Redirection *(15 marks)*

---

*4:00 PM. Most of the team has gone quiet.*

**Abena:** "Last thing. Data streams — this is what trips up engineers who've been using Linux for years."

She puts a sticky note on Kofi's desk:

```
stdin   (0)  ←  input
stdout  (1)  →  normal output
stderr  (2)  →  error output
```

**Abena:** "Every process has these three. Errors go to stream 2 — not stream 1. That is why you can pipe output and still see errors bleeding onto your screen. They're on a different stream. Learn to control where each one goes."

---

### Q19 *(6 marks)*

**Task:**
- Run a single `ls` targeting two paths: one that exists (`logs/`) and one that does not
- Redirect normal output to `reports/stdout_output.txt`
- Redirect error output to `reports/stderr_output.txt`
- Read both files back

📸 Screenshot the outputs.

> 💡 **Hint:** `>` is shorthand for `1>`. Think of `2>&1` as "send stream 2 to wherever stream 1 is going."

> **answers.md:**
> 1. Which content landed where and why?
> 2. Name all three streams, their numbers, and what each carries.
> 3. What does `2>` mean specifically?
> 4. Run the same command with `2>&1 | cat` instead. Explain what `2>&1` does and where you'd use it in a real deployment script.

---

### Q20 *(5 marks)*

**Task:** Write the following report into `reports/weekly_report.txt` using a heredoc — in one operation:

```
========================================
WEEKLY SECURITY REPORT — CypherCore Systems
Week Ending: 2025-06-06
Prepared By: [Your Name]
========================================

SUMMARY:
No critical incidents recorded this week.
One WARN: memory usage spike at 08:14 on 2025-06-02.
One CRITICAL: DB connection failure at 08:15 on 2025-06-02.
Failover to secondary DB executed successfully.

RECOMMENDED ACTION:
Review DB connection pool settings before next deployment.
========================================
```

Read it back. 📸 Screenshot.

> **answers.md:**
> 1. Did you quote the delimiter or not — and why does that choice matter?
> 2. Set a variable `ANALYST="Your Name"`. Write two small heredocs — one quoted, one unquoted — both referencing `$ANALYST`. 📸 Screenshot both. What is the difference and why?
> 3. When do you use a quoted heredoc vs unquoted in a real script? Give a concrete example of each.

---

### Q21 *(4 marks)*

**Task:** Display the final tree of `~/projects/cyphercore`. 📸 Screenshot it.

> **answers.md:** Look at everything you built today — the structure, logs, archives, links, report. How does each connect to what a real DevSecOps engineer does daily? Pick two commands from today that changed how you think about Linux and explain why they matter beyond this bootcamp.

---
---

# 📦 SECTION 7 — Submission Instructions

---

## Step 1 — Organise Your Repo

```
lets-learn-linux-1/
├── answers.md
├── screenshots/
│   ├── q1.png
│   ├── q4_tree.png
│   └── ...         ← one screenshot per execute task
└── README.md       ← optional but encouraged
```

---

## Step 2 — Push to GitHub

```bash
git init
git add .
git commit -m "feat: LetsLearnLinux1 assignment - ParoCyber DevSecOps Bootcamp"
git remote add origin https://github.com/YOUR_USERNAME/lets-learn-linux-1.git
git push -u origin main
```

> ✅ Open your repo on GitHub and confirm all files and screenshots are visible before submitting.

---

## Step 3 — Post on LinkedIn

Write in your own voice — but your post must include:

1. A brief reflection on what you built and what clicked (3–5 sentences minimum)
2. Your GitHub repo link directly in the post
3. This closing line with correct tags:

> *This assignment is part of the DevSecOps training organised by [@ParoCyber](https://www.linkedin.com/company/parocyber) and facilitated by [@Samuel Nartey](https://www.linkedin.com/in/samuelnartey) — come check it out!*

**Example post:**

---

*Week three of the ParoCyber DevSecOps Bootcamp and this assignment changed how I think about Linux.*

*I built a deployment directory structure from scratch, wrote and archived simulated incident logs, broke and repaired symbolic links, and finally understood what an inode actually is. The hard link experiment was the moment everything clicked.*

*Full documentation and screenshots:*
*🔗 https://github.com/YOUR_USERNAME/lets-learn-linux-1*

*This assignment is part of the DevSecOps training organised by @ParoCyber and facilitated by @Samuel Nartey — come check it out!*

---

> ⚠️ **LinkedIn post = 5 marks.** No repo link or missing tags = 0 for this section.

---

## Step 4 — Submit

Send your GitHub repo link to your instructor before:

> **📅 12 June 2026 — 12:00 AM (Midnight). No exceptions.**

---
---

# ✅ Final Checklist

- [ ] `answers.md` has answers to all questions Q1 – Q21
- [ ] `screenshots/` has one screenshot per execute task
- [ ] Heredoc variable experiment (Q10 and Q20) is tested and screenshotted
- [ ] Hard/soft link comparison table (Q18) is fully completed
- [ ] `git log` shows at least one meaningful commit message
- [ ] GitHub repo is named `lets-learn-linux-1` and is **public**
- [ ] LinkedIn post is live with GitHub link and required tags
- [ ] Repo link submitted to instructor before the deadline

---

> *"The terminal doesn't care how confident you sound in a meeting. It only cares whether you know what you're doing."*
> — Abena Asante, Senior DevSecOps Engineer

---

*Assignment prepared for the ParoCyber DevSecOps Bootcamp | Facilitated by Samuel Nartey*