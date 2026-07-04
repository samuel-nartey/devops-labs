# ☁️ CloudFormation Mastery: Zero to Production
### A 10-Level, Project-Based Journey Through Infrastructure as Code

![AWS](https://img.shields.io/badge/AWS-CloudFormation-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Level](https://img.shields.io/badge/Level-Beginner%20to%20Advanced-blueviolet?style=for-the-badge)
![IaC](https://img.shields.io/badge/Infrastructure-as%20Code-2ea44f?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Maintainer](https://img.shields.io/badge/Maintained%20by-ParoCyber-informational?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)

![YAML](https://img.shields.io/badge/YAML-CC1B1B?style=flat-square&logo=yaml&logoColor=white)
![CLI](https://img.shields.io/badge/AWS%20CLI-v2-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)
![Region](https://img.shields.io/badge/Region-Agnostic-blue?style=flat-square)
![Cost](https://img.shields.io/badge/Cost-Free%20Tier%20Friendly-green?style=flat-square)

---

## 📌 What This Repository Is

This is not a tutorial you read. It's a **project you build, level by level**, where every new CloudFormation concept is introduced only when the *previous* project demands it. By the time you finish Level 10, you won't just "know CloudFormation syntax", you will have designed, broken, fixed, and redeployed a real production-style AWS architecture entirely through code.

Each level follows the exact same rhythm:

1. **The Scenario**, a real-world reason you need this concept, not an abstract lecture.
2. **🔮 Prediction Point**, before you deploy, you guess what will happen. Answer is hidden until you check it.
3. **Step-by-Step Build**, exact commands and template code.
4. **🔍 Observation Point**, after you deploy, you inspect the result and reason about *why*. Answer hidden until you check it.
5. **Template Breakdown**, line-by-line dissection of every new concept introduced.
6. **🕳️ Curiosity Gap**, a deliberately unanswered question that pulls you into the next level.
7. **🧪 Challenge**, a small modification you must make yourself before moving on.

---

## 🧭 How to Use This Guide (Read This First)

> **Do not skip levels. Do not copy-paste without typing.** CloudFormation is learned in your fingers, not your eyes.

- **Work in order.** Level 4 depends on the VPC exported in Level 3. Skipping breaks the chain on purpose, that's how real infrastructure dependencies work.
- **Always predict before you deploy.** Open the `<details>` block only *after* you've written down (even mentally) what you think will happen. Guessing wrong and finding out why is where the real learning happens, not reading the answer first.
- **Type the templates yourself for Levels 1–3.** After that, copy is fine, but modify something before you deploy it, even a tag value, so you're never running code you don't understand.
- **Always run `aws cloudformation validate-template` before `deploy`.** Make this muscle memory now; it's what separates hobbyists from production engineers.
- **Tear down after every level** using the `delete-stack` command given at the end of each level. AWS billing does not care that you were "just learning."
- **Keep a "scar log."** Every error message you hit, paste it into a personal notes file with the fix. This becomes your own troubleshooting playbook, more valuable than this guide by Level 10.
- **The Curiosity Gap is intentional.** If a level ends with an unanswered "but what happens when...?", resist searching it online immediately. Sit with it for a minute. Then go build the next level and find out.

### Prerequisites

| Requirement | Why |
|---|---|
| AWS account (Free Tier eligible) | To actually deploy, reading alone won't build the intuition |
| AWS CLI v2 installed & configured (`aws configure`) | All deployments in this guide are CLI-first, not console-first |
| A text editor (VS Code recommended) with YAML extension | Syntax highlighting catches indentation errors early |
| Basic terminal comfort (`cd`, `mkdir`, `cat`) | No prior AWS or IaC experience required |
| ~$0–2 total cost if you tear down after each level | Everything here fits Free Tier if cleaned up promptly |

---

## 🗺️ The 10 Levels at a Glance

| Level | Theme | You Will Build | New Concepts |
|---|---|---|---|
| 1 | Foundations | A single, self-describing S3 bucket | Template anatomy, Resources, stack lifecycle |
| 2 | Making It Reusable | A parameterized web-hosting bucket | Parameters, `Ref`, `AllowedValues`, NoEcho |
| 3 | Environment Awareness | A VPC that adapts to region & environment | Mappings, Conditions, Pseudo Parameters |
| 4 | Talking Between Stacks | A networking stack other stacks depend on | Outputs, `Export`/`Fn::ImportValue`, cross-stack design |
| 5 | Compute & Wiring | An EC2 instance with a live web server | Security Groups, `Fn::GetAtt`, `Fn::Sub`, UserData |
| 6 | Composition | The same architecture, broken into reusable pieces | Nested Stacks, `AWS::CloudFormation::Stack` |
| 7 | Dynamic Intelligence | A stack that looks up its own AMI at deploy time | Custom Resources, Lambda-backed resources, `SSM Parameter` lookups |
| 8 | Production Safety | Safe, reviewable, auditable changes | Change Sets, Stack Policies, Drift Detection, Termination Protection |
| 9 | Full Architecture | A real 3-tier production app (ALB + ASG + RDS Multi-AZ) | StackSets thinking, `DependsOn`, Deletion Policies, Rollback Triggers |
| 10 | Operating It Like a Pro | CI/CD pipeline that deploys your stacks on every git push | CodePipeline + CodeBuild + CloudFormation, governance, Well-Architected review |

---

# LEVEL 1, Foundations: Your First Stack

### 🎬 The Scenario

You've been asked to provision an S3 bucket for a teammate, "just a bucket, nothing fancy." You could click "Create Bucket" in the console in 10 seconds. But you won't, because a bucket created by hand has no history, no version control, and no way to be recreated identically in another account. You will instead write a **template**: a text file that *is* the infrastructure's source of truth.

### 🔮 Prediction Point #1

Before deploying anything, answer this: **If you delete the CloudFormation stack, what happens to the S3 bucket it created?**

<details>
<summary>🔎 Click to reveal answer (only after you've made your own guess)</summary>

By default, CloudFormation **deletes the S3 bucket along with the stack**, but only if the bucket is *empty*. If the bucket has objects in it, the delete will **fail**, and the stack will be stuck in `DELETE_FAILED` state. This is your first taste of CloudFormation's default behavior: **the stack owns the resource's entire lifecycle unless you explicitly tell it otherwise** (you'll meet `DeletionPolicy` properly in Level 9).
</details>

### 🛠️ Step-by-Step Build

**Step 1, Create your project folder**

```bash
mkdir -p ~/cfn-mastery/level-01-foundations
cd ~/cfn-mastery/level-01-foundations
```

**Step 2, Create the template file**

```bash
touch bucket.yaml
```

**Step 3, Write the template**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: >
  Level 1 - A single S3 bucket. The simplest possible CloudFormation stack,
  used to learn template anatomy and the stack lifecycle.

Resources:
  MyFirstBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'cfn-mastery-level1-${AWS::AccountId}'
      Tags:
        - Key: Project
          Value: CloudFormation-Mastery
        - Key: Level
          Value: '1'
```

**Step 4, Validate before you deploy (always do this)**

```bash
aws cloudformation validate-template --template-body file://bucket.yaml
```

**Step 5, Deploy the stack**

```bash
aws cloudformation deploy \
  --template-file bucket.yaml \
  --stack-name level1-foundations
```

**Step 6, Confirm it exists**

```bash
aws cloudformation describe-stacks --stack-name level1-foundations --query 'Stacks[0].StackStatus'
aws s3 ls | grep cfn-mastery-level1
```

### 🔍 Observation Point #1

Run this command and study the output carefully:

```bash
aws cloudformation describe-stack-events --stack-name level1-foundations --max-items 5
```

**Question: Why does the event log show TWO `CREATE_COMPLETE` events, one for the bucket, and one for the stack itself?**

<details>
<summary>🔎 Click to reveal answer</summary>

Because a **stack** and a **resource** are two different things in CloudFormation's model. The stack is a *management wrapper*, a logical container that tracks state, ordering, and rollback behavior. Every individual resource inside it (here, just the bucket) gets its own lifecycle events, and only once **all** resources reach `CREATE_COMPLETE` does the **stack itself** flip to `CREATE_COMPLETE`. This distinction, stack vs. resource, becomes critical later when a stack contains 20+ resources and you need to know exactly which one failed.
</details>

### 📖 Template Breakdown

| Line / Block | What It Does | Why It Matters |
|---|---|---|
| `AWSTemplateFormatVersion` | Declares the template spec version | Always `'2010-09-09'`, it's the only version that has ever existed, but AWS requires it explicitly |
| `Description` | Human-readable summary | Shows up in the console; good practice for team handoff |
| `Resources` | The **only mandatory top-level section** | Every template must declare at least one resource |
| `MyFirstBucket` | The **logical ID** | This is a name *you* choose, it exists only inside the template, not in AWS itself |
| `Type: AWS::S3::Bucket` | The **resource type** | Tells CloudFormation which AWS service API to call |
| `!Sub` | An intrinsic function (shorthand for `Fn::Sub`) | Substitutes `${AWS::AccountId}` with your real account ID at deploy time, guaranteeing a globally unique bucket name |
| `${AWS::AccountId}` | A **Pseudo Parameter** | A built-in variable CloudFormation provides, no declaration needed (more in Level 3) |
| `Tags` | Resource metadata | Enables cost allocation and governance, a production non-negotiable, introduced here as a habit from day one |

### 🕳️ Curiosity Gap

You hardcoded `Level: '1'` as a tag. What if you wanted this **exact same template** to create a bucket for Level 2, Level 3, and so on, without editing the file every time? Right now, you'd have to open the file and manually change the value before every deploy. That's not "Infrastructure as Code", that's "Infrastructure as Copy-Paste." There has to be a way to feed values into a template from the **outside**, at deploy time.

*(That's exactly what Level 2 solves.)*

### 🧪 Challenge

Before moving on, modify `bucket.yaml` yourself to add **versioning** to the bucket (hint: `VersioningConfiguration`), redeploy with `aws cloudformation deploy`, and confirm via `aws s3api get-bucket-versioning`.

### 🧹 Tear Down

```bash
aws s3 rm s3://cfn-mastery-level1-<your-account-id> --recursive
aws cloudformation delete-stack --stack-name level1-foundations
```

---

# LEVEL 2, Making It Reusable: Parameters

### 🎬 The Scenario

Your teammate liked the bucket so much they now want **one for every project**, Level 2, Level 3, Level 4 buckets, all from the same template, with the level number supplied at deploy time. You will also add a **static website configuration**, which means for the first time your template needs to make a *choice* based on input.

### 🔮 Prediction Point #2

**If you declare a Parameter but never pass a value for it at deploy time, and it has no `Default`, what happens?**

<details>
<summary>🔎 Click to reveal answer</summary>

CloudFormation will **not deploy**, it will pause and interactively prompt you for the missing value in the CLI, or, in the console, refuse to proceed past the "Configure stack" screen until every parameter without a default is filled in. Parameters without defaults are **required inputs**, not optional ones.
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-02-parameters
cd ~/cfn-mastery/level-02-parameters
touch website-bucket.yaml
```

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 2 - A parameterized static website bucket.

Parameters:
  ProjectLevel:
    Type: String
    Description: Which level of the guide this bucket belongs to.
    Default: '2'

  EnableWebsiteHosting:
    Type: String
    Description: Whether to enable static website hosting on this bucket.
    AllowedValues:
      - 'true'
      - 'false'
    Default: 'true'

  IndexDocumentName:
    Type: String
    Description: The default page served when visitors hit the site root.
    Default: 'index.html'
    MinLength: 1
    MaxLength: 64

Conditions:
  ShouldHostWebsite: !Equals [!Ref EnableWebsiteHosting, 'true']

Resources:
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'cfn-mastery-level${ProjectLevel}-${AWS::AccountId}'
      WebsiteConfiguration:
        !If
          - ShouldHostWebsite
          - IndexDocument: !Ref IndexDocumentName
          - !Ref 'AWS::NoValue'
      Tags:
        - Key: Project
          Value: CloudFormation-Mastery
        - Key: Level
          Value: !Ref ProjectLevel

Outputs:
  BucketWebsiteURL:
    Description: The website endpoint, if hosting was enabled.
    Value: !If
      - ShouldHostWebsite
      - !GetAtt WebsiteBucket.WebsiteURL
      - 'Website hosting disabled for this bucket'
```

**Deploy with an overridden parameter:**

```bash
aws cloudformation validate-template --template-body file://website-bucket.yaml

aws cloudformation deploy \
  --template-file website-bucket.yaml \
  --stack-name level2-parameters \
  --parameter-overrides ProjectLevel=2 EnableWebsiteHosting=true
```

**Fetch the output:**

```bash
aws cloudformation describe-stacks \
  --stack-name level2-parameters \
  --query 'Stacks[0].Outputs'
```

### 🔍 Observation Point #2

Redeploy the **same stack** with `EnableWebsiteHosting=false`:

```bash
aws cloudformation deploy \
  --template-file website-bucket.yaml \
  --stack-name level2-parameters \
  --parameter-overrides ProjectLevel=2 EnableWebsiteHosting=false
```

**Question: Does CloudFormation delete the bucket and create a new one, or does it modify the existing bucket in place?**

<details>
<summary>🔎 Click to reveal answer</summary>

It **modifies in place**, you'll see an `UPDATE_IN_PROGRESS` → `UPDATE_COMPLETE` cycle, not a delete/create cycle. CloudFormation is smart enough to recognize that changing `WebsiteConfiguration` doesn't require replacing the whole bucket (some property changes *do* force replacement, you'll hit that head-on in Level 5). This "update in place when possible" behavior is core to how CloudFormation minimizes blast radius on production resources.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Parameters block** | `Parameters:` | Declares external inputs the template accepts |
| **Type constraint** | `Type: String` | CloudFormation validates input type before deploy even starts |
| **Allowed values** | `AllowedValues: ['true','false']` | Rejects invalid input at validation time, not deploy time, fail fast |
| **Default** | `Default: '2'` | Makes a parameter optional |
| **Ref (parameter)** | `!Ref ProjectLevel` | Retrieves the *value* passed in for that parameter |
| **Conditions block** | `Conditions:` | Declares named boolean expressions you can reuse |
| **Fn::Equals** | `!Equals [!Ref EnableWebsiteHosting, 'true']` | Compares a parameter's value to a literal |
| **Fn::If** | `!If [ConditionName, valueIfTrue, valueIfFalse]` | Branches a **property's value** based on a condition |
| **AWS::NoValue** | `!Ref 'AWS::NoValue'` | A special pseudo-value meaning "omit this property entirely", not `null`, not empty string, but *absent* |
| **Fn::GetAtt** | `!GetAtt WebsiteBucket.WebsiteURL` | Retrieves an *attribute* of a deployed resource (not something you set, something AWS generates) |

### 🕳️ Curiosity Gap

Notice that `EnableWebsiteHosting` is a `String` with `AllowedValues: ['true','false']`, not a real Boolean. CloudFormation's parameter types don't include a native boolean. That's a quirk you'll carry with you. But here's the bigger gap: what if the **bucket's own configuration should differ depending on which AWS region or environment (dev vs. prod) it's deployed into**, not because someone typed a parameter, but because you, the template author, already know the right values for each region? Passing 15 parameters by hand every time isn't scalable. There must be a way to bake **known reference tables** directly into the template.

*(Mappings, Level 3.)*

### 🧪 Challenge

Add a third `AllowedValue` scenario: introduce a new Parameter called `BucketAccessLevel` (`Private` / `PublicRead`) and use a `Condition` to conditionally attach a bucket policy only when `PublicRead` is chosen. Think carefully about why public S3 buckets are a production red flag, you'll revisit this exact tension in Level 8 (Stack Policies) and Level 10 (Governance).

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level2-parameters
```

---

# LEVEL 3, Environment Awareness: Mappings, Conditions & Pseudo Parameters

### 🎬 The Scenario

Time to move past S3 and build your first **network**, a VPC. But this VPC needs to behave differently depending on two things you don't control at template-write time: **which AWS region** it lands in, and **whether it's a dev or prod environment**. Dev environments should get a smaller CIDR range and no NAT Gateway (save cost); prod should get a larger range and Multi-AZ NAT. This is where CloudFormation stops being "a script" and starts being "a decision engine."

### 🔮 Prediction Point #3

**If your `Mappings` block only has entries for `us-east-1` and `eu-west-1`, and you deploy this stack in `ap-southeast-1`, what happens?**

<details>
<summary>🔎 Click to reveal answer</summary>

The stack **fails immediately at the `CREATE_FAILED` stage** with an error like `Fn::FindInMap: Key ap-southeast-1 not found`. Mappings are **not dynamic lookups against AWS**, they are a **static dictionary you hardcode**, and if a key is missing, CloudFormation cannot fall back to a default. This is a real limitation you must design around (some teams use Custom Resources, Level 7, to solve this properly).
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-03-environment-vpc
cd ~/cfn-mastery/level-03-environment-vpc
touch vpc.yaml
```

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 3 - An environment-aware VPC using Mappings, Conditions, and Pseudo Parameters.

Parameters:
  EnvironmentType:
    Type: String
    Description: Deployment environment. Drives sizing and cost-related decisions.
    AllowedValues: [dev, prod]
    Default: dev

Mappings:
  EnvironmentConfig:
    dev:
      VpcCidr: '10.10.0.0/16'
      PublicSubnetCidr: '10.10.1.0/24'
      EnableNatGateway: 'false'
    prod:
      VpcCidr: '10.20.0.0/16'
      PublicSubnetCidr: '10.20.1.0/24'
      EnableNatGateway: 'true'

Conditions:
  IsProduction: !Equals [!Ref EnvironmentType, 'prod']

Resources:
  MainVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, VpcCidr]
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentType}-vpc-${AWS::Region}'
        - Key: Environment
          Value: !Ref EnvironmentType

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, PublicSubnetCidr]
      AvailabilityZone: !Select [0, !GetAZs !Ref 'AWS::Region']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentType}-public-subnet'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Condition: IsProduction
    Tags:
      - Key: Name
        Value: !Sub '${EnvironmentType}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Condition: IsProduction
    Properties:
      VpcId: !Ref MainVPC
      InternetGatewayId: !Ref InternetGateway

Outputs:
  VpcId:
    Description: The ID of the created VPC
    Value: !Ref MainVPC

  DeployedRegion:
    Description: The AWS region this stack was deployed into
    Value: !Ref 'AWS::Region'

  AccountId:
    Description: The AWS account this stack belongs to
    Value: !Ref 'AWS::AccountId'
```

**Deploy for dev:**

```bash
aws cloudformation validate-template --template-body file://vpc.yaml

aws cloudformation deploy \
  --template-file vpc.yaml \
  --stack-name level3-vpc-dev \
  --parameter-overrides EnvironmentType=dev
```

### 🔍 Observation Point #3

Now deploy a **second, independent stack** for prod, in the same account:

```bash
aws cloudformation deploy \
  --template-file vpc.yaml \
  --stack-name level3-vpc-prod \
  --parameter-overrides EnvironmentType=prod
```

Check resources created:

```bash
aws cloudformation describe-stack-resources --stack-name level3-vpc-dev --query 'StackResources[].ResourceType'
aws cloudformation describe-stack-resources --stack-name level3-vpc-prod --query 'StackResources[].ResourceType'
```

**Question: Why does the `dev` stack have 2 resources but the `prod` stack has 4, from the exact same template?**

<details>
<summary>🔎 Click to reveal answer</summary>

Because of the `Condition: IsProduction` attached to `InternetGateway` and `AttachGateway`. When `EnvironmentType=dev`, `IsProduction` evaluates to `false`, so CloudFormation **skips creating those two resources entirely**, they don't exist as "disabled" resources, they simply aren't provisioned. This is the difference between `Fn::If` (Level 2, branches a *property value*) and a resource-level `Condition:` (branches whether the *entire resource* exists at all). One template, two genuinely different infrastructures, based purely on input.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Mappings** | `Mappings: EnvironmentConfig: dev: {...}` | A static, nested lookup table keyed by a string you control |
| **Fn::FindInMap** | `!FindInMap [MapName, TopLevelKey, SecondLevelKey]` | Retrieves a value from a Mapping, a 3-argument function, always in that order |
| **Resource-level Condition** | `Condition: IsProduction` (on the resource itself) | Whether the *entire resource* is created, not just one property |
| **Fn::GetAZs** | `!GetAZs !Ref 'AWS::Region'` | Returns the list of Availability Zones for a region, dynamic, not hardcoded |
| **Fn::Select** | `!Select [0, !GetAZs ...]` | Picks a specific index out of a list returned by another function |
| **Pseudo Parameter: AWS::Region** | `!Ref 'AWS::Region'` | The region the stack is being deployed into, never declared, always available |
| **Pseudo Parameter: AWS::AccountId** | `!Ref 'AWS::AccountId'` | The account ID, used for naming uniqueness and ARNs |

### 🕳️ Curiosity Gap

You now have **two separate stacks**, `level3-vpc-dev` and `level3-vpc-prod`, sitting in isolation. Each has a `VpcId` in its Outputs. But what if you now want to launch an EC2 instance that needs to know the dev VPC's ID and subnet, from a **completely different template file**? You *could* copy the VPC ID by hand and paste it as a parameter. But hardcoding a resource ID that could change (if you ever rebuild the VPC) is exactly the kind of fragile coupling Infrastructure as Code exists to eliminate.

*(That's the cross-stack reference problem, solved in Level 4.)*

### 🧪 Challenge

Add a `staging` key to `EnvironmentConfig` with its own CIDR ranges, add `staging` to `AllowedValues`, and deploy a third parallel stack: `level3-vpc-staging`. Confirm all three VPCs have non-overlapping CIDRs (a real production requirement if you ever peer them).

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level3-vpc-dev
aws cloudformation delete-stack --stack-name level3-vpc-prod
```

---

# LEVEL 4, Talking Between Stacks: Outputs, Export & ImportValue

### 🎬 The Scenario

You will now build a **networking stack** whose entire purpose is to be depended on by other stacks, exactly how real organizations separate "platform team" infrastructure (VPCs, shared subnets) from "application team" infrastructure (EC2s, databases). This is the first time you'll deploy **two templates that know about each other**.

### 🔮 Prediction Point #4

**If Stack A exports a value and Stack B imports it, then you try to delete Stack A while Stack B still exists, what happens?**

<details>
<summary>🔎 Click to reveal answer</summary>

CloudFormation will **refuse to delete Stack A**, throwing an error like `Export ... cannot be deleted as it is in use by...`. This is a hard safety rail: **you cannot delete an exported value while any stack still imports it.** You must delete the *importing* stack (B) first, or modify it to stop importing the value, before Stack A can be torn down. This ordering constraint is a real production gotcha, teams have been blocked for hours during incident response because of export dependencies they forgot existed.
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-04-cross-stack
cd ~/cfn-mastery/level-04-cross-stack
touch network-stack.yaml app-stack.yaml
```

**Template 1, the exporting "platform" stack:**

```yaml
# network-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 4 - Networking stack that exports values for other stacks to consume.

Resources:
  SharedVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: '10.40.0.0/16'
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: shared-vpc

  PublicSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref SharedVPC
      CidrBlock: '10.40.1.0/24'
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: shared-public-subnet-a

Outputs:
  VpcId:
    Description: Shared VPC ID
    Value: !Ref SharedVPC
    Export:
      Name: NetworkStack-VpcId

  PublicSubnetAId:
    Description: Shared public subnet ID
    Value: !Ref PublicSubnetA
    Export:
      Name: NetworkStack-PublicSubnetAId
```

**Template 2, the importing "application" stack:**

```yaml
# app-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 4 - App stack that imports networking values from another stack.

Resources:
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for the app tier, using an imported VPC.
      VpcId: !ImportValue NetworkStack-VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: app-sg-from-imported-vpc

Outputs:
  SecurityGroupId:
    Description: The Security Group created inside the imported VPC
    Value: !Ref AppSecurityGroup
```

**Deploy in the correct order (this order matters):**

```bash
aws cloudformation deploy --template-file network-stack.yaml --stack-name level4-network
aws cloudformation deploy --template-file app-stack.yaml --stack-name level4-app
```

### 🔍 Observation Point #4

Try deploying `app-stack.yaml` **before** `network-stack.yaml` (delete both stacks first, then flip the order):

```bash
aws cloudformation deploy --template-file app-stack.yaml --stack-name level4-app-test
```

**Question: What error do you get, and what does it tell you about how `Fn::ImportValue` resolves?**

<details>
<summary>🔎 Click to reveal answer</summary>

You'll get: `No export named NetworkStack-VpcId found`. This proves that `Fn::ImportValue` is resolved **at deploy time, against the live state of your account**, not against the template file. CloudFormation doesn't know or care that `network-stack.yaml` exists on your disk; it only cares whether an **export with that exact name currently exists anywhere in that AWS region and account**. This also means export names must be **globally unique per account+region**, a naming collision between two unrelated teams' stacks is a real-world failure mode.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Outputs + Export** | `Export: Name: NetworkStack-VpcId` | Publishes a value to a region-and-account-wide namespace, not just this stack |
| **Fn::ImportValue** | `!ImportValue NetworkStack-VpcId` | Pulls a value published by *any* stack's Export, by name |
| **Cross-stack coupling** | (implicit) | Creates a hard dependency: the exporting stack cannot be deleted while imported |
| **`!GetAZs ''`** | Empty string argument | An idiom meaning "use the region this template is being deployed into", same effect as passing `!Ref 'AWS::Region'` |

### 🕳️ Curiosity Gap

You now have two hand-wired templates connected by string-based export names, `"NetworkStack-VpcId"` is just text; a typo anywhere breaks the link silently until deploy time. As your architecture grows to 5, 10, 20 interdependent stacks (VPC, security groups, load balancer, database, compute), managing this web of Export/Import names by hand becomes its own maintenance burden. What if instead, a **parent template** could own child templates directly, passing values between them **without publishing anything account-wide** at all?

*(Nested Stacks, Level 6. But first, Level 5 gives you real compute to nest.)*

### 🧪 Challenge

Add a second export to `network-stack.yaml`: export the VPC's CIDR block too (`Fn::GetAtt` won't give you this, use `!Ref` on a Parameter you introduce, or hardcode and export it). Then modify `app-stack.yaml` to output that CIDR back out via `!ImportValue`, proving the round-trip works.

### 🧹 Tear Down (app stack first, this order is mandatory)

```bash
aws cloudformation delete-stack --stack-name level4-app
aws cloudformation delete-stack --stack-name level4-network
```

---

# LEVEL 5, Compute & Wiring: EC2, Security Groups & Intrinsic Functions

### 🎬 The Scenario

Static infrastructure is done. Now you deploy **actual compute**, an EC2 instance running a live web server, provisioned entirely through UserData baked into the template, sitting inside a Security Group that only you define. This is the level where CloudFormation starts to feel like real infrastructure engineering.

### 🔮 Prediction Point #5

**You change the EC2 instance's `ImageId` (AMI) in the template and redeploy. Will CloudFormation update the existing instance in place, or replace it entirely?**

<details>
<summary>🔎 Click to reveal answer</summary>

It will **replace the instance entirely**, terminate the old one, launch a new one with a new Instance ID. `ImageId` is one of several EC2 properties CloudFormation classifies as requiring **replacement**, not in-place update, because you cannot change the base image of a running instance at the hypervisor level. This is a critical distinction: **some property changes are safe updates, others are destructive replacements**, and CloudFormation tells you which, in the Change Set (Level 8), *before* you commit to it.
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-05-compute
cd ~/cfn-mastery/level-05-compute
touch webserver.yaml
```

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 5 - EC2 web server with Security Group and UserData bootstrapping.

Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
    Description: Always resolves to the latest Amazon Linux 2023 AMI at deploy time.

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t2.micro]

Resources:
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow HTTP and SSH inbound traffic
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: level5-web-sg

  WebServerInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref LatestAmiId
      SecurityGroups:
        - !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: level5-web-server
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          dnf install -y httpd
          systemctl enable httpd
          systemctl start httpd
          echo "<h1>Deployed by CloudFormation - Level 5</h1>" > /var/www/html/index.html
          echo "<p>Instance region: ${AWS::Region}</p>" >> /var/www/html/index.html

Outputs:
  PublicIp:
    Description: Public IP of the web server
    Value: !GetAtt WebServerInstance.PublicIp

  WebsiteURL:
    Description: Direct URL to the deployed website
    Value: !Sub 'http://${WebServerInstance.PublicIp}'
```

```bash
aws cloudformation validate-template --template-body file://webserver.yaml

aws cloudformation deploy \
  --template-file webserver.yaml \
  --stack-name level5-webserver
```

Wait ~2 minutes for boot, then check:

```bash
aws cloudformation describe-stacks --stack-name level5-webserver --query 'Stacks[0].Outputs'
curl $(aws cloudformation describe-stacks --stack-name level5-webserver --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text)
```

### 🔍 Observation Point #5

Change only `InstanceType` from `t3.micro` to `t3.small` and redeploy:

```bash
aws cloudformation deploy --template-file webserver.yaml --stack-name level5-webserver \
  --parameter-overrides InstanceType=t3.small
```

**Question: Does the Public IP in the Outputs change after this update?**

<details>
<summary>🔎 Click to reveal answer</summary>

**Yes, it changes**, `InstanceType` can be updated in place for many instance families, but the **public IP is not guaranteed to persist** across a stop/start cycle unless you're using an Elastic IP. CloudFormation performs this as a "stop, resize, start" operation under the hood for compatible type changes, and AWS reassigns a new public IPv4 address on start unless one was reserved. This is why production architectures almost never rely on raw instance public IPs, they sit behind an Elastic Load Balancer (which you'll build in Level 9) or use an Elastic IP resource explicitly.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **SSM Parameter type** | `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>` | A special Parameter type that resolves against a **live AWS Systems Manager Parameter Store value** at deploy time, always gets the current AMI without you tracking IDs |
| **Fn::Base64** | `UserData: Fn::Base64: !Sub \| ...` | EC2 requires UserData to be base64-encoded; this function does it for you inline |
| **Fn::Sub with multi-line block** | `!Sub \|` (YAML block scalar) | Lets you substitute variables inside a full shell script |
| **`${AWS::Region}` inside UserData** | Substituted before the script ever reaches the instance | Proves Fn::Sub resolves at **template render time**, not at instance boot time |
| **Fn::GetAtt (runtime attribute)** | `!GetAtt WebServerInstance.PublicIp` | An attribute only known *after* the instance exists, impossible to know at template-write time |

### 🕳️ Curiosity Gap

You now have exactly **one** web server. If it crashes, your website goes down, nobody is watching it, nothing replaces it. Also: this template and the VPC/networking template from Level 4 are two separate, unrelated files that don't know about each other yet. A single production environment realistically needs a VPC, subnets, security groups, EC2 (or an Auto Scaling Group), and probably a database, all wired together. Copy-pasting this EC2 block into every future template is exactly the kind of duplication Infrastructure as Code is supposed to eliminate.

*(Nested Stacks solve the duplication problem, Level 6.)*

### 🧪 Challenge

Add an `AWS::EC2::EIP` resource, associate it with `WebServerInstance` using `AWS::EC2::EIPAssociation`, redeploy, and re-run the instance-type-change test from Observation Point #5. Confirm the public IP now stays the same.

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level5-webserver
```

---

# LEVEL 6, Composition: Nested Stacks

### 🎬 The Scenario

You will now take the VPC (Level 3) and the Web Server (Level 5) and combine them into **one coherent deployment**, but instead of copy-pasting one giant YAML file, you'll split it into three reusable template files, a **network template**, a **compute template**, and a **root/parent template** that stitches them together using `AWS::CloudFormation::Stack`. This is how real platform teams build a library of reusable building blocks.

### 🔮 Prediction Point #6

**When you deploy a parent stack that contains two nested stacks, and you check `aws cloudformation list-stacks`, how many stacks will you actually see?**

<details>
<summary>🔎 Click to reveal answer</summary>

**Three**, the parent stack, plus one **child stack per nested template**, each with an auto-generated name like `ParentStackName-NestedLogicalId-A1B2C3D4E5`. Nested stacks are **real, independent CloudFormation stacks** under the hood, each with their own events, resources, and status, they are simply *owned and orchestrated* by the parent. This is different from a "module" in other IaC tools; in CloudFormation, nesting means genuinely creating more stacks.
</details>

### 🛠️ Step-by-Step Build

Nested stack templates must be uploaded to S3 before the parent can reference them.

```bash
mkdir -p ~/cfn-mastery/level-06-nested/templates
cd ~/cfn-mastery/level-06-nested
```

**`templates/network.yaml`** (trimmed version of Level 3's VPC, now designed to be nested):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 6 - Nested network template.

Resources:
  NestedVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: '10.60.0.0/16'
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: level6-nested-vpc

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref NestedVPC
      CidrBlock: '10.60.1.0/24'
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

Outputs:
  VpcId:
    Value: !Ref NestedVPC
  SubnetId:
    Value: !Ref PublicSubnet
```

**`templates/compute.yaml`** (accepts VPC/Subnet as Parameters instead of ImportValue):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 6 - Nested compute template, wired via parent-passed parameters.

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
  SubnetId:
    Type: AWS::EC2::Subnet::Id
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64

Resources:
  ComputeSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Nested compute SG
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  WebInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: !Ref LatestAmiId
      SubnetId: !Ref SubnetId
      SecurityGroupIds:
        - !Ref ComputeSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          dnf install -y httpd
          systemctl enable httpd
          systemctl start httpd
          echo "<h1>Level 6 - Nested Stack Compute</h1>" > /var/www/html/index.html

Outputs:
  InstancePublicIp:
    Value: !GetAtt WebInstance.PublicIp
```

**`root.yaml`** (the parent template):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 6 - Parent template composing network + compute nested stacks.

Parameters:
  TemplateBucketName:
    Type: String
    Description: S3 bucket where child templates are stored.

Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucketName}.s3.amazonaws.com/network.yaml'
      TimeoutInMinutes: 10

  ComputeStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucketName}.s3.amazonaws.com/compute.yaml'
      Parameters:
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        SubnetId: !GetAtt NetworkStack.Outputs.SubnetId
      TimeoutInMinutes: 10

Outputs:
  WebsitePublicIp:
    Value: !GetAtt ComputeStack.Outputs.InstancePublicIp
```

**Upload child templates, then deploy the parent:**

```bash
BUCKET_NAME="cfn-mastery-templates-$(aws sts get-caller-identity --query Account --output text)"
aws s3 mb s3://$BUCKET_NAME
aws s3 cp templates/network.yaml s3://$BUCKET_NAME/network.yaml
aws s3 cp templates/compute.yaml s3://$BUCKET_NAME/compute.yaml

aws cloudformation deploy \
  --template-file root.yaml \
  --stack-name level6-nested-root \
  --parameter-overrides TemplateBucketName=$BUCKET_NAME
```

### 🔍 Observation Point #6

```bash
aws cloudformation list-stacks --query 'StackSummaries[?contains(StackName, `level6`)].{Name:StackName,Status:StackStatus}'
```

**Question: Notice `ComputeStack` has `DependsOn: NetworkStack` explicitly written, but wouldn't CloudFormation already know ComputeStack depends on NetworkStack, since it references `!GetAtt NetworkStack.Outputs.VpcId`?**

<details>
<summary>🔎 Click to reveal answer</summary>

You're right that CloudFormation **would** infer the dependency automatically from the `!GetAtt` reference, `DependsOn` here is technically redundant for ordering purposes. It's included as a **teaching example** and as **defensive documentation**: explicit `DependsOn` is valuable when a dependency exists that CloudFormation *cannot* infer from references alone, for example, "this IAM policy must exist before this Lambda executes, even though nothing in the Lambda's properties references the policy directly." Knowing when `DependsOn` is necessary vs. redundant is a genuine production skill, over-using it creates artificial serialization that slows down deployments unnecessarily.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Nested stack resource** | `Type: AWS::CloudFormation::Stack` | Treats an entire other template as a single resource in the parent |
| **TemplateURL** | Must point to an S3-hosted template | Nested stacks **cannot** reference local files, they must already be uploaded |
| **Cross-nested-stack data flow** | `!GetAtt NetworkStack.Outputs.VpcId` | Reads a **child stack's Output** as if it were any resource attribute, no Export/Import needed |
| **DependsOn** | `DependsOn: NetworkStack` | Forces explicit ordering, useful when no implicit reference exists |
| **Parameters passed to nested stack** | `Parameters: VpcId: !GetAtt ...` | The parent supplies input the same way you would with any deploy-time parameter |

### 🕳️ Curiosity Gap

You just manually uploaded templates to S3 with `aws s3 cp` before every deploy, a manual, error-prone step that's easy to forget (deploy the parent with stale child templates in S3 and you'll silently get the *old* infrastructure). Also: notice that the **AMI lookup** (`AWS::SSM::Parameter::Value<...>`) works because AWS *already* maintains that Parameter Store path for you. But what if **you** need a value that doesn't exist anywhere in AWS by default, say, the latest AMI *matching a custom filter*, or a value from a system outside AWS entirely? Parameters and Mappings can't call arbitrary code. Something else can.

*(Custom Resources, Level 7.)*

### 🧪 Challenge

Add a third nested stack, a `security.yaml` template that creates a standalone `AWS::EC2::SecurityGroup`, then modify `compute.yaml` to accept that Security Group ID as a Parameter instead of creating its own. This mirrors how real platform teams separate "network," "security," and "compute" ownership across different template authors.

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level6-nested-root
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME
```

---

# LEVEL 7, Dynamic Intelligence: Custom Resources

### 🎬 The Scenario

Sometimes CloudFormation simply doesn't have a native resource type for what you need, or you need a value computed by logic no intrinsic function can express. In this level, you build a **Lambda-backed Custom Resource** that queries the *current* running AMIs matching specific filters (not just "latest Amazon Linux," but "latest Amazon Linux with a specific tag"), something no plain SSM Parameter path provides.

### 🔮 Prediction Point #7

**A Custom Resource's Lambda function fails (throws an error) during stack creation. What does the overall stack do?**

<details>
<summary>🔎 Click to reveal answer</summary>

The stack rolls back, **but only if the Lambda function correctly sends a `FAILED` response back to CloudFormation.** If your Lambda crashes *without* sending any response at all (e.g., it times out or throws an unhandled exception before calling the response URL), CloudFormation will **wait for the entire timeout period** (default up to 1 hour) before giving up, because it has no way of knowing the resource failed, it's still "waiting for a response." This is the single most common Custom Resource bug in production: forgetting to wrap your handler in a try/catch that guarantees a response is always sent, success or failure.
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-07-custom-resources
cd ~/cfn-mastery/level-07-custom-resources
touch custom-resource.yaml
```

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 7 - Custom Resource backed by Lambda to look up a filtered AMI.

Resources:
  AmiLookupFunctionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: DescribeImagesAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: ec2:DescribeImages
                Resource: '*'

  AmiLookupFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12
      Handler: index.handler
      Role: !GetAtt AmiLookupFunctionRole.Arn
      Timeout: 30
      Code:
        ZipFile: |
          import json
          import urllib.request
          import boto3

          def send_response(event, context, status, data):
              body = json.dumps({
                  "Status": status,
                  "Reason": f"See CloudWatch Logs: {context.log_stream_name}",
                  "PhysicalResourceId": context.log_stream_name,
                  "StackId": event["StackId"],
                  "RequestId": event["RequestId"],
                  "LogicalResourceId": event["LogicalResourceId"],
                  "Data": data
              }).encode("utf-8")
              req = urllib.request.Request(
                  url=event["ResponseURL"], data=body, method="PUT",
                  headers={"content-type": "", "content-length": str(len(body))}
              )
              urllib.request.urlopen(req)

          def handler(event, context):
              try:
                  if event["RequestType"] in ("Create", "Update"):
                      ec2 = boto3.client("ec2")
                      images = ec2.describe_images(
                          Owners=["amazon"],
                          Filters=[
                              {"Name": "name", "Values": ["al2023-ami-*-x86_64"]},
                              {"Name": "state", "Values": ["available"]}
                          ]
                      )["Images"]
                      images.sort(key=lambda i: i["CreationDate"], reverse=True)
                      ami_id = images[0]["ImageId"]
                      send_response(event, context, "SUCCESS", {"AmiId": ami_id})
                  else:
                      send_response(event, context, "SUCCESS", {})
              except Exception as e:
                  send_response(event, context, "FAILED", {"Error": str(e)})

  AmiLookupCustomResource:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !GetAtt AmiLookupFunction.Arn

Outputs:
  ResolvedAmiId:
    Description: The AMI ID discovered dynamically by the Custom Resource
    Value: !GetAtt AmiLookupCustomResource.AmiId
```

```bash
aws cloudformation validate-template --template-body file://custom-resource.yaml

aws cloudformation deploy \
  --template-file custom-resource.yaml \
  --stack-name level7-custom-resource \
  --capabilities CAPABILITY_IAM
```

### 🔍 Observation Point #7

```bash
aws cloudformation describe-stacks --stack-name level7-custom-resource --query 'Stacks[0].Outputs'
```

**Question: You had to add `--capabilities CAPABILITY_IAM` to this deploy command for the first time in the whole guide. Why wasn't it needed in Levels 1–6?**

<details>
<summary>🔎 Click to reveal answer</summary>

Because this is the **first template that creates an IAM Role**. CloudFormation requires you to **explicitly acknowledge** that a template will create IAM resources with permissions, as a safety mechanism against templates silently granting privileges you didn't review. Without `--capabilities CAPABILITY_IAM` (or `CAPABILITY_NAMED_IAM` if you name the role explicitly), the deploy is **rejected outright** with `InsufficientCapabilitiesException`, a deliberate friction point designed to make you pause and read the IAM policy before granting it.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Inline Lambda code** | `Code: ZipFile: \|` | Embeds small function code directly in the template, fine for short scripts, not for real applications (Level 10 uses CodeBuild for that) |
| **Custom Resource** | `Type: AWS::CloudFormation::CustomResource` | A resource whose entire behavior is defined by *your* Lambda function, not a built-in AWS service |
| **ServiceToken** | `!GetAtt AmiLookupFunction.Arn` | Tells CloudFormation which Lambda to invoke for Create/Update/Delete events on this resource |
| **RequestType handling** | `event["RequestType"]` | Every Custom Resource Lambda must handle `Create`, `Update`, **and** `Delete` explicitly, forgetting `Delete` leaves orphaned external resources behind |
| **send_response pattern** | `urllib.request` PUT to `ResponseURL` | The mandatory contract: every invocation **must** call back this URL or the stack hangs until timeout |
| **CAPABILITY_IAM** | CLI flag | An explicit safety acknowledgment required whenever a template creates IAM roles/policies |

### 🕳️ Curiosity Gap

Your Custom Resource works, but notice you deployed it directly with `aws cloudformation deploy`, by hand, from your own terminal, using your own IAM credentials. In a real team, nobody wants engineers running ad-hoc deploys from laptops, a stack update in prod should happen through a **reviewed, auditable, repeatable process**: someone opens a pull request, a second person reviews the *exact* infrastructure diff before it happens, and only then does it deploy. Right now, you have zero visibility into "what would this change actually do" before you commit to it.

*(Change Sets, the first stop in Level 8's production-safety toolkit.)*

### 🧪 Challenge

Modify the Lambda to also handle the `Delete` RequestType meaningfully, have it log the AMI ID it's "cleaning up" (even though there's nothing to actually delete in this case) to prove you understand that every Custom Resource lifecycle event needs explicit handling.

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level7-custom-resource
```

---

# LEVEL 8, Production Safety: Change Sets, Stack Policies & Drift Detection

### 🎬 The Scenario

You're no longer "just learning", from here on, treat every stack as if it were a real production system. This level introduces the three tools that separate hobbyist CloudFormation usage from professional operations: **Change Sets** (preview before you commit), **Stack Policies** (prevent accidental resource deletion/replacement), and **Drift Detection** (catch when someone manually changed something in the console, bypassing CloudFormation entirely).

### 🔮 Prediction Point #8

**Someone on your team manually changes a Security Group rule in the AWS Console instead of updating the CloudFormation template. Does CloudFormation notice, automatically fix it, or stay silent?**

<details>
<summary>🔎 Click to reveal answer</summary>

CloudFormation **stays completely silent**, it does not monitor your resources continuously. It only compares template-vs-reality **when you explicitly run a Drift Detection operation**. Until you do that, the stack will happily report `UPDATE_COMPLETE` and appear healthy, even though the real-world resource no longer matches what the template says it should be. This gap between "what CloudFormation thinks exists" and "what actually exists" is called **drift**, and it's one of the most common causes of "but the template says X!" incidents in real organizations.
</details>

### 🛠️ Step-by-Step Build

We'll reuse the Level 5 web server template for this exercise.

```bash
mkdir -p ~/cfn-mastery/level-08-production-safety
cd ~/cfn-mastery/level-08-production-safety
cp ~/cfn-mastery/level-05-compute/webserver.yaml .
```

**Step 1, Deploy the baseline stack:**

```bash
aws cloudformation deploy --template-file webserver.yaml --stack-name level8-safety
```

**Step 2, Attach a Stack Policy to prevent accidental resource replacement:**

```bash
cat > stack-policy.json << 'EOF'
{
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "Update:Replace",
      "Principal": "*",
      "Resource": "LogicalResourceId/WebServerInstance"
    },
    {
      "Effect": "Allow",
      "Action": "Update:*",
      "Principal": "*",
      "Resource": "*"
    }
  ]
}
EOF

aws cloudformation set-stack-policy \
  --stack-name level8-safety \
  --stack-policy-body file://stack-policy.json
```

**Step 3, Create a Change Set instead of deploying directly (edit `InstanceType` to `t3.small` first):**

```bash
aws cloudformation create-change-set \
  --stack-name level8-safety \
  --change-set-name test-instance-type-change \
  --template-body file://webserver.yaml \
  --parameters ParameterKey=InstanceType,ParameterValue=t3.small \
  --use-previous-template false

aws cloudformation describe-change-set \
  --stack-name level8-safety \
  --change-set-name test-instance-type-change \
  --query 'Changes[].ResourceChange.{Action:Action,Resource:LogicalResourceId,Replacement:Replacement}'
```

**Step 4, Now edit the template to change `ImageId` behavior (which forces replacement) and create another Change Set:**

```bash
aws cloudformation create-change-set \
  --stack-name level8-safety \
  --change-set-name test-ami-replacement \
  --template-body file://webserver.yaml \
  --parameters ParameterKey=InstanceType,ParameterValue=t3.micro \
  --use-previous-template false

aws cloudformation describe-change-set \
  --stack-name level8-safety \
  --change-set-name test-ami-replacement \
  --query 'Changes[].ResourceChange.{Action:Action,Resource:LogicalResourceId,Replacement:Replacement}'
```

**Step 5, Try to execute the replacement change set (this should be BLOCKED by your Stack Policy):**

```bash
aws cloudformation execute-change-set \
  --stack-name level8-safety \
  --change-set-name test-ami-replacement
```

**Step 6, Run Drift Detection:**

```bash
DRIFT_ID=$(aws cloudformation detect-stack-drift --stack-name level8-safety --query 'StackDriftDetectionId' --output text)
sleep 15
aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $DRIFT_ID
```

### 🔍 Observation Point #8

**Question: In Step 5, what exact error do you get, and why does the Stack Policy block this specific Change Set but would have allowed the InstanceType-only change from Step 3?**

<details>
<summary>🔎 Click to reveal answer</summary>

You'll see an error resembling: `Action denied by stack policy for resource "WebServerInstance"`. The `stack-policy.json` you wrote explicitly **denies** `Update:Replace` actions targeting `WebServerInstance`, while separately **allowing** all other update types (`Update:*`) on all resources (`Resource: "*"`). The InstanceType-only change (Step 3) was a **safe in-place update**, allowed. The AMI-driven change (Step 4) requires **replacement**, explicitly denied. This is exactly how production Stack Policies are used: not to block all changes, but to surgically protect specific stateful resources (a database, a long-running instance with local data) from being silently swapped out by a future template edit, while still allowing normal updates to flow through.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **Change Set** | `create-change-set` / `describe-change-set` | Computes and displays the *exact diff* CloudFormation would apply, **without applying it** |
| **Replacement field** | `Replacement: True/False/Conditional` | Tells you whether a proposed change is a safe update or a destructive replace-and-recreate |
| **Stack Policy** | JSON document via `set-stack-policy` | An IAM-like policy scoped to *stack update actions*, not AWS API calls in general |
| **`Update:Replace`** | Policy action | One of four update actions you can Allow/Deny: `Update:Modify`, `Update:Replace`, `Update:Delete`, `Update:*` |
| **Drift Detection** | `detect-stack-drift` | An on-demand comparison between template-declared state and live AWS state |
| **`execute-change-set`** | Separate step from creation | Deliberately two-phase: review, *then* commit, this separation is the entire point |

### 🕳️ Curiosity Gap

You've now protected a single EC2 instance from accidental replacement, and you can preview changes before committing. But so far every "production practice" in this level has been something **you** ran manually from your terminal. Real production environments deploy through **pipelines**, a `git push` triggers a build, which triggers a Change Set review, which (after approval) triggers an execute. And so far, everything you've built has been small, isolated pieces, a VPC here, an EC2 there. It's time to combine every concept from Levels 1–8 into **one real, multi-tier production architecture**, and then, in Level 10, wire it into a pipeline that deploys itself.

*(Level 9: the full build. Level 10: the pipeline.)*

### 🧪 Challenge

Add a second Stack Policy statement that also denies `Update:Delete` on `WebServerInstance`, then attempt to deploy a template version that *removes* the `WebServerInstance` resource entirely, and confirm the policy blocks the deletion.

### 🧹 Tear Down

```bash
# Stack Policies do NOT block stack deletion itself, only individual resource update actions
aws cloudformation delete-stack --stack-name level8-safety
```

---

# LEVEL 9, Full Architecture: A Real Production 3-Tier Application

### 🎬 The Scenario

Everything converges here. You will build a genuine production-pattern architecture in a **single, well-organized template**: a VPC with public and private subnets across two Availability Zones, an Application Load Balancer, an Auto Scaling Group of web servers in private subnets, and a Multi-AZ RDS database, with proper `DependsOn` ordering, `DeletionPolicy` protections on the database, and rollback safety nets. This is the architecture pattern behind a large percentage of real-world production web applications.

### 🔮 Prediction Point #9

**You set `DeletionPolicy: Snapshot` on your RDS instance, then delete the entire stack. What happens to the database, and what happens in your AWS account afterward?**

<details>
<summary>🔎 Click to reveal answer</summary>

The **stack deletes successfully**, and CloudFormation reports the RDS resource as deleted, **but AWS actually takes a final snapshot of the database first**, and that snapshot **persists in your account indefinitely**, completely independent of the stack. This is intentional: `DeletionPolicy: Snapshot` (and its cousin `DeletionPolicy: Retain`, which skips even the snapshot and just leaves the live resource running, orphaned from CloudFormation) exist specifically so that **tearing down infrastructure never means losing data by accident**. The tradeoff: you now have a snapshot silently costing you storage money that "delete stack" will never clean up for you, a real operational gotcha to track.
</details>

### 🛠️ Step-by-Step Build

```bash
mkdir -p ~/cfn-mastery/level-09-full-architecture
cd ~/cfn-mastery/level-09-full-architecture
touch production-app.yaml
```

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 9 - Full 3-tier production architecture (VPC, ALB, ASG, Multi-AZ RDS).

Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Master password for the RDS database (never logged or displayed).
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64

Resources:
  # ---------- NETWORK TIER ----------
  ProdVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: '10.90.0.0/16'
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags: [{Key: Name, Value: level9-prod-vpc}]

  PublicSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProdVPC
      CidrBlock: '10.90.1.0/24'
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PublicSubnetB:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProdVPC
      CidrBlock: '10.90.2.0/24'
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProdVPC
      CidrBlock: '10.90.11.0/24'
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnetB:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref ProdVPC
      CidrBlock: '10.90.12.0/24'
      AvailabilityZone: !Select [1, !GetAZs '']

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  GatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref ProdVPC
      InternetGatewayId: !Ref InternetGateway

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref ProdVPC

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: GatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: '0.0.0.0/0'
      GatewayId: !Ref InternetGateway

  PublicSubnetARouteAssoc:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnetA
      RouteTableId: !Ref PublicRouteTable

  PublicSubnetBRouteAssoc:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnetB
      RouteTableId: !Ref PublicRouteTable

  # ---------- SECURITY TIER ----------
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow inbound HTTP from the internet to the ALB
      VpcId: !Ref ProdVPC
      SecurityGroupIngress:
        - {IpProtocol: tcp, FromPort: 80, ToPort: 80, CidrIp: 0.0.0.0/0}

  WebTierSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow inbound HTTP only from the ALB security group
      VpcId: !Ref ProdVPC
      SecurityGroupIngress:
        - {IpProtocol: tcp, FromPort: 80, ToPort: 80, SourceSecurityGroupId: !Ref ALBSecurityGroup}

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow inbound MySQL only from the web tier
      VpcId: !Ref ProdVPC
      SecurityGroupIngress:
        - {IpProtocol: tcp, FromPort: 3306, ToPort: 3306, SourceSecurityGroupId: !Ref WebTierSecurityGroup}

  # ---------- COMPUTE TIER ----------
  WebLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        ImageId: !Ref LatestAmiId
        InstanceType: t3.micro
        SecurityGroupIds: [!Ref WebTierSecurityGroup]
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            dnf install -y httpd
            systemctl enable httpd
            systemctl start httpd
            echo "<h1>Level 9 Production Web Tier - $(hostname)</h1>" > /var/www/html/index.html

  WebAutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      VPCZoneIdentifier: [!Ref PrivateSubnetA, !Ref PrivateSubnetB]
      LaunchTemplate:
        LaunchTemplateId: !Ref WebLaunchTemplate
        Version: !GetAtt WebLaunchTemplate.LatestVersionNumber
      MinSize: '2'
      MaxSize: '4'
      DesiredCapacity: '2'
      TargetGroupARNs: [!Ref WebTargetGroup]

  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Subnets: [!Ref PublicSubnetA, !Ref PublicSubnetB]
      SecurityGroups: [!Ref ALBSecurityGroup]
      Type: application

  WebTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId: !Ref ProdVPC
      Port: 80
      Protocol: HTTP
      HealthCheckPath: /
      TargetType: instance

  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - {Type: forward, TargetGroupArn: !Ref WebTargetGroup}

  # ---------- DATA TIER ----------
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Private subnets for RDS
      SubnetIds: [!Ref PrivateSubnetA, !Ref PrivateSubnetB]

  ProductionDatabase:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      Engine: mysql
      DBInstanceClass: db.t3.micro
      AllocatedStorage: '20'
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      MultiAZ: true
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups: [!Ref DBSecurityGroup]
      BackupRetentionPeriod: 7

Outputs:
  LoadBalancerDNS:
    Description: Public DNS name of the Application Load Balancer
    Value: !GetAtt ApplicationLoadBalancer.DNSName
  DatabaseEndpoint:
    Description: RDS connection endpoint (private - only reachable from web tier)
    Value: !GetAtt ProductionDatabase.Endpoint.Address
```

```bash
aws cloudformation validate-template --template-body file://production-app.yaml

aws cloudformation deploy \
  --template-file production-app.yaml \
  --stack-name level9-production-app \
  --parameter-overrides DBPassword='ChangeMe12345!' \
  --capabilities CAPABILITY_IAM
```

*(This deploy takes 10–15 minutes, RDS Multi-AZ provisioning is slow by nature. Use the wait to re-read the template breakdown below.)*

### 🔍 Observation Point #9

```bash
aws cloudformation describe-stacks --stack-name level9-production-app --query 'Stacks[0].Outputs'
curl $(aws cloudformation describe-stacks --stack-name level9-production-app --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text)
```

**Question: `DBPassword` was passed on the command line in plain text, is that actually secure, and what does `NoEcho: true` protect against, specifically?**

<details>
<summary>🔎 Click to reveal answer</summary>

**No, it is not fully secure**, anyone with shell history access, or anyone watching your terminal, saw the password. `NoEcho: true` only protects one narrow thing: it prevents the value from being **displayed in the AWS Console, CLI describe-stacks output, and CloudFormation events/logs** after the fact, it masks it as `****` everywhere CloudFormation itself surfaces parameter values. It does **not** encrypt the value in transit, does **not** hide it from your shell history, and does **not** replace a real secrets manager. In genuine production, you'd pull `DBPassword` from **AWS Secrets Manager** or **SSM Parameter Store (SecureString)** via a dynamic reference (`{{resolve:secretsmanager:...}}`) instead of ever typing it on a command line at all, a pattern worth researching as your very next step beyond this guide.
</details>

### 📖 Template Breakdown

| Tier | Resources | Key Production Concepts |
|---|---|---|
| **Network** | VPC, 4 subnets across 2 AZs, IGW, Route Table | Multi-AZ from the start, single-AZ designs are a production anti-pattern |
| **Security** | 3 tiered Security Groups | Each tier only accepts traffic from the tier in front of it, `SourceSecurityGroupId` instead of open CIDRs, a real least-privilege pattern |
| **Compute** | Launch Template + Auto Scaling Group + ALB + Target Group | Instances live in **private** subnets, never directly internet-reachable; only the ALB is public |
| **Data** | RDS Multi-AZ + DB Subnet Group | `MultiAZ: true` = automatic failover to a standby in another AZ during an outage |
| **Safety** | `DeletionPolicy: Snapshot`, `UpdateReplacePolicy: Snapshot` | Guards data from both stack *deletion* and any future update that would force *replacement* |
| **NoEcho** | `NoEcho: true` on DBPassword | Masks the value from CloudFormation's own visible surfaces (not a full secrets solution) |

### 🕳️ Curiosity Gap

You just deployed a genuinely production-shaped architecture, but you did it by typing a password on a command line and running `aws cloudformation deploy` from your own laptop. No one reviewed this change. There's no record of *who* deployed *what* and *when*, beyond your own shell history. No automated tests ran against it. If you'd made a typo in a Security Group rule, nothing would have caught it before it reached "production." The entire discipline of DevOps exists to close exactly this gap.

*(Level 10: put this behind a pipeline.)*

### 🧪 Challenge

Add an `AWS::CloudWatch::Alarm` resource that watches the Auto Scaling Group's average CPU utilization and triggers a Scaling Policy to add an instance above 70% CPU. This is the single most common "make it actually production-ready" addition reviewers look for in this architecture.

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level9-production-app
# Remember: RDS DeletionPolicy: Snapshot means a snapshot will remain in your account.
aws rds describe-db-snapshots --query 'DBSnapshots[].DBSnapshotIdentifier'
# Manually delete it if you don't want to keep paying for snapshot storage:
# aws rds delete-db-snapshot --db-snapshot-identifier <name>
```

---

# LEVEL 10, Operating It Like a Pro: CI/CD, Governance & Well-Architected Review

### 🎬 The Scenario

The final level. You will wire your Level 9 architecture into a **CodePipeline** that automatically validates, creates a Change Set, and deploys your CloudFormation stack whenever you push a template change to a Git repository, with a manual approval gate before production changes execute. You'll also learn the governance guardrails real organizations layer on top of CloudFormation, and walk through a Well-Architected-style review of everything you've built across all 10 levels.

### 🔮 Prediction Point #10

**Your pipeline includes a manual approval step before executing the Change Set. If nobody approves it within 7 days, what happens to the pipeline execution?**

<details>
<summary>🔎 Click to reveal answer</summary>

By default, CodePipeline manual approval actions **timeout after 7 days** and the pipeline execution moves to a `Failed` state for that stage, nothing deploys, and you must **re-trigger the pipeline from the start** (e.g., with a new commit or manual release) rather than simply approving the stale action late. This is a deliberate safety design: an approval that sat unreviewed for a week likely no longer reflects the current state of the codebase, so CodePipeline refuses to let a week-old, unreviewed Change Set execute silently.
</details>

### 🛠️ Step-by-Step Build

**Step 1, Repository structure**

```bash
mkdir -p ~/cfn-mastery/level-10-cicd
cd ~/cfn-mastery/level-10-cicd
mkdir -p templates
cp ~/cfn-mastery/level-09-full-architecture/production-app.yaml templates/
touch buildspec.yaml pipeline.yaml
```

**Step 2, `buildspec.yaml`** (tells CodeBuild how to validate the template before the pipeline proceeds):

```yaml
version: 0.2

phases:
  install:
    commands:
      - echo "Installing cfn-lint for static template analysis"
      - pip install cfn-lint
  pre_build:
    commands:
      - echo "Linting CloudFormation templates"
      - cfn-lint templates/production-app.yaml
  build:
    commands:
      - echo "Validating template against the CloudFormation API"
      - aws cloudformation validate-template --template-body file://templates/production-app.yaml

artifacts:
  files:
    - templates/production-app.yaml
```

**Step 3, `pipeline.yaml`** (the CloudFormation template that *creates the pipeline itself*, meta, and deliberately so: your pipeline is also managed as code):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 10 - CI/CD pipeline that lints, validates, and deploys production-app.yaml via Change Sets with manual approval.

Parameters:
  GitHubRepoOwner:
    Type: String
  GitHubRepoName:
    Type: String
  GitHubBranch:
    Type: String
    Default: main
  CodeStarConnectionArn:
    Type: String
    Description: ARN of an existing CodeStar Connection authorized to your GitHub account.

Resources:
  ArtifactBucket:
    Type: AWS::S3::Bucket

  CodeBuildRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: {Service: codebuild.amazonaws.com}
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CodeBuildAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents']
                Resource: '*'
              - Effect: Allow
                Action: ['s3:GetObject', 's3:PutObject']
                Resource: !Sub '${ArtifactBucket.Arn}/*'
              - Effect: Allow
                Action: 'cloudformation:ValidateTemplate'
                Resource: '*'

  LintAndValidateProject:
    Type: AWS::CodeBuild::Project
    Properties:
      ServiceRole: !GetAtt CodeBuildRole.Arn
      Artifacts: {Type: CODEPIPELINE}
      Environment:
        Type: LINUX_CONTAINER
        ComputeType: BUILD_GENERAL1_SMALL
        Image: aws/codebuild/amazonlinux2-x86_64-standard:5.0
      Source: {Type: CODEPIPELINE, BuildSpec: buildspec.yaml}

  PipelineRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: {Service: codepipeline.amazonaws.com}
            Action: sts:AssumeRole
      Policies:
        - PolicyName: PipelineAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: ['s3:*']
                Resource: ['*']
              - Effect: Allow
                Action: ['codebuild:BatchGetBuilds', 'codebuild:StartBuild']
                Resource: '*'
              - Effect: Allow
                Action: ['cloudformation:*']
                Resource: '*'
              - Effect: Allow
                Action: ['iam:PassRole']
                Resource: '*'
              - Effect: Allow
                Action: ['codestar-connections:UseConnection']
                Resource: !Ref CodeStarConnectionArn

  CloudFormationDeployRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal: {Service: cloudformation.amazonaws.com}
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
        # Production note: replace with a scoped-down custom policy - see Governance section below

  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      RoleArn: !GetAtt PipelineRole.Arn
      ArtifactStore: {Type: S3, Location: !Ref ArtifactBucket}
      Stages:
        - Name: Source
          Actions:
            - Name: GitHubSource
              ActionTypeId: {Category: Source, Owner: AWS, Provider: CodeStarSourceConnection, Version: '1'}
              Configuration:
                ConnectionArn: !Ref CodeStarConnectionArn
                FullRepositoryId: !Sub '${GitHubRepoOwner}/${GitHubRepoName}'
                BranchName: !Ref GitHubBranch
              OutputArtifacts: [{Name: SourceOutput}]

        - Name: LintAndValidate
          Actions:
            - Name: LintTemplate
              ActionTypeId: {Category: Build, Owner: AWS, Provider: CodeBuild, Version: '1'}
              Configuration: {ProjectName: !Ref LintAndValidateProject}
              InputArtifacts: [{Name: SourceOutput}]
              OutputArtifacts: [{Name: BuildOutput}]

        - Name: CreateChangeSet
          Actions:
            - Name: GenerateChangeSet
              ActionTypeId: {Category: Deploy, Owner: AWS, Provider: CloudFormation, Version: '1'}
              Configuration:
                ActionMode: CHANGE_SET_REPLACE
                StackName: level10-production-app
                ChangeSetName: pipeline-generated-changeset
                TemplatePath: BuildOutput::templates/production-app.yaml
                RoleArn: !GetAtt CloudFormationDeployRole.Arn
                Capabilities: CAPABILITY_IAM
              InputArtifacts: [{Name: BuildOutput}]

        - Name: ManualApproval
          Actions:
            - Name: ApproveChangeSet
              ActionTypeId: {Category: Approval, Owner: AWS, Provider: Manual, Version: '1'}

        - Name: ExecuteChangeSet
          Actions:
            - Name: DeployChangeSet
              ActionTypeId: {Category: Deploy, Owner: AWS, Provider: CloudFormation, Version: '1'}
              Configuration:
                ActionMode: CHANGE_SET_EXECUTE
                StackName: level10-production-app
                ChangeSetName: pipeline-generated-changeset

Outputs:
  PipelineName:
    Value: !Ref Pipeline
```

```bash
aws cloudformation validate-template --template-body file://pipeline.yaml

# You must first create a CodeStar Connection to GitHub in the console (one-time, manual OAuth step)
# and pass its ARN below.
aws cloudformation deploy \
  --template-file pipeline.yaml \
  --stack-name level10-cicd-pipeline \
  --parameter-overrides \
    GitHubRepoOwner=your-github-username \
    GitHubRepoName=cfn-mastery-guide \
    CodeStarConnectionArn=arn:aws:codestar-connections:region:account:connection/xxxx \
  --capabilities CAPABILITY_IAM
```

### 🔍 Observation Point #10

Push a small, deliberate change to `templates/production-app.yaml` (e.g., change `DesiredCapacity` from `2` to `3`) and push to your connected GitHub branch. Watch the pipeline in the console.

**Question: The pipeline reaches the `ManualApproval` stage and pauses indefinitely. Why did CloudFormation not just apply the ASG capacity change automatically, given that it's such a minor, safe update?**

<details>
<summary>🔎 Click to reveal answer</summary>

Because the pipeline was **designed by you** to require human approval on *every* Change Set, regardless of how small the underlying change looks, this is a deliberate governance choice, not a CloudFormation limitation. In real organizations, teams often tier this: fully automatic deploys to a `dev` pipeline, mandatory manual approval for `staging`, and mandatory approval **plus** a second reviewer for `production`. The lesson here is that **CloudFormation gives you the primitives (Change Sets); your pipeline design decides the actual governance policy** on top of them. "Safe-looking" changes have caused real production incidents before, the discipline of reviewing *every* Change Set, not just the scary-looking ones, is what the manual approval gate enforces.
</details>

### 📖 Template Breakdown

| Concept | Syntax | Purpose |
|---|---|---|
| **CodeStar Connection** | `ConnectionArn` | The modern, OAuth-based replacement for storing GitHub personal access tokens in AWS |
| **CHANGE_SET_REPLACE action mode** | `ActionMode: CHANGE_SET_REPLACE` | Pipeline-native equivalent of `create-change-set`, recreates the Change Set fresh on every run |
| **CHANGE_SET_EXECUTE action mode** | `ActionMode: CHANGE_SET_EXECUTE` | Pipeline-native equivalent of `execute-change-set`, only runs after the prior stage (approval) succeeds |
| **Manual Approval action** | `Category: Approval, Provider: Manual` | A genuine human gate inside an otherwise fully automated pipeline |
| **CloudFormationDeployRole** | Separate IAM Role, assumed by the CloudFormation *service*, not by you | Separation of duties: the pipeline's own permissions differ from the permissions the deployed stack's resources get |
| **cfn-lint in buildspec** | `pip install cfn-lint` then `cfn-lint templates/*.yaml` | Catches template errors, bad practices, and typos **before** AWS even sees the template, the IaC equivalent of a code linter |

### 🏛️ Governance & Well-Architected Notes (Read Before You Finish)

A few things flagged deliberately as "production notes" throughout this guide, collected here as your next research targets beyond Level 10:

- **`AdministratorAccess` on `CloudFormationDeployRole` is a placeholder, not a recommendation.** Real production deploy roles are scoped to exactly the resource types and actions the template needs, nothing more. This is the single most important thing to fix before using this pipeline for anything real.
- **Secrets belong in Secrets Manager / SSM SecureString**, referenced via dynamic references (`{{resolve:secretsmanager:...}}`), never as plain CLI parameters.
- **Service Control Policies (SCPs)** at the AWS Organizations level can enforce guardrails (e.g., "no S3 bucket may ever be public") that no individual template author can override, a governance layer above CloudFormation entirely.
- **StackSets** let you deploy the same template across many accounts/regions from one operation, the natural next step once you're managing more than a handful of AWS accounts.
- **Drift Detection should be scheduled**, not run manually once, pair it with EventBridge + a Lambda notifier for real production monitoring.

### 🕳️ The Final Curiosity Gap

You've now built, in order: a bucket, a parameterized bucket, an environment-aware VPC, a cross-stack network, a live web server, a composed nested architecture, a self-aware Custom Resource, a protected and previewable stack, a full production 3-tier system, and a pipeline that deploys it all safely. Every concept built directly on the one before it, nothing was taught in isolation. The real question left for you now isn't "what CloudFormation feature comes next", it's: **what would you design differently if you started this exact architecture over from Level 1, knowing everything you know now?** That question, not this document, is where mastery actually lives.

### 🧪 Final Challenge

Take the Level 9 architecture and the Level 10 pipeline and combine them into a **StackSet** that could deploy the same production stack into two separate AWS regions simultaneously, for disaster recovery. You won't find a template for this above, by this point, you have everything you need to build it yourself.

### 🧹 Tear Down

```bash
aws cloudformation delete-stack --stack-name level10-cicd-pipeline
aws cloudformation delete-stack --stack-name level9-production-app
```

---

## 🎓 What You've Actually Learned

| Skill Area | Where You Learned It |
|---|---|
| Template anatomy & stack lifecycle | Level 1 |
| Parameters, Conditions, Fn::If, AWS::NoValue | Level 2 |
| Mappings, resource-level Conditions, Pseudo Parameters | Level 3 |
| Outputs, Export/ImportValue, cross-stack coupling risk | Level 4 |
| Security Groups, UserData, in-place vs. replacement updates | Level 5 |
| Nested Stacks, template composition, DependsOn | Level 6 |
| Custom Resources, Lambda-backed logic, CAPABILITY_IAM | Level 7 |
| Change Sets, Stack Policies, Drift Detection | Level 8 |
| Full multi-tier production architecture, DeletionPolicy | Level 9 |
| CI/CD for infrastructure, governance, Well-Architected thinking | Level 10 |

---

## 🤝 Contributing / Feedback

Found an error, an outdated AMI path, or a step that didn't work in your account? Open an issue or submit a PR, this guide is meant to be maintained the same way the infrastructure inside it is: as living, versioned code.

![Made with](https://img.shields.io/badge/Made%20with-☁️%20CloudFormation-orange?style=flat-square)
![Learners](https://img.shields.io/badge/Built%20for-Hands--On%20Learners-brightgreen?style=flat-square)
