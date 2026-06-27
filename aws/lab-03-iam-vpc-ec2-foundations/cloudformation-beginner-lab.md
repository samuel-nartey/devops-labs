# CloudFormation in 8 Levels — Learn by Deploying

A hands-on CloudFormation lab. Every level = a short explanation + a template + console steps.
Deploy it, watch it happen, delete it, move to the next level.

**Rule for every level:** Create stack → confirm `CREATE_COMPLETE` → inspect the real resource in its own console → Delete the stack → confirm it's gone.

---

## Level 1 — Anatomy of a Template

A CloudFormation template is just YAML describing AWS resources you want created. `Resources` is the only required section. Each resource has a Logical ID (your name for it) and a Type (the AWS resource type).

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 1 - My first CloudFormation stack, a single S3 bucket

Resources:
  MyFirstBucket:          # Logical ID - only exists inside this template
    Type: AWS::S3::Bucket # Resource Type - tells CFN what to actually create
    # No Properties needed - S3 will auto-generate a unique bucket name
```

**Deploy:**
1. Save as `level1.yaml`
2. Console → CloudFormation → **Create stack** → **With new resources (standard)**
3. **Upload a template file** → choose `level1.yaml` → Next
4. Stack name: `level1-first-stack` → Next → Next → **Submit**
5. Watch **Events** tab: `CREATE_IN_PROGRESS` → `CREATE_COMPLETE`
6. **Resources** tab → click through to see the real bucket in S3 console
7. Delete the stack → confirm the bucket disappears too

---

## Level 2 — Stack Lifecycle & Failure/Rollback

CloudFormation stacks move through states: `CREATE_IN_PROGRESS`, `CREATE_COMPLETE`, `CREATE_FAILED`, `ROLLBACK_IN_PROGRESS`. If one resource fails, CFN automatically undoes everything it already created in that stack. This is the safety net that makes IaC trustworthy.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 2 - Intentional failure to observe rollback behavior

Resources:
  MyBrokenInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-00000000        # Intentionally invalid AMI ID - will fail
      InstanceType: t2.micro
```

**Deploy:**
1. Save as `level2.yaml` → Create stack as before, name it `level2-rollback-test`
2. Watch **Events** tab: you'll see `CREATE_FAILED` then `ROLLBACK_IN_PROGRESS` then `ROLLBACK_COMPLETE`
3. Click the failed event row → read the **Status reason** column — this is how you debug CFN errors
4. Delete the stack (a `ROLLBACK_COMPLETE` stack still needs deleting)

---

## Level 3 — Parameters: Making It Reusable

Hardcoded values mean one template = one use case. `Parameters` let the person deploying the stack plug in their own values at deploy time — same template, different outcomes.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 3 - Parameterized EC2 instance

Parameters:
  InstanceTypeParam:               # Name we reference later with !Ref
    Type: String
    Default: t2.micro
    AllowedValues:                 # Restricts input to a safe, known list
      - t2.micro
      - t2.small
    Description: Choose the EC2 instance size

  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName  # Special type - CFN shows a dropdown of your real key pairs
    Description: Existing EC2 key pair for SSH access

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c7217cdde317cfec   # Amazon Linux 2023, us-east-1 - change if using another region
      InstanceType: !Ref InstanceTypeParam  # Pulls in whatever the user chose
      KeyName: !Ref KeyPairName
```

**Deploy:**
1. Save as `level3.yaml` → Create stack, name it `level3-parameters`
2. On the **Specify stack details** page, notice the Parameters form CFN auto-generated from your `Parameters` block
3. Pick an instance type and an existing key pair → deploy
4. Confirm in EC2 console the instance matches what you picked
5. Delete the stack

---

## Level 4 — Intrinsic Functions & Pseudo Parameters

`!Ref` pulls a parameter or resource ID. `!GetAtt` pulls a specific attribute off a resource (like its public IP). `!Sub` builds a string by substituting variables in. Pseudo parameters (`AWS::Region`, `AWS::AccountId`, `AWS::StackName`) are values AWS already knows — you don't define them.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 4 - Intrinsic functions and pseudo parameters

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      # !Sub builds the name using the stack name + account ID + region
      # so it's globally unique without you typing anything by hand
      BucketName: !Sub '${AWS::StackName}-${AWS::AccountId}-${AWS::Region}'

Outputs:
  BucketArn:
    Description: ARN of the created bucket
    Value: !GetAtt MyBucket.Arn       # Pulls the Arn attribute off the bucket resource

  BucketNameOutput:
    Description: The generated bucket name
    Value: !Ref MyBucket              # !Ref on an S3 bucket returns its name
```

**Deploy:**
1. Save as `level4.yaml` → Create stack, name it `level4-intrinsics`
2. After `CREATE_COMPLETE`, open the **Outputs** tab — see the bucket name and ARN that CFN computed for you
3. Confirm in S3 console the bucket name matches exactly what `!Sub` generated
4. Delete the stack

---

## Level 5 — Mappings & Conditions: Adding Logic

`Mappings` are static lookup tables (e.g. region → AMI ID). `Conditions` let a resource be created — or a property change — based on a parameter value, using `!Equals` and `!If`. This is how one template can serve `dev` and `prod` differently.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 5 - Mappings and Conditions for dev vs prod sizing

Parameters:
  EnvironmentType:
    Type: String
    AllowedValues: [dev, prod]
    Default: dev

