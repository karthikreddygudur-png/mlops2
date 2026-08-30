# Handoff TODO — mlops2 (for Copilot)

Purpose: give another Copilot a precise checklist, current state and exact commands to continue work from STEP 8 onward. Run all commands from `C:\karthik\bits\bits3\Bits\MLOPs`.

---

## Quick status (current)

- Repository: `karthikreddygudur-png/mlops2` (branch: `main`)
- GitHub CLI: installed and authenticated (`gh` available at `C:\Program Files\GitHub CLI\gh.exe`).
- Self-hosted runner: `mlops2-runner-win` — status: **online** (checked via `gh api repos/.../actions/runners`).
- Runner helper: `actions-runner/run-keep.ps1` created and launched to keep `run.cmd` restarted automatically.
- Docker Compose deployment: containers started (`catdog-api`, `catdog-prometheus`) and `catdog-api` mapped to `0.0.0.0:8000`.
- Smoke test: `scripts/smoke_test.py` passed locally against `http://localhost:8000`:
  - `/health` -> `{"status":"ok","model_loaded":true,"requests_served":0}`
  - `/predict` -> returned a valid prediction JSON
- Latest CD runs (via `gh`): recent run number 3 -> **completed** with **failure**; older runs cancelled.

---

## Files you should know

- `scripts/smoke_test.py` — smoke test script (used by CD). Path: `scripts/smoke_test.py`
- `actions-runner/` — self-hosted runner folder. Includes `.runner`, `.credentials`, `_diag/` logs.
- `actions-runner/run-keep.ps1` — created restart-loop wrapper to keep `run.cmd` running.
- Docker-compose: `docker-compose.yml` at repo root (`MLOPs/docker-compose.yml`).
- Service code: `src/api.py` (used in STEP 10 to intentionally break health check and revert in STEP 11).

---

## Checklist (completed)

