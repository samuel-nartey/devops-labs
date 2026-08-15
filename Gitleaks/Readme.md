# Gitleaks Lab: Secret Detection for Beginners

> A step-by-step, hands-on guide to Gitleaks — the free tool that scans your code (and your Git history) for secrets like passwords, API keys, and tokens that got committed by accident.

**Who this is for:** Beginners. No prior Gitleaks knowledge assumed. Basic Git and terminal use is enough — and Section 1.0 below explains even that from scratch.

**How this lab works:** Four levels. Each one builds on the last. You'll create real (but fake) secrets on purpose, scan for them, and see exactly what Gitleaks reports — so you learn by comparing what Gitleaks *should* find against a known answer key, not by guessing.

---

## Table of Contents

- [Level 1 — What Is Gitleaks & Installing It](#level-1--what-is-gitleaks--installing-it)
- [Level 2 — Your First Scans: `git`, `dir`, `stdin`](#level-2--your-first-scans-git-dir-stdin)
- [Level 3 — Config Files, Redacting, and Reports](#level-3--config-files-redacting-and-reports)
- [Level 4 — Stopping Leaks Automatically: Hooks & CI/CD](#level-4--stopping-leaks-automatically-hooks--cicd)
- [Appendix A — Full Command Reference](#appendix-a--full-command-reference)
- [Appendix B — Concept Glossary](#appendix-b--concept-glossary)
- [Appendix C — If You Find a Real Secret](#appendix-c--if-you-find-a-real-secret)
- [Appendix D — Why Gitleaks Sometimes Ignores What Looks Like a Secret](#appendix-d--why-gitleaks-sometimes-ignores-what-looks-like-a-secret)

---

## Level 1 — What Is Gitleaks & Installing It

### 1.0 Understanding folders and paths in this lab

Before touching Gitleaks at all, it's worth being completely sure about *where* you are in the filesystem at every step — almost every mistake in a lab like this comes from running a command in the wrong folder, not from the tool itself. This section explains every piece of path notation used later, so nothing is assumed.

**What `~` means.** In the terminal, `~` is shorthand for your *home directory*. On a standard Ubuntu EC2 instance logged in as the `ubuntu` user, that's `/home/ubuntu`. So `~/gitleaks-lab` and `/home/ubuntu/gitleaks-lab` refer to the exact same folder — the tilde is just a shortcut so you don't have to type the full thing every time.

Don't assume your username is `ubuntu`, though — confirm your own home directory with:
```bash
echo $HOME
```
Whatever that prints is what `~` expands to for you. Every `~/...` path in this guide is relative to that.

**Absolute vs. relative paths.** A path starting with `/` (like `/home/ubuntu/gitleaks-lab`) is called an *absolute* path — it means the same thing no matter where you currently are. A path that doesn't start with `/` (like `gitleaks-lab` or `./sim1`) is a *relative* path — it's interpreted relative to whatever folder you're currently sitting in. This lab mostly uses `~/...` paths (a mix of both — the `~` part is resolved to an absolute path first, then the rest is exact).

**Knowing where you are: `pwd`.** The command `pwd` stands for "print working directory" — it prints the full, absolute path of the folder you're currently in, with no ambiguity. You'll see `pwd` used after almost every `cd` command in this lab specifically so you can confirm you landed where you expected before running a scan. Get in the habit of running it yourself any time you're not 100% sure.

**Moving and creating folders.** `cd <path>` changes your current folder to `<path>`. `mkdir -p <path>` creates a new folder at `<path>` — the `-p` flag means "create any missing parent folders too, and don't complain if the folder already exists," which is why it's used throughout this lab instead of plain `mkdir`.

**Where this lab's files will end up.** By the time you finish all four levels, your home directory will contain this structure (paths shown as absolute, assuming your home directory is `/home/ubuntu` — substitute your own if `echo $HOME` printed something different):

```
/home/ubuntu/gitleaks-lab/
├── sim1/                     ← built in Level 2 (Simulation Lab #1)
│   ├── aws-config.py
│   ├── payment-config.js
│   ├── database.env
│   ├── deploy.sh
│   ├── internal.py           ← added in Level 3 (custom rule test)
│   ├── .gitleaks.toml        ← added in Level 3 (custom rule config)
│   └── new-secret.py         ← added in Level 4 (pre-commit hook test, its own git repo)
└── sim2/                     ← built in Level 2 (Simulation Lab #2)
    ├── .git/                 ← created by `git init`, stores full history
    └── secrets.py
```

Keep this diagram in mind as you work through the lab — every `mkdir` and `cd` command below is building exactly this, one piece at a time.

### 1.1 What problem does Gitleaks solve?

Imagine a developer writes this, just to get something working quickly:

```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DB_PASSWORD=Password123!
```

They commit it. They push it. The next day they fix it "properly" and delete those lines — feeling like the problem is gone.

**It is not gone.** Git remembers everything. Even though the lines are deleted from the current file, the old commit still contains them, and anyone with access to the repo's history can dig them out with a couple of Git commands. If the repo is ever made public, bots scan GitHub constantly for exactly this kind of leaked key — real keys get abused within minutes of being pushed.

> **Gitleaks does not manage or protect your secrets. It only detects secrets that are already exposed in your code or Git history**, so you can fix them.

> **📌 Note:** the values above (`AKIAIOSFODNN7EXAMPLE`, `wJalrXUtn...EXAMPLEKEY`) are the real, official example credentials from AWS's own documentation — they're shown here only to illustrate the *shape* of a leaked `.env` file. Don't use them later in this lab for a scan test; see [Appendix D](#appendix-d--why-gitleaks-sometimes-ignores-what-looks-like-a-secret) for why they won't trigger a finding even though they look exactly like real credentials.

### 1.2 Installing Gitleaks on Ubuntu (including AWS EC2)

**⚠️ Important — don't use `apt install gitleaks`.** Ubuntu's package repos carry an old, outdated build with no proper version number attached (running `gitleaks version` on it just prints `version is set by build process`, which is a dead giveaway). That old build only has the deprecated `detect`/`protect` commands and will confuse you later in this lab. Always install the official binary directly from GitHub instead.

**Step 1 — check nothing old is already installed:**
```bash
which gitleaks
```
`which` searches your `PATH` (the list of folders the shell looks in for programs) and prints the full path of the `gitleaks` program it would run, if any. If this prints a path (e.g. `/usr/bin/gitleaks`), check if `apt` owns it:
```bash
dpkg -S /usr/bin/gitleaks
```
If it says something like `gitleaks: /usr/bin/gitleaks`, remove it first:
```bash
sudo apt remove gitleaks -y
```

**Step 2 — check your CPU architecture** (this matters on AWS, since Graviton instances like `t4g`, `m6g`, `c7g` are ARM, not standard x86):
```bash
uname -m
```
- `x86_64` → most EC2 instance types, use the `linux_x64` download below
- `aarch64` → Graviton instances, use the `linux_arm64` download below

**Step 3 — download and install the official binary.** Every command below is run from your home directory (`cd ~` first), so the downloaded files land somewhere predictable and don't clutter whatever folder you happened to be in:

For `x86_64`:
```bash
cd ~
pwd                # confirm: should print your home directory, e.g. /home/ubuntu
curl -sSL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz -o gitleaks.tar.gz
tar -xzf gitleaks.tar.gz
sudo mv gitleaks /usr/local/bin/gitleaks
```

For `aarch64` / Graviton:
```bash
cd ~
pwd                # confirm: should print your home directory, e.g. /home/ubuntu
curl -sSL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_arm64.tar.gz -o gitleaks.tar.gz
tar -xzf gitleaks.tar.gz
sudo mv gitleaks /usr/local/bin/gitleaks
```

> **💡 What each line does:** `curl -sSL <url> -o gitleaks.tar.gz` downloads the release archive and saves it as `gitleaks.tar.gz` in your current folder (your home directory, since you just `cd ~`'d there). `tar -xzf gitleaks.tar.gz` extracts it, producing a plain `gitleaks` program file. `sudo mv gitleaks /usr/local/bin/gitleaks` moves that program into `/usr/local/bin/` — a folder that's already in every user's `PATH` on Ubuntu by default, which is *why* Step 4 below will be able to find it by typing just `gitleaks` from any folder, no matter where you are.

**Step 4 — verify it worked:**
```bash
hash -r
which gitleaks     # should print /usr/local/bin/gitleaks
gitleaks version   # should print 8.30.1, NOT "version is set by build process"
```
`hash -r` clears your shell's memory of where it last found the `gitleaks` command — without it, your terminal might keep running an old cached copy even after you've installed the new one.

If `which gitleaks` still points somewhere other than `/usr/local/bin/gitleaks`, that means an old copy is still earlier in your `PATH` — go back to Step 1 and remove it.

*(Not on Ubuntu? macOS users can run `brew install gitleaks` instead. Everyone else can use Docker: `docker pull zricethezav/gitleaks:latest`.)*

### 1.3 The one pattern to memorize

Every single Gitleaks command follows the same shape:

```
gitleaks  <command>  <options>  <target>
```

| Part | What it means | Example |
|---|---|---|
| `gitleaks` | The program itself | — |
| `<command>` | *What* to scan | `git`, `dir`, or `stdin` |
| `<options>` | *How* to scan (flags) | `-v`, `--redact`, `--config` |
| `<target>` | *Where* to scan | `.` (current folder), `./src`, a file path |

The `<target>` is almost always written as `.` in this lab — a single dot means "the folder I'm currently sitting in," i.e. whatever `pwd` would print at that moment. That's exactly why getting into the habit of checking `pwd` before scanning matters: `gitleaks dir .` scans a completely different set of files depending on where `.` currently points.

So `gitleaks git -v .` reads as: *"Gitleaks, scan Git history, be verbose, and use the current folder."* Keep coming back to this table any time a command looks confusing — every command in this lab is just this same shape with different pieces filled in.

> **A note about old tutorials:** if you ever see `gitleaks detect` or `gitleaks protect` in a video or blog post, that's the *old* command style — deprecated since version 8.19.0. They still technically work on old installs (like the `apt` version we just removed!) but the current commands are `git`, `dir`, and `stdin`. This whole lab uses the current style.

### 1.4 Before you start: generating fake secrets that actually get caught

Every simulation in this lab uses **planted fake secrets** so you can check Gitleaks' output against a known answer key. For that to work, the fake secret has to satisfy two things:

1. It must match the *shape* (regex pattern) of a real credential — e.g. an AWS key really does start with `AKIA` followed by 16 specific characters.
2. It must **not** look like an obvious placeholder — Gitleaks deliberately ignores well-known example strings and generic alphabet/number sequences to avoid flooding real projects with false positives from documentation. (Full explanation in [Appendix D](#appendix-d--why-gitleaks-sometimes-ignores-what-looks-like-a-secret).)

The snippet below generates safe, realistic-looking, non-placeholder fake values that satisfy both rules for the three services used throughout this lab. Run it any time you need a fresh batch — it doesn't matter which folder you're in when you run it, since it only prints text to your screen and doesn't read or write any files:

```bash
python3 -c "
import random, string
aws = 'AKIA' + ''.join(random.choices(string.ascii_uppercase + '234567', k=16))
stripe = 'sk_live_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
github = 'ghp_' + ''.join(random.choices(string.ascii_letters + string.digits, k=36))
print('AWS_ACCESS_KEY_ID =', aws)
print('STRIPE_KEY =', stripe)
print('GITHUB_TOKEN =', github)
"
```

> **Why these exact shapes?**
> - AWS access keys only ever use `A-Z` and the digits `2-7` after the `AKIA` prefix (this is Base32 encoding, and it's also what Gitleaks' rule regex specifically checks for) — a `9`, `8`, `0`, or `1` in that part won't match at all.
> - GitHub personal access tokens need to be **exactly 36 characters** after `ghp_` to match the dedicated `github-pat` rule; a shorter random string still gets flagged, just by the looser `generic-api-key` rule instead.
> - Stripe keys are the most forgiving (10–99 characters after `sk_live_`), so almost any random string of reasonable length works.

The rest of this lab uses this snippet's output wherever you see `<your generated AWS key>`, `<your generated Stripe key>`, and `<your generated GitHub token>`.

---

## Level 2 — Your First Scans: `git`, `dir`, `stdin`

### 2.1 The three scanning commands, explained simply

| Command | Scans | Ask yourself |
|---|---|---|
| `gitleaks dir` | Just the files sitting on disk right now | "Is there a secret in these files?" |
| `gitleaks git` | The Git repository's full history, every commit | "Did I *ever* commit a secret, even one I later deleted?" |
| `gitleaks stdin` | Whatever text is piped into it | "Scan this output from another command." |

`dir` is simpler to start with — no Git needed at all. `git` is more powerful because it also checks the past, not just the present. You'll use `dir` and `git` far more often than `stdin` as a beginner.

### 2.2 Simulation Lab #1 — a folder full of fake secrets

Let's build a small, safe practice folder with known fake secrets in it, so you can check Gitleaks' output against an answer key instead of guessing whether it's working.

**Create the folder and move into it.** This creates `sim1` nested inside a new `gitleaks-lab` folder in your home directory — matching the tree diagram from Section 1.0:
```bash
mkdir -p ~/gitleaks-lab/sim1
cd ~/gitleaks-lab/sim1
pwd
```
The `pwd` output should be the absolute version of `~/gitleaks-lab/sim1` — for example `/home/ubuntu/gitleaks-lab/sim1`. If it isn't, stop here and re-run the `cd` command before continuing; every command in the rest of this section assumes you're standing exactly in this folder.

**Generate your fake values** using the snippet from [Section 1.4](#14-before-you-start-generating-fake-secrets-that-actually-get-caught), then create four files, each with one fake secret (replace the placeholders below with your generated values). Each `echo '...' > filename` command creates a new file in your *current* folder (`~/gitleaks-lab/sim1`, confirmed above) containing that one line — the `>` symbol means "write this text into this file, overwriting it if it already exists":

```bash
echo 'AWS_ACCESS_KEY_ID = "<your generated AWS key>"' > aws-config.py

echo 'STRIPE_KEY = "<your generated Stripe key>"' > payment-config.js

echo 'DB_PASSWORD = "SuperSecretPass123!"' > database.env

echo 'GITHUB_TOKEN = "<your generated GitHub token>"' > deploy.sh
```

Confirm the four files landed where you expect before scanning:
```bash
pwd
ls -la
```
You should see `aws-config.py`, `payment-config.js`, `database.env`, and `deploy.sh` listed, all inside `~/gitleaks-lab/sim1`.

**📋 Answer key — what you should see when you scan this folder:**

| File | Fake secret planted | Expected Gitleaks rule ID |
|---|---|---|
| `aws-config.py` | AWS access key | `aws-access-token` |
| `payment-config.js` | Stripe live key | `stripe-access-token` |
| `database.env` | Plain password | **Not expected to trigger.** Plain English-style passwords have no fixed pattern the way an API key does, so none of the default rules match them. Catching these needs a custom rule or an entropy-based generic-secret rule tuned for your own naming conventions (more in Level 3). |
| `deploy.sh` | GitHub personal access token | `github-pat` |

Now scan it. Since you're already standing in `~/gitleaks-lab/sim1` (double-check with `pwd` if you've done anything else in between), the `.` target means exactly this folder:

```bash
gitleaks dir .
```

Compare what prints to your terminal against the answer key table above. You should see exactly 3 findings (the AWS key, the Stripe key, and the GitHub token), and each `File:` line in the output should read one of `aws-config.py`, `payment-config.js`, or `deploy.sh` — not a full path, because Gitleaks prints paths relative to the folder you scanned from. The plain password is the trickiest one and a good discussion point — real secrets are rarely just an English word plus numbers, which is also exactly why they're harder for a tool like Gitleaks to catch reliably.

### 2.3 Simulation Lab #2 — proving Git history never forgets

This is the single most important lesson in the whole lab. Let's prove it ourselves instead of just reading about it.

**Create a separate, independent folder for this simulation** — a sibling of `sim1`, not nested inside it, so the two labs never interfere with each other:
```bash
mkdir -p ~/gitleaks-lab/sim2
cd ~/gitleaks-lab/sim2
pwd
```
The `pwd` output should now be the absolute version of `~/gitleaks-lab/sim2` — for example `/home/ubuntu/gitleaks-lab/sim2`. Note this is a *different* folder from Simulation Lab #1 (`sim1`) — don't run the commands below inside `sim1` by mistake.

**Turn this folder into a Git repository:**
```bash
git init
```
`git init` creates a hidden `.git` subfolder right here inside `sim2` (i.e. at `~/gitleaks-lab/sim2/.git`) — that hidden folder is where Git will store every commit's full history from now on. You won't interact with `.git` directly, but it's what `gitleaks git .` reads from later in this exercise.

**Step 1 — commit a fake secret.** Generate a fresh AWS key with the [Section 1.4](#14-before-you-start-generating-fake-secrets-that-actually-get-caught) snippet and use it here (don't reuse the one from Simulation Lab #1 — a clean example keeps the two labs independent). Make sure you're still in `~/gitleaks-lab/sim2` (`pwd` to check) before running this:
```bash
echo 'AWS_ACCESS_KEY_ID = "<your generated AWS key>"' > secrets.py
git add .
git commit -m "add database config"
```
`git add .` stages every changed file in the current folder (here, just the new `secrets.py`) — "staging" means marking it as ready to be included in the next commit. `git commit -m "..."` then actually records that staged snapshot into the repository's permanent history, with the quoted text as a human-readable message describing what changed.

**Step 2 — scan the current files with `dir` — it's here, of course:**
```bash
pwd
gitleaks dir .
```
✅ You should see the finding (`aws-access-token`), and the `File:` line in the output should read `secrets.py`.

**Step 3 — now "delete" the secret, like a developer fixing their mistake.** Still inside `~/gitleaks-lab/sim2`:
```bash
echo '' > secrets.py
git add .
git commit -m "remove secret, oops"
```
This overwrites `secrets.py` with an empty line, then commits that change as a *new* entry in the history — it does not erase the earlier commit, it just adds one more on top of it.

**Step 4 — scan the current files again with `dir`:**
```bash
gitleaks dir .
```
❌ Nothing found — the file is empty now. Looks clean, right?

**Step 5 — now scan the same folder with `git` instead:**
```bash
gitleaks git .
```
✅ **It finds it anyway.** This is the whole point — `git` mode reads Git's history, not just the files sitting on disk right now. You can double check it yourself, outside of Gitleaks entirely, still from `~/gitleaks-lab/sim2`:
```bash
git log --all -p -- secrets.py
```
That command shows you the old commit still sitting there, secret and all. (`--all` means "check every branch," `-p` means "show the actual line-by-line changes," and `-- secrets.py` limits it to just that one file's history.)

> **Lesson:** deleting a secret in a new commit does **not** remove it from the repository. The only real fixes are (1) rewrite history to actually erase the old commit, and (2) rotate the real credential at its source so the old leaked value stops working. Appendix C covers this properly.

### 2.4 Verbose mode — seeing more detail

Add `-v` (short for `--verbose`) to any command to see more detail about what's being scanned:

```bash
gitleaks git -v .
```

Useful when you're not sure whether Gitleaks is actually looking at the files you expect it to — the verbose output will confirm exactly which folder and files it opened.

---

## Level 3 — Config Files, Redacting, and Reports

### 3.1 Redacting — don't print secrets to your terminal or CI logs

By default, Gitleaks may show you a chunk of the actual matched secret in its output. That's fine on your own laptop, but a real problem in shared CI logs (anyone who can view the pipeline log can now see the leaked key too). Use `--redact` to mask it:

```bash
gitleaks git --redact .
```

This should become your everyday default command once you're past the learning stage:

```bash
gitleaks git --redact .        # scan a Git repo, hide secret values in output
gitleaks dir --redact .        # scan plain files, hide secret values in output
```

### 3.2 Where do the scanning rules come from?

You don't need to write any configuration to start — Gitleaks ships with a large set of built-in rules (AWS keys, GitHub tokens, Slack webhooks, Stripe keys, and more) baked directly into the program itself. That's what caught the secrets in Simulation Lab #1 with zero setup.

You only need your own config file when you have a real reason to, such as:
- your company issues its own custom-shaped tokens the default rules don't recognize
- you're getting false positives you want to silence

### 3.3 Writing a simple custom rule

**Scenario:** your company issues internal keys shaped like `PAROCYBER_LIVE_` followed by letters and numbers. The default rules have never seen this format, so Gitleaks won't catch it unless you teach it.

**Move back into the Simulation Lab #1 folder** for this exercise (this section builds on the files already there):
```bash
cd ~/gitleaks-lab/sim1
pwd
```
Confirm this prints the absolute version of `~/gitleaks-lab/sim1` before continuing.

Create a file named exactly `.gitleaks.toml` **in this same folder** (`~/gitleaks-lab/sim1`) — Gitleaks specifically looks for a file with this exact name sitting in the folder being scanned, so the name and location both matter:

```toml
title = "My Custom Gitleaks Config"

# Keep all the built-in rules AND add mine
[extend]
useDefault = true

[[rules]]
id = "parocyber-internal-key"
description = "ParoCyber internal API key"
regex = '''PAROCYBER_LIVE_[a-zA-Z0-9]{20}'''
```

Two things to notice:
- **`[extend] useDefault = true`** is important — without this line, your file *replaces* all the built-in rules instead of adding to them, and you'd silently lose AWS/GitHub/Stripe detection.
- Gitleaks automatically looks for a `.gitleaks.toml` file sitting in the folder you're scanning — you don't have to point to it manually. But if you want to be explicit (e.g. it's stored somewhere else, at a different path), you can say so directly:

```bash
gitleaks git --config .gitleaks.toml .
```

**Try it.** Still inside `~/gitleaks-lab/sim1`:
```bash
pwd
echo 'INTERNAL_KEY = "PAROCYBER_LIVE_abc123XYZ789def456ghi"' > internal.py
gitleaks dir .
```
Without the config file, this is invisible to Gitleaks. Add the `.gitleaks.toml` file above into that same folder (`~/gitleaks-lab/sim1`, right alongside `internal.py`) and scan again — now it's caught.

### 3.4 Ignoring a false positive (allowlisting)

Sometimes something *looks* like a secret but isn't — test data, documentation examples, placeholder values. The simplest fix, right at the source line:

```python
TEST_API_KEY = "sk_test_FAKE00000000000000000000"  # gitleaks:allow
```

That inline comment tells Gitleaks to skip that exact line. This is the beginner-friendly option — just add the comment next to anything you've confirmed is genuinely fake.

> **📌 You've actually already seen this concept in action** — just built into Gitleaks itself rather than added by you. See [Appendix D](#appendix-d--why-gitleaks-sometimes-ignores-what-looks-like-a-secret) for how Gitleaks' own default rules do the same kind of allowlisting automatically for extremely common placeholder values.

### 3.5 Saving a report instead of just printing to screen

Still from `~/gitleaks-lab/sim1` (or any folder you're scanning — the report file gets written into your *current* folder unless you specify otherwise):

```bash
gitleaks git --report-format json --report-path gitleaks-report.json .
```

Breaking that down using our syntax pattern from Level 1.3:
- `git` → command: scan Git history
- `--report-format json --report-path gitleaks-report.json` → options: save the results as a JSON file with this name
- `.` → target: current folder

You'll now have a `gitleaks-report.json` file sitting right there in your current folder (e.g. `~/gitleaks-lab/sim1/gitleaks-report.json`) that you can open, share, or feed into another tool — confirm it exists with `ls -la`. `csv` is another simple option if you want something you can open in a spreadsheet:
```bash
gitleaks git --report-format csv --report-path gitleaks-report.csv .
```

---

## Level 4 — Stopping Leaks Automatically: Hooks & CI/CD

Everything so far has been *you* remembering to run a scan. The real goal is to make Gitleaks run automatically, so nobody has to remember.

### 4.1 Pre-commit hook — block the secret before it's even committed

This is the earliest point you can catch a leak — before it ever enters Git history at all.

**Simple version, no extra tools needed.** This has to be done inside a folder that's already a Git repository, because the hook lives inside that repo's own `.git` folder. We'll reuse `~/gitleaks-lab/sim1` and turn it into a Git repo along the way:
```bash
cd ~/gitleaks-lab/sim1
pwd
```

Open the hook file for editing — note the exact path: `.git/hooks/pre-commit`, *inside* the repo's hidden `.git` folder:
```bash
nano .git/hooks/pre-commit
```
Paste this in:
```bash
#!/bin/sh
gitleaks git --pre-commit --staged --redact
exit $?
```
Save the file (in `nano`: `Ctrl+O` then `Enter` to write, `Ctrl+X` to exit), then make it runnable:
```bash
chmod +x .git/hooks/pre-commit
```
`chmod +x` adds "execute" permission to the file — without this, Git will see the hook file but refuse to actually run it as a program.

Now every time you run `git commit` **from inside this folder**, Gitleaks automatically checks what you're about to commit first. If it finds a secret, the commit is blocked and you fix it before it ever becomes part of your project's permanent history.

**Test it.** Generate one more fresh fake secret with the [Section 1.4](#14-before-you-start-generating-fake-secrets-that-actually-get-caught) snippet — using a real placeholder-style value here won't trigger the hook, which defeats the point of the test. Still working from `~/gitleaks-lab/sim1`:
```bash
pwd
echo 'NEW_KEY = "<your generated AWS key>"' > new-secret.py
git init      # only needed if this folder isn't already a git repo from an earlier section
git add new-secret.py
git commit -m "test"
```
The commit should be refused, with Gitleaks' finding printed instead — the `pre-commit` hook you just created intercepted it before Git ever recorded it into history.

### 4.2 A simple CI check — GitHub Actions

A pre-commit hook only protects your own machine — a teammate could skip it or simply not have it installed. A CI check is the backstop that runs on GitHub's servers, so it can't be skipped.

**This file has to live at an exact path inside your repository** — `.github/workflows/gitleaks.yml`, relative to the repo's root folder (i.e. `~/gitleaks-lab/sim1/.github/workflows/gitleaks.yml` if you're continuing in that same folder, once it's pushed to an actual GitHub repository). GitHub specifically looks in `.github/workflows/` for any `.yml` files defining automated jobs — this isn't a suggestion, the path is a hard requirement of how GitHub Actions works.

Create the folders and the file:
```bash
mkdir -p .github/workflows
nano .github/workflows/gitleaks.yml
```

Paste this in:

```yaml
name: gitleaks

on: [pull_request, push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # get FULL history, not just the latest commit

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

This is a YAML file — a plain-text configuration format that uses indentation (spaces, not tabs) to show structure, similar to how folders nest inside folders. GitHub Actions reads this specific file to know what to run and when.

Two lines that confuse beginners:
- **`fetch-depth: 0`** — GitHub only downloads the newest commit by default, not the full history. Since Gitleaks needs to check history, tell it to fetch everything.
- **`gitleaks-action@v3`** — use `v3`, not the older `v2`. GitHub is removing the software `v2` depends on (Node 20) on September 16, 2026, so `v2` will stop working after that date.

Once this file is committed and pushed to an actual GitHub repository (this local practice lab alone won't trigger it — GitHub Actions only runs on GitHub's own servers), every future pull request automatically gets scanned — a red ❌ appears on the PR if a secret is found, blocking the merge until it's fixed.

---

## Appendix A — Full Command Reference

```bash
# Check install
gitleaks version
gitleaks --help

# Scan just the files on disk (no Git needed)
gitleaks dir .

# Scan full Git history
gitleaks git .

# Scan only what's staged for commit (used in pre-commit hooks)
gitleaks git --pre-commit --staged .

# Scan piped-in text
cat some_file | gitleaks stdin

# Verbose output
gitleaks git -v .

# Hide secret values from the printed output
gitleaks git --redact .

# Use a specific config file
gitleaks git --config .gitleaks.toml .

# Save a report instead of printing to screen
gitleaks git --report-format json --report-path report.json .
gitleaks git --report-format csv --report-path report.csv .

# Check the exit code (0 = clean, 1 = secrets found)
gitleaks git . ; echo $?
```

---

## Appendix B — Concept Glossary

| Term | Plain-English definition |
|---|---|
| **`~`** | Shorthand for your home directory (e.g. `/home/ubuntu`) — check yours with `echo $HOME` |
| **Absolute path** | A path starting with `/`, meaning the same folder no matter where you currently are (e.g. `/home/ubuntu/gitleaks-lab`) |
| **Relative path** | A path that doesn't start with `/`, interpreted relative to your current folder (e.g. `./sim1`) |
| **`pwd`** | "Print working directory" — shows the full absolute path of the folder you're currently in |
| **Secret** | Any credential that grants access — password, API key, token, private key |
| **Rule** | A pattern Gitleaks uses to recognize one specific type of secret (e.g. an AWS key always starts with `AKIA`) |
| **`dir` command** | Scans plain files on disk right now — no Git awareness |
| **`git` command** | Scans a Git repository's full commit history |
| **`stdin` command** | Scans text piped in from another command |
| **`--redact`** | Hides the actual secret value in the printed output, showing only that *something* was found |
| **`.gitleaks.toml`** | Your own optional config file, used to add custom rules or ignore false positives — must sit in the folder being scanned |
| **`gitleaks:allow`** | An inline comment you add next to a line to tell Gitleaks to ignore it |
| **Allowlist** | A rule-level or global exception list Gitleaks checks *before* reporting a match — if the matched text (or the file path) fits an allowlist entry, the finding is silently dropped |
| **Stopword** | A specific substring (like a well-known placeholder pattern) that, if found anywhere inside a matched secret, causes Gitleaks to discard that finding globally, across every rule |
| **Pre-commit hook** | A script that runs automatically every time you type `git commit`, before the commit is created — lives at `.git/hooks/pre-commit` inside a repo |
| **Exit code** | A number the program returns when it finishes — `0` means clean, `1` means it found something. This is what lets a CI pipeline or hook automatically decide pass/fail |

---

## Appendix C — If You Find a Real Secret

Finding a leak is only the first step — what you do next, and in what order, matters a lot:

1. **Rotate the credential immediately, first.** Go to AWS IAM, Stripe, GitHub, or wherever the credential lives, and revoke/regenerate it *before* anything else. Deleting it from your code does nothing if the live, working credential is still out there.
2. **Remove it from Git history**, not just the current file — a normal delete-and-commit (as you saw in Simulation Lab #2) is not enough. Tools like `git filter-repo` exist for this, but it's a more advanced step best done carefully, ideally with a senior teammate the first time.
3. **Force-push the cleaned history**, and have every other collaborator re-clone the repo (rewritten history breaks their existing copies).
4. **Add a rule or allowlist entry** so this type of leak is caught automatically next time.

Step 1 always comes before step 2. A secret still visible in old Git history, but already rotated, is just a harmless historical record. A secret you deleted from Git but never rotated is still a live, working risk.

---

## Appendix D — Why Gitleaks Sometimes Ignores What Looks Like a Secret

If you plant a fake secret and Gitleaks reports **"no leaks found,"** it doesn't automatically mean something is broken. Gitleaks ships with two built-in mechanisms specifically designed to recognize "this is obviously a documentation placeholder, not a real leak" — and it's worth understanding both, because you'll run into them again in real projects.

### D.1 Rule-level allowlists

Some individual rules carry their own exception list. The AWS access key rule is a good example — its actual definition (from Gitleaks' default config) includes:

```toml
[[rules]]
id = "aws-access-token"
regex = '''\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b'''
entropy = 3
[[rules.allowlists]]
regexes = [
    '''.+EXAMPLE$''',
]
```

That last block means: *any AWS key ending in the literal word `EXAMPLE` is automatically ignored* — regardless of how well it otherwise matches the pattern. This exists because `AKIAIOSFODNN7EXAMPLE` is AWS's **own official example key** from their public documentation, and it appears in an enormous number of tutorials, README files, and Stack Overflow answers. Without this exception, every project that ever copied an AWS doc snippet would show a false "leak."

### D.2 Global stopwords

Separately, Gitleaks maintains a small list of **stopwords** that apply to *every* rule, not just one. One of them is the literal string:

```
abcdefghijklmnopqrstuvwxyz
```

Before reporting any finding, Gitleaks lowercases the matched secret and checks whether it contains any stopword as a substring. A token like `ghp_1234567890abcdefghijklmnopqrstuvwxyz12` contains that exact alphabet run, so it gets silently discarded — even though it perfectly matches the GitHub token *pattern* and has reasonable entropy. The same applies to case-scrambled versions like `aBcDeFgHiJkLmNoPqRsTuVwXyZ`, since the comparison is case-insensitive.

### D.3 Why this matters for you

Both mechanisms exist for the same reason: **sequential, alphabetical, or famous example strings are extremely common in tutorials, tests, and boilerplate — but essentially never appear in a real leaked credential**, because real credentials come from a cryptographically random generator. Gitleaks trades away detection of these specific placeholder values in exchange for not spamming every developer who's ever copy-pasted a code sample with a false alarm.

**The practical takeaway for this lab:** when you plant a fake secret to test Gitleaks, make sure it's *randomly* generated rather than a famous example or an alphabet/number sequence. The generator in [Section 1.4](#14-before-you-start-generating-fake-secrets-that-actually-get-caught) does this for you. If a real finding ever goes unexpectedly quiet on you outside this lab, it's worth asking the same question: *is this value close enough to a known placeholder pattern that Gitleaks' own false-positive protection is filtering it out?*