Mappings:
  RegionMap:                          # Lookup table: region -> AMI ID
    us-east-1:
      AMI: ami-0c7217cdde317cfec
    us-west-2:
      AMI: ami-0e83be366243f524a

Conditions:
  IsProd: !Equals [!Ref EnvironmentType, prod]   # True only if param == "prod"

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]  # Looks up AMI for current region
      InstanceType: !If [IsProd, t2.medium, t2.micro]            # Bigger instance only in prod
```

**Deploy:**
1. Save as `level5.yaml` → Create stack twice with different `EnvironmentType` values: `level5-dev` and `level5-prod`
2. Compare the **InstanceType** in EC2 console between the two — same template, different sizing
3. Delete both stacks

---

## Level 6 — Outputs & Cross-Stack References

`Outputs` with `Export` makes a value available outside its own stack. `Fn::ImportValue` lets a different stack consume that exported value. This is how teams split infrastructure (network team's stack feeds the app team's stack) without copy-pasting IDs by hand.

```yaml
# --- File: level6-network.yaml (deploy this FIRST) ---
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 6 - Network stack exporting a subnet ID

Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAtt 'AWS::Region']  # placeholder, see note below

Outputs:
  SubnetIdExport:
    Value: !Ref MySubnet
    Export:
      Name: Level6-SubnetId          # Other stacks import using this exact name
```

```yaml
# --- File: level6-compute.yaml (deploy this SECOND) ---
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 6 - Compute stack importing the subnet ID

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c7217cdde317cfec
      InstanceType: t2.micro
      SubnetId: !ImportValue Level6-SubnetId   # Pulls in the value exported above
```

> Note: `AvailabilityZone` needs a real AZ string like `us-east-1a` — replace the placeholder line with your region's AZ, or just omit `AvailabilityZone` and let AWS pick.

**Deploy:**
1. Deploy `level6-network.yaml` first, name it `level6-network`
2. Check its **Outputs** tab — confirm `SubnetIdExport` shows a real subnet ID
3. Deploy `level6-compute.yaml` second, name it `level6-compute`
4. Confirm in EC2 console the instance landed in the subnet from the first stack
5. Delete `level6-compute` FIRST, then `level6-network` (you can't delete an exported value while something imports it)

---

## Level 7 — Real Multi-Resource Infrastructure & Dependencies

CloudFormation figures out resource order automatically when one resource references another (implicit dependency via `!Ref`). `DependsOn` forces an explicit order when there's no direct reference but one is still needed. This level wires a VPC, subnet, security group, IAM role, and EC2 instance into one working stack.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 7 - Full 2-tier stack with explicit and implicit dependencies

Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC               # Implicit dependency - CFN creates VPC first automatically
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true

  MyInternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref MyVPC
      InternetGatewayId: !Ref MyInternetGateway

  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow SSH and HTTP
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  MyInstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole

  MyInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref MyInstanceRole

  MyInstance:
    Type: AWS::EC2::Instance
    DependsOn: AttachGateway           # Explicit dependency - no direct !Ref link to the gateway attachment,
                                        # but the instance needs internet access to work, so we force the order
    Properties:
      ImageId: ami-0c7217cdde317cfec
      InstanceType: t2.micro
      SubnetId: !Ref MySubnet
      SecurityGroupIds:
        - !Ref MySecurityGroup
      IamInstanceProfile: !Ref MyInstanceProfile
```

**Deploy:**
1. Save as `level7.yaml` → Create stack, name it `level7-fullstack`
2. Watch the **Events** tab order resources get created in — notice VPC and IGW appear before the instance, with no explicit ordering needed for most of them
3. Confirm in EC2 console: instance running, in the right subnet, with the right security group and IAM role attached
4. Delete the stack — note it deletes in reverse order automatically

---

## Level 8 — Lifecycle Management & Production Habits

A change set is a preview of what CloudFormation *will* do before it actually does it — the single habit that prevents "oops I just resized prod by accident." `DeletionPolicy: Retain` protects a resource from being deleted even if the stack is deleted. Tags make cost tracking possible across many stacks.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Level 8 - Change sets, DeletionPolicy, and tagging

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c7217cdde317cfec
      InstanceType: t2.micro
      Tags:
        - Key: Environment
          Value: learning
        - Key: Owner
          Value: samuel

  MyImportantBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain     # Even if this stack is deleted, this bucket survives
```

**Deploy:**
1. Save as `level8.yaml` → Create stack, name it `level8-lifecycle`, confirm `CREATE_COMPLETE`
2. Edit your local copy: change `InstanceType` to `t2.small`
3. Console → your stack → **Stack actions** → **Create change set for current stack** → upload the edited template
4. Review the change set's diff BEFORE executing — this is the entire point of this level
5. Execute the change set, confirm the instance resized
6. Delete the stack → confirm in S3 console the bucket is STILL there because of `DeletionPolicy: Retain`
7. Manually delete that leftover bucket when you're done (it won't clean itself up)

---

### Wrap-up

By the end of Level 8 you've personally deployed and torn down: S3, EC2, VPC, Subnets, Internet Gateway, Security Groups, IAM Roles, and exported values across stacks — using Parameters, Conditions, Mappings, intrinsic functions, dependencies, and change sets. That's the real day-to-day CloudFormation toolkit.

Natural next step: rebuild a slice of real infrastructure (e.g. a piece of the Nkwa backend) as a CloudFormation stack using these same patterns.
