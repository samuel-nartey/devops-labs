AWS DevOps Class Guide
IAM · CLI · SSM · EC2 · Load Balancing
---
Table of Contents
IAM — Users, Groups & Policies
CLI Authentication & Basic Commands
Creating an SSM Role for EC2
Creating 2 EC2 Instances with User Data
Creating the Load Balancer
Testing & Verification
---
1. IAM — Users, Groups & Policies
What is IAM?
Concept	Description
User	A permanent identity for a person or application. Has a password and/or access keys.
Group	A collection of users. Attach a policy once — all users in the group inherit it.
Policy	A JSON document that defines what actions are allowed or denied on which resources.
Role	A temporary identity assumed by AWS services (e.g. EC2, Lambda). No password needed.
> **Best practice:** Never use the root account for daily work. Create IAM users and grant least privilege.
---
1.1 Create an IAM User
Go to AWS Console → IAM → Users → Add users
Enter a username (e.g. `john-devops`)
Select access type:
 Programmatic access — for CLI/API (generates Access Key + Secret)
 AWS Management Console access — for browser login
Set a password (auto-generated or custom)
Click Next: Permissions
Choose Add user to group (recommended) or attach a policy directly
Click through to Create user
Download the `.csv` file — the Secret Access Key is shown only once
---
1.2 Create an IAM Group
Go to IAM → User groups → Create group
Name the group (e.g. `Developers`, `DevOps-Team`)
Attach a managed policy:
`AdministratorAccess` — full access (use sparingly)
`PowerUserAccess` — everything except IAM management
`AmazonEC2FullAccess` — EC2 only
`ReadOnlyAccess` — view everything, change nothing
Click Create group
Go to the group → Users tab → Add users → select your IAM users
---
1.3 IAM Policy Structure
A policy is a JSON document with this structure:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```
Field	Description	Example Values
`Effect`	Allow or block the action	`Allow` / `Deny`
`Action`	The AWS API calls permitted	`ec2:*`, `s3:GetObject`
`Resource`	Which ARN(s) the action applies to	`arn:aws:s3:::my-bucket/*`
`Condition`	Optional extra conditions	IP range, MFA required
---
2. CLI Authentication & Basic Commands
2.1 Install the AWS CLI
macOS:
```bash
brew install awscli
```
Linux (Ubuntu/Debian):
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```
Windows:
Download the `.msi` installer from https://aws.amazon.com/cli/ and run it.
---
2.2 Configure Authentication
You need the Access Key ID and Secret Access Key from the `.csv` you downloaded when creating the IAM user.
```bash
aws configure
```
You will be prompted for:
```
AWS Access Key ID [None]:     AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]:   us-east-1
Default output format [None]: json
```
---
2.3 Verify Your Identity
```bash
aws sts get-caller-identity
```
Expected output:
```json
{
    "UserId":  "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn":     "arn:aws:iam::123456789012:user/john-devops"
}
```
---
2.4 Using Named Profiles (Multiple Accounts)
```bash
# Set up separate profiles
aws configure --profile dev
aws configure --profile prod

# Use a specific profile per command
aws s3 ls --profile dev

# Or set as default for the terminal session
export AWS_PROFILE=dev
```
---
2.5 Basic CLI Commands
Command	What It Does
`aws sts get-caller-identity`	Show who you're authenticated as
`aws iam list-users`	List all IAM users
`aws iam list-groups`	List all IAM groups
`aws ec2 describe-instances`	List all EC2 instances
`aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"`	List only running instances
`aws ec2 start-instances --instance-ids i-0abc123`	Start a stopped instance
`aws ec2 stop-instances --instance-ids i-0abc123`	Stop a running instance
`aws ec2 describe-regions`	List all AWS regions
`aws s3 ls`	List all S3 buckets
`aws s3 cp file.txt s3://my-bucket/`	Upload a file to S3
`aws help`	Show all CLI commands
---
3. Creating an SSM Role for EC2
Why SSM?
AWS Session Manager lets you connect to EC2 instances securely through the browser or CLI — no SSH key pairs, no open port 22, no bastion host required.
---
3.1 Create the IAM Role
Go to IAM → Roles → Create role
Under Trusted entity type, select AWS service
Under Use case, select EC2 → click Next
In the permissions search box, search for and select:
 `AmazonSSMManagedInstanceCore`
Click Next
Role name: `EC2-SSM-Role`
Description: `Allows EC2 instances to use AWS Systems Manager`
Click Create role
> `AmazonSSMManagedInstanceCore` gives the instance permission to register with SSM, stream session data, and receive commands — all without opening any inbound ports.
---
3.2 Attach the Role During EC2 Launch (Advanced Details)
When launching a new EC2 instance:
Fill in the instance name, AMI, and instance type as normal
Scroll down to the Advanced details section (at the bottom of the launch wizard)
Find IAM instance profile → select `EC2-SSM-Role`
In Key pair (login), select Proceed without a key pair — SSM handles access
In Security Group, you do NOT need to open port 22 (SSH)
Launch the instance
---
3.3 Connect to an Instance via SSM
From the Console:
```
EC2 → Instances → Select instance → Connect → Session Manager tab → Connect
```
A terminal opens directly in your browser.
From the CLI:
```bash
aws ssm start-session --target i-0abc1234567890def
```
---
4. Creating 2 EC2 Instances with User Data
Goal: Each instance serves a different HTML page. When the load balancer distributes traffic, refreshing the browser shows which instance you're hitting.
---
4.1 Launch Instance A — "WebServer-A"
Step 1 — Configure:
Name: `WebServer-A`
AMI: Amazon Linux 2023
Instance type: `t2.micro` (free tier)
Key pair: Proceed without a key pair
Security Group: Allow inbound HTTP (port 80) from `0.0.0.0/0`
Advanced details → IAM instance profile: `EC2-SSM-Role`
Step 2 — Paste this into "User data" (Advanced details, scroll to the bottom):
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# Get the private IP dynamically
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

cat > /var/www/html/index.html <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Instance A</title>
  <style>
    body { font-family: Arial, sans-serif; background: #e8f5e9;
           display: flex; align-items: center; justify-content: center;
           height: 100vh; margin: 0; }
    .card { background: white; border-radius: 12px; padding: 3rem 4rem;
            text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }
    h1 { color: #2e7d32; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .badge { background: #2e7d32; color: white; padding: 6px 20px;
             border-radius: 20px; font-size: 0.9rem; display: inline-block; margin: 1rem 0; }
    p { color: #555; margin-top: 0.8rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🟢 Instance A</h1>
    <div class="badge">WebServer-A</div>
    <p>You are connected to <strong>Instance A</strong></p>
    <p>Private IP: <strong>${PRIVATE_IP}</strong></p>
    <p style="margin-top:2rem;color:#aaa;font-size:0.85rem">
      Refresh the page to see load balancing in action!
    </p>
  </div>
</body>
</html>
EOF
```
Click Launch instance.
---
4.2 Launch Instance B — "WebServer-B"
Repeat the same steps above with these differences:
Name: `WebServer-B`
Availability Zone: use a different AZ from Instance A (e.g. `us-east-1b` vs `us-east-1a`) for high availability
User data: paste the script below instead
```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

# Get the private IP dynamically
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

cat > /var/www/html/index.html <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Instance B</title>
  <style>
    body { font-family: Arial, sans-serif; background: #e3f2fd;
           display: flex; align-items: center; justify-content: center;
           height: 100vh; margin: 0; }
    .card { background: white; border-radius: 12px; padding: 3rem 4rem;
            text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }
    h1 { color: #1565c0; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .badge { background: #1565c0; color: white; padding: 6px 20px;
             border-radius: 20px; font-size: 0.9rem; display: inline-block; margin: 1rem 0; }
    p { color: #555; margin-top: 0.8rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🔵 Instance B</h1>
    <div class="badge">WebServer-B</div>
    <p>You are connected to <strong>Instance B</strong></p>
    <p>Private IP: <strong>${PRIVATE_IP}</strong></p>
    <p style="margin-top:2rem;color:#aaa;font-size:0.85rem">
      Refresh the page to see load balancing in action!
    </p>
  </div>
</body>
</html>
EOF
```
Click Launch instance.
> **Important:** Both instances must be in the **same VPC** and have **HTTP port 80** open in their Security Group.
---
5. Creating the Load Balancer
Architecture
```
Internet (User's Browser)
         |
         ▼
Application Load Balancer (ALB)
         |
    _____|_____
   |           |
   ▼           ▼
WebServer-A  WebServer-B
(AZ: 1a)     (AZ: 1b)
```
The ALB distributes traffic using round-robin — each refresh hits the next instance in turn.
---
5.1 Create a Target Group
A Target Group tells the ALB which instances to send traffic to.
Go to EC2 → Target Groups → Create target group
Target type: Instances
Target group name: `web-servers-tg`
Protocol: HTTP | Port: 80
VPC: select the same VPC as your instances
Health check settings:
Protocol: HTTP
Path: `/`
Healthy threshold: `2`
Unhealthy threshold: `2`
Interval: `30 seconds`
Click Next
In Register targets, select both `WebServer-A` and `WebServer-B`
Click Include as pending below → Create target group
---
5.2 Create the Application Load Balancer
Go to EC2 → Load Balancers → Create load balancer
Choose Application Load Balancer → click Create
Load balancer name: `web-alb`
Scheme: Internet-facing
IP address type: IPv4
Network mapping:
Select your VPC
Select at least 2 Availability Zones (the ones your instances are in)
Select a public subnet in each AZ
Security groups:
Create or select a Security Group that allows inbound HTTP (port 80) from `0.0.0.0/0`
This is the SG for the ALB itself (separate from the EC2 instances' SG)
Listeners and routing:
Listener: HTTP : 80
Default action: Forward to → select `web-servers-tg`
Click Create load balancer
Wait 2–3 minutes for status to change from `provisioning` → `active`
Copy the DNS name from the ALB description tab — it looks like:
    ```
    web-alb-123456789.us-east-1.elb.amazonaws.com
    ```
> **Security tip:** Update the EC2 instances' Security Group to allow port 80 **only from the ALB's Security Group** (not from 0.0.0.0/0). This forces all traffic through the load balancer.
---
6. Testing & Verification
6.1 Test in the Browser
Copy the ALB DNS name from Step 5.2
Open it in a browser: `http://web-alb-123456789.us-east-1.elb.amazonaws.com`
You should see either the green Instance A page or the blue Instance B page
Refresh the page — the ALB will round-robin between instances, so you'll alternate between them
Instance A page shows:
```
🟢 Instance A
WebServer-A
You are connected to Instance A
Private IP: 10.0.1.45
```
Instance B page shows:
```
🔵 Instance B
WebServer-B
You are connected to Instance B
Private IP: 10.0.2.78
```
---
6.2 Check Target Group Health
Before testing the browser, confirm both targets are healthy in the console:
```
EC2 → Target Groups → web-servers-tg → Targets tab
```
Both instances should show status: healthy
Via CLI:
```bash
aws elbv2 describe-target-health \
    --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456:targetgroup/web-servers-tg/abc
```
---
6.3 Useful Verification Commands
```bash
# List all load balancers
aws elbv2 describe-load-balancers

# Get the ALB DNS name
aws elbv2 describe-load-balancers \
    --query "LoadBalancers[*].DNSName" \
    --output table

# Connect to Instance A via SSM to test Apache locally
aws ssm start-session --target i-0INSTANCE_A_ID

# Inside the SSM session, run:
curl localhost
# Should return your HTML page
```
---
6.4 Troubleshooting
Problem	Likely Cause	Fix
Targets show unhealthy	Apache not running / SG blocking port 80	SSM into instance, run `systemctl status httpd`
Only one instance shows	Browser caching	Open in incognito or disable cache (`Ctrl+Shift+R`)
ALB DNS gives no response	ALB still provisioning	Wait 3–5 min, ALB needs to become `active`
SSM connection fails	SSM role not attached / SSM agent not running	Verify `EC2-SSM-Role` is in the IAM instance profile
User data didn't run	Script error	SSM in, check `/var/log/cloud-init-output.log`
---
Full Checklist
#	Task	Section
1	Create IAM User with programmatic access	§1.1
2	Create IAM Group and attach a policy	§1.2
3	Add user to group	§1.2
4	Install AWS CLI	§2.1
5	Run `aws configure` with your access keys	§2.2
6	Verify with `aws sts get-caller-identity`	§2.3
7	Create `EC2-SSM-Role` with `AmazonSSMManagedInstanceCore`	§3.1
8	Launch WebServer-A with user data + SSM role	§4.1
9	Launch WebServer-B with user data + SSM role	§4.2
10	Verify both instances serve HTTP on port 80 via SSM	§6.3
11	Create Target Group `web-servers-tg` with both instances	§5.1
12	Create Application Load Balancer `web-alb`	§5.2
13	Confirm both targets are healthy in Target Group	§6.2
14	Open ALB DNS in browser and refresh to see both instances	§6.1
---
AWS DevOps Class — Follow sections in order. Each section builds on the previous one.
