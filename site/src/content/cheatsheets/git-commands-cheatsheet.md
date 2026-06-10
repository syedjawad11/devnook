---
title: "Git Commands Cheat Sheet"
description: "The complete git commands cheat sheet: setup, staging, branching, merging, remotes, stashing, history, undoing, and recovery — all in one place."
category: "cheatsheets"
template_id: "cheatsheet-v2"
tags:
  - git
  - version-control
  - cheatsheet
  - commands
  - developer-tools
related_posts: []
related_tools: []
published_date: "2026-06-10"
og_image: "/og/cheatsheets/git-commands-cheatsheet.png"
downloadable: true
---

Git commands grouped by workflow phase — setup, staging, branching, merging, remotes, stashing, history, and recovery. Every command is standard Git with no external dependencies. Git models history as a directed acyclic graph (DAG) of snapshots: commits point to their parents, branches are lightweight moveable pointers, and the staging area is an explicit intermediate layer between the working tree and permanent history. Scan the section headers and jump to the phase that matches what you are doing right now.

## Setup and Configuration

Global settings write to `~/.gitconfig` and apply to every repository on this machine. Use `--local` to scope a setting to a single repo — useful when work and personal projects need different author emails.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global core.editor "code --wait"       # VS Code as default editor
git config --global init.defaultBranch main
git config --global pull.rebase false               # merge on pull (safer default)
git config --global merge.conflictstyle diff3       # show base in conflict markers
git config --global core.autocrlf input             # normalize line endings on macOS/Linux

git config --list                                   # view all active settings
git config --list --show-origin                     # settings plus the file that set each one
git config user.name                                # inspect a single value
git config --global --unset core.editor             # remove a global setting
git config --global alias.st status                 # alias: git st = git status
git config --global alias.lg "log --oneline --graph --all"
```

Initialize or clone a repository:

```bash
git init                                            # create repo in current directory
git init my-project                                 # create repo in my-project/
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git my-dir   # clone into a named folder
git clone --depth 1 https://github.com/user/repo.git    # shallow clone, latest commit only
git clone --branch develop https://github.com/user/repo.git  # clone a specific branch
git clone --bare https://github.com/user/repo.git   # bare clone (no working tree)
```

## Git Commands for Daily Workflow

Git's staging area (the index) is an explicit layer between the working tree and committed history. Stage only the changes that belong together — use `git add -p` to pick individual hunks when a file contains multiple unrelated edits.

### Staging and Committing

```bash
git status                                          # show working tree and index state
git status -s                                       # short format (M = modified, ?? = untracked)
git status --porcelain                              # machine-readable output for scripting

git add file.txt                                    # stage a specific file
git add src/components/                             # stage an entire directory
git add .                                           # stage all changes in current directory
git add -p                                          # interactively select hunks to stage
git add -u                                          # stage all tracked modified and deleted files
git add -N file.txt                                 # intent-to-add (file appears in diff before staging)

git commit -m "Add login form"                      # commit staged changes
git commit -am "Fix typo"                           # stage tracked files then commit in one step
git commit --amend                                  # edit last commit message (before pushing only)
git commit --amend --no-edit                        # add staged changes to last commit, keep message
git commit --allow-empty -m "Trigger CI"            # empty commit (useful for pipeline triggers)
```

Write commit messages in imperative mood ("Add login form") and keep the first line under 72 characters so it renders cleanly in `git log --oneline` and pull-request interfaces.

### Comparing Changes

`git diff` without arguments shows only unstaged changes. When everything is already staged, use `--staged` to preview what will actually land in the next commit.

```bash
git diff                                            # unstaged changes (working tree vs index)
git diff --staged                                   # staged changes (index vs last commit)
git diff HEAD                                       # all changes since last commit
git diff branch1..branch2                           # diff between two branch tips
git diff branch1...branch2                          # diff since common ancestor
git diff --stat                                     # changed files and line-count summary
git diff --name-only                                # list changed file paths only
git diff v1.0..v1.1 -- src/                        # diff between tags, scoped to a directory
```

Use the [Diff Viewer tool](/tools/diff-viewer/) for a side-by-side visual comparison when reviewing changes outside the terminal.

## Branching and Switching

Branches are lightweight moveable pointers — creating one is instantaneous and switching is near-instant. Use a branch for every feature, bug fix, or experiment; merge or discard when done. `git switch` (Git 2.23+) is the preferred command for branch operations; `git checkout` still works but its overloaded behavior makes it error-prone when switching is all you need.

```bash
git branch                                          # list local branches
git branch -a                                       # list local and remote tracking branches
git branch -v                                       # each branch with its latest commit
git branch -vv                                      # branches with upstream tracking info
git branch feature/login                            # create a branch at HEAD
git branch feature/login abc1234                    # create a branch at a specific commit
git branch -d feature/login                         # delete a merged branch
git branch -D feature/login                         # force-delete (even if unmerged)
git branch -m old-name new-name                     # rename a branch locally

