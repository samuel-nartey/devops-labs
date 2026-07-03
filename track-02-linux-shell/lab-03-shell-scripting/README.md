# Lab 03 — Shell Scripting

# Bash Scripting: A 10-Level Hands-On Guide (For People Who Already Know `cd` and `ls`)

> **How this guide works**
> Every level follows the same rhythm:
> 1. **Lesson** — a short explanation of one concept.
> 2. **Run This** — a command to type yourself. Before you run it, you're asked to **predict** what will happen. This is the most important part — predicting, then checking, is how the concept actually sticks.
> 3. **What Just Happened** — the explanation, tied directly to the output you saw.
> 4. **Practice** — 4-6 exercises. Try each one yourself *before* opening the hidden answer.
> 5. **Mini-Project** — a small script that uses everything from that level.
>
> Answers are hidden behind `<details>` blocks like this one:
>
> <details>
> <summary>Click to reveal</summary>
>
> This is where the answer lives. Don't peek until you've actually tried it.
> </details>
>
> **Setup:** Open a terminal on Ubuntu/Debian (or any Linux box with `bash`). Make a folder to work in so you don't clutter your home directory:
> ```bash
> mkdir ~/bash-course && cd ~/bash-course
> ```
> Do this once now. Every level assumes you're inside `~/bash-course`.

---

## Level 1 — Your First Script

### Lesson
A shell script is just a text file full of the same commands you already type at the prompt, saved so you can run them all at once. Two things make a file a "runnable script":
1. A **shebang** line at the very top: `#!/bin/bash`. It tells the operating system *which program* should interpret the rest of the file.
2. **Execute permission**, which you grant with `chmod +x filename`.

### Run This
First, predict: what do you think will happen if you try to run a plain text file as a program, *before* you've done anything special to it?

```bash
echo 'echo "Hello, Bash!"' > hello.sh
./hello.sh
```

<details>
<summary>What did you see?</summary>

You almost certainly got something like:
```
bash: ./hello.sh: Permission denied
```
</details>

Now fix it:

```bash
chmod +x hello.sh
./hello.sh
```

### What Just Happened
- `echo 'echo "Hello, Bash!"' > hello.sh` wrote one line of text into a new file called `hello.sh`. The `>` **redirects** the output of `echo` into a file instead of the screen.
- The first attempt to run it failed because the file had no execute permission — Linux refuses to run files that aren't marked executable, even if they contain valid commands.
- `chmod +x hello.sh` added the executable bit. `./` tells bash "look for this program in the current directory" (without it, bash searches your `$PATH`, and your current folder usually isn't in it).
- Notice: we never added a shebang, and it still worked! That's because when you run `./hello.sh`, and the file has no shebang, bash (the shell you're typing in) just executes it with itself. This is fragile — if someone runs your script with `sh hello.sh` or from a different shell, behavior can change. **Always add a shebang.**

Let's fix that properly:
```bash
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, Bash!"
EOF
chmod +x hello.sh
./hello.sh
```

Predict first: what does `cat > hello.sh << 'EOF' ... EOF` do?

<details>
<summary>Explanation</summary>

This is a **heredoc**. Everything between `<< 'EOF'` and the closing `EOF` is fed as input to `cat`, which (because of the `>`) writes it straight into `hello.sh`, replacing the old contents. It's a clean way to write multi-line files from the terminal without opening an editor. The quotes around `'EOF'` stop bash from doing variable substitution inside the block — a detail that will matter a lot once we cover variables in Level 2.
</details>

### Practice
1. Create `bye.sh` that prints `Goodbye!` and make it executable, then run it two different ways: `./bye.sh` and `bash bye.sh`.
   <details><summary>Answer</summary>

   ```bash
   printf '#!/bin/bash\necho "Goodbye!"\n' > bye.sh
   chmod +x bye.sh
   ./bye.sh
   bash bye.sh
   ```
   Both print `Goodbye!`. `bash bye.sh` explicitly tells bash to interpret the file, so it works *even without execute permission or a shebang* — worth knowing for debugging other people's scripts.
   </details>

2. Predict, then check: what happens if you run `sh hello.sh` instead of `./hello.sh`? (`sh` is a more limited shell than `bash`.)
   <details><summary>Answer</summary>

   For this simple script it still prints `Hello, Bash!`, because `echo` works the same in both. The shebang (`#!/bin/bash`) is what *matters* when scripts get more complex — arrays, `[[ ]]`, and other bash-only features will silently break or error under `sh`. Running `sh script.sh` ignores the shebang entirely and forces `sh` regardless of what's written at the top.
   </details>

3. Use `which bash` and `type echo`. What's the difference between the two outputs, and why?
   <details><summary>Answer</summary>

   `which bash` shows the file path of the bash program (e.g. `/usr/bin/bash`) — it's a real executable file. `type echo` shows `echo is a shell builtin` — `echo` isn't a separate program on disk at all; it's built directly into bash itself. This matters later when you wonder why some commands behave slightly differently than their `/usr/bin/` counterparts.
   </details>

4. Remove the shebang line from `hello.sh` (edit it with `nano hello.sh` or `sed -i '1d' hello.sh`), then run `./hello.sh` again. Did it still work? Now try `./hello.sh` after also removing execute permission with `chmod -x hello.sh`. Predict before you run.
   <details><summary>Answer</summary>

   Without the shebang, `./hello.sh` still runs (your interactive shell is bash, so it defaults to bash). Without execute permission, you get `Permission denied` again — permission is checked before content.
   </details>

5. Create a script `whoami-check.sh` containing just `whoami` (no shebang, no `echo`) and run it. What does it print, and what real-world command have you just re-invented in miniature?
   <details><summary>Answer</summary>

   It prints your current username — a script is nothing more than a sequence of ordinary commands, so a "script" containing a single existing command just runs that command.
   </details>

