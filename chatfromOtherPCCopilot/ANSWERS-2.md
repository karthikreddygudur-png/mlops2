# Answers to your questions

---

## Q1 — Cancel the two older queued runs?

**Use the GitHub web UI. You do not need `gh` for this.**

`[NEEDS HUMAN]` Ask the user to:

1. Open `https://github.com/karthikreddygudur-png/mlops2/actions`
2. Find run **33310314478** — click it, then **Cancel workflow** (top right)
3. Do the same for run **33310331051**
4. Leave run **33311498475** alone — that is the good one, built from the fixed `cd.yml`

Two clicks each. Faster than installing `gh` just for this.

**Still install `gh` afterwards** — it makes Task 14 far smoother, because you can check
run status yourself instead of asking the user each time:

```powershell
winget install --id GitHub.cli -e
```

Restart the terminal, then `gh auth login` and follow the browser prompt.

If `winget` is blocked, carry on without it and ask the user to read the Actions tab.

---

## Q2 — Which machine for the runner?

**Here** — `C:\karthik\bits\bits3\Bits\MLOPs`, the machine you are on.

The runner must be where Docker is, because CD runs `docker compose up` to deploy the
container. That is this machine.

---

## Q3 — Runner name and labels

| Setting | Value |
| --- | --- |
| Name | `mlops2-runner-win` |
| Labels | accept the defaults |
| Work folder | `_work` (default) |

**Do not add custom labels.** The workflow uses `runs-on: self-hosted`, and every
self-hosted runner gets that label automatically. Adding extra labels risks a mismatch
where the job never gets picked up.

---

## Q4 — Install as a service?

**No. Run it interactively with `.\run.cmd`.**

Reasons:
- Installing as a service needs administrator rights, which may be blocked.
- Interactive is visible — you can see jobs being picked up in real time, which is useful
  when recording the demo video.
- Keep the terminal window open while working. Closing it stops the runner, and CD jobs
  will queue until it is running again.

---

## Q5 — GHCR visibility

**No change needed.** You pulled `ghcr.io/karthikreddygudur-png/mlops2:latest`
successfully, which is what matters.

Note that your local pull may have succeeded because Docker is already authenticated on
this machine. The CD workflow logs in with `GITHUB_TOKEN` regardless, so it will work
either way.

Optional, and worth doing if it is quick: making the package public means a grader can
pull it without credentials. `Packages → mlops2 → Package settings → Change visibility
→ Public`. Not required.

---

## IMPORTANT — correction to your runner instructions

**Do not use the commands you drafted.** They hardcode runner version `v2.308.0`, which
is old, and they need `gh` to fetch a registration token.

**Use GitHub's own instructions instead.** They give the current version and a valid
token with no `gh` required:

`[NEEDS HUMAN]` Ask the user to:

1. Open `https://github.com/karthikreddygudur-png/mlops2/settings/actions/runners`
2. Click **New self-hosted runner**
3. Select **Windows**
4. Copy each PowerShell command shown on that page and run it in order

The page gives the correct download URL, checksum, and a `.\config.cmd` line with a real
registration token embedded.

When `config.cmd` prompts:

| Prompt | Answer |
| --- | --- |
| Runner group | press Enter (Default) |
| Runner name | `mlops2-runner-win` |
| Additional labels | press Enter (none) |
| Work folder | press Enter (`_work`) |

Then start it:

```powershell
.\run.cmd
```

You should see `Listening for Jobs`. **Leave this window open.**

---

## What happens next

Once the runner is listening, run **33311498475** should be picked up within a few
seconds, and CD will:

1. Log in to GHCR
2. Resolve the lowercase image reference
3. `docker compose pull` and `docker compose up -d`
4. Install `requests` and `pillow`
5. Run `smoke_test.py` against `http://localhost:8000`

**EXPECTED:** the job succeeds, with `[PASS] smoke test succeeded` in the log.

If it does not start automatically, re-run it from the Actions tab.

---

## Then verify

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
docker compose ps
docker compose images
curl.exe http://localhost:8000/health
```

**EXPECTED:** a running container, and `/health` returning `model_loaded: true`.

Mark row 13 `DONE` in the README status board, commit.

---
---

# EVERYTHING REMAINING — Tasks 14 to 17

Work through these in order. Do not skip.

---

## TASK 14.1 — Manual deploy (confirms Compose works)

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
$env:IMAGE = "ghcr.io/karthikreddygudur-png/mlops2:latest"
docker compose pull
docker compose up -d
Start-Sleep -Seconds 15
.\.venv\Scripts\python.exe scripts\smoke_test.py --base-url http://localhost:8000
```