git switch feature/login                            # switch to a branch (Git 2.23+)
git switch -c feature/signup                        # create and switch in one step
git switch -c feature/signup origin/signup          # create local branch from remote tracking
git checkout feature/login                          # legacy: switch to branch
git checkout -b feature/signup                      # legacy: create and switch
```

## Merging, Rebasing, and Cherry-Picking

Merge preserves complete history topology including branch points and merge commits. Rebase rewrites commits onto a new base for a linear history that is easier to follow. Never rebase a branch that others have already pulled — rewriting shared commits forces reconciliation on every other copy.

**Merge commands:**

```bash
git merge feature/login                             # merge into current branch
git merge --no-ff feature/login                     # always create a merge commit
git merge --squash feature/login                    # squash all branch commits into one staged change
git merge --abort                                   # cancel an in-progress merge
```

**Rebase commands:**

```bash
git rebase main                                     # rebase current branch onto main
git rebase -i HEAD~3                                # interactive: squash, reword, reorder, drop
git rebase --onto main feature base                 # transplant commits to a different base
git rebase --abort                                  # cancel an in-progress rebase
git rebase --continue                               # continue after resolving a conflict
```

**Cherry-pick commands:**

```bash
git cherry-pick abc1234                             # copy one commit onto the current branch
git cherry-pick abc1234..def5678                    # copy a range of commits
git cherry-pick --no-commit abc1234                 # apply changes without creating a commit
git cherry-pick --abort                             # cancel an in-progress cherry-pick
```

Choose the right strategy for each situation:

| Scenario | Best Approach | Why |
|----------|---------------|-----|
| Feature branch to shared main | `merge --no-ff` | Preserves branch topology in history |
| Cleaning up local commits before PR | `rebase -i` | Linear history, no shared impact |
| Keeping feature branch current | `rebase main` | Avoids merge commit noise |
| Applying a targeted fix across branches | `cherry-pick` | Copies only the required commit |
| Hotfix into a release branch | Cherry-pick or merge | Depends on release branching model |

## Remote Repository Commands

`git fetch` downloads remote commits and refs without touching your working tree — safe to run at any time. `git pull` is fetch followed by merge (or rebase with `--rebase`). Running fetch first and reviewing before merging gives you full control over what lands on your branch.

```bash
git remote -v                                       # list remotes with URLs
git remote add origin https://github.com/user/repo.git
git remote rename origin upstream                   # rename a remote
git remote remove upstream                          # remove a remote
git remote set-url origin https://...               # update a remote URL
git remote show origin                              # detailed info about a remote

git fetch origin                                    # download new commits, do not apply
git fetch --all                                     # fetch from all remotes
git fetch origin --prune                            # remove stale tracking refs

git pull                                            # fetch and merge from tracked upstream
git pull --rebase                                   # fetch and rebase (cleaner, no merge commit)
git pull origin main                                # pull a specific branch explicitly

