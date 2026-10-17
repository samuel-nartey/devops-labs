# Community Wall v2: build a secure, serverless web app on AWS (console guide)

Workshop project for **AWS User Group Kumasi**. Everything in this guide is done in the **AWS Management Console** in your browser. There is no terminal, no AWS CLI, and nothing to install.

You will deploy a real web application where attendees read a live wall of program reviews, sign in with their own account, post a star rating and review, edit or delete their own review, and optionally share their LinkedIn, X, and GitHub profiles so others can connect. A moderator (admin) can remove any review.

By the end you will have deployed and tested a complete cloud application and understood why each piece exists.

| | |
|---|---|
| Time | About 60 to 90 minutes (the stack itself takes 5 to 8 minutes to build) |
| Cost | A few cents, and often nothing, depending on your account's free tier or credits |
| You need | An AWS account, an email address, a browser, and a plain text editor (Notepad, TextEdit in plain text mode, VS Code). No prior cloud experience is assumed |
| Services used | CloudFormation, S3, CloudFront, Cognito, API Gateway, Lambda, DynamoDB, IAM, CloudWatch |

---

## How to read this guide

Three kinds of callouts appear throughout:

> **NOTE:** An important detail, warning, or tip. Read these before you continue.

> **REASON:** Why we do something this way. Understanding the reason is how you learn to make your own decisions later.

> **ARCHITECTURE:** The design thinking behind a choice. These explain how professionals structure cloud applications.

Every step ends with a **Check**, a quick way to confirm the step worked before you move on.

> **NOTE:** About testing. The backend code was tested locally against a simulated database (ownership rules, admin delete, ratings, paging, input validation, and social-link safety). The CloudFormation template passes `cfn-lint`, the standard template checker. The full stack has not been run in a real AWS account by the author of this guide, which is why Part 4 walks you through testing every feature yourself.

> **NOTE:** Console screens change from time to time. If a label differs slightly from this guide, pick the closest option. The goal is always the same: a private bucket, HTTPS only, sign-in through Cognito, and a Lambda role that can touch one table.

---

# Part 1: Understand what you are building

## 1.1 The files you need

| File | Use it for | Needed? |
|---|---|---|
| `README.md` | This guide | Read first |
| `template.yaml` | The CloudFormation blueprint. You upload it in the console and it builds everything | Yes |
| `frontend/index.html` | The web page. You edit three values in it, then upload it to S3 | Yes |
| `backend/index.py` | The Lambda code. A copy is already embedded in `template.yaml`, so you do not upload it | Reference |
| `frontend/flyer.jpg` | The original flyer (already embedded in `index.html`) | No, keep for social posts |
| `deploy.sh` | A command-line shortcut that does Part 3 in one go | Not used in this guide |

```
community-wall-v2/
  README.md
  template.yaml
  deploy.sh               (optional command-line shortcut, not used here)
  backend/index.py
  frontend/index.html     (flyer embedded, follow links filled in)
  frontend/flyer.jpg      (optional original)
```

## 1.2 What attendees see

1. **The flyer** at the top.
2. **"What's your review of the program?"** with a big **Share your review** button.
3. Tapping the button reveals **the wall**: the live list of reviews with the average rating, and a **Sign in or sign up** button.
4. After signing in, a form appears (name, country, star rating, review, quick-start chips, optional social links) and the user's own reviews get **Edit** and **Delete** buttons.
5. **Follow us** buttons for LinkedIn, Meetup, and WhatsApp.

Two modes:
- **Demo mode:** if the three configuration values in `index.html` are still placeholders, the page runs on its own with a fake sign-in and sample reviews. Nothing is saved. Use it to rehearse or preview without AWS.
- **Live mode:** once the three values are set, reviews are stored in DynamoDB, sign-in is handled by Cognito, and the wall refreshes every 15 seconds for everyone.

The follow links live in the `LINKS` block near the bottom of the script in `index.html`. Edit them there if you need to.

## 1.3 The big picture

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

## 1.4 The services in plain language

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

## 1.5 Concepts every beginner should know

**Serverless.** You do not rent or manage a computer. You give AWS your code and it runs it on demand, then charges only for what you use. There is nothing to patch, restart, or log into.

> **REASON:** For a small, spiky workload (a workshop, a launch, a campaign), serverless is cheaper and safer than a server that sits idle and needs security updates.

