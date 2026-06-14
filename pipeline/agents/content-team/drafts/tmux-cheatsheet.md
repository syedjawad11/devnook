---
title: "tmux Cheat Sheet: Sessions, Windows, Panes and Keys"
description: "tmux cheat sheet covering terminal multiplexing from scratch: sessions, windows, panes, shortcuts, copy mode, and configuration in one place."
category: cheatsheets
template_id: cheatsheet-v1
tags: [tmux, terminal, linux, command-line, productivity]
related_posts: []
related_tools: []
published_date: "2026-06-14"
og_image: "/og/cheatsheets/tmux-cheatsheet.png"
downloadable: true
---

tmux is a terminal multiplexer: it keeps sessions alive after you disconnect, splits the screen into panes, and manages multiple windows in a single terminal. This tmux cheat sheet organizes every command by workflow phase — installation, sessions, windows, panes, copy mode, and configuration. Whether you're new to tmux or looking for a quick reference, start from the top.

## tmux Cheat Sheet: Installation and First Launch

Before the keybindings matter, you need tmux installed and running. Here's how to get it on common platforms:

| Platform | Command |
|----------|---------|
| Ubuntu / Debian | `sudo apt install tmux` |
| macOS (Homebrew) | `brew install tmux` |
| Fedora / RHEL | `sudo dnf install tmux` |
| Arch Linux | `sudo pacman -S tmux` |
| From source | `./configure && make && sudo make install` |

After installation, verify the version to confirm it worked:

```bash
tmux -V
# tmux 3.4 (or similar output)
```

The default prefix key is `Ctrl+b`. Every keybinding below uses `prefix` to mean pressing `Ctrl+b` first, then the letter or symbol that follows. For example, `prefix d` means: press `Ctrl+b`, release, then press `d`.

### Starting tmux

| Command | What It Does |
|---------|-------------|
| `tmux` | Start a new unnamed session |
| `tmux new -s work` | Start a new session named "work" |
| `tmux -u` | Start with UTF-8 support enabled |

## Session Management

A tmux session is a persistent workspace that survives terminal disconnection. You can run multiple sessions simultaneously, each with independent windows and panes. Sessions stay alive as long as the tmux server process is running — typically until you reboot or explicitly kill them.

| Command | What It Does |
|---------|-------------|
| `tmux ls` | List all active sessions |
| `tmux attach` | Attach to the most recent session |
| `tmux attach -t work` | Attach to the session named "work" |
| `tmux kill-session -t work` | Kill the session named "work" |
| `tmux kill-server` | Kill all sessions and stop the tmux server |
| `prefix d` | Detach from the current session (session keeps running) |
| `prefix $` | Rename the current session |
| `prefix s` | Show an interactive session picker |
| `prefix (` | Switch to the previous session |
| `prefix )` | Switch to the next session |
| `prefix L` | Switch to the last (previously used) session |

### Typical session workflow

```bash
# Morning: start a named session
tmux new -s dev

# Work for a while, then detach without killing it
# (inside tmux): prefix d

# Later, list what's running
tmux ls
# dev: 2 windows (created Mon Jun 14 09:00:12 2026) [220x50]

# Reattach — even after an SSH reconnect
tmux attach -t dev
```

Named sessions are worth the habit. When you have `api`, `frontend`, and `infra` sessions running alongside each other, `tmux attach -t api` is faster than rebuilding your working environment from scratch.

## Window Management

Windows inside a session act like browser tabs — each one has its own shell. You can name them to match what you're running, and switch between them without mouse clicks.

| Command | What It Does |
|---------|-------------|
| `prefix c` | Create a new window |
| `prefix ,` | Rename the current window |
| `prefix w` | Show an interactive window picker |
| `prefix n` | Move to the next window |
| `prefix p` | Move to the previous window |
| `prefix 0–9` | Jump directly to window by index |
| `prefix &` | Kill the current window (prompts for confirmation) |
| `prefix .` | Move window to a different index |
| `prefix f` | Search for a window by name |
| `prefix l` | Switch to the last (previously active) window |

### Naming windows by workload

```bash
# Open tmux and create four named windows:
# prefix c  → prefix ,  → type 'server'   → Enter
# prefix c  → prefix ,  → type 'db'       → Enter
# prefix c  → prefix ,  → type 'logs'     → Enter
# prefix c  → prefix ,  → type 'notes'    → Enter

# Navigate by name via the picker:
# prefix w   → arrow keys → Enter

# Or jump directly by index:
# prefix 1  →  server
# prefix 2  →  db
# prefix 3  →  logs
```

The status bar at the bottom of the screen shows your windows by name and highlights the active one. After a few days with named windows, you stop looking at terminal titles entirely.

## Pane Management

Panes split a single window into multiple terminal areas arranged vertically or horizontally. Running a server process in one pane and tailing logs in another — without switching windows — is the main reason developers reach for tmux.

| Command | What It Does |
|---------|-------------|
| `prefix %` | Split pane vertically (left/right) |
| `prefix "` | Split pane horizontally (top/bottom) |
| `prefix o` | Cycle to the next pane |
| `prefix ;` | Toggle between the two most recently active panes |
| `prefix q` | Flash pane index numbers |
| `prefix q 0–9` | Jump to a pane by its index number |
| `prefix x` | Kill the current pane (prompts for confirmation) |
| `prefix z` | Toggle full-screen zoom on the current pane |
| `prefix {` | Swap the current pane with the previous pane |
| `prefix }` | Swap the current pane with the next pane |
| `prefix !` | Break current pane into its own window |
| `prefix Space` | Rotate through built-in pane layouts |
| `prefix Ctrl+arrow` | Resize pane one cell in the arrow direction |
| `prefix Alt+arrow` | Resize pane five cells in the arrow direction |

