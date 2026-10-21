# Terraform Learning Lab: "Team Workspace Platform"

A hands-on project that takes you from your first `terraform apply` to modules, remote state, workspaces and refactoring. You build it in **11 milestones**. Every milestone has four parts:

1. **Concepts**: a short plain-English explanation of what you are about to use.
2. **Build**: fully commented code. Read the comments, they explain *what* each line does and *why* it is there.
3. **Hands-on checks**: things to try and what you should see.
4. **Exam check**: questions written in the style of the Terraform Associate exam (single answer, "choose two", scenario based), each with an explanation of why the right answer is right and why the others are wrong.

**The story:** your organization has several teams. Each team needs its own private storage bucket, an IAM group and users with access to only that bucket, and (optionally) a small lab server on a shared network. You build all of that, then rebuild it as reusable modules, then run it as `dev` and `prod`.

**Why start locally?** Part 1 uses only local files, so you can see state, plans, `count` vs `for_each` and variables clearly, with no cloud account and no cost. Part 2 then moves to AWS.

---

## Table of contents

1. [How to learn with this lab](#1-how-to-learn-with-this-lab)
2. [Prerequisites and cost](#2-prerequisites-and-cost)
3. [What you will build](#3-what-you-will-build)
4. [Folder structure](#4-folder-structure)
5. [Concept map](#5-concept-map)
6. [Part 1: Local warm-up (no cloud)](#6-part-1-local-warm-up-no-cloud): M0, M1, M2
7. [Part 2: The platform on AWS](#7-part-2-the-platform-on-aws): M3 to M10
8. [Final self-test](#8-final-self-test)
9. [Exam check score sheet](#9-exam-check-score-sheet)
10. [Extension challenges](#10-extension-challenges)
11. [Cleanup](#11-cleanup)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. How to learn with this lab

Use this loop at every step:

1. **Read** the goal and the code comments.
2. **Predict** the result of `terraform plan` (write your guess down).
3. **Run** it.
4. **Explain** any difference between your guess and reality.

Do not copy and paste blindly. Type the code. It slows you down enough to notice what each line does.

**About the Exam checks:** answer them *without* looking at the explanation, then expand it. For each one you miss, write down the concept in one sentence. The real exam is mostly multiple choice with tricky wrong options, so practice reading all four options before choosing. Question types you will meet:

- **Single answer:** choose one.
- **Choose two (or more):** select every correct option. Marks require all of them.
- **Scenario:** a short situation, "what happens?" or "what should you do?"
- **True or false** (shown as two options).

Commit to Git after every milestone so `git diff` shows exactly what changed.

---

## 2. Prerequisites and cost

| Need | Details |
|---|---|
| Terraform | **1.11 or newer** (`terraform version`). Needed for S3 native state locking in M7 |
| Git | Optional but strongly recommended |
| AWS account | Only for Part 2. Use a **sandbox** account, never production |
| AWS CLI v2 | Configured, `aws sts get-caller-identity` works |

**Cost:** Part 1 is free. In Part 2, S3, IAM, VPC, subnets, security groups and SSM standard parameters cost nothing or almost nothing. The only billable resource is the **optional lab server** (`t3.micro`), off by default. There is **no NAT gateway, load balancer or database** on purpose. Run `terraform destroy` at the end of each session.

---

## 3. What you will build

```
PART 1 (local only)                      PART 2 (AWS)

 variables + tfvars                       For each team (module, for_each):
        |                                   S3 bucket (versioned, private)
        v                                   Lifecycle rule (retention days)
 local_file per team  (for_each)            IAM group + policy for that bucket
 local_file per badge (count vs for_each)   IAM user per member
                                          Shared network module:
                                            VPC, subnets (for_each), security group (dynamic rules)
                                          Optional lab server (count toggle)
                                          SSM secret, remote state (S3), workspaces dev/prod
```

---

## 4. Folder structure

```
terraform-learning-lab/
├── README.md
├── .gitignore
├── 01-local-warmup/                 # Part 1 (M0 to M2)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars             # auto-loaded
│   ├── counts.tf                    # M2: the count trap
│   └── foreach.tf                   # M2: the fix
└── 02-platform/                     # Part 2 (M3 to M10)
    ├── versions.tf
    ├── providers.tf
    ├── backend.tf                   # M7
    ├── backend.hcl.example          # M7
    ├── variables.tf
    ├── locals.tf
    ├── data.tf
    ├── main.tf
    ├── moved.tf                     # M4
    ├── outputs.tf
    ├── dev.tfvars
    ├── prod.tfvars
    └── modules/
        ├── team/    main.tf  variables.tf  outputs.tf
        └── network/ main.tf  variables.tf  outputs.tf
```

`.gitignore`:

```gitignore
# Provider plugins and module cache, recreated by terraform init
.terraform/
# State files can contain secrets. NEVER commit them.
*.tfstate
*.tfstate.*
# Saved plans can also contain secrets
*.tfplan
*.log
# Backend settings with your bucket name
backend.hcl
# Generated files from Part 1
out/
crash.log
# KEEP .terraform.lock.hcl in Git. It pins provider versions for the whole team.
```

---

## 5. Concept map

| Milestone | New concepts |
|---|---|
| M0 | `init`, `plan`, `apply`, `destroy`, resources, providers, state, plan symbols, idempotency, implicit dependency, drift |
| M1 | `variable` types, defaults, validation, `terraform.tfvars` auto-loading, `-var-file`, `TF_VAR_`, precedence, `locals`, `output`, interpolation, heredoc |
| M2 | `count` vs `for_each` (index-shift trap), `for` expressions, splat, conditionals, functions, `terraform console` |
| M3 | Real provider, version constraints, lock file, data sources, `default_tags`, `for_each` over another resource, `terraform graph` |
| M4 | Child modules, inputs and outputs, module `for_each`, `moved` blocks |
| M5 | `flatten`, nested `for`, `aws_iam_policy_document`, `jsonencode` vs heredoc, explicit `depends_on` |
| M6 | Dynamic blocks, `count` toggle, `one()`, lifecycle, `precondition`, `postcondition`, `check` |
| M7 | Backends, `-backend-config`, state migration, locking, `state` commands, `import`, drift, `-refresh-only` |
| M8 | Workspaces, `terraform.workspace`, environments |
| M9 | `terraform_data`, `local-exec`, `-replace`, secrets in state, `TF_LOG` |
| M10 | Registry modules, version pinning, HCP Terraform |

---

# 6. Part 1: Local warm-up (no cloud)

```bash
mkdir -p terraform-learning-lab/01-local-warmup
cd terraform-learning-lab/01-local-warmup
git init
```

---

## M0: First resources, state and the plan symbols

**Goal:** understand the workflow and what state really is.

### Concepts

- **Provider:** a plugin that lets Terraform talk to a platform. Here `random` (makes random values) and `local` (makes files on your computer).
- **Resource:** one thing you want to exist. Its address is `TYPE.NAME`, for example `random_pet.lab`.
- **Implicit dependency:** if resource B uses an attribute of resource A, Terraform knows A must be built first. You never write the order.
- **State:** Terraform's record of what it built, mapping your names to real objects.
- **Idempotent:** running again with no changes does nothing.

### Build: `main.tf`

```hcl
# ===========================================================================
# 01-local-warmup/main.tf
# A tiny configuration that needs no cloud account. It creates one random
# name and one text file whose name uses that random value.
# ===========================================================================

# The "terraform" block configures Terraform ITSELF (not your infrastructure).
# It cannot use variables, because it is read before anything else.
terraform {
  # required_version: the Terraform CLI must satisfy this rule.
  # If your CLI is older, Terraform stops immediately with a clear message.
  required_version = ">= 1.5.0"

  # required_providers: which plugins this configuration needs and where to
  # download them. "terraform init" reads this block.
  required_providers {
    # random: generates random values. No credentials needed.
    random = {
      source  = "hashicorp/random" # namespace/type on registry.terraform.io
      version = "~> 3.6"           # allow 3.6 and later 3.x, but never 4.0
    }

    # local: creates files on the machine running Terraform.
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

# A RESOURCE block has the shape:  resource "TYPE" "NAME" { ...arguments... }
#   TYPE = random_pet   (decided by the provider: what kind of thing)
#   NAME = lab          (decided by YOU: how you refer to it in this config)
# Together the address is:  random_pet.lab
resource "random_pet" "lab" {
  length = 2 # two words, for example "happy-otter"
}

# This resource READS random_pet.lab.id in two arguments below.
# That reference is an IMPLICIT DEPENDENCY: Terraform builds random_pet.lab
# first, because it cannot know the id before it exists. You never state the order.
resource "local_file" "hello" {
  # path.module = the folder containing this .tf file.
  # "${ ... }" inside a string inserts the value of an expression.
  filename = "${path.module}/out/hello-${random_pet.lab.id}.txt"

  # The \n at the end adds a newline to the file.
  content = "Hello from Terraform. My lucky pet is ${random_pet.lab.id}\n"
}
```

### Run

```bash
terraform init        # downloads the two providers, creates .terraform/ and .terraform.lock.hcl
terraform plan        # preview only. Nothing is created.
terraform apply       # type: yes. Creates the pet and the file.
ls out/
head -40 terraform.tfstate     # look at what Terraform remembers
```

### Plan symbols (memorize)

| Symbol | Meaning |
|---|---|
| `+` | create |
| `-` | destroy |
| `~` | update in place |
| `-/+` | destroy then create (replace). Look for `# forces replacement` |
| `<=` | read (data source) |
| `(known after apply)` | the value does not exist until creation |

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| `terraform plan` again with no edits | "No changes" | Idempotency: desired state already equals real state |
| Edit the file's `content` text, then `plan` | `-/+` replace of `local_file.hello` | This resource cannot change content in place, so it is replaced |
| Delete `out/hello-*.txt` by hand, then `plan` | Plans to create the file again | Terraform refreshes against reality and finds drift |
| Open `terraform.tfstate`, find `random_pet.lab` | Real attribute values stored | State maps your names to real objects |

### Exam check

**Q1 (IaC concepts).** You run `terraform apply` three times in a row on an unchanged configuration. The first run creates 5 resources. What do the second and third runs do?

- A) Create 5 more resources each time
- B) Report that no changes are needed
- C) Destroy and recreate all 5 resources
- D) Fail because the state is already locked

<details><summary>Answer</summary>

**B.** Terraform is declarative and idempotent: it compares desired state with real state and applies only the difference. With no difference, nothing happens. A describes an imperative script. C only happens with forced replacement. D is unrelated to a normal sequential run.
</details>

**Q2 (Plan symbols).** A plan shows `-/+ local_file.hello (must be replaced)`. What will happen on `terraform apply`?

- A) The file is updated in place
- B) The existing file is destroyed and a new one is created
- C) The file is removed from state only
- D) The file is read as a data source

<details><summary>Answer</summary>

**B.** `-/+` means replace: destroy, then create. It happens when an argument cannot be changed in place. A would be `~`. C is `terraform state rm`. D would be `<=`.
</details>

**Q3 (State).** A developer deletes `terraform.tfstate`, but the real resources still exist. What will the next `terraform apply` most likely do?

- A) Discover the existing resources automatically and report no changes
- B) Try to create all resources again, because Terraform believes none exist
- C) Destroy all the real resources
- D) Restore the state from the provider

