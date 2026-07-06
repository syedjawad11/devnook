---
title: "SSH Command Guide: Ports, Keys, and Tunneling Explained"
description: "Learn how to configure SSH port, set up SSH keys, and use SSH port forwarding for secure tunneling. Commands, config examples, and security tips included."
category: guides
subcategory: DevOps & Infrastructure
template_id: guide-v2
tags: [ssh, linux, devops, networking, security]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-06"
og_image: "/og/guides/ssh-command-guide.png"
actual_word_count: 2547
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Article", "FAQPage"],
    "headline": "SSH Command Guide: Ports, Keys, and Tunneling Explained",
    "description": "Learn how to configure SSH port, set up SSH keys, and use SSH port forwarding for secure tunneling. Commands, config examples, and security tips included.",
    "datePublished": "2026-07-06",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/guides/ssh-command-guide/",
    "mainEntity": [
      {"@type": "Question", "name": "What is the default SSH port?", "acceptedAnswer": {"@type": "Answer", "text": "The default SSH port is 22, assigned by IANA. To change it, edit /etc/ssh/sshd_config and update the Port directive, then restart sshd with sudo systemctl restart sshd."}},
      {"@type": "Question", "name": "How do I set up SSH key authentication?", "acceptedAnswer": {"@type": "Answer", "text": "Generate a key pair with ssh-keygen -t ed25519, then copy the public key to the server using ssh-copy-id user@server. The private key stays on your local machine; the public key is appended to ~/.ssh/authorized_keys on the server."}},
      {"@type": "Question", "name": "What is SSH port forwarding used for?", "acceptedAnswer": {"@type": "Answer", "text": "SSH port forwarding tunnels TCP traffic through an encrypted SSH connection. Local forwarding (-L) lets you access a remote service on a local port. Remote forwarding (-R) exposes a local service on the server. Dynamic forwarding (-D) creates a SOCKS proxy for routing traffic through the server."}}
    ]
  }
  </script>
---

SSH is the tool you will reach for every time you log into a remote server, transfer files, or build a secure tunnel between machines. It handles authentication, encryption, and SSH port forwarding in a single command-line interface. This guide walks through the core mechanics — SSH port configuration, key-based authentication, tunneling, and the SSH config file — with working commands and concrete examples for each.

## SSH Port: Default, Custom, and Why It Matters

Every SSH connection targets a specific port on the remote host. The standard is **port 22**, reserved by the [Internet Assigned Numbers Authority (IANA)](https://www.iana.org/assignments/service-names-port-numbers/) as the SSH port number since 1995. When you run `ssh user@server` without specifying a port, your client connects to port 22 automatically.

Many administrators change the default SSH port away from 22. The motivation is not pure security through obscurity — SSH on port 2222 is still SSH, and a determined scanner will find it. The practical value is noise reduction: automated brute-force bots almost exclusively target port 22, so running on a different port cuts authentication log spam and reduces exposure to credential-stuffing attacks.

To change the SSH port on a Linux server, open `/etc/ssh/sshd_config` in a text editor:

```bash
Port 2222
```

Restart the service to apply the change:

```bash
sudo systemctl restart sshd
```

When connecting to a non-default port, pass the `-p` flag to the `ssh` command:

```bash
ssh -p 2222 user@your-server.com
```

Update your firewall rules before changing the port — allow the new port and optionally block the old one. Lock yourself out and you will need out-of-band console access to recover.

### Checking Which Port SSH Is Listening On

Run this on the server to confirm the active listening port:

```bash
sudo ss -tlnp | grep sshd
```

You should see output showing `LISTEN` on the configured port, such as `0.0.0.0:2222`. If nothing appears, the sshd service is not running.

You can also check the current sshd configuration without restarting:

```bash
sudo sshd -T | grep -i port
```

## How SSH Authentication Works

SSH supports two primary authentication methods: **password-based** and **key-based**. Key-based authentication is the standard for any server that matters.

With password authentication, the client sends a password over the encrypted channel on every connection. With key authentication, the client holds a private key that cryptographically proves identity — no password traverses the network at all (though you should protect your private key with its own passphrase).

The key authentication protocol flow:

1. Client connects and announces which public key it wishes to authenticate with.
2. Server checks whether that public key appears in `~/.ssh/authorized_keys`.
3. Server encrypts a random challenge using the public key and sends it to the client.
4. Client decrypts the challenge with the corresponding private key and sends back a signed response.
5. Server verifies the signature. If it matches, authentication succeeds.

The private key never leaves your machine. The server stores only the public key, which has no value without the corresponding private key.

## Setting Up SSH Keys

### Generating a Key Pair

Ed25519 is the recommended algorithm today — it produces smaller keys, signs faster, and is considered more secure than older RSA 2048 keys:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

You will be prompted for:
- A file path (default `~/.ssh/id_ed25519` — press Enter to accept)
- An optional passphrase (use one for any key that protects production access)

This creates two files:

```
~/.ssh/id_ed25519       # private key — never share, never commit to version control
~/.ssh/id_ed25519.pub   # public key — safe to share with servers
```

For environments requiring RSA (some older servers or services):

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### Copying the Public Key to a Server

The `ssh-copy-id` command appends your public key to the server's `authorized_keys` file in a single step:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server.com
```

If `ssh-copy-id` is not available on your system, do it manually:

```bash
cat ~/.ssh/id_ed25519.pub | ssh user@your-server.com \
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### Fixing Permission Errors

Incorrect permissions on `~/.ssh` are the most common reason key authentication fails silently — the server still prompts for a password even though the key is present. Set permissions correctly on the server:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

OpenSSH refuses to use an `authorized_keys` file that is world-readable, and it does so silently unless you enable verbose logging.

### Verifying the Key Fingerprint

Before trusting a server's host key, verify its fingerprint against a known-good value (obtainable from the server's console):

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

