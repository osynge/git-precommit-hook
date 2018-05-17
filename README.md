# git-precommit-hook
A pre-commit hook is a piece of code that runs before every commit and determines whether or not the commit should be accepted. Think of it as the gatekeeper to your codebase.

## Introduction

Want to ensure you did not accidentally leave any PDBs in your code? Pre-commit hook. Want to make sure your javascript is JSHint approved? Pre-commit hook. Want to guarantee clean, readable PEP8-compliant code? Pre-commit hook.

## Why Most Pre-Commit Hooks are Wrong

The majority of pre-commit hooks on the web are wrong. Most test against whatever files are currently on disk, not what is in the staging area (the files actually being committed).

This hook uses 'git stash' for changes that are not part of the staging area before running checks and then popping the changes afterwards. This is very important because a file could be fine on disk while the changes that are being committed maybe wrong.

## Credit

The code is derived from the work shown here:

    https://dzone.com/articles/why-your-need-git-pre-commit

If you do not want to invoke this git hook use:

    git commit --no-verify

## Usage

The pre-commit hook is just an executable file that runs before every commit. If it exits with zero status, the commit is accepted. If it exits with a non-zero status, the commit is rejected. (Note: A pre-commit hook can be bypassed by passing the --no-verify argument.)

### Git hooks directory

    .git/hooks

Along with the pre-commit hook there are numerous other git hooks that are available: post-commit, post-merge, pre-receive, and others that can be found in the git hoo.

This hook is simply a set of checks to be run against any files that have been modified in this commit. Each check can be configured to include/exclude particular types of files. It is designed for a Django environment, but should be adaptable to other environments with minor changes. Note that you need git 1.7.7+