<details><summary>Answer</summary>

**B.** Terraform does not scan your account. Without state it thinks nothing is managed, so it plans to create everything, which may cause conflicts or duplicates. Recover from a state backup, or bring objects back with `import`. This is why remote, versioned state matters.
</details>

**Q4 (Dependencies).** Which configuration creates an **implicit** dependency of `local_file.hello` on `random_pet.lab`?

- A) `depends_on = [random_pet.lab]` inside `local_file.hello`
- B) Using `random_pet.lab.id` in an argument of `local_file.hello`
- C) Putting both blocks in the same file
- D) Giving both resources the name `lab`

<details><summary>Answer</summary>

**B.** Referencing another resource's attribute creates an implicit dependency. A is an **explicit** dependency. File layout (C) and names (D) never affect ordering.
</details>

### What you learned
- The workflow `init`, `plan`, `apply`, `destroy`.
- A resource has a type, a name and arguments. Its address is `TYPE.NAME`.
- Order comes from references. State is Terraform's memory. Plan compares code, state and reality.

Finish with `terraform destroy`.

---

## M1: Variables, tfvars, locals, outputs

**Goal:** make the configuration reusable and understand where values come from.

### Concepts

- **`variables.tf` declares, `terraform.tfvars` assigns.** A variable block says "an input called X exists, of this type". A tfvars file says "X equals this".
- **Locals** are values computed inside your configuration. Variables come from outside.
- **Outputs** print results and are how modules return data.
- **Precedence** (lowest to highest): `default`, `TF_VAR_` environment variable, `terraform.tfvars`, `terraform.tfvars.json`, `*.auto.tfvars`, then `-var` and `-var-file` in the order given.

### Build: `variables.tf`

```hcl
# ===========================================================================
# variables.tf : DECLARES inputs. It never holds environment-specific values.
# ===========================================================================

variable "project" {
  description = "Short project name" # shown in prompts and docs
  type        = string               # type constraint: only text is accepted
  default     = "learninglab"        # having a default makes the variable OPTIONAL

  # validation: your own rule, checked at plan time.
  validation {
    # can() returns false instead of an error if the expression fails.
    # regex() fails when the text does not match, so can() turns that into false.
    condition     = can(regex("^[a-z][a-z0-9-]{2,15}$", var.project))
    error_message = "project must be 3 to 16 characters: lowercase letters, digits, hyphens."
  }
}

variable "environment" {
  description = "dev or prod"
  type        = string
  default     = "dev"

  validation {
    # contains(list, value) is true when the value is in the list
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be \"dev\" or \"prod\"."
  }
}

# A MAP of OBJECTS: team name -> that team's settings.
# "object" means every team must have EXACTLY these attributes with these types.
variable "teams" {
  description = "Teams and their settings"
  type = map(object({
    members        = list(string) # usernames
    retention_days = number       # days to keep old data
  }))
  # No default, so this variable is REQUIRED. Terraform prompts if no value is given.
}
```

### Build: `terraform.tfvars`

```hcl
# terraform.tfvars is loaded AUTOMATICALLY (no flag needed).
# It only ASSIGNS values. It cannot declare variables or types.
environment = "dev"

teams = {
  alpha = { members = ["ama", "kofi"], retention_days = 30 }
  beta  = { members = ["yaw"],         retention_days = 90 }
}
```

### Add to `main.tf`

```hcl
# ---------------------------------------------------------------------------
# LOCALS: named values calculated inside the configuration.
# Use them when you would otherwise repeat the same expression many times.
# Declared in "locals" (plural), used as "local.NAME" (singular).
# ---------------------------------------------------------------------------
locals {
  name_prefix = "${var.project}-${var.environment}" # e.g. "learninglab-dev"
  is_prod     = var.environment == "prod"           # true or false
}

# ---------------------------------------------------------------------------
# for_each over a MAP creates one instance per map entry.
# Inside the block:
#   each.key   = the map key   (team name, such as "alpha")
#   each.value = the map value (that team's object)
# Instance addresses: local_file.team_readme["alpha"], local_file.team_readme["beta"]
# ---------------------------------------------------------------------------
resource "local_file" "team_readme" {
  for_each = var.teams

  filename = "${path.module}/out/${local.name_prefix}/${each.key}/README.txt"

  # A heredoc is a multi-line string. "<<-" removes the common leading
  # indentation so the code can stay neatly indented.
  content = <<-EOT
    Team: ${each.key}
    Environment: ${var.environment}
    Members: ${join(", ", each.value.members)}
    Retention: ${each.value.retention_days} days
  EOT
}
```

### Build: `outputs.tf`

```hcl
# Outputs print values after apply, and are how modules hand data to their parent.
output "team_files" {
  description = "Path of each team's README"

  # A "for expression" with braces builds a MAP.
  # Read it as: for each team and file, produce "team => filename".
  value = { for team, f in local_file.team_readme : team => f.filename }
}

output "total_members" {
  # Inner for builds a list of lists, flatten() merges them into one list,
  # length() counts the items.
  value = length(flatten([for t in var.teams : t.members]))
}
```

### Run

```bash
terraform init
terraform fmt                       # rewrite files in canonical style
terraform validate                  # check syntax and consistency (no cloud calls)
terraform plan
terraform apply
terraform output                    # all outputs
terraform output -json team_files   # one output as JSON
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| Create `prod.tfvars` with `environment = "prod"`, run `plan` with no flag | Still `dev` | `prod.tfvars` is not auto-loaded. Only `terraform.tfvars` and `*.auto.tfvars` are |
| `terraform plan -var-file=prod.tfvars` | `prod` | `-var-file` is loaded explicitly |
| `TF_VAR_environment=prod terraform plan` | Still `dev` | `terraform.tfvars` beats `TF_VAR_` |
| `terraform plan -var="environment=staging"` | Your validation error message | Validation runs at plan time |
| Delete the `teams` line from `terraform.tfvars` | Terraform prompts | The variable has no default |
| Add `owner = "sammy"` (undeclared) to `terraform.tfvars` | A warning only | A tfvars file cannot create a variable. On the command line with `-var` it is an error |

### Exam check

**Q1 (tfvars loading, choose two).** A directory contains `terraform.tfvars`, `prod.tfvars`, `staging.auto.tfvars` and `vars.json`. Which files does Terraform load automatically? Choose two.

- A) `prod.tfvars`
- B) `terraform.tfvars`
- C) `vars.json`
- D) `staging.auto.tfvars`

<details><summary>Answer</summary>

**B and D.** Only `terraform.tfvars`, `terraform.tfvars.json`, and files ending in `.auto.tfvars` or `.auto.tfvars.json` load automatically. `prod.tfvars` must be passed with `-var-file`. A plain `vars.json` is never auto-loaded.
</details>

**Q2 (Precedence).** The environment variable `TF_VAR_environment=prod` is set, `terraform.tfvars` contains `environment = "dev"`, and you run `terraform plan` with no flags. Which value is used?

- A) `prod`
- B) `dev`
- C) Terraform prompts for a value
- D) Terraform returns an error for a conflict

<details><summary>Answer</summary>

**B.** `terraform.tfvars` has higher precedence than `TF_VAR_` environment variables. Order, lowest to highest: default, `TF_VAR_`, `terraform.tfvars`, `terraform.tfvars.json`, `*.auto.tfvars`, `-var` and `-var-file` (in order given). There is no conflict error, the higher source simply wins.
</details>

**Q3 (Required variables).** A variable has no `default` and no value is supplied anywhere. You run `terraform plan` in an interactive terminal. What happens?

- A) Terraform uses `null`
- B) Terraform fails immediately in all cases
- C) Terraform prompts you to type a value
- D) Terraform uses an empty string

<details><summary>Answer</summary>

**C.** A variable without a default is required, and Terraform prompts for it interactively. With `-input=false` or in automation, it errors instead. It never invents `null` or an empty string.
</details>

**Q4 (Locals).** Which statement about local values is correct?

- A) They can be set with `-var` on the command line
- B) They are named expressions computed inside a module and referenced as `local.NAME`
- C) They are referenced as `locals.NAME`
- D) They cannot reference input variables

<details><summary>Answer</summary>

**B.** Locals are computed from other values (including variables) and cannot be set from outside. You declare them in a `locals` block (plural) and use `local.name` (singular). A is wrong because only variables take outside input. C has the wrong prefix. D is wrong because locals commonly use variables.
</details>

**Q5 (Outputs).** Which command prints the value of one output as a plain string with no quotes, suitable for a shell script?

- A) `terraform output -json website_url`
- B) `terraform output -raw website_url`
- C) `terraform show website_url`
- D) `terraform state show website_url`

<details><summary>Answer</summary>

**B.** `-raw` prints the bare string. `-json` wraps it in JSON (quotes included for strings). `show` and `state show` do not read outputs this way.
</details>

### What you learned
- `variables.tf` **declares**, `terraform.tfvars` **assigns**, and the precedence order.
- Locals vs variables, outputs and the `-raw`/`-json` flags.
- `for_each` over a map, heredocs, interpolation, `join`, `flatten`, `length`.

---

## M2: count vs for_each, expressions, functions

**Goal:** see for yourself why `count` is risky with lists of distinct items.

### Concepts

- **`count`** makes N copies identified by **index** (`[0]`, `[1]`, ...). Good for identical copies or an on/off switch.
- **`for_each`** makes one copy per item, identified by **key** (`["alice"]`). Good for distinct items.
- **`for` expressions** transform collections. `[ ]` gives a list, `{ }` gives a map, `if` filters.
- **Functions** are built in (you cannot write your own). Test them in `terraform console`.

### Build: `counts.tf` (the trap)

```hcl
variable "member_names" {
  type    = list(string)
  default = ["ama", "kofi", "yaw"]
}