SSH key fingerprints are SHA-256 hashes of the public key. You can use the [hash generator](/tools/hash-generator/) to cross-check fingerprints manually when working with multiple key formats.

## The SSH Config File: Stop Typing Long Commands

Every time you connect to a server with a custom port, specific identity file, and non-default username, you face a command like:

```bash
ssh -p 2222 -i ~/.ssh/deploy_key deploy@staging.example.com
```

The `~/.ssh/config` file stores named connection profiles that replace this with `ssh staging`:

```bash
Host staging
    HostName staging.example.com
    User deploy
    Port 2222
    IdentityFile ~/.ssh/deploy_key
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host production
    HostName prod.example.com
    User ubuntu
    IdentityFile ~/.ssh/prod_key
```

Set the config file to 600 permissions — SSH ignores it when it is world-readable:

```bash
chmod 600 ~/.ssh/config
```

### Useful SSH Config Directives

| Directive | Purpose |
|-----------|---------|
| `HostName` | Actual server address or IP |
| `User` | Remote username |
| `Port` | SSH port if not 22 |
| `IdentityFile` | Path to private key |
| `ServerAliveInterval` | Keepalive packet interval (seconds) |
| `ServerAliveCountMax` | Max missed keepalives before disconnect |
| `ForwardAgent` | Enable SSH agent forwarding |
| `StrictHostKeyChecking` | Control host key verification |
| `ProxyJump` | Route through a bastion host |

Apply settings globally to all connections with a `Host *` block:

```bash
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519
```

## SSH Port Forwarding and Tunneling

SSH port forwarding tunnels TCP traffic through an encrypted connection. The SSH process listens on a local or remote port and transparently proxies traffic to a destination. Three modes cover most scenarios.

### Local Port Forwarding

Local forwarding exposes a remote service on a local port. The canonical use case is accessing a database that only accepts connections from localhost on the server:

```bash
ssh -L 5432:localhost:5432 user@your-server.com
```

After this connection opens, `psql -h localhost -p 5432` on your machine reaches the remote PostgreSQL instance. The `-L` flag takes the form `local_port:destination_host:destination_port`. The destination is resolved by the SSH server, not by your local machine, so `localhost` refers to the server's own loopback interface.

You can forward to any host the server can reach, not just its own localhost:

```bash
ssh -L 3306:internal-db.example.com:3306 user@bastion.example.com
```

### Remote Port Forwarding

