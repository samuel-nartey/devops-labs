# Lab: Terraform Standard Runs vs Speculative Plans (HCP Terraform)

Hi, I'm Samuel. This is a beginner-friendly, hands-on lab where you will see for yourself how HCP Terraform behaves differently when you **commit to your main branch** and when you **open a pull request**.

No cloud account (AWS, Azure, GCP) is needed and nothing here costs money. Everything is done in your web browser, using the **GitHub console** and the **HCP Terraform console**. You do not need to install Terraform.

> **A note on how I wrote this guide.** I built this lab inside my own `devops-labs` repository, in a folder called `Terraform/hcp-terraform-run-types`. You will most likely start from scratch with a brand new repo, so the main steps below are written for that. Wherever my setup differs, I add a short **"In my case"** note so you can see what I did and why.

---

## What you will learn

By the end of this lab you will be able to:

- Explain what HCP Terraform is and how it differs from Terraform on your own machine
- Connect a GitHub repository to an HCP Terraform workspace
- Tell the difference between a **standard run** and a **speculative plan**
- Understand why a pull request can show you a Terraform plan without changing anything
- Read the **Runs** page in HCP Terraform with confidence

**Time needed:** about 30 to 45 minutes.

---

## What is HCP Terraform?

**Terraform** is a tool that reads text files describing infrastructure and creates that infrastructure for you. When you install it on your own computer, everything happens on your laptop: the work, the state file, and any credentials.

**HCP Terraform** (formerly called Terraform Cloud) is a website run by HashiCorp that runs that same Terraform tool for you, on their servers, and adds team features around it.

| | Terraform on your machine | HCP Terraform |
|---|---|---|
| **Where it runs** | Your laptop | HashiCorp's cloud servers |
| **State file** | A file on your disk (easy to lose) | Stored safely online, with history and locking |
| **Starting a run** | You type `terraform plan` or `apply` | Can start automatically when you commit to GitHub |
| **Pull request previews** | Not available | Speculative plans appear for pull requests |
| **History** | Only what you remember | Every run is logged with who, when and what |
| **Approvals** | None | Can require someone to click Confirm & Apply |

The features you will see in this lab (runs, speculative plans, the Confirm & Apply button) exist only in HCP Terraform.

---

## Key terms explained

You do not need to memorize these. Come back to this table whenever a word feels unfamiliar.

| Term | Plain-English meaning | Everyday comparison |
|---|---|---|
| **Terraform** | A tool that lets you describe infrastructure in a text file and then creates it for you. | A recipe you write down, plus a robot cook that follows it. |
| **HCP Terraform** | A website that runs Terraform for you, stores results, and keeps a history. | A shared kitchen where the robot cook works and keeps a logbook. |
| **Organization** | Your top-level space in HCP Terraform. Everything you build lives inside it. | The whole kitchen. |
| **Workspace** | One project in HCP Terraform. It holds your configuration, variables, state and run history. | One project folder in the kitchen. |
| **Repository (repo)** | A folder on GitHub that holds your files and remembers every change. | A shared folder with a full "undo history". |
| **Branch** | A separate copy of your files where you can try changes safely. `main` is the official copy. | A photocopy you scribble on before touching the original. |
| **Commit** | Saving a change to a branch, with a short note about it. | Pressing "Save" and writing a label on it. |
| **Pull request (PR)** | A request that says "I made changes on my branch, please review them and add them into `main`." | Handing in your edited copy and asking the teacher to approve it. |
| **Merge** | Accepting a pull request so the changes become part of `main`. | The teacher approves it and it goes into the official document. |
| **VCS (Version Control System)** | A tool like GitHub that tracks changes to files. HCP Terraform connects to it to watch your repo. | A guard watching the folder for any change. |
| **Provider** | A plugin that teaches Terraform how to talk to a service. Here we use `random`, which only makes random values. | A translator for one language. |
| **Resource** | One thing Terraform manages. Here it is a random pet name. | One dish on the recipe. |
| **Output** | A value Terraform shows you at the end. | The finished dish on the plate. |
| **Plan** | Terraform's preview of what it would change. Nothing is changed yet. | Reading the recipe aloud: "here is what I am about to cook." |
| **Apply** | Terraform actually makes the changes from the plan. | Actually cooking. |
| **State** | Terraform's memory of what it has already created. | The kitchen logbook. |
| **Run** | One full attempt by HCP Terraform to do work. It starts with a plan and may end with an apply. | One cooking session. |
| **Standard run** | A run that can be applied. It changes things and updates the state. | A real cooking session. |
| **Speculative plan** | A plan-only run that can never be applied. | A rehearsal. Nothing gets cooked. |
| **Working directory** | The folder inside the repo where HCP Terraform should look for your `.tf` files. | Telling the cook which shelf holds the recipe. |

