# GitHub Actions Mastery Lab
## Levels 1–4: Fundamentals → YAML → Workflow Anatomy → Steps & Actions

> Work through each concept in order. Before any hands-on lab, look at the **Sample Workflow** for that section — every line is commented so you can see the shape before you write your own. Answers to questions are hidden in collapsible `Show Answer` blocks so you can try first.

---

# LEVEL 1: Fundamentals

## 1.1 What is CI/CD, and why automate?

**Explain it simply:** Imagine every time you wanted to serve a customer at a restaurant, the chef had to personally walk to the farm, pick vegetables, drive back, and cook from scratch — every single order. That's manual software delivery: build, test, and deploy done by hand, every time, by a person. CI/CD is the kitchen line: prepped ingredients, standard stations, repeatable steps, so food (code) goes out fast and consistent.

- **CI (Continuous Integration):** every time code changes, automatically build and test it.
- **CD (Continuous Delivery/Deployment):** automatically package and ship that tested code toward production.

**Why it matters:** humans forget steps, get tired, and skip tests under deadline pressure. Machines don't.

**When NOT to over-automate:** a one-person weekend prototype repo doesn't need a 12-stage pipeline. Automation pays off once more than one person touches the code, or the deploy has real consequences.

### Try It Now
Answer in your own words (write 2–3 sentences):
1. Name one bug or outage you've heard of that automated testing could have caught before it shipped.
2. If you had to explain CI/CD to a non-technical friend using an analogy *other* than the restaurant one, what would you use?

<details>
<summary>Show Answer</summary>

There's no single right answer here — this is a reflection exercise. A strong answer for (1) names a specific real or plausible failure (e.g., a deploy that skipped a broken-login check). A strong answer for (2) picks any repeatable-process analogy (an assembly line, an airport pre-flight checklist, a bakery's daily bread routine) and clearly maps "check happens automatically every time" onto it.
</details>

---

## 1.2 How GitHub Actions works internally

**Explain it simply:** GitHub Actions is an event-driven robot assistant living inside your repo. Something happens (an **event**, like a push) → the robot checks its instructions (a **workflow** file) → it spins up a disposable computer (a **runner**) → it does the steps you wrote → then throws that computer away.

**The chain, in order:**

```
Event (e.g. push to main)
   ↓
Workflow file (.github/workflows/*.yml) listens for that event
   ↓
Workflow triggers one or more Jobs
   ↓
Each Job runs on a Runner (a fresh virtual machine or container)
   ↓
Each Job runs a sequence of Steps
   ↓
Steps either run shell commands, or call a pre-built Action
```

**Why / when to use it:** this model is why Actions scales — every run starts from a clean slate, so you never get "works on my machine" drift.

### Try It Now
Replace "push to main" in the chain above with three other events you can imagine triggering a workflow. No syntax needed yet — just the concept.

<details>
<summary>Show Answer</summary>

Reasonable substitutes: "someone opens a pull request," "a maintainer manually clicks Run," "midnight arrives (a scheduled timer)." Any real GitHub event works — the point is recognizing that *any* trigger feeds into the same Workflow → Job → Runner → Step chain.
</details>

---

## 1.3 Runners: hosted vs self-hosted

**Explain it simply:** A runner is the computer that actually executes your steps. GitHub gives you rental computers (**GitHub-hosted runners** — Ubuntu, Windows, macOS images, wiped clean after every job). Or you can bring your own computer and register it as a **self-hosted runner** — useful if you need special hardware, private network access, or want to avoid paying per-minute for hosted runners.

| | GitHub-hosted | Self-hosted |
|---|---|---|
| Setup | Zero setup | You install & maintain the agent |
| Cost | Free minutes, then billed | Your own infrastructure cost |
| Environment | Fresh every run | Persists between runs (you manage state) |
| Use case | Most projects | Special hardware, internal network, GPUs, compliance |

**Best practice:** default to GitHub-hosted runners until you have a *specific* reason (cost at scale, private resources, custom hardware) to self-host.

### Try It Now
For each scenario below, write "hosted" or "self-hosted":
1. A public open-source Node.js library with light CI needs.
2. A pipeline that must deploy to a server inside a private corporate network with no internet exposure.
3. A team running thousands of test minutes/day trying to cut cloud costs.

<details>
<summary>Show Answer</summary>