Remote forwarding does the reverse: it exposes a port on the server that tunnels back to something on your local machine. This is useful for sharing a development server with someone who can reach the SSH server but not your workstation:

```bash
ssh -R 8080:localhost:3000 user@your-server.com
```

Anyone connecting to port 8080 on the server is routed to port 3000 on your local machine. To allow external connections (not just localhost on the server), add `GatewayPorts yes` to sshd_config.

### Dynamic Port Forwarding (SOCKS Proxy)

Dynamic forwarding creates a SOCKS5 proxy endpoint on your local machine. Configure a browser or application to use `localhost:1080` as a SOCKS proxy, and all traffic routes through the SSH server:

```bash
ssh -D 1080 user@your-server.com
```

This is the lightweight alternative to a full VPN when you need to access a remote network or route traffic through a trusted server.

### Running Tunnels in the Background

Start a tunnel without opening an interactive session:

```bash
ssh -fNL 5432:localhost:5432 user@your-server.com
```

`-f` forks SSH to the background after authentication; `-N` tells it not to execute a remote command. The tunnel stays alive until you kill the process. To find and stop it:

```bash
ps aux | grep "ssh -fN"
kill <pid>
```

## Common SSH Commands Reference

| Command | What It Does |
|---------|-------------|
| `ssh user@host` | Connect to remote host on port 22 |
| `ssh -p 2222 user@host` | Connect on a custom SSH port |
| `ssh -i ~/.ssh/key user@host` | Authenticate with a specific key |
| `ssh -L 8080:localhost:80 user@host` | Local port forward |
| `ssh -R 9090:localhost:3000 user@host` | Remote port forward |
| `ssh -D 1080 user@host` | Dynamic SOCKS proxy |
| `ssh -A user@host` | Enable SSH agent forwarding |
| `ssh -J bastion user@target` | Jump through a bastion host |
| `ssh -v user@host` | Verbose output (debug connection) |
| `ssh-copy-id user@host` | Copy public key to server |
| `ssh-keygen -t ed25519` | Generate Ed25519 key pair |
| `ssh-keygen -lf key.pub` | Show key fingerprint |
| `scp file user@host:/path` | Secure copy a file to server |
| `sftp user@host` | Interactive SFTP file session |

For a broader command-line reference covering file management, process control, and networking utilities, see the [Linux commands cheat sheet](/cheatsheets/linux-commands-cheatsheet/).

## SSH Security Best Practices

A default OpenSSH install is functional but leaves several attack surfaces open. Apply these settings in `/etc/ssh/sshd_config` to harden the configuration.

**Disable password authentication** once key auth is working:

```bash
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
```

**Disable direct root login**:

```bash
PermitRootLogin no
```

**Restrict access to specific users**:

```bash
AllowUsers deploy alice bob
```

Or use a group if you manage many accounts:

```bash
AllowGroups ssh-users
```

**Limit authentication attempts and idle logins**:

```bash
MaxAuthTries 3
LoginGraceTime 20
ClientAliveInterval 300
ClientAliveCountMax 2
```

Always validate sshd_config syntax before restarting — a syntax error locks everyone out:

```bash
sudo sshd -t
```

If that command exits cleanly, restart safely:

```bash
sudo systemctl restart sshd
```

### Auditing the Negotiated Cipher Suite

OpenSSH ships with sensible modern defaults, but older servers sometimes still negotiate weak ciphers. Check what is actually in use on a connection:

```bash
ssh -vv user@host 2>&1 | grep -E "cipher|MAC|kex"
```

