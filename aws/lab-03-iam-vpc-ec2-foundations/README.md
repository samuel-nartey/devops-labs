# AWS Hands-On Lab Guide
### Team Presentation -- Sunday, May 24, 2026

---

> "DO HARD THINGS."
>
> Every concept you struggle with today is a concept you own forever. If something breaks, if something does not work the way you expected, do not skip it. Document what happened, form a hypothesis, test it, and write it down. That is not failure. That is engineering.

---

## Presentation Rules and Assessment Structure

**Every group has 15 minutes to present.**

The 15 minutes must be used as follows:

- 5 minutes: Live demonstration of your assigned lab scenario in the AWS console. The assessor will watch you navigate and execute, not just explain.
- 5 minutes: Conceptual walkthrough. Explain what is happening behind the scenes at each step. Do not just read the steps. Explain why each step exists.
- 5 minutes: Reserved for the group task (described at the end of this guide).

**Individual quiz:**
Each member of the group will be asked one practical question. You have 2 minutes to respond. Your response must include a conceptual explanation and, where possible, a live demonstration in the console or terminal. Marks are awarded for dexterity (can you actually do it?), depth (do you understand why it works?), and clarity (can you explain it to someone who has never seen it?).

**Group task:**
Each group receives one task at the start of the presentation session. The task will require applying concepts from across the labs, not just one. It will be something that cannot be rehearsed because it combines concepts in a new way. You will have time during the 15 minutes to attempt it.

**Challenge documentation:**
If your group encounters a problem during the lab or during the presentation, document it. Write down what you expected to happen, what actually happened, the error message or behavior you observed, the steps you took to investigate, and the resolution or the current status if unresolved. Groups that document challenges well are demonstrating exactly the mindset that this lab is designed to build.

---

## What You Are Expected to Present

Each group is assigned one primary lab. However, all members of all groups are expected to understand all labs because the individual quiz questions are drawn from the full lab guide, not just your group's lab.

**Group 1:** Lab 1 -- IAM, Users, Groups, Effective Permissions, Permission Boundaries

**Group 2:** Lab 2 -- AWS Organizations (Challenge Lab)

**Group 3:** Lab 3 -- EC2 Bootstrapping, AMI, and Load Balancing

**Group 4:** Lab 4 -- VPC Peering, Flow Logs, Security Groups, NACLs, Ephemeral Ports

---

## Before You Start -- Mental Models That Will Save You

AWS is abstract. The services have names that do not always explain what they do. Before touching the console, internalize these analogies. They will appear again and again throughout the labs.

Think of an AWS account as a company office building.

| Real World Concept | AWS Equivalent |
|---|---|
| The company itself | AWS Account |
| Parent company owning many offices | AWS Organizations |
| An employee's badge and identity | IAM User |
| A department's access rules | IAM Group Policy |
| A legal cap on what a junior employee can do | Permission Boundary |
| Head office policy that all branches must follow | Service Control Policy (SCP) |
| A server room in the building | EC2 Instance |
| The reception desk routing incoming calls | Load Balancer |
| The building's private internal floor plan | VPC |
| A door lock on one specific office | Security Group |
| The building-wide visitor access list | Network ACL (NACL) |
| A photograph of a room at a specific moment | AMI (Amazon Machine Image) |
| A corridor connecting two buildings privately | VPC Peering |
| Security camera footage of all movement | VPC Flow Logs |

---

## Challenge Documentation Template

When something does not work as expected, copy this format and fill it in. Paste it at the end of your lab notes or on a shared document your group can see.

```
CHALLENGE LOG

Date and time: 
Who encountered it: 
Lab section: 
Step number: 

What I expected to happen:

What actually happened (include error messages exactly as shown):

What I tried:
  1.
  2.
  3.

What I found:

Current status: [ ] Resolved  [ ] Unresolved
Resolution (if resolved):
Lesson learned:
```

---
---

# LAB 1 -- IAM: Users, Groups, Effective Permissions, and Permission Boundaries

## Objectives

- Create 3 IAM users inside a group named CloudOpsTeam
- Attach group-level policies to control what the group can do
- Demonstrate effective permissions where a group deny overrides a user allow
- Demonstrate a permission boundary that caps what a user can ever do regardless of their policies

---

## Curiosity Gap -- Before You Read Any Further

Before this section gives you any explanations, think about these two scenarios and form your own answer. Write it down. You will check it against reality when you run the simulation.

**Scenario A:** Alice has a personal policy that says she is allowed to delete S3 objects. Her group also has a policy that says nobody in the group is allowed to delete S3 objects. Who wins?

**Scenario B:** Bob has a policy attached to him that says he can do everything in AWS, every single action. But a permission boundary has been attached to him that only allows S3 read access. What can Bob actually do?

Hold your answers. The lab will confirm or correct them.

---

## Concept: What is IAM?

Identity and Access Management is the gatekeeper of your entire AWS account. It answers three questions every time any action is attempted:

- Who is making the request? (Authentication)
- What are they asking to do? (The action)
- Are they allowed to do it? (Authorization)

IAM does not care about network traffic or servers. It is purely about identity and what that identity is permitted to do.

There are three core building blocks:

**IAM User:** A permanent identity representing a person or an application. It has credentials (a password for console access or access keys for programmatic access). It is not deleted when you log out. It exists until you delete it.

**IAM Group:** A container for users. You attach policies to the group, and every user inside that group inherits those policies. If you have 30 developers who all need the same access, you attach the policy once to the group rather than 30 times to each user. Adding a new developer is as simple as adding them to the group.

**IAM Policy:** A JSON document that defines what is allowed or denied. It specifies three things: Effect (Allow or Deny), Action (what AWS operation, like s3:DeleteObject), and Resource (which AWS resource the action applies to, like a specific S3 bucket or all resources using an asterisk).

---

## Step-by-Step Instructions

### Step 1: Sign in to the AWS Console

1. Open your browser and go to https://console.aws.amazon.com
2. Sign in with an account that has administrative access. For this lab, do not use the root user for actual resource creation. Use an IAM admin user if you have one.
3. In the top search bar, type IAM and select it from the dropdown.

---

### Step 2: Create the IAM Group -- CloudOpsTeam

A group defines a job role's permissions. You are creating a group for a cloud operations team that should only be able to read, not modify or delete anything.

1. In the IAM left sidebar, click "User groups"
2. Click "Create group"
3. Group name: CloudOpsTeam
4. Under "Attach permissions policies", search for and select:
   - AmazonS3ReadOnlyAccess (allows listing and reading S3 buckets and objects)
   - AmazonEC2ReadOnlyAccess (allows describing and viewing EC2 resources)
5. Click "Create user group"

**Why read-only?** The group represents the baseline access for this team. Individual users may be granted more through their own policies, but we want to see what happens when the group's rules conflict with a user's rules. That is the entire point of the next few steps.

---

### Step 3: Create 3 IAM Users

#### User 1: alice-ops

1. In IAM, click "Users" then "Add users"
2. Username: alice-ops
3. Check "Provide user access to the AWS Management Console"
4. Select "I want to create an IAM user"
5. Set a custom password, for example: AliceOps2026!
6. Uncheck "User must create a new password at next sign-in" (this makes the lab easier to simulate)
7. Click "Next"
8. Under "Add user to group", select CloudOpsTeam
9. Click "Next" then "Create user"
10. On the confirmation screen, copy or download the console sign-in URL. You will need it.