1. Hosted — no special requirements, GitHub's free/cheap runners are perfectly fine.
2. Self-hosted — the runner needs network access GitHub's cloud runners don't have.
3. Self-hosted — at high volume, your own hardware becomes cheaper than paying per-minute.
</details>

---

## 1.4 Events: what can trigger a workflow

**Explain it simply:** Events are the doorbell. Something happens on GitHub, and if your workflow is "listening" for that doorbell sound, it runs.

**Common events:**
- `push` — code pushed to a branch
- `pull_request` — a PR opened/updated
- `schedule` — runs on a cron timer, like an alarm clock
- `workflow_dispatch` — a manual "run now" button
- `release` — a GitHub release is published

### Try It Now
Which event would you use for each?
1. "Run tests every night at 2 AM regardless of whether anyone pushed code."
2. "Let me click a button in the GitHub UI to trigger a deploy on demand."
3. "Run tests automatically whenever someone proposes a code change for review."

<details>
<summary>Show Answer</summary>

1. `schedule`
2. `workflow_dispatch`
3. `pull_request`
</details>

---

## 1.5 Anatomy of a workflow file (preview)

**Explain it simply:** Every workflow file is a YAML file living at `.github/workflows/<name>.yml`. It's a recipe card: what triggers it, what jobs to run, and what steps each job does. We'll go syntax-deep in Level 3 — for now, just recognize the shape.

### Sample Workflow (fully commented)

```yaml
# .github/workflows/hello.yml
# This is the whole file — read every comment before moving on.

name: My First Workflow        # Cosmetic label shown in the "Actions" tab on GitHub.
                                # Purely for humans — has no effect on behavior.

on: push                       # The trigger. "push" means: run this workflow any time
                                # anyone pushes a commit to any branch in this repo.

jobs:                          # "jobs" is a mapping (dictionary): job-id -> job-definition.
                                # You can have one job or many; each is independent unless
                                # you link them later with "needs" (Level 3).

  say-hello:                   # This is a job ID. You choose this name yourself.
                                # No spaces allowed — use hyphens or underscores.

    runs-on: ubuntu-latest      # Which OS image this job's runner uses. "ubuntu-latest"
                                # is the most common default — a fresh Ubuntu VM.

    steps:                     # "steps" is an ordered LIST (note the dashes below).
                                # Order matters: step 1 fully finishes before step 2 starts.

      - name: Print a greeting  # "name" here just labels this one step in the logs.
        run: echo "Hello, GitHub Actions!"
                                # "run" executes a literal shell command on the runner.
```

**Line by line recap:**
- `name:` — cosmetic label for the whole workflow (optional but recommended).
- `on:` — the trigger event(s).
- `jobs:` — a mapping of job-id → job-definition.
- `runs-on:` — which OS/runner image the job executes on.
- `steps:` — an ordered list of actions to perform in that job.
- `run:` — a literal shell command to execute.

### Try It Now
**Lab 1.5 — Your first real workflow.**
1. In your repo, create the folder path `.github/workflows/`.
2. Create a file called `hello.yml` inside it.
3. Copy the sample above exactly, but change the greeting message to include your name.
4. Commit and push to your default branch.
5. Go to the **Actions** tab on GitHub and confirm it ran and printed your custom message.

**Expected output:** A green checkmark on the workflow run, and your custom greeting visible in the step logs.

**What likely breaks:**
- Folder typo'd as `.github/workflow/` (missing the "s") → GitHub won't detect it at all.
- Wrong file extension (`.yaml` is fine, `.yml.txt` is not).
- Bad indentation → workflow fails to parse, shows a red "invalid workflow file" banner instead of running.

**Best practice:** one workflow file per logical process (e.g., `ci.yml`, `deploy.yml`) rather than one giant file for everything.

---

## Level 1 Quiz
1. What are the four layers in the chain from "event" to "step" in GitHub Actions?
2. True/False: GitHub-hosted runners persist state between separate workflow runs.
3. Which event would you use to run a workflow every day at midnight?
4. What folder path (exact) must workflow files live in?
5. Spot the bug:
   ```yaml
   name: Broken
   on push
   jobs:
     test:
       runs-on: ubuntu-latest
   ```
6. Why might a team choose a self-hosted runner over a GitHub-hosted one?

<details>
<summary>Show Answers</summary>