---

## The big idea

HCP Terraform watches your GitHub repo. What it does depends on what you do in GitHub:

| What you do in GitHub | Run type HCP Terraform starts | Can you apply it? |
|---|---|---|
| Commit or merge into `main` | **Standard run** | Yes |
| Open a pull request | **Speculative plan** | No (preview only) |

Why does this matter? A speculative plan lets your team **see the effect of a change before it goes live**, right inside the pull request. It is a safety net.

---

## Before you start

You need:

1. A **GitHub account** (free)
2. An **HCP Terraform account** (free tier). Sign up at **app.terraform.io**. The sign-up page offers **Create Terraform account** or **Create HCP account**. Either works for this lab. An HCP account also gives you access to other HashiCorp cloud products with the same login. I used it because one login covers both.
3. A browser that **allows pop-ups** for `app.terraform.io` (needed to connect GitHub, see Troubleshooting)

---

## Part 1: Create your repository

> **In my case:** I did not create a new repo. I added this lab to my existing `devops-labs` repo, inside the folder `Terraform/hcp-terraform-run-types/`. That meant I had to tell HCP Terraform which folder to look in (the working directory setting in Part 2).
>
> **Since you are starting from scratch with a new repo, do this instead.** Your `main.tf` goes at the top level of the repo, so you will not need the working directory setting at all.

### Step 1: Create the repo

1. Sign in to **GitHub**.
2. Click the **+** icon at the top right, then **New repository**.
3. Name it `run-demo`.
4. Choose **Public** or **Private** (either works).
5. Tick **Add a README file**. This makes sure a `main` branch exists.
6. Click **Create repository**.

### Step 2: Add the Terraform file

1. Inside your new repo, click **Add file**, then **Create new file**.
2. Name the file `main.tf`.
3. Paste this in:

```hcl
terraform {
  required_providers {
    random = {
      source = "hashicorp/random"
    }
  }
}

resource "random_pet" "demo" {
  length = 2
}

output "pet_name" {
  value = random_pet.demo.id
}
```

4. Scroll down, keep **Commit directly to the main branch** selected, and click **Commit changes**.

**What does this file say, in plain English?**

- The first block says: "I need the `random` provider, the plugin that makes random values."
- The `resource` block says: "Create a random pet name made of **2** words, like `happy-otter`."
- The `output` block says: "Show me the name when you are done."

> **Heads up if you use a folder like I did:** when you type a file name in GitHub, the path is counted from the **repo root**. I accidentally ended up with `Terraform/Terraform/hcp-terraform-run-types` because I was already inside the `Terraform` folder when I typed the path. If that happens, edit the file, delete the extra folder name at the start of the path in the file name box, and commit.

---

## Part 2: Create your HCP Terraform workspace

### Step 3: Create an organization

1. Sign in at **app.terraform.io**.
2. Click **Create organization**.
3. Choose **Personal** (for your own projects). The organization type cannot be changed after creation.
4. Enter a unique organization name, such as `yourname-devops-labs`, and keep the email that is filled in. (Mine is `samuel-devops-labs`.)
5. Click **Create organization**.

### Step 4: Start a new workspace

1. Click **New**, then **Workspace**.
2. Choose **Version control workflow**. This means "watch my GitHub repo and react to changes."
   - *CLI-Driven* needs Terraform installed on your machine.
   - *API-Driven* is for custom scripts and pipelines.

