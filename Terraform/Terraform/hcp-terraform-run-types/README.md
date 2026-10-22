# Terraform Run Types Demo: Standard Runs vs Speculative Plans

A beginner-friendly hands-on lab. You will see for yourself how HCP Terraform behaves differently when you **commit to your main branch** versus when you **open a pull request**.

No cloud account (AWS, Azure, GCP) is needed. Nothing here costs money. Everything is done in your web browser using the **GitHub console** and the **HCP Terraform console**.

---

## What you will learn

By the end of this lab you will be able to:

- Explain the difference between a **standard run** and a **speculative plan**
- Understand why a pull request can show you a Terraform plan without changing anything
- Read the **Runs** page in HCP Terraform with confidence

---

## Before you start

You need:

1. A **GitHub account** (free)
2. An **HCP Terraform account** (free tier) and an **organization**. If you have never used it, sign up at app.terraform.io and it will guide you to create an organization (think of an organization as your team's folder for everything).

---

## Key terms explained (read this first)

You do not need to memorize these. Come back to this list whenever a word feels unfamiliar.

| Term | Plain-English meaning | Everyday comparison |
|---|---|---|
| **Terraform** | A tool that lets you describe infrastructure (servers, networks, names, etc.) in a text file, and then creates it for you. | A recipe you write down, and a robot cook that follows it. |
| **HCP Terraform** | A website run by HashiCorp that runs Terraform for you, stores your results, and keeps a history. | A shared kitchen where the robot cook works and keeps a logbook. |
| **Repository (repo)** | A folder on GitHub that holds your files and remembers every change ever made to them. | A shared folder with a full "undo history". |
| **Branch** | A separate copy of your files where you can try changes safely. `main` is the official, trusted copy. | Making a photocopy of a document to scribble on before touching the original. |
| **Commit** | Saving a change to a branch, with a short note about what you changed. | Pressing "Save" and writing a label on it. |
| **Pull request (PR)** | A request that says "I made changes on my branch, please review them and add them into `main`." | Handing in your edited copy and asking the teacher to approve it. |
| **Merge** | Accepting a pull request, so the changes become part of `main`. | The teacher approves it and it goes into the official document. |
| **Workspace** | In HCP Terraform, one workspace manages one set of infrastructure and remembers its state. | One project folder in the shared kitchen. |
| **Provider** | A plugin that teaches Terraform how to talk to a specific service. Here we use the `random` provider, which only makes random values. | A translator for a particular language. |
| **Resource** | One thing Terraform manages. Here it is a random pet name. | One dish on the recipe. |
| **Output** | A value Terraform shows you at the end. | The finished dish on the plate. |
| **Plan** | Terraform's preview of what it *would* change. Nothing is changed yet. | Reading the recipe aloud and saying "here is what I am about to cook." |
| **Apply** | Terraform actually makes the changes from the plan. | Actually cooking. |
| **State** | Terraform's memory of what it has already created. | The kitchen logbook. |
| **Run** | One full attempt by HCP Terraform to do work: it starts with a plan, and may finish with an apply. | One cooking session. |
| **Standard run** | A run that can be applied. It changes real things and updates the state. | A real cooking session. |
| **Speculative plan** | A plan-only run. It shows what *would* happen but can never be applied. | A rehearsal. Nothing gets cooked. |
| **VCS (Version Control System)** | A tool like GitHub that tracks changes to files. HCP Terraform connects to it to watch your repo. | A security guard watching the folder for any change. |

---

## The big idea

HCP Terraform watches your GitHub repo. What it does depends on what *you* do in GitHub:

| What you do in GitHub | Run type HCP Terraform starts | Can you apply it? |
|---|---|---|
| Commit or merge into `main` | **Standard run** | Yes |
| Open a pull request | **Speculative plan** | No (preview only) |

Why does this matter? A speculative plan lets your team **see the effect of a change before it goes live**, right inside the pull request. It is a safety net.

---

## Part 1: Create the project files

### Step 1: Create the repository

1. Sign in to **GitHub**.
2. Click the **+** icon at the top right, then click **New repository**.
3. Name it `run-demo`.
4. Choose **Public** or **Private** (either works).
5. Tick **Add a README file** so the repo is not empty and a `main` branch exists.
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

4. Scroll down, leave **Commit directly to the main branch** selected, and click **Commit changes**.

**What does this file say, in plain English?**

- The first block says: "I need the `random` provider (the plugin that makes random values)."
- The `resource` block says: "Create a random pet name made of **2** words, like `happy-otter`."
- The `output` block says: "Show me the name when you are done."

---

## Part 2: Connect HCP Terraform to your repo

### Step 3: Create a workspace

1. Sign in to **HCP Terraform** (app.terraform.io) and open your organization.
2. Click **New**, then **Workspace**.
3. Choose **Version control workflow**. This means "watch my GitHub repo and react to changes."
4. Choose **GitHub** and approve the connection when asked. If asked which repos to allow, include `run-demo`.
5. Select the `run-demo` repository.
6. Give the workspace a name (for example `run-demo`) and click **Create**.

---

## Part 3: Your first standard run

A **standard run** is the "real" kind. It can change things and update the state.

### Step 4: Start the run

1. Open your workspace and click the **Runs** tab.
2. If no run has started on its own, click **Actions**, then **Start new run**, and click **Start run**. (A brand new workspace sometimes needs this first nudge. After that, commits to `main` start runs automatically.)
3. Wait for the **Plan** stage to finish. Terraform is previewing: "I will create one random pet name."

### Step 5: Apply it

1. When the plan finishes, a **Confirm & Apply** button appears. This button is how you know it is a standard run.
2. Click **Confirm & Apply**, add a short comment if you like, and confirm.
3. When it finishes, open the **Outputs** section to see your pet name. Open the **States** tab to see the new state version.

You now have a state that remembers one random pet name.

---

## Part 4: See a speculative plan (pull request)

Now you will propose a change *without* touching `main`.

### Step 6: Create a new branch

1. In GitHub, open your repo and click the **branch dropdown** (it says `main`).
2. Type `test-change` in the box.
3. Click **Create branch: test-change from main**.

### Step 7: Make a change on that branch

1. Make sure the branch dropdown shows `test-change`.
2. Click `main.tf`, then click the **pencil icon** to edit.
3. Change `length = 2` to `length = 3`.
4. Click **Commit changes**, keep **Commit directly to the test-change branch** selected, and commit.

Your official `main` is untouched. Only the practice copy changed.

### Step 8: Open the pull request

1. Back on the repo's main page, you will see a banner with **Compare & pull request**. Click it.
2. Click **Create pull request**.

### Step 9: Watch HCP Terraform react

1. Go to your workspace's **Runs** tab in HCP Terraform.
2. A new run appears, labeled **Speculative plan**.
3. Open it. You will see Terraform previewing that the pet name would be replaced by a longer one (3 words instead of 2).
4. Notice what is **missing**: there is **no Confirm & Apply button**. Speculative plans can never be applied. They are preview only.
5. Go back to the pull request page in GitHub. Near the bottom you will see a **status check** from HCP Terraform showing the result of the plan. This is how reviewers see the effect of a change without leaving GitHub.

---

## Part 5: Back to a standard run

### Step 10: Merge the pull request

1. In GitHub, on the pull request page, click **Merge pull request**, then **Confirm merge**.

### Step 11: Watch the new standard run

1. Return to the **Runs** tab in HCP Terraform.
2. A new run starts, and this one is a **standard run** (not labeled speculative).
3. After the plan finishes, **Confirm & Apply** is back. Click it if you want to apply the change.
4. Check the **Outputs** again. Your pet name is now 3 words.

---

## What you should have seen

| Your action | Run type | Apply button? |
|---|---|---|
| First run / commit to `main` | Standard | Yes |
| Open a pull request | Speculative plan | No |
| Merge the pull request | Standard | Yes |

---

## Troubleshooting

- **No run appeared after creating the workspace.** Use **Actions > Start new run** once.
- **No speculative plan after opening the PR.** Check that the pull request targets `main` and that the workspace is connected to the `run-demo` repo (workspace **Settings > Version Control**).
- **GitHub does not list my repo.** Re-open the GitHub connection step and allow access to `run-demo`.
- **Provider download errors.** Make sure `main.tf` was copied exactly, including the `required_providers` block.

---

## Clean up

When you are done, remove what you made so nothing lingers:

1. In HCP Terraform, open the workspace, go to **Settings > Destruction and Deletion**, and click **Queue destroy plan** (and confirm the apply). Then delete the workspace.
2. In GitHub, open the repo, go to **Settings**, scroll to the bottom, and click **Delete this repository**.

---

## Key takeaway

> A **commit or merge to `main`** starts a **standard run** you can apply.
> A **pull request** starts a **speculative plan** that only previews.
> That is how teams review infrastructure changes safely before they go live.