**EXPECTED:** last line reads `[PASS] smoke test succeeded`

**IF `docker compose pull` fails with `denied`** → the package is private. Ask the user
to make it public, or run `docker login ghcr.io -u karthikreddygudur-png` (the user types
their Personal Access Token themselves — never ask them to send it to you).

---

## TASK 14.2 — Prove automatic deployment

```powershell
git commit --allow-empty -m "Trigger CI/CD pipeline"
git push
```

Then watch:

```powershell
gh run list --limit 5
docker compose ps
docker compose images
```

**EXPECTED:** CI green, then CD green on the self-hosted runner, and a running container.

**IF CD NEVER STARTS** → the runner window was closed. Restart it with `.\run.cmd`.

Mark row 14 in progress.

---

## TASK 14.3 — Prove the smoke test blocks a bad release

The assignment explicitly requires this. **Do not skip it.**

Open `src/api.py` and find this exact line:

```python
        model_loaded=STATE["model"] is not None,
```

Change **that one line only** to:

```python
        model_loaded=False,
```

**Do not change `status="ok"` instead.** The smoke test only inspects the HTTP status
code and `model_loaded`, so altering the status text changes nothing and the pipeline
would stay green — making the demonstration meaningless.

```powershell
git add src/api.py
git commit -m "Temporarily break health check to prove smoke test gate"
git push
```

**EXPECTED:** CI passes, then **CD FAILS** at the `Smoke test` step, and the
`Roll back on failure` step runs `docker compose down`.

Capture evidence for the video and the report:

```powershell
gh run list --workflow=cd.yml --limit 3
gh run view --log-failed
```

**Then revert immediately. Do not leave the code broken:**

```powershell
git revert --no-edit HEAD
git push
```

Confirm CD goes green again and the container is running:

```powershell
gh run list --limit 5
docker compose ps
curl.exe http://localhost:8000/health
```

Mark row 14 `DONE`, commit.

---

## TASK 15 — Demo video (under 5 minutes)

`[NEEDS HUMAN]` — you cannot record a screen. Give the user this guidance.

**Tool:** OBS Studio (`obsproject.com`), free. Add a *Display Capture* source, press
Start Recording. Avoid Xbox Game Bar — it refuses to capture File Explorer and the
desktop, which this demo needs.

**The timing trap:** CI takes 5–8 minutes but the video must be under 5 minutes. Do not
sit watching a spinner. Push first, then narrate other material while CI runs.

| Time | Show |
| --- | --- |
| 0:00 | Edit one line in `src/api.py`, commit, **push** — this starts CI |
| 0:30 | While CI runs: `mlflow ui` at :5000 — params, metrics, confusion matrix, loss curves |
| 1:30 | While CI runs: `data/raw.dvc` and `dvc status` — dataset versioning |
| 2:00 | While CI runs: walk through `Dockerfile`, `ci.yml`, `cd.yml` |
| 2:45 | Back to Actions — CI green, image pushed to GHCR |
| 3:00 | CD starts automatically on the self-hosted runner |
| 3:30 | Smoke test passes; `docker compose ps` shows the new container |
| 4:00 | `curl.exe` a live prediction against the deployed service |
| 4:30 | `/metrics` and `docker logs` — monitoring |

**Before recording:** rehearse once, set terminal font to about 16pt, enable Windows
Focus Assist to suppress notifications, pre-open the Actions and Packages tabs, close
chat and email apps.

**Two details that earn marks:** show the smoke-test failure from Task 14.3, and point
out that the running image tag matches the commit SHA — traceability from code to
deployment.

Mark row 15 `DONE`.

---

## TASK 16 — Build the submission zip

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
$stage = "submission_2024AD05132"
Remove-Item -Recurse -Force $stage, "$stage.zip" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $stage | Out-Null
$items = 'src','tests','scripts','samples','monitoring','models','reports','mlruns',
         '.github','.dvc','.git','data','Dockerfile','docker-compose.yml',
         'requirements.txt','requirements-dev.txt','params.yaml','pytest.ini',
         '.dockerignore','.dvcignore','.gitignore','README.md'