1. Event → Workflow → Job → Step (with Runner sitting under Job as what executes it).
2. False — hosted runners are wiped clean and fresh for every run.
3. `schedule`.
4. `.github/workflows/`.
5. Missing colon after `on` (should be `on: push`), and no `steps:` defined under the `test` job.
6. Private network access, special hardware (GPUs), or cutting cost at high volume.
</details>

---

# LEVEL 2: YAML Mastery

YAML ("YAML Ain't Markup Language") is the format every GitHub Actions workflow is written in. It's whitespace-sensitive — meaning **spacing is not cosmetic, it's structural**. Get this level solid or every later level will feel like fighting quicksand.

## 2.1 Indentation

**Explain it simply:** YAML uses indentation the way outlines use bullet nesting — indentation *is* the parent/child relationship. There are no braces `{}` or brackets to show nesting, just spaces.

**Rules:**
- Use **spaces only, never tabs**. Tabs will break parsing.
- Each nested level is indented consistently (2 spaces is the GitHub Actions convention).
- Items at the same indentation level are siblings (same "rank").

### Sample Workflow (fully commented, indentation focus)

```yaml
name: Indentation Demo
on: push

jobs:                      # level 0
  build:                   # 2 spaces in -> child of "jobs"
    runs-on: ubuntu-latest  # 4 spaces in -> child of "build", sibling of "steps"
    steps:                 # 4 spaces in -> child of "build"
      - name: First step    # 6 spaces + dash -> first item of the "steps" list
        run: echo "one"      # 8 spaces -> child of THIS list item, not a new item
      - name: Second step   # 6 spaces + dash -> second item, same rank as "First step"
        run: echo "two"
```

Notice: `name:` and `run:` under "First step" line up at the same indentation — they're both properties of that single step. The next `-` starts a brand-new sibling step.

### Try It Now
**Lab 2.1 — Fix the broken indentation.**
```yaml
jobs:
build:
  runs-on: ubuntu-latest
    steps:
    - run: echo hi
```
Rewrite this so `build` is a child of `jobs`, `runs-on` and `steps` are children of `build`, and the step list is properly nested.

<details>
<summary>Show Answer</summary>

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
```
`build` moves in 2 spaces to become a child of `jobs`. `runs-on` and `steps` sit at the same indentation (4 spaces) as siblings under `build`. The step list item aligns 2 spaces deeper than `steps:`.
</details>

---

## 2.2 Mappings (key: value)

**Explain it simply:** A mapping is just a labeled box: `key: value`. Almost everything in a workflow file is a mapping.

```yaml
name: CI Pipeline
runs-on: ubuntu-latest
```

**Rule:** always a space after the colon. `name:CI` (no space) is invalid; `name: CI` is correct.

### Try It Now
Write a 3-line mapping describing yourself: `name:`, `role:`, `favorite_language:` with a colon-space between each key and value.

<details>
<summary>Show Answer</summary>

```yaml
name: Jamie
role: Backend Developer
favorite_language: Python
```
Any values are fine — the check is: colon immediately after the key, then a single space, then the value.
</details>

---

## 2.3 Lists (sequences)

**Explain it simply:** A list is an ordered set of items, each marked with a dash `-`. Steps in a job are a list because order matters — step 1 must finish before step 2 starts.

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  - name: Run tests
    run: npm test
```

**Line by line:** each `-` starts a new list item. Everything indented under that dash (at the same level) belongs to *that* item — here, each step is itself a small mapping (`name:` and `uses:`/`run:`).

### Try It Now
**Lab 2.3.** Write a `steps:` list with three items: one that checks out code (`uses: actions/checkout@v4`), one that runs `echo "step 2"`, and one that runs `echo "step 3"`.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  - name: Step two
    run: echo "step 2"
  - name: Step three
    run: echo "step 3"
```
</details>

---

## 2.4 Strings, multiline strings, and comments

**Explain it simply:** Most strings in YAML don't need quotes at all (`runs-on: ubuntu-latest`). Quotes matter when a value could be misread as something else (a number, a boolean, or contains special characters like `:`).

**Multiline strings** — for running several shell commands in one step, use `|` (keep line breaks) or `>` (fold into one line):

### Sample Workflow (fully commented)

```yaml
name: Multiline Demo
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # This comment explains the next step — comments are ignored by the parser,
      # they exist purely to leave notes for humans reading the file later.
      - name: Run several commands in sequence
        run: |
          echo "Step A"        # the "|" keeps each line as its own separate command
          echo "Step B"
          echo "Step C"

      - name: Fold into one line
        run: >
          echo "This long sentence
          will be folded into
          a single line at runtime"