### Mini-Project: `greet.sh`
Write a script that:
- Has a proper shebang
- Prints `Starting greeting script...`
- Prints `Hello, Bash learner!`
- Prints `Done.`

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
echo "Starting greeting script..."
echo "Hello, Bash learner!"
echo "Done."
```
Save, `chmod +x greet.sh`, run with `./greet.sh`.
</details>

---

## Level 2 — Variables

### Lesson
Variables store data. In bash: `name=value` — **no spaces around the `=`**. You read a variable's value with `$name` or `${name}`.

### Run This
Predict what each line prints before running:
```bash
name=Alice
echo name
echo $name
echo "$name"
echo '$name'
```

<details>
<summary>What did you see?</summary>

```
name
Alice
Alice
$name
```
</details>

### What Just Happened
- `echo name` printed the literal word `name` — without a `$`, bash treats it as plain text, not a variable reference.
- `echo $name` and `echo "$name"` both printed `Alice` — the `$` triggers **expansion** (substituting the variable's value).
- `echo '$name'` printed `$name` literally — **single quotes disable all expansion**. **Double quotes allow expansion**. This distinction will save you from bugs constantly, so lock it in now: `'…'` = literal, `"…"` = expand.
- `name=Alice` with **no spaces**: try `name = Alice` (with spaces) and you'll get `name: command not found` — bash thinks you're trying to *run a command* called `name` with arguments `=` and `Alice`.

### Command Substitution
Predict, then run:
```bash
today=$(date +%A)
echo "Today is $today"
```

<details>
<summary>Explanation</summary>

`$(command)` runs `command` and substitutes its **output** into the variable. This is called command substitution — it's how you capture the result of any command into a variable for later use.
</details>

### Practice
1. Predict and check: what happens if you type `name = Alice` (with spaces on both sides of `=`)?
   <details><summary>Answer</summary>

   `name: command not found` — bash parses `name` as a command to execute, and `=` and `Alice` as its arguments. Assignment syntax requires **no whitespace** around `=`.
   </details>

2. Create a variable `count` set to `5`, then print: `"You have 5 items."` using the variable, not the literal number.
   <details><summary>Answer</summary>

   ```bash
   count=5
   echo "You have $count items."
   ```
   </details>

3. Predict: what does `echo "$count items cost \$$count"` print (assuming `count=5`)? Why does one `$` show up literally and the other expands?
   <details><summary>Answer</summary>

   Output: `5 items cost $5`. The backslash `\$` **escapes** the dollar sign, telling bash "treat this as a literal character, not the start of a variable reference." The unescaped `$count` still expands normally.
   </details>

4. Store the output of `pwd` in a variable called `here`, then use it in a sentence: `"I am currently in <path>"`.
   <details><summary>Answer</summary>

   ```bash
   here=$(pwd)
   echo "I am currently in $here"
   ```
   </details>

5. Run `readonly locked=100` then try `locked=200`. Predict the result first.
   <details><summary>Answer</summary>

   ```
   bash: locked: readonly variable
   ```
   `readonly` locks a variable so it can't be reassigned — useful for constants you want to protect from accidental changes later in a script.
   </details>

6. What's the difference between `${name}` and `$name`? Test it by running:
   ```bash
   file=report
   echo "$filename.txt"
   echo "${file}name.txt"
   ```
   <details><summary>Answer</summary>

   `echo "$filename.txt"` prints just `.txt` (nothing else) — bash tried to expand a variable called `filename` (not `file`), which doesn't exist, so it expands to empty text. `${file}name.txt` correctly expands `file` and prints `reportname.txt`. **The braces `{}` explicitly mark where the variable name ends**, which matters whenever a variable is immediately followed by more text with no separator.
   </details>

### Mini-Project: `sysinfo.sh`
Write a script that stores your username (`whoami`), the current date, and the current directory in three variables, then prints a one-paragraph summary using all three.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
user=$(whoami)
now=$(date)
dir=$(pwd)
echo "User $user is working in $dir on $now."
```
</details>

---

## Level 3 — User Input and Script Arguments

### Lesson
Scripts can take input two ways:
- **Interactively**, using `read`, which pauses and waits for the user to type something.
- **As arguments**, passed on the command line when the script is launched (`./script.sh arg1 arg2`), accessible inside the script as `$1`, `$2`, etc.

### Run This
```bash
cat > ask.sh << 'EOF'
#!/bin/bash
echo "What's your name?"
read username
echo "Nice to meet you, $username!"
EOF
chmod +x ask.sh
./ask.sh
```
Predict what happens when it runs, then actually type a name when prompted.

### What Just Happened
`read username` pauses execution and waits for a line of keyboard input, storing whatever you type into the variable `username`. Nothing fancy — it's just another assignment, sourced from stdin instead of `=`.

### Run This — Arguments
```bash
cat > args.sh << 'EOF'
#!/bin/bash
echo "Script name: $0"
echo "First arg: $1"
echo "Second arg: $2"
echo "All args: $@"
echo "Number of args: $#"
EOF
chmod +x args.sh
```
**Predict**: what will `./args.sh hello world` print for each line? Write down your guess, then run it.

<details>
<summary>What did you see?</summary>

```
Script name: ./args.sh
First arg: hello
Second arg: world
All args: hello world
Number of args: 2
```
</details>

### What Just Happened
- `$0` is the script's own name/path (not "argument zero" of your data — it's special).
- `$1`, `$2`, … are **positional parameters** — one per argument, in order.
- `$@` expands to all arguments.
- `$#` is a count of how many arguments were given.
- If you'd run `./args.sh hello` (one argument), `$2` would simply be empty — bash doesn't error on missing positional parameters, it just gives you nothing.

### Practice
1. Predict, then test: run `./args.sh` with **no arguments at all**. What prints for `$1` and `$#`?
   <details><summary>Answer</summary>

   `$1` is empty (blank line), `$#` is `0`. Bash never errors for "missing" positional args; they're just empty strings.
   </details>

2. Modify `ask.sh` to also ask for the user's age with a second `read`, then print both in one sentence.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   echo "What's your name?"
   read username
   echo "How old are you?"
   read age
   echo "$username is $age years old."
   ```
   </details>

3. Predict the difference between `$@` and `$*` when quoted: `"$@"` vs `"$*"`. (Hint: this only shows up with multiple multi-word arguments — try `./test.sh "first one" "second one"` where the script loops and prints each argument on its own line — we'll cover loops properly in Level 5, so for now just run `printf '%s\n' "$@"` vs `printf '%s\n' "$*"` inside a script.)
   <details><summary>Answer</summary>

   `"$@"` preserves each argument as a **separate** item (so `"first one"` and `"second one"` stay as two distinct strings). `"$*"` joins **all** arguments into a **single** string separated by spaces. This distinction becomes important once you loop over arguments — using `"$@"` is almost always what you want.
   </details>

4. Write `greet-arg.sh` that greets a name passed as an argument, but if no argument is given, defaults to `"stranger"`. (Hint: research the `${var:-default}` syntax.)
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   name=${1:-stranger}
   echo "Hello, $name!"
   ```
   `${1:-stranger}` means "use `$1` if it's set and non-empty, otherwise use `stranger`."
   </details>

