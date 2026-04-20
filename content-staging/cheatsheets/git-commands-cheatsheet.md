---
category: cheatsheets
content_type: editorial
description: A complete Git commands cheat sheet covering init, clone, branch, merge,
  rebase, stash, and more. Quick reference for beginners and pros.
downloadable: true
og_image: /og/cheatsheets/git-commands-cheatsheet.png
published_date: '2026-04-20'
related_posts:
- /guides/http-status-codes-guide
- /guides/curl-command-guide
- /blog/sorting-algorithms-comparison
related_tools:
- /tools/diff-viewer
- /tools/hash-generator
tags:
- git
- version-control
- cheatsheet
- commands
- developer-tools
template_id: cheatsheet-v2
title: Git Commands Cheat Sheet
word_count_target: 800
---

# Git Commands Cheat Sheet

Git commands grouped by task — setup, daily workflow, branching, history, and recovery. Every command here is standard Git with no external dependencies.

## Setup and Configuration

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global core.editor "code --wait"   # VS Code as default editor
git config --global init.defaultBranch main

git config --list          # show all config values
git config user.name       # show a single value
```

Initialize or clone a repository:

```bash
git init                   # create new repo in current directory
git init my-project        # create new repo in my-project/
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git target-dir   # clone into specific folder
git clone --depth 1 https://github.com/user/repo.git    # shallow clone (latest commit only)
```

## Daily Workflow

### Staging and Committing

```bash
git status                 # show working tree status
git status -s              # short format

git add file.txt           # stage a specific file
git add src/               # stage a directory
git add .                  # stage all changes in current directory
git add -p                 # interactively stage hunks

git commit -m "message"    # commit staged changes
git commit -am "message"   # stage tracked files + commit in one step
git commit --amend         # edit last commit message (only before pushing)
git commit --amend --no-edit   # add staged changes to last commit, keep message
```

### Viewing Changes

```bash
git diff                   # unstaged changes
git diff --staged          # staged changes (what will be committed)
git diff HEAD              # all changes since last commit
git diff branch1..branch2  # diff between two branches
git diff --stat            # summarize changes (files + line counts)
```

Use the [Diff Viewer tool](/tools/diff-viewer) for a side-by-side visual comparison when reviewing changes between files.

## Branching

```bash
git branch                 # list local branches
git branch -a              # list local + remote branches
git branch feature/login   # create a branch
git branch -d feature/login   # delete merged branch
git branch -D feature/login   # force delete (unmerged OK)
git branch -m old-name new-name   # rename branch

git switch feature/login   # switch to branch (Git 2.23+)
git switch -c feature/signup  # create and switch
git checkout feature/login # older equivalent of git switch
git checkout -b feature/signup  # older equivalent of git switch -c
```

## Merging and Rebasing

```bash
# Merge
git merge feature/login              # merge into current branch
git merge --no-ff feature/login      # force merge commit (no fast-forward)
git merge --squash feature/login     # squash into single staged change
git merge --abort                    # abort in-progress merge

# Rebase
git rebase main                      # rebase current branch onto main
git rebase -i HEAD~3                 # interactive rebase last 3 commits
git rebase --onto main feature base  # transplant commits
git rebase --abort                   # abort in-progress rebase
git rebase --continue                # continue after resolving conflicts
```

When to use each:

| Situation | Prefer |
|-----------|--------|
| Feature branch → main on shared repo | Merge (preserves history) |
| Cleaning up local commits before PR | Rebase -i (squash/reword) |
| Keeping feature branch current | Rebase onto main |
| Hotfix into multiple branches | Cherry-pick |

## Remote Repositories

```bash
git remote -v                        # list remotes
git remote add origin https://...    # add remote
git remote rename origin upstream    # rename remote
git remote remove upstream           # remove remote
git remote set-url origin https://... # change remote URL

