# Terraform on AWS — A Progressive Learning Guide

This guide teaches Terraform syntax and file structure using AWS as the cloud provider.
It's built in **levels** — start at Level 0 even for the tiniest project, and only move
up a level when you actually need what it introduces. Every level is a complete,
runnable mini-project on its own.

> **Rule of thumb:** don't add a file or a feature until this guide tells you why you need it.
> A single `main.tf` is a perfectly valid Terraform project.

---

## Table of Contents

- [Level 0 — Prerequisites & Setup](#level-0--prerequisites--setup)
- [Level 1 — One File, One Resource](#level-1--one-file-one-resource)
- [Level 2 — Introducing Variables](#level-2--introducing-variables)
- [Level 3 — terraform.tfvars (feeding values in)](#level-3--terraformtfvars-feeding-values-in)
- [Level 4 — Outputs](#level-4--outputs)
- [Level 5 — Splitting Files & Locals](#level-5--splitting-files--locals)
- [Level 6 — Multiple Resources & Dependencies](#level-6--multiple-resources--dependencies)
- [Level 7 — Data Sources](#level-7--data-sources)
- [Level 8 — Provisioners & Lifecycle (use sparingly)](#level-8--provisioners--lifecycle-use-sparingly)
- [Level 9 — Modules](#level-9--modules)
- [Level 10 — Remote State & Backends](#level-10--remote-state--backends)
- [Level 11 — Workspaces & Environments](#level-11--workspaces--environments)
- [Reference — Full File Glossary](#reference--full-file-glossary)
- [Reference — Terraform CLI Cheatsheet](#reference--terraform-cli-cheatsheet)
- [Reference — Best Practices Checklist](#reference--best-practices-checklist)

---

## Level 0 — Prerequisites & Setup

**Goal:** get Terraform installed and AWS credentials working before writing any `.tf` code.

1. Install Terraform: https://developer.hashicorp.com/terraform/install
2. Install and configure the AWS CLI:
   ```bash
   aws configure
   ```
   This creates `~/.aws/credentials` and `~/.aws/config`, which Terraform's AWS provider
   will use automatically — you do **not** hardcode keys in `.tf` files.
3. Verify:
   ```bash
   terraform -version
   aws sts get-caller-identity
   ```

**Folder for this whole guide:**
```
terraform-aws-learning/
```
Create one subfolder per level as you go (`level-1/`, `level-2/`, ...), or just evolve
a single folder in place — either works for learning.

---

## Level 1 — One File, One Resource

**Goal:** understand the absolute minimum Terraform needs — a provider and one resource.
No variables, no outputs, nothing fancy. This is the smallest useful Terraform project.

**Files:**
```
level-1/
└── main.tf
```

**`main.tf`**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_s3_bucket" "learning_bucket" {
  bucket = "sammy-tf-learning-bucket-0001" # must be globally unique
}
```

**What each block means:**
| Block | Purpose |
|---|---|
| `terraform {}` | Meta-settings for Terraform itself: which providers/versions this project needs |
| `provider "aws" {}` | Configures *which* cloud and *where* (region) resources get created |
| `resource "<TYPE>" "<LOCAL_NAME>" {}` | Declares an actual AWS object to create. `TYPE` is fixed by AWS provider docs (e.g. `aws_s3_bucket`); `LOCAL_NAME` is yours to choose, used only inside Terraform to refer to it |

**Run it:**
```bash
terraform init      # downloads the aws provider plugin
terraform plan       # shows what WILL happen, changes nothing
terraform apply      # actually creates the resource
terraform destroy    # tears it down again
```

---

## Level 2 — Introducing Variables

**Goal:** stop hardcoding values like `region` and `bucket name` directly in `main.tf`.

**Files:**
```
level-2/
├── main.tf
└── variables.tf
```

**`variables.tf`**
```hcl
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}
```

**`main.tf`**
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "learning_bucket" {
  bucket = var.bucket_name
}
```

**Key idea:** `variable "X" {}` *declares* an input. You *use* it elsewhere with `var.X`.
Variables can have a `type`, a `description` (good habit — write these always), and an
optional `default`. `bucket_name` has no default, so Terraform will now **prompt you**
for it at `terraform apply` — which leads directly to Level 3.

---

## Level 3 — terraform.tfvars (feeding values in)

**Goal:** stop being prompted interactively — supply variable values from a file instead.

**Files:**
```
level-3/
├── main.tf
├── variables.tf
└── terraform.tfvars
```

**`terraform.tfvars`**
```hcl
aws_region  = "eu-west-1"
bucket_name = "sammy-tf-learning-bucket-0002"
```

Terraform **automatically loads** a file literally named `terraform.tfvars` (or any
`*.auto.tfvars`) — no flag needed. `main.tf` and `variables.tf` stay exactly as in Level 2.

**Other ways to pass variables (good to know, not required to use all of them):**
```bash
# 1. CLI flag
terraform apply -var="bucket_name=my-bucket-123"

# 2. A differently-named tfvars file (must be pointed to explicitly)
terraform apply -var-file="prod.tfvars"

# 3. Environment variable
export TF_VAR_bucket_name="my-bucket-123"
terraform apply
```

**Precedence (highest wins):** CLI `-var` > `*.auto.tfvars` > `terraform.tfvars` > environment variables > `default` in `variables.tf`.

> ⚠️ Never commit `terraform.tfvars` if it contains secrets. Add it to `.gitignore`
> and share an example instead — see [`terraform.tfvars.example`](#reference--full-file-glossary).

---

## Level 4 — Outputs

**Goal:** print useful information back after `apply` (e.g. a bucket's ARN) instead of
digging through the AWS console.

**Files:**
```
level-4/
├── main.tf
├── variables.tf
├── terraform.tfvars
└── outputs.tf
```

**`outputs.tf`**
```hcl
output "bucket_id" {
  description = "The name of the created bucket"
  value       = aws_s3_bucket.learning_bucket.id
}

output "bucket_arn" {
  description = "ARN of the created bucket"
  value       = aws_s3_bucket.learning_bucket.arn
}
```

After `terraform apply`, these print automatically. You can also fetch them anytime with:
```bash
terraform output
terraform output bucket_arn   # single value, useful for scripting
```

**Key idea:** `resource_type.local_name.attribute` is how you read *any* value out of a
resource you created — inside outputs, inside other resources, anywhere.

---

## Level 5 — Splitting Files & Locals

**Goal:** as a project grows past ~1 resource, split by concern and stop repeating
computed values.

**Files:**
```
level-5/
├── providers.tf     # terraform{} + provider{} blocks
├── variables.tf      # all variable declarations
├── locals.tf         # computed / derived values
├── main.tf            # actual resources
├── outputs.tf
└── terraform.tfvars
```

**`locals.tf`**
```hcl
locals {
  environment  = "learning"
  project_name = "tf-aws-guide"
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
  }
}
```

**`main.tf`**
```hcl
resource "aws_s3_bucket" "learning_bucket" {
  bucket = var.bucket_name
  tags   = local.common_tags
}
```

**`variable` vs `local` — the distinction that trips people up:**
| | Set from outside? | Purpose |
|---|---|---|
| `variable` | Yes (tfvars, CLI, env) | An **input** to the configuration |
| `local` | No — computed inside `.tf` | A **derived/reused value**, avoids repetition |

There's no required filename for any of this — `providers.tf`, `locals.tf`, `main.tf`
are pure convention. Terraform actually reads **every** `.tf` file in the folder and
merges them into one configuration. Splitting files is for *humans*, not Terraform.

---

## Level 6 — Multiple Resources & Dependencies

**Goal:** create resources that depend on each other, and see how Terraform figures out
the order automatically.

**`main.tf`**
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = merge(local.common_tags, { Name = "learning-vpc" })
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id       # <- implicit dependency
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags                    = merge(local.common_tags, { Name = "learning-public-subnet" })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}
```

**Key idea:** because `aws_subnet.public` references `aws_vpc.main.id`, Terraform builds
a dependency graph automatically and creates the VPC first — you never manually order
resources. For rare cases with no direct reference, force ordering with:
```hcl
resource "aws_subnet" "public" {
  # ...
  depends_on = [aws_internet_gateway.igw]
}
```
Use `depends_on` only when there's genuinely no attribute reference to create the link.

---

## Level 7 — Data Sources

**Goal:** read information about existing AWS resources (things you didn't create with
this Terraform config) instead of hardcoding IDs.

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  tags          = local.common_tags
}
```

**Key idea:** `data "<TYPE>" "<NAME>" {}` looks something up; `resource "<TYPE>" "<NAME>" {}`
creates something. Reference a data source with `data.TYPE.NAME.attribute`.

---

## Level 8 — Provisioners & Lifecycle (use sparingly)

**Goal:** know these exist, and know why the Terraform community avoids them when possible.

```hcl
resource "aws_instance" "example" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
    ignore_changes        = [tags]
  }
}
```
`lifecycle {}` changes *how* Terraform manages a resource's create/update/destroy
behavior — genuinely useful. `provisioner "remote-exec" {}` / `local-exec {}` run scripts
on create/destroy, but are considered a last resort — prefer AMIs baked with Packer,
user-data, or config management tools instead. Mentioned here so you recognize it in
other people's code.

---

## Level 9 — Modules

**Goal:** package a reusable group of resources (e.g. "a standard VPC") so you're not
copy-pasting the same blocks across projects.

**Files:**
```
level-9/
├── main.tf                  # root module — calls the child module
├── variables.tf
├── outputs.tf
└── modules/
    └── s3-bucket/
        ├── main.tf            # child module resources
        ├── variables.tf        # child module's own inputs
        └── outputs.tf           # child module's own outputs
```

**`modules/s3-bucket/main.tf`**
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}
```

**`modules/s3-bucket/variables.tf`**
```hcl
variable "bucket_name" { type = string }
variable "tags"        { type = map(string), default = {} }
```

**`modules/s3-bucket/outputs.tf`**
```hcl
output "arn" { value = aws_s3_bucket.this.arn }
```

**Root `main.tf` — calling the module:**
```hcl
module "learning_bucket" {
  source      = "./modules/s3-bucket"
  bucket_name = var.bucket_name
  tags        = local.common_tags
}

output "bucket_arn_from_module" {
  value = module.learning_bucket.arn
}
```

**Key idea:** a module is just a folder of `.tf` files. `source = "./modules/s3-bucket"`
points at it. Every module has its own `variables.tf` (its "API in") and `outputs.tf`
(its "API out"). Modules can also come from the public Terraform Registry
(`source = "terraform-aws-modules/vpc/aws"`) — you'll recognize the same pattern.

---

## Level 10 — Remote State & Backends

**Goal:** stop storing `terraform.tfstate` only on your laptop — store it somewhere
shared and lockable, which matters the moment more than one person touches the project.

**`backend.tf`**
```hcl
terraform {
  backend "s3" {
    bucket         = "sammy-tf-state-bucket"
    key            = "learning/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-locks"   # prevents two applies running at once
    encrypt        = true
  }
}
```
This state bucket and lock table have to exist *before* you point a config at them
(usually created in their own tiny "bootstrap" Terraform project, ironically applied
with local state once).

```bash
terraform init -reconfigure   # re-initializes against the new backend
```

**Key idea:** `terraform.tfstate` is Terraform's record of what it thinks exists in AWS.
Local state = fine for solo learning. Remote state = required for teams.

---

## Level 11 — Workspaces & Environments

**Goal:** manage `dev` / `staging` / `prod` without duplicating your entire codebase.

```bash
terraform workspace new dev
terraform workspace new prod
terraform workspace select dev
terraform workspace show
```

```hcl
resource "aws_s3_bucket" "learning_bucket" {
  bucket = "${var.bucket_name}-${terraform.workspace}"
}
```

**Alternative (often preferred at scale):** separate `.tfvars` per environment instead
of workspaces:
```bash
terraform apply -var-file="envs/dev.tfvars"
terraform apply -var-file="envs/prod.tfvars"
```
Workspaces share the same backend config and are simplest for learning; separate
directories/tfvars-per-env give more isolation and are common in real teams. Both are
worth knowing.

---

## Reference — Full File Glossary

| File | Required? | Purpose |
|---|---|---|
| `main.tf` | No (by convention only) | Where resources typically live |
| `providers.tf` | No | `terraform{}` + `provider{}` blocks, split out once the project grows |
| `variables.tf` | No | Declares inputs (`variable` blocks) |
| `terraform.tfvars` | No | Supplies values for declared variables; auto-loaded |
| `*.auto.tfvars` | No | Same as above, also auto-loaded, useful for multiple files |
| `terraform.tfvars.example` | No | A committed template showing what to put in your own `.tfvars` (without secrets) |
| `outputs.tf` | No | Declares `output` blocks — values shown after apply |
| `locals.tf` | No | Declares `local` blocks — computed/derived values |
| `backend.tf` | No | Where state is stored (S3, Terraform Cloud, etc.) |
| `versions.tf` | No | Sometimes used to isolate the `required_version` / `required_providers` block |
| `data.tf` | No | Sometimes used to isolate `data` source blocks |
| `.terraform/` | Auto-generated | Downloaded provider plugins — never edit/commit |
| `.terraform.lock.hcl` | Auto-generated | Locks exact provider versions — **do commit this one** |
| `terraform.tfstate` | Auto-generated | Terraform's record of real-world resource state — sensitive, don't commit |
| `.gitignore` | Recommended | Should include `.terraform/`, `*.tfstate*`, `*.tfvars` (except `.example`) |

**None of these need to exist for Terraform to work.** A single `main.tf` with a
`provider` and a `resource` block, as in Level 1, is a complete Terraform project.
Everything else is added only when it solves a real problem you've hit.

---

## Reference — Terraform CLI Cheatsheet

```bash
terraform init                 # download providers/modules, set up backend
terraform validate             # check syntax without touching AWS
terraform fmt                  # auto-format .tf files to canonical style
terraform plan                 # preview changes
terraform plan -out=plan.out    # save a plan to apply later
terraform apply                 # create/update real resources
terraform apply plan.out         # apply a previously saved plan
terraform apply -auto-approve     # skip the yes/no prompt (use carefully)
terraform destroy                  # tear down everything this config manages
terraform show                      # inspect current state in human-readable form
terraform state list                 # list all resources tracked in state
terraform state show <resource>       # inspect one resource's tracked attributes
terraform output                       # show all outputs
terraform workspace list                # list workspaces
terraform graph                          # generate a dependency graph (pipe to Graphviz)
```

---

## Reference — Best Practices Checklist

- [ ] Pin provider versions (`required_providers { aws = { version = "~> 5.0" } }`) so `terraform init` doesn't silently pull breaking changes
- [ ] Never commit `terraform.tfvars` if it holds secrets — commit a `.example` version instead
- [ ] Never commit `terraform.tfstate` — use a remote backend once more than one person is involved
- [ ] Always run `terraform plan` and read it before `terraform apply`
- [ ] Give every `variable` and `output` a `description` — future-you will thank present-you
- [ ] Use `terraform fmt` and `terraform validate` before every commit
- [ ] Tag every resource (`local.common_tags` pattern) — makes cost tracking and cleanup sane
- [ ] Start with local state and no modules; only add a backend and modules when the project actually needs them — don't front-load complexity a small project doesn't need

---

*This guide is intentionally incremental — copy just the level you need, or run the
whole thing top to bottom as a personal AWS/Terraform crash course.*
