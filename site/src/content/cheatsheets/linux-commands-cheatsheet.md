---
title: "Linux Commands Cheat Sheet"
description: "A comprehensive Linux commands cheat sheet covering file management, permissions, process control, networking, and shell scripting essentials for developers."
category: cheatsheets
template_id: cheatsheet-v3
tags: [linux, bash, terminal, shell, sysadmin, cheatsheet]
related_posts: []
related_tools: []
published_date: "2026-04-25"
og_image: "/og/cheatsheets/linux-commands-cheatsheet.png"
downloadable: true
content_type: editorial
---

The Linux command line gives you direct, scriptable control over every aspect of your system. This reference organises the most-used commands by task — from navigating the file system to diagnosing network issues — across beginner, intermediate, and advanced tiers.

## File System Navigation & Management

### Beginner: Essential Navigation

| Command | Description |
|---------|-------------|
| `pwd` | Print current working directory |
| `ls` | List directory contents |
| `ls -la` | Long listing including hidden files |
| `cd <dir>` | Change directory |
| `cd ..` | Go up one directory |
| `cd ~` | Go to home directory |
| `mkdir <dir>` | Create a directory |
| `mkdir -p a/b/c` | Create nested directories |
| `rm <file>` | Remove a file |
| `rm -rf <dir>` | Recursively remove directory and contents |
| `cp <src> <dst>` | Copy file or directory |
| `mv <src> <dst>` | Move or rename a file |
| `touch <file>` | Create empty file or update timestamp |
| `cat <file>` | Display file contents |
| `less <file>` | Page through file contents |

### Intermediate: Search & Find

| Command | Description |
|---------|-------------|
| `find / -name "*.conf"` | Find files by name pattern |
| `find . -type f -mtime -7` | Files modified in the last 7 days |
| `grep -r "pattern" /path` | Recursive text search in files |
| `grep -i "pattern" file` | Case-insensitive search |
| `locate <name>` | Fast filename search (uses index) |
| `which <command>` | Show full path of a command |
| `du -sh <dir>` | Disk usage of a directory |
| `df -h` | Disk usage of all mounted filesystems |
| `wc -l <file>` | Count lines in a file |

```bash
# Find all .log files larger than 100MB
find /var/log -name "*.log" -size +100M

# Search for "ERROR" in all Python files under current directory
grep -r "ERROR" --include="*.py" .

# Show the 10 largest directories in /var
du -h /var/* | sort -rh | head -10
```

## File Permissions & Ownership

Understanding Linux permissions is critical for security and correct operation.

| Command | Description |
|---------|-------------|
| `chmod 755 <file>` | Set permissions (rwxr-xr-x) |
| `chmod +x <file>` | Add execute permission |
| `chmod -R 644 <dir>` | Recursively set permissions |
| `chown user:group <file>` | Change owner and group |
| `chown -R user <dir>` | Recursively change owner |
| `ls -l` | View file permissions |
| `umask` | Show default permission mask |
| `sudo <command>` | Run command as root |
| `su - <user>` | Switch to another user |

### Permission Notation Quick Reference

| Octal | Symbolic | Meaning |
|-------|----------|---------|
| `7` | `rwx` | Read, write, execute |
| `6` | `rw-` | Read, write |
| `5` | `r-x` | Read, execute |
| `4` | `r--` | Read only |
| `0` | `---` | No permissions |

```bash
# Make a script executable
chmod +x deploy.sh

# Give owner full access, group read/execute, others nothing
chmod 750 /opt/my-app

# Recursively set correct permissions for a web directory
find /var/www -type d -exec chmod 755 {} \;
find /var/www -type f -exec chmod 644 {} \;
```

## Process Management

| Command | Description |
|---------|-------------|
| `ps aux` | List all running processes |
| `top` | Interactive real-time process viewer |
| `htop` | Enhanced interactive process viewer |
| `kill <pid>` | Send SIGTERM to a process |
| `kill -9 <pid>` | Force kill a process (SIGKILL) |
| `killall <name>` | Kill all processes by name |
| `pkill <pattern>` | Kill processes matching a pattern |
| `bg` | Resume a suspended job in background |
| `fg` | Bring background job to foreground |
| `jobs` | List background jobs in current shell |
| `nohup <cmd> &` | Run command immune to hangups |
| `nice -n 10 <cmd>` | Run with lower CPU priority |

