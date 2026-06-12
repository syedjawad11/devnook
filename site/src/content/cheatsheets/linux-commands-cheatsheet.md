---
title: "Linux Commands Cheat Sheet"
description: "Linux commands cheatsheet covering bash commands, file management, permissions, process control, networking, and terminal commands for developers."
category: "cheatsheets"
template_id: "cheatsheet-v3"
tags: [linux, bash, terminal, shell, sysadmin, cheatsheet]
related_posts: []
related_tools: []
published_date: "2026-06-10"
og_image: "/og/cheatsheets/linux-commands-cheatsheet.png"
downloadable: true
---

This linux cheatsheet organises the most-used bash commands and terminal commands by task area — from navigating the filesystem to writing shell scripts and managing services. Use it as a linux commands list you can scan at a glance during development or system administration work. Each section pairs a reference table with realistic, copy-pasteable code examples.

## File System Navigation and Linux Commands List

These are the foundational terminal commands for moving around the filesystem and managing files. Every linux tutorial starts here.

| Command | Description |
|---------|-------------|
| `pwd` | Print the current working directory |
| `ls` | List directory contents |
| `ls -la` | Long listing including hidden files |
| `ls -lh` | Long listing with human-readable sizes |
| `ls -lt` | List sorted by modification time, newest first |
| `cd <dir>` | Change to the specified directory |
| `cd ..` | Go up one directory level |
| `cd ~` | Go to your home directory |
| `cd -` | Return to the previous directory |
| `mkdir <dir>` | Create a new directory |
| `mkdir -p a/b/c` | Create a nested directory path all at once |
| `rmdir <dir>` | Remove an empty directory |
| `rm <file>` | Delete a file |
| `rm -rf <dir>` | Recursively delete a directory and all its contents |
| `cp <src> <dst>` | Copy a file to a destination |
| `cp -r <src> <dst>` | Recursively copy a directory |
| `mv <src> <dst>` | Move or rename a file or directory |
| `touch <file>` | Create an empty file or update its timestamp |
| `ln -s <target> <link>` | Create a symbolic link |
| `cat <file>` | Print the contents of a file |
| `less <file>` | Page through a file interactively (q to quit) |
| `more <file>` | Page through a file (forward only) |
| `head -n 20 <file>` | Print the first 20 lines of a file |
| `tail -n 20 <file>` | Print the last 20 lines of a file |
| `tail -f <file>` | Follow a file in real time as it grows |
| `file <name>` | Identify the type of a file |
| `stat <file>` | Show detailed metadata: size, permissions, timestamps |

```bash
## List the 10 most recently modified files
ls -lt | head -11

## Create a standard project directory structure
mkdir -p project/{src,tests,docs,scripts,config}

## Safely preview files before deleting
ls /tmp/*.log && rm /tmp/*.log
```

## File Search and Filtering

These bash commands locate files and content across the filesystem — a skill every linux commands list should cover in depth.

| Command | Description |
|---------|-------------|
| `find . -name "*.conf"` | Find files by name pattern starting from current dir |
| `find / -type f -name "*.sh"` | Find all shell scripts on the system |
| `find . -type f -mtime -7` | Files modified in the last 7 days |
| `find . -type f -newer ref.txt` | Files modified more recently than ref.txt |
| `find . -size +100M` | Files larger than 100 MB |
| `find . -perm 777` | Files with world-writable permissions set |
| `find . -type f -exec grep -l "TODO" {} \;` | Find files that contain a specific string |
| `find . -empty` | Find empty files and directories |
| `grep "pattern" <file>` | Search for a pattern in a file |
| `grep -r "pattern" <dir>` | Recursive search across a directory tree |
| `grep -i "pattern" <file>` | Case-insensitive pattern match |
| `grep -n "pattern" <file>` | Show line numbers alongside matches |
| `grep -v "pattern" <file>` | Show lines that do NOT match the pattern |
| `grep -c "pattern" <file>` | Count the number of matching lines |
| `grep -l "pattern" <dir>` | List only filenames that contain a match |
| `locate <name>` | Fast filename search using a pre-built index |
| `which <command>` | Show the full filesystem path of an executable |
| `type <command>` | Show whether a command is a builtin, alias, or file |
| `du -sh <dir>` | Total disk usage of a directory |
| `df -h` | Disk usage of all mounted filesystems |
| `wc -l <file>` | Count lines in a file |
| `wc -w <file>` | Count words in a file |

