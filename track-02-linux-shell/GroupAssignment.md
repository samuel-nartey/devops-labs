Welcome to ***doing hard things***.

# Linux User & Group Management — Commands + Challenges

## 1. Group Work Instructions

Before you touch a single command, assign these roles within your group:

1. **The Reader** — one person reads the current question/task out loud to the group, or asks another group member to read it. **This role rotates with every new question** — so if Member A reads Challenge 2, Member B reads Challenge 3, Member C reads Challenge 4, and so on. Everyone gets a turn at this.

2. **The Explainer** — after the question has been read, someone explains what needs to be done and why, or the group nudges a specific person to attempt the explanation before anyone else jumps in. The Explainer should share their ideas on the question with the group and actively guide the person sharing their screen — telling them what to type next and why, rather than just watching silently. **This role is picked at random, not in a fixed order** — don't let the same one or two confident people always explain. Mix it up deliberately; call on someone different each time, including whoever looks least sure.

3. **The Screen-Sharer / Documenter** — one person shares their screen as the commands are run, takes a screenshot at each key step, and labels every screenshot descriptively (e.g. `01-groupadd-deployteam.png`, `02-sgid-permissions-set.png`, `03-devops1-file-inherits-group.png`) rather than leaving them as generic, unlabeled screenshots. This makes it far easier to build the article afterward and for anyone reviewing to follow what happened and in what order.

**Why this matters:** this isn't about how easy or difficult any single challenge is. It's about sharing ideas, interacting with your teammates, and learning out loud — explaining something to someone else (or being the one who has to explain) is one of the fastest ways to actually learn it, not just complete it. Even if you already know the answer, let someone else take a shot at explaining first. The goal is confidence and shared understanding, not just a finished terminal screen.

Once roles are assigned and the question has been read and explained, you can refer to the command reference and challenge steps below if you still need help.

---

## 2. Command Reference

### User Management
| Command | Purpose |
|---|---|
| `useradd -m -s /bin/bash <user>` | Create a user with a home directory and bash shell |
| `userdel -r <user>` | Delete a user and their home directory |
| `usermod -aG <group> <user>` | Add a user to a supplementary group |
| `usermod -L <user>` / `usermod -U <user>` | Lock / unlock a user account |
| `usermod -s /usr/sbin/nologin <user>` | Disable shell login for a user |
| `passwd <user>` | Set or change a user's password |
| `chage -l <user>` | List password aging info for a user |
| `chage -M 90 <user>` | Force password expiry every 90 days |
| `id <user>` | Show UID, GID, and group memberships |
| `whoami` / `who` / `w` | Show current user / logged-in users |
| `su - <user>` | Switch to another user (with their environment) |
| `sudo -l -U <user>` | List sudo privileges for a user |

### Group Management
| Command | Purpose |
|---|---|
| `groupadd <group>` | Create a new group |
| `groupdel <group>` | Delete a group |
| `groupmod -n <newname> <oldname>` | Rename a group |
| `gpasswd -a <user> <group>` | Add a user to a group (alternative to usermod) |
| `gpasswd -d <user> <group>` | Remove a user from a group |
| `groups <user>` | List all groups a user belongs to |
| `getent group <group>` | Show group details from the database |
| `getent passwd <user>` | Show user details from the database |

### Key Files
| File | Purpose |
|---|---|
| `/etc/passwd` | User account info (username, UID, GID, home, shell) |
| `/etc/shadow` | Encrypted passwords and aging rules |
| `/etc/group` | Group names, GIDs, and members |
| `/etc/gshadow` | Group password info |
| `/etc/sudoers` | Sudo access rules (edit only via `visudo`) |
| `/etc/login.defs` | Default settings for new users (UID range, password rules) |

### Permissions Relevant to Users/Groups
| Command | Purpose |
|---|---|
| `chown <user>:<group> <file>` | Change file owner and group |
| `chgrp <group> <file>` | Change only the group owner |
| `chmod g+rwx <file>` | Grant group read/write/execute |
| `chmod 2770 <dir>` | Set SGID so new files inherit the directory's group |

---

## 3. Challenges

### Challenge 1 — Create Users and a Shared Group (Beginner)
Create two users, `devops1` and `devops2`, each with a home directory and bash shell. Create a group called `deployteam` and add both users to it. Verify membership without opening `/etc/group` directly — use a command instead.

**Goal:** practice `useradd`, `groupadd`, `usermod -aG`, and `groups`.

