#!/usr/bin/env bash
# Run this on your own computer (needs git and your GitHub login) from inside this folder.
set -e
git init
git branch -M main
git remote add origin https://github.com/Eshwaar881/BDF-Group-assignment.git 2>/dev/null || true
git add .
git commit -m "Add task 1 to task 6 and complete ToolTown Makerspace API"
git pull origin main --rebase --allow-unrelated-histories || true
git push -u origin main