foreach ($i in $items) { if (Test-Path $i) { Copy-Item $i -Destination $stage -Recurse -Force } }
Remove-Item -Recurse -Force "$stage\.dvc\cache","$stage\data\raw" -ErrorAction SilentlyContinue
Compress-Archive -Path "$stage\*" -DestinationPath "$stage.zip" -Force
Remove-Item -Recurse -Force $stage
"zip size: $([math]::Round((Get-Item "$stage.zip").Length/1MB,2)) MB"
```

**EXPECTED:** 5–30 MB. Must **not** contain `.venv/`, `data/raw/` or `.dvc/cache/`.
If it exceeds 100 MB, one of those slipped in.

Verify:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path "submission_2024AD05132.zip"))
'src/api.py','Dockerfile','docker-compose.yml','models/model.pt','data/raw.dvc',
'.github/workflows/ci.yml','.github/workflows/cd.yml','requirements.txt' | ForEach-Object {
  $n = $_; $hit = $z.Entries | Where-Object { $_.FullName -replace '\\','/' -like "*$n" }
  "{0,-40} {1}" -f $n, $(if ($hit) { "OK" } else { "MISSING" })
}
$z.Dispose()
```

Every line must read `OK`.

Mark row 16 `DONE`, commit.

---

## TASK 17 — Hand over to the user

Give the user this summary, with real values filled in:

> **Your MLOps Assignment 2 is complete. Submit these two items.**
>
> **1. `submission_2024AD05132.zip`** — `<full path>`, `<size>` MB
> Contains all source code, DVC / CI-CD / Docker / Compose configuration, the trained
> model, MLflow run history, and the training and post-deployment reports.
>
> **2. Screen recording** — `<full path>`, `<mm:ss>` (must be under 5 minutes)
>
> Repository: `https://github.com/karthikreddygudur-png/mlops2`
> Container image: `ghcr.io/karthikreddygudur-png/mlops2:latest`
>
> **Results:** 70.2% model test accuracy, 13 unit tests passing, 24,998 images versioned
> with DVC, CI and CD pipelines both verified green, smoke-test failure path demonstrated
> and reverted.
>
> **Before submitting, please confirm:** the video is under 5 minutes, the zip opens and
> contains `models/model.pt`, and the GitHub repository is public.

**Also tell the user about anything that did not go to plan** — any workaround used, and
anything still outstanding. Do not claim success for a step that did not actually pass.

Mark row 17 `DONE`. The assignment is finished.

---

## FINAL CHECK — every line must be true before submitting

| # | Check | How to confirm |
| --- | --- | --- |
| 1 | All status board rows say `DONE` | Read the board in `README.md` |
| 2 | Unit tests pass | `pytest -q` → `13 passed` |
| 3 | Docker image exists | `docker images` |
| 4 | Container serves predictions | `curl.exe .../predict` returns a label |
| 5 | Code is on GitHub | `git remote -v`, repo has files |
| 6 | CI ran green | `gh run list` or Actions tab |
| 7 | Image published to GHCR | Repository → Packages |
| 8 | Self-hosted runner registered | Settings → Actions → Runners |
| 9 | CD deployed automatically | CD workflow green after a push |
| 10 | Smoke test passed in the pipeline | CD log shows `[PASS] smoke test succeeded` |
| 11 | Smoke-test failure demonstrated | Task 14.3 produced a red CD run |
| 12 | `src/api.py` reverted, CD green again | `git log` shows the revert |
| 13 | Video under 5 minutes | Check file duration |
| 14 | Zip verified | Every line printed `OK` |

---

## Report back in `REPLY-TASK-14.md`

1. Were the two stale runs cancelled?
2. Does the runner show **Idle** or **Active**?
3. CD run result — did it pass, and did the smoke test pass?
4. Last 15 lines of the CD job log.
5. Output of `docker compose ps` and `curl.exe http://localhost:8000/health`.
6. Task 14.3 — did CD go red as expected, and was the revert pushed?
7. Anything that failed, with exact error text.

---

## Rules — still apply

- Never change pinned versions in `requirements.txt` or `requirements-dev.txt`.
- Never modify `Dockerfile`, `src/`, `tests/` or `.github/` — except the single line in
  Task 14.3, which you then revert.
- Use `curl.exe`, never bare `curl`.
- Always run commands from `C:\karthik\bits\bits3\Bits\MLOPs`.
- Report real command output, not a summary.
- If a command fails twice, stop and report the task, the command, the exact error, and
  what you already tried.
- Never ask the user to paste a password or token to you — they type it into the
  terminal themselves.