git fetch origin                     # download changes, don't merge
git fetch --all                      # fetch all remotes
git pull                             # fetch + merge
git pull --rebase                    # fetch + rebase (cleaner history)

git push origin main                 # push to remote
git push -u origin feature/login     # push + set upstream tracking
git push --force-with-lease          # safe force push (fails if remote changed)
git push origin --delete feature/old # delete remote branch
```

## Stashing

```bash
git stash                            # stash working directory changes
git stash push -m "WIP: login form"  # stash with message
git stash list                       # list stashes
git stash pop                        # apply latest stash + remove it
git stash apply stash@{2}            # apply specific stash, keep it
git stash drop stash@{0}             # delete a stash
git stash clear                      # delete all stashes
git stash branch feature/stashed     # create branch from stash
```

## Viewing History

```bash
git log                              # full log
git log --oneline                    # one line per commit
git log --oneline --graph --all      # ASCII branch graph
git log -n 10                        # last 10 commits
git log --author="Name"              # filter by author
git log --since="2 weeks ago"        # filter by date
git log --grep="fix"                 # filter by commit message
git log -p file.txt                  # show patches for a file
git log --follow file.txt            # follow file renames

git show abc1234                     # show a commit
git show HEAD~2:src/app.js           # show file at specific commit
```

## Undoing Changes

```bash
git restore file.txt                 # discard unstaged changes in file
git restore --staged file.txt        # unstage file (keep changes)
git restore .                        # discard all unstaged changes

git reset HEAD~1                     # undo last commit, keep changes staged
git reset --soft HEAD~1              # undo last commit, keep changes staged
git reset --mixed HEAD~1             # undo last commit, unstage changes (default)
git reset --hard HEAD~1              # undo last commit, discard changes (destructive)

git revert abc1234                   # create new commit that undoes abc1234
git revert HEAD                      # revert last commit
```

**When to use reset vs revert:**
- `git reset`: use for commits that have never been pushed (local history only)
- `git revert`: use for commits that are already on a shared remote — it adds a new commit, preserving history

## Cherry-Picking

```bash
git cherry-pick abc1234              # apply commit to current branch
git cherry-pick abc1234..def5678     # apply a range of commits
git cherry-pick --no-commit abc1234  # apply changes without committing
git cherry-pick --abort              # abort in-progress cherry-pick
```

## Tags

```bash
git tag                              # list tags
git tag v1.0.0                       # lightweight tag on HEAD
git tag -a v1.0.0 -m "Release 1.0"  # annotated tag
git tag -a v1.0.0 abc1234           # tag a specific commit
git push origin v1.0.0              # push tag to remote
git push origin --tags              # push all tags
git tag -d v1.0.0                   # delete local tag
git push origin --delete v1.0.0     # delete remote tag
```

## Searching and Debugging

```bash
git grep "function login"            # search working tree
git grep "TODO" -- "*.js"            # search in specific file types

git blame file.txt                   # show who changed each line
git blame -L 10,20 file.txt          # blame for specific line range

git bisect start                     # start bisect session
git bisect bad                       # mark current commit as bad
git bisect good v1.0.0               # mark known good commit
git bisect reset                     # end bisect session
```

`git bisect` performs a binary search through your commit history to find which commit introduced a bug. Git checks out commits automatically; you mark each as good or bad until it identifies the culprit.

## Useful Shortcuts

```bash
git diff HEAD~1 HEAD -- file.txt     # changes in last commit for a file
git log --all --full-history -- deleted-file.txt  # find deleted file history
git reflog                           # all recent HEAD movements (recovery lifeline)
git shortlog -sn                     # contributor summary by commit count
git rev-parse HEAD                   # get current commit SHA
git ls-files --others --exclude-standard  # list untracked files
```

The [Hash Generator tool](/tools/hash-generator) can verify file integrity by generating SHA checksums — useful when comparing artifact hashes in CI pipelines.

For more on interacting with remote servers programmatically, see the [curl Command guide](/guides/curl-command-guide).