Repeat this process for:
- bob-ops (add to CloudOpsTeam)
- charlie-ops (add to CloudOpsTeam)

---

### Step 4: Give alice-ops an Inline Policy for S3 Write Access

This is where the effective permissions experiment begins. Alice will have a personal policy that grants her more access than the group allows.

1. In IAM, click "Users" then click alice-ops
2. Click the "Permissions" tab
3. Click "Add permissions" then "Create inline policy"
4. Click the "JSON" tab and paste the following:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:DeleteObject",
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "*"
    }
  ]
}
```

5. Click "Next"
6. Name the policy: alice-s3-extended
7. Click "Create policy"

Alice now has two sources of permission. Her group gives her S3 read-only access. Her personal policy gives her S3 read, write, and delete access. Before you run the simulation, revisit your answer to Scenario A.

---

### Observation Checkpoint -- After Step 4

Stop here. Open a new incognito or private browser window. Sign in to the IAM console sign-in URL using alice-ops credentials. Navigate to S3. Try to create a bucket. Try to upload a file. Try to delete an object from an existing bucket (if you have one), or note what options appear to be available.

**Write down what you observe.** Then come back and continue.

**Questions to answer from your observation:**

1. Could alice-ops delete an object? If yes, why? If no, why not?
2. Did anything surprise you about what was available or not available in the console?
3. The group has AmazonS3ReadOnlyAccess. That policy does not explicitly deny anything -- it just does not include write permissions. So if the group does not deny writes but also does not allow them, and Alice's personal policy allows writes, what do you think will happen? Was your prediction correct?

---

### Step 5: Add an Explicit Group Deny for S3 Delete

Now we escalate the experiment. We will add an explicit Deny to the group. Previously the group simply did not grant delete access. Now the group will actively deny it.

1. Go to "User groups" then click CloudOpsTeam
2. Click the "Permissions" tab
3. Click "Add permissions" then "Create inline policy"
4. Paste the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteBucket"
      ],
      "Resource": "*"
    }
  ]
}
```

5. Name it: cloudops-deny-s3-delete
6. Click "Create policy"

**Now simulate as alice-ops again.** Sign in using the incognito window. Try to delete an S3 object.

---

### Observation Checkpoint -- After Step 5

**Questions to answer:**

1. Before this step, could alice-ops delete objects? After adding the group deny, can she?
2. You have now seen two different situations: one where the group simply does not grant a permission, and one where the group explicitly denies it. Explain in your own words why these two situations are different and why the result changed.
3. What is the AWS rule that governs this behavior? Write it in one sentence.
4. Can you think of a real-world scenario where you would want an explicit deny rather than simply not granting a permission?

**The technical explanation you should arrive at:**

AWS policy evaluation follows a strict hierarchy. An explicit Deny at any level overrides any number of Allows from any other source. This is intentional. AWS assumes that if an administrator explicitly wrote "Deny", they meant it as an absolute. A user's personal policy cannot argue with a group deny. This is the core of effective permissions: the effective result is the combination of all policies evaluated together, and a single explicit Deny in any of them removes that permission entirely.

---

### Step 6: Create a Permission Boundary for bob-ops

Now we explore a different mechanism. bob-ops will receive a policy that grants him administrator-level access to everything. But we will attach a permission boundary that caps what he can actually use.

#### Step 6a: Create the Boundary Policy

A permission boundary is itself just an IAM policy. What makes it a boundary is how it is attached -- not as a regular identity policy, but as a boundary.

1. In IAM, click "Policies" then "Create policy"
2. Click the JSON tab and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
```

3. Click "Next"
4. Name it: boundary-s3-readonly-only
5. Click "Create policy"

This boundary says: regardless of what identity policies say, this identity can only read from S3. Nothing else.

#### Step 6b: Give bob-ops an Unrestricted Identity Policy

1. Go to "Users" then click bob-ops
2. Click the "Permissions" tab then "Add permissions" then "Create inline policy"
3. Paste this JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

4. Name it: bob-admin-attempt
5. Create the policy

Without a boundary, this policy would make Bob an administrator. He could create users, delete databases, launch instances, and change billing settings.

#### Step 6c: Attach the Permission Boundary

1. Still on bob-ops, click the "Permissions boundary" tab
2. Click "Set boundary"
3. Search for boundary-s3-readonly-only
4. Select it and click "Set boundary"

---

### Curiosity Gap -- Before You Test bob-ops

Before you simulate bob-ops, think about this: bob-ops has a policy that allows everything. The boundary allows only S3 read. The group also has S3 read access attached. When bob tries to create an EC2 instance, how many "allow" sources does he have? How many does he need? And does having more allow sources help him?

Form your answer. Then test it.

---

### Observation Checkpoint -- After Step 6

Sign in as bob-ops in an incognito window. Try the following actions and record what happens:

- List S3 buckets
- View an object inside an S3 bucket
- Try to upload a file to an S3 bucket
- Navigate to EC2 and try to view running instances
- Navigate to IAM and try to create a new user

**Questions to answer:**

1. Bob has Action: * in his identity policy. That literally means every action. Why can he not create an EC2 instance?
2. How does a permission boundary differ from a group deny? Both are blocking Bob from certain actions. Are they the same mechanism?
3. Write the formula for how effective permissions work when a boundary is present. Use plain language, not just the math notation.
4. If you removed the boundary tomorrow but left the bob-admin-attempt policy, what would bob-ops be able to do?

**The technical explanation:**

A permission boundary defines the maximum possible permissions. It does not grant permissions on its own. It acts as a filter on top of whatever identity policies exist. The effective permission is the intersection: only actions that are permitted by both the identity policy and the boundary are actually granted. If the boundary allows S3 read and the identity policy allows everything, the intersection is S3 read only. The group membership does not expand the boundary. Adding more identity policies does not expand the boundary either. The boundary is a ceiling, not a wall.

---

### Step 7: Observe charlie-ops -- No Personal Policies

charlie-ops has no inline policies. charlie-ops only inherits from the group.

1. Sign in as charlie-ops in an incognito window
2. Try the following and record results:
   - View EC2 instances
   - Try to start or stop an EC2 instance
   - List S3 buckets
   - Try to delete an S3 object

This is the baseline. charlie represents the minimum any member of this group has.

---

### Summary Table -- IAM Lab Results

| User | Identity Policy | Group Policy | Boundary | Effective Result |
|---|---|---|---|---|
| alice-ops | Allow S3 write and delete | Allow S3 read, Deny S3 delete | None | S3 read and write, no delete -- group deny wins |
| bob-ops | Allow all actions | Allow S3 read, Deny S3 delete | S3 read only | S3 read only -- boundary is the ceiling |
| charlie-ops | None | Allow S3 read, Deny S3 delete | None | S3 read only -- inherits group, denied delete |

---

### Final Reflection Questions -- Lab 1

These are the types of questions you may be asked during the presentation quiz. Practice answering them out loud.

1. If I attach a policy that allows EC2 full access directly to alice-ops, will she be able to launch EC2 instances? Walk through your reasoning using the policy evaluation logic.
2. A new developer joins the team and they should have the same access as charlie-ops but also be allowed to upload files to S3. What is the cleanest way to configure this without modifying the group's policy?
3. A security incident occurs. You need to immediately ensure that no member of CloudOpsTeam can access S3 at all, including reads, without deleting any users or the group itself. What is the fastest way to do this?
4. Bob's manager tells you to give Bob the ability to create EC2 instances. You cannot remove the permission boundary because company policy requires it. What are your options?

---
---

# LAB 2 -- AWS Organizations (Challenge Lab)

> "DO HARD THINGS."
>
> This lab requires either a real AWS Organization with management account access, or a simulated walkthrough using the console with at least two accounts. If your group does not have this access, document your attempt, the point at which you were blocked, and what you would have expected to happen. Incomplete execution with strong documentation is more valuable than skipping the lab.

## Objectives

- Create an AWS Organization and designate it as All Features mode
- Create two Organizational Units: TeamAlpha and TeamBeta
- Invite or create member accounts in each OU
- Write and apply Service Control Policies to restrict what each OU can do
- Demonstrate how SCPs interact with IAM and why they are fundamentally different

---

## Curiosity Gap -- The Problem SCPs Solve

Imagine you are the head of security for a company that uses AWS. You have 12 AWS accounts -- one per product team. Each account has its own IAM administrators. One of those administrators makes a mistake and grants a junior developer full administrator access. That junior developer, out of curiosity, launches 50 GPU instances in a region you have never used, running up a $40,000 bill over a weekend.

IAM policies live inside an account and are controlled by the account's admins. If the account admin makes a mistake or goes rogue, IAM cannot protect you from them.

How would you prevent this? What mechanism would you need that lives outside of and above any individual account's IAM system?

Think about it before reading on.

---

## Concept: AWS Organizations

AWS Organizations is a governance layer that sits above individual AWS accounts. It lets you group accounts into a hierarchy and apply rules that no administrator inside any individual account can override.

The hierarchy looks like this:

```
Root (the top of the organization)
  |
  +-- TeamAlpha OU
  |     |
  |     +-- Account: TeamAlpha-Dev
  |     +-- Account: TeamAlpha-Staging
  |
  +-- TeamBeta OU
        |
        +-- Account: TeamBeta-Ops
        +-- Account: TeamBeta-Prod
