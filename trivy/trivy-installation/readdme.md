# Trivy Installation on AWS EC2 (Ubuntu)

This guide explains what **Trivy** is, why it is used in **DevSecOps**, and how to install and use Trivy on an **AWS EC2 instance running Ubuntu**.

The guide is written for beginners and explains the purpose of each command rather than simply providing installation commands.

---

## Table of Contents

* [What is Trivy?](#what-is-trivy)
* [Why Use Trivy?](#why-use-trivy)
* [Prerequisites](#prerequisites)
* [Connect to the EC2 Instance](#connect-to-the-ec2-instance)
* [Install Trivy on Ubuntu](#install-trivy-on-ubuntu)
* [Verify the Installation](#verify-the-installation)
* [Scan a Docker Image](#scan-a-docker-image)
* [Scan a File System](#scan-a-file-system)
* [Scan for Secrets](#scan-for-secrets)
* [Scan Infrastructure as Code](#scan-infrastructure-as-code)
* [Scan a Dockerfile](#scan-a-dockerfile)
* [Filter Vulnerabilities by Severity](#filter-vulnerabilities-by-severity)
* [Use Trivy as a CI/CD Security Gate](#use-trivy-as-a-cicd-security-gate)
* [Trivy in a DevSecOps Pipeline](#trivy-in-a-devsecops-pipeline)
* [GitHub Actions Integration](#github-actions-integration)
* [Useful Trivy Commands](#useful-trivy-commands)
* [Troubleshooting](#troubleshooting)
* [Best Practices](#best-practices)
* [Learning Exercises](#learning-exercises)
* [Conclusion](#conclusion)

---

## What is Trivy?

**Trivy** is an open-source security scanner developed by **Aqua Security**.

It is commonly used in DevSecOps and CI/CD pipelines to identify security issues in applications, container images, dependencies, configuration files, and infrastructure before they are deployed.

Trivy can scan:

* Container images
* File systems
* Git repositories
* Software dependencies
* Kubernetes environments
* Infrastructure-as-Code (IaC)
* Software Bill of Materials (SBOMs)
* Configuration files

Trivy can detect several types of security issues, including:

* Vulnerabilities (CVEs)
* Misconfigurations
* Secrets
* License-related issues
* Vulnerable software dependencies

For example, if a Docker image contains an outdated version of OpenSSL with a known vulnerability, Trivy can identify the vulnerability and provide information about its severity.

---

## Why Use Trivy?

Security should be incorporated into the software development lifecycle rather than being performed only after an application has been deployed.

Trivy helps implement this approach by allowing security checks to be performed early and automatically.

### Key benefits

* Helps identify vulnerabilities before deployment
* Scans container images for known vulnerabilities
* Detects vulnerable software dependencies
* Helps identify accidentally exposed secrets
* Scans Infrastructure-as-Code configurations
* Can be integrated into CI/CD pipelines
* Supports automated security gates
* Is lightweight and easy to use
* Is open source

Trivy can be integrated with CI/CD platforms and tools such as:

* GitHub Actions
* Jenkins
* GitLab CI/CD
* Azure DevOps
* AWS CI/CD services

---

# Prerequisites

Before installing Trivy, you should have:

1. An AWS account
2. An EC2 instance
3. Ubuntu installed on the EC2 instance
4. SSH access to the instance
5. A user with `sudo` privileges
6. Internet connectivity from the EC2 instance

If you intend to scan Docker images locally, Docker should also be installed and running on the EC2 instance.

---

# Connect to the EC2 Instance

From your local computer, connect to the Ubuntu EC2 instance using SSH.

Example:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Replace:

* `your-key.pem` with your EC2 private key
* `YOUR_EC2_PUBLIC_IP` with the public IP address of your EC2 instance

After successfully connecting, you should see a terminal similar to:

```text
ubuntu@ip-172-31-xx-xx:~$
```

You can confirm that you are running Ubuntu with:

```bash
cat /etc/os-release
```

---

# Install Trivy on Ubuntu

There are several ways to install Trivy.

In this guide, we will install Trivy using the **official Trivy APT repository**.

Using the repository allows Trivy to be managed through Ubuntu's package manager.

---

## Step 1: Update the Package Index

First, update the Ubuntu package index:

```bash
sudo apt-get update
```

This retrieves the latest information about available packages and their versions.

It is good practice to update the package index before installing new software.

---

## Step 2: Install Required Packages

Install `wget` and `gnupg`:

```bash
sudo apt-get install wget gnupg
```

These tools are required to configure the Trivy repository.

### `wget`

`wget` is a command-line utility used to download files from the internet.

### `gnupg`

`gnupg` provides tools for working with GPG keys.

GPG keys are used to verify the authenticity of software packages and repositories.

---

## Step 3: Add the Trivy GPG Key

Run:

```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
```

This command downloads the public GPG key used by the Trivy repository and stores it on the system.

The key is saved as:

```text
/usr/share/keyrings/trivy.gpg
```

### Why is the GPG key required?

When installing software from an external repository, your package manager needs a way to verify that the packages come from a trusted source.

The GPG key allows APT to verify the digital signature of packages from the Trivy repository.

In simple terms:

> The GPG key allows your system to verify the authenticity of packages downloaded from the Trivy repository.

---

## Step 4: Add the Trivy APT Repository

Run:

```bash
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
```

This adds the Trivy APT repository to Ubuntu.

The repository configuration is stored in:

```text
/etc/apt/sources.list.d/trivy.list
```

The important part of this configuration is:

```text
signed-by=/usr/share/keyrings/trivy.gpg
```

This tells APT to use the specified GPG key when verifying packages from the Trivy repository.

---

## Step 5: Update the Package Index Again

Now that the Trivy repository has been added, update the package index:

```bash
sudo apt-get update
```

This allows APT to retrieve information about packages available from the newly added Trivy repository.

---

## Step 6: Install Trivy

Install Trivy:

```bash
sudo apt-get install trivy
```

APT will download and install Trivy and any required dependencies.

---

# Verify the Installation

After installation, verify that Trivy is available:

```bash
trivy --version
```

You should receive output similar to:

```text
Version: 0.x.x
Vulnerability DB:
  Version: ...
  UpdatedAt: ...
```

The exact version will depend on the Trivy release currently installed.

You can also determine where the Trivy executable is located:

```bash
which trivy
```

For example:

```text
/usr/bin/trivy
```

If `trivy --version` returns a version number, the installation was successful.

---

# Scan a Docker Image

One of the most common uses of Trivy is scanning container images for vulnerabilities.

For example:

```bash
trivy image nginx:latest
```

Trivy will scan the `nginx:latest` container image and report vulnerabilities found in the image's operating system packages and supported application dependencies.

A simplified result may look like:

```text
Library        Vulnerability    Severity
openssl        CVE-XXXX-XXXXX   HIGH
curl           CVE-XXXX-XXXXX   MEDIUM
```

The actual results will depend on the current contents of the image and Trivy's vulnerability database.

---

# Understanding Vulnerability Severity

Trivy commonly categorizes vulnerabilities using the following severity levels:

| Severity   | Description                      |
| ---------- | -------------------------------- |
| `UNKNOWN`  | Severity could not be determined |
| `LOW`      | Lower-risk vulnerability         |
| `MEDIUM`   | Moderate-risk vulnerability      |
| `HIGH`     | Significant security risk        |
| `CRITICAL` | Very serious security risk       |

A vulnerability's severity should not be the only factor used when deciding whether an application is safe to deploy.

Security teams should also consider factors such as:

* Whether the vulnerable component is actually used
* Whether the vulnerable functionality is exposed
* Whether the vulnerability is exploitable in the environment
* Whether a patch or updated package is available
* The business impact of exploitation

---

# Filter Vulnerabilities by Severity

You can instruct Trivy to display only vulnerabilities with specific severity levels.

For example:

```bash
trivy image --severity HIGH,CRITICAL nginx:latest
```

This limits the results to:

* `HIGH`
* `CRITICAL`

This is useful when you want your CI/CD pipeline to focus on vulnerabilities that require immediate attention.

---

# Scan a File System

Trivy can scan application source code and dependencies in a file system.

To scan the current directory:

```bash
trivy fs .
```

You can also specify a particular project:

```bash
trivy fs /home/ubuntu/my-project
```

This is useful for identifying vulnerabilities in application dependencies and supported files within a project.

For example, a Node.js project containing a vulnerable npm package may be flagged during the scan.

---

# Scan for Secrets

Trivy can also detect potentially exposed secrets.

For example:

```bash
trivy fs --scanners secret .
```

This can help identify accidentally committed sensitive information such as:

* API keys
* Access tokens
* Credentials
* Private keys
* Other potentially sensitive values

> **Important:** Secret scanning should be combined with proper secret-management practices. Never intentionally store AWS credentials, passwords, or other sensitive information in source code.

If a secret is accidentally committed, removing it from the latest commit is not always sufficient. The secret should also be considered compromised and rotated or revoked.

---

# Scan Infrastructure as Code

Trivy can scan Infrastructure-as-Code configurations.

Run:

```bash
trivy config .
```

This is useful when working with technologies such as:

* Terraform
* Kubernetes manifests
* Dockerfiles
* CloudFormation
* Other supported configuration formats

For example, Trivy may identify an insecure configuration such as an overly permissive security rule.

This allows infrastructure security problems to be identified before the infrastructure is deployed.

---

# Scan a Dockerfile

You can scan a Dockerfile using:

```bash
trivy config Dockerfile
```

This can identify potentially insecure Dockerfile configurations.

Examples of Docker security considerations include:

* Avoiding unnecessary privileges
* Using trusted base images
* Keeping base images updated
* Avoiding unnecessary packages
* Running applications as a non-root user where appropriate

---

# Use Trivy as a CI/CD Security Gate

Trivy can be configured to return a non-zero exit code when vulnerabilities meeting a specified severity threshold are detected.

For example:

```bash
trivy image --exit-code 1 --severity HIGH,CRITICAL nginx:latest
```

The important option here is:

```text
--exit-code 1
```

If Trivy finds vulnerabilities matching the selected severity levels, it can return exit code `1`.

CI/CD systems can interpret this as a failed step.

This allows Trivy to act as a **security gate**.

For example:

```text
Developer
    |
    v
Git Push
    |
    v
Build Application
    |
    v
Build Docker Image
    |
    v
Trivy Security Scan
    |
    +---- Vulnerabilities Found ----> Pipeline Fails
    |
    v
Push Image
    |
    v
Deploy Application
```

This prevents an image from automatically progressing through the pipeline when it does not meet the defined security requirements.

---

# Trivy in a DevSecOps Pipeline

A typical DevSecOps pipeline might look like this:

```text
Developer
    |
    v
Git Repository
    |
    v
Checkout Source Code
    |
    v
Install Dependencies
    |
    v
Run Tests
    |
    v
Build Application
    |
    v
Build Docker Image
    |
    v
Trivy Security Scan
    |
    +---- Failed Security Check ----> Stop Pipeline
    |
    v
Push Image to Container Registry
    |
    v
Deploy Application
```

The exact position of Trivy can vary depending on the pipeline architecture.

For example, you may perform:

* File system scanning before building the image
* Dependency scanning during the build process
* Container image scanning after building the image
* Configuration scanning before deploying infrastructure

The goal is to identify security issues as early as possible.

---

# GitHub Actions Integration

Trivy can be integrated into GitHub Actions to automatically scan your project.

A simplified example:

```yaml
name: Security Scan

on:
  push:
    branches:
      - main

jobs:
  trivy-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          severity: HIGH,CRITICAL
          exit-code: '1'
```

### What happens in this workflow?

1. GitHub Actions starts a runner.
2. The repository is checked out.
3. Trivy scans the project.
4. Trivy looks for `HIGH` and `CRITICAL` vulnerabilities.
5. If matching vulnerabilities are detected, the workflow step fails.

This is an example of **Shift Left Security**.

Shift Left Security means moving security checks earlier in the software development lifecycle so that security issues can be identified before the software reaches production.

---

# Useful Trivy Commands

| Command                                                    | Purpose                                                  |
| ---------------------------------------------------------- | -------------------------------------------------------- |
| `trivy --version`                                          | Display the installed Trivy version                      |
| `trivy image nginx:latest`                                 | Scan a container image                                   |
| `trivy image --severity HIGH,CRITICAL nginx:latest`        | Scan for HIGH and CRITICAL vulnerabilities               |
| `trivy fs .`                                               | Scan the current file system                             |
| `trivy config .`                                           | Scan configuration and IaC files                         |
| `trivy fs --scanners secret .`                             | Scan for secrets                                         |
| `trivy config Dockerfile`                                  | Scan a Dockerfile                                        |
| `trivy image --exit-code 1 --severity HIGH,CRITICAL IMAGE` | Fail the command when matching vulnerabilities are found |

---

# Troubleshooting

## `trivy: command not found`

If you receive:

```text
trivy: command not found
```

Check whether Trivy is installed:

```bash
dpkg -l | grep trivy
```

You can also check whether the executable is available:

```bash
which trivy
```

If it is not installed, run:

```bash
sudo apt-get update
sudo apt-get install trivy
```

---

## APT Cannot Find the Trivy Package

If you receive:

```text
E: Unable to locate package trivy
```

Check whether the repository file exists:

```bash
cat /etc/apt/sources.list.d/trivy.list
```

You should see the Trivy repository configuration.

Then update the package index:

```bash
sudo apt-get update
```

Try installing Trivy again:

```bash
sudo apt-get install trivy
```

---

## Check the Trivy Repository Configuration

You can inspect the repository configuration with:

```bash
cat /etc/apt/sources.list.d/trivy.list
```

The configuration should reference the Trivy repository and its GPG key.

---

# Best Practices

When using Trivy in a real DevSecOps environment, consider the following practices.

## 1. Scan Before Deployment

Container images should be scanned before they are deployed to production.

## 2. Establish Severity Thresholds

Define which vulnerabilities should cause the pipeline to fail.

For example:

```bash
--severity HIGH,CRITICAL
```

This allows your team to establish a consistent security policy.

## 3. Keep Trivy Updated

Keep the Trivy package and vulnerability database updated.

For example:

```bash
sudo apt-get update
sudo apt-get install --only-upgrade trivy
```

## 4. Investigate Vulnerabilities

Do not automatically ignore vulnerabilities simply because they appear frequently.

Investigate:

* The affected package
* The vulnerability
* The severity
* Whether the package is actually used
* Whether a patch is available
* Whether the application is exposed to the vulnerability

## 5. Use Multiple Security Tools

Trivy is an important DevSecOps security tool, but it should not be considered a complete security solution.

A broader DevSecOps toolchain might include:

| Tool                | Primary Purpose                                    |
| ------------------- | -------------------------------------------------- |
| Trivy               | Vulnerability, container, IaC, and secret scanning |
| Gitleaks            | Secret detection                                   |
| SonarQube           | Code quality and security analysis                 |
| OWASP ZAP           | Dynamic application security testing               |
| Dependency scanners | Third-party dependency vulnerabilities             |

The exact tools used will depend on the organization's requirements and architecture.

---

# Trivy Is a Scanner, Not a Firewall

It is important to understand what Trivy does and does not do.

Trivy is primarily a **security scanning tool**.

It does not replace:

* Firewalls
* Security groups
* Network ACLs
* IAM policies
* Endpoint protection
* Intrusion detection systems
* Runtime security controls

Think of the difference this way:

```text
Firewall
    |
    +-- Controls network traffic

IAM
    |
    +-- Controls access to resources

Trivy
    |
    +-- Scans software, images, configurations,
        dependencies, and other supported artifacts
```

Trivy is therefore one component of a broader security strategy.

---

# Learning Exercises

After installing Trivy, complete the following exercises.

## Exercise 1: Check the Trivy Version

```bash
trivy --version
```

Confirm that Trivy is installed correctly.

---

## Exercise 2: Scan an NGINX Image

```bash
trivy image nginx:latest
```

Review the vulnerabilities reported by Trivy.

Pay attention to:

* Vulnerability ID
* Package
* Installed version
* Fixed version
* Severity

---

## Exercise 3: Show Only HIGH and CRITICAL Vulnerabilities

```bash
trivy image --severity HIGH,CRITICAL nginx:latest
```

Compare the output with the previous scan.

---

## Exercise 4: Scan Your Project

Navigate to your project directory and run:

```bash
trivy fs .
```

Review the vulnerabilities found in your project dependencies.

---

## Exercise 5: Scan Infrastructure-as-Code

Run:

```bash
trivy config .
```

Review any configuration or infrastructure security issues identified by Trivy.

---

## Exercise 6: Scan for Secrets

Run:

```bash
trivy fs --scanners secret .
```

Check whether your project contains potentially exposed secrets.

---

## Exercise 7: Use Trivy as a Security Gate

Run:

```bash
trivy image --exit-code 1 --severity HIGH,CRITICAL nginx:latest
```

Observe the exit code returned by the command.

This demonstrates how Trivy can be used to stop a CI/CD pipeline when serious vulnerabilities are detected.

---

# Conclusion

In this guide, you learned how to:

* Understand what Trivy is
* Understand the role of Trivy in DevSecOps
* Install Trivy on an Ubuntu EC2 instance
* Verify the Trivy installation
* Scan Docker images
* Scan file systems
* Scan Infrastructure-as-Code
* Scan Dockerfiles
* Detect potentially exposed secrets
* Filter vulnerabilities by severity
* Use Trivy as a CI/CD security gate
* Integrate Trivy with GitHub Actions

The main DevSecOps principle to remember is:

> **Security should be integrated into the software delivery lifecycle rather than treated as an afterthought.**

Trivy helps implement this principle by automating security scanning and allowing teams to identify vulnerabilities before software and infrastructure reach production.

---

# Next Step

A good next step is to integrate Trivy into your existing **GitHub Actions CI/CD pipeline**.

The goal would be to create a pipeline such as:

```text
Code Push
    |
    v
Checkout
    |
    v
Install Dependencies
    |
    v
Run Tests
    |
    v
Build Application
    |
    v
Build Docker Image
    |
    v
Trivy Scan
    |
    +---- Security Issues ----> Fail Pipeline
    |
    v
Push Image to Registry
    |
    v
Deploy
```

This turns Trivy from a tool you run manually into an automated security control within your DevSecOps pipeline.

---
# Trivy Practical Vulnerability Scanning Lab

This section provides a practical Trivy laboratory environment containing intentionally vulnerable files and configurations.

The purpose of this lab is to generate meaningful Trivy findings across different scanner types rather than scanning an empty or unsupported file.

The lab contains:

* Vulnerable application dependencies
* A vulnerable Dockerfile
* Fake AWS credentials for secret scanning
* Fake GitHub-style tokens
* Terraform misconfigurations
* Kubernetes misconfigurations
* CloudFormation misconfigurations
* Configuration files containing insecure settings
* License-testing files
* A multi-scanner project for combined scanning
* CI/CD security-gate examples

> **Security Warning:** This laboratory is intentionally insecure. Use it only in a disposable training directory or lab environment. Never use the credentials in this example as real credentials.

---

# Create the Trivy Lab

Create a new directory:

```bash
mkdir -p ~/trivy-security-lab
cd ~/trivy-security-lab
```

Create the following directory structure:

```text
trivy-security-lab/
├── app/
│   ├── package.json
│   ├── requirements.txt
│   └── .env
├── secrets/
│   ├── aws-credentials.txt
│   ├── application.env
│   └── deployment.yaml
├── docker/
│   └── Dockerfile
├── terraform/
│   └── main.tf
├── kubernetes/
│   └── deployment.yaml
├── cloudformation/
│   └── insecure-stack.yaml
├── config/
│   ├── nginx.conf
│   └── application.yaml
├── licenses/
│   └── THIRD-PARTY-LICENSE.txt
└── README.md
```

You can create the directories with:

```bash
mkdir -p app secrets docker terraform kubernetes cloudformation config licenses
```

---

# 1. Vulnerable Node.js Application

Create:

```bash
nano app/package.json
```

Add:

```json
{
  "name": "trivy-vulnerable-demo",
  "version": "1.0.0",
  "description": "Intentionally vulnerable Node.js application for Trivy training",
  "private": true,
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "4.17.1",
    "lodash": "4.17.15",
    "axios": "0.21.1",
    "minimist": "1.2.0",
    "handlebars": "4.5.3",
    "jsonwebtoken": "8.5.1",
    "node-fetch": "2.6.0",
    "serialize-javascript": "3.0.0",
    "tar": "4.4.13",
    "underscore": "1.8.3"
  }
}
```

These versions are deliberately old and are included for vulnerability-scanning practice.

However, there is an important point:

**Do not expect Trivy to report vulnerabilities from this file alone.**

For Node.js dependency scanning, Trivy works particularly well when dependency lock files such as `package-lock.json` are available.

---

# 2. Generate package-lock.json

Install Node.js and npm if they are not already installed:

```bash
sudo apt-get update
sudo apt-get install -y nodejs npm
```

Move into the application directory:

```bash
cd ~/trivy-security-lab/app
```

Generate the dependency lock file:

```bash
npm install --package-lock-only
```

Check the files:

```bash
ls -la
```

You should now have:

```text
package.json
package-lock.json
```

Now return to the lab directory:

```bash
cd ~/trivy-security-lab
```

Run:

```bash
trivy fs app
```

This time Trivy should be able to identify the Node.js dependency information.

You can specifically run:

```bash
trivy fs --scanners vuln app
```

---

# 3. Scan Only HIGH and CRITICAL Vulnerabilities

Run:

```bash
trivy fs \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  app
```

This is useful for simulating a CI/CD security policy where only serious vulnerabilities block the pipeline.

---

# 4. Create a Python Vulnerable Dependency File

Create:

```bash
nano app/requirements.txt
```

Add:

```text
Django==2.2.0
Flask==0.12.2
requests==2.19.1
urllib3==1.24.1
PyYAML==5.1
Jinja2==2.10
Pillow==6.2.0
cryptography==2.8
paramiko==2.4.2
SQLAlchemy==1.2.0
```

These versions are intentionally outdated for laboratory purposes.

Run:

```bash
trivy fs --scanners vuln app
```

You can also focus on serious findings:

```bash
trivy fs \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  app
```

---

# 5. Create a Fake Secrets File

Now we will deliberately create files containing **fake credentials**.

These credentials are not real AWS credentials.

Create:

```bash
nano secrets/aws-credentials.txt
```

Add:

```text
# ============================================================
# TRIVY SECRET SCANNING LAB
# THESE ARE FAKE TRAINING CREDENTIALS
# DO NOT USE THEM
# ============================================================

AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1

AWS_ACCOUNT_ID=123456789012

DATABASE_USERNAME=admin
DATABASE_PASSWORD=TrivyTrainingPassword123!

API_KEY=trivy-demo-api-key-123456789
APPLICATION_SECRET=training-secret-value-123456789
```

The AWS values above are intentionally example values and should never be used as credentials.

Trivy includes built-in secret-detection rules for things such as AWS access keys, GCP service accounts, GitHub tokens, GitLab tokens, and Slack tokens.

---

# 6. Create an Application Environment File

Create:

```bash
nano secrets/application.env
```

Add:

```text
# Intentionally insecure training configuration

APP_ENV=production

DB_HOST=database.internal
DB_PORT=5432
DB_NAME=production
DB_USER=admin
DB_PASSWORD=SuperSecretTrainingPassword123

REDIS_PASSWORD=RedisTrainingPassword123

AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

STRIPE_SECRET_KEY=sk_test_51TrainingOnlyExample
JWT_SECRET=training-jwt-secret-change-me

GITHUB_TOKEN=ghp_example_training_token_123456789
SLACK_TOKEN=xoxb-training-example-token

INTERNAL_API_KEY=internal-training-api-key-123456789
```

Run:

```bash
trivy fs --scanners secret secrets
```

---

# 7. Scan the Entire Lab for Secrets

From:

```bash
cd ~/trivy-security-lab
```

run:

```bash
trivy fs --scanners secret .
```

You should now have several plaintext files for Trivy's secret scanner to inspect.

Trivy's secret scanner scans plaintext files using built-in rules and can identify several types of exposed credentials and keys.

---

# 8. Create an Intentionally Insecure Dockerfile

Create:

```bash
nano docker/Dockerfile
```

Add:

```dockerfile
# ============================================================
# INTENTIONALLY INSECURE DOCKERFILE
# FOR TRIVY TRAINING ONLY
# ============================================================

FROM ubuntu:latest

# Running package installation without pinning versions
RUN apt-get update

# Install unnecessary packages
RUN apt-get install -y \
    curl \
    wget \
    sudo \
    netcat \
    vim

# Store credentials directly inside the image
ENV AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
ENV AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

ENV DATABASE_PASSWORD=SuperSecretTrainingPassword123

# Create an unnecessary privileged user
RUN useradd -m devops

# Grant excessive sudo privileges
RUN echo "devops ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy everything into the image
COPY . /app

WORKDIR /app

# Run application as root
USER root

# Expose an arbitrary application port
EXPOSE 8080

# Insecure shell command
CMD ["bash"]
```

Now scan it:

```bash
trivy config docker/Dockerfile
```

Trivy's configuration scanner supports Dockerfiles and other Infrastructure-as-Code formats.

---

# 9. Scan the Dockerfile Using Filesystem Scanning

You can also scan the entire directory:

```bash
trivy fs \
  --scanners misconfig,secret \
  docker
```

This demonstrates an important difference:

```text
trivy config
        |
        +-- Primarily configuration/IaC scanning

trivy fs
        |
        +-- Can combine vulnerability,
            misconfiguration and secret scanning
```

Trivy allows filesystem scanning to use multiple scanners simultaneously.

---

# 10. Create an Insecure Terraform Configuration

Create:

```bash
nano terraform/main.tf
```

Add:

```hcl
# ============================================================
# INTENTIONALLY INSECURE TERRAFORM
# FOR TRIVY TRAINING ONLY
# ============================================================

terraform {
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = "us-east-1"
}

# ------------------------------------------------------------
# Insecure S3 bucket
# ------------------------------------------------------------

resource "aws_s3_bucket" "training_bucket" {
  bucket = "trivy-training-insecure-bucket"

  tags = {
    Environment = "production"
    Purpose     = "security-training"
  }
}

# ------------------------------------------------------------
# Public bucket ACL
# ------------------------------------------------------------

resource "aws_s3_bucket_acl" "training_acl" {
  bucket = aws_s3_bucket.training_bucket.id

  acl = "public-read"
}

# ------------------------------------------------------------
# Insecure security group
# ------------------------------------------------------------

resource "aws_security_group" "training_sg" {
  name        = "trivy-insecure-security-group"
  description = "Intentionally insecure security group"

  ingress {
    description = "Allow SSH from anywhere"

    from_port = 22
    to_port   = 22
    protocol  = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    description = "Allow HTTP from anywhere"

    from_port = 80
    to_port   = 80
    protocol  = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  ingress {
    description = "Allow database access from anywhere"

    from_port = 3306
    to_port   = 3306
    protocol  = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ------------------------------------------------------------
# IAM policy with excessive permissions
# ------------------------------------------------------------

resource "aws_iam_policy" "insecure_policy" {
  name = "trivy-training-insecure-policy"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = "*"

        Resource = "*"
      }
    ]
  })
}

# ------------------------------------------------------------
# Hard-coded credentials for training
# ------------------------------------------------------------

variable "database_password" {
  default = "SuperSecretTrainingPassword123"
}

variable "api_key" {
  default = "trivy-training-api-key-123456789"
}
```

Do **not** deploy this Terraform configuration.

It is deliberately designed to contain multiple security problems for scanning.

---

# 11. Scan Terraform

Run:

```bash
trivy config terraform
```

You can also specify the scanner explicitly:

```bash
trivy fs \
  --scanners misconfig,secret \
  terraform
```

Trivy supports Terraform as one of its Infrastructure-as-Code misconfiguration scanners.

---

# 12. Create an Insecure Kubernetes Deployment

Create:

```bash
nano kubernetes/deployment.yaml
```

Add:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: trivy-insecure-app

  labels:
    app: trivy-insecure-app

spec:

  replicas: 1

  selector:
    matchLabels:
      app: trivy-insecure-app

  template:

    metadata:
      labels:
        app: trivy-insecure-app

    spec:

      hostNetwork: true

      hostPID: true

      hostIPC: true

      containers:

        - name: insecure-app

          image: nginx:latest

          securityContext:

            privileged: true

            allowPrivilegeEscalation: true

            runAsUser: 0

            runAsGroup: 0

            readOnlyRootFilesystem: false

          ports:

            - containerPort: 80

          env:

            - name: DATABASE_PASSWORD
              value: "SuperSecretTrainingPassword123"

            - name: AWS_ACCESS_KEY_ID
              value: "AKIAIOSFODNN7EXAMPLE"

            - name: AWS_SECRET_ACCESS_KEY
              value: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

          resources:

            requests:

              cpu: "10m"

            limits:

              cpu: "4"

              memory: "4Gi"

---

apiVersion: v1

kind: Service

metadata:

  name: trivy-insecure-service

spec:

  type: LoadBalancer

  selector:

    app: trivy-insecure-app

  ports:

    - protocol: TCP

      port: 80

      targetPort: 80
```

Do not apply this manifest to a real Kubernetes cluster.

---

# 13. Scan Kubernetes Configuration

Run:

```bash
trivy config kubernetes
```

You can also run:

```bash
trivy fs \
  --scanners misconfig,secret \
  kubernetes
```

Trivy's misconfiguration scanner supports Kubernetes configuration files.

---

# 14. Create an Insecure CloudFormation Template

Create:

```bash
nano cloudformation/insecure-stack.yaml
```

Add:

```yaml
AWSTemplateFormatVersion: '2010-09-09'

Description: >
  Intentionally insecure CloudFormation template
  for Trivy security scanning training.

Resources:

  PublicSecurityGroup:

    Type: AWS::EC2::SecurityGroup

    Properties:

      GroupDescription: Insecure security group for Trivy training

      SecurityGroupIngress:

        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          CidrIp: 0.0.0.0/0

  PublicBucket:

    Type: AWS::S3::Bucket

    Properties:

      AccessControl: PublicRead

      BucketName: trivy-training-public-bucket

      Tags:

        - Key: Environment
          Value: production

  InsecureInstance:

    Type: AWS::EC2::Instance

    Properties:

      InstanceType: t2.micro

      ImageId: ami-00000000000000000

      SecurityGroupIds:

        - !Ref PublicSecurityGroup

      UserData:

        Fn::Base64: !Sub |

          #!/bin/bash

          export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE

          export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

          export DATABASE_PASSWORD=SuperSecretTrainingPassword123

          echo "Training application started"
```

This file is intentionally insecure and contains a placeholder AMI ID.

**Do not deploy it.**

---

# 15. Scan CloudFormation

Run:

```bash
trivy config cloudformation
```

Or:

```bash
trivy fs \
  --scanners misconfig,secret \
  cloudformation
```

Trivy's misconfiguration scanner supports CloudFormation templates.

---

# 16. Create an Insecure Application Configuration

Create:

```bash
nano config/application.yaml
```

Add:

```yaml
application:

  name: insecure-training-application

  environment: production

  debug: true

  logging:
    level: DEBUG

  database:

    host: database.internal

    port: 5432

    username: admin

    password: SuperSecretTrainingPassword123

    ssl: false

  redis:

    host: redis.internal

    password: RedisTrainingPassword123

    tls: false

  security:

    authentication: false

    authorization: false

    csrf_protection: false

    session_secure: false

    session_http_only: false

  api:

    api_key: trivy-training-api-key-123456789

    allow_origins:
      - "*"

  aws:

    access_key_id: AKIAIOSFODNN7EXAMPLE

    secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

    region: us-east-1
```

Scan it:

```bash
trivy fs --scanners secret config
```

---

# 17. Create an NGINX Configuration

Create:

```bash
nano config/nginx.conf
```

Add:

```nginx
# ============================================================
# INTENTIONALLY INSECURE NGINX CONFIGURATION
# FOR TRIVY TRAINING
# ============================================================

user root;

worker_processes 1;

events {
    worker_connections 1024;
}

http {

    server {

        listen 80;

        server_name _;

        # Directory listing enabled
        autoindex on;

        # Proxy requests to an internal service
        location / {

            proxy_pass http://127.0.0.1:8080;

            proxy_set_header Host $host;

            proxy_set_header X-Real-IP $remote_addr;

        }

        # Expose sensitive files
        location /backup {

            alias /var/backups/;

            autoindex on;

        }

        # Debug endpoint
        location /debug {

            return 200 "DEBUG MODE ENABLED";

        }
    }
}
```

Run:

```bash
trivy fs --scanners secret,misconfig config
```

Note that Trivy's built-in misconfiguration coverage is primarily aimed at supported configuration/IaC formats; not every arbitrary application configuration file will produce findings.

---

# 18. License Scanning

Create:

```bash
nano licenses/THIRD-PARTY-LICENSE.txt
```

Add:

```text
THIRD-PARTY SOFTWARE LICENSE INFORMATION

============================================================
Training Dependency A
============================================================

Copyright 2026 Trivy Training Lab

This software is distributed under the GNU General Public
License version 3.

This file is intentionally included for license-scanning
training.

------------------------------------------------------------

GNU GENERAL PUBLIC LICENSE

Version 3, 29 June 2007

Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

This license text is included solely as a laboratory artifact.

============================================================

Training Dependency B
============================================================

License: Apache License 2.0

This component is included as a second license example.

============================================================

Training Dependency C
============================================================

License: MIT

This component is included as a third license example.

============================================================

Training Dependency D
============================================================

License: UNKNOWN

This component intentionally represents an unknown license
classification for training purposes.
```

License scanning is available in Trivy and can be explicitly enabled with `--scanners license`. Full license scanning can additionally inspect source files, Markdown files, text files, and license documents.

Run:

```bash
trivy fs \
  --scanners license \
  licenses
```

For extended scanning:

```bash
trivy fs \
  --scanners license \
  --license-full \
  licenses
```

---

# 19. Scan the Entire Laboratory

Now return to the root directory:

```bash
cd ~/trivy-security-lab
```

Run the normal filesystem scan:

```bash
trivy fs .
```

The default filesystem scan includes vulnerability and secret scanning.

---

# 20. Run All Major Scanners Together

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret,license \
  .
```

This is one of the most useful commands in this laboratory.

The supported scanner types include:

```text
vuln
misconfig
secret
license
```

Trivy's current CLI documentation lists these as the scanner types available to the filesystem and image commands.

---

# 21. Run All Scanners and Show Only HIGH and CRITICAL

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret,license \
  --severity HIGH,CRITICAL \
  .
```

This simulates a security policy where the organization considers HIGH and CRITICAL findings to be pipeline-blocking issues.

---

# 22. Scan Individual Scenarios

Instead of scanning everything at once, test each security category separately.

## Vulnerability Scanning

```bash
trivy fs \
  --scanners vuln \
  app/
```

---

## Secret Scanning

```bash
trivy fs \
  --scanners secret \
  secrets/
```

---

## Terraform Misconfiguration Scanning

```bash
trivy config terraform/
```

---

## Kubernetes Misconfiguration Scanning

```bash
trivy config kubernetes/
```

---

## CloudFormation Misconfiguration Scanning

```bash
trivy config cloudformation/
```

---

## Dockerfile Misconfiguration Scanning

```bash
trivy config docker/
```

---

## License Scanning

```bash
trivy fs \
  --scanners license \
  --license-full \
  licenses/
```

---

# 23. Combine Vulnerability and Secret Scanning

Run:

```bash
trivy fs \
  --scanners vuln,secret \
  .
```

This asks Trivy to look for both dependency vulnerabilities and exposed secrets.

---

# 24. Combine Vulnerability and Misconfiguration Scanning

Run:

```bash
trivy fs \
  --scanners vuln,misconfig \
  .
```

This is useful for projects containing both application dependencies and IaC.

---

# 25. Combine Misconfiguration and Secret Scanning

Run:

```bash
trivy fs \
  --scanners misconfig,secret \
  .
```

This is particularly useful for infrastructure repositories containing:

* Terraform
* Kubernetes
* Dockerfiles
* CloudFormation
* Configuration files
* Environment files

---

# 26. Scan Everything and Save JSON Results

You can save the scan results to a JSON file.

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret,license \
  --format json \
  --output trivy-results.json \
  .
```

Check the file:

```bash
ls -lh trivy-results.json
```

View it:

```bash
less trivy-results.json
```

This is useful for CI/CD systems because JSON results can be consumed by other tools.

---

# 27. Save the Results as SARIF

SARIF is commonly used by security tooling and code-scanning systems.

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --format sarif \
  --output trivy-results.sarif \
  .
```

Check the result:

```bash
ls -lh trivy-results.sarif
```

---

# 28. Generate a Table Report

The default human-readable output is useful when learning.

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --format table \
  .
```

---

# 29. Create a Security Gate

Now simulate a CI/CD security gate.

Run:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  .
```

The important option is:

```text
--exit-code 1
```

If Trivy discovers findings matching the selected severity threshold, the command can return a non-zero exit status.

Check the result:

```bash
echo $?
```

If the security gate failed, you should see:

```text
1
```

If no findings matched the selected threshold, you may see:

```text
0
```

This is the same principle used to make a CI/CD pipeline fail when security requirements are not met.

---

# 30. Demonstrate the Difference Between Scanners

Run these commands separately.

### Vulnerabilities

```bash
trivy fs --scanners vuln app/
```

Question:

> Are vulnerable dependencies present?

---

### Secrets

```bash
trivy fs --scanners secret secrets/
```

Question:

> Are credentials or sensitive values exposed?

---

### Misconfigurations

```bash
trivy config terraform/
```

Question:

> Are infrastructure resources configured insecurely?

---

### License Issues

```bash
trivy fs --scanners license --license-full licenses/
```

Question:

> What licenses are present and how does Trivy classify them?

---

# 31. Scan a Single File

Trivy can also scan a single supported file.

For example:

```bash
trivy config terraform/main.tf
```

Or:

```bash
trivy config kubernetes/deployment.yaml
```

This is useful when troubleshooting a particular configuration file.

---

# 32. Scan Multiple Directories

You can scan the entire project:

```bash
trivy fs .
```

Or scan individual areas:

```bash
trivy fs app/
trivy fs secrets/
trivy fs docker/
trivy fs terraform/
trivy fs kubernetes/
```

This makes it easier to understand which scanner is responsible for each finding.

---

# 33. Why Your Original Test Returned No Vulnerabilities

Your original command was:

```bash
trivy fs .
```

The directory contained:

```text
package.json
```

but did not contain a dependency lock file such as:

```text
package-lock.json
```

Your output showed:

```text
Number of language-specific files: 0
```

and:

```text
Supported files for scanner(s) not found
```

That means Trivy did not find a supported dependency file that it could use for vulnerability analysis.

After generating:

```text
package-lock.json
```

run:

```bash
trivy fs .
```

again.

You should now have a dependency file that Trivy can analyze.

---

# 34. Recommended Lab Sequence

Do not run everything at once initially.

Work through the laboratory in this order.

### Stage 1 — Dependency Vulnerabilities

```bash
trivy fs --scanners vuln app/
```

Learn how Trivy identifies vulnerable packages.

---

### Stage 2 — Secret Scanning

```bash
trivy fs --scanners secret secrets/
```

Learn how Trivy identifies exposed credentials.

---

### Stage 3 — Docker Security

```bash
trivy config docker/
```

Learn how Dockerfile misconfigurations are identified.

---

### Stage 4 — Terraform Security

```bash
trivy config terraform/
```

Learn how IaC security problems are identified.

---

### Stage 5 — Kubernetes Security

```bash
trivy config kubernetes/
```

Learn how Kubernetes configuration problems are identified.

---

### Stage 6 — CloudFormation Security

```bash
trivy config cloudformation/
```

Learn how AWS infrastructure configuration can be scanned.

---

### Stage 7 — License Scanning

```bash
trivy fs \
  --scanners license \
  --license-full \
  licenses/
```

Learn how Trivy analyzes software licenses.

---

### Stage 8 — Full Project Scan

Finally:

```bash
trivy fs \
  --scanners vuln,misconfig,secret,license \
  .
```

---

# 35. Simulate a Real DevSecOps Pipeline

After completing the individual scans, simulate a complete CI/CD security process.

```text
Developer
    |
    v
Git Push
    |
    v
Checkout Source Code
    |
    v
Dependency Installation
    |
    v
Unit Tests
    |
    v
Trivy Vulnerability Scan
    |
    +---- HIGH/CRITICAL ----> FAIL
    |
    v
Build Docker Image
    |
    v
Trivy Image Scan
    |
    +---- HIGH/CRITICAL ----> FAIL
    |
    v
Trivy IaC Scan
    |
    +---- Misconfiguration ----> FAIL
    |
    v
Trivy Secret Scan
    |
    +---- Secret Found ----> FAIL
    |
    v
Push Image
    |
    v
Deploy
```

This demonstrates the principle of **DevSecOps security gates**.

---

# 36. Useful Trivy Command Reference

| Scenario              | Command                                                  |
| --------------------- | -------------------------------------------------------- |
| Check version         | `trivy --version`                                        |
| Basic filesystem scan | `trivy fs .`                                             |
| Vulnerability scan    | `trivy fs --scanners vuln .`                             |
| Secret scan           | `trivy fs --scanners secret .`                           |
| Misconfiguration scan | `trivy fs --scanners misconfig .`                        |
| License scan          | `trivy fs --scanners license .`                          |
| Dockerfile scan       | `trivy config docker/`                                   |
| Terraform scan        | `trivy config terraform/`                                |
| Kubernetes scan       | `trivy config kubernetes/`                               |
| CloudFormation scan   | `trivy config cloudformation/`                           |
| HIGH/CRITICAL only    | `trivy fs --severity HIGH,CRITICAL .`                    |
| All major scanners    | `trivy fs --scanners vuln,misconfig,secret,license .`    |
| JSON report           | `trivy fs --format json --output trivy-results.json .`   |
| SARIF report          | `trivy fs --format sarif --output trivy-results.sarif .` |
| CI/CD security gate   | `trivy fs --severity HIGH,CRITICAL --exit-code 1 .`      |

---

# 37. Important Trivy Concept

Do not assume that:

```bash
trivy fs .
```

means:

> "Scan every possible security problem in every file."

Instead, Trivy uses different scanners for different types of security analysis.

For example:

```text
                    TRIVY
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
   Vulnerability   Secret       Misconfiguration
       |              |              |
       v              v              v
Dependencies      Credentials       IaC
Packages          API Keys          Terraform
CVEs              Tokens            Kubernetes
                  Passwords         Dockerfile
                                    CloudFormation

                      +
                      |
                      v
                  License
                      |
                      v
                License Analysis
```

The current Trivy documentation identifies vulnerability and secret scanning as enabled by default for filesystem scanning, while misconfiguration and license scanning can be explicitly enabled with `--scanners`.

---

# 38. Expected Outcome

By the end of this laboratory, your project should contain multiple categories of findings:

```text
trivy-security-lab/
│
├── Vulnerabilities
│   ├── Node.js dependencies
│   └── Python dependencies
│
├── Secrets
│   ├── Fake AWS credentials
│   ├── Fake API keys
│   └── Fake application passwords
│
├── Docker Misconfigurations
│   ├── Unpinned base image
│   ├── Root user
│   ├── Excessive packages
│   └── Insecure configuration
│
├── Terraform Misconfigurations
│   ├── Public S3 bucket
│   ├── 0.0.0.0/0 ingress
│   ├── Excessive IAM permissions
│   └── Hard-coded secrets
│
├── Kubernetes Misconfigurations
│   ├── Privileged container
│   ├── Root user
│   ├── hostNetwork
│   ├── hostPID
│   └── hostIPC
│
└── CloudFormation Misconfigurations
    ├── Public security group
    ├── Public S3 bucket
    └── Hard-coded credentials
```

The exact number of findings will vary depending on your installed Trivy version, vulnerability database, scanner configuration, and current vulnerability data.

---

# 39. Final Full Scan

Once everything has been created, run:

```bash
cd ~/trivy-security-lab

trivy fs \
  --scanners vuln,misconfig,secret,license \
  --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL \
  .
```

For a CI/CD-style test:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  .
```

For a machine-readable report:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --format json \
  --output trivy-results.json \
  .
```

For a GitHub-compatible SARIF report:

```bash
trivy fs \
  --scanners vuln,misconfig,secret \
  --format sarif \
  --output trivy-results.sarif \
  .
```

---

# What You Should Learn From This Lab

The most important lesson is that **Trivy is not one scanner doing one thing**.

It is a collection of security capabilities that can be applied to different targets.

You should be able to explain the following after completing the lab:

| Question                                 | Answer                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| What does `trivy fs` scan?               | A local filesystem/project                                               |
| What does `trivy image` scan?            | A container image                                                        |
| What does `trivy config` scan?           | Supported IaC/configuration files                                        |
| What does `--scanners vuln` do?          | Enables vulnerability scanning                                           |
| What does `--scanners secret` do?        | Enables secret scanning                                                  |
| What does `--scanners misconfig` do?     | Enables misconfiguration scanning                                        |
| What does `--scanners license` do?       | Enables license scanning                                                 |
| What does `--severity HIGH,CRITICAL` do? | Filters displayed findings by severity                                   |
| What does `--exit-code 1` do?            | Allows findings to cause a non-zero exit status                          |
| Why use `package-lock.json`?             | It gives Trivy dependency information for Node.js vulnerability analysis |
| Why use `trivy config`?                  | To analyze supported Infrastructure-as-Code/configuration files          |
| Why use `--format json`?                 | To produce machine-readable results                                      |
| Why use SARIF?                           | To integrate scan results with security/code-scanning workflows          |

This is the difference between simply knowing how to run:

```bash
trivy fs .
```

and actually understanding how Trivy fits into a DevSecOps pipeline.


## Author

Prepared for AWS, DevOps, and DevSecOps learners.
