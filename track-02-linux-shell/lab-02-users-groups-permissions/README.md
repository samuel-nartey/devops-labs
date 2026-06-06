# Lab 02 — Users Groups Permissions

# Linux File Permissions, Ownership & Special Permissions Lab

## Overview

This lab is designed to test your understanding of:

* Linux file permissions
* Ownership and groups
* `chmod`
* `chown`
* `chgrp`
* `umask`
* Special permissions (SUID, SGID, Sticky Bit)
* `chattr +i`
* `chattr +a`

> **Important:** Do not skip the prediction section. The goal of this lab is to think like a Linux administrator, not simply execute commands.

For every task, follow this process:

1. **Predict**
2. **Execute**
3. **Observe**
4. **Explain**

---

# Task 1: File Permissions and Ownership

## Objective

Understand the relationship between permissions, ownership, and groups.

---

## Before Running (Prediction)

Answer the following before running any commands:

1. What permissions do you think a newly created file will have?
2. What permissions do you think a newly created directory will have?
3. Why do you think they are different?
4. What do you think will change when using `chmod`?
5. What do you think will change when using `chown`?
6. What do you think will change when using `chgrp`?

---

## Commands to Execute

```bash
mkdir linux_lab
cd linux_lab

touch project.txt
mkdir reports

ls -ld project.txt reports

chmod 764 project.txt

ls -l project.txt

sudo chown <username> project.txt

sudo chgrp <groupname> project.txt

ls -l project.txt
```

---

## Observation

Record:

1. Default permissions of the file.
2. Default permissions of the directory.
3. Permissions after applying `chmod`.
4. Ownership before and after `chown`.
5. Group ownership before and after `chgrp`.

---

## Explanation

Answer the following:

1. What is the difference between permissions and ownership?
2. What is the difference between `chmod`, `chown`, and `chgrp`?
3. Why might a system administrator change ownership without changing permissions?

---

# Task 2: Understanding Umask

## Objective

Understand how Linux determines default permissions.

---

## Before Running (Prediction)

1. What is the purpose of `umask`?
2. If the umask is `0022`, what permissions do you think a new file will receive?
3. If the umask is `0022`, what permissions do you think a new directory will receive?
4. How do you think changing the umask affects newly created files?

---

## Commands to Execute

```bash
umask

touch finance.txt
mkdir finance_dir

ls -ld finance.txt finance_dir

umask 0077

touch secret.txt
mkdir secret_dir

ls -ld secret.txt secret_dir
```

---

## Observation

Record:

1. Current umask value.
2. Permissions of `finance.txt`.
3. Permissions of `finance_dir`.
4. Permissions of `secret.txt`.
5. Permissions of `secret_dir`.

---

## Explanation

1. How did the umask influence the permissions?
2. Why were the permissions of the second set of files different?
3. Why might an organization choose a restrictive umask such as `0077`?

---

# Task 3: Special Permissions (SUID, SGID & Sticky Bit)

## Objective

Understand Linux special permissions and their practical use cases.

---

## Before Running (Prediction)

1. What do you think SUID does?
2. What do you think SGID does?
3. What do you think the Sticky Bit does?
4. Where do you think the letters `s` and `t` will appear when viewing permissions?
5. Which special permission do you think is most useful in a shared environment?

---

## Commands to Execute

```bash
touch suid_file

mkdir sgid_dir
mkdir shared_dir

chmod 4755 suid_file
chmod 2775 sgid_dir
chmod 1777 shared_dir

ls -ld suid_file sgid_dir shared_dir
```

---

## Observation

Record:

1. Permission string for `suid_file`.
2. Permission string for `sgid_dir`.
3. Permission string for `shared_dir`.
4. Location of the `s` character.
5. Location of the `t` character.

---

## Explanation

1. Explain SUID.
2. Explain SGID.
3. Explain Sticky Bit.
4. Why is the `/tmp` directory usually configured with a Sticky Bit?
5. Provide one real-world use case for each special permission.

---

# Task 4: Protecting Critical Files with chattr +i

## Objective

Understand immutable files and their security benefits.

---

## Before Running (Prediction)

1. What do you think the immutable (`+i`) attribute does?
2. After applying it, do you think you will be able to:

   * Modify the file?
   * Rename the file?
   * Delete the file?
3. Why might a Linux administrator use this attribute?

---

## Commands to Execute

```bash
touch critical.conf

sudo chattr +i critical.conf

lsattr critical.conf

echo "test" >> critical.conf

mv critical.conf backup.conf

rm critical.conf
```

Remove the immutable attribute:

```bash
sudo chattr -i critical.conf

echo "test" >> critical.conf

rm critical.conf
```

---

## Observation

Record:

1. Output of `lsattr`.
2. Which commands succeeded.
3. Which commands failed.
4. What changed after removing the immutable attribute.

---

## Explanation

1. What does `chattr +i` do?
2. Why is it useful for protecting critical files?
3. What risks could arise if administrators forget a file has been made immutable?

---

# Task 5: Audit Log Protection with chattr +a

## Objective

Understand append-only files and their role in auditing and security.

---

## Before Running (Prediction)

1. What do you think the append-only (`+a`) attribute does?
2. Will you be able to:

   * Add data to the file?
   * Overwrite existing data?
   * Delete the file?
3. How do you think this differs from `+i`?

---

## Commands to Execute

```bash
touch audit.log

sudo chattr +a audit.log

lsattr audit.log

echo "User Login Successful" >> audit.log

echo "Overwrite Test" > audit.log

rm audit.log
```

---

## Observation

Record:

1. Output of `lsattr`.
2. Which commands succeeded.
3. Which commands failed.
4. Whether your predictions were correct.

---

## Explanation

1. What does `chattr +a` do?
2. Why can data be appended but not overwritten?
3. Why can the file not be deleted?
4. Why is append-only commonly used for audit logs?
5. Compare `chattr +a` and `chattr +i`.

---

# Final Reflection

Answer the following in complete sentences:

1. What is the difference between permissions and ownership?
2. What is the difference between `chmod`, `chown`, and `chgrp`?
3. How does `umask` affect file creation?
4. What problem does SUID solve?
5. What problem does SGID solve?
6. Why is the Sticky Bit important?
7. Compare `chattr +i` and `chattr +a`.
8. Which concept from this lab would be most useful in a production Linux environment and why?

---

## Submission Requirements

Submit the following:

* Commands used
* Screenshots of outputs
* Observations
* Explanations
* Final reflection answers

> Remember: A Linux administrator's value is not measured by the commands they memorize, but by their ability to predict, investigate, and explain system behavior.