---

### Challenge 2 — Shared Project Directory with SGID (Beginner–Intermediate)
Create a directory `/srv/projects/cicd` owned by `root:deployteam`. Configure it so:
- Members of `deployteam` can read/write/execute inside it.
- Any new file or subdirectory created inside automatically inherits the `deployteam` group (without users having to `chgrp` manually).

Test it by switching to `devops1`, creating a file inside the directory, and confirming its group ownership.

**Goal:** practice `chown`, `chmod 2770` (SGID), and `su -`.

**Steps:**
```bash
sudo mkdir -p /srv/projects/cicd
sudo chown root:deployteam /srv/projects/cicd
sudo chmod 2770 /srv/projects/cicd
ls -ld /srv/projects/cicd
su - devops1
cd /srv/projects/cicd
touch pipeline.yaml
ls -l pipeline.yaml
exit
```

**What's happening:**
- `chown root:deployteam` makes `deployteam` the group owner, so the permission bits you set next actually apply to your team, not just to `root`.
- `chmod 2770` sets three things at once: `7` for the owner, `7` for the group (read/write/execute), `0` for everyone else, and the leading `2` turns on the **SGID bit** on the directory.
- The SGID bit is the real trick here — normally a new file takes the *primary group of whoever creates it*. With SGID set on the parent directory, every new file or folder created inside instead inherits the **directory's** group (`deployteam`). That's why `devops1`, whose primary group might be something else entirely, still produces a file owned by `deployteam`.
- `ls -ld` lets you actually see the SGID bit — look for an `s` in the group execute position (`rwxrws---`) instead of the usual `x`.

**Curiosity gap:** What do you think happens if you create a *subdirectory* inside `/srv/projects/cicd` instead of a file, then create a file inside *that* subdirectory? Does the inheritance still hold two levels deep? Test it and see — this is exactly the behavior that makes SGID so popular for shared team directories in real production environments.

---

### Challenge 3 — Restricted Service Account (Intermediate)
Create a system account called `svc-monitor` that:
- Has no interactive shell (cannot SSH or log in directly).
- Has a home directory at `/opt/svc-monitor`.
- Belongs to a new group `monitoring` as its primary group.

Confirm that attempting to `su - svc-monitor` fails appropriately, and explain (in a comment or short note) why this setup is safer than giving it a normal login shell.

**Goal:** practice `useradd -r -s /usr/sbin/nologin -d ... -g ...`, and reasoning about least-privilege service accounts.

**Steps:**
```bash
sudo groupadd monitoring
sudo useradd -r -m -d /opt/svc-monitor -s /usr/sbin/nologin -g monitoring svc-monitor
id svc-monitor
su - svc-monitor
```

**What's happening:**
- `groupadd monitoring` creates the dedicated primary group first, since `useradd -g` needs an existing group to attach to.
- `useradd -r` marks this as a **system account** — it pulls a UID from the system range (usually below 1000) instead of the normal human-user range, which is how monitoring tools, dashboards, and admins immediately recognize it as non-human.
- `-d /opt/svc-monitor` gives it a home directory outside the usual `/home` tree, which is conventional for service accounts that don't belong to a person.
- `-s /usr/sbin/nologin` is the actual security control: it sets the account's shell to a binary whose only job is to print a message and exit. The account technically exists and can own processes, but nobody — not even someone with the password — can get an interactive shell through it.
- When you run `su - svc-monitor`, the system tries to start the login shell defined for that user, finds `nologin`, and refuses, printing something like "This account is currently not available."
- **Why this matters in production:** if an attacker ever compromises a process running as `svc-monitor` (say, a monitoring agent with a vulnerability), `nologin` means they still can't pivot into an interactive shell on that account. It's a small change that meaningfully shrinks your attack surface — this is the same reasoning behind why services like `nginx`, `postgres`, and most daemons run as `nologin` accounts on a properly hardened server.

**Curiosity gap:** Try running a command *as* `svc-monitor` without an interactive shell — for example `sudo -u svc-monitor whoami`. Does that work even though `su -` fails? Think about why `sudo -u` and `su -` behave differently here, and what that difference means for how cron jobs and systemd services are able to run safely under restricted accounts.

---

### Challenge 4 — Password Policy and Account Lockout (Intermediate–Advanced)
For user `devops2`:
- Set a password expiry policy so the password must be changed every 60 days, with a 7-day warning before expiry.
- Lock the account temporarily, confirm the lock using `passwd -S devops2`, then unlock it.
- Use `chage -l` to display and interpret the full aging report.

