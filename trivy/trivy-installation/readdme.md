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

## Author

Prepared for AWS, DevOps, and DevSecOps learners.
