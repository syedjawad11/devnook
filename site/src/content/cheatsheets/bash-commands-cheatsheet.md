---
title: "Bash Commands Cheat Sheet: Essential Reference"
description: "Master the most useful bash commands with this quick-reference cheat sheet. Covers navigation, file ops, permissions, grep, process management, and scripting."
category: cheatsheets
subcategory: "Reference"
template_id: cheatsheet-v1
tags: [bash, linux, terminal, shell, command-line]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-02"
og_image: "/og/cheatsheets/bash-commands-cheatsheet.png"
actual_word_count: 2710
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "Bash Commands Cheat Sheet: Essential Reference",
    "description": "Master the most useful bash commands with this quick-reference cheat sheet. Covers navigation, file ops, permissions, grep, process management, and scripting.",
    "datePublished": "2026-07-02",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/cheatsheets/bash-commands-cheatsheet/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between bash and sh?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "bash (Bourne Again SHell) is a superset of sh that adds arrays, arithmetic expansion, [[ ]] conditionals, and process substitution. On most Linux systems /bin/sh links to a minimal POSIX shell like dash, not bash. Use #!/usr/bin/env bash when your scripts need bash-specific features."
        }
      },
      {
        "@type": "Question",
        "name": "How do I find a file by name in bash?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Use the find command: find /home -name '*.log' -type f searches all .log files under /home. Add -maxdepth to limit recursion depth. For searching text inside files, use grep -r 'pattern' . instead."
        }
      },
      {
        "@type": "Question",
        "name": "How do I check which process is using a specific port?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Run lsof -i :8080 to see the process name, PID, and user. Alternatively use ss -tlnp | grep :8080 (faster, built into modern Linux) or netstat -tlnp | grep :8080. sudo is required for processes owned by other users."
        }
      }
    ]
  }
  </script>
---

Bash is the default shell on most Linux distributions and macOS, and the runtime behind CI pipelines, deployment scripts, and developer automation. This bash commands cheat sheet groups the most-used commands by category — navigation, file operations, text processing, I/O redirection, process management, and scripting syntax — so you can jump straight to the section you need without filtering through man pages.

## Essential Bash Commands by Category

A quick-lookup overview of the command groups covered in this reference:

| Category | Key commands |
|----------|-------------|
| Navigation | `cd`, `ls`, `pwd`, `pushd`, `popd`, `dirs` |
| Files | `cp`, `mv`, `rm`, `mkdir`, `touch`, `find`, `ln` |
| Viewing | `cat`, `less`, `head`, `tail`, `wc`, `diff` |
| Text processing | `grep`, `sed`, `awk`, `cut`, `sort`, `uniq` |
| Variables | `$VAR`, `${VAR:-default}`, `$(...)`, `$((math))` |
| I/O | `>`, `>>`, `<`, `|`, `2>&1`, `tee` |
| Processes | `ps`, `top`, `kill`, `bg`, `fg`, `jobs`, `nohup` |
| Networking | `curl`, `ping`, `ssh`, `scp`, `rsync`, `ss` |
| Scripting | `if`, `for`, `while`, `case`, `function`, `set` |

## Navigation and Directory Commands

The bash commands you run dozens of times a day:

| Command | What it does |
|---------|--------------|
| `pwd` | Print the current working directory |
| `ls` | List directory contents |
| `ls -la` | Long listing including hidden files |
| `ls -lh` | Long listing with human-readable file sizes |
| `ls -lt` | Sort by modification time, newest first |
| `ls -R` | List directories recursively |
| `cd <dir>` | Change directory |
| `cd ..` | Go up one level |
| `cd ~` | Go to home directory |
| `cd -` | Return to the previous directory |
| `pushd <dir>` | Push directory onto stack and switch to it |
| `popd` | Pop directory from stack and return |
| `dirs` | Display the directory stack |
| `mkdir -p a/b/c` | Create a nested directory path in one step |
| `rmdir <dir>` | Remove an empty directory |

For a wider reference covering the Linux filesystem hierarchy and system administration utilities, the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet/) covers broader territory including package management, disk usage, and service control.

## File Operations

### Copying, Moving, and Removing

