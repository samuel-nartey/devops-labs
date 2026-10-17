# Community Wall: Launch Your First Cloud Application on AWS

Workshop project for **AWS User Group Kumasi** (online, Oct 17, 3:00 PM, 1 hour).

A small but real serverless web app. Attendees open one page that shows the event flyer, tap **Share your review**, and post a message that appears on a shared wall within seconds. The page also invites them to follow the community on LinkedIn, Meetup, and WhatsApp.

Built with five AWS services: **S3, CloudFront, API Gateway, Lambda, DynamoDB** (plus CloudWatch Logs and IAM, which come with the others).

---

## 0. Files you need

| File | Use it for | Needed? |
|---|---|---|
| `README.md` | This guide: build steps, deploy, run-of-show, troubleshooting | Read first |
| `frontend/index.html` | The web page. Flyer and follow links are already inside. You only edit `API_URL` | Yes |
| `lambda/index.py` | Backend code to paste into Lambda (console build) | Yes, for the console build |
| `template.yaml` | CloudFormation template that creates everything in one command | Yes, as your backup and for the IaC segment |
| `frontend/flyer.jpg` | Original flyer image (already embedded in `index.html`) | No, keep for social posts |

```
community-wall/
  README.md
  template.yaml
  frontend/index.html     (flyer embedded, links filled in)
  frontend/flyer.jpg      (optional original)
  lambda/index.py
```

The Lambda code inside `template.yaml` is identical to `lambda/index.py`, and the template passes `cfn-lint` validation.

---

## 1. What attendees see

1. **The flyer** at the top, on a pink and orange background.
2. **"What's your review of the program?"** with a big **Share your review** button.
3. Tapping the button reveals **the wall**: a form (name, country, review, quick-start chips) and a live list of reviews with colorful avatars.
4. **Follow us**: buttons for LinkedIn, Meetup, and WhatsApp.

Two modes:
- **Demo mode:** if `API_URL` is still the placeholder, the page runs on its own with sample reviews (nothing is saved). Use it to rehearse or preview without AWS.
- **Live mode:** once `API_URL` is set, reviews are stored in DynamoDB and refresh every 5 seconds for everyone.

Links already set in `index.html`:
- LinkedIn: `https://www.linkedin.com/company/akwannyahub/`
- Meetup: `https://www.meetup.com/65155013-572d-4ad3-98a7-e5f22b286294/`
- WhatsApp: `https://chat.whatsapp.com/KGua0DQsHqE84kYwoL4kul`

To change them, edit the `LINKS` block near the bottom of the script in `index.html`.

---

## 2. How it works

```
Browser
  |-- (1) loads the page ----> CloudFront ---> S3 (private bucket, index.html)
  |
  |-- (2) GET/POST /messages -> API Gateway (HTTP API) ---> Lambda ---> DynamoDB
                                                              |
                                                              +--> CloudWatch Logs
```

1. The browser asks CloudFront for the page. CloudFront fetches `index.html` from a **private** S3 bucket and serves it over HTTPS.
2. When someone posts a review, the page calls `POST /messages`. It refreshes the wall with `GET /messages` every 5 seconds.
3. API Gateway checks the route, applies rate limits, and invokes the Lambda function.
4. Lambda validates the input, then saves the review to DynamoDB (POST) or reads the newest 50 (GET).
5. Every Lambda run writes logs to CloudWatch.

### Why these services

| Service | Job in this app | Why it fits |
|---|---|---|
| **S3** | Stores the page | Cheapest, most durable home for static files. No server. Stays private. |
| **CloudFront** | Serves the page over HTTPS worldwide | Free HTTPS URL, no domain needed. Lets the bucket stay private. |
| **API Gateway (HTTP API)** | Public front door of the backend | Handles HTTPS, routing, CORS, and throttling. Simpler and cheaper than the REST API type. |
| **Lambda** | Runs the backend code | No servers to patch. Pay only per request. |
| **DynamoDB** | Stores the reviews | Fully managed, on-demand pricing, fast key lookups. |
| **IAM** | Controls access | The Lambda role can only write and query this one table (least privilege). |
| **CloudWatch Logs** | Shows what the code did | The first place to look when something breaks. |

Why serverless for a first app: nothing to install or patch, a workshop costs pennies, it is a real production pattern, and every piece has one job.

---

## 3. Before you start

You need:
- An AWS account (use an IAM or Identity Center user, **not the root user**).
- **MFA** turned on.
- The files from this folder.

**Pick one region and stay in it.** This guide uses **Europe (Ireland) `eu-west-1`**. Confirm the region at the top right of the console before creating anything.

> Cost note: this app should cost a few cents at most, and often nothing, depending on your account's free tier or credits. Set a budget first (Step 0).