### Three-pane development setup

```bash
# Start with one window, then build a layout:

# 1. Split vertically — left and right halves
# prefix %

# 2. Move to right pane and split horizontally
# prefix o
# prefix "

# Result:
# +--------------------+----------+
# |                    |  server  |
# |   code editor      +----------+
# |                    |   logs   |
# +--------------------+----------+

# Zoom into the server pane to read output:
# prefix z

# Zoom back out (same key):
# prefix z
```

`prefix z` is one of the most useful pane shortcuts: it temporarily fills the window with the active pane for focus, then restores the layout when pressed again. No resizing needed.

## Copy Mode and Scrollback

tmux keeps a scrollback buffer for each pane. Copy mode lets you navigate it, search for text, and copy selections — all with keyboard shortcuts. By default, keybindings follow emacs conventions; most developers switch to vi mode.

| Command | What It Does |
|---------|-------------|
| `prefix [` | Enter copy mode |
| `q` or `Escape` | Exit copy mode |
| `Arrow keys` | Move cursor one character or line |
| `Ctrl+b` | Scroll up half a page |
| `Ctrl+f` | Scroll down half a page |
| `PgUp / PgDn` | Scroll up / down a full page |
| `g` | Jump to the top of the buffer |
| `G` | Jump to the bottom of the buffer |
| `/` | Search forward |
| `?` | Search backward |
| `n` | Jump to the next search match |
| `N` | Jump to the previous search match |
| `Space` | Start selection (vi mode) |
| `Enter` | Copy selection to the tmux paste buffer |
| `prefix ]` | Paste from the paste buffer into the active pane |

### Enabling vi keybindings in copy mode

Add the following to `~/.tmux.conf` to use familiar vi motions for navigation and selection:

```bash
# Use vi keybindings in copy mode
setw -g mode-keys vi

# v starts selection, y yanks it (like Vim visual mode)
bind -T copy-mode-vi v send-keys -X begin-selection
bind -T copy-mode-vi y send-keys -X copy-selection-and-cancel

# Also copy to the system clipboard (requires xclip on Linux)
bind -T copy-mode-vi y send-keys -X copy-pipe-and-cancel "xclip -in -selection clipboard"
```

With vi mode active: `prefix [` enters copy mode, `v` starts selection, `y` yanks. `prefix ]` pastes. This matches the workflow muscle memory from Vim and Neovim users.

## tmux Configuration

tmux reads `~/.tmux.conf` on startup. The defaults are functional but sparse. The config below covers the most common quality-of-life adjustments:

```bash
# ~/.tmux.conf

# Change prefix from Ctrl+b to Ctrl+a (screen-style, easier to reach)
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# Enable mouse support — click to switch panes and resize
set -g mouse on

# Start window and pane indices at 1 (keyboard layout matches)
set -g base-index 1
setw -g pane-base-index 1

# Renumber windows automatically when one is closed
set -g renumber-windows on

# Reload config inside tmux without restarting
bind r source-file ~/.tmux.conf \; display-message "Config reloaded"

# More intuitive split keybindings
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %

# New windows and panes open in the current directory
bind c new-window -c "#{pane_current_path}"

# Move between panes with vi-style hjkl
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# vi keybindings in copy mode
setw -g mode-keys vi

# Increase scrollback history
set -g history-limit 50000

# Reduce escape-time (critical for Vim/Neovim responsiveness)
set -sg escape-time 10

# Enable 256-color and true-color support
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"

# Status bar
set -g status-position bottom
set -g status-interval 5
```

After saving changes, reload the config from inside a running tmux session:

```bash
tmux source-file ~/.tmux.conf
# Or use prefix r if you added the bind above
```

## Quick Reference: Miscellaneous Commands

| Command | What It Does |
|---------|-------------|
| `prefix ?` | List all active keybindings |
| `prefix :` | Open the tmux command prompt |
| `prefix t` | Show a clock in the current pane |
| `prefix ~` | Show tmux server messages |
| `prefix i` | Display information about the current window |
| `tmux info` | Print full tmux server environment info |
| `tmux show-options -g` | Show all global options |

`prefix ?` is the binding to remember first. It shows the full keybinding list from inside the running session. You don't need to memorize everything on this page — just remember that `prefix ?` puts the reference one keypress away.

## Conclusion

This tmux cheat sheet covers the complete workflow: installing tmux, managing sessions that outlive your SSH connection, organizing work across named windows, splitting panes for parallel visibility, navigating the scrollback buffer in copy mode, and tuning behavior through `~/.tmux.conf`. The session, window, and pane commands handle the vast majority of daily use — the rest you can look up with `prefix ?` or the official [tmux man page](https://man7.org/linux/man-pages/man1/tmux.1.html). For more terminal reference material, the [Linux commands cheatsheet](/cheatsheets/linux-commands-cheatsheet), [Git commands cheatsheet](/cheatsheets/git-commands-cheatsheet), and [Docker commands cheatsheet](/cheatsheets/docker-commands-cheatsheet) cover the tools you're most likely running inside those panes. The [tmux GitHub wiki](https://github.com/tmux/tmux/wiki) is the authoritative source for options not covered here.