### Step 5: Connect GitHub

1. Choose **GitHub**.
2. A small pop-up window opens. Sign in if asked, click **Authorize**, and choose which repositories HCP Terraform may see. Select `run-demo`.
3. Pick the `run-demo` repository from the list.

> **I hit an error here:** "Failed to install GitHub App. Please disable pop-up blocker and try again." My browser had blocked the pop-up. See Troubleshooting for the fix.

### Step 6: Configure the workspace

| Setting | What to enter |
|---|---|
| **Workspace Name** | `run-demo` (mine was `devops-labs-hcp-terraform-run-types`, because I wanted it tied to my labs repo) |
| **Description** | `Demo of standard runs vs speculative plans using random_pet` |
| **Tags** | Optional. Skip, or add `lab`. |

Click **Advanced options** and check these:

| Setting | What to do |
|---|---|
| **Terraform working directory** | **Leave empty** for your new repo. (In my case I typed `Terraform/hcp-terraform-run-types`, because my `main.tf` lives in that folder. The path is case-sensitive.) |
| **Auto-apply** boxes | Leave **unchecked**. You want to click Confirm & Apply yourself. |
| **VCS trigger type** | Keep **Branch-based** |
| **VCS branch** | Leave as the default branch (`main`) |
| **Automatic run triggering** | Keep **Always trigger runs** |
| **Automatic speculative plans** | Keep **checked**. This is what creates a plan on pull requests. Without it, Part 4 will not work. |
| **Include submodules on clone** | Leave unchecked |

Click **Create**.

You will land on a **Workspace created!** page that says **No variables found**. That is correct, because this configuration has no input variables. You do not need to add any.

---

## Part 3: Your first standard run

A **standard run** is the "real" kind. It can change things and update the state.

### Step 7: Start the run

1. Click **Start new plan**.
2. In the dialog **Start a new run**, keep **Run Type** as **Plan and apply (standard)**.
3. Optionally rename the run (for example `First standard run`) and click **Start run**.

The other run types are good to know about:

| Run type | Meaning |
|---|---|
| **Plan and apply (standard)** | A normal run you can apply |
| **Minimal refresh** | Only checks resources Terraform expects to change |
| **Refresh state** | Checks real infrastructure against the state to detect drift |
| **Plan only** | A speculative plan, which can never be applied |
| **Allow empty apply** | Applies even when there are no changes |

### Step 8: Read the plan

When the plan finishes you will see **1 to create**. Look at the output `pet_name`: it says **Known after apply**. That is because Terraform only picks the random name when it actually creates the resource.

At this point **nothing has been created yet**. The run is at **Apply pending**, waiting for you.

### Step 9: Apply it

1. Click **Confirm & Apply**.
2. Add a comment explaining why you approved it, such as `First standard run: creating random_pet for the HCP Terraform run types lab`, and confirm.
3. When it finishes you will see **Resources: 1 added, 0 changed, 0 destroyed**.
4. Open the **Outputs** tab to see your name, and the **States** tab to see the first saved state version.

My name was `relevant-tick`. Yours will be different. Write it down, because you will watch it change in Part 5.

---

## Part 4: See a speculative plan (pull request)

Now you will propose a change without touching `main`.

### Step 10: Create a branch

1. In GitHub, open your repo and click the **branch dropdown** (it says `main`).
2. Type `test-change` and click **Create branch: test-change from main**.

### Step 11: Make a change on that branch

1. Make sure the dropdown shows `test-change`.
2. Click `main.tf`, then click the **pencil icon**.
3. Change `length = 2` to `length = 3`.
4. Click **Commit changes**. Keep **Commit directly to the test-change branch** selected. Suggested message: `Change random_pet length from 2 to 3`.

Your official `main` is untouched. Only the practice copy changed.

### Step 12: Open the pull request