5. Use `read -p "Prompt text: " variable` (a one-liner version of the two-step `echo` + `read`). Rewrite `ask.sh` using it.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   read -p "What's your name? " username
   echo "Nice to meet you, $username!"
   ```
   `-p` displays the prompt on the same line as the input, without needing a separate `echo`.
   </details>

### Mini-Project: `intro.sh`
Write a script that takes a name and a favorite programming language as two command-line arguments, and prints: `"<name> says their favorite language is <language>."` If either argument is missing, print a usage message like `"Usage: ./intro.sh <name> <language>"` and exit (we'll make exiting cleaner in Level 9 — for now just use plain `exit 1`).

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./intro.sh <name> <language>"
  exit 1
fi
echo "$1 says their favorite language is $2."
```
(Don't worry if `[ -z ... ]` looks unfamiliar — that's exactly what Level 4 covers next.)
</details>

---

## Level 4 — Conditionals

### Lesson
`if` statements let a script make decisions. The classic form:
```bash
if [ condition ]; then
  # runs if condition is true
elif [ other_condition ]; then
  # runs if that one is true
else
  # runs otherwise
fi
```
`[ condition ]` is actually a *command* called `test` (square brackets are just another way to invoke it) — that's why the spaces around `[` and `]` are mandatory.

### Run This
Predict the output first:
```bash
age=20
if [ "$age" -ge 18 ]; then
  echo "You are an adult."
else
  echo "You are a minor."
fi
```

<details>
<summary>What did you see?</summary>

```
You are an adult.
```
`-ge` means "greater than or equal to," used for **numeric** comparisons.
</details>

### What Just Happened
Common test operators:
| Numeric | Meaning | String | Meaning |
|---|---|---|---|
| `-eq` | equal | `=` or `==` | equal |
| `-ne` | not equal | `!=` | not equal |
| `-gt` | greater than | `-z` | string is empty |
| `-lt` | less than | `-n` | string is non-empty |
| `-ge` | ≥ | | |
| `-le` | ≤ | | |

Notice: numeric comparison uses `-eq`, not `==`. Using `==` on numbers (`[ "$age" == 20 ]`) works by accident because it's comparing them as strings, but mixing this up is a classic beginner bug — e.g., `[ "10" -lt "9" ]` is false (numeric), but `[ "10" < "9" ]` behaves unpredictably as a string comparison inside single brackets.

### Run This — File Tests
```bash
touch testfile.txt
if [ -f testfile.txt ]; then
  echo "testfile.txt exists and is a regular file."
fi
if [ -d testfile.txt ]; then
  echo "It's a directory."
else
  echo "It's not a directory."
fi
```
Predict both outcomes before running.

<details>
<summary>Explanation</summary>

`-f` tests "is this a regular file," `-d` tests "is this a directory." Since `testfile.txt` was just created with `touch` (which makes an empty file), the first check passes and the second fails.
</details>

### Practice
1. Predict, then verify: `[ "5" -eq "05" ]` — true or false? Why?
   <details><summary>Answer</summary>

   True. Numeric comparison operators interpret both sides as numbers, and `05` numerically equals `5`. Leading zeros don't matter for `-eq`.
   </details>

