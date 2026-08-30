# Results and Next Questions

## Results (current state)

- Fixed files copied & pushed:
  - `.github/workflows/cd.yml` — 1921 bytes
  - `docker-compose.yml` — 897 bytes
  - Commit: "Apply CD fixes: lowercase image, bash shell, smoke test deps" pushed to `origin/main`.
- GitHub Actions runs:
  - Queued-before-fix run IDs: 33310314478, 33310331051
  - Newer run for the fix commit: 33311498475 (keep this)
  - I could not cancel runs here because the `gh` CLI is not installed/available on this machine.
- GHCR image visibility:
  - `docker pull ghcr.io/karthikreddygudur-png/mlops2:latest` succeeded locally (image downloaded).

## Actions I can take (requires `gh` on this machine or you run commands locally)

- I can cancel the two older queued runs for you if you install and authenticate the `gh` CLI here, or you can run these locally (PowerShell):

```powershell
# list recent CD runs
gh run list --workflow=cd.yml --limit 10

# cancel the older queued runs
gh run cancel 33310314478
gh run cancel 33310331051

# verify
gh run list --workflow=cd.yml --limit 10
```

- To register a self-hosted runner (PowerShell on the runner machine):

```powershell
# create and enter runner folder
New-Item -ItemType Directory -Path actions-runner
Set-Location actions-runner

# download runner (example v2.308.0 — update if needed)
Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.308.0/actions-runner-win-x64-2.308.0.zip" -OutFile "actions-runner.zip"
Expand-Archive actions-runner.zip -DestinationPath .

# get registration token (run where `gh` is authenticated)
gh api -X POST repos/karthikreddygudur-png/mlops2/actions/runners/registration-token
# extract the JSON `token` value and use it below

# configure the runner (replace TOKEN and RUNNER_NAME)
.\config.cmd --url https://github.com/karthikreddygudur-png/mlops2 --token TOKEN --name RUNNER_NAME --labels self-hosted,windows --work _work --unattended

# run interactively
.\run.cmd

# optional: install as a service (follow prompts from config or see docs)
```

If you prefer I fetch a registration token and configure the runner here, I will need `gh` installed and authenticated (`gh auth login`).

## Questions for you (please answer)

1) Do you want me to cancel the two older queued runs here now, or will you run the `gh run cancel` commands locally?
2) Will you install the self-hosted runner on this machine (`C:\karthik\...`) or on another machine? Reply with "here" or provide host details.
3) Runner name and labels to use (suggested name: `mlops2-runner-win`, labels: `self-hosted,windows`).
4) Do you want the runner installed as a service (Yes/No)?
5) Confirm GHCR public status: I successfully pulled the image here — do you still want me to make any changes to registry visibility?

---

Reply inline in this file or answer in chat; I will act on your responses.