**Static page, dynamic app.** The web page itself (`index.html`) is a static file: every visitor receives the same file. The app is dynamic because that page calls an API to read and write live data. Most modern web apps work exactly this way.

> **ARCHITECTURE:** Separating the "frontend" (files served from S3 and CloudFront) from the "backend" (API, functions, database) lets each part scale and be secured independently. The frontend can serve millions of visitors without ever touching your code or database.

**API.** A set of web addresses your page can call to ask for or change data. Ours has four: read reviews, create a review, update a review, delete a review.

**Authentication versus authorization.** Authentication answers "who are you?" (sign-in). Authorization answers "what are you allowed to do?" (only edit your own review, only admins can remove others'). This app does both, in two different places, as you will see in Part 6.

**Tokens, JWT, and OAuth.** After sign-in, Cognito gives the browser a **JWT** (JSON Web Token). It is a small piece of text that contains facts about the user (a unique ID, groups, an expiry time) and is **digitally signed** by Cognito, so nobody can forge or change it. The sign-in process itself follows **OAuth 2.0**, the industry-standard way to sign in without your own code ever seeing a password.

**IAM and least privilege.** IAM controls permissions. "Least privilege" means giving each component only the permissions it needs and nothing more.

> **REASON:** If Lambda is ever compromised through a bug, the damage is limited to what its role allows. Ours can only read and write one table. It cannot touch other tables, buckets, or users.

**Infrastructure as Code (IaC).** Instead of clicking to create each resource, you describe your infrastructure in a file (`template.yaml`) and CloudFormation builds it. A set of resources built from one template is called a **stack**. In this guide you still use the console, but you click **once** (upload the template) instead of dozens of times.

> **REASON:** Clicks cannot be reviewed, repeated, or undone reliably. A template can be stored in Git, reviewed by teammates, reused in other accounts or regions, and deleted in one click.

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

Look at the region selector at the top right of the console. This guide uses **Europe (Ireland), `eu-west-1`**. Use the same region for everything. If you prefer another region, that is fine: stay in it for the whole guide and read `eu-west-1` as your region.

> **NOTE:** The most common beginner problem is creating something in one region and looking for it in another. If a resource seems to be missing, check the region selector first. Every console page you open in this guide (CloudFormation, S3, Cognito, API Gateway, Lambda, DynamoDB, CloudWatch) must show the same region. CloudFront is the one exception, because it is a global service.

> **ARCHITECTURE:** AWS is split into independent regions (geographic areas). Most services live inside exactly one region. Choose a region close to your users, and keep an application's parts together to reduce delay and avoid cross-region complexity.

**Check:** the region selector shows Europe (Ireland) or the region you chose.

## Step 4: Get the project files onto your computer

1. Download the project zip (`community-wall-v2.zip`) and **unzip** it.
2. Confirm you can see `template.yaml` and the `frontend` and `backend` folders.

**Check:** you can find `template.yaml` and `frontend/index.html` on your computer.

## Step 5 (optional): Preview the page without AWS

Double-click `frontend/index.html` to open it in your browser. It runs in **demo mode**: a fake sign-in, in-memory reviews, and every feature of the interface. Nothing is saved.

> **REASON:** Seeing the interface first makes the rest of the guide easier to follow, and demo mode lets you rehearse a presentation without any cloud dependency.

**Check:** you see the flyer, the review prompt, and a "Demo mode" note after you click **Share your review**.

---

# Part 3: Deploy the application

## Step 6: Know what will be created

The template creates these resources. You do not need to memorize them, but it helps to see how they connect.

| Group | Resources | Purpose |
|---|---|---|
| Identity | Cognito user pool, domain, app client, `admin` group | Sign-up, sign-in, tokens, moderator role |
| Data | DynamoDB table | Stores reviews and rating totals |
| Compute | Lambda function, IAM role, log group | Backend logic, restricted permissions, logs |
| API | HTTP API, JWT authorizer, 4 routes, stage, permission | Public entry point with token checking and rate limits |
| Frontend | S3 bucket, bucket policy, CloudFront distribution, origin access control | Private storage served securely over HTTPS |

> **ARCHITECTURE:** CloudFormation works out the order itself. It sees that the Lambda function needs the table's name and the role's ARN, so it creates the table and role first. This web of references is called a **dependency graph**. You write what you want, not the order to build it.

## Step 7: Create the stack

1. Open **CloudFormation** in the console and confirm the region (Step 3).
2. Choose **Create stack**, then **With new resources (standard)**.
3. Under **Prerequisite - Prepare template**, keep **Choose an existing template**.
4. Under **Specify template**, choose **Upload a template file**, click **Choose file**, and select `template.yaml` from the project folder. Choose **Next**.
5. **Stack name:** `community-wall-v2`.
6. Leave the three parameters at their defaults, or change them if you wish:
   - `ProjectName`: `community-wall-v2` (used to name every resource)
   - `EventId`: `kumasi-2026-10-17` (reviews are stored under this event name)
   - `ReviewRetentionDays`: `30` (reviews delete themselves after this many days)

   Choose **Next**.
7. On **Configure stack options**, leave everything as it is. Choose **Next**.
8. On the review page, scroll to **Capabilities** and tick **I acknowledge that AWS CloudFormation might create IAM resources**. Choose **Submit**.

> **REASON (the IAM tick box):** The template creates an IAM role for Lambda. CloudFormation makes you confirm this on purpose, because IAM changes can affect security. It is a speed bump, not an error.

> **NOTE:** Choose a different `ProjectName` if a second copy of this app already exists in the same account. The Cognito sign-in domain is built from the project name and your account ID, and it must be unique in the region.

**Check:** the stack appears with the status **CREATE_IN_PROGRESS**.

## Step 8: Wait for the stack and copy its outputs

1. Stay on the stack page and open the **Events** tab. Refresh now and then. The first resources appear within a minute. CloudFront is the slowest, so expect **5 to 8 minutes** in total.
2. When the status at the top changes to **CREATE_COMPLETE**, open the **Outputs** tab.
3. Copy these values into a text file for the next step:

| Output key | You will use it for |
|---|---|
| `SiteUrl` | The address of your finished site |
| `ApiUrl` | Goes into the page (value 1 of 3) |
| `CognitoDomainUrl` | Goes into the page (value 2 of 3) |
| `UserPoolClientId` | Goes into the page (value 3 of 3) |
| `BucketName` | The S3 bucket you upload the page to |
| `DistributionId` | Reference only (helps you find the right CloudFront distribution) |
| `UserPoolId`, `TableName` | Reference only |

> **REASON:** The page needs the API address and Cognito details, but those only exist after the stack is built. That is why you build the stack first and configure the page second.

> **NOTE:** If the status becomes **ROLLBACK_IN_PROGRESS**, then **ROLLBACK_COMPLETE**, the stack failed and CloudFormation removed what it had built. Open the **Events** tab and scroll to the **earliest** row marked **CREATE_FAILED**. Its **Status reason** names the cause. A stack in **ROLLBACK_COMPLETE** cannot be reused: select it, choose **Delete**, wait for it to disappear, fix the cause, and create the stack again from Step 7. See Part 9 for common causes.

**Check:** the status is **CREATE_COMPLETE** and you have the `ApiUrl`, `CognitoDomainUrl`, and `UserPoolClientId` values.

## Step 9: Put the three values into the page

The page is still in demo mode. You will switch it to live mode by editing one line.

1. Open `frontend/index.html` in a **plain text editor** (Notepad, VS Code, TextEdit in plain text mode). Do not use Word.
2. Use **Find** (Ctrl+F) to search for `PASTE_API_URL`. You will land on this line:

   ```js
   const CONFIG = { apiUrl: "PASTE_API_URL", cognitoDomain: "PASTE_COGNITO_DOMAIN", clientId: "PASTE_CLIENT_ID" };
   ```

3. Replace the three placeholders with your outputs, keeping the quotation marks. The result looks like this (your values will differ):

   ```js
   const CONFIG = { apiUrl: "https://abc123xyz.execute-api.eu-west-1.amazonaws.com", cognitoDomain: "https://community-wall-v2-123456789012.auth.eu-west-1.amazoncognito.com", clientId: "1a2b3c4d5e6f7g8h9i0j1k2l3m" };
   ```

4. Save the file, keeping the name `index.html`.

> **NOTE:** Use straight quotation marks (`"`), not curly ones. Do **not** add a slash at the end of the API address or the Cognito address. Do not change anything else in the file.

> **NOTE:** The file is large (about 250 KB) because the flyer image is embedded inside it. That is normal. Some editors pause for a second when opening it.

**Check:** searching the file for `PASTE` finds nothing in the `CONFIG` line.

## Step 10: Upload the page to S3

1. Open **S3**, then **Buckets**, and click the bucket named in the `BucketName` output (it starts with `community-wall-v2-sitebucket-`).
2. Choose **Upload**, then **Add files**, select your edited `index.html`, and choose **Upload**.
3. Wait for **Upload succeeded**, then choose **Close**.

> **NOTE:** The file must be called exactly `index.html`, and it must sit at the top level of the bucket, not inside a folder. CloudFront is set to serve `index.html` for the main address.

> **ARCHITECTURE:** Notice that you did not change any bucket settings. The template already made it **private** (Block all public access is on) and wrote a bucket policy that lets only this one CloudFront distribution read from it. This is called **origin access control**.

**Check:** `index.html` is listed in the bucket.

## Step 11: Open your site

Open the `SiteUrl` value from the stack outputs in your browser.

**Check:** you see the flyer, the question "What's your review of the program?", and the **Share your review** button, and there is no "Demo mode" note after you click the button.

> **NOTE:** If you see an XML **AccessDenied** message instead, wait two minutes and refresh, then check Part 9. If you see "Demo mode", repeat Steps 9 and 10.

---

# Part 4: Use and test the app

Test each feature. This is also how you learn what the system enforces.

## Step 12: Create your account

1. Click **Share your review**. You see the wall and a **Sign in or sign up** button.
2. Click it. You are taken to Cognito's hosted sign-in page.
3. Choose **Sign up**, enter your email and a password (at least 10 characters, with upper case, lower case, and a number).
4. Cognito emails you a verification code. Enter it.
5. You are returned to the site, now signed in. The form appears.

> **NOTE:** Cognito's default email sender has a small daily limit (as far as the author knows, about 50 emails per day, but check the current Cognito quotas). That is fine for testing. If you plan a live session where many people sign up at once, set up **Amazon SES** for Cognito, or have attendees read the wall while only a few post.

> **ARCHITECTURE:** Your application never sees or stores passwords. Cognito's hosted page collects them, and your page only receives tokens. Outsourcing authentication to a specialist service removes the highest-risk code from your project (password storage, reset flows, brute-force protection).

**Check:** the top of the form says "Signed in as your@email".

## Step 13: Post a review

1. Enter a display name and country.
2. Click a star rating.
3. Write a review, or click a colored chip such as "I learned a lot" to start one.
4. Click **Add my socials**. Fill in any of LinkedIn, X, or GitHub. You can paste a profile link or type a username.
5. Click **Post my review**.

The page scrolls to the wall and your review appears with the average rating at the top and your social buttons underneath.

> **NOTE:** Social links are public. Anyone who reads the wall can click them. Only add profiles you want people to see.

**Check:** your review appears with its stars and social buttons, and the summary line shows "5.0 out of 5, from 1 review" (or your rating).

## Step 14: Edit and delete your review

1. Click **Edit** on your review. The form fills in with your values and the button changes to **Save changes**. A **Cancel edit** button appears.
2. Change the rating or text and save. The card now shows "(edited)", and the average updates.
3. Click **Delete**, confirm, and the review disappears and the totals drop back.

**Check:** the average and count change each time, matching your actions.

## Step 15: Prove that other people cannot change your review

1. Post a review again.
2. Open the site in a **private (incognito) window** and sign up with a **second email address**.
3. Look at your first review from this second account. There is no Edit or Delete button on it.

> **REASON:** Hiding a button is only a courtesy to the user. The real protection is in the backend, which you test in Step 16.

**Check:** the second account sees reviews but only has buttons on its own.

## Step 16: Test the backend directly in the Lambda console

You can run the Lambda function yourself and watch how it responds, without the website at all.

1. Open **Lambda**, then **Functions**, and click `community-wall-v2-api`.
2. Open the **Test** tab. Choose **Create new event**, name it `get-test`, and paste:

   ```json
   { "routeKey": "GET /reviews" }
   ```

   Choose **Save**, then **Test**. Expect `"statusCode": 200` and a body that lists your reviews and the stats.

3. Create a second event named `post-test` and paste the following. It imitates what API Gateway passes to Lambda after it has checked a token (the `claims` block is the verified identity):

   ```json
   {
     "routeKey": "POST /reviews",
     "requestContext": { "authorizer": { "jwt": { "claims": { "sub": "test-user-1" } } } },
     "body": "{\"name\":\"Ama\",\"country\":\"Ghana\",\"message\":\"Hello from the Lambda console\",\"rating\":5}"
   }
   ```

   Choose **Test**. Expect `"statusCode": 201`.

4. Run `get-test` again. The new review appears in the list. Refresh the website and it appears on the wall too, under the name Ama.

5. Break it on purpose. Edit the `post-test` event and change `"rating":5` to `"rating":9`, then test. Expect `"statusCode": 400` and the message `rating must be a whole number from 1 to 5`.

> **REASON:** The `body` is a JSON string **inside** JSON, which is why the inner quotation marks are written as `\"`. API Gateway hands Lambda the request body as plain text, and the code parses it itself.

> **NOTE:** The test review is real. It lives in the same table as everyone else's. Remove it as an admin once you complete Step 17, or delete the item in DynamoDB (Step 19).

> **ARCHITECTURE:** This test skips API Gateway, so it does **not** prove that signed-out visitors are blocked. That protection happens before Lambda runs. To see the rejection yourself, send a POST to `YOUR_API_URL/reviews` with no `Authorization` header using a request tool such as Postman. API Gateway answers **401 Unauthorized** and your Lambda code never runs. Rejected requests cost you nothing. This is called the **front door check**.

**Check:** the first test returns 200, the second returns 201, and the invalid rating returns 400.

## Step 17: Become an admin

Admins are members of a Cognito group called `admin`. You add yourself in the console.

1. Make sure you have signed up (Step 12).
2. Open **Amazon Cognito**, then **User pools**, and click `community-wall-v2-users`.
3. Open the **Groups** tab, click the **admin** group, and choose **Add user to group**.
4. Select your user and choose **Add**.
5. In the website click **Sign out**, then sign in again.
6. The top of the form now says "(admin)", and every review has a **Remove (admin)** button.

> **NOTE:** You must sign in again because group membership is written into your token when it is issued. An old token does not know about your new group.

> **REASON:** Roles are managed in Cognito (not in your code), so you can promote or demote moderators without redeploying the app. This is called **role-based access control**.

**Check:** you can remove another user's review (try the Ama test review), and that review disappears from the wall.

---

# Part 5: Look inside the running system

Understanding what happened is as important as making it work. Use the console, in the same region.

## Step 18: Read the logs (CloudWatch)

1. Open **CloudWatch**, then **Log groups**, then `/aws/lambda/community-wall-v2-api`.
2. Open the newest log stream. Find lines like `{"level": "info", "msg": "review_created", ...}`.

> **REASON:** The logs are written as JSON (one record per line) instead of free text. Structured logs can be searched, filtered, and counted automatically (for example "how many errors per hour"), which is what production teams rely on.

**Check:** you can find the creation, update, and delete events from your own testing.

## Step 19: See the data (DynamoDB)

1. Open **DynamoDB**, then **Tables**, then `community-wall-v2-data`, then **Explore table items**.
2. You will see two kinds of items:
   - Reviews, with `pk` starting `EVENT#` and a sort key `sk` like `1792234412000#a1b2c3d4`.
   - One `STATS` item holding `reviewCount` and `ratingSum`.

> **ARCHITECTURE:** DynamoDB finds items by key, not by searching. We design keys for the questions we will ask. All reviews share the partition key `EVENT#<event id>`. The sort key begins with a millisecond timestamp, so asking for "the newest 20" is a single cheap query with no scanning, and results come back already in order.

> **REASON:** The average rating is `ratingSum / reviewCount`. Keeping those two numbers in a separate item means the page does not have to download every review to compute an average. A DynamoDB **transaction** updates the review and the totals together, so they can never disagree even if two people post at the same instant.

**Check:** the `STATS` item matches the number of reviews you see.

## Step 20: See the users (Cognito)

1. Open **Amazon Cognito**, then **User pools**, then `community-wall-v2-users`.
2. Open **Users** to see the accounts you created and **Groups** to see `admin` and its members.

**Check:** your test accounts are listed and confirmed.

## Step 21: See the API rules (API Gateway)

1. Open **API Gateway**, then `community-wall-v2-api`, then **Routes**.
2. `GET /reviews` shows no authorizer. `POST /reviews`, `PUT /reviews/{id}`, and `DELETE /reviews/{id}` show the JWT authorizer.
3. Open **Authorization** to see the authorizer's issuer (your Cognito user pool) and audience (your app client).
4. Open **Stages**, then `$default`, and look at the throttling: reads allow a high rate, writes a lower one.

> **REASON:** Reading a public wall should be easy for everyone, so reads are open and generously limited. Writes are the abuse risk, so they require identity and a stricter rate limit.

**Check:** one route has no authorizer, three routes have the JWT authorizer.

## Step 22: Confirm the bucket is private

Try to open the S3 file directly in your browser (use your bucket name and region):

```
https://YOUR_BUCKET_NAME.s3.eu-west-1.amazonaws.com/index.html
```

You should get an **Access Denied** message, while the CloudFront address works.

> **ARCHITECTURE:** The bucket allows reading only for this one CloudFront distribution, through **origin access control**. Visitors can never bypass CloudFront to reach the bucket. That keeps all traffic going through one controlled, cacheable, HTTPS-only entrance. You can see the rule yourself in **S3**, your bucket, **Permissions**, **Bucket policy**.

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

> **REASON (sessionStorage):** Tokens live in `sessionStorage`, which is cleared when the tab closes. The page never writes tokens to `localStorage`, which persists indefinitely. Access tokens last 60 minutes, then the user signs in again.

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

> **REASON (IAM):** The function's role allows only `GetItem`, `PutItem`, `UpdateItem`, `DeleteItem`, and `Query`, and only on this one table. It cannot create tables, read other tables, or touch any other service apart from writing its own logs. You can read the policy in **IAM**, **Roles**, the role starting with `community-wall-v2-FunctionRole-`.

## 6.4 Social links are untrusted input

Anything a user types and other people later click is a security risk. Someone could try a malicious `javascript:` address or a link to a look-alike phishing site. This is how the app handles it:

1. The user types a username or pastes a profile link.
2. The backend accepts **only** LinkedIn, X (or Twitter), and GitHub. It checks the host name exactly, so `linkedin.com.evil.io` is rejected.
3. It validates the username against that site's rules.
4. It then **builds a new, clean `https` link itself** from the username. The text the user typed is never stored or shown as a link.
5. The page checks the link's host again before drawing the button, and opens it with `rel="noopener noreferrer nofollow ugc"` in a new tab.

> **REASON:** Never trust data from a browser, and never repeat it back as a link without checking it. Rebuilding the value from validated parts (a method called **canonicalization**) is stronger than trying to filter out bad strings.

## 6.5 CORS and throttling

**CORS** (Cross-Origin Resource Sharing) is a browser rule: a page from one address may only call another address if that address says it is allowed. Our API allows calls only from our own CloudFront address, with the methods and headers the app uses. You can see this in **API Gateway**, your API, **CORS**.

> **REASON:** Without CORS limits, any website a user visits could make that user's browser call your API. Locking it to your own site is a cheap, standard protection. (It does not stop direct request tools, which is why the token check exists as well.)

**Throttling** limits how many requests are allowed per second: 100 per second for reads, 10 per second for each write route.

> **ARCHITECTURE:** Limits protect your wallet and your database from accidents and abuse. Different limits for different routes reflect different risks: reads are cheap and expected in bulk, writes are costly and the common target of spam.

## 6.6 The frontend

- **Demo mode:** if the three configuration values are still placeholders, the page runs on in-memory data. This lets the same file be previewed, taught from, and deployed.
- **No `innerHTML`:** all user text is inserted with `textContent`, so a message such as `<script>` is shown as plain text and never runs. This prevents **cross-site scripting (XSS)**.
- **Accessibility:** buttons have labels, star ratings describe themselves, the wall announces updates, focus outlines are visible, and animation respects the "reduce motion" setting.
- **Refresh:** the wall refreshes every 15 seconds while visible and not being edited.

---

# Part 7: Change something and redeploy

There are two kinds of change, and they use different consoles.

## 7.1 Change the page (colors, text, follow links)

1. Edit `frontend/index.html` on your computer. Keep your three `CONFIG` values (Step 9).
2. Upload it to the bucket again (Step 10). S3 replaces the old file.
3. The distribution uses the **CachingDisabled** policy, so visitors see the new page straight away. If you ever switch to a caching policy, open **CloudFront**, your distribution, **Invalidations**, **Create invalidation**, enter `/*`, and create it.

## 7.2 Change the backend code (for example, the 200-character review limit)

The Lambda code lives inside `template.yaml`, under `ZipFile: |`. So you change it there and let CloudFormation update the function.

1. Open `template.yaml` in a text editor and find the line `ZipFile: |`. The code below it is indented by 10 spaces. Make your change **and keep the indentation**. YAML is strict about spaces.
2. Make the same change in `backend/index.py` so the two copies stay identical.
3. Open **CloudFormation**, select your stack, and choose **Update stack**, then **Make a direct update**.
4. Choose **Replace existing template**, **Upload a template file**, select your edited `template.yaml`, and choose **Next**.
5. Leave the parameters, choose **Next**, then **Next** again. Tick the IAM acknowledgement and choose **Submit**.
6. Wait for **UPDATE_COMPLETE**. Then test the change on the website.

> **REASON:** CloudFormation compares your template with what exists and changes only the differences. You can safely repeat an update as often as you like. This is called an **idempotent** deployment.

> **NOTE:** Do not edit the code in the Lambda console and stop there. It works for a quick experiment, but the next stack update overwrites it with the template's version. The template is the source of truth.

> **NOTE:** The template contains a copy of the Lambda code so you can deploy with no packaging step. For a larger project you would keep the code in separate files and package it (with AWS SAM or CDK).

**Challenge ideas:** add a "role" field (student, engineer, other); add a character counter; show only reviews from the last hour; add a CloudWatch alarm that emails you when Lambda has an error; deploy a second copy with a different stack name and event ID.

---

# Part 8: Running it as a live workshop (60 minutes)

| Time | Activity |
|---|---|
| 0 to 5 | Welcome, quick poll ("Have you deployed an app before?"), show the architecture diagram (section 1.3) |
| 5 to 10 | Setup check: budget alert, one region, IAM basics and MFA |
| 10 to 25 | **Create the stack** (Steps 7 and 8). While CloudFormation builds, explain Cognito, tokens, and least privilege using Part 1 and Part 6 |
| 25 to 35 | **Frontend:** copy the outputs, edit the three values, upload `index.html` to S3 (Steps 9 and 10) |
| 35 to 50 | **Go live:** share the site link. Everyone signs up and posts. Open CloudWatch Logs and DynamoDB to see their requests (Steps 18 and 19) |
| 50 to 55 | **Security and admin:** make yourself an admin and remove a review, show the API Gateway routes and the private bucket (Steps 17, 21, 22) |
| 55 to 60 | Cleanup, show the follow links, next steps, Q&A |

Interactivity tips:
- Build live yourself. Attendees follow along, or just use your pre-deployed link.
- Polls at the start and midpoint. A "type DONE in chat" checkpoint after each phase.
- Ask the moderator to watch the chat, flag blockers, and relay questions.
- Mini challenges: "find your request in the logs", "find your review in DynamoDB".

## Pre-session checklist

- [ ] Create the stack once yourself **as a backup** and keep its `SiteUrl` ready. Stack creation takes 5 to 8 minutes, so never start it for the first time during the session.
- [ ] Complete Steps 9 and 10 for the backup site and post a test review.
- [ ] Sign up with two different emails and confirm the verification emails arrive (check spam).
- [ ] Remember the default Cognito email limit (Step 12). If many people will sign up at once, set up Amazon SES first, or let most attendees read the wall while a few post.
- [ ] Add yourself to the `admin` group and test **Remove (admin)**.
- [ ] Open the three follow links in a private window. Confirm the Meetup group and LinkedIn page are public and the WhatsApp invite has not expired or hit its member limit.
- [ ] Share the repo link and a pre-work note in advance: create an AWS account, turn on MFA, set a budget alert.
- [ ] Clear test reviews before the session (remove them as admin, or delete the items in DynamoDB).
- [ ] Record the session and share the repo afterward.

---

# Part 9: Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Stack ends in **ROLLBACK_COMPLETE** | A resource failed to create, so CloudFormation undid everything | **CloudFormation**, your stack, **Events**, find the earliest **CREATE_FAILED** row and read its **Status reason**. Then select the stack, **Delete** it, and create it again (Step 7). A stack in this state cannot be updated or reused |
| Stack seems to be missing | You are looking in a different region | Check the region selector (Step 3) |
| **CREATE_FAILED** on the CloudFront distribution, with a message about verifying your account | New or restricted AWS accounts must be verified before using CloudFront | Contact AWS Support to verify the account, then recreate the stack |
| **CREATE_FAILED** on the user pool domain | The domain prefix is already taken in this region | Delete the failed stack and recreate it with a different `ProjectName` |
| **CREATE_FAILED** mentioning permissions or "not authorized" | Your IAM user cannot create one of the resource types | Use a user with administrator access for this workshop |
| Upload of the template is refused | The file is not the original `template.yaml`, or an editor changed its indentation | Re-extract the original from the zip and try again |
| The deployed page says "Demo mode" | The three placeholders were not replaced, or the old file is in the bucket | Redo Step 9, then upload again (Step 10) |
| `AccessDenied` XML on the site | The page is not uploaded yet, or it is not named `index.html` at the top of the bucket | Check the bucket (Step 10). If it is there, wait two minutes and refresh |
| Cognito shows `redirect_mismatch` | You opened the site at an address other than the CloudFront one, or without the final `/` | Open exactly the `SiteUrl` from the stack outputs |
| Sign-in returns and says "Sign-in failed" | The page lost its stored secret (new tab, private mode, or storage blocked) | Start again from the page in one tab |
| Sign-in page cannot be reached | The `cognitoDomain` value has a typo or a trailing slash | Compare it with the `CognitoDomainUrl` output (Step 9) |
| No verification email | Cognito's daily email limit, or it went to spam | See the NOTE in Step 12. You can also confirm a user manually in **Cognito**, **Users** |
| "Session expired" or 401 when posting | Token older than 60 minutes | Sign in again |
| 403 "You can only edit your own review" | You are not the owner | Expected behavior |
| No Remove button after becoming admin | Old token | Sign out and sign in again |
| Browser console shows a CORS error | Page opened from a different address, or the API address in the page is wrong | Use the `SiteUrl` address and compare `apiUrl` with the `ApiUrl` output |
| `{"message":"Internal Server Error"}` or the wall will not load | Lambda failed | Read the CloudWatch log group (Step 18) |
| Lambda test says `Runtime.HandlerNotFound` | The handler setting was changed | **Lambda**, **Code**, **Runtime settings**, set Handler to `index.handler` |
| Edited page still looks old | Browser cache, or the new file did not upload | Hard refresh (Ctrl+Shift+R) and check the upload time in S3 |
| Stack deletion fails | The bucket still has files in it | Empty the bucket (Part 11), then delete the stack again |

---

# Part 10: Before real users arrive (production checklist)

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
| Caching | Switch CloudFront from `CachingDisabled` to `CachingOptimized` and invalidate on each page update | Faster pages and lower cost at scale |

> **ARCHITECTURE:** Production readiness is not one feature. It is a set of layers: identity, rate limiting, monitoring, repeatable deployment, recovery, and privacy. Each layer reduces a different kind of risk.

---

# Part 11: Clean up

When you are finished, delete everything so nothing keeps costing money. Stay in the same region.

1. **Empty the bucket first.** Open **S3**, then **Buckets**, select the `community-wall-v2-sitebucket-...` bucket, and choose **Empty**. Type `permanently delete` to confirm, then choose **Empty**.
2. **Delete the stack.** Open **CloudFormation**, select `community-wall-v2`, choose **Delete**, and confirm.
3. Wait. CloudFront takes several minutes to remove. The status goes from **DELETE_IN_PROGRESS** and then the stack disappears from the list.
4. **Delete the budget** (optional). Open **AWS Budgets**, select the budget, and delete it, if you no longer want it.

> **REASON:** Because everything was created from one template, everything is removed together: the table, the user pool and its users, the function, its log group, the API, the distribution, and the bucket. Nothing is left behind to find and delete by hand. This is one of the biggest practical benefits of Infrastructure as Code.

> **NOTE:** CloudFormation cannot delete a bucket that still has files in it. If the stack deletion fails, empty the bucket (step 1) and delete the stack again.

**Check:** the stack no longer appears in **CloudFormation**. Change the status filter to **Deleted** to confirm it shows as **DELETE_COMPLETE**.

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
