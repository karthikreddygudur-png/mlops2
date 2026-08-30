# Task 14 Report (placeholders)

## Actions I performed

- Read and executed `ANSWERS-2.md`.
- Fixed and pushed `.github/workflows/cd.yml` and `docker-compose.yml` (already done).
- Queried workflow runs and found queued run IDs (older runs): `33310314478`, `33310331051`.
- Attempted to cancel runs here but the `gh` CLI is not installed and no API token is available.
- Verified GHCR image is pullable: `docker pull ghcr.io/karthikreddygudur-png/mlops2:latest` succeeded locally.

## What I need from you (or `gh` installed here)

- Cancel the two older queued runs (either via GitHub Actions UI or `gh run cancel`):

  Web UI (recommended):
  1. Open https://github.com/karthikreddygudur-png/mlops2/actions
  2. Click run `33310314478` → Cancel workflow
  3. Click run `33310331051` → Cancel workflow

  OR (PowerShell with `gh` authenticated):

```powershell
gh run cancel 33310314478
gh run cancel 33310331051
gh run list --workflow=cd.yml --limit 10
```

- Register the self-hosted runner using the GitHub UI instructions at:
  https://github.com/karthikreddygudur-png/mlops2/settings/actions/runners
  (choose **New self-hosted runner** → Windows, then copy/paste the PowerShell commands shown)

Recommended runner name: `mlops2-runner-win` (leave labels blank).
Run interactively: `./run.cmd` (do not install as service).

## Commands to run after the runner is listening (paste outputs into this file)

```powershell
# verify runs
gh run list --workflow=cd.yml --limit 10

# view latest CD run (open in browser or use gh)
# if you prefer CLI logs:
gh run view --log -R karthikreddygudur-png/mlops2 <RUN_ID>

# check container and health
cd C:\karthik\bits\bits3\Bits\MLOPs
docker compose ps
curl.exe http://localhost:8000/health

# show last 15 lines of CD job log (if using gh):
# (replace RUN_ID and JOB_ID)
gh run view --log-failed -R karthikreddygudur-png/mlops2 <RUN_ID>

# manual deploy commands (if needed)
$env:IMAGE = "ghcr.io/karthikreddygudur-png/mlops2:latest"
docker compose pull
docker compose up -d
Start-Sleep -Seconds 15
.\.venv\Scripts\python.exe scripts\smoke_test.py --base-url http://localhost:8000
```

## Report fields (fill and paste outputs below)

1) Were the two stale runs cancelled? (Y/N)

2) Runner state (Idle/Active) and name:

3) CD run result for `33311498475` (pass/fail) and smoke test outcome:

4) Last 15 lines of the CD job log (paste raw):

```

```

5) Output of `docker compose ps` and `curl.exe http://localhost:8000/health` (paste raw):

```

```

6) Task 14.3 (smoke-test fail demo): Did CD go red and was the revert pushed? (describe)

7) Any failures or errors (copy exact text):


---

Once you paste the answers here I will continue: cancel remaining runs if needed, fetch a registration token (if you install `gh` locally and authenticate), and watch the CD run pick up on the runner.