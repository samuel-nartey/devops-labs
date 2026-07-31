# Level 1 — GitHub Actions Fundamentals

Welcome to Level 1. By the end of this level you will have written and run three real workflows on GitHub, and you'll understand exactly what happens the moment you push code.

**Rule for this level:** don't read past a "🔧 Try It Now" without actually doing it. Have a GitHub repo open in another tab right now — create a new empty one called `actions-lab` if you don't have one.

---

## Concept 1: What is CI, and why does it exist?

**Explain it simply**
CI stands for **Continuous Integration**. Every time someone changes code, a robot automatically checks: "does this still work?" — runs the tests, checks the formatting, tries to build it. No human has to remember to do it.

**Real-world analogy**
Imagine a bakery where every batch of bread gets weighed and taste-tested automatically the second it comes out of the oven — before it ever reaches a customer. Nobody has to remember to check; the checking is built into the process. That's CI. The "oven" is your code editor, the "batch" is your commit, and the "taste test" is your test suite.

**Why it exists**
Before CI, teams would write code for weeks, merge it all at once, and then spend days fixing everything that broke ("integration hell"). CI catches problems in minutes instead of weeks, on every single change.

**When to use it**
Any project with more than one contributor, or any project you care about not breaking silently. Even solo projects benefit — CI catches your own mistakes before your future self has to debug them.

**When NOT to use it**
Throwaway scripts, one-off experiments you'll delete tomorrow. Setting up CI has a small cost; don't pay it for code with no future.

🔧 **Try It Now**
No code yet — just answer in your own words: if you push broken code to a shared repo with no CI, who finds out it's broken, and when? Write one sentence.

---

## Concept 2: What is CD?

**Explain it simply**
CD is **Continuous Delivery/Deployment** — automatically taking code that passed CI and putting it somewhere real (a server, an app store, a cloud environment) without a human manually copying files around.

**Real-world analogy**
CI is the taste test in the bakery. CD is the conveyor belt that automatically loads the approved loaves onto the delivery truck — no one has to carry them out by hand.

**Why it exists**
Manual deployments are slow, error-prone, and inconsistent — someone forgets a step, does it differently on a Friday afternoon, or deploys the wrong version. CD makes deployment boring and repeatable, which is exactly what you want.

**When to use it**
Any application with a real environment (staging, production) that gets updated regularly.

**When NOT to use it**
Highly regulated deployments that legally require a human sign-off at every release — there you'd use CD to *prepare* the release, but a human still presses the final button (this is called Continuous **Delivery** vs Continuous **Deployment** — the difference is literally whether a human clicks approve).

🔧 **Try It Now**
In your own words: what's the one-word difference between "Continuous Delivery" and "Continuous Deployment"? (Hint: it's about who clicks the button.)

---

## Concept 3: Why GitHub Actions specifically?

**Explain it simply**
GitHub Actions is GitHub's own built-in robot-runner. It lives right next to your code, reacts to things that happen in your repo (a push, a pull request, a schedule), and runs commands on a fresh temporary computer that GitHub gives you for free (within limits).

**Real-world analogy**
Other CI tools (Jenkins, CircleCI) are like hiring an outside contractor who you have to explain your address to every time. GitHub Actions is like having an assistant who already lives in your building and watches the front door — the moment something happens, they react, with zero setup to "connect" it to your repo.

**Why it exists**
GitHub wanted CI/CD to require zero extra accounts, zero extra billing relationships, and zero extra integration work for repos already hosted on GitHub.

**When to use it**
Your code is already on GitHub. Free tier is generous for public repos and reasonable for private ones.

**When NOT to use it**
Your code lives on GitLab or Bitbucket (use their native CI). Or you need extremely specialized, long-running, expensive build hardware that's cheaper to manage yourself long-term (self-hosted runners can bridge this, more in Level 9).

🔧 **Try It Now**
Go to your `actions-lab` repo on GitHub.com right now. Click the **Actions** tab. Screenshot or just note: what does GitHub suggest as starter workflows? You don't need to click anything yet — just look.

---

## Concept 4: How GitHub Actions works internally

**Explain it simply**
Here's the actual sequence, every single time:

1. Something happens in your repo (you push code, open a PR, etc.) — this is an **event**.
2. GitHub checks: "is there a workflow file listening for this event?"
3. If yes, GitHub spins up a **brand new, disposable virtual machine** (a "runner").
4. GitHub copies your repo's code onto that machine.
5. It runs the steps you defined, one by one, top to bottom.
6. When it's done, the machine is thrown away completely. Next run gets a 100% fresh one.

**Real-world analogy**
It's like ordering a pop-up kitchen for a single event: a fully-equipped kitchen appears, cooks exactly one meal following your recipe card, and then is torn down completely. The next event gets a brand new pop-up kitchen — nothing is left over from last time (this is why you can't "save state" between runs without deliberately using caching or artifacts — more on that in Level 6).

**Why it exists**
This throwaway-machine model guarantees every run is consistent — no "works on my machine" drift, no leftover files from a previous run silently breaking your build.

**When to use it**
Always — this is just how it works, not a choice you make.

**When NOT to use it**
N/A — but knowing this explains *why* you must explicitly declare every dependency install, every checkout step. Nothing is assumed to already be there.

🔧 **Try It Now**
Without looking it up: if a workflow run installs a package on the runner, and then a second run happens five minutes later, will that package still be there? Answer yes/no and explain why in one sentence.

---

## Concept 5: Hosted runners vs self-hosted runners

**Explain it simply**
A **runner** is the actual computer that executes your workflow.
- **GitHub-hosted runner**: GitHub owns and manages the machine. You just say `runs-on: ubuntu-latest` and it appears, ready to go, then disappears after.
- **Self-hosted runner**: You provide the machine (your laptop, a company server, an EC2 instance) and install GitHub's runner agent on it yourself. It stays alive between runs unless you tear it down.

**Real-world analogy**
GitHub-hosted = renting a hotel room for one night, fully cleaned and stocked, gone when you check out. Self-hosted = your own apartment — you set it up once, but you're also responsible for cleaning it, and anything you leave behind is still there next time.

**Why both exist**
Hosted runners are zero-maintenance but limited in CPU/RAM/OS choice and have usage limits. Self-hosted runners give you full control (specific hardware, GPUs, internal network access, no time limits) but you manage security and upkeep.

**When to use hosted**
99% of beginner and small/medium projects. Default choice.

**When to use self-hosted**
You need access to a private network, specific hardware, or you're running so many jobs that hosted-runner minutes get expensive.

🔧 **Try It Now**
Which type would you use for: (a) a personal open-source project's test suite, (b) a company's internal deployment that needs access to a private VPN-only database? Answer both in one line each.

---

## Concept 6: Event-driven automation

**Explain it simply**
Nothing runs "just because." Every workflow starts because of a **trigger** — an event GitHub is watching for. Common ones: `push`, `pull_request`, `schedule` (like a cron job), `workflow_dispatch` (a manual "Run" button).

**Real-world analogy**
A workflow is a smoke detector, not a security guard patrolling on a schedule (well — unless you use `schedule`). It sits silently doing nothing until the specific thing it's listening for happens, then it reacts instantly.

**Why it exists**
So automation happens exactly when it's needed — not constantly polling and wasting resources.

**When to use `push`**
Run tests every time code changes on a branch.

**When to use `pull_request`**
Run checks before code is allowed to merge — this is the most common CI trigger.

**When NOT to trigger on every push**
On a huge monorepo, triggering a 40-minute build on every single push to every branch wastes time and money — you'd scope it down (paths, branches) — more in Level 3.

🔧 **Try It Now**
No code yet. Just decide: for a workflow that runs your test suite, should it trigger on `push`, `pull_request`, or both? Write your answer and your reasoning in 1–2 sentences.

---

## Concept 7: Anatomy of a workflow file

**Explain it simply**
A workflow is just a YAML file that lives in a specific folder GitHub always looks in: `.github/workflows/`. Any `.yml` file there is automatically discovered — no registration step, no config elsewhere.

**The syntax, broken down line by line**

