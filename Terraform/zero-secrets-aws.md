# Zero Secrets Left Behind

**Short-lived AWS credentials with Terraform and HashiCorp Vault**

Built for HashiCorp User Group Accra, Saturday 7 November 2026.
By Samuel Nartey, DevSecOps Engineer, AWS Community Builder, HashiCorp User Group Co-Organizer.

---

## Table of contents

1. [What we are building](#1-what-we-are-building)
2. [Before you start](#2-before-you-start)
3. [Set up your machine](#3-set-up-your-machine)
4. [Level A: Beginner (30 minutes)](#4-level-a-beginner-30-minutes)
5. [Troubleshooting for Level A](#5-troubleshooting-for-level-a)
6. [Level B: Intermediate](#6-level-b-intermediate)
7. [Level C: Advanced](#7-level-c-advanced)
8. [Threat model](#8-threat-model)
9. [Cleanup](#9-cleanup)

---

## 1. What we are building

Welcome. In this lab I will walk you through one repository, `zero-secrets-aws`, built in three levels. Every level is a complete, working system, so you can stop at any level and still have something real to show.

| Level | What you build | Time | Who it is for |
|---|---|---|---|
| **A. Beginner** | Vault in dev mode hands out 15-minute AWS credentials, and Terraform uses them to build an S3 bucket | 30 min | Everyone |
| **B. Intermediate** | A real Vault server, config as code, a least-privilege policy, and a wrapper that keeps credentials out of Terraform state | 60 min | Practitioners |
| **C. Advanced** | GitHub Actions logs into Vault with OIDC (no stored secret anywhere), remote state, ephemeral resources, audit, tests and policy checks | 2 to 3 hours | Experts |

### The one idea I want you to take home

> **A secret that does not exist cannot leak.**

Long-lived AWS access keys are exactly what attackers hunt for in repos, laptops and CI logs. We replace them with credentials that expire in minutes and are issued fresh for every run.

### The honest catch

Vault itself still needs a way to talk to AWS. I will be straight with you about that at every level:

- **Level A** uses one "broker" key to keep things simple.
- **Level B** rotates that key so even I can no longer see it.
- **Level C** removes static keys from the pipeline entirely.

### Architecture

```
GitHub Actions (OIDC token, no stored secret)
        |
        v
   Vault JWT auth  --->  policy: read aws/creds/terraform-deployer only
        |
        v
   Vault AWS secrets engine --- sts:AssumeRole --->  IAM role terraform-deployer
        |
        v
   15-minute AWS credentials (ASIA... keys + session token)
        |
        v
   terraform plan / apply  --->  AWS resources
```

Think of a hotel. **Vault** is the front desk. The **broker user** is the clerk who can only make guest keycards. The **deployer role** is the room Terraform needs to enter. The **temporary credentials** are the guest keycards, and they stop working on their own after a set time.

### Key terms (say them out loud)

| Term | Plain meaning |
|---|---|
| **Secrets engine** | A Vault plugin that creates or stores secrets. Ours is the AWS one. |
| **Dynamic secret** | Created on request, with a lease (a timer), then it expires. |
| **Lease** | Vault's record of a credential and its time to live (TTL). |
| **STS** | AWS Security Token Service, which issues temporary credentials. Keys starting with `ASIA` are temporary. Keys starting with `AKIA` are long-lived. |
| **Auth method** | How a person or machine proves who they are to Vault (token, AppRole, JWT/OIDC). |
| **Policy** | Which Vault paths an identity may touch. |

---

## 2. Before you start

You need:

- An AWS **sandbox** account, with the AWS CLI v2 configured using an admin profile. We use admin **only** for the one-time bootstrap.
- Terraform 1.10 or newer (1.11 or newer if you want S3 native state locking)
- Vault 1.17 or newer
- `jq` and Git
- Docker (Level B) and a GitHub account (Level C)

**Cost:** STS is free and a demo S3 bucket costs almost nothing. Destroy everything at the end anyway.

> **Note:** I teach this lab on Ubuntu running inside WSL on Windows. Everything works the same on a normal Linux machine. The troubleshooting section covers the WSL-specific problems I ran into while testing, so you do not have to.

> **Tip:** Keep the AWS console open in a browser tab. At several steps I give you a **Console check** so you can see with your own eyes what the commands did.

### Repo layout

```
zero-secrets-aws/
  README.md
  .gitignore
  docs/                      architecture diagram, threat model, demo script
  bootstrap/                 IAM broker user + target role (run once)
  vault-config/              Vault configured with Terraform (Level B)
  app/                       the demo infrastructure Terraform deploys
  scripts/
    vault-env.sh             points your terminal at Vault
    vault-dev-setup.sh       rebuilds the Vault side after a restart
    vault-aws-env.sh         exports short-lived creds as env vars (Level B)
    prove-zero-secrets.sh    evidence script (Level C)
  .github/workflows/terraform.yml
  .pre-commit-config.yaml
```

Create it:

```bash
mkdir zero-secrets-aws && cd zero-secrets-aws
git init
mkdir -p bootstrap vault-config app scripts docs .github/workflows
```

Create a `.gitignore` **right now**, before any secret file exists:

```bash
cat > .gitignore <<'EOF'
broker.json
**/broker.json
*.tfstate
*.tfstate.*
.terraform/
*.tfplan
tfplan
EOF
```

> **Warning:** This is the single most important habit in the lab. The whole point is that no secret ever reaches Git. Set up `.gitignore` before you create the broker key, not after.

---

## 3. Set up your machine

### 3.1 Install `jq` with apt, not snap

```bash
sudo apt update && sudo apt install -y jq
which jq
```

`which jq` should print `/usr/bin/jq`.

> **Warning:** If it prints `/snap/bin/jq`, remove the snap version first with `sudo snap remove jq`, then install with apt. Snap apps are confined and get their own private `/tmp`, so snap `jq` cannot open files you created in the real `/tmp`. You will see a misleading "file not found" error. See [Troubleshooting](#5-troubleshooting-for-level-a).

### 3.2 Install Terraform and Vault from HashiCorp's official repo

When the terminal suggests `snap install vault`, ignore it. Use HashiCorp's own apt repository so you get the official, signed package.

```bash
sudo apt update && sudo apt install -y gpg wget lsb-release

wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor --yes -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update && sudo apt install -y terraform vault
terraform version
vault version
```

What those commands do:

- The `wget ... | gpg --dearmor` line downloads HashiCorp's signing key and converts it into the format apt expects, so apt can verify packages really come from HashiCorp.
- The `echo ... | tee` line adds HashiCorp's repository to apt. `$(lsb_release -cs)` fills in your Ubuntu codename, like `jammy`.
- The `--yes` flag lets `gpg` overwrite the keyring file if it already exists. Without it, a second run stops and asks "Enter new filename:".

> **Note:** When Vault installs, you may see a message about a TLS key and self-signed certificate generated in `/opt/vault/tls`. That is for running Vault as a system service. We use dev mode in Level A, so ignore it.

### 3.3 Make the AWS CLI speak JSON

By default your AWS CLI may print **tables**. That is pretty to read but `jq` cannot parse it. Set JSON as the default:

```bash
aws configure set output json
aws sts get-caller-identity
```

> **Tip:** Even with JSON as the default, I still add `--output json` to any command whose result I plan to pipe into `jq`. It costs nothing and protects you if someone else's config differs.

> **Console check:** The `get-caller-identity` command should show your admin identity. In the AWS console, click your name at the top right to confirm you are in the sandbox account you expect.

### 3.4 Open two terminals

Dev mode runs Vault in the foreground, so you need two terminals:

- **Terminal 1:** the Vault server. Leave it running.
- **Terminal 2:** everything else.

---

## 4. Level A: Beginner (30 minutes)

**Goal:** see a credential appear, work, and expire.

### Step A1. Bootstrap AWS (one time)

Create `bootstrap/main.tf`. It makes a **broker user** (the only identity Vault will ever use) and a **deployer role** (what Terraform will act as).

```hcl
terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}

variable "region" { default = "us-east-1" }
provider "aws" { region = var.region }

resource "aws_iam_user" "vault_broker" {
  name = "vault-broker"
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_user.vault_broker.arn]
    }
  }
}

resource "aws_iam_role" "deployer" {
  name                 = "terraform-deployer"
  assume_role_policy   = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}

# Demo permissions: S3 buckets named zero-secrets-* only
data "aws_iam_policy_document" "deployer" {
  statement {
    actions   = ["s3:*"]
    resources = ["arn:aws:s3:::zero-secrets-*", "arn:aws:s3:::zero-secrets-*/*"]
  }
}
resource "aws_iam_role_policy" "deployer" {
  role   = aws_iam_role.deployer.id
  policy = data.aws_iam_policy_document.deployer.json
}

# Broker may ONLY assume the deployer role
data "aws_iam_policy_document" "broker" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.deployer.arn]
  }
}
resource "aws_iam_user_policy" "broker" {
  user   = aws_iam_user.vault_broker.name
  policy = data.aws_iam_policy_document.broker.json
}

output "deployer_role_arn" { value = aws_iam_role.deployer.arn }
```

Apply it. I run every command from the **repo root** (`zero-secrets-aws/`) and use `-chdir` to reach subfolders. That way the commands work no matter which folder you were in.

```bash
terraform -chdir=bootstrap init
terraform -chdir=bootstrap apply
terraform -chdir=bootstrap output -raw deployer_role_arn
```

The last command should print a full ARN like `arn:aws:iam::123456789012:role/terraform-deployer`.

> **Teaching point:** The broker can do exactly one thing: assume one role. A stolen broker key is **not** an admin key.

> **Console check:** In the AWS console, open **IAM, Users, vault-broker** and look at the **Permissions** tab. You will see one inline policy that allows only `sts:AssumeRole`. Then open **IAM, Roles, terraform-deployer, Trust relationships** and you will see the broker user named as the only trusted principal.

#### Create the broker key

Create the key with the CLI so it never lands in Terraform state. Note three details: `umask 077` makes the file readable only by you, `--output json` makes sure `jq` can parse it, and we save it **inside the repo's `bootstrap` folder** (already covered by `.gitignore`) instead of `/tmp`.

```bash
umask 077
aws iam create-access-key --user-name vault-broker --output json > bootstrap/broker.json
```

Check that the file really is JSON and holds a key:

```bash
head -c 1 bootstrap/broker.json; echo
jq -r .AccessKey.AccessKeyId < bootstrap/broker.json
```

The first line should be `{`, and the second should be a key ID starting with `AKIA`.

> **Warning:** Notice the `< bootstrap/broker.json` form. I feed the file to `jq` through your shell instead of passing the filename as an argument. That works even if you accidentally ended up with a snap-confined `jq`.

> **Warning:** The secret access key exists **only** in that file. AWS will never show it to you again. If you delete the file before Vault has it, you must delete the key and create a new one.

> **Note:** An IAM user can have at most two access keys. If you see `LimitExceeded`, list the keys with `aws iam list-access-keys --user-name vault-broker --output table`, delete the one you do not need with `aws iam delete-access-key --user-name vault-broker --access-key-id <KEY_ID>`, then try again.

> **Tip:** I used to shred this file straight away. In dev mode that backfires: Vault forgets everything when it restarts, and then you need the secret again. For this lab, **keep `bootstrap/broker.json` until the cleanup step**, then shred it. Level B rotates the key and makes the file worthless anyway.

> **Console check:** **IAM, Users, vault-broker, Security credentials** shows one access key, with status Active and the creation time matching what you just did.

### Step A2. Start Vault in dev mode

Create a tiny helper so every new terminal can find Vault in one command. Save this as `scripts/vault-env.sh`:

```bash
#!/usr/bin/env bash
# Usage: source scripts/vault-env.sh
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
echo "Vault CLI pointed at $VAULT_ADDR"
```

**Terminal 1** (leave it running):

```bash
vault server -dev -dev-root-token-id=root
```

**Terminal 2**, from the repo root:

```bash
source scripts/vault-env.sh
vault status
```

You want to see `Initialized true` and `Sealed false`.

What the server output means:

- **In-memory:** nothing is saved to disk. Stop the server and every secret, policy and setting is gone.
- **Unsealed:** a normal Vault starts sealed (encrypted and unusable) until someone supplies unseal keys. Dev mode skips that so we can start immediately.
- **Root Token: root:** the all-powerful admin credential. Because we passed `-dev-root-token-id=root`, the token is literally the word `root`.

> **Warning:** Dev mode is in-memory, unsealed, and uses a known root token. It is for learning only. Level B fixes this.

> **Tip:** Environment variables like `VAULT_ADDR` and `VAULT_TOKEN` belong to **one terminal only**. Every time you open a new terminal (or restart your PC), run `source scripts/vault-env.sh` again. This one habit prevents the most common error in this lab.

### Step A3. Turn on the AWS secrets engine

Here are the commands, then I will explain them. Run them from the repo root.

First load the broker credentials into your terminal:

```bash
export BROKER_KEY=$(jq -r .AccessKey.AccessKeyId < bootstrap/broker.json)
export BROKER_SECRET=$(jq -r .AccessKey.SecretAccessKey < bootstrap/broker.json)
echo "$BROKER_KEY"
```

`echo` must print a key ID. If it prints nothing, stop and fix that first, otherwise Vault will happily store empty credentials.

Now configure Vault:

```bash
vault secrets enable -path=aws aws

vault write aws/config/root \
  access_key="$BROKER_KEY" secret_key="$BROKER_SECRET" region=us-east-1

vault write aws/roles/terraform-deployer \
  credential_type=assumed_role \
  role_arns="$(terraform -chdir=bootstrap output -raw deployer_role_arn)" \
  default_sts_ttl=15m max_sts_ttl=1h
```

Verify what Vault actually saved:

```bash
vault read aws/config/root
vault read aws/roles/terraform-deployer
```

`access_key` should show your broker key ID, and `role_arns` must show `[arn:aws:iam::...:role/terraform-deployer]`.

> **Warning:** If `role_arns` shows `[]`, the role is broken even though Vault printed "Success!". Vault accepts an empty value without complaint. This happens when the `$(...)` part fails silently, for example because of a wrong folder. Fix the command, run it again, and read the role back. Writing to the same path simply overwrites it.

#### What each command means

- `vault secrets enable -path=aws aws` installs a secrets engine of type `aws` at the path `aws/`. Think of installing a vending machine of type "AWS" and putting it at the spot labelled `aws/`.
- `vault write aws/config/root ...` hands Vault the broker's login. Here "root" means the engine's base credentials, **not** the AWS root account and **not** Vault's root token. The trailing `\` just means "the command continues on the next line".
- `vault write aws/roles/terraform-deployer ...` creates a recipe. When someone asks for credentials from this role, Vault assumes the IAM role in `role_arns` and hands back the temporary result.
- `credential_type=assumed_role` borrows the permissions of an existing role through STS. The alternatives are `iam_user` (creates a real IAM user per lease) and `federation_token`.
- `default_sts_ttl=15m` is the lifetime if the requester does not ask for one. `max_sts_ttl=1h` is the longest anyone can request.
- `$(terraform -chdir=bootstrap output -raw deployer_role_arn)` runs the command inside the brackets and pastes its output in place. `-raw` removes the quotes so you get the plain ARN.

> **Note:** STS has a 15 minute minimum, so `15m` is the shortest honest TTL.

> **Tip:** Because dev mode forgets everything on restart, I keep these three steps in a script. Save this as `scripts/vault-dev-setup.sh`, make it executable with `chmod +x scripts/vault-dev-setup.sh`, and run it from the repo root any time the dev server is freshly started:
>
> ```bash
> #!/usr/bin/env bash
> # Usage: ./scripts/vault-dev-setup.sh   (run from the repo root, dev server must be running)
> set -euo pipefail
> export VAULT_ADDR=http://127.0.0.1:8200
> export VAULT_TOKEN=root
>
> BROKER_FILE=bootstrap/broker.json
> [ -f "$BROKER_FILE" ] || { echo "Missing $BROKER_FILE"; exit 1; }
>
> BROKER_KEY=$(jq -r .AccessKey.AccessKeyId < "$BROKER_FILE")
> BROKER_SECRET=$(jq -r .AccessKey.SecretAccessKey < "$BROKER_FILE")
> ROLE_ARN=$(terraform -chdir=bootstrap output -raw deployer_role_arn)
> [ -n "$BROKER_KEY" ] || { echo "Broker key is empty"; exit 1; }
> [ -n "$ROLE_ARN" ]   || { echo "Role ARN is empty"; exit 1; }
>
> vault status > /dev/null
> vault secrets list | grep -q '^aws/' || vault secrets enable -path=aws aws
>
> vault write aws/config/root \
>   access_key="$BROKER_KEY" secret_key="$BROKER_SECRET" region=us-east-1
>
> vault write aws/roles/terraform-deployer \
>   credential_type=assumed_role \
>   role_arns="$ROLE_ARN" \
>   default_sts_ttl=15m max_sts_ttl=1h
>
> vault read aws/creds/terraform-deployer > /dev/null \
>   && echo "OK: Vault can issue credentials"
> ```
>
> It refuses to continue if anything is empty, which avoids the silent `role_arns []` trap.

### Step A4. Watch a credential be born

```bash
vault read aws/creds/terraform-deployer
```

Point at four things on screen:

1. `access_key` starts with **ASIA** (temporary).
2. There is a `security_token`.
3. There is a `lease_id`.
4. `lease_duration` is **15 minutes**.

Now prove it is real. Replace the placeholders with the values from your output:

```bash
AWS_ACCESS_KEY_ID=<access_key> AWS_SECRET_ACCESS_KEY=<secret_key> \
AWS_SESSION_TOKEN=<security_token> aws sts get-caller-identity
```

The ARN contains `assumed-role/terraform-deployer/...`. It is a role session, **not** a user.

> **Note:** If `vault read aws/creds/terraform-deployer` fails with `AccessDenied`, the problem is on the AWS side. Check that the role's trust policy names the `vault-broker` user, and that the broker's policy allows `sts:AssumeRole` on that role's ARN. IAM changes can take a few seconds to spread, so wait 10 seconds and retry.

> **Tip:** Always run this command **before** you move on to Terraform. If Vault can issue credentials, the whole chain (Vault, then broker, then role) works. If Terraform fails later, you already know the problem is not here.

> **Console check:** Open **CloudTrail, Event history** and filter by event name `AssumeRole`. You will see the request Vault made, a few seconds ago, using the broker user.

### Step A5. Let Terraform consume it

Create `app/main.tf`:

```hcl
terraform {
  required_version = ">= 1.10"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 6.0" }
    vault  = { source = "hashicorp/vault", version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

variable "region" { default = "us-east-1" }

provider "vault" {}   # reads VAULT_ADDR and VAULT_TOKEN from the environment

data "vault_aws_access_credentials" "creds" {
  backend = "aws"
  role    = "terraform-deployer"
  type    = "sts"
}

provider "aws" {
  region     = var.region
  access_key = data.vault_aws_access_credentials.creds.access_key
  secret_key = data.vault_aws_access_credentials.creds.secret_key
  token      = data.vault_aws_access_credentials.creds.security_token
}

resource "random_id" "suffix" { byte_length = 4 }

resource "aws_s3_bucket" "demo" {
  bucket = "zero-secrets-${random_id.suffix.hex}"
  tags   = { project = "zero-secrets-aws", managed_by = "terraform" }
}
```

Before running Terraform, make sure **this terminal** knows where Vault is:

```bash
echo "$VAULT_ADDR"      # must print http://127.0.0.1:8200
echo "$VAULT_TOKEN"     # must print root
```

If either is blank, run `source scripts/vault-env.sh`. Then:

```bash
terraform -chdir=app init
terraform -chdir=app apply
```

> **Warning:** The empty `provider "vault" {}` block reads its settings from the environment. If `VAULT_ADDR` is empty, Terraform fails with `failed to configure Vault address`. It is almost never a bug in your code. It means this terminal has no variables.

> **Note:** By default the Vault provider creates a **child token** for itself. In Level A the root token allows that. In Level B your policy must allow `auth/token/create`, or you set `skip_child_token = true` in the provider.

> **Tip:** `terraform init` downloads the AWS provider, which is several hundred MB when unpacked. On WSL with limited memory it can crash with `Bus error (core dumped)`. Set a provider cache first so you download it once for all your folders:
>
> ```bash
> mkdir -p ~/.terraform.d/plugin-cache
> export TF_PLUGIN_CACHE_DIR=~/.terraform.d/plugin-cache
> ```
>
> More fixes are in [Troubleshooting](#5-troubleshooting-for-level-a).

> **Console check:** Open the **S3 console** and find the bucket named `zero-secrets-` followed by 8 hex characters, with the two tags we set.

### Step A6. The honest moment (do this live)

```bash
grep -E 'ASIA|AKIA|security_token' app/terraform.tfstate
```

You will find the temporary keys sitting in state. They expire in 15 minutes, so the damage is small, but a secret in state is still a bad habit. That is the motivation for Levels B and C. I never hide this from learners, and neither should you.

### Step A7. Revoke and clean up

```bash
vault lease revoke -prefix aws/creds/terraform-deployer
terraform -chdir=app destroy
```

> **Warning:** Run `terraform destroy` **while Vault is still running**. The destroy needs to read fresh credentials from Vault. If you stopped the server first, destroy fails with a connection error.

> **Note:** For `assumed_role` credentials, AWS STS tokens **cannot be revoked early**. Your protection is the short TTL. If you need true revocation, use `credential_type=iam_user`. Vault then creates and deletes a real IAM user per lease, at the cost of IAM user limits and slower issuance.

### Level A checkpoint

- [ ] Credential issued with an `ASIA` prefix and a 15 minute lease
- [ ] `get-caller-identity` shows the assumed role
- [ ] S3 bucket created by Terraform using Vault credentials
- [ ] You found keys in state and can explain why that matters

---

## 5. Troubleshooting for Level A

These are real errors I hit while testing this lab. Find your symptom, apply the fix.

### `jq: error: Could not open file /tmp/broker.json: No such file or directory`

**But `ls /tmp` shows the file.** Cause: `jq` is the snap version (`which jq` prints `/snap/bin/jq`). Snap apps run confined with a private `/tmp`.

```bash
sudo snap remove jq
sudo apt install -y jq
which jq        # should print /usr/bin/jq
```

Or feed the file through stdin so your shell opens it: `jq -r .AccessKey.AccessKeyId < file.json`.

### `parse error: Invalid numeric literal at line 2, column 0`

Cause: the file contains an ASCII **table**, not JSON, because your AWS CLI default output is `table`. Confirm with `head -3 bootstrap/broker.json` (you will see dashes and `|`).

Fix: rotate the key with explicit JSON output.

```bash
aws iam list-access-keys --user-name vault-broker --output table
aws iam delete-access-key --user-name vault-broker --access-key-id <OLD_KEY_ID>
umask 077
aws iam create-access-key --user-name vault-broker --output json > bootstrap/broker.json
aws configure set output json
```

### `Command 'vault' not found, but can be installed with: snap install vault`

Do not use the snap. Install from HashiCorp's apt repo using the commands in [section 3.2](#32-install-terraform-and-vault-from-hashicorps-official-repo).

### `gpg` stops at `Enter new filename:`

The keyring file already exists from an earlier attempt. Press `Ctrl+C`, then re-run with `--yes`:

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor --yes -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
```

If `apt update` warns that a target is "configured multiple times", check `ls /etc/apt/sources.list.d/ | grep -i hashicorp` and keep only one `hashicorp.list`.

### `bash: cd: bootstrap: No such file or directory`, then `Success!`, then `role_arns []`

Cause: you ran a command written for the repo root while standing inside `bootstrap/`. The `$(...)` produced an empty string and Vault saved an empty role without complaint.

Fix: run from the repo root with `-chdir`:

```bash
cd ~/projects/zero-secrets-aws
vault write aws/roles/terraform-deployer \
  credential_type=assumed_role \
  role_arns="$(terraform -chdir=bootstrap output -raw deployer_role_arn)" \
  default_sts_ttl=15m max_sts_ttl=1h
vault read aws/roles/terraform-deployer     # role_arns must NOT be []
```

### `terraform init` crashes with `Bus error (core dumped)`

Cause: WSL ran out of memory or disk while unpacking the AWS provider.

```bash
df -h ~ /tmp
free -h
```

Try these in order:

1. Clear the partial download and retry: `rm -rf app/.terraform` then `terraform -chdir=app init`.
2. Use a provider cache: `export TF_PLUGIN_CACHE_DIR=~/.terraform.d/plugin-cache` (create the folder first).
3. Give WSL more memory. Create or edit `C:\Users\<you>\.wslconfig` in Windows:

   ```
   [wsl2]
   memory=4GB
   swap=4GB
   ```

   Then run `wsl --shutdown` in PowerShell and reopen the terminal.

> **Warning:** Shutting WSL down stops your dev Vault server and wipes it. After a restart, follow "Connection refused" below.

### `Error: failed to configure Vault address`

`echo "$VAULT_ADDR"` prints nothing. This terminal has no variables.

```bash
source scripts/vault-env.sh
vault status
```

If it still fails, check the `provider "vault"` block for a typo in `address`. A malformed value overrides the environment variable.

### `vault status` says `connection refused`

Nothing is listening on port 8200. The dev server is not running. This happens after you shut down the PC or WSL, because dev mode lives in memory.

1. **Terminal 1:** `vault server -dev -dev-root-token-id=root`
2. **Terminal 2**, from the repo root:

```bash
source scripts/vault-env.sh
./scripts/vault-dev-setup.sh
```

Everything in AWS (the broker user, the role, the key) and your Terraform state **survive**. Only the Vault side is rebuilt. This works as long as `bootstrap/broker.json` still exists.

### Dev server will not start: `address already in use`

The packaged Vault system service may already be using port 8200.

```bash
systemctl status vault
sudo systemctl stop vault
```

Then start the dev server again.

### `vault read aws/creds/terraform-deployer` returns `AccessDenied`

Check in this order:

1. The role's **trust policy** names the `vault-broker` user (Console: IAM, Roles, terraform-deployer, Trust relationships).
2. The broker's policy allows `sts:AssumeRole` on that exact role ARN.
3. `vault read aws/config/root` shows the right `access_key`. A blank value means the variables were empty when you wrote it. Export them again and redo the `vault write aws/config/root` command.
4. Wait 10 seconds and retry. IAM changes need a moment to spread.

### `LimitExceeded` when creating the access key

An IAM user can hold only two keys. List them, delete the extra one, retry. See the note in Step A1.

### Quick reference

| Symptom | First thing to try |
|---|---|
| Any `jq` file error | `which jq`, remove the snap, use `< file` |
| `parse error` from `jq` | Re-create the key with `--output json` |
| `role_arns []` | Run from repo root, use `terraform -chdir=bootstrap ...` |
| `failed to configure Vault address` | `source scripts/vault-env.sh` |
| `connection refused` | Restart dev server, run `scripts/vault-dev-setup.sh` |
| `Bus error` | Provider cache, more WSL memory |
| `AccessDenied` | Trust policy, broker policy, wait 10 seconds |

---

## 6. Level B: Intermediate

**Goal:** a real Vault, config as code, least privilege, and **no credentials in state**.

> **Note:** Level B uses a fresh Vault server in Docker. Stop your Level A dev server first (press `Ctrl+C` in Terminal 1), because both want port 8200.

### Step B1. Run a real Vault server

Create `vault-config/vault.hcl`:

```hcl
storage "raft" {
  path    = "/vault/data"
  node_id = "vault-1"
}
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true   # local lab only. Production uses TLS, always.
}
api_addr     = "http://127.0.0.1:8200"
cluster_addr = "http://127.0.0.1:8201"
ui           = true
```

Start it:

```bash
docker run -d --name vault --cap-add=IPC_LOCK -p 8200:8200 \
  -v "$PWD/vault-config/vault.hcl:/vault/config/vault.hcl" \
  -v vault-data:/vault/data \
  hashicorp/vault:latest server

export VAULT_ADDR=http://127.0.0.1:8200
unset VAULT_TOKEN
vault operator init -key-shares=5 -key-threshold=3   # SAVE the output in a password manager
vault operator unseal   # run 3 times with 3 different keys
vault login             # root token, used ONLY for initial setup
vault audit enable file file_path=/vault/logs/audit.log
```

In one sentence: Vault encrypts everything, and the unseal keys are needed to decrypt its master key. Never leave the root token in use after setup.

> **Warning:** `unset VAULT_TOKEN` matters. Your Level A shell still has `VAULT_TOKEN=root`, which is wrong for this new server and will confuse `vault login`.

> **Tip:** On WSL, make sure Docker Desktop has **WSL integration** switched on for your Ubuntu distro, otherwise `docker` is not found. If it exits immediately, run `docker logs vault` and read the first error.

### Step B2. Configure Vault with Terraform (config as code)

Create `vault-config/main.tf`:

```hcl
terraform {
  required_version = ">= 1.10"
  required_providers {
    vault = { source = "hashicorp/vault", version = "~> 5.0" }
  }
}

variable "broker_access_key" { sensitive = true }
variable "broker_secret_key" { sensitive = true }
variable "deployer_role_arn" {}

provider "vault" {}

resource "vault_aws_secret_backend" "aws" {
  path                      = "aws"
  access_key                = var.broker_access_key
  secret_key                = var.broker_secret_key
  region                    = "us-east-1"
  default_lease_ttl_seconds = 900
  max_lease_ttl_seconds     = 3600
}

resource "vault_aws_secret_backend_role" "deployer" {
  backend         = vault_aws_secret_backend.aws.path
  name            = "terraform-deployer"
  credential_type = "assumed_role"
  role_arns       = [var.deployer_role_arn]
  default_sts_ttl = 900
  max_sts_ttl     = 3600
}

resource "vault_policy" "terraform" {
  name   = "terraform-deployer"
  policy = <<-EOT
    path "aws/creds/terraform-deployer" { capabilities = ["read"] }
    path "auth/token/create"            { capabilities = ["update"] }
  EOT
}
```

Pass the variables through the environment, so no secret is typed or stored in a file:

```bash
export VAULT_TOKEN=<root token from vault operator init>
export TF_VAR_broker_access_key=$(jq -r .AccessKey.AccessKeyId < bootstrap/broker.json)
export TF_VAR_broker_secret_key=$(jq -r .AccessKey.SecretAccessKey < bootstrap/broker.json)
export TF_VAR_deployer_role_arn=$(terraform -chdir=bootstrap output -raw deployer_role_arn)

terraform -chdir=vault-config init
terraform -chdir=vault-config apply
```

> **Warning:** The broker key passes through Terraform state here, which is exactly why Step B4 matters. Treat this state as sensitive: encrypted remote backend, restricted access.

> **Tip:** If you reuse a Vault that already has the `aws/` engine enabled by hand (for example from Level A), Terraform will complain that the path is in use. On a fresh Docker Vault you will not see this. If you do, run `vault secrets disable aws` first.

### Step B3. Create a least-privilege token for Terraform

```bash
vault token create -policy=terraform-deployer -ttl=30m -format=json | jq -r .auth.client_token
```

Export that value as `VAULT_TOKEN` and **stop using root**. Now test the boundary:

```bash
vault policy read terraform-deployer     # must fail with: permission denied
vault read aws/creds/terraform-deployer  # must succeed
```

Showing a denial is a powerful demo. It proves the token can do one thing and nothing else.

### Step B4. Keep credentials out of state entirely

Instead of passing keys through the provider block, let Terraform read the standard AWS environment variables. Save this as `scripts/vault-aws-env.sh`:

```bash
#!/usr/bin/env bash
# Usage: source scripts/vault-aws-env.sh
creds=$(vault read -format=json aws/creds/terraform-deployer) \
  || { echo "Could not read credentials from Vault"; return 1; }
export AWS_ACCESS_KEY_ID=$(jq -r .data.access_key <<<"$creds")
export AWS_SECRET_ACCESS_KEY=$(jq -r .data.secret_key <<<"$creds")
export AWS_SESSION_TOKEN=$(jq -r .data.security_token <<<"$creds")
echo "Credentials issued, lease $(jq -r .lease_duration <<<"$creds")s"
```

> **Warning:** I deliberately left out `set -euo pipefail`. This script is **sourced**, which means it runs inside your current shell. With `set -e` active, any later failed command would close your terminal. That is why the script uses `return 1` instead of `exit`.

Now edit `app/main.tf`. Delete the `vault` provider, the data source and the key arguments. What remains:

```hcl
terraform {
  required_version = ">= 1.10"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 6.0" }
    random = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

variable "region" { default = "us-east-1" }

provider "aws" { region = var.region }

resource "random_id" "suffix" { byte_length = 4 }

resource "aws_s3_bucket" "demo" {
  bucket = "zero-secrets-${random_id.suffix.hex}"
  tags   = { project = "zero-secrets-aws", managed_by = "terraform" }
}
```

Run it and repeat the grep from Step A6:

```bash
source scripts/vault-aws-env.sh
terraform -chdir=app init -upgrade
terraform -chdir=app apply
grep -E 'AKIA|ASIA|security_token' app/terraform.tfstate
```

The grep now finds **nothing**. Same result, no secret in state. The same pattern works for the S3 backend in Level C.

> **Tip:** If the grep still finds keys, look for `app/terraform.tfstate.backup`. Terraform keeps the previous state there, and it may still hold the old Level A credentials. Delete it (`rm app/terraform.tfstate.backup`) or grep it too. Those old keys have long expired, but the habit of checking matters.

> **Note:** Credentials from the script expire in 15 minutes. If `terraform apply` fails with `ExpiredToken`, run `source scripts/vault-aws-env.sh` again and retry.

### Step B5. Rotate the broker key

First give the broker permission to manage **its own** key. In `bootstrap/main.tf`, change the broker policy to:

```hcl
data "aws_iam_policy_document" "broker" {
  statement {
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.deployer.arn]
  }
  statement {
    actions   = ["iam:CreateAccessKey", "iam:DeleteAccessKey", "iam:ListAccessKeys"]
    resources = [aws_iam_user.vault_broker.arn]
  }
}
```

```bash
terraform -chdir=bootstrap apply
vault write -f aws/config/rotate-root
```

Vault replaces the broker's access key with a new one that only Vault knows. Even you can no longer see it.

> **Warning:** After rotation, `bootstrap/broker.json` holds a **dead key**. Delete it: `shred -u bootstrap/broker.json`.

> **Warning:** Terraform still has the old key in its config. The next `terraform apply` in `vault-config` would push that dead key back into Vault and break everything. Tell Terraform to leave those two fields alone:
>
> ```hcl
> resource "vault_aws_secret_backend" "aws" {
>   # ...existing arguments...
>   lifecycle {
>     ignore_changes = [access_key, secret_key]
>   }
> }
> ```

> **Console check:** **IAM, Users, vault-broker, Security credentials** now shows a **new** access key with a new creation time, and the old one is gone.

### Level B checkpoint

- [ ] Persistent Vault with audit logging, root token retired
- [ ] Vault configured by Terraform, not by hand
- [ ] Terraform token can read exactly one path
- [ ] State contains no credentials (the grep proves it)

---

## 7. Level C: Advanced

**Goal:** remove the last stored secret, add guardrails, and make everything reproducible and auditable.

### Step C1. Passwordless CI with GitHub OIDC and Vault JWT auth

AppRole needs a `secret_id`, and that is a secret. OIDC removes it: GitHub proves who the workflow is, and Vault verifies it. Add to `vault-config/main.tf`:

```hcl
resource "vault_jwt_auth_backend" "github" {
  path               = "jwt"
  oidc_discovery_url = "https://token.actions.githubusercontent.com"
  bound_issuer       = "https://token.actions.githubusercontent.com"
}

# Apply role: only the main branch of YOUR repo
resource "vault_jwt_auth_backend_role" "apply" {
  backend         = vault_jwt_auth_backend.github.path
  role_name       = "github-terraform-apply"
  role_type       = "jwt"
  user_claim      = "repository"
  bound_audiences = ["https://github.com/samuel-nartey"]
  bound_claims = {
    repository = "samuel-nartey/zero-secrets-aws"
    ref        = "refs/heads/main"
  }
  token_policies = [vault_policy.terraform.name]
  token_ttl      = 600
  token_max_ttl  = 900
}
```

> **Warning:** The `repository` and `ref` bound claims are your **security boundary**. If they are too loose, any repository on GitHub could ask Vault for credentials. Say this clearly in your own README.

For pull requests, create a **second** role and policy that maps to a read-only AWS role (plan only). A sketch of the Vault side:

```hcl
resource "vault_jwt_auth_backend_role" "plan" {
  backend         = vault_jwt_auth_backend.github.path
  role_name       = "github-terraform-plan"
  role_type       = "jwt"
  user_claim      = "repository"
  bound_audiences = ["https://github.com/samuel-nartey"]
  bound_claims = {
    repository = "samuel-nartey/zero-secrets-aws"
    event_name = "pull_request"
  }
  token_policies = ["terraform-plan"]   # a policy you write, pointing at a read-only AWS role
  token_ttl      = 600
  token_max_ttl  = 900
}
```

> **Note:** The `terraform-plan` policy and a read-only AWS role are your exercise. Build them the same way as the deployer pair. **Never let a pull request from a fork reach the apply role.**

Now the workflow, `.github/workflows/terraform.yml`:

```yaml
name: terraform
on:
  pull_request:
  push:
    branches: [main]
permissions:
  id-token: write   # required to mint the OIDC token
  contents: read
jobs:
  terraform:
    runs-on: ubuntu-latest
    env:
      VAULT_ADDR: ${{ vars.VAULT_ADDR }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.11.0
      - uses: hashicorp/setup-vault@v3
      - uses: hashicorp/vault-action@v3
        with:
          url: ${{ vars.VAULT_ADDR }}
          method: jwt
          role: ${{ github.event_name == 'pull_request' && 'github-terraform-plan' || 'github-terraform-apply' }}
          jwtGithubAudience: https://github.com/samuel-nartey
          exportToken: true
      - name: Short-lived AWS credentials
        run: |
          creds=$(vault read -format=json aws/creds/terraform-deployer)
          echo "::add-mask::$(jq -r .data.secret_key <<<"$creds")"
          echo "::add-mask::$(jq -r .data.security_token <<<"$creds")"
          {
            echo "AWS_ACCESS_KEY_ID=$(jq -r .data.access_key <<<"$creds")"
            echo "AWS_SECRET_ACCESS_KEY=$(jq -r .data.secret_key <<<"$creds")"
            echo "AWS_SESSION_TOKEN=$(jq -r .data.security_token <<<"$creds")"
          } >> "$GITHUB_ENV"
      - run: terraform -chdir=app init -input=false
      - run: terraform -chdir=app plan -input=false -out=tfplan
      - if: github.ref == 'refs/heads/main'
        run: terraform -chdir=app apply -input=false tfplan
```

> **Note:** The runner must reach Vault over **HTTPS**: a public endpoint behind TLS, HCP Vault Dedicated, or a self-hosted runner inside your network. A `localhost` Vault will not work from GitHub's runners.

> **Tip:** Check the current `setup-vault` and `vault-action` documentation for the exact inputs before you rely on this file. Action versions move quickly.

> **Tip:** The repository stores **zero** AWS secrets. Take a screenshot of the empty **Settings, Secrets and variables, Actions** page for your README. It is the most convincing picture in the whole project.

### Step C2. Remote state with encryption and locking

```hcl
terraform {
  backend "s3" {
    bucket       = "your-org-tfstate-prod"
    key          = "zero-secrets-aws/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    kms_key_id   = "alias/tfstate"
    use_lockfile = true   # S3 native locking, Terraform 1.11+ (no DynamoDB table)
  }
}
```

Extend the deployer role with access to the state bucket prefix and the KMS key. Turn on bucket versioning, block public access, and add a bucket policy that limits access to the deployer role.

### Step C3. Ephemeral resources (Terraform 1.10 or newer)

Ephemeral resources are **never written to state or plan files**. If you prefer reading credentials inside Terraform rather than through environment variables, use the ephemeral form from the Vault provider (5.x). The shape is:

```hcl
ephemeral "vault_aws_access_credentials" "creds" {
  backend = "aws"
  role    = "terraform-deployer"
  type    = "sts"
}
```

> **Warning:** Check the current Vault provider documentation for the exact resource name and supported attributes before you present this. Ephemeral support has been expanding release by release.

Pair it with **write-only attributes** (Terraform 1.11 or newer) wherever a resource accepts a secret, so values like database passwords are sent but never stored.

### Step C4. Quality gates

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.1
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_trivy
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

> **Tip:** Update the `rev` values to the current releases, then run `pre-commit install` so the checks run on every commit.

Add a native test in `app/tests/bucket.tftest.hcl` using `command = plan`, with assertions that the bucket name has the `zero-secrets-` prefix and that the tags include `managed_by`. Pin provider versions, commit `.terraform.lock.hcl`, and set branch protection so `main` requires a passing plan.

Optional policy as code: Sentinel (HCP Terraform) or OPA/conftest on the plan JSON, to block any IAM policy containing `"Action": "*"`.

### Step C5. Audit and observability

- **Vault audit log:** every credential read is recorded with the identity, path and time. Show one entry, with the client token hashed.
- **CloudTrail:** assumed role sessions carry Vault's session name (it includes the Vault display name), so you can search CloudTrail for what a single run did.
- **Alert ideas:** reads of `aws/creds/*` outside business hours or from unexpected claims, and audit device failure. Vault stops serving when it cannot write audit logs, and that is a feature.
- **Metrics:** enable Vault telemetry and chart lease counts and `vault.core.unsealed` in Prometheus and Grafana.

### Step C6. Production design for Vault

Document this even if you do not build it:

```hcl
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "alias/vault-unseal"
}
storage "raft" {
  path    = "/vault/data"
  node_id = "vault-1"
  retry_join { leader_api_addr = "https://vault-2.internal:8200" }
  retry_join { leader_api_addr = "https://vault-3.internal:8200" }
}
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/tls/tls.crt"
  tls_key_file  = "/vault/tls/tls.key"
}
```

- 3 or 5 node integrated storage (Raft) cluster across availability zones, with auto-unseal through KMS
- TLS everywhere, private networking, scheduled snapshots to S3, and **tested** restores
- Run Vault on EC2 or EKS with an instance profile or IRSA and leave `aws/config/root` unset. Vault then uses its own workload identity, and **no static broker key exists at all**. This is the cleanest zero-secrets answer.
- Vault Enterprise and HCP offer plugin workload identity federation for the AWS engine, which also removes the broker key. That is the managed path.
- Revoke the initial root token. Use `vault operator generate-root` only for emergencies.

### Step C7. Evidence script

`scripts/prove-zero-secrets.sh` should run these checks and print **PASS** or **FAIL** for each:

1. `gitleaks detect` finds no secrets in the repo or its history
2. `grep -E 'AKIA|ASIA' app/terraform.tfstate` returns nothing (for remote state, use `terraform state pull | grep ...`)
3. The GitHub repo has zero Actions secrets (`gh secret list`)
4. A credential issued 16 minutes ago is **rejected** by `aws sts get-caller-identity`
5. A token from the PR role **cannot** read the apply path (an expected denial)

> **Tip:** This script turns claims into proof. Anyone can say "no secrets", but a script that prints PASS five times is evidence.

### Level C checkpoint

- [ ] Pipeline authenticates with OIDC, and the repository holds zero AWS secrets
- [ ] Remote encrypted state with locking
- [ ] Pre-commit, tests, and a plan on every pull request
- [ ] Audit trail demonstrated end to end
- [ ] Evidence script passes

---

## 8. Threat model

Save this as `docs/threat-model.md` as well.

| Threat | Mitigation | Residual risk |
|---|---|---|
| Leaked AWS key in repo or state | No static keys, STS credentials expire in 15 min | A leaked live token works until expiry |
| Stolen CI token | OIDC claims bound to repo and branch, 10 min TTL | A compromised `main` branch |
| Over-permissive role | Least-privilege deployer role, separate plan role | Role permissions drift, so review quarterly |
| Vault compromise | Audit log, auto-unseal, private network, policies | Vault becomes a high-value target, so harden it |
| Cannot revoke STS early | Short TTL, or `iam_user` type where revocation matters | Up to TTL exposure |

---

## 9. Cleanup

Order matters. Do these in sequence and **keep Vault running until the first command finishes**.

```bash
# 1. Destroy the demo infrastructure (needs Vault running)
terraform -chdir=app destroy

# 2. Delete any remaining broker access keys (IAM users with keys cannot be destroyed)
aws iam list-access-keys --user-name vault-broker --output table
aws iam delete-access-key --user-name vault-broker --access-key-id <KEY_ID>

# 3. Destroy the bootstrap resources
terraform -chdir=bootstrap destroy

# 4. Remove the local secret file
shred -u bootstrap/broker.json

# 5. Stop Vault
#    Level A: press Ctrl+C in Terminal 1
#    Level B:
docker rm -f vault && docker volume rm vault-data
```

> **Warning:** If you rotated the key in Level B, the key now in IAM was created by Vault, not by you. Step 2 deletes it, and that is exactly what you want.

> **Console check:** Confirm in the AWS console that **no** `vault-broker` user, `terraform-deployer` role, or `zero-secrets-*` bucket remains. IAM (Users and Roles) and S3 each take about 10 seconds to check.

---

## License

MIT. Use it, teach it, improve it.

## Credits

Built and taught by **Samuel Nartey** for HashiCorp User Group Accra. If this helped you, star the repo, share it with someone still keeping AWS keys in a `.env` file, and tell me what broke so I can fix it for the next learner.
