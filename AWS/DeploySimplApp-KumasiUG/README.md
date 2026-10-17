# Community Wall: build a secure, serverless web app on AWS

A step-by-step guide for beginners.

You will deploy a real web application where attendees read a live wall of program reviews, sign in with their own account, post a star rating and review, edit or delete their own review, and optionally share their LinkedIn, X, and GitHub profiles so others can connect with them. A moderator (admin) can remove any review.

By the end you will have deployed and tested a complete cloud application and understood why each piece exists.

| | |
|---|---|
| Time | About 60 to 90 minutes (deployment itself takes 5 to 8 minutes) |
| Cost | A few cents, and often nothing, depending on your account's free tier or credits |
| You need | An AWS account, an email address, and a browser. No prior cloud experience is assumed |
| Services used | S3, CloudFront, Cognito, API Gateway, Lambda, DynamoDB, IAM, CloudWatch, CloudFormation |

---

## How to read this guide

Three kinds of callouts appear throughout:

> **NOTE:** An important detail, warning, or tip. Read these before you continue.

> **REASON:** Why we do something this way. Understanding the reason is how you learn to make your own decisions later.

> **ARCHITECTURE:** The design thinking behind a choice. These explain how professionals structure cloud applications.

Every step ends with a **Check**, a quick way to confirm the step worked before you move on.

> **NOTE:** About testing. The backend code was tested locally against a simulated database (ownership rules, admin delete, ratings, paging, input validation, and social-link safety). The CloudFormation template passes `cfn-lint`, the standard template checker. The full stack has not been run in a real AWS account by the author of this guide, which is why Part 4 walks you through testing every feature yourself.

---

# Part 1: Understand what you are building

## 1.1 The big picture

```
                         +--------------------+
   (1) load the page --> |  CloudFront (CDN)  | --> S3 bucket (private, holds index.html)
                         +--------------------+

   (2) sign in -------->  Cognito (users, passwords, tokens)

   (3) read / write --->  API Gateway  --checks the token-->  Lambda  -->  DynamoDB
        reviews              (HTTP API)                         |
                                                           CloudWatch Logs
                              IAM role: Lambda may touch only this one table
```

In words:
1. The browser downloads the web page from **CloudFront**, which gets it from a **private S3 bucket**.
2. When a user wants to post, the page sends them to **Cognito** to sign in. Cognito gives the page a signed **token**, a digital pass that proves who the user is.
3. The page calls **API Gateway** with that token. API Gateway verifies the token and, only if it is valid, runs a **Lambda** function. Lambda reads and writes reviews in **DynamoDB**.
4. Lambda writes diary entries (logs) to **CloudWatch**, and an **IAM role** limits what Lambda is allowed to do.

## 1.2 The services in plain language

| Service | Think of it as | Its job here |
|---|---|---|
| **S3** | A storage cabinet for files | Holds the web page |
| **CloudFront** | A chain of delivery points around the world | Serves the page quickly over HTTPS (the padlock in the browser) |
| **Cognito** | The receptionist who checks IDs and issues visitor badges | Handles sign-up, email verification, sign-in, and issues tokens |
| **API Gateway** | The front desk of the backend | Receives requests, checks badges, limits traffic, passes valid requests on |
| **Lambda** | A chef who only works when an order arrives | Runs our Python code for each request |
| **DynamoDB** | A very fast filing system | Stores the reviews |
| **IAM** | The key card system | Decides exactly what Lambda is allowed to touch |
| **CloudWatch** | The security camera and diary | Stores logs so we can see what happened |
| **CloudFormation** | The architect's blueprint, executed automatically | Builds everything above from one file |

## 1.3 Concepts every beginner should know

**Serverless.** You do not rent or manage a computer. You give AWS your code and it runs it on demand, then charges only for what you use. There is nothing to patch, restart, or log into.

> **REASON:** For a small, spiky workload (a workshop, a launch, a campaign), serverless is cheaper and safer than a server that sits idle and needs security updates.