---

## 4. Build it by hand in the console (the learning path)

Each step ends with a **Check**.

### Step 0: Set a budget alert
1. Open **AWS Budgets** and choose **Create budget**.
2. Pick the **Zero spend budget** template (or a small monthly budget such as 5 USD).
3. Enter your email and create it.

**Check:** the budget appears in the list.

### Step 1: Create the DynamoDB table
1. Open **DynamoDB** (confirm the region) and choose **Create table**.
2. **Table name:** `community-wall-messages`
3. **Partition key:** `pk` (String). **Sort key:** `sk` (String).
4. Under **Table settings**, choose **Customize settings**, then **Capacity mode: On-demand**.
5. Create the table and wait for **Active**.
6. Open the table, go to **Additional settings**, find **Time to Live (TTL)**, turn it on, and enter the attribute `expiresAt`. Old reviews now delete themselves.
7. Copy the table **ARN** (Overview tab, Additional info). You need it in Step 2.

Why `pk` and `sk`? Every review shares `pk = "WALL"`. The `sk` starts with a timestamp, so DynamoDB returns the newest first with a cheap query (no full scan).

**Check:** table is Active and you have the ARN.

### Step 2: Create the Lambda function
1. Open **Lambda**, choose **Create function**, **Author from scratch**.
2. **Function name:** `community-wall-api`. **Runtime:** `Python 3.12`.
3. Keep **Create a new role with basic Lambda permissions**. Create the function.
4. In the **Code** tab, open `lambda_function.py`, delete its contents, and paste all of `lambda/index.py`.
5. Go to **Code**, then **Runtime settings**, **Edit**, and set **Handler** to `lambda_function.handler`. Save.
6. Choose **Deploy** above the editor. (Saving is not deploying.)
7. **Configuration**, **Environment variables**, **Edit**, add:
   - `TABLE_NAME` = `community-wall-messages`
   - `RETENTION_DAYS` = `7`
8. **Configuration**, **General configuration**, **Edit**: set **Timeout** to `10 seconds`.
9. **Configuration**, **Permissions**: click the **role name** (opens IAM).
10. In IAM choose **Add permissions**, **Create inline policy**, **JSON**, and paste this with your table ARN:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem", "dynamodb:Query"],
      "Resource": "PASTE_YOUR_TABLE_ARN_HERE"
    }
  ]
}
```

11. Name it `WallTableAccess` and create it.

**Check (test in the console):**
1. **Test** tab, new event `get-test`:
```json
{ "requestContext": { "http": { "method": "GET" } } }
```
Expect `"statusCode": 200` and `"body": "[]"`.
2. New event `post-test`:
```json
{
  "requestContext": { "http": { "method": "POST" } },
  "body": "{\"name\":\"Ama\",\"country\":\"Ghana\",\"message\":\"Hello from my first Lambda\"}"
}
```
Expect `"statusCode": 201`. Run `get-test` again and your message appears.

### Step 3: Create the API
1. Open **API Gateway**, find **HTTP API**, choose **Build**.
2. **Add integration**, **Lambda**, select `community-wall-api`. **API name:** `community-wall-api`. Next.
3. Configure two routes, both to your Lambda: `GET /messages` and `POST /messages`.
4. Keep stage `$default` with **Auto-deploy** on. Create.
5. Copy the **Invoke URL** (like `https://abc123.execute-api.eu-west-1.amazonaws.com`). Save it for Step 4. ### https://msddqek0wf.execute-api.us-east-1.amazonaws.com
6. **CORS**, **Configure**:
   - **Access-Control-Allow-Origin:** `*` (temporary, tightened in Step 6)
   - **Access-Control-Allow-Headers:** `content-type`
   - **Access-Control-Allow-Methods:** `GET`, `POST`, `OPTIONS`
7. **Stages**, `$default`, set default route **throttling**: rate `10`, burst `20`.

**Check:** open `YOUR_INVOKE_URL/messages` in a browser. You see `[]` or your test message.

### Step 4: Prepare the page and create the S3 bucket
1. Open `frontend/index.html` in a text editor. Find:
   ```js
   const API_URL = "PASTE_YOUR_API_URL_HERE";
   ```
   Replace the placeholder with your Invoke URL (no trailing slash). Save.
   (The flyer and the three follow links are already inside the file.)
2. Open **S3**, **Create bucket**. Name it uniquely, for example `community-wall-site-yourname-1234`.
3. Keep **Block all public access ON**.
4. Create the bucket, then **Upload** `index.html`.

**Check:** `index.html` is listed in the bucket.