# COUNT: each instance is identified by its POSITION in the list.
#   badge_count[0] = ama, badge_count[1] = kofi, badge_count[2] = yaw
resource "local_file" "badge_count" {
  count = length(var.member_names) # how many copies to make

  # count.index is the current position (0, 1, 2 ...)
  filename = "${path.module}/out/badges-count/${var.member_names[count.index]}.txt"
  content  = "Badge for ${var.member_names[count.index]}\n"
}
```

Apply it. Then **remove `"ama"`** from the list and run `terraform plan`.

<details><summary>What does the plan do, and why?</summary>

State holds `[0]=ama`, `[1]=kofi`, `[2]=yaw`. After removal the list is `["kofi","yaw"]`, so Terraform wants `[0]=kofi` and `[1]=yaw` and no `[2]`. It **replaces** `[0]` and `[1]` (their filenames changed) and **destroys** `[2]`. You wanted one removal but everything shifted. With servers or databases this can be destructive.
</details>

### Build: `foreach.tf` (the fix)

```hcl
# FOR_EACH: each instance is identified by a KEY, not a position.
# for_each accepts a MAP or a SET of strings. A list must be converted with toset().
resource "local_file" "badge_each" {
  for_each = toset(var.member_names) # {"ama","kofi","yaw"}: each item is its own key

  # For a set, each.key and each.value are the same string.
  filename = "${path.module}/out/badges-each/${each.key}.txt"
  content  = "Badge for ${each.key}\n"
}
```

Apply, remove `"ama"` again and compare. Only `badge_each["ama"]` is destroyed.

### Expressions and functions: `terraform console`

```bash
terraform console
```

Predict each result, then press Enter:

```hcl
var.teams["alpha"].members                                # list: ["ama", "kofi"]
keys(var.teams)                                           # ["alpha", "beta"]
[for t, cfg in var.teams : upper(t)]                      # ["ALPHA", "BETA"]
{ for t, cfg in var.teams : t => length(cfg.members) }    # { alpha = 2, beta = 1 }
[for t, cfg in var.teams : t if cfg.retention_days > 60]  # ["beta"]  (if filters)
flatten([for t, cfg in var.teams : [for m in cfg.members : "${t}/${m}"]])
                                                          # ["alpha/ama","alpha/kofi","beta/yaw"]
local.is_prod ? "careful" : "relax"                       # "relax"  (condition ? yes : no)
merge({ a = 1 }, { a = 2, b = 3 })                        # { a = 2, b = 3 }  (later wins)
lookup({ a = 1 }, "z", 0)                                 # 0  (default when key is missing)
element(["a", "b", "c"], 4)                               # "b"  (wraps around: 4 mod 3 = 1)
toset(["a", "b", "a"])                                    # ["a", "b"]  (unique, unordered)
format("team-%03d", 7)                                    # "team-007"
cidrsubnet("10.20.0.0/16", 8, 1)                          # "10.20.1.0/24"
```

### Exam check

**Q1 (count behavior).** A resource uses `count = length(var.names)` and `var.names` is `["web", "api", "db"]`. You remove `"web"` and run `terraform plan`. What is the most likely result?

- A) Only the first instance is destroyed
- B) Nothing changes
- C) Instances shift index, so two are modified or replaced and the last index is destroyed
- D) Terraform returns an error because count cannot use lists

<details><summary>Answer</summary>

**C.** `count` tracks instances by index, so removing the first item moves every later item down one position. `for_each` with `toset()` avoids this because each instance has a stable key. A describes the `for_each` behavior.
</details>

**Q2 (for_each input).** Which value can be given to `for_each` **without conversion**?

- A) `list(string)`
- B) `map(string)`
- C) `number`
- D) `string`

<details><summary>Answer</summary>

**B.** `for_each` accepts a map or a set of strings. A list must be converted with `toset()` (or reshaped into a map). Numbers and single strings are not collections.
</details>

**Q3 (for expressions).** What is the value of `[for n in [1, 2, 3, 4] : n * 2 if n > 2]`?

- A) `[2, 4, 6, 8]`
- B) `[6, 8]`
- C) `[3, 4]`
- D) `[1, 2]`

<details><summary>Answer</summary>

**B.** The `if` clause filters first (keeps 3 and 4), then the expression doubles them: 6 and 8. C is the filtered items before doubling. A ignores the filter.
</details>

**Q4 (Functions).** What does `element(["a", "b", "c"], 4)` return?

- A) An error
- B) `"c"`
- C) `"b"`
- D) `null`

<details><summary>Answer</summary>

**C.** `element` wraps around when the index is larger than the list: 4 modulo 3 is 1, which is `"b"`. Contrast with `list[4]` indexing, which errors. Remember also `lookup()` returns a default for a missing key, `merge()` lets later maps win.
</details>

**Q5 (Meta-arguments).** Which statement is correct?

- A) `count` and `for_each` can be used together on the same resource
- B) `count` instances are identified by index and `for_each` instances by key
- C) `count` requires a map
- D) `for_each` requires a number

<details><summary>Answer</summary>

**B.** You cannot combine `count` and `for_each` on one block (A). `count` takes a number (C is wrong) and `for_each` takes a map or set (D is wrong).
</details>

### What you learned
- **`count` vs `for_each`**, and the index-shift trap (a very common exam topic).
- `for` expressions with `if` filters, splat, conditionals.
- `merge`, `lookup`, `flatten`, `toset`, `join`, `element`, `cidrsubnet`, and `terraform console`.

Run `terraform destroy` before moving on.

---

# 7. Part 2: The platform on AWS

```bash
cd ..
mkdir -p 02-platform/modules/team 02-platform/modules/network
cd 02-platform
```

---

## M3: AWS provider, data sources, implicit dependencies

**Goal:** talk to a real cloud and build one bucket per team.

### Concepts

- **Version constraints:** `~> 5.60` means `>= 5.60` and `< 6.0`. `~> 5.60.1` means `>= 5.60.1` and `< 5.61.0`.
- **Lock file:** `.terraform.lock.hcl` records the exact provider version chosen. Commit it. Upgrade deliberately with `terraform init -upgrade`.
- **Data source:** reads something that already exists or is computed. It never creates anything.
- **`default_tags`:** tags set once on the provider and applied to every taggable resource.

### Build: `versions.tf`

```hcl
terraform {
  # CLI constraint: at least 1.11 (for S3 native locking later), below 2.0
  required_version = ">= 1.11.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60" # ">= 5.60 and < 6.0": new features, no surprise breaking major version
    }
  }
}
```

### Build: `providers.tf`

```hcl
# The provider block CONFIGURES a plugin (here: which region to use).
# Credentials are NOT written here. The AWS provider reads your AWS CLI profile
# or environment variables. Never hardcode keys in .tf files.
provider "aws" {
  region = var.region

  # default_tags: applied to EVERY taggable resource this provider creates,
  # including resources inside child modules. Saves repeating tags everywhere.
  default_tags {
    tags = local.common_tags
  }
}
```

### Build: `variables.tf`

```hcl
variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "project" {
  type    = string
  default = "learninglab"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,15}$", var.project))
    error_message = "project must be 3 to 16 characters: lowercase letters, digits, hyphens."
  }
}

variable "environment" {
  description = "dev or prod. No default, so the caller must choose."
  type        = string

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be \"dev\" or \"prod\"."
  }
}

variable "teams" {
  description = "Teams and their settings"
  type = map(object({
    members        = list(string)
    retention_days = number
  }))
}

variable "extra_tags" {
  description = "Additional tags merged onto every resource"
  type        = map(string)
  default     = {}
}
```

### Build: `locals.tf`

```hcl
locals {
  # Used in every resource name so dev and prod never collide in one account
  name_prefix = "${var.project}-${var.environment}"

  # Bool used for protections that differ per environment
  is_prod = var.environment == "prod"

  # merge(a, b): combine two maps. If a key exists in both, b wins.
  common_tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
      Workspace   = terraform.workspace # built-in: the selected workspace name
    },
    var.extra_tags
  )
}
```

### Build: `data.tf`

```hcl
# DATA SOURCES read information. Address style: data.TYPE.NAME.ATTRIBUTE

# "Who am I?" gives the account ID, used below to make bucket names globally unique.
data "aws_caller_identity" "current" {}

# Which availability zones can I use in this region right now?
data "aws_availability_zones" "available" {
  state = "available"
}
```

### Build: `dev.tfvars`

```hcl
# Not auto-loaded (name is not terraform.tfvars). Use: -var-file=dev.tfvars
environment = "dev"

teams = {
  alpha = { members = ["ama", "kofi"], retention_days = 30 }
  beta  = { members = ["yaw"],         retention_days = 90 }
}
```

### Build: `main.tf` (resources directly in the root, for now)

```hcl
# One bucket PER TEAM. for_each over the teams map gives each team its own instance.
# Address examples: aws_s3_bucket.team["alpha"], aws_s3_bucket.team["beta"]
resource "aws_s3_bucket" "team" {
  for_each = var.teams

  # Bucket names are global across all of AWS, so we add the account ID.
  bucket = "${local.name_prefix}-${each.key}-${data.aws_caller_identity.current.account_id}"

  # Lets Terraform delete a non-empty bucket. Acceptable outside prod.
  force_destroy = !local.is_prod
}

# for_each over ANOTHER RESOURCE: iterate the buckets we just defined.
# Because we use each.value.id (the bucket's id), Terraform knows this must wait
# for the bucket. That is an IMPLICIT DEPENDENCY, created purely by the reference.
resource "aws_s3_bucket_versioning" "team" {
  for_each = aws_s3_bucket.team

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled" # keep old versions of objects
  }
}