**Static page, dynamic app.** The web page itself (`index.html`) is a static file: every visitor receives the same file. The app is dynamic because that page calls an API to read and write live data. Most modern web apps work exactly this way.

> **ARCHITECTURE:** Separating the "frontend" (files served from S3 and CloudFront) from the "backend" (API, functions, database) lets each part scale and be secured independently. The frontend can serve millions of visitors without ever touching your code or database.

**API.** A set of web addresses your page can call to ask for or change data. Ours has four: read reviews, create a review, update a review, delete a review.

**Authentication versus authorization.** Authentication answers "who are you?" (sign-in). Authorization answers "what are you allowed to do?" (only edit your own review, only admins can remove others'). This app does both, in two different places, as you will see in Part 6.

**Tokens, JWT, and OAuth.** After sign-in, Cognito gives the browser a **JWT** (JSON Web Token). It is a small piece of text that contains facts about the user (a unique ID, groups, an expiry time) and is **digitally signed** by Cognito, so nobody can forge or change it. The sign-in process itself follows **OAuth 2.0**, the industry-standard way to sign in without your own code ever seeing a password.

**IAM and least privilege.** IAM controls permissions. "Least privilege" means giving each component only the permissions it needs and nothing more.

> **REASON:** If Lambda is ever compromised through a bug, the damage is limited to what its role allows. Ours can only read and write one table. It cannot touch other tables, buckets, or users.

**Infrastructure as Code (IaC).** Instead of clicking in the console, you describe your infrastructure in a file (`template.yaml`) and CloudFormation builds it. A set of resources built from one template is called a **stack**.

> **REASON:** Clicks cannot be reviewed, repeated, or undone reliably. A template can be stored in Git, reviewed by teammates, reused in other accounts or regions, and deleted in one command.

---

# Part 2: Prepare your environment

## Step 1: Use a safe AWS login

1. Sign in to the AWS console with an IAM user or IAM Identity Center user, **not the root user**.
2. Turn on **multi-factor authentication (MFA)** for that user (an authenticator app on your phone).

> **REASON:** The root user can do anything, including closing the account. An attacker who gets a password without MFA can run up bills in minutes. MFA is the single most effective protection you can add.

**Check:** you can sign in and are prompted for an MFA code.

## Step 2: Set a budget alert

1. In the console search bar type **Budgets** and open **AWS Budgets**.
2. Choose **Create budget**, pick the **Zero spend budget** template (or a small monthly budget such as 5 USD), enter your email, and create it.

> **REASON:** Cloud billing is pay-as-you-go. A budget alert is your safety net against mistakes such as leaving something running.

**Check:** the budget appears in the list.

## Step 3: Choose one region

Look at the region selector at the top right of the console. This guide uses **Europe (Ireland), `eu-west-1`**. Use the same region for everything.

> **NOTE:** The most common beginner problem is creating something in one region and looking for it in another. If a resource seems to be missing, check the region first.

> **ARCHITECTURE:** AWS is split into independent regions (geographic areas). Most services live inside exactly one region. Choose a region close to your users, and keep an application's parts together to reduce delay and avoid cross-region complexity. CloudFront is a global service, but the rest of this app sits in your chosen region.

**Check:** the region selector shows Europe (Ireland) or the region you chose.

## Step 4: Get a place to run commands

You need a terminal with the AWS command line interface (CLI). Pick **one** option.

**Option A (easiest): AWS CloudShell.** Click the **terminal icon** (`>_`) in the top bar of the console. It opens a ready-to-use terminal that is already signed in and already has the AWS CLI. Nothing to install.

**Option B: your own computer.** Install **AWS CLI version 2** and sign in with `aws configure` (access keys) or `aws configure sso` (Identity Center). Use macOS, Linux, or Windows with WSL.

Confirm you are signed in to the correct account:

```bash
aws sts get-caller-identity
```

> **NOTE:** If you use your own computer, avoid long-lived access keys for the root user. Use SSO or a dedicated IAM user with only the permissions you need.

**Check:** the command prints your account ID and user, with no error.

## Step 5: Get the project files

Download the project zip, then:

- **CloudShell:** choose **Actions**, then **Upload file**, select the zip, then run:
  ```bash
  unzip community-wall-v2.zip
  cd community-wall-v2
  ```
- **Your computer:** unzip it and open a terminal in the folder.

You should see:

```
community-wall-v2/
  README.md              this guide
  template.yaml          CloudFormation blueprint for the whole app
  deploy.sh              one command that builds everything and publishes the page
  backend/index.py       the Lambda code (a copy is embedded in template.yaml)
  frontend/index.html    the web page (the flyer image is embedded in it)
  frontend/flyer.jpg     the original flyer image (not needed to deploy)
```

**Check:** `ls` shows `template.yaml`, `deploy.sh`, `backend`, and `frontend`.

## Step 6 (optional): Preview the page without AWS

Open `frontend/index.html` in your browser (double-click it on your computer). It runs in **demo mode**: a fake sign-in, in-memory reviews, and every feature of the interface. Nothing is saved.

> **REASON:** Seeing the interface first makes the rest of the guide easier to follow, and demo mode lets you rehearse a presentation without any cloud dependency.

**Check:** you see the flyer, the review prompt, and a "Demo mode" note after you click **Share your review**.

---

# Part 3: Deploy the application

## Step 7: Know what will be created

The template creates these resources. You do not need to memorize them, but it helps to see how they connect.

| Group | Resources | Purpose |
|---|---|---|
| Identity | Cognito user pool, domain, app client, `admin` group | Sign-up, sign-in, tokens, moderator role |
| Data | DynamoDB table | Stores reviews and rating totals |
| Compute | Lambda function, IAM role, log group | Backend logic, restricted permissions, logs |
| API | HTTP API, JWT authorizer, 4 routes, stage, permission | Public entry point with token checking and rate limits |
| Frontend | S3 bucket, bucket policy, CloudFront distribution, origin access control | Private storage served securely over HTTPS |

> **ARCHITECTURE:** CloudFormation works out the order itself. It sees that the Lambda function needs the table's name and the role's ARN, so it creates the table and role first. This web of references is called a **dependency graph**. You write what you want, not the order to build it.

## Step 8: Run the deploy script

From inside the `community-wall-v2` folder:

```bash
./deploy.sh community-wall-v2 eu-west-1
```

(If you get "permission denied", run `chmod +x deploy.sh` first, or run `bash deploy.sh community-wall-v2 eu-west-1`.)

The script performs four stages and prints progress:

1. **Deploys the stack** (`aws cloudformation deploy`). This takes about 5 to 8 minutes, mostly waiting for CloudFront to spread to AWS's edge locations.
2. **Writes configuration into the page.** It reads the stack's outputs (API address, Cognito sign-in address, app client ID) and substitutes them for the three placeholders at the top of the page's script.
3. **Uploads the page** to the private S3 bucket.
4. **Clears the CloudFront cache** so visitors immediately get the new page.

> **REASON:** The page needs the API address and Cognito details, but those only exist after the stack is built. The script closes that loop automatically so you never copy and paste values by hand.

> **NOTE:** If the stack fails, CloudFormation rolls back and removes what it created. Read the error message with: `aws cloudformation describe-stack-events --stack-name community-wall-v2 --region eu-west-1 --max-items 15`. The first `CREATE_FAILED` row names the cause. Fix it, then run the script again.

**Check:** the script ends with `Done. Open: https://xxxx.cloudfront.net` and prints an admin command.

## Step 9: Open your site

Open the printed address in your browser.

**Check:** you see the flyer, the question "What's your review of the program?", and the **Share your review** button.

---

# Part 4: Use and test the app

Test each feature. This is also how you learn what the system enforces.

## Step 10: Create your account

1. Click **Share your review**. You see the wall and a **Sign in or sign up** button.
2. Click it. You are taken to Cognito's hosted sign-in page.
3. Choose **Sign up**, enter your email and a password (at least 10 characters, with upper case, lower case, and a number).
4. Cognito emails you a verification code. Enter it.
5. You are returned to the site, now signed in. The form appears.

> **NOTE:** Cognito's default email sender has a small daily limit (as far as the author knows, about 50 emails per day, but check the current Cognito quotas). That is fine for testing. If you plan a live session where many people sign up at once, set up **Amazon SES** for Cognito or have attendees read the wall while only a few post.

> **ARCHITECTURE:** Your application never sees or stores passwords. Cognito's hosted page collects them, and your page only receives tokens. Outsourcing authentication to a specialist service removes the highest-risk code from your project (password storage, reset flows, brute-force protection).

**Check:** the top of the form says "Signed in as your@email".

## Step 11: Post a review

1. Enter a display name and country.
2. Click a star rating.
3. Write a review, or click a colored chip such as "I learned a lot" to start one.
4. Click **Add my socials**. Fill in any of LinkedIn, X, or GitHub. You can paste a profile link or type a username.
5. Click **Post my review**.

The page scrolls to the wall and your review appears with the average rating at the top and your social buttons underneath.

> **NOTE:** Social links are public. Anyone who reads the wall can click them. Only add profiles you want people to see.

**Check:** your review appears with its stars and social buttons, and the summary line shows "5.0 out of 5, from 1 review" (or your rating).

## Step 12: Edit and delete your review

1. Click **Edit** on your review. The form fills in with your values and the button changes to **Save changes**. A **Cancel edit** button appears.
2. Change the rating or text and save. The card now shows "(edited)", and the average updates.
3. Click **Delete**, confirm, and the review disappears and the totals drop back.

**Check:** the average and count change each time, matching your actions.

## Step 13: Prove that other people cannot change your review

1. Post a review again.
2. Open the site in a **private (incognito) window** and sign up with a **second email address**.
3. Look at your first review from this second account. There is no Edit or Delete button on it.

> **REASON:** Hiding a button is only a courtesy to the user. The real protection is in the backend, which you will test next.

**Check:** the second account sees reviews but only has buttons on its own.

## Step 14: Test security from outside the page

Do this from your terminal. Replace `YOUR_API_URL` with the `ApiUrl` value (find it with the command below).

```bash
API_URL=$(aws cloudformation describe-stacks --stack-name community-wall-v2 --region eu-west-1 \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)

# Reading is public: expect HTTP 200 and your reviews
curl -i "$API_URL/reviews"

# Writing without a token: expect HTTP 401 Unauthorized
curl -i -X POST "$API_URL/reviews" -H "content-type: application/json" \
  -d '{"name":"Hacker","message":"hi","rating":5}'
```

> **ARCHITECTURE:** This is the key lesson of the app. The 401 came from **API Gateway**, before your Lambda code ran at all. Invalid or missing tokens never reach your code, and you pay nothing for the rejected requests. This is called the **front door check**.

**Check:** the first call returns 200 and the second returns 401.

## Step 15: Become an admin

1. Make sure you have signed up (Step 10).
2. Run the command printed at the end of the deploy script, which looks like this (use your own pool ID and email):

```bash
aws cognito-idp admin-add-user-to-group \
  --user-pool-id YOUR_POOL_ID --username YOUR_EMAIL --group-name admin --region eu-west-1
```

3. In the page click **Sign out**, then sign in again.
4. The top of the form now says "(admin)", and every review has a **Remove (admin)** button.

> **NOTE:** You must sign in again because group membership is written into your token when it is issued. An old token does not know about your new group.

> **REASON:** Roles are managed in Cognito (not in your code), so you can promote or demote moderators without redeploying the app. This is called **role-based access control**.

**Check:** you can remove another user's review, and that user can no longer see it.

---

# Part 5: Look inside the running system

Understanding what happened is as important as making it work. Use the console (same region).

## Step 16: Read the logs (CloudWatch)

1. Open **CloudWatch**, then **Log groups**, then `/aws/lambda/community-wall-v2-api`.
2. Open the newest log stream. Find lines like `{"level": "info", "msg": "review_created", ...}`.

> **REASON:** The logs are written as JSON (one record per line) instead of free text. Structured logs can be searched, filtered, and counted automatically (for example "how many errors per hour"), which is what production teams rely on.

**Check:** you can find the creation, update, and delete events from your own testing.

## Step 17: See the data (DynamoDB)

1. Open **DynamoDB**, then **Tables**, then `community-wall-v2-data`, then **Explore table items**.
2. You will see two kinds of items:
   - Reviews, with `pk` starting `EVENT#` and a sort key `sk` like `1792234412000#a1b2c3d4`.
   - One `STATS` item holding `reviewCount` and `ratingSum`.

> **ARCHITECTURE:** DynamoDB finds items by key, not by searching. We design keys for the questions we will ask. All reviews share the partition key `EVENT#<event id>`. The sort key begins with a millisecond timestamp, so asking for "the newest 20" is a single cheap query with no scanning, and results come back already in order.

> **REASON:** The average rating is `ratingSum / reviewCount`. Keeping those two numbers in a separate item means the page does not have to download every review to compute an average. A DynamoDB **transaction** updates the review and the totals together, so they can never disagree even if two people post at the same instant.

**Check:** the `STATS` item matches the number of reviews you see.

## Step 18: See the users (Cognito)

1. Open **Amazon Cognito**, then **User pools**, then `community-wall-v2-users`.
2. Open **Users** to see the accounts you created and **Groups** to see `admin` and its members.

**Check:** your test accounts are listed and confirmed.

## Step 19: See the API rules (API Gateway)

1. Open **API Gateway**, then `community-wall-v2-api`, then **Routes**.
2. `GET /reviews` shows no authorizer. `POST /reviews`, `PUT /reviews/{id}`, and `DELETE /reviews/{id}` show the JWT authorizer.
3. Open **Stages**, then `$default`, and look at the throttling: reads allow a high rate, writes a lower one.

> **REASON:** Reading a public wall should be easy for everyone, so reads are open and generously limited. Writes are the abuse risk, so they require identity and a stricter rate limit.

## Step 20: Confirm the bucket is private

Try to open the S3 file directly (replace the bucket name from the stack outputs):

```
https://YOUR_BUCKET.s3.eu-west-1.amazonaws.com/index.html
```

You should get an **Access Denied** message, while the CloudFront address works.

> **ARCHITECTURE:** The bucket allows reading only for this one CloudFront distribution, through a feature called **origin access control**. Visitors can never bypass CloudFront to reach the bucket. That keeps all traffic going through one controlled, cacheable, HTTPS-only entrance.

**Check:** the direct S3 address is denied and the CloudFront address loads.

---

# Part 6: How it works in detail

## 6.1 The sign-in flow, step by step

This is the OAuth 2.0 **authorization code flow with PKCE**, the standard for browser apps.

1. **The user clicks Sign in.** The page creates two random values: a `state` and a `code_verifier` (a secret), and stores them in the browser's `sessionStorage`. It computes a one-way hash of the verifier, called the `code_challenge`.
2. **Redirect to Cognito.** The browser goes to Cognito's `/oauth2/authorize` address, carrying the challenge (not the secret) and the state.
3. **The user authenticates.** Cognito shows its hosted page, handles sign-up, verification, password, and optional MFA.
4. **Redirect back with a code.** Cognito returns the browser to our site with a short-lived, single-use `code` and the same `state`.
5. **The page checks the state.** If it does not match what was stored, the page stops (this blocks a class of forgery attacks).
6. **The page exchanges the code for tokens.** It sends the code and the original secret verifier to `/oauth2/token`. Cognito hashes the verifier and compares it with the challenge from step 2. If they match, it returns an access token, an ID token, and a refresh token.
7. **The page keeps the session** and sends the access token with each write request.

> **REASON (why PKCE):** A browser app is a "public client": anything in its code can be read by anyone, so it cannot safely hold a client secret. PKCE replaces the secret with a one-time proof. Even if someone intercepts the code in step 4, it is useless without the verifier, which never left the user's browser.

> **REASON (access token, not ID token, for the API):** The ID token says who the user is, for the page's display. The access token is meant for calling APIs. Using the right token for the right purpose is a standard best practice.

> **REASON (sessionStorage):** Tokens live in `sessionStorage`, which is cleared when the tab closes. The page never writes tokens to `localStorage`, which persists indefinitely. Tokens last 60 minutes, then the user signs in again.

## 6.2 Two layers of protection: authentication and authorization

When you post a review, two checks happen:

1. **API Gateway (authentication).** The JWT authorizer verifies the token's signature using Cognito's published keys, and checks that the token has not expired and was issued for our app client. If anything is wrong, it replies 401 and stops.
2. **Lambda (authorization).** For an edit or delete, our code loads the review, compares the token's user ID (`sub`) with the review's `userId`, and replies 403 if they differ. For delete, it also allows members of the `admin` group.

> **ARCHITECTURE:** This is **defense in depth**. The gateway ensures only real, signed-in users reach your code. Your code then decides what that particular user may do. Neither layer trusts the browser. The page hides buttons for convenience, but the rules are enforced on the server.

> **NOTE:** The Lambda reads identity from the claims the gateway already verified. It never decodes or trusts a token it received directly. That is why the user ID cannot be faked by editing the request.

## 6.3 The Lambda function

One function handles all four routes. API Gateway tells it which route matched (`routeKey`), and a small table sends the request to the right function:

| Route | Who | What it does |
|---|---|---|
| `GET /reviews` | Everyone | Returns up to 10 to 50 newest reviews, the stats, and a `nextToken` for more |
| `POST /reviews` | Signed-in users | Validates input, saves the review and updates stats in one transaction |
| `PUT /reviews/{id}` | The review's owner | Validates, updates the review, adjusts the totals by the difference |
| `DELETE /reviews/{id}` | Owner or admin | Deletes the review and subtracts it from the totals |

Design details worth noticing:
- **Validation.** Names, countries, and messages are trimmed and length-limited. Ratings must be whole numbers 1 to 5. Request bodies over 4 KB are rejected.
- **Error mapping.** Bad input returns 400, wrong owner returns 403, a missing review returns 404, and unexpected failures return a generic 500 (details go to the log, not to the user).
- **Paging.** `nextToken` encodes where the last page ended. The code verifies the token belongs to this event before using it.
- **Expiry.** Items have an `expiresAt` time. DynamoDB deletes them automatically (TTL), but it can take a while, so the query also filters out expired items.

> **REASON (one function):** For a small app, one function with a route table is simpler to deploy and read. Large teams often split into one function per route for finer permissions and independent scaling. Neither is wrong, the choice depends on size.

> **REASON (IAM):** The function's role allows only `GetItem`, `PutItem`, `UpdateItem`, `DeleteItem`, and `Query`, and only on this one table. It cannot create tables, read other tables, or touch any other service apart from writing its own logs.

## 6.4 Social links are untrusted input

Anything a user types and other people later click is a security risk. Someone could try a malicious `javascript:` address or a link to a look-alike phishing site. This is how the app handles it:

1. The user types a username or pastes a profile link.
2. The backend accepts **only** LinkedIn, X (or Twitter), and GitHub. It checks the host name exactly, so `linkedin.com.evil.io` is rejected.
3. It validates the username against that site's rules.
4. It then **builds a new, clean `https` link itself** from the username. The text the user typed is never stored or shown as a link.
5. The page checks the link's host again before drawing the button, and opens it with `rel="noopener noreferrer nofollow ugc"` in a new tab.

> **REASON:** Never trust data from a browser, and never repeat it back as a link without checking it. Rebuilding the value from validated parts (a method called **canonicalization**) is stronger than trying to filter out bad strings.

## 6.5 CORS and throttling

**CORS** (Cross-Origin Resource Sharing) is a browser rule: a page from one address may only call another address if that address says it is allowed. Our API allows calls only from our own CloudFront address, with the methods and headers the app uses.

> **REASON:** Without CORS limits, any website a user visits could make that user's browser call your API. Locking it to your own site is a cheap, standard protection. (It does not stop direct tools such as `curl`, which is why the token check exists as well.)

**Throttling** limits how many requests are allowed per second: 100 per second for reads, 10 per second for each write route.

> **ARCHITECTURE:** Limits protect your wallet and your database from accidents and abuse. Different limits for different routes reflect different risks: reads are cheap and expected in bulk, writes are costly and the common target of spam.

## 6.6 The frontend

- **Demo mode:** if the three configuration values are still placeholders, the page runs on in-memory data. This lets the same file be previewed, taught from, and deployed.
- **No `innerHTML`:** all user text is inserted with `textContent`, so a message such as `<script>` is shown as plain text and never runs. This prevents **cross-site scripting (XSS)**.
- **Accessibility:** buttons have labels, star ratings describe themselves, the wall announces updates, focus outlines are visible, and animation respects the "reduce motion" setting.
- **Refresh:** the wall refreshes every 15 seconds while visible and not being edited.

---

# Part 7: Change something and redeploy

1. Edit `backend/index.py` (for example, change the 200-character limit).
2. The template carries its own copy of the Lambda code, so the two must match. Copy your change into the template by running this from the project folder:

```bash
python3 - <<'PY'
import re
t = open('template.yaml').read()
code = open('backend/index.py').read().rstrip('\n').split('\n')
block = '\n'.join(('          ' + l) if l.strip() else '' for l in code)
pat = re.compile(r"(        ZipFile: \|\n)(.*?)(\n      Tags:)", re.S)
open('template.yaml', 'w').write(pat.sub(lambda m: m.group(1) + block + m.group(3), t, count=1))
PY
```

3. Run `./deploy.sh community-wall-v2 eu-west-1` again.

> **REASON:** CloudFormation compares your template with what exists and changes only the differences. You can safely rerun the script as often as you like. This is called an **idempotent** deployment.

> **NOTE:** The template contains a copy of the Lambda code so you can deploy with no packaging step. For a larger project you would keep the code in separate files and package it (with AWS SAM or CDK).

**Challenge ideas:** add a "role" field (student, engineer, other); add a character counter; show only reviews from the last hour; add a CloudWatch alarm that emails you when Lambda has an error; deploy a second copy with a different stack name and event ID.

---

# Part 8: Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| The deployed page says "Demo mode" | Placeholders were not replaced | Deploy with `deploy.sh`, not by uploading the file by hand |
| Cognito shows `redirect_mismatch` | You opened the site at an address other than the CloudFront one, or without the final `/` | Open exactly the `SiteUrl` the script printed |
| Sign-in returns and says "Sign-in failed" | The page lost its stored secret (new tab, private mode, or storage blocked) | Start again from the page in one tab |
| No verification email | Cognito's daily email limit, or it went to spam | See the NOTE in Step 10 |
| "Session expired" or 401 when posting | Token older than 60 minutes | Sign in again |
| 403 "You can only edit your own review" | You are not the owner | Expected behavior |
| No Remove button after becoming admin | Old token | Sign out and sign in again |
| Browser console shows a CORS error | Page opened from a different address, or API changed | Use the CloudFront address from the stack outputs |
| `{"message":"Internal Server Error"}` | Lambda failed | Read the CloudWatch log group (Step 16) |
| Deploy fails on the user pool domain | The domain prefix is taken | Deploy with a different stack name or change the `ProjectName` parameter |
| Edited page still looks old | CloudFront cache | `deploy.sh` clears it; otherwise create an invalidation for `/*` |
| Cannot find a resource | Wrong region | Check the region selector |

---

# Part 9: Before real users arrive (production checklist)

The app is built with good habits, but a public launch needs more. Work through these in order of risk.

| Area | What to add | Reason |
|---|---|---|
| Email | Amazon SES for Cognito messages | The default sender has low limits and a generic address |
| Domain | Route 53 + ACM certificate, and a custom Cognito domain | Trust and branding (`wall.example.com` instead of a random address) |
| Abuse | AWS WAF with rate rules on CloudFront and the API, a CAPTCHA for sign-up | Bots and spam are the first problem of any public form |
| Sessions | Use the refresh token so users stay signed in; stricter Content Security Policy headers on CloudFront | Better experience and defense against injected scripts |
| Monitoring | CloudWatch alarms (Lambda errors, API 5xx, unusual 4xx) sent to email through SNS | You should hear about problems before your users do |
| Delivery | GitHub Actions with OIDC (no stored AWS keys), tests, and separate dev and prod stacks (ideally separate accounts) | Repeatable, reviewed, safe changes |
| Privacy | A privacy notice, a retention policy (the app deletes reviews after 30 days by default), and a way to delete a user's data | Legal and ethical responsibility for personal data |
| Resilience | Point-in-time recovery is already on for the table | Lets you restore data to any second in the last 35 days |
| Moderation | An admin dashboard and report button | Scale beyond one person removing reviews by hand |

> **ARCHITECTURE:** Production readiness is not one feature. It is a set of layers: identity, rate limiting, monitoring, repeatable deployment, recovery, and privacy. Each layer reduces a different kind of risk.

---

# Part 10: Clean up

When you are finished, delete everything so nothing keeps costing money.

```bash
BUCKET=$(aws cloudformation describe-stacks --stack-name community-wall-v2 --region eu-west-1 \
  --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)

# 1. Empty the bucket (CloudFormation cannot delete a bucket that has files in it)
aws s3 rm "s3://$BUCKET" --recursive --region eu-west-1

# 2. Delete the stack and everything in it
aws cloudformation delete-stack --stack-name community-wall-v2 --region eu-west-1

# 3. Wait until it finishes
aws cloudformation wait stack-delete-complete --stack-name community-wall-v2 --region eu-west-1
```

> **REASON:** Because everything was created from one template, everything is removed together. Nothing is left behind to find and delete by hand. This is one of the biggest practical benefits of Infrastructure as Code.

**Check:** `aws cloudformation describe-stacks --stack-name community-wall-v2 --region eu-west-1` reports that the stack does not exist.

---

# Glossary

| Term | Meaning |
|---|---|
| **ARN** | Amazon Resource Name, the unique identifier of any AWS resource |
| **CDN** | Content delivery network: servers around the world that serve copies of your files |
| **Claims** | Facts stored inside a token, such as the user ID and groups |
| **CORS** | Browser rule controlling which websites may call an API |
| **IaC** | Infrastructure as Code: describing infrastructure in files |
| **IAM role** | A set of permissions that a service (like Lambda) can assume |
| **JWT** | JSON Web Token: a signed token proving identity and carrying claims |
| **MFA** | Multi-factor authentication: a second proof, such as a phone code |
| **OAuth 2.0** | The standard way to grant a site access without sharing passwords |
| **OAC** | Origin access control: lets only CloudFront read a private S3 bucket |
| **PKCE** | A one-time proof that makes OAuth safe for browser apps |
| **Partition key / sort key** | The two parts of a DynamoDB item's address |
| **Stack** | A set of AWS resources created together from one CloudFormation template |
| **Throttling** | Limiting requests per second |
| **TTL** | Time to live: automatic deletion of items after a set time |
| **XSS** | Cross-site scripting: an attack that makes a page run an attacker's code |