```

**Management Account:** The account that created the organization. It has authority over all other accounts. SCPs written in the management account apply to every account in the organization except the management account itself.

**Organizational Unit (OU):** A folder for grouping accounts. Policies attached to an OU apply to every account inside it and to every OU nested inside it.

**Service Control Policy (SCP):** A policy that defines the maximum permissions available to accounts in the OU. SCPs do not grant permissions. They restrict them. An account's IAM policies still need to grant access. But if an SCP blocks an action, no IAM policy in any account can unblock it.

This is the answer to the curiosity gap: SCPs are the mechanism that lives above individual account IAM. The management account writes the rules, and no account admin can override them.

---

## Concept: The Critical Difference Between SCP and IAM

| Characteristic | IAM Policy | Service Control Policy |
|---|---|---|
| Where it lives | Inside one account | In the organization, above all accounts |
| Who writes it | The account's IAM admin | The management account admin |
| What it can do | Grant or deny actions | Only restrict -- it cannot grant |
| Can an account admin override it? | Yes, within that account | No |
| Applies to the management account? | Yes | No |
| Default state | Deny all (if no allow) | Allow all via FullAWSAccess default SCP |

The most important thing to understand: SCPs do not replace IAM. An SCP that allows S3 does not mean a user can access S3. The user still needs an IAM policy that allows S3. The SCP just ensures that even if someone creates an IAM policy that grants everything, certain things remain blocked.

---

## Step-by-Step Instructions

### Step 1: Create the Organization

1. In the AWS console, search for "AWS Organizations"
2. Click "Create an organization"
3. Select "Enable all features" -- not just Consolidated Billing. All Features is required for SCPs to work.
4. AWS will configure the current account as the management account.
5. You will receive a verification email. Complete it.

---

### Step 2: Create Organizational Units

1. In Organizations, click "AWS accounts" in the left sidebar
2. Click on "Root" in the account tree
3. Click "Actions" then "Organizational unit" then "Create new"
4. Name: TeamAlpha
5. Repeat to create: TeamBeta

---

### Step 3: Add Member Accounts

If you have two separate AWS accounts available:
1. From the management account in Organizations, click "AWS accounts" then "Add an AWS account"
2. Choose "Invite an existing AWS account"
3. Enter the email address or account ID of the account you want to invite
4. The invited account's root user will receive an email. Accept the invitation from that account.
5. Once accepted, move the account to its OU: select the account, click "Actions", "Move", and choose the appropriate OU.

If you do not have a second account:
1. Click "Add an AWS account" then "Create an AWS account"
2. Name: TeamAlpha-Dev
3. Email: use an email address you control with a unique suffix (many services support plus addressing, like yourname+teamalpha@gmail.com)
4. AWS will create the account. This takes a few minutes.
5. Repeat for TeamBeta-Ops
6. Move each account into its respective OU

**Challenge note:** If account creation is blocked due to limits or verification requirements, document what happened and proceed with the SCP creation steps which you can still complete at the OU level even without member accounts.

---

### Step 4: Create and Apply Service Control Policies

Before attaching SCPs, you must enable SCP support. In Organizations, go to "Policies" in the left sidebar, click "Service control policies", and click "Enable service control policies".

#### SCP 1: TeamAlpha Region Lockdown

This SCP prevents any user in TeamAlpha accounts from creating resources outside of us-east-1. Even if a TeamAlpha IAM admin creates a policy that allows EC2 in Ireland, this SCP blocks it.

1. Go to "Policies" then "Service control policies" then "Create policy"
2. Name: alpha-region-lockdown
3. Paste the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyOutsideUSEast1",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

4. Create the policy
5. Navigate back to "AWS accounts", click TeamAlpha OU
6. Click the "Policies" tab then "Attach" and select alpha-region-lockdown

---

### Observation Checkpoint -- After Attaching the Region SCP

Before attaching the second SCP, discuss these questions with your group:

1. If a TeamAlpha developer switches their console to the eu-west-1 (Ireland) region and tries to launch an EC2 instance, what will happen and why?
2. The SCP uses a condition: StringNotEquals on aws:RequestedRegion. What does this condition evaluate against, and how does AWS know which region a request is targeting?
3. Are there any AWS services that are global and not region-specific? Would this SCP block those too? How might you handle that?
4. If the TeamAlpha account's IAM admin creates a new IAM user and gives that user AdministratorAccess, can that user launch EC2 instances in Ireland?

**The technical explanation:**

The aws:RequestedRegion condition key is evaluated by AWS at the time of the API call. When you click "Launch Instance" in the console, the console sends an API call to the EC2 service endpoint for that region. The SCP intercepts this at the Organizations level before IAM even evaluates it. Because the effect is Deny and the condition is StringNotEquals, the logic reads: "If the region being requested is anything other than us-east-1, deny the action." There is no IAM policy that can override this because SCPs are evaluated before IAM policies in the AWS authorization chain.

---

#### SCP 2: TeamBeta EC2 Restriction

TeamBeta is an operations team. Their workloads run on managed services, not raw EC2. This SCP ensures they cannot launch EC2 instances even if someone mistakenly grants them EC2 access in IAM.

1. Create a new SCP
2. Name: beta-no-ec2
3. JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyEC2Launch",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Attach it to the TeamBeta OU

---

### Step 5: Verify and Simulate

Log into a TeamAlpha member account (use the account's root or an IAM user with EC2 access):
- Switch the console region to eu-west-1 and try to launch an EC2 instance. Expected result: denied by SCP.
- Switch back to us-east-1 and try again. Expected result: allowed (assuming IAM also permits it).

Log into a TeamBeta member account:
- Try to launch any EC2 instance in any region. Expected result: denied by SCP.
- Try to create an S3 bucket. Expected result: allowed (no SCP blocks S3 for TeamBeta).

---

### Observation Checkpoint -- After the Full Organizations Lab

1. A TeamBeta administrator is frustrated that they cannot launch EC2 instances. They argue that since they have AdministratorAccess in IAM, they should be able to do anything. How do you explain to them why their IAM policy does not help here?
2. If you attach an SCP to the Root rather than a specific OU, which accounts does it apply to?
3. The management account has the region lockdown SCP attached to TeamAlpha OU. Can the management account itself launch EC2 in Ireland? Why or why not?
4. A developer says: "SCPs and IAM are doing the same thing, just at different levels." Is this accurate? What is the key conceptual difference?

### Challenge Documentation Prompt

If your group could not complete this lab due to account access limitations, document the following:
- At what step were you blocked?
- What would you have expected to happen if you had continued?
- What is the architectural reason that SCPs must be managed from a management account and cannot be replicated using only IAM?

---
---

# LAB 3 -- EC2 Bootstrapping, AMI, and Load Balancing

## Objectives

- Use EC2 User Data to bootstrap a web server automatically on first launch
- Create an AMI from the configured instance
- Launch two EC2 instances from that AMI
- Create a Target Group and Application Load Balancer
- Observe how the Load Balancer distributes traffic and why both instances serve the same content

---

## Curiosity Gap -- What If Configuration Was Not Automatic?

Imagine you are running a web application and you need to scale from 2 servers to 20 servers in the next 30 minutes because your product just got featured on a major news site. If you had to manually SSH into each new server, install software, copy configuration files, set file permissions, and start services, how long would that take? What is the chance you make an error on one of the 20 servers? What happens to traffic if one misconfigured server is included in the pool?

Now imagine all 20 servers configured themselves correctly the moment they started, with zero human intervention, every single time, identically.

That is what bootstrapping and AMIs give you.

---

## Concept: Bootstrapping with User Data

When you launch an EC2 instance, AWS gives you the option to provide a "User Data" script. This is a shell script (or cloud-init configuration) that runs automatically as the root user the very first time the instance boots.

The script runs before anyone can SSH in. By the time the instance is reachable, it has already executed your instructions. This means you can install software, configure services, write files, set environment variables, and pull from a code repository, all without logging in.

User Data runs exactly once: on first boot. If you stop and start the instance, it does not run again unless you configure it to do so explicitly.

The URL http://169.254.169.254 is a special address called the Instance Metadata Service. It is only accessible from within the instance itself. It provides information about the instance such as its ID, its availability zone, and the IAM role attached to it. The bootstrap script uses this to write dynamic content to the web page.

---

## Concept: AMI -- Amazon Machine Image

An AMI is a complete snapshot of an EC2 instance at a specific point in time. It captures the operating system, all installed packages, all configuration files, all changes made to the root volume. It does not capture instance-specific things like the instance ID or the IP address. Those are assigned fresh each time a new instance is launched.

When you launch 10 instances from the same AMI, you get 10 servers that are in exactly the same state as the original instance was when you took the snapshot. This is the foundation of horizontal scaling: make one instance perfect, capture it as an AMI, and stamp out as many copies as you need.

Without an AMI, you would need to either bootstrap every new instance from scratch (which takes time on each launch) or manually configure each one. AMIs eliminate both problems.

---

## Concept: Application Load Balancer

A Load Balancer accepts incoming traffic on behalf of your application and distributes it across multiple instances. It acts as the single point of contact for clients. Clients never connect directly to your EC2 instances. They connect to the Load Balancer's DNS name, and the Load Balancer decides which instance to send each request to.

The Application Load Balancer (ALB) operates at Layer 7, meaning it understands HTTP and HTTPS. It can make routing decisions based on the URL path, the HTTP headers, or the hostname. For this lab, it simply distributes requests evenly using round-robin.

The ALB constantly checks whether instances are healthy using a Health Check: it sends an HTTP request to each instance at a defined path and interval. If an instance stops responding, the ALB stops sending traffic to it. When it recovers, the ALB adds it back automatically.

---

## Step-by-Step Instructions

### Step 1: Launch the Bootstrap EC2 Instance

1. In the AWS console, go to EC2 and click "Launch Instance"
2. Name: bootstrap-webserver
3. AMI: Amazon Linux 2023 (select the free tier eligible option)
4. Instance type: t2.micro
5. Key pair: create a new key pair named labkey, RSA type, .pem format. Download the file and keep it secure.
6. Network settings:
   - VPC: use the default VPC
   - Subnet: choose any public subnet
   - Auto-assign public IP: Enable
   - Security Group: create a new one named webserver-sg
     - Rule 1: Type HTTP, Port 80, Source 0.0.0.0/0
     - Rule 2: Type SSH, Port 22, Source My IP
7. Scroll to "Advanced details" and find the "User data" field
8. Paste this entire script:

```bash
#!/bin/bash
yum update -y
yum install -y httpd