For pattern-based searches in text files, the [Regex Cheat Sheet](/cheatsheets/regex-cheatsheet/) pairs well with `grep` and `sed` — it covers the full regex syntax used across these tools.

```bash
## Find .log files larger than 100 MB under /var/log
find /var/log -name "*.log" -size +100M

## Recursive search for "ERROR" in Python source files only
grep -r "ERROR" --include="*.py" .

## Show the 10 largest subdirectories under /var
du -h /var/* | sort -rh | head -10
```

## File Permissions and Ownership

Linux uses a read/write/execute permission model per owner, group, and others. Understanding this model is critical for both security and correct application behaviour.

| Command | Description |
|---------|-------------|
| `ls -l` | View permission bits on files in a directory |
| `chmod 755 <file>` | Set permissions to rwxr-xr-x |
| `chmod 644 <file>` | Set permissions to rw-r--r-- (common for files) |
| `chmod +x <file>` | Add the execute bit for all roles |
| `chmod u+x <file>` | Add execute bit for the owner only |
| `chmod -R 644 <dir>` | Recursively apply permissions to all files |
| `chown user:group <file>` | Change the file's owner and group |
| `chown -R user <dir>` | Recursively change ownership |
| `sudo <command>` | Run a command with root (superuser) privileges |
| `su - <user>` | Open a login shell as another user |
| `umask` | Show the default permission mask for new files |
| `getfacl <file>` | Display extended ACL permissions |
| `setfacl -m u:user:rx <file>` | Grant a specific user read and execute via ACL |

**Permission octal quick reference:**

| Octal | Symbolic | Meaning |
|-------|----------|---------|
| `7` | `rwx` | Read, write, and execute |
| `6` | `rw-` | Read and write |
| `5` | `r-x` | Read and execute |
| `4` | `r--` | Read only |
| `0` | `---` | No permissions |

```bash
## Make a script executable by its owner
chmod +x deploy.sh

## Correct permissions for a web document root
find /var/www -type d -exec chmod 755 {} \;
find /var/www -type f -exec chmod 644 {} \;

## Transfer ownership to the web server user recursively
chown -R www-data:www-data /var/www/html
```

## Process and Job Management

These terminal commands inspect, control, and schedule work on the running system.

| Command | Description |
|---------|-------------|
| `ps aux` | List all running processes with CPU and memory usage |
| `ps -ef` | Full-format process list showing parent PIDs |
| `top` | Interactive real-time process and resource viewer |
| `htop` | Enhanced interactive viewer with colour output |
| `pgrep <name>` | Find process IDs matching a name pattern |
| `pstree` | Show processes as a visual tree |
| `kill <pid>` | Send SIGTERM (graceful termination) to a process |
| `kill -9 <pid>` | Send SIGKILL (forced, immediate termination) |
| `killall <name>` | Terminate all processes with a given name |
| `pkill <pattern>` | Kill processes whose name matches a pattern |
| `jobs` | List background jobs in the current shell session |
| `bg` | Resume a suspended job and run it in the background |
| `fg` | Bring the most recent background job to the foreground |
| `nohup <cmd> &` | Run a command immune to terminal hangup |
| `disown %1` | Detach job 1 from the shell entirely |
| `nice -n 10 <cmd>` | Start a command with reduced CPU scheduling priority |
| `renice 15 -p <pid>` | Adjust the priority of an already-running process |
| `wait` | Wait for all background jobs in the current shell to finish |
| `crontab -e` | Open the current user's cron schedule for editing |
| `crontab -l` | List all scheduled cron jobs for the current user |
| `at now + 2 hours` | Schedule a one-time command to run 2 hours from now |

```bash
## Gracefully stop a named process
kill $(pgrep nginx)

## Start a long job in the background and record its PID
nohup python3 train_model.py > training.log 2>&1 &
echo "Job PID: $!"

## Show the five processes consuming the most memory
ps aux --sort=-%mem | head -6
```