git push origin main                                # push branch to remote
git push -u origin feature/login                    # push and set upstream tracking ref
git push --force-with-lease                         # safe force-push (fails if remote has new commits)
git push origin --delete feature/old                # delete a remote branch
git push origin --tags                              # push all tags to remote
```

For programmatic interaction with remote HTTP endpoints, see the [curl Command guide](/guides/curl-command-guide/).

## Stashing Work in Progress

The stash is a stack. `git stash pop` applies and removes the top entry; `git stash apply` keeps the entry so you can re-apply it. Label stashes with `push -m` when juggling several tasks — the default `stash@{0}` numbering shifts every time you push a new entry, making unlabeled stashes hard to identify later.

```bash
git stash                                           # stash working tree and index changes
git stash push -m "WIP: login form validation"      # stash with a descriptive label
git stash push -u                                   # stash including untracked files
git stash push -a                                   # stash everything including ignored files
git stash list                                      # list all stash entries
git stash show stash@{0}                            # summary of a stash entry
git stash show -p stash@{0}                         # full diff of a stash entry
git stash pop                                       # apply latest stash and remove it from list
git stash apply stash@{1}                           # apply a specific stash, keep it in list
git stash drop stash@{0}                            # delete a specific stash entry
git stash clear                                     # delete all stash entries
git stash branch feature/stashed                    # create a branch from the latest stash
```

## Viewing History and Searching

`git log` is most powerful when flags are combined: `--oneline --graph --all` renders a full ASCII branch diagram across every ref. Use `--follow` when tracking a renamed file — without it, log stops at the rename boundary.

**Commit log:**

```bash
git log                                             # full log: author, date, message, SHA
git log --oneline                                   # one line per commit (short SHA)
git log --oneline --graph --all                     # ASCII branch and merge graph for all refs
git log -n 10                                       # last 10 commits only
git log --author="Name"                             # filter by author name
git log --since="2 weeks ago"                       # filter by date range
git log --grep="fix"                                # filter by commit message keyword
git log -p file.txt                                 # patches for a specific file
git log --follow file.txt                           # track a file through renames
git log --stat                                      # files changed and line counts per commit
git log --no-merges --oneline                       # exclude merge commits
```

**Inspect a specific commit or file state:**

```bash
git show abc1234                                    # full diff of a commit
git show HEAD~2                                     # commit two steps back
git show HEAD~2:src/app.js                          # file content at a specific commit
```

**Search tracked files:**

```bash
git grep "function authenticate"                    # search the working tree
git grep "TODO" -- "*.ts"                           # search within specific file types
git grep -n "api_key"                               # results with line numbers
```

**Blame and binary-search for regressions:**

`git bisect` performs a binary search through commits to isolate the exact commit that introduced a bug — efficient even across thousands of commits.

```bash
git blame file.txt                                  # last commit to touch each line
git blame -L 10,30 file.txt                         # limit blame to a line range
git blame --ignore-rev abc1234 file.txt             # skip a known reformatting commit