| Command | What it does |
|---------|--------------|
| `cp file.txt copy.txt` | Copy a file |
| `cp -r src/ dst/` | Copy a directory recursively |
| `cp -u src dst` | Copy only if source is newer than destination |
| `mv old.txt new.txt` | Rename a file |
| `mv file.txt /tmp/` | Move a file to a directory |
| `rm file.txt` | Delete a file |
| `rm -rf dir/` | Delete a directory and all its contents |
| `touch file.txt` | Create an empty file or update timestamp |
| `ln -s /path/to/target link` | Create a symbolic link |
| `find . -name "*.tmp" -delete` | Find and delete files matching a pattern |

### Viewing File Contents

| Command | What it does |
|---------|--------------|
| `cat file.txt` | Print file contents to stdout |
| `less file.txt` | Page through a file (`q` to quit) |
| `head -n 20 file.txt` | First 20 lines of a file |
| `tail -n 20 file.txt` | Last 20 lines of a file |
| `tail -f log.txt` | Follow a file as it grows (useful for logs) |
| `wc -l file.txt` | Count lines |
| `wc -w file.txt` | Count words |
| `wc -c file.txt` | Count bytes |
| `diff file1 file2` | Show line-by-line differences |
| `stat file.txt` | Show file metadata (size, permissions, timestamps) |

## Bash Variables and Parameter Expansion

Bash variables are set without spaces around `=` and read with `$`. Single quotes prevent expansion; double quotes allow it:

```bash
name="Alice"
count=0
readonly CONFIG_DIR="/etc/myapp"

echo "$name"                    # Alice
echo "Hello, ${name}!"         # Hello, Alice!
echo "${name:-default}"        # use "default" if $name is unset or empty
echo "${name:0:3}"             # substring: first 3 chars → Ali
echo "${name^^}"               # uppercase → ALICE
echo "${#name}"                # string length → 5
echo "${name/Alice/Bob}"       # replace first match → Bob

 # Command substitution
today=$(date +%Y-%m-%d)
file_count=$(ls | wc -l)

 # Arithmetic
((count++))
result=$((count * 10 + 5))
echo "$result"

 # Arrays
servers=("web01" "web02" "db01")
echo "${servers[0]}"           # web01
echo "${servers[@]}"           # all elements
echo "${#servers[@]}"          # array length
```

Special variables Bash always provides:

| Variable | Value |
|----------|-------|
| `$0` | Script name |
| `$1` … `$9` | Positional arguments |
| `$@` | All arguments as separate quoted words |
| `$*` | All arguments as a single word |
| `$#` | Number of arguments |
| `$?` | Exit status of the last command |
| `$$` | PID of the current shell |
| `$!` | PID of the last background process |
| `$SECONDS` | Seconds elapsed since the shell started |
| `$LINENO` | Current line number in the script |
| `$RANDOM` | Random integer 0–32767 |

## Text Search and Processing

### grep — Search Files and Streams

| Command | What it does |
|---------|--------------|
| `grep "pattern" file.txt` | Search for lines matching a pattern |
| `grep -r "pattern" dir/` | Search recursively in a directory |
| `grep -i "pattern" file.txt` | Case-insensitive search |
| `grep -n "pattern" file.txt` | Show line numbers |
| `grep -v "pattern" file.txt` | Show lines that do NOT match |
| `grep -l "pattern" *.log` | List filenames that contain the pattern |
| `grep -c "pattern" file.txt` | Count matching lines |
| `grep -E "error\|warn" file.txt` | Extended regex, match either word |
| `grep -o "pattern" file.txt` | Print only the matched text |
| `grep -A 3 "pattern" file.txt` | Include 3 lines after each match |
| `grep -B 3 "pattern" file.txt` | Include 3 lines before each match |

Use the [regex tester](/tools/regex-tester/) to validate patterns interactively before embedding them in scripts or grep commands.

### sed — Stream Editor

`sed` edits text streams line by line. The most common use is substitution:

| Command | What it does |
|---------|--------------|
| `sed 's/old/new/g' file.txt` | Replace all occurrences of "old" with "new" |
| `sed -i 's/old/new/g' file.txt` | Replace in place (edit the file directly) |
| `sed -i.bak 's/old/new/g' file.txt` | Replace in place, keep `.bak` backup |
| `sed '5d' file.txt` | Delete line 5 |
| `sed -n '5,10p' file.txt` | Print only lines 5 through 10 |
| `sed '/pattern/d' file.txt` | Delete lines matching a pattern |
| `sed 's/^/PREFIX: /' file.txt` | Prepend text to every line |
| `sed 's/$/ SUFFIX/' file.txt` | Append text to every line |

### awk — Column and Record Processing

`awk` processes structured text (CSV, log fields, whitespace-delimited output) by splitting each line into fields:

| Command | What it does |
|---------|--------------|
| `awk '{print $1}' file.txt` | Print the first column |
| `awk -F: '{print $1}' /etc/passwd` | Set delimiter to `:`, print first field |
| `awk '{sum += $2} END {print sum}' file.txt` | Sum the second column |
| `awk 'NR==5' file.txt` | Print only line 5 |
| `awk 'length > 80' file.txt` | Print lines longer than 80 characters |
| `awk '$3 > 1000 {print $1, $3}' file.txt` | Conditional column output |
| `awk 'NR%2==0' file.txt` | Print every second line |

## I/O Redirection and Pipelines

Bash connects commands using stdin (0), stdout (1), and stderr (2):

| Operator | Effect |
|----------|--------|
| `command > file` | Write stdout to file, overwriting it |
| `command >> file` | Append stdout to file |
| `command < file` | Read stdin from file |
| `command 2> file` | Write stderr to file |
| `command 2>&1` | Merge stderr into stdout |
| `command &> file` | Write both stdout and stderr to file |
| `command 2>/dev/null` | Discard all error output |
| `command1 \| command2` | Pipe stdout of command1 to stdin of command2 |
| `command \| tee file` | Write stdout to a file and also to the terminal |

Practical pipeline patterns:

```bash
 # Discard errors entirely
ls /nonexistent 2>/dev/null

 # Capture stdout and stderr together
output=$(command 2>&1)

 # Analyze the 20 most-requested 404 URLs in an nginx access log
cat access.log \
  | grep " 404 " \
  | awk '{print $7}' \
  | sort \
  | uniq -c \
  | sort -rn \
  | head -20

 # Write to a file and see it at the same time
make 2>&1 | tee build.log

 # Process substitution: use command output as a file argument
diff <(sort file1.txt) <(sort file2.txt)

 # Here-string: pass a string as stdin
base64 <<< "hello world"
```

## Process and Job Management

| Command | What it does |
|---------|--------------|
| `ps aux` | List all running processes |
| `ps aux \| grep nginx` | Find a specific process by name |
| `top` | Interactive process monitor (`q` to quit) |
| `htop` | Improved interactive monitor (if installed) |
| `kill <pid>` | Send SIGTERM to a process (graceful stop) |
| `kill -9 <pid>` | Send SIGKILL (force stop, cannot be caught) |
| `killall nginx` | Kill all processes with that exact name |
| `pkill -f "python app.py"` | Kill processes matching a pattern |
| `jobs` | List background and suspended jobs in this shell |
| `bg %1` | Resume job 1 in the background |
| `fg %1` | Bring job 1 to the foreground |
| `command &` | Start a command in the background |
| `nohup command &` | Run immune to hangup signal, stays after logout |
| `disown %1` | Remove job 1 from the shell's job table |
| `wait` | Wait for all background jobs to finish |
| `nice -n 10 command` | Run with reduced CPU scheduling priority |
| `renice -n 5 -p <pid>` | Adjust priority of a running process |

When running long-lived processes over SSH, pair these commands with a terminal multiplexer. The [tmux Cheat Sheet](/cheatsheets/tmux-cheatsheet/) covers session, window, and pane management so processes survive disconnections.

## Bash Scripting Quick Reference

### Conditionals