# Block every form of public access. Good security default.
resource "aws_s3_bucket_public_access_block" "team" {
  for_each = aws_s3_bucket.team

  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### Build: `outputs.tf`

```hcl
output "team_buckets" {
  description = "Bucket name per team"
  value       = { for team, b in aws_s3_bucket.team : team => b.id }
}
```

### Run

```bash
terraform init
cat .terraform.lock.hcl
terraform fmt && terraform validate
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
terraform graph | head -40
terraform state list
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| Count the resources in the first plan | 6 (3 types x 2 teams) | `for_each` makes one instance per team for each resource |
| `terraform init -upgrade` then view the lock file | Provider moves to the newest version allowed by `~> 5.60` | `-upgrade` re-evaluates constraints |
| Add a third team and plan | 3 new resources | New key, so only new instances |
| Remove the middle team and plan | Only that team's 3 resources destroyed | Stable keys do not shift |
| `terraform graph` | Edges from versioning and public access block to the bucket | References become graph edges |

### Exam check

**Q1 (Version constraints).** What does `version = "~> 5.60.1"` allow?

- A) `>= 5.60.1` and `< 5.61.0`
- B) `>= 5.60.1` and `< 6.0.0`
- C) Exactly `5.60.1`
- D) Any version `>= 5.60.1`

<details><summary>Answer</summary>

**A.** The pessimistic operator lets only the rightmost component increase. With three components (`5.60.1`) only the patch number can rise. With two (`~> 5.60`) the minor can rise, which is answer B's range.
</details>

**Q2 (Lock file).** Your constraint is `~> 5.60` and the lock file records `5.62.0`. Version `5.70.0` is released. You run `terraform init`. Which version is used?

- A) `5.70.0`
- B) `5.62.0`
- C) `6.0.0`
- D) `5.60.0`

<details><summary>Answer</summary>

**B.** Terraform keeps the version recorded in `.terraform.lock.hcl`. It only moves to a newer allowed version when you run `terraform init -upgrade`. This is why the lock file is committed: everyone gets the same provider build.
</details>

**Q3 (Data sources).** What does a `data` block do?

- A) Creates a new resource in the cloud
- B) Reads existing or computed information and exposes it as attributes
- C) Stores the Terraform state
- D) Declares an input variable

<details><summary>Answer</summary>

**B.** Data sources are read-only lookups, referenced as `data.TYPE.NAME.ATTRIBUTE`. Resources create and manage objects (A). State is a backend concern (C). Variables use `variable` blocks (D).
</details>

**Q4 (Implicit dependencies).** A resource has `for_each = aws_s3_bucket.team` and uses `bucket = each.value.id`. What ordering does Terraform guarantee?

- A) None, resources are always created in parallel
- B) Each instance is created only after its bucket exists, because of the reference
- C) All versioning resources are created before any bucket
- D) Instances are created in alphabetical order

<details><summary>Answer</summary>

**B.** Using the bucket's `id` is a reference, so the graph has an edge from the bucket to the dependent resource. Unrelated resources (for example the two teams' buckets) are still created in parallel, up to the default of 10 at once.
</details>

**Q5 (Provider configuration).** What is the effect of a `default_tags` block inside a provider block?

- A) It tags only the first resource created
- B) It applies the tags to all taggable resources created through that provider configuration
- C) It creates a new tag resource
- D) It filters which resources Terraform manages

<details><summary>Answer</summary>

**B.** `default_tags` apply to every taggable resource that provider configuration creates, including inside child modules. Resource-level `tags` are merged on top.
</details>

### What you learned
- Providers, `required_providers`, version constraints, the lock file.
- Data sources vs resources. Implicit dependencies and the dependency graph.
- `for_each` over a variable and over another resource. `default_tags`.

---

## M4: Refactor into a child module (moved blocks)

**Goal:** package the per-team resources into a reusable module **without destroying anything**.

### Concepts

- **Module:** a folder of Terraform code with inputs (variables), resources, and outputs. Like a function.
- **Root module:** the folder you run commands in. **Child module:** one it calls.
- **A module is a sealed box.** The parent passes values as arguments and reads values only through the module's outputs.
- **`moved` block:** tells Terraform "this object did not disappear, it changed address". The old alternative is `terraform state mv`.

### Build: `modules/team/variables.tf`

```hcl
# Module INPUTS. The parent sets these as arguments in its "module" block.

variable "name_prefix" {
  description = "Prefix for resource names, for example learninglab-dev"
  type        = string
}

variable "team_name" {
  description = "Name of this team, for example alpha"
  type        = string
}

variable "account_id" {
  description = "AWS account ID, used for globally unique bucket names"
  type        = string
}

variable "force_destroy" {
  description = "Allow deleting a non-empty bucket"
  type        = bool
  default     = false
}
```

### Build: `modules/team/main.tf`

```hcl
# The same three resources as in M3, now INSIDE a module.
# They are named "this" because a module usually contains one of each kind.
# The bucket name is built EXACTLY as before, so the real bucket does not change.

resource "aws_s3_bucket" "this" {
  bucket        = "${var.name_prefix}-${var.team_name}-${var.account_id}"
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id # implicit dependency, same as before

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### Build: `modules/team/outputs.tf`

```hcl
# Module OUTPUTS. The ONLY way a child shares data with its parent.
# The parent reads this as: module.team["alpha"].bucket_name
output "bucket_name" {
  description = "Name of the team bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "ARN of the team bucket"
  value       = aws_s3_bucket.this.arn
}
```

### Change the root `main.tf`

Delete the three old resource blocks and replace them with:

```hcl
# MODULE with for_each: one copy of the whole module per team.
# Instance addresses look like: module.team["alpha"], module.team["beta"]
module "team" {
  source   = "./modules/team" # local folder path
  for_each = var.teams        # each.key = team name, each.value = its settings object

  # These arguments are the child's INPUT VARIABLES
  name_prefix   = local.name_prefix
  team_name     = each.key
  account_id    = data.aws_caller_identity.current.account_id
  force_destroy = !local.is_prod
}
```

Update `outputs.tf`:

```hcl
output "team_buckets" {
  # We cannot read module internals. We use the module's declared OUTPUT.
  value = { for team, m in module.team : team => m.bucket_name }
}
```

### First, predict (do NOT add moved blocks yet)

```bash
terraform init          # needed because a new module appeared
terraform plan -var-file=dev.tfvars
```

The plan shows **6 destroys and 6 creates**. Terraform sees old addresses vanish and new addresses appear, so it assumes a rebuild. For buckets with data that would be a disaster. **Do not apply.**

### Fix it with `moved` blocks: `moved.tf`

```hcl
# A "moved" block says: "this object has a NEW ADDRESS, it is not new".
# Terraform updates state to the new address and changes nothing real.
# Addresses must be written out, so we need one block per object per team
# (2 teams x 3 resources = 6 blocks).

moved {
  from = aws_s3_bucket.team["alpha"]               # old address (root, for_each key)
  to   = module.team["alpha"].aws_s3_bucket.this   # new address (inside the module)
}
moved {
  from = aws_s3_bucket_versioning.team["alpha"]
  to   = module.team["alpha"].aws_s3_bucket_versioning.this
}
moved {
  from = aws_s3_bucket_public_access_block.team["alpha"]
  to   = module.team["alpha"].aws_s3_bucket_public_access_block.this
}

moved {
  from = aws_s3_bucket.team["beta"]
  to   = module.team["beta"].aws_s3_bucket.this
}
moved {
  from = aws_s3_bucket_versioning.team["beta"]
  to   = module.team["beta"].aws_s3_bucket_versioning.this
}
moved {
  from = aws_s3_bucket_public_access_block.team["beta"]
  to   = module.team["beta"].aws_s3_bucket_public_access_block.this
}
```

```bash
terraform plan -var-file=dev.tfvars     # each object shows "has moved". Summary: 0 to add, 0 to change, 0 to destroy
terraform apply -var-file=dev.tfvars
terraform state list                    # now shows module.team[...] addresses
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| Plan without `moved.tf` | 6 destroy, 6 create | Address change looks like delete plus new |
| Plan with `moved.tf` | "has moved", no real changes | State is re-addressed only |
| In `outputs.tf`, try `module.team["alpha"].aws_s3_bucket.this.id` | Error | A parent cannot reach inside a module. Use the output |

### Exam check

**Q1 (Module outputs).** A parent module needs the VPC ID created inside a child module named `network`. How can it obtain it?

- A) `module.network.aws_vpc.this.id`
- B) Through an `output` declared in the child, read as `module.network.vpc_id`
- C) By reading the child's state file
- D) With a `data` block pointing at the child's folder

<details><summary>Answer</summary>

**B.** Module internals are encapsulated. A child exposes values only through `output` blocks, and the parent reads them as `module.NAME.OUTPUT_NAME`. A is invalid, and C and D are not supported ways to read child values.
</details>

**Q2 (Addresses).** Which address refers to the bucket inside the module instance for team `alpha` (module declared with `for_each`)?

- A) `module.team.alpha.aws_s3_bucket.this`
- B) `module.team["alpha"].aws_s3_bucket.this`
- C) `aws_s3_bucket.this["alpha"]`
- D) `module["team"].alpha.aws_s3_bucket.this`

<details><summary>Answer</summary>

**B.** A module with `for_each` produces instances addressed with a key in square brackets, then the resource address inside the module follows.
</details>

**Q3 (moved).** What is the purpose of a `moved` block?

- A) To copy a resource to another region
- B) To tell Terraform an existing object has a new address so it is not destroyed and recreated
- C) To move the state file to another backend
- D) To delete a resource from state

<details><summary>Answer</summary>

**B.** `moved` is for refactoring (renaming resources, moving them into or out of modules). The older manual equivalent is `terraform state mv`. Moving the state file (C) is done with `terraform init -migrate-state`. Deleting from state (D) is `state rm`.
</details>

**Q4 (Module installation).** You add a new `module` block and run `terraform plan`. Terraform says the module is not installed. What should you run?

- A) `terraform apply`
- B) `terraform refresh`
- C) `terraform init` (or `terraform get`)
- D) `terraform validate`

<details><summary>Answer</summary>

**C.** Modules are downloaded or linked during `init` (or `get`). Run it again whenever you add a module or change its `source` or `version`.
</details>

**Q5 (Module sources).** Which `source` allows a `version` argument?

- A) `"./modules/team"`
- B) `"terraform-aws-modules/vpc/aws"`
- C) `"git::https://example.com/repo.git"`
- D) `"../shared"`

<details><summary>Answer</summary>

**B.** Only **registry** modules (public or private) support `version`. Git sources are pinned with `?ref=TAG`, and local paths have no versions.
</details>

### What you learned
- A module has inputs, resources and outputs. Root vs child module. `for_each` on a module.
- **`moved` blocks** refactor safely. Why a module change needs `terraform init`.

---

## M5: IAM inside the module, explicit dependency, flatten

**Goal:** give each team a group and users limited to their own bucket, and learn when `depends_on` is required.

### Concepts

- **Explicit dependency (`depends_on`)** is for a relationship that exists in reality but is invisible in code, because no value is passed between the two resources.
- **`aws_iam_policy_document`** is a data source that builds policy JSON from HCL. It makes no AWS call.
- **`jsonencode()`** converts an HCL object into a JSON string.
- **`flatten()`** turns nested lists into one list.

### Add to `modules/team/variables.tf`

```hcl
variable "members" {
  description = "Usernames of the team members"
  type        = list(string)
}

variable "retention_days" {
  description = "Days to keep old object versions"
  type        = number
}
```

### Add to `modules/team/main.tf`

```hcl
# --- Lifecycle rule: delete OLD VERSIONS of objects after N days ---
resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "expire-old-versions"
    status = "Enabled"

    filter {} # empty filter = apply to every object

    noncurrent_version_expiration {
      noncurrent_days = var.retention_days
    }
  }

  # EXPLICIT DEPENDENCY.
  # Nothing in this resource references the versioning resource, so Terraform
  # sees no relationship. But AWS requires versioning to be enabled first.
  # depends_on states that hidden ordering rule.
  depends_on = [aws_s3_bucket_versioning.this]
}