### Step 5: Create the CloudFront distribution
1. Open **CloudFront**, **Create distribution**.
2. **Origin domain:** your S3 bucket.
3. **Origin access:** **Origin access control settings (recommended)**, **Create new OAC** (defaults).
4. **Viewer protocol policy:** **Redirect HTTP to HTTPS**.
5. **Cache policy:** **CachingDisabled** (edits show instantly during the workshop).
6. Do not enable WAF for the workshop (adds cost).
7. **Default root object:** `index.html`. Create.
8. When the banner says the bucket policy must be updated, choose **Copy policy**, open the bucket **Permissions**, and paste it under **Bucket policy**. Save.
9. Wait 3 to 5 minutes until the status is no longer **Deploying**.
10. Copy the **Distribution domain name** (like `d1234abcd.cloudfront.net`).

**Check:** open `https://YOUR_DISTRIBUTION_DOMAIN`. You see the flyer, the review prompt, and the follow buttons.

> Console screens change from time to time. If a label differs slightly, pick the closest option. The goal is always: private bucket, origin access control, HTTPS only.

### Step 6: Tighten CORS
1. **API Gateway**, your API, **CORS**, **Edit**.
2. Replace `*` with `https://YOUR_DISTRIBUTION_DOMAIN` (with `https://`, no trailing slash). Save.

**Check:** reload the site, tap **Share your review**, post a review. It still works.

### Step 7: Go live and look inside
1. Tap **Share your review**, post a review, and ask a friend to do the same.
2. Watch the wall update every few seconds.
3. Open **CloudWatch**, **Log groups**, `/aws/lambda/community-wall-api`, newest stream. Find the `message_saved` line with your name.
4. Open **DynamoDB**, your table, **Explore table items** to see the saved records.

### Step 8: Clean up
Delete in this order:
1. **CloudFront:** disable the distribution, wait, then delete.
2. **S3:** empty the bucket, then delete it.
3. **API Gateway:** delete `community-wall-api`.
4. **Lambda:** delete `community-wall-api`.
5. **IAM:** delete the role starting with `community-wall-api-role-`.
6. **CloudWatch:** delete log group `/aws/lambda/community-wall-api`.
7. **DynamoDB:** delete table `community-wall-messages`.

---

## 5. Deploy the same app with CloudFormation

Everything you clicked is described in `template.yaml` (Infrastructure as Code).

### Prerequisites
- AWS CLI v2 installed and credentials configured.
- `aws sts get-caller-identity` shows the right account.

### Deploy

```bash
# 1. Create the whole stack (3 to 6 minutes, mostly CloudFront)
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name community-wall \
  --capabilities CAPABILITY_IAM \
  --region eu-west-1

# 2. Read the outputs
aws cloudformation describe-stacks \
  --stack-name community-wall \
  --region eu-west-1 \
  --query "Stacks[0].Outputs" --output table
```

Outputs: `SiteUrl`, `ApiUrl`, `BucketName`, `TableName`, `DistributionId`.

### Publish the page

```bash
# 3. Put your ApiUrl into the page (replace the values)
API_URL="https://abc123.execute-api.eu-west-1.amazonaws.com"
BUCKET="community-wall-sitebucket-xxxxxxxx"

sed "s|PASTE_YOUR_API_URL_HERE|$API_URL|" frontend/index.html > index.deploy.html

# 4. Upload it (one file, the flyer is embedded)
aws s3 cp index.deploy.html "s3://$BUCKET/index.html" \
  --content-type "text/html" --region eu-west-1
```

Open `SiteUrl` in your browser.

### Update later
Edit `template.yaml`, run the same `deploy` command. CloudFormation updates only what changed. For a page change, re-run steps 3 and 4.

### Delete everything

```bash
aws s3 rm "s3://$BUCKET" --recursive --region eu-west-1
aws cloudformation delete-stack --stack-name community-wall --region eu-west-1
```

The bucket must be emptied first, or the stack deletion fails.

### What the template creates

| Resource | Purpose |
|---|---|
| `MessagesTable` | DynamoDB table, on-demand, encrypted, with TTL |
| `FunctionRole` | IAM role: logs plus PutItem and Query on this table only |
| `FunctionLogGroup` | CloudWatch log group, 7-day retention |
| `ApiFunction` | The Lambda function (code inlined, no packaging) |
| `HttpApi`, routes, stage, integration | API Gateway with throttling and CORS locked to your CloudFront domain |
| `ApiInvokePermission` | Lets API Gateway call the function |
| `SiteBucket`, `SiteBucketPolicy` | Private S3 bucket readable only by this CloudFront distribution |
| `OriginAccessControl`, `Distribution` | CloudFront in front of S3, HTTPS only |

---

## 6. Run-of-show (60 minutes)