```yaml
name: My First Workflow

on: push

jobs:
  say-hello:
    runs-on: ubuntu-latest
    steps:
      - name: Print a greeting
        run: echo "Hello, GitHub Actions!"
```

Line by line:

| Line | What it means |
|---|---|
| `name: My First Workflow` | The label shown in the Actions tab UI. Optional but always name your workflows. |
| `on: push` | The trigger. This workflow runs every time someone pushes a commit. |
| `jobs:` | A workflow contains one or more **jobs**. Each job runs on its own fresh runner. The colon means "everything indented under this belongs to `jobs`." |
| `  say-hello:` | This is the **job ID** — a name you invent for this job. Indented 2 spaces under `jobs:` because it belongs to it. |
| `    runs-on: ubuntu-latest` | Which runner OS to use for this job. Indented under `say-hello:` because it's a property of that job. |
| `    steps:` | A job contains one or more **steps**, run top to bottom, in order, on the same machine. |
| `      - name: Print a greeting` | The dash (`-`) means "this is one item in a list." Each step is a list item. `name` here is just a human-readable label for this one step (different from the workflow's `name` above). |
| `        run: echo "..."` | The actual command to execute in the shell. Indented under the step's `-` because it belongs to that step. |

**Why indentation is everything in YAML**
YAML has no curly braces or semicolons — indentation *is* the structure. Two spaces vs four spaces, or a missing space after a colon, will either break the file or silently change what belongs to what. There is no "it still kind of works" in YAML — it's exact or it's broken.

🔧 **Try It Now**
Create the file `.github/workflows/hello.yml` in your `actions-lab` repo with the exact content above. Commit it directly to `main` (or via a PR if you prefer). Go to the **Actions** tab and watch it run. Click into the run, click into the `say-hello` job, and find the line of output where it printed your greeting.

**Best practice**
Always use **spaces**, never tabs, in YAML — GitHub's parser will reject tabs. Most editors (VS Code) can be set to convert tabs to spaces automatically.

📝 **Scenario**
Your teammate pastes this into a new file and asks why GitHub says the workflow is invalid:

```yaml
name: Deploy Check

on: push

jobs:
deploy-check:
    runs-on: ubuntu-latest
    steps:
      - name: Confirm
        run: echo "checking..."
```

What's wrong, and what's the one-line fix?

<details>
<summary>Solution</summary>

`deploy-check:` has no indentation, so YAML doesn't know it belongs under `jobs:` — it looks like a separate top-level key instead of a job. Fix: indent it 2 spaces, same as `say-hello:` was indented in the working example:

```yaml
jobs:
  deploy-check:
    runs-on: ubuntu-latest
```

</details>

---

## Concept 8: Manual trigger with `workflow_dispatch`

**Explain it simply**
`workflow_dispatch` adds a manual "Run workflow" button in the GitHub UI. You click it, it runs — no push needed.

**Syntax**
```yaml
on: workflow_dispatch
```

**Why it exists**
Some workflows shouldn't run automatically — a production deploy, a data cleanup script. You want a human to deliberately press a button.

**When to use it**
Deploys, one-off maintenance tasks, anything requiring deliberate human intent.

**When NOT to use it (alone)**
Your test suite — you don't want to have to remember to click a button every time you push code; use `push` or `pull_request` instead.

🔧 **Try It Now**
Edit `hello.yml` — change `on: push` to `on: workflow_dispatch`. Commit it. Go to the Actions tab, select your workflow on the left, and find the "Run workflow" button that now appears. Click it and confirm it runs.

**Bonus — combine triggers**
```yaml
on: [push, workflow_dispatch]
```
The square brackets `[ ]` are YAML's way of writing a list on one line — equivalent to writing `push` and `workflow_dispatch` on separate indented lines with dashes. Update your file to this and confirm both the push trigger AND the manual button still work.

📝 **Scenario**
Your team wants a "Cleanup old branches" workflow that should **never** run automatically on push — it should only ever run when someone deliberately decides to run it, from the Actions tab. What should the `on:` line be, and why is `push` the wrong choice here?

<details>
<summary>Solution</summary>

```yaml
on: workflow_dispatch
```

`push` is wrong because it fires automatically on every commit — for a destructive action like deleting branches, you never want that to happen without explicit human intent. `workflow_dispatch` adds a manual "Run workflow" button and does nothing until someone deliberately clicks it.

</details>

---

## Concept 9: Printing environment info (getting comfortable with `run`)

**Explain it simply**
The `run` keyword executes shell commands. You can run more than one command per step.

**Syntax**
```yaml
      - name: Show runner info
        run: |
          echo "OS is:"
          uname -a
          echo "Current directory:"
          pwd
          echo "Files here:"
          ls -la
```

Breakdown:
- The pipe `|` after `run:` tells YAML "the following indented lines are one multi-line string — keep the line breaks." Without it, YAML would try to read everything as one line and fail.
- Each line runs as a separate shell command, in order, on the same runner.

🔧 **Try It Now**
Add this step to your workflow (as a second step, after the "Print a greeting" step). Push it, watch it run, and open the log. Answer: what operating system is the runner actually using? What's the current working directory GitHub starts you in?

**Common mistake**
Forgetting the `|` when writing multiple lines under `run:` — YAML will try to parse subsequent lines as new keys, not commands, and throw an error. Try removing the `|` on purpose and see the exact error GitHub gives you.

📝 **Scenario**
A learner writes this step and can't figure out why it fails:

```yaml
      - name: Setup steps
        run: echo "Step 1"
          echo "Step 2"
          echo "Step 3"
```

What's missing, and what should the corrected step look like?

<details>
<summary>Solution</summary>

The `|` is missing after `run:`. Without it, YAML treats `run:` as having a single-line value (`echo "Step 1"`) and the following lines as stray, unindented-relative-to-nothing text, which breaks parsing. Corrected:

```yaml
      - name: Setup steps
        run: |
          echo "Step 1"
          echo "Step 2"
          echo "Step 3"
```

</details>

---

## Mini Project: Your First Real Pipeline

Combine everything from this level into one workflow, `.github/workflows/level1-project.yml`:

**Requirements:**
1. Named `"Level 1 Capstone"`.
2. Triggers on both `push` to `main` and manual `workflow_dispatch`.
3. One job, `runs-on: ubuntu-latest`.
4. Step 1: print a greeting with your name.
5. Step 2: print the runner's OS, current directory, and list files (multi-line `run`).
6. Step 3: print today's date using the shell `date` command.

Build it yourself from what you've learned — don't copy-paste concept 7's example verbatim, type it fresh so your fingers learn the indentation.

---

## Debugging Exercise

Here is a broken workflow. Find and fix all 3 bugs before running it.

```yaml
name: Broken Workflow
on push
jobs:
  test:
  runs-on: ubuntu-latest
    steps:
      - name: Say hi
      run: echo "hi"
```

Don't scroll past this — actually find all three problems and write the corrected version yourself first. Then create it in your repo, watch it fail, and use GitHub's error message to confirm what you already found.

<details>
<summary>Reveal fixes only after you've tried (click to expand)</summary>

1. `on push` is missing a colon — must be `on: push`.
2. `runs-on: ubuntu-latest` is not indented under `test:` — needs 2 more spaces.
3. `run: echo "hi"` is not indented under the `- name: Say hi` step — needs to be at the same indent level as `name`, both under the `-`.

</details>

---

## Level 1 Quiz

Answer these before moving to Level 2. No peeking at the concepts above until you've written an answer for each.

1. In one sentence, what's the difference between CI and CD?
2. What folder must workflow files live in for GitHub to find them?
3. What does the dash (`-`) mean in YAML, structurally?
4. True or false: files created on a runner during one job run are still there for the next run. Why?
5. What trigger would you use for a workflow that must only run when a human deliberately clicks a button?
6. What does the `|` symbol do after `run:`?
7. Spot the bug: `runs-on ubuntu-latest` — what's wrong and what's the fix?
8. Why does GitHub Actions use a brand-new virtual machine for every job instead of reusing one?

---

**Once you've completed the mini project, fixed the debugging exercise, and answered the quiz, you're ready for Level 2 — YAML Mastery**, where we go deep on the syntax rules that make workflows like this one work (and break).