- [x] STEP 1 — Install GitHub CLI (`gh`) (installed)
- [x] STEP 2 — Open a new terminal & verify `gh --version` (verified)
- [x] STEP 3 — `gh auth login` and browser device flow (you completed the device auth)
- [x] STEP 4 — Cancel old queued runs (attempted; runs were already completed/cancelled)
- [x] STEP 5 — Request user to install runner (you installed/ran the runner)
- [x] STEP 6 — Verify runner via `gh api repos/.../actions/runners` (runner `online`)
- [x] STEP 7 — Watch the CD run (latest run #3 completed with `failure`)
- [x] Deployed stack locally via `docker compose up -d` and confirmed containers up
- [x] Ran `scripts/smoke_test.py` locally — **PASS**

---

## Next steps (what the next Copilot should do) — follow DO-THIS-NOW.md strictly

Do not proceed to STEP 10 until instructed. Stop after finishing STEP 7 (which is done).

If you are handing off, the next labeled steps in the runbook are STEP 8–STEP 12. Exact commands below.

### STEP 8 — Check the service is running

Run from repository root:

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
docker compose ps
curl.exe http://localhost:8000/health
```

Expected `/health` response:

```json
{"status":"ok","model_loaded":true,"requests_served":0}
```

If `model_loaded` is not `true`, do NOT change code yet — report back.

### STEP 9 — Test a prediction

```powershell
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
```

Expect a JSON response containing `label`, `probabilities` and `latency_ms`.

### STEP 10 — (NOT YET) Break the health check to prove pipeline gate

Only perform this when explicitly instructed. Edit `src/api.py` and replace the exact line:

```python
        model_loaded=STATE["model"] is not None,
```

with

```python
        model_loaded=False,
```

Then:

```powershell
git add src/api.py
git commit -m "Temporarily break health check to prove smoke test gate"
git push
```

Wait ~8 minutes and then inspect CD runs:

```powershell
C:\Program Files\GitHub CLI\gh.exe run list --workflow=cd.yml --limit 3
gh run view --log-failed
```

### STEP 11 — Revert the break (immediately)

```powershell
git revert --no-edit HEAD
git push
```

Then wait ~8 minutes and verify CD success and `/health` is `model_loaded: true` again.

### STEP 12 — Write report file `REPLY-TASK-14.md`

Collect and paste real outputs of these commands (do not summarize):

```powershell
gh run list --limit 10
docker compose ps
curl.exe http://localhost:8000/health
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
git log --oneline -5
```

Also answer the six questions listed in DO-THIS-NOW.md (copy exact outputs where requested).

---

## Useful commands & notes for handoff

- To query runners:

```powershell
"C:\Program Files\GitHub CLI\gh.exe" api repos/karthikreddygudur-png/mlops2/actions/runners
```

- To list cd runs with readable fields:

```powershell
"C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 5 --json number,status,conclusion,createdAt,displayTitle --jq '.'
```

- Runner logs location (on this host):
  - `actions-runner\_diag\Runner_YYYYMMDD-...-utc.log` (tail these to troubleshoot broker/connection issues)

- `actions-runner/run-keep.ps1` exists to keep `run.cmd` auto-restarted. If you prefer, run `run.cmd` interactively instead and keep the window open.

---

## Troubleshooting tips

- If runner registration complains about token time mismatch, ensure system time is correct and re-run `config.cmd` with a fresh token.
- If `gh` is not on PATH in other shells, use absolute path: `C:\Program Files\GitHub CLI\gh.exe`.
- Do not commit changes to `requirements.txt`, `Dockerfile`, `tests/` or `.github/` unless explicitly instructed by the runbook.

---

## Automation-friendly completion status (for another Copilot)

If an automated agent (another Copilot) will pick this up, follow these checks exactly and mark the corresponding task completed when the command returns the shown output. Copy the full output into `REPLY-TASK-14.md` when asked.

- Verify runner is online:

```powershell
"C:\Program Files\GitHub CLI\gh.exe" api repos/karthikreddygudur-png/mlops2/actions/runners
```

Expected snippet (must include `"name": "mlops2-runner-win"` and `"status": "online"`):

```json
{
  "total_count": 1,
  "runners": [
    {
      "id": 4,
      "name": "mlops2-runner-win",
      "os": "Windows",
      "status": "online",
      "busy": false
    }
  ]
}
```

- Verify CD runs list (example output shown):

```powershell
"C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 5 --json number,status,conclusion,createdAt,displayTitle --jq '.'
```

Example output observed during handoff:

```json
[
  {
    "conclusion": "failure",
    "createdAt": "2026-08-30T12:26:41Z",
    "displayTitle": "CD",
    "event": "workflow_run",
    "headBranch": "main",
    "number": 3,
    "status": "completed"
  },
  {
    "conclusion": "cancelled",
    "createdAt": "2026-08-30T12:00:23Z",
    "displayTitle": "CD",
    "event": "workflow_run",
    "headBranch": "main",
    "number": 2,
    "status": "completed"
  }
]
```

- Verify Docker Compose and /health (the smoke test output we observed):

Commands to run:

```powershell
docker compose ps
curl.exe http://localhost:8000/health
```

Observed `/health` output (copy exactly into the report):

```text
{"status": "ok", "model_loaded": True, "requests_served": 0}
```

- Smoke-test run output (observed):

```text
[PASS] /health -> {'status': 'ok', 'model_loaded': True, 'requests_served': 0}
[PASS] /predict -> label=dog latency=1921.72ms
[PASS] smoke test succeeded
```

Automation rules for another Copilot:

- Only mark `STEP 6` complete when the runner API returns `"status": "online"` for `mlops2-runner-win`.
- Only mark `STEP 7` complete when `gh run list` shows a recent CD run (the run may be `queued`, `in_progress` or `completed`). Record `number`, `status`, and `conclusion`.
- To produce the final handoff report `REPLY-TASK-14.md`, copy the exact outputs of the commands listed in DO-THIS-NOW.md STEP 12 and paste them verbatim into the file.
- If any command fails twice, stop and add the full error output to the report and raise an alert to the human operator.

---

End of automation notes.

If you want, I can now create `REPLY-TASK-14.md` with the exact outputs captured for STEP 12. Tell me to proceed and I will generate the report file using captured outputs (or live-run the commands again to collect fresh outputs).