2. Write a script `even-odd.sh` that takes a number as `$1` and prints whether it's even or odd. (Hint: `$((num % 2))` computes the remainder.)
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   num=$1
   if [ $((num % 2)) -eq 0 ]; then
     echo "$num is even."
   else
     echo "$num is odd."
   fi
   ```
   </details>

3. Predict: what happens if you run your `even-odd.sh` with **no argument** at all? Try it, read the error, then fix the script so it prints a friendly usage message instead of an ugly error.
   <details><summary>Answer</summary>

   You'll likely see something like `[: -eq: unary operator expected` — because `$num` is empty, `$((num % 2))` still evaluates oddly to a value but the underlying issue is `$1` being unset makes downstream logic fragile. Fix:
   ```bash
   #!/bin/bash
   if [ -z "$1" ]; then
     echo "Usage: ./even-odd.sh <number>"
     exit 1
   fi
   num=$1
   if [ $((num % 2)) -eq 0 ]; then
     echo "$num is even."
   else
     echo "$num is odd."
   fi
   ```
   </details>

4. Explore `[[ ]]` (double brackets, a bash-specific upgrade to `[ ]`). Run both of these and compare — predict first:
   ```bash
   name="John Smith"
   [ $name = "John Smith" ] && echo "single bracket matched"
   [[ $name = "John Smith" ]] && echo "double bracket matched"
   ```
   <details><summary>Answer</summary>

   The single-bracket version throws an error like `too many arguments`, because `$name` is unquoted and contains a space — `[` splits it into two separate words and gets confused. The double-bracket version works fine even unquoted, because `[[ ]]` handles word-splitting more safely. **Lesson: prefer `[[ ]]` in bash scripts, and when you do use `[ ]`, always quote your variables:** `[ "$name" = "John Smith" ]`.
   </details>

5. Write `file-check.sh` that takes a filename as `$1` and reports whether it exists, and if it does, whether it's a file or a directory.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   if [ -e "$1" ]; then
     if [ -d "$1" ]; then
       echo "$1 exists and is a directory."
     else
       echo "$1 exists and is a file."
     fi
   else
     echo "$1 does not exist."
   fi
   ```
   `-e` tests plain existence, regardless of type.
   </details>

6. Predict and test: combine conditions with `&&` (AND) and `||` (OR). What does this print for `score=85`?
   ```bash
   score=85
   if [ "$score" -ge 90 ]; then
     echo "A"
   elif [ "$score" -ge 80 ] && [ "$score" -lt 90 ]; then
     echo "B"
   else
     echo "C or below"
   fi
   ```
   <details><summary>Answer</summary>

   Prints `B`. `85` fails the first check (`-ge 90`), passes the second (`>= 80 AND < 90`).
   </details>

### Mini-Project: `grade.sh`
Take a numeric score as `$1` and print a letter grade using this scale: 90+ = A, 80-89 = B, 70-79 = C, 60-69 = D, below 60 = F. Validate that an argument was actually given first.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./grade.sh <score>"
  exit 1
fi
score=$1
if [ "$score" -ge 90 ]; then
  echo "A"
elif [ "$score" -ge 80 ]; then
  echo "B"
elif [ "$score" -ge 70 ]; then
  echo "C"
elif [ "$score" -ge 60 ]; then
  echo "D"
else
  echo "F"
fi
```
</details>

---

## Level 5 — Loops

### Lesson
Three loop types:
- `for` — iterate over a known list of items.
- `while` — repeat as long as a condition is true.
- `until` — repeat until a condition becomes true (opposite of `while`).

### Run This
Predict the full output before running:
```bash
for fruit in apple banana cherry; do
  echo "I like $fruit"
done
```

<details>
<summary>What did you see?</summary>

```
I like apple
I like banana
I like cherry
```
</details>

### Run This — Counting Loops
```bash
for i in {1..5}; do
  echo "Count: $i"
done
```
Predict the range of numbers you'll see.

<details>
<summary>Explanation</summary>

`{1..5}` is **brace expansion** — bash expands it into `1 2 3 4 5` before the loop even starts. Try `{1..10..2}` on your own to discover step values.
</details>

### Run This — `while`
```bash
count=1
while [ "$count" -le 3 ]; do
  echo "Loop number $count"
  count=$((count + 1))
done
```
Predict: what happens if you forget the `count=$((count + 1))` line? (Don't actually run it without a way to stop — you'd need Ctrl+C.)

<details>
<summary>Answer</summary>

Without incrementing `count`, the condition `[ "$count" -le 3 ]` never becomes false, so the loop runs **forever** — an infinite loop. This is the single most common loop bug. Always double-check the update step exists and actually moves toward the exit condition.
</details>

### Practice
1. Write a `for` loop that prints the numbers 10 down to 1 (descending). (Hint: `{10..1}` — does it work the way you expect? Test your prediction.)
   <details><summary>Answer</summary>

   ```bash
   for i in {10..1..-1}; do
     echo "$i"
   done
   ```
   Plain `{10..1}` (without the `-1` step) actually **does** work in modern bash and counts down automatically — bash is smart enough to detect the direction. Try both and compare.
   </details>

2. Loop over the files in your current directory and print each filename with `"Found: "` in front. (Hint: `for f in *; do ... done`.)
   <details><summary>Answer</summary>

   ```bash
   for f in *; do
     echo "Found: $f"
   done
   ```
   </details>

3. Write a `while` loop that keeps asking the user to `read` a number until they type `0`, then stops.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   num=1
   while [ "$num" -ne 0 ]; do
     read -p "Enter a number (0 to stop): " num
   done
   echo "Stopped."
   ```
   </details>

4. Predict, then test the difference: rewrite exercise 3 using `until` instead of `while`.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   num=1
   until [ "$num" -eq 0 ]; do
     read -p "Enter a number (0 to stop): " num
   done
   echo "Stopped."
   ```
   `until` is simply the negated form of `while` — it loops while the condition is **false**, and stops once it becomes true. Same result, inverted logic.
   </details>

5. Use `break` and `continue`. Predict this output, then run it:
   ```bash
   for i in {1..10}; do
     if [ "$i" -eq 3 ]; then
       continue
     fi
     if [ "$i" -eq 6 ]; then
       break
     fi
     echo "$i"
   done
   ```
   <details><summary>Answer</summary>

   ```
   1
   2
   4
   5
   ```
   `continue` skips the rest of *that one iteration* (so `3` never gets printed) but the loop keeps going. `break` exits the loop entirely (so nothing after `5` prints, including `6` itself).
   </details>

6. Write a loop that sums the numbers 1 through 100 and prints the total. Predict the answer mathematically first (there's a famous shortcut formula), then confirm the script agrees.
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   sum=0
   for i in {1..100}; do
     sum=$((sum + i))
   done
   echo "Sum: $sum"
   ```
   Output: `Sum: 5050`. (Shortcut: `n(n+1)/2 = 100*101/2 = 5050`.)
   </details>

### Mini-Project: `countdown.sh`
Take a starting number as `$1`, then count down from it to `1`, printing each number, and finish with `"Liftoff!"`. Handle the case where no argument is given.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./countdown.sh <start_number>"
  exit 1
fi
n=$1
while [ "$n" -ge 1 ]; do
  echo "$n"
  n=$((n - 1))
  sleep 1
done
echo "Liftoff!"
```
</details>

---

## Level 6 — Functions

### Lesson
Functions bundle reusable code under a name. Define with `function_name() { ... }`, call by just typing the name (like any other command). Functions can take arguments (accessed as `$1`, `$2`… *inside the function*, separate from the script's own `$1`), and can `return` a numeric exit status or `echo` output to be captured.

### Run This
Predict what this prints:
```bash
greet() {
  echo "Hello, $1!"
}
greet "World"
greet "Bash"
```

<details>
<summary>What did you see?</summary>

```
Hello, World!
Hello, Bash!
```
</details>

### What Just Happened
- Defining `greet() { ... }` doesn't run anything by itself — it just teaches bash the recipe.
- Calling `greet "World"` runs the function body with `$1` set to `"World"` *inside that function only*.
- Functions must be **defined before they're called** in the file (bash reads top to bottom).

### Run This — Return Values
```bash
add() {
  echo $(( $1 + $2 ))
}
result=$(add 3 4)
echo "Result: $result"
```
Predict the output before running.

<details>
<summary>Explanation</summary>

Bash functions don't "return" data the way functions in Python or JavaScript do — `return` in bash can only send back a small numeric **exit status** (0-255), meant for signaling success/failure, not data. To get actual data out, the convention is: have the function `echo` its result, and capture that with `$(...)` from the caller, exactly like we captured command output in Level 2.
</details>

### Practice
1. Predict, then verify: are variables created inside a function visible outside it by default?
   ```bash
   myfunc() {
     inner=42
   }
   myfunc
   echo "$inner"
   ```
   <details><summary>Answer</summary>

   It prints `42`. By default, bash functions share the **same variable scope** as the rest of the script — variables aren't automatically local. This surprises people coming from other languages. To make a variable function-local, declare it with `local`:
   ```bash
   myfunc() {
     local inner=42
   }
   myfunc
   echo "$inner"   # prints nothing — inner never escaped the function
   ```
   </details>

2. Write a function `is_even` that takes a number and `echo`s `"yes"` or `"no"`. Call it and capture the result in a variable.
   <details><summary>Answer</summary>

   ```bash
   is_even() {
     if [ $(( $1 % 2 )) -eq 0 ]; then
       echo "yes"
     else
       echo "no"
     fi
   }
   answer=$(is_even 8)
   echo "Is 8 even? $answer"
   ```
   </details>

3. Predict: what's the actual **exit status** convention in bash — is `0` success or failure? Test with:
   ```bash
   check_positive() {
     if [ "$1" -gt 0 ]; then
       return 0
     else
       return 1
     fi
   }
   check_positive 5
   echo "Exit status: $?"
   check_positive -3
   echo "Exit status: $?"
   ```
   <details><summary>Answer</summary>

   ```
   Exit status: 0
   Exit status: 1
   ```
   In bash (and Unix generally), **`0` means success**, and any non-zero value means some kind of failure — the opposite of what boolean logic in most programming languages would suggest. `$?` always holds the exit status of the most recently run command or function.
   </details>

4. Write a function `max` that takes two numbers and echoes the larger one. Test it with a few pairs including equal numbers.
   <details><summary>Answer</summary>

   ```bash
   max() {
     if [ "$1" -ge "$2" ]; then
       echo "$1"
     else
       echo "$2"
     fi
   }
   echo "$(max 7 3)"
   echo "$(max 2 9)"
   echo "$(max 5 5)"
   ```
   </details>

5. Predict and test: can a function call another function? Write `describe_number` that calls your `is_even` function from exercise 2 internally.
   <details><summary>Answer</summary>

   ```bash
   describe_number() {
     local result
     result=$(is_even "$1")
     echo "$1 is even: $result"
   }
   describe_number 10
   ```
   Yes — functions can freely call other functions defined earlier in the same script.
   </details>

### Mini-Project: `toolbox.sh`
Build a script with three functions: `square` (echoes a number squared), `is_prime` (echoes `"yes"`/`"no"` — a naive check is fine, e.g. loop from 2 to n-1 checking divisibility), and `main` that reads a number from the user and prints both results using the other two functions. Call `main` at the bottom of the script.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash

square() {
  echo $(( $1 * $1 ))
}

is_prime() {
  local n=$1
  if [ "$n" -lt 2 ]; then
    echo "no"
    return
  fi
  local i=2
  while [ "$i" -lt "$n" ]; do
    if [ $(( n % i )) -eq 0 ]; then
      echo "no"
      return
    fi
    i=$((i + 1))
  done
  echo "yes"
}

main() {
  read -p "Enter a number: " num
  echo "Square: $(square "$num")"
  echo "Prime: $(is_prime "$num")"
}

main
```
</details>

---

## Level 7 — Arrays

### Lesson
Arrays hold multiple values in one variable. Declare with `arr=(item1 item2 item3)`. Access by index with `${arr[0]}` (bash arrays are **zero-indexed**). Get all elements with `${arr[@]}`, and the count with `${#arr[@]}`.

### Run This
Predict the output of each line:
```bash
colors=(red green blue)
echo "${colors[0]}"
echo "${colors[1]}"
echo "${colors[@]}"
echo "${#colors[@]}"
```

<details>
<summary>What did you see?</summary>

```
red
green
red green blue
3
```
</details>

### What Just Happened
- `colors[0]` is `red` — the **first** element, at index 0, not 1.
- `${colors[@]}` expands to every element, space-separated.
- `${#colors[@]}` gives the array's length (3 elements), not the length of any string.

### Run This — Looping Over Arrays
```bash
for color in "${colors[@]}"; do
  echo "Color: $color"
done
```
Predict, then run — and notice we quoted `"${colors[@]}"`. Try it *unquoted* too (`${colors[@]}`) with an array that has a multi-word element, and compare:
```bash
names=("Ann Lee" "Bob" "Cy Young")
for n in "${names[@]}"; do echo "Quoted: [$n]"; done
for n in ${names[@]}; do echo "Unquoted: [$n]"; done
```

<details>
<summary>Explanation</summary>

Quoted:
```
Quoted: [Ann Lee]
Quoted: [Bob]
Quoted: [Cy Young]
```
Unquoted:
```
Unquoted: [Ann]
Unquoted: [Lee]
Unquoted: [Bob]
Unquoted: [Cy]
Unquoted: [Young]
```
Without quotes, bash **word-splits** on spaces, breaking `"Ann Lee"` into two separate loop iterations. **Always quote `"${array[@]}"` when looping**, unless you deliberately want word-splitting.
</details>

### Practice
1. Create an array of your three favorite foods and print them one per line using a `for` loop.
   <details><summary>Answer</summary>

   ```bash
   foods=("pizza" "sushi" "tacos")
   for f in "${foods[@]}"; do
     echo "$f"
   done
   ```
   </details>

2. Predict: how do you add an item to an existing array? Try:
   ```bash
   foods+=("pasta")
   echo "${foods[@]}"
   ```
   <details><summary>Answer</summary>

   `+=` appends to an array. Output: `pizza sushi tacos pasta`.
   </details>

3. Print just the last element of an array without knowing its length in advance. (Hint: `${array[-1]}`.)
   <details><summary>Answer</summary>

   ```bash
   echo "${foods[-1]}"
   ```
   Negative indices count from the end — `-1` is the last element. This is a bash 4.3+ feature, standard on modern Ubuntu.
   </details>

4. Predict and test: what does `${foods[@]:1:2}` print? (This is array **slicing**: offset:length.)
   <details><summary>Answer</summary>

   Given `foods=("pizza" "sushi" "tacos" "pasta")`, it prints `sushi tacos` — starting at index 1, taking 2 elements.
   </details>

5. Build an associative array (a dictionary — key/value pairs instead of numeric indices). Predict, then run:
   ```bash
   declare -A capitals
   capitals[France]="Paris"
   capitals[Japan]="Tokyo"
   echo "${capitals[France]}"
   for country in "${!capitals[@]}"; do
     echo "$country -> ${capitals[$country]}"
   done
   ```
   <details><summary>Answer</summary>

   ```
   Paris
   France -> Paris
   Japan -> Tokyo
   ```
   (Order of the loop may vary — associative arrays are unordered.) `declare -A` is required to create an associative array; without it, `capitals[France]` would just create index `0` since `France` gets treated as an arithmetic expression evaluating to `0`. `"${!capitals[@]}"` gives you the **keys**.
   </details>

6. Remove an element from an array using `unset`. Predict what the array looks like afterward — does the index gap get filled in?
   ```bash
   nums=(10 20 30 40)
   unset 'nums[1]'
   echo "${nums[@]}"
   echo "${#nums[@]}"
   for i in "${!nums[@]}"; do echo "index $i = ${nums[$i]}"; done
   ```
   <details><summary>Answer</summary>

   ```
   10 30 40
   3
   index 0 = 10
   index 2 = 30
   index 3 = 40
   ```
   The gap at index `1` is **not** filled — index `2` still holds `30`. `${#nums[@]}` correctly reports `3` remaining elements, but the indices are no longer contiguous. This matters if you ever loop with a numeric counter (`for ((i=0; i<${#nums[@]}; i++))`) instead of `"${!nums[@]}"`.
   </details>

### Mini-Project: `roster.sh`
Build a script that starts with an array of student names, then:
- Prints the total number of students.
- Prints each name with a number in front (`1. Alice`, `2. Bob`, …).
- Asks the user for a new name and adds it to the array.
- Prints the updated roster.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
students=("Alice" "Bob" "Charlie")

echo "Total students: ${#students[@]}"

i=1
for s in "${students[@]}"; do
  echo "$i. $s"
  i=$((i + 1))
done

read -p "Enter a new student name: " new_student
students+=("$new_student")

echo "--- Updated Roster ---"
i=1
for s in "${students[@]}"; do
  echo "$i. $s"
  i=$((i + 1))
done
```
</details>

---

## Level 8 — Text, Strings, and Files (`grep`, `sed`, `awk` Basics)

### Lesson
Bash scripts often glue together small, powerful Unix tools rather than reimplementing text-processing logic from scratch:
- `grep` **finds** lines matching a pattern.
- `sed` **transforms** text (classic use: find-and-replace).
- `awk` **extracts and processes** columns of data.
- Bash also has built-in **string operations** for simpler cases.

### Run This
```bash
cat > names.txt << 'EOF'
Alice,28,Engineer
Bob,35,Designer
Charlie,22,Engineer
Dana,41,Manager
EOF

grep "Engineer" names.txt
```
Predict which lines will print.

<details>
<summary>What did you see?</summary>

```
Alice,28,Engineer
Charlie,22,Engineer
```
`grep` scans the file line by line and prints only the lines containing the pattern `"Engineer"`.
</details>

### Run This — `sed`
```bash
sed 's/Engineer/Developer/' names.txt
```
Predict the output, and notice: does this change `names.txt` itself, or just what's printed?

<details>
<summary>Explanation</summary>

`sed 's/OLD/NEW/'` substitutes the **first** match of `OLD` with `NEW` **on each line**, printing the result to the screen. `names.txt` itself is **unchanged** — `sed` reads and prints by default. To edit the file in place, you'd add the `-i` flag: `sed -i 's/Engineer/Developer/' names.txt` (be careful — this permanently rewrites the file).
</details>

### Run This — `awk`
```bash
awk -F',' '{print $1}' names.txt
```
Predict the output before running — what do you think `$1` refers to here (careful — this is a *different* `$1` from bash's positional arguments)?

<details>
<summary>Explanation</summary>

```
Alice
Bob
Charlie
Dana
```
`-F','` tells `awk` to split each line into fields wherever a comma appears. `$1` inside `awk` means "the first field of the current line" — completely separate from bash's `$1` (script argument), just a coincidence of notation. `$2` would print the ages, `$0` prints the whole original line.
</details>

### Practice
1. Use `grep` to find every line in `names.txt` where the age is `35` or higher... actually, plain `grep` can't do numeric comparisons — it only matches text patterns. Use `awk` instead: print every row where the second column (age) is greater than 30.
   <details><summary>Answer</summary>

   ```bash
   awk -F',' '$2 > 30 {print $0}' names.txt
   ```
   This shows `awk` isn't just for extracting columns — the part before `{ }` is a **condition**, and `{print $0}` only runs for lines matching it.
   </details>

2. Predict, then test: what does `grep -c "Engineer" names.txt` do? (`-c` flag)
   <details><summary>Answer</summary>

   It prints `2` — the **count** of matching lines, instead of the lines themselves.
   </details>

3. Predict, then test: what does `grep -v "Engineer" names.txt` do? (`-v` flag)
   <details><summary>Answer</summary>

   It prints every line that does **NOT** match — the inverse of normal `grep`. Output:
   ```
   Bob,35,Designer
   Dana,41,Manager
   ```
   </details>

4. Use `sed` to replace commas with tabs in `names.txt` (without modifying the actual file — just print the result).
   <details><summary>Answer</summary>

   ```bash
   sed 's/,/\t/g' names.txt
   ```
   The `g` flag means "global" — replace **every** match on the line, not just the first. Without `g`, `sed` only replaces the first comma per line.
   </details>

5. Explore bash's built-in string operations (no external tool needed). Predict each output:
   ```bash
   text="Hello, Bash World"
   echo "${#text}"
   echo "${text^^}"
   echo "${text,,}"
   echo "${text/Bash/Shell}"
   ```
   <details><summary>Answer</summary>

   ```
   18
   HELLO, BASH WORLD
   hello, bash world
   Hello, Shell World
   ```
   `${#text}` = length, `${text^^}` = uppercase all, `${text,,}` = lowercase all, `${text/OLD/NEW}` = replace first match (bash's own built-in substitution, no `sed` required for simple cases).
   </details>

6. Combine tools in a pipeline: count how many "Engineer" rows exist using `grep` piped into `wc -l` (word/line count).
   <details><summary>Answer</summary>

   ```bash
   grep "Engineer" names.txt | wc -l
   ```
   The `|` (pipe) sends `grep`'s output as input to `wc -l`, which counts lines. This is the essence of Unix philosophy: small tools, connected together, each doing one job well.
   </details>

### Mini-Project: `report.sh`
Using `names.txt` from above, write a script that prints:
- The total number of people (hint: `wc -l < names.txt`)
- The number of Engineers
- Every person's name and age only (not job title), one per line, formatted as `"Name is Age years old"` — use `awk` with a custom output format.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
total=$(wc -l < names.txt)
engineers=$(grep -c "Engineer" names.txt)

echo "Total people: $total"
echo "Engineers: $engineers"
echo "--- Ages ---"
awk -F',' '{print $1 " is " $2 " years old"}' names.txt
```
</details>

---

## Level 9 — Exit Codes, Errors, and Debugging

### Lesson
Every command that finishes leaves behind an **exit status** in `$?`: `0` for success, non-zero for failure. Scripts can check this to react to errors, and can set their *own* exit status with `exit N`. Bash also offers safety nets: `set -e` (stop on first error), `set -u` (error on undefined variables), and `trap` (run cleanup code when the script exits or is interrupted).

### Run This
Predict the exit status before running each:
```bash
ls /this/does/not/exist
echo "Exit status: $?"

ls .
echo "Exit status: $?"
```

<details>
<summary>What did you see?</summary>

```
ls: cannot access '/this/does/not/exist': No such file or directory
Exit status: 2
(file listing)
Exit status: 0
```
Different failures can produce different non-zero codes — `2` here happens to be `ls`'s specific code for "cannot access." What matters most for your own scripts is usually just "was it zero (success) or not."
</details>

### Run This — `set -e`
```bash
cat > risky.sh << 'EOF'
#!/bin/bash
set -e
echo "Step 1"
ls /nonexistent/path
echo "Step 2 - did we get here?"
EOF
chmod +x risky.sh
./risky.sh
```
Predict: does `"Step 2"` print?

<details>
<summary>Explanation</summary>

No — `set -e` makes the entire script **exit immediately** the moment any command fails (returns non-zero), instead of bash's default behavior of plowing ahead regardless. This is a widely recommended safety habit for scripts that shouldn't continue after something's gone wrong.
</details>

### Run This — `trap`
```bash
cat > cleanup.sh << 'EOF'
#!/bin/bash
trap 'echo "Cleaning up before exit..."' EXIT
echo "Doing some work..."
touch tempfile.txt
echo "Work done."
EOF
chmod +x cleanup.sh
./cleanup.sh
```
Predict when the "Cleaning up..." message appears relative to the others.

<details>
<summary>Explanation</summary>

```
Doing some work...
Work done.
Cleaning up before exit...
```
`trap 'command' EXIT` registers `command` to run automatically whenever the script exits — normally, via error, or via `exit` — regardless of *where* in the script it stops. This is the standard bash pattern for guaranteeing cleanup (like deleting temp files) always happens.
</details>

### Practice
1. Predict, then check: what's `$?` immediately after a successful `echo`?
   <details><summary>Answer</summary>

   `0`. `echo` basically always succeeds.
   </details>

2. Write `divide.sh` that takes two numbers and divides them, but first checks if the second number is `0` and exits with an error message and status `1` if so (avoiding bash's divide-by-zero crash).
   <details><summary>Answer</summary>

   ```bash
   #!/bin/bash
   if [ "$2" -eq 0 ]; then
     echo "Error: cannot divide by zero." >&2
     exit 1
   fi
   echo $(( $1 / $2 ))
   ```
   (`>&2` redirects the error message to **stderr** instead of stdout — the correct place for error output, a habit worth building now.)
   </details>

3. Predict, then test: what does `set -u` do here?
   ```bash
   set -u
   echo "$undefined_variable"
   ```
   <details><summary>Answer</summary>

   ```
   bash: undefined_variable: unbound variable
   ```
   Normally, referencing an unset variable just silently expands to empty text — a common source of subtle bugs (e.g., accidentally wiping a directory because a variable in `rm -rf "$dir"` was empty). `set -u` turns that silent bug into a loud, immediate error.
   </details>

4. Add both `set -e` and `set -u` to the top of your `divide.sh` from exercise 2. Predict: does adding them change its behavior for normal, correct usage? Test it with `./divide.sh 10 2` to confirm nothing broke.
   <details><summary>Answer</summary>

   No change for correct usage — `set -e`/`set -u` only change behavior when something actually goes wrong (an error, or an unset variable), acting purely as safety nets.
   </details>

5. Use `trap` to catch `Ctrl+C` (technically the `INT` signal) instead of `EXIT`. Predict what happens when you run this and press Ctrl+C while it's sleeping:
   ```bash
   trap 'echo "Interrupted! Exiting gracefully."; exit 1' INT
   echo "Sleeping for 10 seconds... press Ctrl+C to interrupt."
   sleep 10
   echo "Finished sleeping normally."
   ```
   <details><summary>Answer</summary>

   Pressing Ctrl+C prints `Interrupted! Exiting gracefully.` and the script stops immediately — `"Finished sleeping normally."` never prints. Without the `trap`, Ctrl+C would still stop the script, but without your custom message or controlled cleanup.
   </details>

6. Debug mode: run any earlier script with `bash -x scriptname.sh` instead of `./scriptname.sh`. Predict what's different about the output.
   <details><summary>Answer</summary>

   `-x` makes bash print **every command it executes**, prefixed with `+`, before running it — a built-in trace/debug mode. Extremely useful when a script isn't doing what you expect and you can't tell which line is the culprit.
   </details>

### Mini-Project: `safe-backup.sh`
Write a script that:
- Takes a filename as `$1`.
- Uses `set -e` and `set -u` at the top.
- Uses `trap` to print `"Backup script finished."` on exit, no matter what.
- Checks the file exists (`-f`); if not, prints an error to stderr and exits `1`.
- If it exists, copies it to `<filename>.bak` and prints a success message.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
set -eu
trap 'echo "Backup script finished."' EXIT

if [ -z "${1:-}" ]; then
  echo "Usage: ./safe-backup.sh <filename>" >&2
  exit 1
fi

if [ ! -f "$1" ]; then
  echo "Error: '$1' does not exist or is not a file." >&2
  exit 1
fi

cp "$1" "$1.bak"
echo "Backed up '$1' to '$1.bak'."
```
Note the `${1:-}` trick — with `set -u` active, checking `$1` when it might not exist would itself trigger the "unbound variable" error, so we use the default-value syntax from Level 3 to check safely first.
</details>

---

## Level 10 — Capstone: Putting It All Together

### Lesson
There's no new syntax in this level — it's entirely about **composition**: combining variables, arguments, conditionals, loops, functions, arrays, text tools, and error handling into one coherent program. This is what real-world scripts look like.

### Run This — Study a Combined Example
Before building your own, read this script carefully and **predict its full output** for the input log below, *before* running it.

```bash
cat > access.log << 'EOF'
2024-01-01,200,/home
2024-01-01,404,/missing
2024-01-02,200,/home
2024-01-02,500,/api
2024-01-02,200,/about
2024-01-03,404,/old-page
EOF

cat > log-report.sh << 'EOF'
#!/bin/bash
set -eu

count_status() {
  local status=$1
  grep -c ",$status," access.log || true
}

main() {
  local logfile="access.log"
  if [ ! -f "$logfile" ]; then
    echo "Error: $logfile not found." >&2
    exit 1
  fi

  local total
  total=$(wc -l < "$logfile")
  echo "Total requests: $total"

  local statuses=(200 404 500)
  for s in "${statuses[@]}"; do
    local c
    c=$(count_status "$s")
    echo "Status $s: $c"
  done

  echo "--- Errors (4xx/5xx) ---"
  awk -F',' '$2 >= 400 {print $1, $2, $3}' "$logfile"
}

main
EOF
chmod +x log-report.sh
./log-report.sh
```

<details>
<summary>What did you see?</summary>

```
Total requests: 6
Status 200: 3
Status 404: 2
Status 500: 1
--- Errors (4xx/5xx) ---
2024-01-01 404 /missing
2024-01-02 500 /api
2024-01-03 404 /old-page
```
</details>

### What Just Happened — Trace the Concepts
Go back through `log-report.sh` and identify, out loud or in writing, where each of these appears — this is the real exercise for this level:
- Shebang & `set -eu` (Levels 1, 9)
- A function with a local variable and a parameter (Level 6)
- `grep -c` and the `|| true` trick that stops `set -e` from killing the script when `grep` finds zero matches, which counts as "failure" (Levels 8, 9)
- An array and a `for` loop over it (Levels 5, 7)
- File existence checking (Level 4)
- `awk` with a numeric condition (Level 8)

<details>
<summary>Why the <code>|| true</code>?</summary>

`grep -c` returns exit status `1` (failure) if it finds **zero** matches, even though printing `0` is a perfectly valid, non-broken answer. Under `set -e`, that "failure" would silently kill the whole script. `|| true` says "if this command fails, run `true` instead" (which always succeeds), neutralizing the unwanted exit. This is a real, commonly-hit gotcha — good to have seen it once deliberately.
</details>

### Practice
1. Modify `log-report.sh` to also report the count of `200` vs non-`200` as a percentage (integer math is fine — bash doesn't do decimals natively).
   <details><summary>Answer</summary>

   ```bash
   local ok
   ok=$(count_status 200)
   local pct=$(( ok * 100 / total ))
   echo "Success rate: ${pct}%"
   ```
   Add this inside `main`, after the total is calculated.
   </details>

2. Add a command-line argument so the script accepts a log filename instead of hardcoding `"access.log"`, defaulting to `access.log` if none is given.
   <details><summary>Answer</summary>

   ```bash
   local logfile="${1:-access.log}"
   ```
   Replace the hardcoded assignment with this.
   </details>

3. Add a `trap` that prints `"Report generation complete."` on exit.
   <details><summary>Answer</summary>

   Add near the top, after `set -eu`:
   ```bash
   trap 'echo "Report generation complete."' EXIT
   ```
   </details>

4. Predict, then verify: what happens to the script if `access.log` is empty (zero lines)? Test it: `> access.log && ./log-report.sh` (this empties the file first).
   <details><summary>Answer</summary>

   `Total requests: 0`, and every status count prints `0` thanks to the `|| true` safety net from earlier — nothing crashes. This is exactly the kind of edge case that separates a fragile script from a robust one, and it's a direct payoff of the Level 9 habits.
   </details>

5. Add input validation: if the log file has any line that *doesn't* match the expected `date,status,path` format (3 comma-separated fields), print a warning listing which lines are malformed. (Hint: use `awk -F',' 'NF != 3 {print NR": "$0}'` — `NF` is number of fields, `NR` is the line number.)
   <details><summary>Answer</summary>

   ```bash
   local bad_lines
   bad_lines=$(awk -F',' 'NF != 3 {print NR": "$0}' "$logfile")
   if [ -n "$bad_lines" ]; then
     echo "Warning: malformed lines found:" >&2
     echo "$bad_lines" >&2
   fi
   ```
   </details>

### Final Capstone Project: `system-audit.sh`
Combine everything from Levels 1-10 into one script that:
1. Accepts an optional directory path as `$1` (defaults to the current directory).
2. Validates the directory exists; exits with a clear error and status `1` if not.
3. Uses a **function** to count how many files vs. directories are inside it.
4. Uses an **array** to track file extensions found (e.g. `.sh`, `.txt`), and a loop to tally how many of each.
5. Uses `grep`/`awk` to search all `.txt` files in that directory for a keyword the user provides via `read`.
6. Sets `set -eu` and a `trap` that reports `"Audit complete."` when the script exits, success or failure.
7. Prints a clean, labeled summary report at the end.

There's no single "correct" answer here — this is meant as a genuine design exercise. Before opening the sample solution, sketch your own version on paper (or in a file) and try to get it running. Compare your approach to the one below afterward; differences aren't necessarily mistakes.

<details>
<summary>Sample solution</summary>

```bash
#!/bin/bash
set -eu
trap 'echo "Audit complete."' EXIT

count_items() {
  local dir=$1
  local files
  local dirs
  files=$(find "$dir" -maxdepth 1 -type f | wc -l)
  dirs=$(find "$dir" -maxdepth 1 -type d | wc -l)
  echo "$files $dirs"
}

main() {
  local target="${1:-.}"

  if [ ! -d "$target" ]; then
    echo "Error: '$target' is not a valid directory." >&2
    exit 1
  fi

  echo "=== Auditing: $target ==="

  read -r file_count dir_count <<< "$(count_items "$target")"
  echo "Files: $file_count"
  echo "Directories: $dir_count"

  echo "--- Extension breakdown ---"
  local extensions=()
  for f in "$target"/*; do
    [ -f "$f" ] || continue
    local ext="${f##*.}"
    if [ "$ext" = "$f" ]; then
      ext="(none)"
    fi
    extensions+=("$ext")
  done

  if [ "${#extensions[@]}" -eq 0 ]; then
    echo "No files found."
  else
    printf '%s\n' "${extensions[@]}" | sort | uniq -c
  fi

  echo "--- Keyword search in .txt files ---"
  read -p "Enter a keyword to search for: " keyword
  local txt_files
  txt_files=$(find "$target" -maxdepth 1 -type f -name "*.txt")
  if [ -z "$txt_files" ]; then
    echo "No .txt files found in $target."
  else
    grep -n "$keyword" $txt_files 2>/dev/null || echo "No matches found for '$keyword'."
  fi
}

main "$@"
```

**Deliberately worth noticing:** `"${f##*.}"` is a new bit of syntax — bash's built-in pattern-stripping (`##*.` strips everything up to the last `.`), giving the file extension without needing `awk` or `sed`. Look it up and predict what `${f#*.}` (single `#`) would do differently before testing — that's one more prediction exercise, free of charge, to close out the guide.
</details>

---

## Where to Go Next
You've now covered variables, arguments, conditionals, loops, functions, arrays, text processing, and error handling — the core toolkit for the overwhelming majority of real-world bash scripts. From here:
- Read other people's scripts (`/usr/bin`, dotfiles on GitHub, `/etc/init.d`) and try to explain what each line does before checking.
- Look into `getopts` for proper flag parsing (`-v`, `--verbose`, etc.) — a natural next step past simple positional arguments.
- Learn `shellcheck`, a linter that catches exactly the kinds of quoting and scoping bugs this guide highlighted, automatically.
- Keep predicting before running. That habit is worth more than memorizing syntax.
