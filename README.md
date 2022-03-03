# GitHub Quick Blocker
Review & block users posting annoying issues (and comments) in a GitHub repository.

## Usage
### Start
```bash
python main.py -u <username> -t <GitHub OAuth token> -r <repository URL>
```
An example of repository URL: `https://github.com/facebook/react`

### Review & Block/Ignore/Whitelist
After starting the program, you can review the issues and comments in the repository.

You will see the issues and comments in the terminal.

Example output:
```bash
GitHub Quick Blocker
Repository: for/example
Logged in as: someone
--------------------------------------------------------------------------------
Issue #23964: F-word
User: Spammer
Content: 
More f-words
--------------------------------------------------------------------------------
Block user `Spammer'?
y/n/w/q:
```

You can then choose to block the user (`y`), ignore (`n`), or whitelist (`w`) the user, or quit (`q`).

Users in the whitelist will not be asked to block again.
