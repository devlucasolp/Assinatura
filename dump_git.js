const cp = require('child_process');
const fs = require('fs');
fs.writeFileSync('git_status.txt', cp.execSync('git status').toString());
fs.writeFileSync('git_log.txt', cp.execSync('git log -n 5 --oneline').toString());
fs.writeFileSync('git_diff.txt', cp.execSync('git diff HEAD~5..HEAD').toString());