```bash
# Find and kill a process by name
kill $(pgrep nginx)

# Run a long process in background, immune to terminal close
nohup python train_model.py > training.log 2>&1 &

# Show top 5 memory-consuming processes
ps aux --sort=-%mem | head -6
```

## Text Processing

These commands form the backbone of shell scripting and log analysis.

| Command | Description |
|---------|-------------|
| `echo "text"` | Print text to stdout |
| `sort <file>` | Sort lines alphabetically |
| `sort -n <file>` | Sort numerically |
| `uniq` | Remove adjacent duplicate lines |
| `cut -d',' -f1` | Extract fields from delimited text |
| `awk '{print $1}'` | Process and extract text fields |
| `sed 's/old/new/g'` | Find and replace in text stream |
| `head -n 20 <file>` | Show first 20 lines |
| `tail -n 20 <file>` | Show last 20 lines |
| `tail -f <file>` | Follow file as it grows |
| `tr 'a-z' 'A-Z'` | Translate characters |
| `xargs` | Build command from stdin input |

```bash
# Count unique IP addresses in a web server log
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20

# Replace all occurrences of old_domain in config files
sed -i 's/old.example.com/new.example.com/g' /etc/nginx/sites-available/*.conf

# Extract the second column from a CSV
cut -d',' -f2 data.csv
```

## Networking Commands

| Command | Description |
|---------|-------------|
| `ip addr` | Show network interfaces and IP addresses |
| `ip route` | Show routing table |
| `ping <host>` | Test connectivity to a host |
| `curl <url>` | Make HTTP requests |
| `wget <url>` | Download files from the web |
| `netstat -tlnp` | Show listening ports and processes |
| `ss -tlnp` | Modern replacement for netstat |
| `nmap <host>` | Scan open ports on a host |
| `traceroute <host>` | Trace network path to a host |
| `dig <domain>` | DNS lookup |
| `nslookup <domain>` | DNS query (interactive) |
| `host <domain>` | Simple DNS lookup |
| `scp user@host:/src /dst` | Secure copy over SSH |
| `rsync -avz src/ dst/` | Sync files efficiently |
| `ssh user@host` | Connect to remote host via SSH |

```bash
# Check which process is listening on port 3000
ss -tlnp | grep :3000

# Download a file and save with its original name
wget -P /tmp https://example.com/archive.tar.gz

# Test an API endpoint
curl -s -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## Advanced: System & Shell Scripting

| Command | Description |
|---------|-------------|
| `env` | Show all environment variables |
| `export VAR=value` | Set an environment variable |
| `source ~/.bashrc` | Reload shell configuration |
| `history` | Show command history |
| `!!` | Repeat last command |
| `!$` | Use last argument of previous command |
| `ctrl+r` | Reverse search through history |
| `crontab -e` | Edit scheduled cron jobs |
| `systemctl status <svc>` | Check a systemd service status |
| `journalctl -u <svc>` | View systemd service logs |
| `tar -czf out.tar.gz dir/` | Create compressed archive |
| `tar -xzf archive.tar.gz` | Extract compressed archive |
| `zip -r out.zip dir/` | Create zip archive |
| `lsof -p <pid>` | List files opened by a process |
| `strace <cmd>` | Trace system calls |

```bash
# Schedule a daily backup at 2 AM
# Add to crontab with: crontab -e
0 2 * * * /opt/scripts/backup.sh >> /var/log/backup.log 2>&1

# Check and restart a failed service
systemctl is-active nginx || systemctl restart nginx

# Extract only specific files from a tar archive
tar -xzf archive.tar.gz path/to/specific/file.txt
```

This cheat sheet covers the Linux commands every developer and sysadmin reaches for daily. The [DevNook guides hub](/guides/) has deeper walkthroughs on shell scripting and system administration. For version control alongside your terminal work, the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet) is a natural companion. Browse the full collection of quick-reference cards at the [cheatsheets hub](/cheatsheets/), or explore [DevNook tools](/tools/) to complement your command-line workflow.