systemctl start httpd
systemctl enable httpd

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)

AZ=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
  <title>AWS Lab</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f0f4f8; text-align: center; padding: 60px; }
    .box { background: white; padding: 40px; border-radius: 8px;
           max-width: 480px; margin: auto; box-shadow: 0 2px 12px rgba(0,0,0,0.12); }
    h2 { color: #232f3e; }
    .label { font-size: 12px; color: #888; text-transform: uppercase; }
    .value { font-size: 18px; font-weight: bold; color: #ff9900; }
  </style>
</head>
<body>
  <div class="box">
    <h2>AWS Lab Web Server</h2>
    <p class="label">Instance ID</p>
    <p class="value">${INSTANCE_ID}</p>
    <p class="label">Availability Zone</p>
    <p class="value">${AZ}</p>
    <p style="color:#888; font-size:13px;">Configured automatically via User Data on first boot.</p>
  </div>
</body>
</html>
EOF

echo "Bootstrap completed at $(date)" >> /var/log/bootstrap.log
```

9. Click "Launch instance"

---

### Step 2: Verify Bootstrapping

1. Wait 2 to 3 minutes
2. Select bootstrap-webserver in EC2 and copy the Public IPv4 address
3. Open a browser and navigate to http://public-ip-address (use http, not https)
4. You should see the web page showing the instance ID and AZ

Verify via SSH:
```bash
ssh -i labkey.pem ec2-user@your-public-ip
cat /var/log/bootstrap.log
```

You should see a line that says Bootstrap completed at followed by a timestamp.

---

### Observation Checkpoint -- After Step 2

Before creating the AMI, discuss or write down answers to these questions:

1. The bootstrap script retrieves the Instance ID from a URL on 169.254.169.254. That address is not on the internet. Where does it come from, and why can only the instance itself access it?
2. If you run the bootstrap script again manually from inside the instance, would it create a second web page or overwrite the existing one? Why?
3. The script uses systemctl enable httpd. What does enable do differently from systemctl start httpd?
4. What would happen if the User Data script had a syntax error and failed partway through? Would the instance still launch?

---

### Step 3: Create an AMI from the Bootstrapped Instance

You are about to freeze this instance's current state into a reusable blueprint.

1. In EC2, select bootstrap-webserver
2. Click "Actions" then "Image and templates" then "Create image"
3. Image name: webserver-ami-v1
4. Image description: Apache web server configured via User Data
5. Leave all other settings at their defaults
6. Click "Create image"
7. Go to "AMIs" in the left sidebar
8. Wait until the AMI status changes from pending to available. This usually takes 3 to 5 minutes.

**What is happening during this wait?** AWS is stopping the instance temporarily (or taking a snapshot while running, depending on settings), creating a snapshot of the root EBS volume, and registering that snapshot as an AMI with all the metadata needed to launch new instances from it. The original instance continues running.

---

### Step 4: Launch Two Instances from the AMI

#### Instance 1: webserver-1

1. In AMIs, select webserver-ami-v1
2. Click "Launch instance from AMI"
3. Name: webserver-1
4. Instance type: t2.micro
5. Key pair: labkey
6. Network: use the default VPC
7. Subnet: choose a subnet in us-east-1a (or the first AZ available)
8. Auto-assign public IP: Enable
9. Security Group: select webserver-sg (the one created earlier)
10. Click "Launch instance"

#### Instance 2: webserver-2

Repeat the same steps with these differences:
- Name: webserver-2
- Subnet: choose a subnet in us-east-1b (a different AZ from webserver-1)

The different AZ is intentional. Placing instances in different AZs means that if one AZ experiences a failure, the other continues serving traffic. This is the foundation of high availability.

---

### Curiosity Gap -- Before Testing the AMI Instances

You created webserver-1 and webserver-2 from the AMI. You did not give them any User Data script. The AMI contains a pre-written static HTML file that references the original instance's ID. What do you think the web page on webserver-1 and webserver-2 will show? Will it show the original instance ID from the bootstrap instance, or their own? Why?

Form your answer. Then access their public IPs directly and check.

---

### Observation Checkpoint -- After Step 4

1. What instance ID does each server display? Is it the same as the bootstrap-webserver or their own?
2. The HTML file was written by the bootstrap script with the original instance's ID embedded in it. But the new instances show their own IDs. How is this possible? What part of the process handled this?

**The technical explanation:**

Look at the bootstrap script again. The HTML file is generated dynamically using the INSTANCE_ID variable, which is fetched from the metadata service at the time the script runs. When you create an AMI, the HTML file that exists on disk at that moment contains the bootstrap instance's ID. When webserver-1 and webserver-2 launch from that AMI, the HTML file they inherit still has the old ID.

Wait -- but the page shows the new instance IDs. That means the script ran again. Why?

Actually, by default User Data does not run again after the first boot. If your page is showing the new instance IDs, it is because systemd and httpd are serving the same static file, and the instance ID in it is from the bootstrap instance. If you want each new instance to display its own ID, you need to either put the User Data script back in when launching from the AMI, or modify the HTML on each instance after launch.

This is an important discovery. Test it. Navigate to the IP addresses of webserver-1 and webserver-2 and check what ID appears. Then SSH in and run:

```bash
cat /var/www/html/index.html | grep INSTANCE
```

Compare that value to what the EC2 console shows as the instance ID. Are they the same or different? Document your finding. This is a real-world subtlety that catches engineers off guard.

---

### Step 5: Create a Target Group

The Target Group is the list of instances the Load Balancer will distribute traffic to.

1. In EC2, scroll down in the left sidebar to "Target Groups"
2. Click "Create target group"
3. Target type: Instances
4. Target group name: webserver-targets
5. Protocol: HTTP
6. Port: 80
7. VPC: default VPC
8. Health check protocol: HTTP
9. Health check path: /
10. Click "Next"
11. Select both webserver-1 and webserver-2 from the list
12. Click "Include as pending below"
13. Click "Create target group"

The health check path / means the Load Balancer will send a GET request to the root of the web server every 30 seconds. If the server responds with HTTP 200, it is considered healthy. If it fails, the ALB stops sending traffic to it.

---

### Step 6: Create the Application Load Balancer

1. In EC2, go to "Load Balancers" then "Create load balancer"
2. Select "Application Load Balancer" and click "Create"
3. Name: webserver-alb
4. Scheme: Internet-facing (accepts requests from the public internet)
5. IP address type: IPv4
6. Network mapping: select your default VPC, then select at least two AZs -- the ones that contain webserver-1 and webserver-2
7. Security groups: select webserver-sg
8. Listeners: Protocol HTTP, Port 80, Default action: Forward to webserver-targets
9. Click "Create load balancer"

Wait for the ALB state to change to Active. This takes 2 to 3 minutes.

---

### Step 7: Test Load Balancing

1. Click on webserver-alb and copy the DNS name
2. Open a browser and navigate to http://dns-name (the DNS name, not an IP address)
3. Refresh the page 5 to 10 times
4. Watch the Instance ID on the page

You should see the Instance ID alternate between the two instances as the ALB routes each request to a different backend.

---

### Observation Checkpoint -- After the Full Lab 3

1. Both instances serve the same HTML layout even though you wrote no HTML on them directly. Trace the exact path: where was the HTML created, and how did it get to both servers?
2. The ALB has a DNS name but no IP address you can directly use. Why does AWS use DNS for the ALB and not a static IP? What happens if you pin the ALB's IP address in your hosts file?
3. If webserver-1 crashes, what happens to traffic? How does the ALB know webserver-1 is down? How long does it take to detect this?
4. You need to update the web page content on both servers. What is the best practice approach if you are using AMIs? What would you do differently versus editing each server directly?
5. The script uses systemctl enable httpd. If you built an AMI without running this command, what would happen when a new instance launched from that AMI and then was stopped and started again?

---
---

# LAB 4 -- VPC Peering, Flow Logs, Security Groups, NACLs, and Ephemeral Ports

## Objectives

- Create two VPCs with non-overlapping CIDR ranges
- Establish a VPC Peering connection and configure routing
- Enable VPC Flow Logs and analyze the captured traffic
- Prove that Security Groups are stateful by removing outbound rules and observing behavior
- Prove that NACLs are stateless by demonstrating what happens when ephemeral port rules are missing
- Understand what ephemeral ports are and why NACLs must account for them explicitly

---

## Curiosity Gap -- The Two-Guard Problem

Imagine a building with two types of security guards:

Guard A stands at the door of each individual office room. When you enter a room, Guard A stamps your wrist. When you try to leave, Guard A sees the stamp and lets you out automatically. Guard A remembers you. Guard A is also not allowed to refuse entry to specific people -- Guard A can only make a list of people who are allowed in. If you are not on the list, you cannot enter. But Guard A cannot actively block a specific known troublemaker.

Guard B controls entire floors of the building. Guard B checks your badge every single time you enter or exit through a floor corridor. Guard B does not stamp your wrist and does not remember you. Every crossing is evaluated from scratch. Guard B can both allow and explicitly refuse specific people or groups, but because Guard B does not remember, even a person who was allowed in 10 seconds ago must show their badge again on the way out.

Before reading on: which guard is the Security Group and which is the NACL? And what problem does each guard model create that the other guard does not have?

---

## Concept: VPC

A Virtual Private Cloud is an isolated private network inside AWS. It has its own IP address space defined by a CIDR block, its own subnets, its own routing rules, and its own internet gateway if you want it to reach the internet.

By default, two VPCs cannot communicate with each other, even if they are in the same AWS account and the same region. They are isolated. VPC Peering is one mechanism to connect them.

CIDR notation defines the IP address range. 10.0.0.0/16 means: start at 10.0.0.0 and use 16 bits for the network portion, leaving 16 bits for host addresses. That gives you 2 to the power of 16 = 65,536 possible addresses.

---

## Concept: VPC Peering

VPC Peering creates a private, direct network connection between two VPCs. Traffic between them does not traverse the public internet. It stays within the AWS backbone network.

VPC Peering is not transitive. If VPC-A peers with VPC-B, and VPC-B peers with VPC-C, VPC-A cannot reach VPC-C through VPC-B. Each peering connection is a direct, dedicated link between exactly two VPCs.

One critical requirement: the two VPCs cannot have overlapping CIDR ranges. If VPC-A uses 10.0.0.0/16 and VPC-B also uses 10.0.0.0/16, AWS cannot determine which VPC a packet addressed to 10.0.1.5 is destined for. The IP routing system would be ambiguous.

---

## Concept: Security Groups

A Security Group is a stateful virtual firewall attached to an EC2 instance's network interface. Stateful means it tracks connection state. When an inbound connection is allowed, the response traffic for that connection is automatically permitted, even if there is no explicit outbound rule for it.

Security Groups can only have Allow rules. There is no Deny rule in a Security Group. Everything not explicitly allowed is implicitly denied. If you want to block a specific IP address, you cannot add a Deny rule for it in a Security Group. You would need to either not include it in your allow list (which only works if you define a restricted allow list) or use a NACL.

---

## Concept: Network ACLs

A Network ACL is a stateless firewall that operates at the subnet boundary. It evaluates every packet independently, with no memory of previous packets. A packet arriving at the subnet is checked against inbound rules. A packet leaving the subnet is checked against outbound rules. The fact that a packet was allowed inbound 50 milliseconds ago is irrelevant to whether a response packet is allowed outbound.

NACLs evaluate rules in order by rule number, starting from the lowest. The first rule that matches the packet is applied, and evaluation stops. This is different from Security Groups, where all rules are evaluated and the most permissive match wins.

NACLs can have both Allow and Deny rules. This is the capability Security Groups lack.

The default NACL created with a VPC allows all inbound and outbound traffic. A custom NACL you create yourself blocks all traffic by default.

---

## Concept: Ephemeral Ports

This is the concept that causes the most confusion with NACLs, and it is also one of the most elegant concepts in networking once you understand it.

When your laptop (or any client) makes a TCP connection to a server, the communication has two endpoints: the server's well-known port (like 80 for HTTP) and the client's source port. The client's source port is chosen randomly from a range of high-numbered ports, typically 1024 to 65535. This randomly chosen port is called an ephemeral port. The word ephemeral means short-lived. The port is used only for the duration of that connection and then released.

```
Client makes request:
  Source: 203.0.113.45 : 54321 (ephemeral port, chosen randomly)
  Destination: 54.23.100.5 : 80 (your EC2 server, well-known port)

Server sends response:
  Source: 54.23.100.5 : 80
  Destination: 203.0.113.45 : 54321 (must go back to the ephemeral port)
```

For a Security Group on the server, this is handled automatically. The inbound allow rule for port 80 covers the request, and the Security Group tracks the connection state to allow the response back out.

For a NACL on the server's subnet, this requires explicit rules:
- Inbound rule allowing TCP port 80 (to receive the client's request)
- Outbound rule allowing TCP ports 1024 to 65535 (because the response must go to the client's ephemeral port, which could be any number in that range)

If you forget the outbound ephemeral rule, the NACL allows the request to arrive but blocks the server's response from leaving. The client receives no response, and the connection appears to time out. This is one of the most common NACL debugging scenarios.

The same principle applies in the other direction. When your EC2 instance makes an outbound request (for example, running yum update), the EC2 instance itself uses an ephemeral port as its source port, and the response from the yum repository server comes back to that ephemeral port. Your NACL must have an inbound rule allowing TCP 1024 to 65535 to permit those responses.

---

## Step-by-Step Instructions

### Step 1: Create VPC-A

1. In the AWS console, search for VPC
2. Click "Create VPC"
3. Select "VPC and more" to have AWS create subnets and routing automatically
4. Name: VPC-A
5. IPv4 CIDR: 10.0.0.0/16
6. Number of Availability Zones: 1
7. Number of public subnets: 1
8. Number of private subnets: 0
9. NAT Gateways: None
10. Click "Create VPC"

---

### Step 2: Create VPC-B

1. Click "Create VPC" again
2. Select "VPC and more"
3. Name: VPC-B
4. IPv4 CIDR: 172.16.0.0/16 (must not overlap with VPC-A's range)
5. Same settings as VPC-A: 1 AZ, 1 public subnet, no private subnets, no NAT
6. Click "Create VPC"

---

### Curiosity Gap -- Why Must CIDRs Not Overlap?

Before moving on, think through this: you have two VPCs. VPC-A has an EC2 instance with private IP 10.0.1.50. VPC-B also has the range 10.0.0.0/16, and VPC-B also has an instance with private IP 10.0.1.50. You try to peer them and send a packet to 10.0.1.50. How does the routing system know which VPC the packet is meant for?

Write your answer. Then check whether AWS even allows you to create a peering connection between overlapping VPCs. Attempt it and document what happens.

---

### Step 3: Create VPC Peering Connection

1. In the VPC console, click "Peering connections" then "Create peering connection"
2. Name: vpc-a-to-vpc-b
3. Requester VPC: VPC-A
4. Account: My account
5. Region: This region
6. Accepter VPC: VPC-B
7. Click "Create peering connection"
8. The connection appears as Pending Acceptance
9. Select it, click "Actions" then "Accept request"
10. The status changes to Active

The peering connection exists, but instances still cannot communicate. The connection is like building a tunnel between two buildings but not yet putting a door at each end. The next step adds the doors.

---

### Step 4: Update Route Tables

Each VPC's route table must have a route that sends traffic destined for the other VPC's CIDR through the peering connection.

#### VPC-A Route Table:
1. Go to "Route tables"
2. Find the route table associated with VPC-A's public subnet (check the "Subnet associations" tab to identify it)
3. Click "Routes" then "Edit routes"
4. Add a route:
   - Destination: 172.16.0.0/16
   - Target: select the peering connection vpc-a-to-vpc-b
5. Save changes

#### VPC-B Route Table:
1. Find VPC-B's public subnet route table
2. Edit routes
3. Add a route:
   - Destination: 10.0.0.0/16
   - Target: select vpc-a-to-vpc-b
4. Save changes

---

### Step 5: Launch EC2 Instances in Each VPC

#### EC2 in VPC-A:
1. Launch instance
2. Name: ec2-vpc-a
3. AMI: Amazon Linux 2023
4. Type: t2.micro
5. Key pair: labkey
6. Network: VPC-A, public subnet
7. Auto-assign public IP: Enable
8. Security Group (create new): sg-vpc-a
   - Allow SSH port 22 from My IP
   - Allow All ICMP IPv4 from 172.16.0.0/16

#### EC2 in VPC-B:
1. Launch instance
2. Name: ec2-vpc-b
3. VPC: VPC-B, public subnet
4. Auto-assign public IP: Enable
5. Security Group: sg-vpc-b
   - Allow SSH port 22 from My IP
   - Allow All ICMP IPv4 from 10.0.0.0/16

---

### Step 6: Test VPC Peering

SSH into ec2-vpc-a:
```bash
ssh -i labkey.pem ec2-user@public-ip-of-ec2-vpc-a
```

From inside ec2-vpc-a, ping ec2-vpc-b using its private IP (find this in the EC2 console):
```bash
ping 172.16.x.x
```

You should see responses. This traffic is travelling through the peering connection, inside the AWS network, without touching the public internet.

---

### Step 7: Enable VPC Flow Logs

Flow Logs are a passive capture mechanism. They do not affect your traffic. They record metadata about every connection attempt: source IP, destination IP, ports, protocol, bytes transferred, and whether the traffic was accepted or rejected.

#### Create a CloudWatch Log Group:
1. Go to CloudWatch
2. Click "Log groups" then "Create log group"
3. Name: /vpc/flow-logs
4. Click "Create"

#### Create an IAM Role for Flow Logs:
1. Go to IAM, click "Roles" then "Create role"
2. Trusted entity type: AWS service
3. Use case: search for "VPC Flow Logs"
4. Next, attach policy: CloudWatchLogsFullAccess
5. Name: vpc-flow-logs-role
6. Create role

#### Enable Flow Logs on VPC-A:
1. Go to VPC, select VPC-A
2. Click "Actions" then "Create flow log"
3. Filter: All (capture both accepted and rejected traffic)
4. Maximum aggregation interval: 1 minute
5. Destination: Send to CloudWatch Logs
6. Destination log group: /vpc/flow-logs
7. IAM role: vpc-flow-logs-role
8. Click "Create flow log"

Wait 2 to 3 minutes, then generate some traffic: ping ec2-vpc-b again, attempt an SSH connection, visit the instance's public IP in a browser.

---

### Step 8: Analyze Flow Log Entries

Go to CloudWatch, click "Log groups", open /vpc/flow-logs. Click on a log stream. It will be named after a network interface ID (eni-...).

You will see entries like this:

```
2 111122223333 eni-0a1b2c3d 10.0.1.5 172.16.1.8 0 0 1 4 336 1716000000 1716000060 ACCEPT OK
2 111122223333 eni-0a1b2c3d 203.0.113.45 10.0.1.5 54321 22 6 8 4096 1716000000 1716000060 ACCEPT OK
2 111122223333 eni-0a1b2c3d 198.51.100.2 10.0.1.5 0 80 6 1 44 1716000000 1716000060 REJECT OK
```

Reading a flow log entry:

| Position | Field | Example | Meaning |
|---|---|---|---|
| 1 | Version | 2 | Log format version |
| 2 | Account ID | 111122223333 | Your AWS account |
| 3 | Interface | eni-0a1b2c3d | Which network interface |
| 4 | Source IP | 10.0.1.5 | Traffic originated here |
| 5 | Destination IP | 172.16.1.8 | Traffic destined here |
| 6 | Source port | 54321 | Ephemeral port of the client |
| 7 | Destination port | 22 | SSH port |
| 8 | Protocol | 6 | 6=TCP, 17=UDP, 1=ICMP |
| 9 | Packets | 8 | Packets in this flow |
| 10 | Bytes | 4096 | Bytes in this flow |
| 11 | Start | 1716000000 | Unix timestamp, flow start |
| 12 | End | 1716000060 | Unix timestamp, flow end |
| 13 | Action | ACCEPT or REJECT | Was it allowed? |
| 14 | Status | OK | Log delivery status |

---

### Observation Checkpoint -- After Analyzing Flow Logs

1. Find a REJECT entry in the logs. What source IP and port does it show? Why was this traffic rejected?
2. Find an entry where the destination port is 22. What is the source port? Is it a number below 1024 or above 1024? Why?
3. The flow logs show ACCEPT and REJECT. Which AWS service generates the REJECT: the Security Group or the NACL? How can you tell from the flow log which one caused the rejection?
4. A colleague asks why the source port for an SSH session shows a high number like 54321. Explain ephemeral ports in two sentences without using technical jargon.

---

### Step 9: Prove That Security Groups Are Stateful

This is a deliberate experiment designed to show you something that surprises most people when they see it.

1. Go to ec2-vpc-a's Security Group: sg-vpc-a
2. Add an inbound rule: HTTP, port 80, source 0.0.0.0/0
3. Now go to the "Outbound rules" tab and delete all outbound rules (remove the default "Allow all outbound" rule entirely)
4. SSH into ec2-vpc-a and install Apache:

```bash
sudo yum install -y httpd
sudo systemctl start httpd
```

5. Navigate to http://public-ip-of-ec2-vpc-a in your browser

---

### Observation Checkpoint -- The Stateful Test

**Before you check:** predict the result. The Security Group allows HTTP inbound. The Security Group has no outbound rules at all. What will happen when a browser tries to load the page?

After you check, answer these questions:

1. Did the page load? If yes, explain exactly why. If no, explain what you would change.
2. The Security Group has no outbound rule. The server needs to send its HTTP response back to the browser. How does this response get out?
3. Now add an outbound rule that denies all traffic on port 80. What would you expect to happen? (If you have a NACL available, use it instead, since Security Groups cannot deny -- but reason through what would happen if they could.)
4. Describe the concept of connection tracking in one paragraph, as if you are explaining it to someone who has never worked with networking.

**The technical explanation:**

Security Groups maintain a connection state table. When a packet arrives and is permitted by an inbound rule, AWS records the connection: the source IP, source port, destination IP, destination port, and protocol. When a response packet attempts to leave, AWS checks it against the connection state table rather than against the outbound rules. If the packet is part of an established connection that was permitted inbound, it is allowed outbound regardless of what the outbound rules say. This is what stateful means. The firewall remembers the conversation and does not require you to re-approve the response.

---

### Step 10: Create a Custom NACL and Prove Stateless Behavior

This experiment will break access to your instance and then restore it by understanding ephemeral ports.

**Read this entire step before executing it.** Because a new custom NACL denies all traffic by default, you will temporarily lose access to the instance if you associate it before adding rules.

#### Step 10a: Create the NACL

1. In VPC console, click "Network ACLs" then "Create network ACL"
2. Name: strict-nacl
3. VPC: VPC-A
4. Click "Create network ACL"
5. Do not associate it with the subnet yet

#### Step 10b: Add Inbound Rules

Select strict-nacl and click the "Inbound rules" tab then "Edit inbound rules":

| Rule Number | Type | Protocol | Port Range | Source | Allow/Deny |
|---|---|---|---|---|---|
| 100 | SSH | TCP | 22 | Your IP /32 | Allow |
| 110 | HTTP | TCP | 80 | 0.0.0.0/0 | Allow |
| 120 | Custom TCP | TCP | 1024-65535 | 0.0.0.0/0 | Allow |
| asterisk | All traffic | All | All | 0.0.0.0/0 | Deny |

The asterisk rule is created automatically and cannot be modified. It denies everything that does not match a preceding rule.

#### Step 10c: Add Outbound Rules

Click the "Outbound rules" tab then "Edit outbound rules":

| Rule Number | Type | Protocol | Port Range | Destination | Allow/Deny |
|---|---|---|---|---|---|
| 100 | HTTP | TCP | 80 | 0.0.0.0/0 | Allow |
| 110 | HTTPS | TCP | 443 | 0.0.0.0/0 | Allow |
| 120 | Custom TCP | TCP | 1024-65535 | 0.0.0.0/0 | Allow |
| asterisk | All traffic | All | All | 0.0.0.0/0 | Deny |

#### Step 10d: Associate the NACL with VPC-A's Public Subnet

1. Click the "Subnet associations" tab
2. Click "Edit subnet associations"
3. Select VPC-A's public subnet
4. Save

The new NACL now controls all traffic into and out of this subnet.

---

### Step 10e: Test Without the Ephemeral Rule

1. Temporarily delete inbound rule 120 (the 1024-65535 rule)
2. Try to SSH into ec2-vpc-a
3. Try to load the web page in your browser

Record what happens.

4. Now delete outbound rule 120 as well (while rule 120 inbound is also gone)
5. Try to SSH again

Record what happens.

6. Restore both rule 120 entries (inbound and outbound)
7. Confirm access is restored

---

### Observation Checkpoint -- After the NACL Ephemeral Port Test

1. When you removed inbound rule 120 but kept everything else, SSH failed. Port 22 was still allowed inbound by rule 100. Why did SSH fail?
2. When you removed outbound rule 120, what specifically was being blocked that prevented communication?
3. Draw the exact path of an SSH connection from your laptop to ec2-vpc-a. Label every point where a NACL rule or Security Group is evaluated. At each point, state which rule applies and why.
4. A colleague argues that adding 1024-65535 outbound is a security risk because it allows too much. They want to only allow responses on specific ports. Why is this not practical with NACLs and stateless firewalls in general?
5. You configure a NACL with inbound rule: Allow TCP 443. A client connects from port 49152. The server tries to respond. Walk through every packet evaluation step, identifying which NACL rules apply and in what order.

**The technical explanation of the ephemeral inbound rule:**

When your EC2 instance makes an outbound connection (for example, to download a package with yum), the instance sends a packet from an ephemeral source port. The response from the remote server comes back to that ephemeral port. At the NACL boundary, this returning response is an inbound packet. Its destination port is the ephemeral port your EC2 used. Without inbound rule 120 allowing 1024-65535, this response packet is blocked by the default deny rule. Your instance can send the request but never receives the response. yum hangs. Downloads fail. This is exactly why both inbound and outbound rules for the ephemeral range are required.

---

### Final Reflection Questions -- Lab 4

1. A NACL allows HTTP inbound on port 80, and a Security Group also allows HTTP inbound on port 80. A request arrives at the subnet. Describe the exact order in which each control is evaluated.
2. You add a NACL rule at number 90 that denies all TCP traffic from a specific IP. You already have a rule at number 100 that allows TCP port 22 from all sources. Can that specific IP still SSH into the subnet? Why or why not?
3. VPC Peering does not route traffic transitivelly. VPC-A peers with VPC-B, and VPC-B peers with VPC-C. An EC2 in VPC-A tries to ping an EC2 in VPC-C. What happens? What would you need to do to make this work?
4. A flow log entry shows REJECT for traffic arriving on port 443 to an instance that has a Security Group allowing HTTPS. The NACL also has a rule allowing port 443 inbound. What else could cause a REJECT?
5. You are debugging why an instance cannot reach the internet to download software. You check the Security Group: it allows all outbound. You check the route table: it has a route to the internet gateway. But downloads still fail. What do you check next, and what specifically would you look for?

---
---

# Group Task Structure

Each group will receive a task at the beginning of the presentation session. The task will not repeat anything you practiced. It will combine concepts from different labs and ask you to apply them in a configuration you have not seen before. Below are examples of the type of task you may receive. These specific tasks may or may not be the ones used on the day, but the complexity level and style are representative.

**Example Task for a Group assigned Lab 1:**
"Create a fourth user named devops-ops. This user must be able to launch EC2 instances and create S3 buckets, but must never be able to delete anything in S3 or IAM, even if future policies grant them that access. Implement this using the most appropriate mechanism and explain your choice."

**Example Task for a Group assigned Lab 2:**
"An account in the TeamAlpha OU needs to run a global service that requires access in both us-east-1 and eu-west-1. The current SCP blocks all non-us-east-1 activity. Add an exception for a specific list of services in eu-west-1 without removing the lockdown for other services. Implement it and explain the condition logic."

**Example Task for a Group assigned Lab 3:**
"webserver-1 is returning a 503 error. The Load Balancer is reporting it as unhealthy. SSH into webserver-1, diagnose the issue, fix it, and confirm that the Load Balancer marks it healthy again. Document every step of your diagnosis."

**Example Task for a Group assigned Lab 4:**
"A new EC2 instance in VPC-A's subnet can receive traffic on port 443 from the internet but its outbound requests to package repositories are timing out. The Security Group allows all outbound. Diagnose and fix the issue using NACL rules only. Do not modify the Security Group."

---

# Cleanup Checklist

Run through this list after the lab or after the presentation. Leaving resources running incurs AWS charges.

- [ ] Terminate ec2-vpc-a, ec2-vpc-b, bootstrap-webserver, webserver-1, webserver-2
- [ ] Delete the Application Load Balancer: webserver-alb
- [ ] Delete the Target Group: webserver-targets
- [ ] Deregister the AMI: webserver-ami-v1
- [ ] Delete the EBS snapshot associated with the AMI (check Snapshots in EC2)
- [ ] Delete the VPC Peering Connection: vpc-a-to-vpc-b
- [ ] Delete VPC-A and VPC-B (this removes associated subnets, route tables, and internet gateways)
- [ ] Delete IAM users: alice-ops, bob-ops, charlie-ops
- [ ] Delete IAM group: CloudOpsTeam
- [ ] Delete inline and managed policies created for the lab
- [ ] Delete permission boundary policy: boundary-s3-readonly-only
- [ ] Delete CloudWatch Log Group: /vpc/flow-logs
- [ ] Delete IAM role: vpc-flow-logs-role
- [ ] If using Organizations: detach all SCPs from OUs before attempting to close or remove member accounts

---

# Further Reference

| Topic | AWS Documentation URL |
|---|---|
| IAM Policy Evaluation Logic | docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html |
| Permission Boundaries | docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html |
| SCP Basics | docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html |
| EC2 User Data | docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html |
| Instance Metadata Service | docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html |
| ALB Documentation | docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html |
| VPC Peering | docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html |
| VPC Flow Logs | docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html |
| Security Groups | docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html |
| Network ACLs | docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html |

---

*Lab guide prepared for team presentation -- May 24, 2026.*

*Depth of understanding is assessed over memorization. Be ready to explain why, not just what.*