The [OpenSSH project documentation](https://www.openssh.com/) covers the `Ciphers`, `MACs`, and `KexAlgorithms` directives you can add to sshd_config to restrict the negotiation to modern algorithms only.

## Keeping Sessions Alive with tmux

SSH sessions drop when your local network hiccups or your laptop sleeps. Any process running directly in an SSH session dies with the connection.

`tmux` decouples the session from the connection: start a named session on the server, detach from it, then reattach after reconnecting. The processes keep running regardless of how many times the SSH connection drops. See the [tmux cheat sheet](/cheatsheets/tmux-cheatsheet/) for the full command set — `tmux new -s session_name` to start, `Ctrl-b d` to detach, and `tmux attach -t session_name` to reattach.

For file transfers and HTTP calls to the same remote servers, the [curl command guide](/guides/curl-command-guide/) covers patterns that pair well with SSH-based infrastructure work.

## Troubleshooting Common SSH Issues

### Permission Denied (publickey)

The server rejected key authentication. Common causes:

- **Wrong key selected** — specify it explicitly: `ssh -i ~/.ssh/specific_key user@host`
- **Bad permissions on server** — `~/.ssh` must be 700, `authorized_keys` must be 600
- **Wrong username** — check the remote user: `ssh -v user@host` and look for "Offering public key"
- **AuthorizedKeysFile path wrong** — defaults to `~/.ssh/authorized_keys`; verify in sshd_config

Enable verbose output to see exactly where authentication fails:

```bash
ssh -vvv user@host
```

### Connection Timed Out

The server is unreachable on the target port. Test without SSH:

```bash
nc -zv server-ip 22
```

If that fails, the port is blocked by a firewall. Check the server's UFW or iptables rules:

```bash
sudo ufw status
sudo iptables -L -n | grep 22
```

### Host Key Verification Failed

The server's host key changed since your last connection. This is expected after rebuilding a server; it could also indicate a man-in-the-middle attack. If the rebuild is expected, remove the stale key:

```bash
ssh-keygen -R hostname-or-ip
```

Then reconnect — SSH will prompt you to accept and store the new host key.

### SSH Hangs During Connection

Add `-v` to identify where the handshake stalls:

```bash
ssh -v user@host
```

A common hang is the server performing reverse DNS lookup on the client IP. Add `UseDNS no` to sshd_config to skip it and cut connection time significantly on servers with slow or misconfigured DNS.

## Frequently Asked Questions

### What is the default SSH port?

The default SSH port is **22**, reserved by IANA for the Secure Shell protocol. Most servers listen on port 22 unless an administrator has changed it in sshd_config. To connect to a server on a non-default SSH port, use `ssh -p <port> user@host`, or set `Port <port>` in your `~/.ssh/config` for a permanent alias.

### How do I disable SSH password authentication?

Set `PasswordAuthentication no` in `/etc/ssh/sshd_config`, then run `sudo systemctl restart sshd`. Do this only after verifying that key-based authentication works in a separate terminal session — if you disable password auth while holding the only active session, you will lock out future password-based recovery.

### What is the difference between local and remote SSH port forwarding?

Local forwarding (`ssh -L`) creates a listener on your local machine and tunnels traffic to a destination the SSH server can reach — you access a remote service locally. Remote forwarding (`ssh -R`) creates a listener on the remote server and tunnels traffic back to something your local machine can reach. Both run over the same encrypted SSH connection; the direction of the listener is what differs.

### Can I run SSH on multiple ports simultaneously?

Yes. Add multiple `Port` lines in sshd_config:

```bash
Port 22
Port 2222
```

After restarting sshd, the server accepts connections on both ports. This is useful during migration from the default port — keep port 22 open until all clients are updated, then remove it.

### How do I transfer files securely over SSH?

Use `scp` for one-off copies: `scp localfile user@host:/remote/path` to upload, `scp user@host:/remote/file .` to download. For bulk transfers or interactive browsing, `sftp user@host` opens a session where you can use `put`, `get`, `ls`, and `cd`. Both tools use the same SSH authentication and encryption as a regular login session.

## Conclusion

SSH port configuration, key-based authentication, and port forwarding are the three skills that transform SSH from a basic remote login tool into a foundational infrastructure building block. Start by switching to Ed25519 keys and disabling password auth — those two steps eliminate the majority of SSH-related security incidents on internet-facing servers. From there, the config file and tunneling modes give you the flexibility to handle nearly any remote access scenario without exposing additional services to the public internet.

For the definitive reference, the [OpenSSH project](https://www.openssh.com/) maintains authoritative documentation covering every directive and option. The [OpenBSD SSH manual](https://man.openbsd.org/ssh) is the authoritative source for every command-line flag. The [Wikipedia article on Secure Shell](https://en.wikipedia.org/wiki/Secure_Shell) provides useful protocol-level background on the cryptographic design that makes SSH port forwarding and key authentication work the way they do.