## Text Processing with Bash Commands

These bash commands handle log analysis, data wrangling, and stream manipulation — the core of shell scripting work.

| Command | Description |
|---------|-------------|
| `echo "text"` | Print a string to stdout |
| `printf "%s\n" "text"` | Formatted output — more portable than echo |
| `sort <file>` | Sort lines alphabetically |
| `sort -n <file>` | Sort lines numerically |
| `sort -rn <file>` | Sort numerically in reverse order |
| `sort -t',' -k2 <file>` | Sort a CSV-style file by its second field |
| `sort -u <file>` | Sort and remove duplicate lines |
| `uniq <file>` | Remove adjacent duplicate lines |
| `uniq -c` | Prefix each unique line with its occurrence count |
| `uniq -d` | Print only duplicate lines |
| `cut -d',' -f1` | Extract the first field from comma-delimited input |
| `cut -d':' -f1,3` | Extract fields 1 and 3 from colon-delimited input |
| `awk '{print $1}'` | Print the first whitespace-delimited field |
| `awk -F',' '{print $2}'` | Print the second field from CSV input |
| `awk '{sum += $1} END {print sum}'` | Sum a column of numbers |
| `awk 'NR>1'` | Skip the first line (header row) |
| `sed 's/old/new/g'` | Global find and replace in a text stream |
| `sed -i 's/old/new/g' <file>` | In-place find and replace on a file |
| `sed '/^#/d'` | Delete lines that start with # (comment lines) |
| `sed -n '10,20p'` | Print only lines 10 through 20 |
| `tr 'a-z' 'A-Z'` | Translate characters — here lowercase to uppercase |
| `tr -d '\r'` | Strip Windows carriage-return characters |
| `xargs` | Build and execute commands from stdin arguments |
| `tee <file>` | Write stdout to both a file and the terminal simultaneously |
| `diff <f1> <f2>` | Show line-by-line differences between two files |

```bash
## Count unique IP addresses in a web server access log
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20

## Replace a hostname across all nginx virtual-host configs
sed -i 's/old.example.com/new.example.com/g' /etc/nginx/sites-available/*.conf

## Extract the second column from a CSV, skipping the header row
tail -n +2 data.csv | cut -d',' -f2
```

## Networking and Remote Access

This section of the linux commands cheatsheet covers connectivity diagnostics, file transfer, and remote operations.

For a deep dive into HTTP from the shell, the [curl Command: The Complete Guide for Developers](/guides/curl-command-guide/) covers every flag with real examples.

| Command | Description |
|---------|-------------|
| `ip addr` | Show all network interfaces with their IP addresses |
| `ip route` | Print the kernel routing table |
| `ip link` | Show link-layer states of all interfaces |
| `ping -c 4 <host>` | Send 4 ICMP echo packets to test reachability |
| `traceroute <host>` | Trace the hop-by-hop network path to a host |
| `mtr <host>` | Combined ping and traceroute with live packet loss stats |
| `curl <url>` | Fetch a URL over HTTP or HTTPS |
| `curl -I <url>` | Fetch only the HTTP response headers |
| `curl -o <file> <url>` | Save the response body to a named file |
| `curl -u user:pass <url>` | Send HTTP Basic authentication credentials |
| `wget <url>` | Download a file to the current directory |
| `wget -P <dir> <url>` | Download a file to a specific directory |
| `wget -c <url>` | Resume an interrupted download |
| `netstat -tlnp` | Show TCP listening sockets and their owning processes |
| `ss -tlnp` | Modern, faster replacement for netstat |
| `ss -s` | Summary statistics for all socket types |
| `nmap -sV <host>` | Scan open ports and identify running services |
| `dig <domain>` | Full DNS query showing all answer records |
| `nslookup <domain>` | Quick DNS lookup (interactive mode also available) |
| `host <domain>` | Lightweight DNS resolution |
| `ssh user@host` | Open a secure interactive shell on a remote machine |
| `ssh -L 8080:localhost:80 user@host` | Forward local port 8080 to remote port 80 |
| `ssh -N -f -L 5432:db:5432 user@host` | Background tunnel to a remote database |
| `scp <src> user@host:<dst>` | Securely copy a file to a remote host |
| `rsync -avz <src>/ <dst>/` | Efficient directory sync with compression |
| `rsync -avz --delete src/ user@host:dst/` | Mirror a local directory to a remote host |