```bash
#!/usr/bin/env bash

log_file="/var/log/app.log"

 # File tests
if [[ -f "$log_file" ]]; then
    echo "Log file exists"
elif [[ -d "/var/log" ]]; then
    echo "Directory exists but no log file yet"
else
    echo "Neither exists"
fi

 # Common file test flags
 # -f  regular file exists
 # -d  directory exists
 # -e  path exists (file or directory)
 # -r  readable    -w  writable    -x  executable
 # -s  non-empty file
 # -L  symbolic link

 # String comparison
env="${DEPLOY_ENV:-development}"
if [[ "$env" == "production" ]]; then
    echo "Production mode — extra caution"
fi

 # Numeric comparison (use (()) for arithmetic)
file_count=$(ls | wc -l)
if (( file_count > 100 )); then
    echo "More than 100 files in current directory"
fi

 # Case statement
case "$1" in
    start)   systemctl start myapp ;;
    stop)    systemctl stop myapp ;;
    restart) systemctl restart myapp ;;
    *)       echo "Usage: $0 {start|stop|restart}" ;;
esac
```

### Loops

```bash
 # For loop over a list
for service in nginx postgresql redis; do
    if systemctl is-active --quiet "$service"; then
        echo "$service is running"
    else
        echo "$service is STOPPED"
    fi
done

 # Glob expansion — iterate over files
for log in /var/log/*.log; do
    size=$(wc -l < "$log")
    echo "$log: $size lines"
done

 # C-style for loop
for (( i=1; i<=5; i++ )); do
    echo "Step $i of 5"
done

 # While loop reading a file line by line
while IFS= read -r line; do
    echo "Processing: $line"
done < input.txt

 # Until loop (opposite of while — loops until condition is TRUE)
count=0
until [[ $count -ge 5 ]]; do
    echo "count=$count"
    ((count++))
done
```

### Functions

```bash
 # Define with the function keyword or bare name()
check_service() {
    local service_name="$1"          # always use local for function vars
    if systemctl is-active --quiet "$service_name"; then
        echo "$service_name is running"
        return 0
    else
        echo "$service_name is NOT running" >&2
        return 1
    fi
}

 # Call with arguments
check_service nginx
check_service postgresql || echo "postgresql down — alerting on-call"

 # Return values via stdout (command substitution)
get_version() {
    local app="$1"
    "$app" --version 2>&1 | head -1
}
version=$(get_version node)
echo "Node version: $version"
```

### Error Handling

```bash
set -euo pipefail
 # -e   exit immediately on any error
 # -u   treat unset variables as errors
 # -o pipefail   pipe fails if any command in it fails

 # Trap errors and cleanup
trap 'echo "Error on line $LINENO — exiting" >&2' ERR
trap 'rm -f "/tmp/scratch_$$"' EXIT

 # Conditional execution
command1 && command2   # run command2 only if command1 succeeds
command1 || command2   # run command2 only if command1 fails
```

## Bash History and Keyboard Shortcuts

### History Commands

| Command | What it does |
|---------|--------------|
| `history` | Show full command history |
| `history 20` | Show the last 20 commands |
| `!!` | Repeat the last command |
| `!grep` | Repeat the last command starting with `grep` |
| `!<n>` | Repeat history entry number n |
| `!$` | Last argument of the previous command |
| `!*` | All arguments of the previous command |
| `Ctrl+R` | Reverse incremental search through history |
| `history -c` | Clear history for the current session |
| `HISTSIZE=10000` | Number of history entries to keep in memory |
| `HISTFILESIZE=10000` | Number of entries to save to `~/.bash_history` |

### Essential Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Interrupt / kill the foreground process |
| `Ctrl+Z` | Suspend the foreground process (use `fg` to resume) |
| `Ctrl+D` | Send EOF / exit the current shell |
| `Ctrl+L` | Clear the terminal screen |
| `Ctrl+A` | Move cursor to the beginning of the line |
| `Ctrl+E` | Move cursor to the end of the line |
| `Ctrl+W` | Delete the word before the cursor |
| `Ctrl+U` | Delete from the cursor to the beginning of the line |
| `Ctrl+K` | Delete from the cursor to the end of the line |
| `Alt+.` | Insert the last argument of the previous command |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

## Networking Commands