git bisect start                                    # begin a bisect session
git bisect bad                                      # mark current commit as broken
git bisect good v1.0.0                              # mark the last known-good commit
git bisect good                                     # mark this checkout as OK (Git advances)
git bisect bad                                      # mark this checkout as broken (Git narrows)
git bisect reset                                    # end session and return to original HEAD
```

## Undoing Changes and Recovering Lost Work

Match the undo tool to where the change currently lives. `git restore` handles working-tree and index edits; `git reset` rewinds local commits that have not been shared; `git revert` safely reverses a commit already on a shared remote; `git reflog` recovers seemingly lost work.

**Discard unstaged changes** (irreversible — no commit snapshot exists):

```bash
git restore file.txt                                # discard working-tree changes in one file
git restore .                                       # discard all unstaged changes
```

**Unstage** (keeps changes in the working tree):

```bash
git restore --staged file.txt                       # move file from index back to working tree
git restore --staged .                              # unstage everything
```

**Reset commits** (rewrites local history — avoid on pushed commits):

```bash
git reset --soft HEAD~1                             # undo last commit, keep changes staged
git reset --mixed HEAD~1                            # undo last commit, unstage changes (default)
git reset --hard HEAD~1                             # undo last commit, discard changes entirely
```

**Revert** (adds an inverse commit — safe for shared history):

```bash
git revert abc1234                                  # reverse a specific commit
git revert HEAD                                     # reverse the last commit
git revert HEAD~3..HEAD                             # revert a range of commits
```

**Reflog** — last resort for recovering work that looks permanently lost:

```bash
git reflog                                          # every HEAD movement for the last 90 days
git reflog show feature/login                       # reflog for a specific branch
git checkout abc1234                                # detach HEAD at a recovered SHA
git branch recovered-branch abc1234                 # create a branch at a recovered SHA
```

Choose the right approach based on where the change is:

| Situation | Command | Notes |
|-----------|---------|-------|
| Unstaged working-tree edit | `git restore` | Instant; discards permanently (not committed) |
| File accidentally staged | `git restore --staged` | Moves back to working tree, edits preserved |
| Committed but not yet pushed | `git reset` | Rewrites local history only |
| Committed and pushed to shared remote | `git revert` | Safe — adds inverse commit |
| Branch deleted or hard-reset too far | `git reflog` | Recoverable for 90 days by default |

## Tags and Releases

Tags mark specific commits as significant — typically release points. Lightweight tags are plain refs with no metadata; annotated tags (`-a`) store the author, date, and message, making them the standard for public releases. Tags are not pushed automatically with `git push`; push them explicitly.

```bash
git tag                                             # list all tags
git tag v1.0.0                                      # lightweight tag at HEAD
git tag -a v1.0.0 -m "Release 1.0.0"               # annotated tag with a message
git tag -a v1.0.0 abc1234 -m "Tag a past commit"   # annotated tag at a specific SHA
git show v1.0.0                                     # show tag metadata and tagged commit

git push origin v1.0.0                              # push a single tag
git push origin --tags                              # push all tags to remote
git fetch --tags                                    # fetch all remote tags locally

git tag -d v1.0.0                                   # delete tag locally
git push origin --delete v1.0.0                     # delete tag on remote

git tag | sort -V                                   # list tags in semantic version order
git describe --tags                                 # nearest tag, offset count, and SHA
git describe --tags --abbrev=0                      # nearest tag name only
git checkout v1.0.0                                 # detach HEAD at a tagged commit (read-only)
```

## Quick Reference and Useful One-Liners

Less-common commands that save time once you know them.

**File and change inspection:**

```bash
git diff HEAD~1 HEAD -- file.txt                    # changes introduced by the last commit for one file
git log --all --full-history -- deleted-file.txt    # find history of a deleted file
git show HEAD~2:src/app.js                          # file content as it was two commits ago
git ls-files --others --exclude-standard            # list untracked files
git ls-files -d                                     # list tracked files deleted from working tree
```

**Contributor summaries and cleanup:**

```bash
git shortlog -sn                                    # commit count by author, sorted
git log --format="%ae" | sort | uniq -c | sort -rn  # commit counts by email
git clean -n                                        # dry run: show what git clean would remove
git clean -fd                                       # delete untracked files and directories
git gc                                              # garbage collect (compress objects)
```

**Navigation and branch helpers:**

```bash
git rev-parse HEAD                                  # print current commit SHA
git rev-parse --abbrev-ref HEAD                     # print current branch name
git log --merges --oneline                          # list only merge commits
git log --no-merges --oneline                       # exclude merge commits
git stash show -p | git apply --reverse             # undo a stash that was already applied
```

The [Hash Generator tool](/tools/hash-generator/) generates SHA checksums for file verification — useful when auditing artifact hashes in CI/CD pipelines.

For a broader terminal reference, see the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet/) and the [Docker Commands Cheat Sheet](/cheatsheets/docker-commands-cheatsheet/) for container workflows.

For the authoritative command reference and in-depth explanations, see the [Git documentation](https://git-scm.com/docs) and the free online [Pro Git book](https://git-scm.com/book/en/v2).