```bash
## Find which process is listening on port 3000
ss -tlnp | grep ':3000'

## Call a JSON API and pretty-print the response
curl -s -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' | python3 -m json.tool

## Sync project files to a remote server, excluding large directories
rsync -avz --exclude='.git' --exclude='node_modules' \
  ./myproject/ deploy@192.168.1.10:/var/www/myproject/
```

## System Services and Monitoring

Systemd is the standard init system on modern Linux. These terminal commands manage services and track system resource health.

| Command | Description |
|---------|-------------|
| `systemctl status <svc>` | Show service status and the most recent log lines |
| `systemctl start <svc>` | Start a stopped service |
| `systemctl stop <svc>` | Stop a running service |
| `systemctl restart <svc>` | Stop and immediately restart a service |
| `systemctl reload <svc>` | Signal the service to reload its config without restarting |
| `systemctl enable <svc>` | Enable the service to start automatically at boot |
| `systemctl disable <svc>` | Disable autostart at boot |
| `systemctl list-units --type=service` | List all loaded service units and their states |
| `journalctl -u <svc>` | View all logs for a named service |
| `journalctl -u <svc> -f` | Stream live log output from a service |
| `journalctl -u <svc> --since "1 hour ago"` | Show only the last hour of a service's logs |
| `journalctl -b` | Show all logs from the current boot |
| `free -h` | Display RAM and swap usage in human-readable units |
| `vmstat 1 5` | Print CPU, memory, and I/O statistics every second, 5 times |
| `iostat -xz 1` | Per-device I/O utilisation statistics |
| `lscpu` | Print detailed CPU architecture information |
| `lsblk` | Show the block device tree |
| `lsof -p <pid>` | List files and sockets open by a specific process |
| `lsof -i :80` | Show which process is bound to port 80 |
| `uptime` | System uptime and 1/5/15-minute load averages |
| `uname -r` | Print the running kernel release version |
| `hostnamectl` | Show and optionally set the system hostname |

```bash
## Auto-restart nginx if it is not running
systemctl is-active nginx || systemctl restart nginx

## Stream live logs from an application service
journalctl -u myapp.service -f

## Watch memory and load update every 2 seconds
watch -n 2 'free -h && uptime'
```

## Archive, Compression, and Package Management

Managing archives and packages are essential day-to-day bash commands on any Linux system.

| Command | Description |
|---------|-------------|
| `tar -czf out.tar.gz dir/` | Create a gzip-compressed tar archive |
| `tar -cjf out.tar.bz2 dir/` | Create a bzip2-compressed tar archive |
| `tar -cJf out.tar.xz dir/` | Create an xz-compressed tar archive (smaller) |
| `tar -xzf archive.tar.gz` | Extract a gzip tar archive in the current directory |
| `tar -xzf archive.tar.gz -C /target` | Extract a gzip archive to a specific directory |
| `tar -tzf archive.tar.gz` | List the contents of an archive without extracting |
| `zip -r out.zip dir/` | Create a zip archive of a directory |
| `unzip archive.zip` | Extract a zip archive |
| `unzip -l archive.zip` | List the contents of a zip file |
| `gzip <file>` | Compress a file in place, replacing the original |
| `gunzip <file>.gz` | Decompress a gzip file |
| `xz <file>` | Compress a file with xz (high compression ratio) |
| `apt update` | Refresh the local package index (Debian / Ubuntu) |
| `apt install <pkg>` | Install a package and its dependencies |
| `apt remove <pkg>` | Remove an installed package |
| `apt upgrade` | Upgrade all installed packages to their latest versions |
| `apt search <term>` | Search available packages by keyword |
| `dpkg -l` | List all installed packages |
| `rpm -qa` | List all installed packages (RHEL / CentOS / Fedora) |
| `dnf install <pkg>` | Install a package on RHEL 8+ or Fedora |
| `snap install <pkg>` | Install a snap package |