# --- IAM group for the team ---
resource "aws_iam_group" "this" {
  name = "${var.name_prefix}-${var.team_name}"
}

# A DATA SOURCE used as a policy builder. HCL in, JSON out, no quoting mistakes.
# This statement lets users LIST the bucket (needs the bucket ARN)...
data "aws_iam_policy_document" "team_access" {
  statement {
    sid       = "ListTeamBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.this.arn] # reference = implicit dependency on the bucket
  }

  # ...and READ/WRITE the objects inside it (needs "/*" after the ARN).
  statement {
    sid       = "ReadWriteTeamObjects"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.this.arn}/*"]
  }
}

# Attach the generated JSON to the group as an inline policy.
resource "aws_iam_group_policy" "this" {
  name   = "team-bucket-access"
  group  = aws_iam_group.this.name
  policy = data.aws_iam_policy_document.team_access.json # .json is the rendered policy string
}

# One IAM user per member. toset() converts the list so for_each can use it.
# Address example: aws_iam_user.member["ama"]
resource "aws_iam_user" "member" {
  for_each = toset(var.members)

  name          = "${var.name_prefix}-${var.team_name}-${each.key}"
  force_destroy = true # allow deletion even if the user has extra credentials
}

# Put every user in the team group. Iterating over aws_iam_user.member means one
# membership per user, and each.value.name creates the dependency on that user.
resource "aws_iam_user_group_membership" "member" {
  for_each = aws_iam_user.member

  user   = each.value.name
  groups = [aws_iam_group.this.name]
}
```

### Add to `modules/team/outputs.tf`

```hcl
output "group_name" {
  value = aws_iam_group.this.name
}

output "user_names" {
  # for expression producing a LIST of user names
  value = [for u in aws_iam_user.member : u.name]
}
```

### Update the module call in the root `main.tf`

```hcl
module "team" {
  source   = "./modules/team"
  for_each = var.teams

  name_prefix    = local.name_prefix
  team_name      = each.key
  account_id     = data.aws_caller_identity.current.account_id
  force_destroy  = !local.is_prod
  members        = each.value.members        # NEW: passed from the team's object
  retention_days = each.value.retention_days # NEW
}
```

### Add to root `outputs.tf`

```hcl
output "team_users" {
  value = { for team, m in module.team : team => m.user_names }
}

# Nested for + flatten: turn { alpha = [ama, kofi], beta = [yaw] } into one flat list.
output "all_members" {
  value = flatten([
    for team, cfg in var.teams : [
      for member in cfg.members : "${team}/${member}"
    ]
  ])
}
```

```bash
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
terraform output
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| Add member `efua` to team beta, plan | 2 new resources (user and membership) | Stable keys, existing users untouched |
| `terraform state list \| grep member` | `module.team["alpha"].aws_iam_user.member["ama"]` | module key, resource, resource key |
| Rewrite the policy using `jsonencode()` then `plan` | No real change | Same permissions, different way to write JSON |

### Exam check

**Q1 (depends_on).** When is `depends_on` required?

- A) Whenever one resource uses an attribute of another
- B) When a dependency exists but is not visible through any reference in the configuration
- C) For every module call
- D) Never, Terraform always detects every dependency

<details><summary>Answer</summary>

**B.** References create implicit dependencies automatically (A). `depends_on` is for hidden relationships such as permissions or settings that must exist first. Overuse makes plans slower and hides intent.
</details>

**Q2 (flatten).** What does `flatten([[1, 2], [3, [4]]])` return?

- A) `[[1, 2], [3, [4]]]`
- B) `[1, 2, 3, [4]]`
- C) `[1, 2, 3, 4]`
- D) `[4, 3, 2, 1]`

<details><summary>Answer</summary>

**C.** `flatten` removes all levels of nesting and returns one flat list in the original order.
</details>

**Q3 (jsonencode and data sources).** Which statements are correct? Choose two.

- A) `jsonencode()` converts an HCL value into a JSON string
- B) `aws_iam_policy_document` is a resource that creates a policy in AWS
- C) `data.aws_iam_policy_document.x.json` gives the policy as a JSON string
- D) A heredoc is validated as JSON by Terraform when assigned to a `policy` argument

<details><summary>Answer</summary>

**A and C.** `aws_iam_policy_document` is a **data source** (B is wrong): it renders JSON locally and creates nothing. A heredoc is just a string, Terraform does not check it as JSON (D is wrong), which is why `jsonencode()` is less error prone.
</details>

**Q4 (Addresses).** In `module.team["alpha"].aws_iam_user.member["ama"]`, what does `"ama"` represent?

- A) The module instance key
- B) The `for_each` key of the resource inside the module instance
- C) The name of the AWS account
- D) The index of a `count` instance

<details><summary>Answer</summary>

**B.** `"alpha"` is the module's `for_each` key, `aws_iam_user.member` is the resource, and `"ama"` is that resource's own `for_each` key. A `count` instance would be written `[0]`, with no quotes.
</details>

### What you learned
- `flatten` and nested `for` expressions. `depends_on` and when it is truly needed.
- `jsonencode` vs heredoc vs `aws_iam_policy_document`. Address anatomy in modules.

---

## M6: Network module, dynamic blocks, count toggle, lifecycle, conditions

**Goal:** add a shared network and an optional server, and use Terraform's guardrails.

### Concepts

- **Dynamic block:** generates repeated nested blocks (such as firewall rules) from a collection.
- **`count` as a switch:** `count = condition ? 1 : 0`.
- **`one()`:** turns a list of 0 or 1 items into a single value (or `null`).
- **Lifecycle:** `create_before_destroy`, `ignore_changes`, `prevent_destroy`, `replace_triggered_by`.
- **Guardrails:** variable `validation` (inputs), `precondition` (before a resource), `postcondition` (after), `check` (warning only).

### Build: `modules/network/variables.tf`

```hcl
variable "name_prefix" {
  type = string
}

variable "vpc_cidr" {
  description = "IP range of the whole network, for example 10.20.0.0/16"
  type        = string
}

variable "azs" {
  description = "Availability zones to spread subnets across"
  type        = list(string)
}

# A LIST of OBJECTS. Each object is one firewall rule. This drives the dynamic block.
variable "ingress_rules" {
  description = "Inbound rules for the lab security group"
  type = list(object({
    description = string
    port        = number
    cidr        = string
  }))
}
```

### Build: `modules/network/main.tf`

```hcl
locals {
  # Turn the list of AZs into a map so for_each can use stable keys:
  #   { "eu-west-1a" = 0, "eu-west-1b" = 1 }
  az_index = { for i, az in var.azs : az => i }

  # Dynamic blocks need a collection. A map keyed by "port-cidr" keeps each rule
  # stable even if you reorder the list:  { "443-0.0.0.0/0" = {...} }
  rules = { for r in var.ingress_rules : "${r.port}-${r.cidr}" => r }
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${var.name_prefix}-vpc" }
}

# One public subnet per availability zone.
resource "aws_subnet" "public" {
  for_each = local.az_index

  vpc_id            = aws_vpc.this.id # implicit dependency on the VPC
  availability_zone = each.key        # "eu-west-1a" and so on

  # cidrsubnet(prefix, newbits, netnum): add 8 bits to a /16 to get /24 slices.
  #   cidrsubnet("10.20.0.0/16", 8, 0) = 10.20.0.0/24
  #   cidrsubnet("10.20.0.0/16", 8, 1) = 10.20.1.0/24
  cidr_block = cidrsubnet(var.vpc_cidr, 8, each.value)

  tags = { Name = "${var.name_prefix}-public-${each.key}" }
}

resource "aws_security_group" "lab" {
  name_prefix = "${var.name_prefix}-lab-" # AWS appends a unique suffix
  description = "Lab server access"
  vpc_id      = aws_vpc.this.id

  # DYNAMIC BLOCK: write the nested block ONCE, Terraform generates one copy
  # per element of for_each. Inside content {} the iterator is named after the
  # block ("ingress"), so we use ingress.key and ingress.value.
  dynamic "ingress" {
    for_each = local.rules

    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = [ingress.value.cidr]
    }
  }

  # All outbound traffic allowed ("-1" means every protocol)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.name_prefix}-lab-sg" }

  lifecycle {
    # If this resource must be replaced, build the NEW one first, then delete the old.
    # name_prefix gives the new one a different name, so both can exist at once.
    create_before_destroy = true
  }
}
```

### Build: `modules/network/outputs.tf`

```hcl
output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  # values() turns the map of subnets into a list, [*].id is a SPLAT expression:
  # "take the id of every item". Same as: [for s in values(...) : s.id]
  value = values(aws_subnet.public)[*].id
}

output "security_group_id" {
  value = aws_security_group.lab.id
}
```

### Add to root `variables.tf`

```hcl
variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"

  validation {
    # cidrhost() errors on an invalid CIDR, can() turns that error into false
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR block."
  }
}

variable "az_count" {
  description = "Number of availability zones"
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 1 && var.az_count <= 3
    error_message = "az_count must be 1, 2 or 3."
  }
}

variable "ingress_rules" {
  type = list(object({
    description = string
    port        = number
    cidr        = string
  }))
  default = [
    { description = "HTTPS", port = 443, cidr = "0.0.0.0/0" },
  ]
}

variable "enable_lab_server" {
  description = "Create the optional lab EC2 instance"
  type        = bool
  default     = false
}

variable "lab_instance_type" {
  type    = string
  default = "t3.micro"
}
```

### Add to root `data.tf`

```hcl
# Find the newest Amazon Linux 2023 image. AMI IDs differ by region and change
# over time, so hardcoding one would break. A data source stays correct.
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  lifecycle {
    # POSTCONDITION: checked AFTER the data is read. "self" is this data source.
    postcondition {
      condition     = self.architecture == "x86_64"
      error_message = "The AMI must be x86_64 to match the instance type."
    }
  }
}
```

### Add to root `locals.tf`

```hcl
locals {
  # slice(list, start, end) takes the first az_count zone names
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}
```

### Add to root `main.tf`

```hcl
module "network" {
  source = "./modules/network"

  name_prefix   = local.name_prefix
  vpc_cidr      = var.vpc_cidr
  azs           = local.azs
  ingress_rules = var.ingress_rules
}

# COUNT AS AN ON/OFF SWITCH:
#   enable_lab_server = true  -> count = 1 -> aws_instance.lab[0] exists
#   enable_lab_server = false -> count = 0 -> nothing is created
resource "aws_instance" "lab" {
  count = var.enable_lab_server ? 1 : 0

  ami                    = data.aws_ami.al2023.id
  instance_type          = var.lab_instance_type
  subnet_id              = module.network.public_subnet_ids[0] # first subnet
  vpc_security_group_ids = [module.network.security_group_id]

  metadata_options {
    http_tokens = "required" # enforce IMDSv2, a security best practice
  }

  tags = { Name = "${local.name_prefix}-lab" }

  lifecycle {
    # "latest" AMI changes over time. Do not replace a running server just
    # because a newer image appeared.
    ignore_changes = [ami]

    # PRECONDITION: checked BEFORE the resource is created or changed.
    precondition {
      condition     = contains(["t3.micro", "t3.small"], var.lab_instance_type)
      error_message = "lab_instance_type must be t3.micro or t3.small for this lab."
    }
  }
}

# CHECK BLOCK: a continuous guardrail. If the assertion fails Terraform only
# WARNS and carries on. It never blocks a plan or apply.
check "workspace_matches_environment" {
  assert {
    condition     = terraform.workspace == var.environment || terraform.workspace == "default"
    error_message = "Workspace \"${terraform.workspace}\" does not match environment \"${var.environment}\"."
  }
}
```

### Add to root `outputs.tf`

```hcl
output "vpc_id" {
  value = module.network.vpc_id
}

# aws_instance.lab[*].id is a list with 0 or 1 ids. one() returns the single id,
# or null when the list is empty (server disabled). Plain [0] would error when count = 0.
output "lab_server_id" {
  value = one(aws_instance.lab[*].id)
}
```

```bash
terraform init
terraform apply -var-file=dev.tfvars
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| Plan with `-var="enable_lab_server=true"` | `aws_instance.lab[0]` will be created | count switched from 0 to 1. Destroy it afterwards to avoid cost |
| Add an HTTP rule to `ingress_rules` | Security group gets one more rule | The dynamic block regenerates, no copy and paste |
| `az_count = 5` | Validation error | Variable validation runs first |
| `lab_instance_type = "t3.large"` with the server on | Your precondition message | Precondition runs before the resource |
| `terraform workspace new test` then plan | A warning, plan still completes | `check` blocks only warn |

### Exam check

**Q1 (Dynamic blocks).** What is the purpose of a `dynamic` block?

- A) To create resources only during plan
- B) To generate repeated nested blocks inside a resource from a collection
- C) To replace modules
- D) To read environment variables

<details><summary>Answer</summary>

**B.** Some resources contain repeated nested blocks (security group `ingress` rules, ASG `tag` blocks). A `dynamic` block with `for_each` and `content` generates one block per element so you avoid copy and paste. Inside it, the iterator is named after the block (for example `ingress.value`).
</details>

**Q2 (create_before_destroy).** What does `create_before_destroy = true` change?

- A) The resource is never destroyed
- B) When replacement is needed, the new object is created first and the old one removed afterwards
- C) The resource is destroyed only at the end of the run
- D) The resource is created in a different region

<details><summary>Answer</summary>

**B.** The default order for replacement is destroy then create. This setting reverses it to reduce downtime or avoid dependency conflicts. It does not stop destruction (that is `prevent_destroy`).
</details>

**Q3 (ignore_changes).** Which is the effect of `lifecycle { ignore_changes = [ami] }`?

- A) Terraform deletes the `ami` argument
- B) Changes to `ami` made outside Terraform, or by a changed data source, do not trigger an update on later plans
- C) The resource cannot be created
- D) Terraform ignores the entire resource

<details><summary>Answer</summary>

**B.** Only the named attributes are ignored when comparing configuration with reality. The rest of the resource is still managed.
</details>

**Q4 (Custom conditions).** Which statement about custom conditions is correct?

- A) A `check` block stops the run when its assertion fails
- B) A `precondition` is evaluated before the resource is created or changed, and a failure stops the run
- C) A `postcondition` is evaluated before the resource is created
- D) Variable `validation` blocks run only during `apply`

<details><summary>Answer</summary>

**B.** `precondition` runs before, `postcondition` runs after, and both stop the run on failure. `check` only warns (A is wrong). Variable `validation` runs at plan time (D is wrong).
</details>

**Q5 (Count and null).** With `count = 0` on `aws_instance.lab`, which expression safely returns `null` instead of an error?

- A) `aws_instance.lab[0].id`
- B) `one(aws_instance.lab[*].id)`
- C) `aws_instance.lab.id`
- D) `aws_instance.lab["0"].id`

<details><summary>Answer</summary>

**B.** The splat `[*]` gives an empty list when count is 0, and `one()` turns a 0 or 1 item list into a single value (or `null`). Indexing `[0]` errors when no instance exists.
</details>

**Q6 (Validation).** Which feature validates the value of an input variable at plan time?

- A) A `validation` block inside the `variable` block
- B) A `check` block
- C) A provisioner
- D) A `moved` block

<details><summary>Answer</summary>

**A.** `validation` lives inside the variable and uses `condition` and `error_message`. `check` blocks are for general assertions and only warn.
</details>

### What you learned
- Dynamic blocks, and how to feed them. `count` as an on/off switch, `one()`, splat.
- `create_before_destroy`, `ignore_changes`. The four guardrails.
- `slice`, `cidrsubnet`, `contains`, `can`.

---

## M7: Remote state, locking, state commands, import, drift

**Goal:** move state off your laptop and learn to inspect and repair it.

### Concepts

- **Backend:** where state is stored (and how it is locked). Local by default. S3 is common.
- **Locking:** prevents two runs from changing state at the same time.
- **Partial backend configuration:** backend blocks cannot use variables, so values are supplied with `-backend-config`.
- **Drift:** real infrastructure changed outside Terraform.
- **Import:** bring an existing object under Terraform management.

### 1. Create the state bucket (once, with the AWS CLI)

```bash
BUCKET=<your-unique-name>-tfstate     # must be globally unique
REGION=eu-west-1

# Create the bucket
aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"

# Versioning: lets you recover an older state file if one is damaged
aws s3api put-bucket-versioning --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

# State is sensitive: block every kind of public access
aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Why not create it with Terraform? Terraform needs the bucket **before** it can store state in it (a chicken-and-egg problem).

### 2. Build: `backend.tf`

```hcl
# PARTIAL backend configuration: the empty braces say "use S3" and the real
# settings come from backend.hcl at init time. Backend blocks cannot use
# variables or locals because they are read before anything else is evaluated.
terraform {
  backend "s3" {}
}
```

### 3. Build: `backend.hcl.example` (copy to `backend.hcl`)

```hcl
bucket       = "REPLACE-with-your-state-bucket"
key          = "learning-lab/terraform.tfstate" # path of the state file inside the bucket
region       = "eu-west-1"
encrypt      = true                              # encrypt the state file at rest
use_lockfile = true                              # native S3 locking. Older setups use: dynamodb_table = "tf-locks"
```

### 4. Migrate

```bash
cp backend.hcl.example backend.hcl      # edit the bucket name
terraform init -backend-config=backend.hcl -migrate-state    # answer: yes (copies local state to S3)
aws s3 ls "s3://$BUCKET/" --recursive
terraform plan -var-file=dev.tfvars     # should say: no changes
```

### Labs

| Task | Command | What you learn |
|---|---|---|
| Inspect | `terraform state list`, `terraform state show 'module.team["alpha"].aws_s3_bucket.this'` | State maps addresses to real IDs |
| Raw state | `terraform state pull \| head -50` | State is JSON and may contain secrets |
| Locking | Run `terraform apply` in two terminals at once | The second waits or fails with a lock message. `terraform force-unlock <ID>` clears a stuck lock |
| Drift | `aws s3api put-bucket-tagging --bucket <bucket> --tagging 'TagSet=[{Key=Hacked,Value=yes}]'` then `terraform plan` | Plan detects the change and proposes reverting it |
| Refresh only | `terraform plan -refresh-only` | Update state to match reality without changing infrastructure |
| Stop managing | `terraform state rm 'module.team["beta"].aws_iam_user_group_membership.member["yaw"]'` then `plan` | Removed from state, NOT deleted in AWS. Plan wants to create it again |
| Recover | View object versions of the state file in S3 | Why bucket versioning matters |

### Import lab

```bash
# 1. Create a bucket by hand (a "legacy" resource unknown to Terraform)
aws s3api create-bucket --bucket <unique-name>-legacy --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1
```

Add to `main.tf`:

```hcl
# You must still WRITE the resource block, so the code matches the real object.
resource "aws_s3_bucket" "legacy" {
  bucket = "<unique-name>-legacy"
}

# import block (Terraform 1.5+): "attach the real object with this ID to that address".
# Plan shows "will be imported". Apply writes it into state.
import {
  to = aws_s3_bucket.legacy
  id = "<unique-name>-legacy"
}
```

```bash
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

Afterwards remove the `legacy` resource and `import` block, apply, and confirm the bucket is deleted.

### Exam check

**Q1 (Backends).** Why can the `backend` block not use `var.bucket`?

- A) Variables are not supported in Terraform
- B) The backend is initialized before variables are evaluated, so it only accepts literal values
- C) Backends only support integers
- D) Variables are only allowed in modules

<details><summary>Answer</summary>

**B.** The backend is needed at `init`, before variables exist. Supply dynamic values with `terraform init -backend-config=file.hcl` (partial configuration) or `-backend-config="key=value"`.
</details>

**Q2 (state rm).** What happens when you run `terraform state rm aws_instance.web`?

- A) The instance is destroyed in AWS
- B) Terraform stops tracking the instance, but it keeps running
- C) The resource block is deleted from the configuration
- D) The instance is replaced

<details><summary>Answer</summary>

**B.** `state rm` only removes the entry from state. The real object stays. If the configuration still declares it, the next plan proposes creating it again. To delete the real object use `terraform destroy`.
</details>

**Q3 (Locks).** A previous run crashed and left the state locked. Which command releases the lock?

- A) `terraform refresh`
- B) `terraform force-unlock LOCK_ID`
- C) `terraform state unlock`
- D) `terraform init -upgrade`

<details><summary>Answer</summary>

**B.** `force-unlock` removes a stuck lock. Use it carefully, only when you are sure no other run is active.
</details>

**Q4 (Changing backends).** You change the backend configuration and run `terraform init`. Terraform asks what to do with existing state. Which option copies the existing state to the new backend?

- A) `-reconfigure`
- B) `-migrate-state`
- C) `-upgrade`
- D) `-lock=false`

<details><summary>Answer</summary>

**B.** `-migrate-state` copies state to the new backend. `-reconfigure` ignores the old configuration without copying. `-upgrade` is for provider versions.
</details>

**Q5 (Drift).** Someone edits a tag in the cloud console on a managed resource. Which command updates **only the state** to match reality, without changing infrastructure?

- A) `terraform apply`
- B) `terraform apply -refresh-only`
- C) `terraform destroy`
- D) `terraform fmt`

<details><summary>Answer</summary>

**B.** `-refresh-only` syncs state with reality. A normal `apply` would instead change the real resource back to match the configuration. The standalone `terraform refresh` command is deprecated in favor of `-refresh-only`.
</details>

**Q6 (Import).** You created a bucket manually and want Terraform to manage it. Which approach is correct in Terraform 1.5 and later?

- A) Write only an `import` block, no resource block is needed
- B) Write the `resource` block and an `import` block with the bucket ID, then plan and apply
- C) Run `terraform state rm` on the bucket
- D) Run `terraform taint` on the bucket

<details><summary>Answer</summary>

**B.** `import` binds an existing object to a resource address in state. You still provide matching resource configuration (or generate it with `-generate-config-out`). `state rm` and `taint` do the opposite or something unrelated.
</details>

### What you learned
- Backends, partial configuration, `-migrate-state`. Remote state needs versioning, encryption and locking.
- State commands, drift, `-refresh-only`, and `import`. State is sensitive.

---

## M8: Workspaces and environments

**Goal:** run the same code as `dev` and `prod` with separate state.

### Concepts

- A **CLI workspace** is another state file for the **same** configuration and backend.
- `default` always exists and cannot be deleted. `terraform.workspace` gives the current name in code.
- With the S3 backend, non-default workspaces are stored at `env:/<workspace>/<key>`.
- Workspaces do **not** isolate credentials or code. **HCP Terraform workspaces** are a different, richer concept.

First, remove what exists in the default workspace (names would otherwise collide):

```bash
terraform destroy -var-file=dev.tfvars
```

### Build: `prod.tfvars`

```hcl
environment = "prod"

teams = {
  alpha = { members = ["ama", "kofi"], retention_days = 365 }
  beta  = { members = ["yaw"],         retention_days = 365 }
  gamma = { members = ["efua"],        retention_days = 365 }
}

enable_lab_server = false # no lab server in prod
```

### Run

```bash
terraform workspace list
terraform workspace new dev                  # creates AND switches
terraform apply -var-file=dev.tfvars

terraform workspace new prod
terraform apply -var-file=prod.tfvars

terraform workspace show                     # which one am I in?
aws s3 ls "s3://$BUCKET/" --recursive        # look at the keys
```

### Hands-on checks

| Try this | You should see | Why |
|---|---|---|
| List the state bucket keys | `env:/dev/...` and `env:/prod/...` | Per-workspace state files |
| In workspace `dev`, `plan -var-file=prod.tfvars` | Check warning about mismatch | The guardrail catches the wrong pairing |
| `terraform workspace delete default` | Error | The default workspace cannot be deleted |
| Why do dev and prod not clash? | Names include the environment | `local.name_prefix` is in every name |

### Exam check

**Q1 (State location).** With the S3 backend and key `app/terraform.tfstate`, where is the state for workspace `prod` stored?

- A) `app/terraform.tfstate`
- B) `env:/prod/app/terraform.tfstate`
- C) `prod/app/terraform.tfstate.backup`
- D) In a local file named `prod.tfstate`

<details><summary>Answer</summary>

**B.** Non-default workspaces are stored under `env:/<workspace>/<key>`. The `default` workspace uses the plain key (A).
</details>

**Q2 (terraform.workspace).** What does `terraform.workspace` return?

- A) The name of the AWS region
- B) The name of the currently selected workspace
- C) The path of the working directory
- D) The name of the backend

<details><summary>Answer</summary>

**B.** It is a built-in value often used in names and tags.
</details>

**Q3 (Workspace rules).** Which statements are correct? Choose two.

- A) The `default` workspace can be deleted
- B) You cannot delete the workspace you are currently in
- C) Each CLI workspace uses a separate state file for the same configuration
- D) CLI workspaces provide separate credentials for each environment

<details><summary>Answer</summary>

**B and C.** `default` can never be deleted (A is wrong) and CLI workspaces share the same code and credentials (D is wrong). Destroy a workspace's resources before deleting it, or they become orphaned.
</details>

**Q4 (CLI vs HCP workspaces).** How does an HCP Terraform workspace differ from a CLI workspace?

- A) They are identical
- B) An HCP workspace is a full container with its own variables, state, and run history, while a CLI workspace is only a separate state
- C) HCP workspaces cannot store state
- D) CLI workspaces include policy checks

<details><summary>Answer</summary>

**B.** The names match but the concepts differ. HCP workspaces hold configuration links, variables, state versions, permissions, and runs.
</details>

**Q5 (Command).** Which command prints the name of the current workspace?

- A) `terraform workspace show`
- B) `terraform workspace current`
- C) `terraform show workspace`
- D) `terraform state workspace`

<details><summary>Answer</summary>

**A.** The subcommands are `new`, `select`, `list`, `show` and `delete`.
</details>

### What you learned
- CLI workspaces and how state is stored per workspace. Environment-specific tfvars and guardrails.

---

## M9: Provisioners, secrets, replace, debugging

**Goal:** learn the last-resort tools and what Terraform does with secrets.

### Concepts

- **Provisioner:** runs a script as part of creating or destroying a resource. HashiCorp calls it a **last resort**.
- **`terraform_data`:** a built-in resource (no provider) used to hold triggers and provisioners. It replaces `null_resource`.
- **`-replace=ADDRESS`:** force one resource to be recreated. It replaces `terraform taint`.
- **Sensitive values:** hidden in CLI output, **still stored in state in plain text**.
- **`TF_LOG`:** controls log verbosity (`TRACE` is the most detailed).

### Add to `variables.tf`

```hcl
variable "platform_api_key" {
  description = "Example secret. Supply it with TF_VAR_platform_api_key"
  type        = string
  sensitive   = true # hides the value in plan/apply output (it is STILL in state)

  validation {
    condition     = length(var.platform_api_key) >= 8
    error_message = "platform_api_key must be at least 8 characters."
  }
}
```

### Add to `main.tf`

```hcl
# A secret stored as an encrypted SSM parameter.
# The value comes from a sensitive variable, so CLI output shows (sensitive value).
resource "aws_ssm_parameter" "api_key" {
  name  = "/${local.name_prefix}/platform_api_key"
  type  = "SecureString"
  value = var.platform_api_key
}

# terraform_data holds the provisioner. It needs no cloud account.
resource "terraform_data" "deploy_log" {
  # Re-run the provisioner whenever this value changes
  # (here: whenever the set of bucket names changes).
  triggers_replace = [join(",", [for t in module.team : t.bucket_name])]

  # local-exec runs on YOUR machine (where Terraform runs), only when this
  # resource is CREATED (or destroyed, with when = destroy). It does NOT run on
  # every apply, and Terraform does not track what the command did.
  provisioner "local-exec" {
    command = "echo \"$(date -u) ${local.name_prefix}: ${join(" ", [for t in module.team : t.bucket_name])}\" >> deploy-${var.environment}.log"
  }
}
```

### Add to `outputs.tf`

```hcl
output "api_key_length" {
  value     = length(var.platform_api_key)
  sensitive = true # REQUIRED because the value derives from a sensitive variable
}
```

### Run

```bash
export TF_VAR_platform_api_key='Sup3rSecret-123'   # env var, so no secret is written to a file
terraform apply -var-file=dev.tfvars               # in the dev workspace
cat deploy-dev.log
terraform output                                   # api_key_length shows <sensitive>
terraform output -raw api_key_length               # reveals it
```

### Labs

| Task | Command | What you learn |
|---|---|---|
| Secrets in state | `terraform state pull \| grep -i Sup3rSecret` | The plain text secret is in state, even though plan hid it |
| Force replacement | `terraform apply -var-file=dev.tfvars -replace='terraform_data.deploy_log'` | One resource is recreated and the log gets a second line |
| Provisioners run once | `terraform apply` again with no change | The log does not grow |
| Debugging | `TF_LOG=DEBUG TF_LOG_PATH=./tf-debug.log terraform plan -var-file=dev.tfvars` | Detailed log written to a file |

### Exam check

**Q1 (Sensitive and state).** A variable is marked `sensitive = true`. Which statement is correct?

- A) The value is encrypted in the state file
- B) The value is hidden in CLI output but is still stored in state in plain text
- C) The value cannot be used in resources
- D) The value is removed from state after `apply`

<details><summary>Answer</summary>

**B.** `sensitive` only redacts CLI output. Protect state with an encrypted remote backend, strict access control and versioning, and never commit it to Git.
</details>

**Q2 (Provisioner failure).** A `local-exec` provisioner exits with a non-zero status and `on_failure` is not set. What happens?

- A) Terraform ignores the failure
- B) The apply fails and the resource is marked tainted
- C) The resource is destroyed immediately without a plan
- D) Terraform retries forever

<details><summary>Answer</summary>

**B.** The default is `on_failure = fail`: the apply fails and the resource is tainted (recreated on the next apply). `on_failure = continue` ignores the error.
</details>

**Q3 (-replace).** Which command forces `aws_instance.web` to be recreated on the next apply, replacing the older `terraform taint`?

- A) `terraform apply -target=aws_instance.web`
- B) `terraform apply -replace=aws_instance.web`
- C) `terraform state rm aws_instance.web`
- D) `terraform refresh aws_instance.web`

<details><summary>Answer</summary>

**B.** `-replace=ADDRESS` marks it for destruction and recreation. `-target` only limits scope.
</details>

**Q4 (Logging).** Which setting gives the **most verbose** Terraform logging?

- A) `TF_LOG=INFO`
- B) `TF_LOG=DEBUG`
- C) `TF_LOG=TRACE`
- D) `TF_LOG=ERROR`

<details><summary>Answer</summary>

**C.** Levels from most to least verbose: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`. Add `TF_LOG_PATH` to write to a file.
</details>

**Q5 (Provisioner scope).** Where does a `local-exec` provisioner run?

- A) On the newly created resource
- B) On the machine running Terraform
- C) In HCP Terraform only
- D) In the cloud provider's control plane

<details><summary>Answer</summary>

**B.** `local-exec` runs locally. `remote-exec` runs on the created resource (it needs a `connection` block). Provisioners run only at create or destroy time and are a last resort: prefer `user_data`, prebuilt images, or configuration management.
</details>

**Q6 (Supplying secrets).** Which is the most appropriate way to give a password to a root module without writing it into a file in the repository?

- A) Put it in `terraform.tfvars` and commit it
- B) Set an environment variable named `TF_VAR_<variable_name>`
- C) Hardcode it as a variable `default`
- D) Put it in a `local` value

<details><summary>Answer</summary>

**B.** `TF_VAR_` variables avoid writing the secret in code. Even better, design so the secret never enters Terraform (for example a managed password feature, or reading it from a secrets manager at runtime).
</details>

### What you learned
- `terraform_data`, `local-exec`, `triggers_replace`, why provisioners are a last resort.
- `-replace`. **Sensitive values are hidden, not protected, in state.** `TF_VAR_` and `TF_LOG`.

---

## M10: Registry modules, HCP Terraform, final review

**Goal:** use someone else's module and see how teams run Terraform at scale.

### Registry module (try it in a throwaway workspace)

```bash
terraform workspace new sandbox
```

Replace your network module call with the public VPC module:

```hcl
module "network" {
  source  = "terraform-aws-modules/vpc/aws" # <NAMESPACE>/<NAME>/<PROVIDER> on the public Registry
  version = "~> 5.0"                        # ALWAYS pin registry module versions

  name = local.name_prefix
  cidr = var.vpc_cidr
  azs  = local.azs

  # for expression building a list of subnet CIDRs from the AZ list
  public_subnets = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 8, i)]

  tags = local.common_tags
}
```

Adapt the references (the public module's outputs are `vpc_id` and `public_subnets`), run `terraform init`, and `plan`. Compare how much code you wrote yourself against what the module gives you. Delete the sandbox workspace afterwards.

### HCP Terraform (conceptual walkthrough, free tier)

1. Create an organization and a workspace.
2. Connect a Git repo (VCS-driven) or use the CLI-driven workflow:

```hcl
terraform {
  cloud {
    organization = "my-org"       # your HCP Terraform organization
    workspaces {
      name = "learning-lab-dev"   # the HCP workspace this configuration uses
    }
  }
}
```

3. Run `terraform login` to store an API token.
4. Add variables in the UI and mark secrets **Sensitive**.
5. Look at remote runs, state versions, policy checks (Sentinel, OPA), the private registry, and team permissions.

A `cloud` block and a `backend` block cannot both be used.

### Exam check

**Q1 (Registry addresses).** Which `source` is a valid public Terraform Registry module address?

- A) `registry.terraform.io/vpc`
- B) `terraform-aws-modules/vpc/aws`
- C) `github.com/vpc`
- D) `module://vpc/aws`

<details><summary>Answer</summary>

**B.** Registry modules use `<NAMESPACE>/<NAME>/<PROVIDER>`. Only registry modules support the `version` argument.
</details>

**Q2 (Pinning).** Why should you pin the `version` of a registry module?

- A) The registry requires it to download
- B) Without pinning, a later `init` can pull a newer version that changes behavior
- C) Pinning makes plans faster
- D) Pinned modules ignore variables

<details><summary>Answer</summary>

**B.** Pinning keeps results repeatable. Use constraints such as `~> 5.0` just like providers.
</details>

**Q3 (Connecting to HCP Terraform).** Which block connects a configuration to HCP Terraform?

- A) `backend "hcp" {}`
- B) A `cloud` block inside the `terraform` block
- C) `provider "hcp" {}`
- D) `workspace {}` at the top level

<details><summary>Answer</summary>

**B.** Use `terraform { cloud { ... } }` and authenticate with `terraform login`. It cannot be combined with a `backend` block.
</details>

**Q4 (HCP features, choose two).** Which are capabilities of HCP Terraform?

- A) Remote state storage with locking and history
- B) Replacing provider plugins with built-in ones
- C) Policy as code enforcement with Sentinel or OPA
- D) Running Terraform with no configuration files

<details><summary>Answer</summary>

**A and C.** HCP Terraform also provides remote runs, a private registry, team access control, cost estimation, and drift detection. It does not replace providers and still needs configuration.
</details>

### Review checklist

Explain each in your own words with an example from this lab:

- [ ] Declarative vs imperative
- [ ] What `init`, `plan`, `apply`, `destroy` do
- [ ] Implicit vs explicit dependency, and where you used each
- [ ] `count` vs `for_each` and the index-shift trap
- [ ] `variables.tf` vs `terraform.tfvars` and the precedence order
- [ ] Locals vs variables
- [ ] Child module inputs and outputs, and why a parent cannot reach inside
- [ ] `moved` blocks vs `state mv` vs `import`
- [ ] Remote backends, locking, why state is sensitive
- [ ] Workspaces and their limits
- [ ] Lifecycle arguments and the four guardrails
- [ ] Why provisioners are a last resort
- [ ] Provider version constraints and the lock file

---

# 8. Final self-test

Answer without looking, then check.

1. You rename `aws_s3_bucket.a` to `aws_s3_bucket.b` with no other change. What does `plan` show, and what are two ways to avoid it?
2. A teammate removes the first name from a list used with `count`. What goes wrong?
3. What does `~> 5.60` allow? What about `~> 5.60.1`?
4. Where is the state for workspace `prod` stored with the S3 backend?
5. A variable is `sensitive = true`. Is it encrypted in state?
6. Which of these stops a run: variable validation, precondition, postcondition, check block?
7. How does a parent module read a value created inside a child?
8. `terraform state rm` vs `terraform destroy`: what is the difference?
9. When must you use `depends_on`?
10. How do you deploy to two regions from one configuration?
11. Which should be committed: `terraform.tfstate`, `.terraform.lock.hcl`, `*.tfplan`?
12. `terraform.tfvars` vs `dev.tfvars`: which is auto-loaded?

<details><summary>Answers</summary>

1. Destroy and create. Use a `moved` block or `terraform state mv`.
2. Remaining items shift index, so Terraform replaces or changes items that did not need to change. Use `for_each`.
3. `>= 5.60, < 6.0`. And `>= 5.60.1, < 5.61.0`.
4. `env:/prod/<key>` in the backend bucket.
5. No. It is only hidden from CLI output. State holds it in plain text.
6. Validation, precondition and postcondition stop the run. A check block only warns.
7. Through an `output` of the child: `module.name.output_name`.
8. `state rm` only forgets it (the real object stays). `destroy` deletes the real object.
9. When a dependency exists but is not visible as a reference.
10. A second `provider` block with an `alias`, then `provider = aws.alias` on the resource (or `providers = {}` on a module).
11. `.terraform.lock.hcl`. Never the state or plan files.
12. `terraform.tfvars`. `dev.tfvars` needs `-var-file`.
</details>

---

# 9. Exam check score sheet

Tick each question you answered correctly **before** reading the explanation. Any area under 70% needs a second pass.

| Milestone | Exam check questions | Topic areas | Correct |
|---|---|---|---|
| M0 | Q1 to Q4 | IaC, plan symbols, state, implicit dependency | ___ / 4 |
| M1 | Q1 to Q5 | tfvars, precedence, required variables, locals, outputs | ___ / 5 |
| M2 | Q1 to Q5 | count, for_each, for expressions, functions | ___ / 5 |
| M3 | Q1 to Q5 | version constraints, lock file, data sources, dependencies, provider config | ___ / 5 |
| M4 | Q1 to Q5 | module outputs, addresses, moved, init, module sources | ___ / 5 |
| M5 | Q1 to Q4 | depends_on, flatten, jsonencode, data sources, addresses | ___ / 4 |
| M6 | Q1 to Q6 | dynamic blocks, lifecycle, custom conditions, count and null, validation | ___ / 6 |
| M7 | Q1 to Q6 | backends, state rm, locks, migration, drift, import | ___ / 6 |
| M8 | Q1 to Q5 | workspace state paths, terraform.workspace, workspace rules, HCP vs CLI | ___ / 5 |
| M9 | Q1 to Q6 | sensitive data, provisioners, replace, logging, secrets | ___ / 6 |
| M10 | Q1 to Q4 | registry modules, pinning, HCP Terraform | ___ / 4 |
| **Total** | | | ___ / 55 |

---

# 10. Extension challenges

1. Convert the `count`-based lab server toggle to a `for_each` over a map of servers (`{ jump = "t3.micro" }`) and see how addresses change.
2. Add a `removed` block to stop managing a resource without destroying it.
3. Add a CI workflow that runs `terraform fmt -check -recursive` and `terraform validate` on every pull request.
4. Add a second AWS provider with an `alias` for another region and create a backup bucket there. Pass it into the team module with `providers = {}` and `configuration_aliases`.
5. Write a `variable` with `optional()` attributes in an object type (for example an optional `description` per team).
6. Add a `precondition` that fails when a team has no members.
7. Publish your `team` module to a Git repository and call it with `source = "git::https://...?ref=v1.0.0"`.

---

# 11. Cleanup

Destroy in this order so nothing is left behind:

```bash
cd 02-platform
terraform workspace select prod
terraform destroy -var-file=prod.tfvars

terraform workspace select dev
terraform destroy -var-file=dev.tfvars

terraform workspace select default
terraform workspace delete prod
terraform workspace delete dev
terraform workspace delete sandbox   # if you created it
```

Then delete the state bucket (empty all object **versions** first):

```bash
aws s3api delete-bucket --bucket "$BUCKET" --region eu-west-1
```

If the delete fails because of versions, empty the bucket in the AWS console and retry. Finally delete `deploy-*.log`, `tf-debug.log`, and any `*.tfplan` files. In `01-local-warmup`, run `terraform destroy` and delete the `out/` folder.

---

# 12. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `Error acquiring the state lock` | Another run is active or one crashed. Wait, or `terraform force-unlock <ID>` |
| `Backend initialization required` | Backend settings changed. Run `terraform init -reconfigure` (or `-migrate-state`) |
| `Unsupported argument: use_lockfile` | Terraform is too old. Upgrade, or use `dynamodb_table` |
| `BucketAlreadyExists` | S3 names are global. Choose a more unique prefix |
| `Module not installed` | You added a module. Run `terraform init` |
| Plan wants to destroy and recreate after a refactor | Missing `moved` block, or old and new addresses do not match exactly |
| `Invalid for_each argument ... known only after apply` | Keys depend on something not created yet. Use keys known at plan time |
| `Inconsistent dependency lock file` | Provider constraints changed. Run `terraform init -upgrade` |
| Variable prompts every run | The variable has no default. Provide it in `terraform.tfvars` or with `-var-file` |
| `AccessDenied` | Your IAM identity lacks a permission. The error names the action |
| Warning about workspace | You are in the wrong workspace for the tfvars file |
| `local-exec` fails on Windows | Use WSL or Git Bash, or set `interpreter = ["PowerShell", "-Command"]` on the provisioner |

---

### A final tip

When something surprises you, resist the urge to fix it immediately. Ask first: **what did Terraform think the current state was, what did my code say, and what did reality look like?** Almost every Terraform puzzle is a mismatch between those three things.