1. Go to the **Pull requests** tab. A banner shows **test-change had recent pushes**. Click **Compare & pull request**.
2. Check that **base** is `main` and **compare** is `test-change`.
3. Give it a title such as `Test speculative plan: change random_pet length to 3` and click **Create pull request**. Do not merge it yet.

### Step 13: Watch HCP Terraform react

1. Go to the workspace's **Runs** tab. A new run appears, marked **plan-only run**, with your pull request title.
2. Open it. The plan shows `length: 2 → 3` marked **Forces replacement**, and your pet name changing to **Known after apply**. Terraform cannot stretch a 2-word name into a 3-word one, so it would remove the old name and create a new one.
3. Notice what is missing: **there is no Confirm & Apply button**. The page says the run was started from a pull request and cannot be applied. It must be merged into the default branch first.
4. Your state still holds the old name. Nothing was changed.
5. Back on the pull request page in GitHub, scroll down to see the **status check** from HCP Terraform. This is how reviewers see the effect of a change without leaving GitHub.

---

## Part 5: Back to a standard run

### Step 14: Merge the pull request

1. In GitHub, on the pull request page, click **Merge pull request**, then **Confirm merge**.

### Step 15: Apply the change

1. Return to the **Runs** tab. A new run starts, named after the merge (mine was `Merge pull request #4 from samuel-nartey/test-change`), triggered via GitHub on branch `main`. This is a **standard run**.
2. When the plan finishes, it shows **1 to create, 1 to destroy**. That is the replacement you previewed in Part 4.
3. Click **Confirm & Apply**, add a comment such as `Applying length = 3 change after merged PR`, and click **Confirm plan**.
4. Open the **Outputs** tab. Your `pet_name` is now a three-word name. The **States** tab shows a new state version.

While a run is working, the workspace shows **Running** with a lock. HCP Terraform locks the workspace so that two runs cannot change the state at once. It unlocks when the run finishes.

---

## What you should have seen

Your **Runs** page should now list three runs. Mine looked like this:

| Run | Type | Result |
|---|---|---|
| Triggered via UI | Standard | Applied |
| Test speculative plan: change random_pet length to 3 | Plan-only (speculative) | Planned and finished, cannot be applied |
| Merge pull request #4 from samuel-nartey/test-change | Standard | Applied |

And this table sums up the lab:

| Action | Run type | Can apply? |
|---|---|---|
| Start a run from the UI, or commit to `main` | Standard | Yes |
| Open a pull request | Speculative | No |
| Merge the pull request | Standard | Yes |

---

## Troubleshooting

- **"Failed to install GitHub App. Please disable pop-up blocker and try again."** This is the error I hit. Your browser blocked the connection pop-up. Click the blocked pop-up icon in the address bar and allow pop-ups for `app.terraform.io`, or add it under your browser's site settings. Ad blockers can also cause this, so pause them or try a private window. Then retry the GitHub step.
- **My repo is not in the list.** Allow access to it in GitHub under **Settings > Applications**, then refresh the list in HCP Terraform.
- **The first plan fails with "no configuration files found".** Check that `main.tf` is committed on the `main` branch. If you put it in a folder, check **Settings > General > Terraform Working Directory**. It must exactly match the folder in GitHub, including capital letters.
- **No speculative plan appeared after opening the pull request.** Check that the pull request targets `main`, and that **Automatic speculative plans** is enabled in **Settings > Version Control**.
- **Provider download errors.** Make sure `main.tf` was copied exactly, including the `required_providers` block.

---

## Clean up

When you are done, remove what you made so nothing lingers:

1. In HCP Terraform, open the workspace and go to **Settings > Destruction and Deletion**. Click **Queue destroy plan** and confirm. Then delete the workspace.
2. In GitHub, delete the `test-change` branch. If you want to remove the whole repo, go to its **Settings**, scroll to the bottom, and click **Delete this repository**.

---

## Key takeaway

> A **commit or merge to `main`** starts a **standard run** you can apply.
> A **pull request** starts a **speculative plan** that only previews.
> That is how teams review infrastructure changes safely before they go live.

If this lab helped you, feel free to open an issue or a pull request with improvements.