**Goal:** practice `chage`, `usermod -L/-U`, and `passwd -S`, and understand how password aging fields map to real policy.

**First, a general explanation of how Linux passwords actually work** (we haven't covered this fully yet, so it's worth slowing down here before you touch a single command):

Every user's encrypted password and its aging rules live in `/etc/shadow`, one line per user, with fields separated by colons. A simplified line looks like:

```
devops2:$6$randomsalt$hashvalue:19800:0:60:7:::
```

Reading that left to right:
- **Field 1 — username**
- **Field 2 — the encrypted password hash.** This is never the plaintext password; it's a one-way hash (commonly SHA-512, shown by the `$6$` prefix) combined with a random "salt" so two users with the same password don't produce the same hash. Linux never decrypts this — when you type a password to log in, it hashes *what you typed* with the same salt and checks if the result matches.
- **Field 3 — last password change**, stored as the number of days since January 1, 1970 ("epoch").
- **Field 4 — minimum days** before the password can be changed again.
- **Field 5 — maximum days** the password is valid before it must be changed (this is your "expire every 60 days" rule).
- **Field 6 — warning period**, in days, before expiry (your "7-day warning").
- **Field 7 — inactivity period** after expiry before the account is disabled entirely.
- **Field 8 — account expiration date** (epoch days), separate from password expiration.
- **Field 9** — reserved, unused.

`chage` is simply a friendly command-line wrapper that reads and writes these fields for you, so you never have to hand-edit `/etc/shadow` (which, like `/etc/sudoers`, can break login for everyone if you get the format wrong).

**Steps:**
```bash
sudo chage -M 60 -W 7 devops2
sudo chage -l devops2
sudo usermod -L devops2
sudo passwd -S devops2
sudo usermod -U devops2
sudo passwd -S devops2
```

**What's happening:**
- `chage -M 60 -W 7 devops2` sets field 5 (max days = 60) and field 6 (warning days = 7) directly. From the next login after this, the system starts counting down and will nag the user 7 days before their password dies.
- `chage -l devops2` prints all of this back out in human-readable form — last change date, expiry date, inactivity date, and account expiry date — so you can confirm your policy actually landed correctly instead of trusting the command silently.
- `usermod -L devops2` "locks" the account, but not in the way most learners expect. It doesn't disable the account or touch the aging fields at all — it prepends a `!` to the front of the encrypted password hash in field 2. Since `!hashvalue` can never match any real password hash during the login check, password authentication is effectively impossible, while everything else about the account stays untouched.
- `passwd -S devops2` reports the account's status in a compact form (e.g. `devops2 L 06/20/2026 0 60 7 -1`) — the `L` is what confirms the lock took effect, versus `P` for a usable password or `NP` for no password set at all.
- `usermod -U devops2` reverses the lock by stripping that leading `!` back off, restoring the original hash exactly as it was.

**Curiosity gap:** Since `usermod -L` only touches the password hash field and nothing else, think about it before you test: if `devops2` had SSH key-based login set up instead of a password, would locking the account with `usermod -L` actually stop them from logging in over SSH? Try it (or reason it through) and you'll understand exactly why production systems often combine `usermod -L` with `usermod -s /usr/sbin/nologin` for a truly locked-out account.

---

### Challenge 5 — Audit and Fix a Misconfigured Sudoers Setup (Advanced)
You inherit a server where:
- `devops1` was accidentally granted full `ALL=(ALL) NOPASSWD: ALL` sudo access in `/etc/sudoers`.
- The `deployteam` group should instead only be allowed to run `systemctl restart`, `systemctl status`, and `journalctl` commands (no password-less full root).

Tasks:
1. Safely edit the sudoers configuration using `visudo` (never edit `/etc/sudoers` directly).
2. Remove `devops1`'s blanket access.
3. Create a sudoers rule (ideally as a file under `/etc/sudoers.d/`) that grants `%deployteam` permission to run only the three specified commands, with a clear command alias.
4. Test as `devops1` that restricted commands work but something outside the list (e.g. `sudo reboot`) is denied.

**Goal:** practice `visudo`, command aliases, `%group` syntax in sudoers, and the principle of least privilege in access control.