```bash
## Create a timestamped backup archive
tar -czf "backup-$(date +%Y%m%d-%H%M%S).tar.gz" /opt/myapp

## Extract one specific file from a large archive
tar -xzf archive.tar.gz path/to/config.conf

## Install a package and immediately check its version
apt install -y htop && htop --version
```

## Bash Scripting and Shell Productivity Tips

Mastering these features of the bash shell turns the terminal into a fast, scriptable automation environment. This section doubles as a compact linux tutorial on scripting essentials.

| Command / Feature | Description |
|-------------------|-------------|
| `export VAR=value` | Set an environment variable for the current session and its children |
| `env` | List all environment variables in the current session |
| `printenv VAR` | Print the value of a single environment variable |
| `unset VAR` | Remove an environment variable |
| `source ~/.bashrc` | Reload the shell configuration file without starting a new shell |
| `alias ll='ls -la'` | Define a shortcut for a commonly used command |
| `unalias <name>` | Remove a previously defined alias |
| `history` | Show the full command history |
| `history 50` | Show the most recent 50 commands |
| `!<n>` | Re-run command number n from the history list |
| `!!` | Repeat the last command verbatim |
| `!$` | Expand to the last argument used in the previous command |
| `Ctrl+R` | Reverse-search through command history interactively |
| `Ctrl+C` | Send SIGINT to interrupt the running command |
| `Ctrl+Z` | Suspend the foreground process and return to the shell |
| `Ctrl+D` | Send EOF — exits a shell session or interactive tool |
| `Ctrl+L` | Clear the terminal screen |
| `Ctrl+A` / `Ctrl+E` | Move the cursor to the start or end of the current line |
| `set -e` | Abort the script immediately on any non-zero exit code |
| `set -u` | Treat references to unset variables as errors |
| `set -o pipefail` | Propagate pipeline errors through each stage |
| `$?` | Exit status code of the most recent command |
| `$#` | Number of positional arguments passed to the script |
| `$@` | All positional arguments as separate quoted words |
| `${VAR:-default}` | Substitute the default value when VAR is unset or empty |
| `$(command)` | Command substitution — run a command and capture its stdout |
| `>file` | Redirect stdout to a file, overwriting any existing content |
| `>>file` | Redirect stdout to a file, appending to existing content |
| `2>&1` | Redirect stderr to the same destination as stdout |
| `&>file` | Redirect both stdout and stderr to a file |
| `cmd1 \| cmd2` | Pipe stdout of cmd1 into stdin of cmd2 |
| `cmd1 && cmd2` | Run cmd2 only if cmd1 exits with status 0 |
| `cmd1 \|\| cmd2` | Run cmd2 only if cmd1 exits with a non-zero status |
| `strace <cmd>` | Trace every system call a command makes |

For comprehensive language reference, the [GNU Bash Manual](https://www.gnu.org/software/bash/manual/bash.html) is the authoritative guide to all shell built-ins and scripting constructs. The [Linux man pages](https://man7.org/linux/man-pages/) document every command and system call in precise detail.

```bash
#!/usr/bin/env bash
set -euo pipefail

## Minimal backup script with safe defaults
BACKUP_DIR="${BACKUP_DIR:-/var/backups/myapp}"
APP_DIR="/opt/myapp"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "${BACKUP_DIR}/backup-${TIMESTAMP}.tar.gz" "$APP_DIR"
echo "Backup complete: ${BACKUP_DIR}/backup-${TIMESTAMP}.tar.gz"
```

```bash
## Loop over a list of hosts and check a service on each
for host in web1 web2 web3; do
  ssh "$host" 'systemctl is-active nginx && echo OK || echo FAILED'
done

## Read a file line by line safely
while IFS= read -r line; do
  echo "Processing: $line"
done < servers.txt

## Check whether a tool is installed before using it
command -v docker >/dev/null 2>&1 && echo "Docker found" || echo "Docker not installed"
```

This linux commands cheatsheet covers the bash commands and terminal commands that developers and sysadmins reach for every day. For version control at the command line, the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet/) is a natural companion. If you run containers on Linux, the [Docker Commands Cheat Sheet](/cheatsheets/docker-commands-cheatsheet/) extends this reference into container and image management.