```

### Try It Now
**Lab 2.4.** Write a single step whose `run:` value uses the `|` block style to execute three separate `echo` commands, with one `#` comment above explaining what the step does.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  # Prints three status lines during the build
  - name: Print status
    run: |
      echo "Starting build"
      echo "Running checks"
      echo "Build complete"
```
</details>

---

## 2.5 Anchors & aliases

**Explain it simply:** Anchors (`&name`) let you "bookmark" a chunk of YAML, and aliases (`*name`) let you reuse that bookmarked chunk elsewhere — copy-paste without the copy-paste.

```yaml
defaults: &default_settings
  run:
    shell: bash

jobs:
  build:
    <<: *default_settings
    runs-on: ubuntu-latest
```

**Why / when:** useful for repeating identical config blocks (like environment variables) across multiple jobs. **When not to use:** for small workflows it usually adds more confusion than it saves — don't reach for it until duplication actually hurts.

### Try It Now
No lab required yet (this is an advanced/rare tool) — just answer: if you had 5 jobs that all needed the identical `env:` block, would an anchor help, and why?

<details>
<summary>Show Answer</summary>

Yes — define the `env:` block once with `&shared_env`, then reference it in each of the 5 jobs with `<<: *shared_env`. This avoids retyping (and risking a typo mismatch in) the same block five times, and means updating it once updates it everywhere it's used.
</details>

---

## Level 2 Quiz
1. Why does YAML forbid tabs?
2. What does a `-` at the start of a line signify?
3. What's the difference between `|` and `>` in a multiline string?
4. Spot the bug:
   ```yaml
   steps:
     - name:Build
       run: npm run build
   ```
5. Rewrite this list so it's valid YAML:
   ```yaml
   steps:
   - run: echo one
     - run: echo two
   ```
6. What symbol starts a YAML comment?
7. What do anchors (`&`) and aliases (`*`) let you do together?

<details>
<summary>Show Answers</summary>

1. Tabs aren't interpreted as a consistent width across parsers/editors, so YAML disallows them entirely to avoid ambiguity.
2. It marks the start of a new item in a list (sequence).
3. `|` preserves each line break as-is; `>` folds multiple lines into a single line (joined by spaces).
4. Missing space after the colon: `name:Build` → `name: Build`.
5.
   ```yaml
   steps:
     - run: echo one
     - run: echo two
   ```
   Both dashes must align at the same indentation level as siblings.
6. `#`
7. Bookmark a block of YAML once (`&name`) and reuse it elsewhere (`*name`) without retyping it.
</details>

---

# LEVEL 3: Workflow Anatomy

Now we go deep on every top-level keyword in a workflow file.

## 3.1 `name` and `on`

Already covered in 1.5 — quick recap: `name` labels the workflow in the UI; `on` defines the trigger(s).

### Sample Workflow (fully commented)

```yaml
name: CI on Main               # Label shown in the Actions tab.

on:                             # Expanded form of "on" — lets us filter per-event.
  push:                         # Trigger #1: a push event...
    branches: [main]            # ...but ONLY if the push lands on the "main" branch.
  pull_request:                 # Trigger #2: a pull_request event...
    branches: [main]            # ...but ONLY if the PR TARGETS the "main" branch.

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Triggered by ${{ github.event_name }}"
        # github.event_name is a built-in context value (deep dive in Level 5) —
        # for now just notice it tells us WHICH of the two triggers fired.
```

### Try It Now
Write an `on:` block that triggers only on pushes to `main` **and** on any pull request targeting `main`.

<details>
<summary>Show Answer</summary>

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```
</details>

---

## 3.2 `jobs`, `runs-on`

**Explain it simply:** `jobs` is the container for all the work. Each job is independent by default — they run in **parallel** unless you tell them not to (more in 3.6 / Level 9 `needs`).

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "linting"
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "testing"
```

Here `lint` and `test` run **at the same time**, on separate fresh runners.

### Job ID vs Job `name:` — don't confuse these two

This trips up almost everyone early on, so slow down here.