| Command | What it does |
|---------|--------------|
| `ping -c 4 example.com` | Send 4 ICMP echo requests |
| `curl -I https://example.com` | Fetch HTTP response headers only |
| `curl -L -o file.zip https://example.com/file.zip` | Download a file, following redirects |
| `curl -X POST -d '{"key":"val"}' -H 'Content-Type: application/json' URL` | POST JSON |
| `wget -q https://example.com/file.tar.gz` | Download quietly |
| `ssh user@host` | Open an SSH session |
| `ssh -p 2222 user@host` | SSH on a non-standard port |
| `ssh -L 8080:localhost:80 user@host` | Local port forwarding via SSH tunnel |
| `scp file.txt user@host:/path/` | Copy a file to a remote host |
| `rsync -avz src/ user@host:dst/` | Sync a directory to a remote host |
| `netstat -tlnp` | List listening TCP ports with PIDs |
| `ss -tlnp` | Faster alternative to netstat |
| `lsof -i :8080` | Show which process is using port 8080 |
| `dig example.com` | DNS lookup |
| `host example.com` | Simple DNS resolution |

For a thorough walkthrough of curl — including request headers, authentication schemes, and JSON payloads — see the [curl Command Guide](/guides/curl-command-guide/). When deploying from scripts, the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet/) covers the repository operations you'll need alongside push and pull automation. The [Docker Commands Cheat Sheet](/cheatsheets/docker-commands-cheatsheet/) pairs well for containerized deployment workflows.

The [GNU Bash Manual](https://www.gnu.org/software/bash/manual/) is the authoritative reference for every built-in and shell option. The [Linux man page for bash](https://man7.org/linux/man-pages/man1/bash.1.html) documents every flag, expansion rule, and built-in command in full detail.

## Frequently Asked Questions

### What is the difference between bash and sh?

`sh` is the POSIX shell standard — a minimal specification for shell behavior including basic conditionals, loops, and parameter expansion. `bash` (Bourne Again SHell) is a strict superset of `sh` that adds arrays, arithmetic expansion with `$((...))`, `[[ ... ]]` extended conditionals, process substitution with `<(...)`, readline editing, and a richer history system.

On most modern Linux systems, `/bin/sh` is a symlink to `dash` or another minimal POSIX shell — not bash. Scripts with `#!/bin/sh` run in POSIX mode and will fail if they use bash-specific syntax like `[[ ]]` or arrays. Use `#!/usr/bin/env bash` when your script needs bash features, and `#!/bin/sh` only when strict POSIX portability matters (e.g., inside BusyBox or Alpine Linux containers where bash is not installed).

### How do I find a file by name in bash?

Use the `find` command with the `-name` flag:

```bash
find /home -name "*.log" -type f            # all .log files under /home
find . -name "config.json" -maxdepth 3      # search up to 3 levels deep
find /tmp -mmin -30 -type f                 # files modified in the last 30 minutes
find . -name "*.pyc" -delete                # find and delete all .pyc files
find /var/log -size +100M -type f           # files larger than 100 MB
```

For searching text content within files, use `grep -r "pattern" .` instead. Combine both to locate files by name and then filter by content:

```bash
find . -name "*.conf" -exec grep -l "timeout" {} \;
```

### How do I check which process is using a specific port?

Run one of these commands — they need `sudo` for processes owned by other users:

```bash
lsof -i :8080           # process name, PID, user — most readable
ss -tlnp | grep :8080   # faster; built into modern Linux kernels
netstat -tlnp | grep :8080  # classic; requires the net-tools package
fuser 8080/tcp          # returns just the PID
```

`lsof -i :8080` is the most readable on a single server. On high-traffic servers or in scripts, `ss` is faster because it queries the kernel directly without the overhead of scanning `/proc`.

## Conclusion

These bash commands cover the full daily workflow: navigating filesystems, reading and transforming text with grep, sed, and awk, managing background jobs, and writing scripts that handle errors cleanly with `set -euo pipefail` and traps. The scripting section is worth revisiting any time a sequence of bash commands grows beyond a one-liner — the discipline of `local` variables, explicit error handling, and meaningful exit codes pays back quickly in debugging time.

For terminal session management across long-running tasks, the [tmux Cheat Sheet](/cheatsheets/tmux-cheatsheet/) is the natural companion reference. For a broader coverage of Linux system administration commands including disk management, user control, and service configuration, the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet/) goes deeper on system-level utilities.