| Time | Activity |
|---|---|
| 0-5 | Welcome, quick poll ("Have you deployed an app before?"), show the architecture diagram |
| 5-10 | Setup check: budget alert, one region, IAM basics |
| 10-25 | **Backend:** DynamoDB table, Lambda (use `lambda/index.py`), API Gateway routes and CORS |
| 25-40 | **Frontend:** edit `API_URL`, upload `index.html` to S3, create CloudFront |
| 40-50 | **Go live:** share the CloudFront link, everyone taps **Share your review** and posts. Open CloudWatch Logs to see their requests |
| 50-55 | **Industry standards:** least-privilege IAM, throttling, tags, then show `template.yaml` and the one-command deploy |
| 55-60 | Cleanup, show the follow links, next steps, Q&A |

Interactivity tips:
- Build live yourself. Attendees follow along, or just use your pre-deployed link.
- Polls at the start and midpoint. A "type DONE in chat" checkpoint after each phase.
- Ask Paula (moderator) to watch chat, flag blockers, and relay questions.
- Mini challenges: "add one field", "find your request in the logs".

### Pre-session checklist
- [ ] Deploy the CloudFormation stack once as your **backup**, and keep its `SiteUrl` ready.
- [ ] Do the full console build once, timing each phase. CloudFront takes 3 to 5 minutes, so create it early and talk through security while it deploys.
- [ ] Set `API_URL` in `index.html`, upload, and post a test review.
- [ ] Open the three follow links in a private window. Confirm the Meetup group and LinkedIn page are public and the WhatsApp invite has not expired or hit its member limit.
- [ ] Share the repo link and a pre-work note in advance: create an AWS account, turn on MFA, set a budget alert.
- [ ] Clear test reviews before the session (delete items in DynamoDB, or wait for the 7-day TTL).
- [ ] Record the session and share the repo afterward.

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Page says "Demo mode" and reviews do not reach others | `API_URL` still the placeholder | Edit `index.html`, upload it again |
| "Could not load reviews" | CORS origin does not match your site exactly | Use `https://domain` with no trailing slash |
| CORS error in the browser console | CORS not saved or wrong origin | Re-check API Gateway CORS |
| `AccessDenied` XML on the site | Bucket policy missing or OAC not set | Redo Step 5.8 |
| `{"message":"Internal Server Error"}` | Lambda crashed | Read CloudWatch Logs for the function |
| `Runtime.HandlerNotFound` | Handler name mismatch | Console build: set Handler to `lambda_function.handler` |
| `AccessDeniedException` from DynamoDB | IAM policy missing or wrong ARN | Redo Step 2.10 |
| Edited page still shows the old version | CloudFront cache | Use CachingDisabled, or invalidate `/*` |
| Flyer not showing | Old `index.html` uploaded, or file opened without the embedded version | Upload the latest `index.html` (flyer is embedded) |
| Follow buttons greyed out | A link in `LINKS` is empty | Fill it in and upload again |
| Resource "not found" right after creating it | Wrong region | Check the region selector |
| Stack delete fails | Bucket not empty | Empty the bucket, delete the stack again |

---

## 8. Recommendations

**Security**
- Never use the root user for daily work. Turn on MFA everywhere.
- Keep IAM policies narrow, like the Lambda role here.
- Keep S3 private and serve through CloudFront.
- Never put secrets in `index.html`. Anything in the browser is public.
- Validate input on the server (the Lambda does) and render user text with `textContent`, never `innerHTML` (the page does), so nobody can inject scripts.
- In production add **AWS WAF** in front of CloudFront, and **Cognito** if users must sign in.

**Cost**
- Set a budget before building. Tag resources (we use `project`). Clean up after workshops. TTL keeps data from piling up.

**Reliability**
- Add CloudWatch alarms for Lambda errors and API 5xx.
- Keep log retention short (7 to 30 days).
- In production use CloudFront `CachingOptimized` and invalidate on each deploy.

**Delivery**
- Keep this folder in Git. Do not click-deploy production.
- Next: GitHub Actions running `aws cloudformation deploy` with OIDC (no long-lived keys).
- Next: AWS SAM or CDK for packaging and local testing.
- Next: custom domain with Route 53 and ACM.

**For beginners**
- Change one thing at a time and test after each step.
- Read CloudWatch logs first when something fails.
- Break it on purpose (remove the IAM permission) and watch the error. It teaches more than a smooth run.

---

## 9. Challenge ideas

1. Add a "role" field to the form, the Lambda, and the table.
2. Add a character counter to the review box.
3. Show only reviews from the last hour.
4. Add a CloudWatch alarm that emails you on any Lambda error.
5. Rebuild the stack in a second region using only `template.yaml`.