```yaml
jobs:
  run-unit-tests:            # <-- This is the JOB ID (the key itself, e.g. "run-unit-tests")
    name: "Run Unit Tests 🧪" # <-- This is the JOB NAME (a separate, optional field)
    runs-on: ubuntu-latest
    steps:
      - run: echo "testing"
```

| | Job ID | Job `name:` |
|---|---|---|
| What it is | The key under `jobs:` itself (e.g. `run-unit-tests`) | An optional field *inside* the job, purely cosmetic |
| Where it's used | Referenced in code — `needs:`, `jobs.<job-id>.outputs`, status checks, branch protection rules | Shown to humans — the label displayed in the Actions tab / PR checks UI |
| Allowed characters | Letters, numbers, `-` and `_` only. No spaces, no emoji, no special characters. | Any string at all — spaces, emoji, punctuation all fine. |
| Required? | Yes — every job needs an ID (it's the map key) | No — if omitted, GitHub just displays the job ID instead. |
| Can it change safely? | Changing it breaks anything that referenced the old ID (`needs:`, branch protection rules pointing at that check name) | Changing it is purely cosmetic — safe to rename anytime |

**Why this distinction exists:** the ID is what the *machine* uses to wire jobs together (`needs: run-unit-tests`); the `name:` is what the *human* sees in the UI. You can rename the display label as often as you like without breaking any automation — but renaming the ID is a breaking change if anything depends on it.

**Common mistake:** trying to write `needs: "Run Unit Tests 🧪"` (the display name) instead of `needs: run-unit-tests` (the actual ID) — this fails, because `needs:` always refers to the ID, never the cosmetic name.

**Best practice:** keep job IDs short, kebab-case, and stable (`lint`, `unit-tests`, `deploy-prod`); use `name:` for anything you want more human-readable or decorated in the UI.

### Try It Now (Job ID vs Name)
Fix this workflow so `deploy` correctly waits for the test job to finish. Spot what's wrong first:
```yaml
jobs:
  run-tests:
    name: "Run All Tests"
    runs-on: ubuntu-latest
    steps:
      - run: echo "testing"
  deploy:
    needs: "Run All Tests"
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying"
```

<details>
<summary>Show Answer</summary>

`needs:` must reference the job **ID**, not the display `name:`. The fix:
```yaml
jobs:
  run-tests:
    name: "Run All Tests"
    runs-on: ubuntu-latest
    steps:
      - run: echo "testing"
  deploy:
    needs: run-tests
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying"
```
The UI will still show "Run All Tests" as the friendly label, but `deploy` correctly waits on the ID `run-tests`.
</details>

### Try It Now
**Lab 3.2.** Write a workflow with two jobs, `job-a` and `job-b`, each running on `ubuntu-latest`, each printing its own name via `echo`. Push it and confirm in the Actions tab that both ran, and check whether they ran in parallel or sequence (look at the timestamps).

<details>
<summary>Show Answer</summary>

```yaml
name: Parallel Jobs Demo
on: push

jobs:
  job-a:
    runs-on: ubuntu-latest
    steps:
      - run: echo "This is job-a"
  job-b:
    runs-on: ubuntu-latest
    steps:
      - run: echo "This is job-b"
```
In the Actions tab, `job-a` and `job-b` should show overlapping start times — confirming they ran in parallel, since neither depends on the other.
</details>

---

## 3.3 `permissions`

**Explain it simply:** By default, the temporary token GitHub gives your workflow (`GITHUB_TOKEN`) has certain access levels to your repo. `permissions` lets you explicitly restrict or grant what that token can do — the principle of least privilege.

```yaml
permissions:
  contents: read
  pull-requests: write
```

**Best practice:** always set `permissions` explicitly, scoped to only what's needed.

### Try It Now
For a workflow that only runs tests and never writes anything back to the repo, write the `permissions:` block that grants the *minimum* access needed.

<details>
<summary>Show Answer</summary>

```yaml
permissions:
  contents: read
```
Read-only access to the repo's contents is enough to check out code and run tests — nothing needs write access here.
</details>

---

## 3.4 `defaults`

**Explain it simply:** Instead of repeating the same setting on every step, `defaults` sets it once for the whole job or workflow.

```yaml
defaults:
  run:
    shell: bash
    working-directory: ./app
```

### Try It Now
Write a `defaults:` block that makes every step in the job default to running from a `./backend` subfolder using `bash`.

<details>
<summary>Show Answer</summary>

```yaml
defaults:
  run:
    shell: bash
    working-directory: ./backend
```
</details>

---

## 3.5 `timeout-minutes`

**Explain it simply:** A safety valve — if a job hangs, this kills it after N minutes instead of burning runner-minutes (and money) forever.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
```

**Best practice:** always set a reasonable `timeout-minutes` — default is 360 minutes, far too generous for most jobs.

### Try It Now
Add `timeout-minutes: 5` to your Lab 3.2 workflow's `job-a`.

<details>
<summary>Show Answer</summary>

```yaml
jobs:
  job-a:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - run: echo "This is job-a"
```
</details>

---

## 3.6 `concurrency`

**Explain it simply:** Prevents overlapping runs — e.g., if someone pushes twice quickly, you often want to cancel the first (now-stale) run rather than let both finish and waste resources.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

*(The `${{ }}` syntax is covered fully in Level 5 — for now, just recognize the shape.)*

### Try It Now
Answer conceptually: if three commits are pushed to the same branch within a minute, what would you *want* `cancel-in-progress: true` to do, and why does that save money?

<details>
<summary>Show Answer</summary>

You'd want the first two (now-outdated) runs cancelled as soon as a newer commit's run starts, since only the latest commit's result actually matters. This saves runner-minutes (and money, on paid plans) that would otherwise be spent finishing runs whose results are immediately superseded.
</details>

---

## 3.7 `strategy` / `matrix`

**Explain it simply:** A matrix runs the *same* job multiple times with different input combinations.

### Sample Workflow (fully commented)

```yaml
name: Matrix Demo
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:                    # Defines the combinations to run.
        node-version: [16, 18, 20]   # This creates 3 separate job runs,
                                       # one per value in this list.
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          # matrix.node-version is substituted with 16, then 18, then 20
          # -- a different value in each of the 3 parallel runs.
      - run: npm test
```

### Try It Now
**Lab 3.7.** Write a matrix that runs a job across `node-version: [18, 20]` **and** `os: [ubuntu-latest, windows-latest]` (a matrix can have more than one dimension — this produces 4 combinations total). Just `echo` the values, no real test commands needed.

<details>
<summary>Show Answer</summary>

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        node-version: [18, 20]
        os: [ubuntu-latest, windows-latest]
    steps:
      - run: echo "Running on ${{ matrix.os }} with Node ${{ matrix.node-version }}"
```
This produces 4 total runs: (18, ubuntu), (18, windows), (20, ubuntu), (20, windows).
</details>

---

## 3.8 `outputs`

**Explain it simply:** Jobs are isolated — one job's variables don't automatically exist in another job. `outputs` is the explicit hand-off.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      build-version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying version ${{ needs.build.outputs.build-version }}"
```

**Line by line:** the `id: get-version` step writes `version=1.2.3` into a special file (`$GITHUB_OUTPUT`); the job then exposes that as `outputs.build-version`; `deploy` declares `needs: build` (so it waits for it and can read its outputs) via `needs.build.outputs.build-version`.

### Try It Now
Answer conceptually: why can't `deploy` simply read a shell variable set inside `build`'s step directly, without this `outputs` mechanism?

<details>
<summary>Show Answer</summary>

Because each job runs on its own separate, isolated runner (a fresh VM) — there's no shared memory or filesystem between `build` and `deploy`. `outputs` is the explicit, documented hand-off mechanism GitHub Actions provides to move a value from one job to another.
</details>

---

## Level 3 Quiz
1. What's the difference between the short list form and expanded form of `on`?
2. Do jobs run in parallel or sequence by default?
3. What does `permissions: contents: read` restrict?
4. What problem does `timeout-minutes` solve?
5. What does `cancel-in-progress: true` do inside `concurrency`?
6. If a matrix has `node-version: [16, 18]` and `os: [ubuntu-latest, macos-latest]`, how many total job runs does it produce?
7. Why do jobs need an explicit `outputs:` mechanism instead of just sharing variables directly?
8. What's the difference between a job's ID and its `name:` field, and which one does `needs:` reference?
9. Spot the bug:
   ```yaml
   jobs:
     test:
       runs-on: ubuntu-latest
     timeout-minutes: 5
   ```

<details>
<summary>Show Answers</summary>

1. Short form (`on: push` or `on: [push, pull_request]`) triggers on any branch/path with no filtering. Expanded form lets you filter which branches/paths trigger each event.
2. Parallel.
3. It limits the `GITHUB_TOKEN` to read-only access to the repo's contents.
4. Prevents a hung job from running indefinitely, wasting runner time and cost.
5. Cancels an older in-progress run when a newer run starts in the same concurrency group.
6. 4 total runs (2 × 2).
7. Jobs run on isolated, separate runners with no shared memory/filesystem — there's no shell variable to "just share" without an explicit hand-off.
8. The job ID is the key under `jobs:` (e.g. `run-tests`) — it's what code (`needs:`, `jobs.<job-id>.outputs`) references, and it must be alphanumeric/hyphen/underscore with no spaces. The `name:` field is an optional, purely cosmetic display label shown in the UI, and can be any string. `needs:` always references the job ID, never the `name:`.
9. `timeout-minutes` is indented at the wrong level — it's a sibling of `jobs:` instead of being nested inside `test:`. It should be indented under `test:`, alongside `runs-on:`.
</details>

---

# LEVEL 4: Steps & Actions

## 4.1 `uses` vs `run`

**Explain it simply:** A step does one of two things: runs a **raw shell command** (`run:`), or calls a **pre-built, reusable Action** someone already wrote (`uses:`). Think of `run` as cooking from raw ingredients, and `uses` as opening a can of something already made.

### Sample Workflow (fully commented)

```yaml
name: Uses vs Run Demo
on: push

jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        # "uses" calls a pre-built Action from the Marketplace.
        # "actions/checkout" is maintained by GitHub itself; "@v4" pins
        # the version so it won't silently change behavior later.

      - name: Print current directory
        run: pwd
        # "run" executes a raw shell command directly on the runner.
        # No external code is being called here -- just the OS shell.
```

**Why / when:** use `uses` whenever a well-maintained action already exists — don't reinvent it with raw shell. Use `run` for anything custom/simple.

### Try It Now
Write two steps: one that uses `actions/checkout@v4`, and one that runs `ls -la` to list files.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  - name: List files
    run: ls -la
```
</details>

---

## 4.2 `with`, `env`

**Explain it simply:** `with` passes **inputs** into an action (like arguments to a function). `env` sets **environment variables** available to that step's shell process.

```yaml
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: '20'

  - name: Use an env var
    run: echo "Building for $ENVIRONMENT"
    env:
      ENVIRONMENT: production
```

**Line by line:** `with:` keys are defined by the action being called, not by GitHub Actions generally. `env:` keys are names you choose, available as shell variables.

### Try It Now
**Lab 4.2.** Write a step using `actions/setup-node@v4` with `node-version: '20'`, followed by a step that sets `env: GREETING: "hi"` and echoes it.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: '20'

  - name: Print greeting
    run: echo "$GREETING"
    env:
      GREETING: "hi"
```
</details>

---

## 4.3 `id` and referencing step outputs

**Explain it simply:** `id` gives a step a nickname so later steps (or jobs, via `outputs`) can refer back to what it did or produced.

```yaml
steps:
  - id: whoami
    run: echo "user=$(whoami)" >> "$GITHUB_OUTPUT"

  - run: echo "The user was ${{ steps.whoami.outputs.user }}"
```

### Try It Now
Write a step with `id: get-date` that outputs today's date (`date` command) into `$GITHUB_OUTPUT` as `today`, and a second step that echoes `steps.get-date.outputs.today`.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - id: get-date
    run: echo "today=$(date)" >> "$GITHUB_OUTPUT"

  - run: echo "Today is ${{ steps.get-date.outputs.today }}"
```
</details>

---

## 4.4 `if` conditions

**Explain it simply:** `if` is a gatekeeper — the step (or job) only runs when the condition is true.

```yaml
steps:
  - name: Deploy
    if: github.ref == 'refs/heads/main'
    run: echo "Deploying..."

  - name: Notify on failure
    if: failure()
    run: echo "Something broke!"
```

### Try It Now
Write a step that only runs `echo "Only on main!"` if the branch is `main`, and a separate step that only runs on failure of prior steps.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - name: Main branch only
    if: github.ref == 'refs/heads/main'
    run: echo "Only on main!"

  - name: On failure
    if: failure()
    run: echo "A previous step failed."
```
</details>

---

## 4.5 `continue-on-error`

**Explain it simply:** Normally, if a step fails, the whole job stops. `continue-on-error: true` says "note the failure, but keep going anyway."

```yaml
steps:
  - name: Optional lint (non-blocking)
    run: npm run lint
    continue-on-error: true
```

**When NOT to use it:** never on security scans or test suites you actually rely on.

### Try It Now
Name one step type where `continue-on-error: true` is reasonable, and one where it would be dangerous.

<details>
<summary>Show Answer</summary>

Reasonable: an experimental/optional linter you're not ready to enforce yet, or a "nice to have" code-style check. Dangerous: your actual test suite or a security vulnerability scan — letting those fail silently defeats the purpose of having them in CI at all.
</details>

---

## 4.6 `shell` and `working-directory`

**Explain it simply:** `shell` picks which command interpreter runs your `run:` block. `working-directory` picks which folder the command executes from.

```yaml
steps:
  - name: Run from subfolder
    run: npm install
    working-directory: ./frontend
    shell: bash
```

### Try It Now
Write a step that runs `npm install` from a `./api` subfolder using `bash` explicitly.

<details>
<summary>Show Answer</summary>

```yaml
steps:
  - name: Install API dependencies
    run: npm install
    working-directory: ./api
    shell: bash
```
</details>

---

## 4.7 Marketplace actions

**Explain it simply:** The GitHub Actions Marketplace is a library of community/official pre-built actions. Reference them as `owner/repo@version`.

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```

**Best practice:** pin to a specific major version tag (`@v5`) rather than `@main`/`@master`. For anything security-sensitive, pin to a full commit SHA instead of a tag.

### Try It Now
Write the `uses:` + `with:` block for a setup action for a language you use, pinned to a version tag.

<details>
<summary>Show Answer</summary>

Example for Python:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```
Any language works — the check is: `uses:` pinned to an `@vN` tag (not `@main`), and `with:` supplying that action's documented input keys.
</details>

---

## 4.8 Composite / custom actions (intro)

**Explain it simply:** When you find yourself repeating the *same sequence of steps* across many workflows, bundle them into your own reusable **composite action**.

```yaml
# .github/actions/greet/action.yml
name: 'Greet'
description: 'Prints a greeting'
inputs:
  who:
    description: 'Name to greet'
    required: true
runs:
  using: 'composite'
  steps:
    - run: echo "Hello, ${{ inputs.who }}!"
      shell: bash
```

Used from a workflow like:
```yaml
- uses: ./.github/actions/greet
  with:
    who: 'Team'
```

*(Much deeper dive in Level 9 — for now, recognize the shape.)*

### Try It Now
Answer conceptually: if five different workflows in your org all needed the identical 4-step "notify Slack" sequence, what's the benefit of a composite action over copy-pasting those 4 steps five times?

<details>
<summary>Show Answer</summary>

One update fixes it everywhere it's used — instead of hunting down and editing 5 separate copies (and risking one getting missed or drifting out of sync), you change the composite action once and every workflow that calls it picks up the fix automatically.
</details>

---

## Level 4 Quiz
1. What's the core difference between `uses:` and `run:`?
2. What does `with:` do, and where do its valid keys come from?
3. Why would a step need an `id:`?
4. Spot the bug:
   ```yaml
   - name: Deploy
     if github.ref == 'refs/heads/main'
     run: echo "deploying"
   ```
5. What does `continue-on-error: true` change about job behavior, and name one case where it's risky to use.
6. What's the difference between `shell:` and `working-directory:`?
7. Why should you pin marketplace actions to a version tag or SHA instead of `@main`?
8. What problem do composite actions solve?

<details>
<summary>Show Answers</summary>

1. `uses:` calls a pre-built action; `run:` executes a raw shell command.
2. It passes inputs into an action; valid keys are defined by that specific action's own documentation, not by GitHub Actions generally.
3. So later steps (or jobs, via `outputs`) can reference what it produced.
4. Missing colon after `if` — should be `if: github.ref == 'refs/heads/main'`.
5. The job continues running even if that step fails, instead of stopping the whole job. Risky on real test suites or security scans, where a failure should actually block the pipeline.
6. `shell` picks the interpreter running the command (bash, pwsh, etc.); `working-directory` picks the folder the command runs from.
7. So a third party can't silently change the action's behavior (or introduce malicious code) without your review — `@main` can change under you at any time.
8. Avoids duplicating the same step sequence across many workflows — one update fixes it everywhere it's used.
</details>