**Steps:**
```bash
sudo visudo
# inside the editor, find and delete the line:
# devops1 ALL=(ALL) NOPASSWD: ALL
# save and exit

sudo visudo -f /etc/sudoers.d/deployteam
# inside the editor, type:
# Cmnd_Alias DEPLOY_CMDS = /bin/systemctl restart *, /bin/systemctl status *, /usr/bin/journalctl
# %deployteam ALL=(ALL) DEPLOY_CMDS
# save and exit

sudo chmod 440 /etc/sudoers.d/deployteam
sudo -l -U devops1

su - devops1
sudo systemctl status nginx
sudo systemctl restart nginx
sudo reboot
exit
```

**What's happening:**
- `sudo visudo` opens `/etc/sudoers` through a wrapper that locks the file, opens it in a text editor, and — critically — **parses and validates the syntax before saving**. If you make a typo, `visudo` refuses to write the broken version and asks you to fix it or abort, which is exactly what protects you from locking everyone out of `sudo` on the box.
- Removing `devops1`'s `NOPASSWD: ALL` line takes away the blanket, password-less root access that should never have been granted in the first place.
- `visudo -f /etc/sudoers.d/deployteam` creates and validates a *separate* file rather than editing the main `/etc/sudoers` directly. Files in `/etc/sudoers.d/` are automatically included by default (via an `#includedir` line in the main file), so this keeps your custom rule isolated, easy to review, and easy to remove later without touching the core file.
- `Cmnd_Alias DEPLOY_CMDS = ...` defines a named group of exact commands (with full paths, which sudoers requires) so the actual permission line stays short and readable instead of repeating long paths.
- `%deployteam ALL=(ALL) DEPLOY_CMDS` is the permission grant itself: the leading `%` means "this is a group, not a user," and it limits every member of `deployteam` to running only the commands inside `DEPLOY_CMDS` — nothing else, and notably *with* a password prompt since we didn't add `NOPASSWD`.
- `chmod 440` matches the permissions sudoers expects on files in that directory (owner and group read-only, no write, no execute) — sudo will actually ignore files with looser permissions as a safety measure.
- `sudo -l -U devops1` lets you audit exactly what `devops1` is allowed to run *before* they even log in, which is the fastest way to confirm your fix worked.
- When `devops1` runs `sudo systemctl restart nginx`, it matches the wildcard pattern in `DEPLOY_CMDS` and succeeds (after a password prompt). When they try `sudo reboot`, sudo checks it against every rule that applies to `devops1` and finds no match, so it's denied with a message like "sorry, user devops1 is not allowed to execute '/usr/sbin/reboot'."

**Curiosity gap:** Notice the path-based syntax (`/bin/systemctl restart *`) — sudoers matches the *exact path and argument pattern*, not just the command name. Try testing what happens if `devops1` runs `sudo /usr/bin/systemctl restart nginx` using a slightly different path than the one in your alias, or tries `sudo systemctl restart nginx; sudo reboot` chained together. Does your rule hold up? This is exactly the kind of gap real attackers look for when sudoers rules are written carelessly — work through it and you'll understand why command aliases need to be written precisely.

---

### Bonus Tip
For all challenges, validate your work with:
```bash
getent passwd <user>
getent group <group>
sudo -l -U <user>
```
This is the fastest way to confirm what actually took effect versus what you intended.

---

## 4. Submission Requirements

**Deadline: Friday, June 26, 2026, 12:00 PM**

**How many to complete:** You may attempt all 5 challenges, but you must complete **at least 3 of the 5** (any combination from Part 2) to satisfy this assignment.

**What to submit:**
1. Write a full article on your assignment — Medium, Dev.to, Hashnode, or your platform of choice.
2. The article must include:
   - The steps you took, in order.
   - Screenshots of your terminal output at each key stage (command run + result).
   - A step-by-step guide detailed enough that a complete beginner could follow it and replicate your work exactly.
   - Your own explanation of *why* each step works, not just *what* you typed — this is what actually convinces a recruiter that you understand the work, not just that you copied commands.
3. Post the article (or a summary with a link to it) on LinkedIn.
4. End your article and your LinkedIn post with this exact closing line:

   > *This assignment is part of the DevSecOps training by @ParoCyber and Facilitated by @Samuel Nartey.*

**Important note on AI-generated content:** Do not copy AI-generated explanations and paste them directly into your article. Run the commands yourself, understand the output, and write the explanation in your own words. Submissions that read as directly copied from AI tools risk being flagged, and repeated violations may result in account restriction. The goal is for your article to demonstrate that *you* did the work and *you* understand it.
