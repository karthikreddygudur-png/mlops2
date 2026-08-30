# START HERE — AI agent instructions

You are an AI coding agent. Read this whole file, then begin work at **Task 10**.

This is a university MLOps assignment that is **78% complete**. Tasks 1 to 9 are already
finished and verified. Your job is Tasks 10 to 17.

`README.md` in this folder contains the full detailed runbook. This file is the
operational summary — the commands below are enough to work from.

---

## STEP 0 — Put these files in the right place

**If this machine already has the project** (a folder containing `params.yaml` and a
`.git` directory):

Copy everything from this `v1` folder over that project, replacing existing files. Keep
the existing `.git` folder — it holds the commit history you need. Then `cd` into the
project and confirm:

```powershell
git log --oneline | Select-Object -First 3
git status --short
```

**If this machine does NOT have the project yet:**

Work directly in this folder, and initialise Git:

```powershell
git init -b main
git add -A
git commit -m "MLOps assignment 2 - cats vs dogs pipeline"
```

---

## STEP 1 — Verify you have the fixed files

Three bugs were fixed after the earlier copy. Confirm all four checks return a match:

```powershell
Select-String -Path .github\workflows\cd.yml -Pattern "tr '\[:upper:\]'"
Select-String -Path .github\workflows\cd.yml -Pattern "shell: bash"
Select-String -Path .github\workflows\cd.yml -Pattern "requests pillow"
Select-String -Path docker-compose.yml -Pattern "mlops2"
```

If any returns nothing, you have an old copy. Stop and tell the user.

---

## Project facts

| Item | Value |
| --- | --- |
| GitHub username | `karthikreddygudur-png` |
| Repository | `mlops2` |
| Repository URL | `https://github.com/karthikreddygudur-png/mlops2` |
| Container image | `ghcr.io/karthikreddygudur-png/mlops2:latest` |
| Git author name | `Karthik Reddy` |
| Git author email | `karthikreddy.gudur@gmail.com` |
| Python required | **3.12** — use `py -3.12`, never plain `python` |
| Model accuracy | 70.2% (a baseline; accuracy is not graded) |
| `models/model.pt` | must be exactly **978168** bytes |

The image name is lowercase even though the repository is uppercase. Container
registries reject uppercase. This is correct and expected.

---

## Rules you must follow

1. Work tasks in order. One at a time.
2. After each task, edit the Status Board in `README.md`, changing that row from `TODO`
   to `DONE`, then `git add README.md && git commit -m "Task N complete"`.
3. If output does not match EXPECTED, stop and read the failure notes.
4. Never change pinned versions in `requirements.txt` or `requirements-dev.txt`.
5. Never modify `Dockerfile`, `src/`, `tests/` or `.github/` — except the single line in
   Task 14.3, which you then revert.
6. Use `curl.exe`, never bare `curl`. In PowerShell `curl` is an alias for
   `Invoke-WebRequest` and does not support `-F`.
7. Never invent a username, repository name or URL.
8. If a command fails twice, stop. Report the task, the exact command, the exact error,
   and what you tried.
9. Never ask the user to give you a password or token. Tell them to type it into the
   terminal themselves.
10. Report real command output, not a summary of it.

---

## Environment setup (skip if already done)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe --version          # must print 3.12.x
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q       # expect: 13 passed
```

If you see any `.tar.gz` download or "Building wheel", the wrong Python is being used.
Delete `.venv` and start again with `py -3.12`.

---

## TASK 10 — Run the container and verify predictions

Build first if the image does not exist (`docker images catdog-api`):

```powershell
docker build -t catdog-api:local .
```

The build takes 5–10 minutes. Do not abort it, and do not remove torch to speed it up.

```powershell
docker run -d -p 8000:8000 --name catdog catdog-api:local
Start-Sleep -Seconds 15
curl.exe http://localhost:8000/health
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
curl.exe -F "file=@samples/cat_10.jpg" http://localhost:8000/predict
curl.exe http://localhost:8000/metrics
docker logs catdog
docker stop catdog
docker rm catdog
```

**EXPECTED**
- `/health` → `{"status":"ok","model_loaded":true,"requests_served":0}`
- `/predict` → JSON with `label`, `probabilities`, `latency_ms`, `request_id`
- `/metrics` → contains `http_requests_total`
- `docker logs` → lines containing `"event": "prediction"`

**`model_loaded` must be `true`.** If it is `false`, the model did not reach the image:

```powershell
Get-Item models\model.pt | Select-Object Length     # must be 978168
docker run --rm catdog-api:local ls -l /app/models
```

**A wrong `label` is NOT a failure.** The model is ~70% accurate and skews toward "cat".
Do not try to fix the model. Only malformed responses, errors, or
`model_loaded: false` count as failures.

Mark row 10 `DONE`, commit.

---

## TASK 11 — Push to GitHub

`[NEEDS HUMAN]` Ask the user to create the repository if it does not exist:
`https://github.com/new` → name `mlops2` → **Public** → do **not** add a README,
.gitignore or licence.

```powershell
git config user.name "Karthik Reddy"
git config user.email "karthikreddy.gudur@gmail.com"
git remote add origin https://github.com/karthikreddygudur-png/mlops2.git
git branch -M main
```

Test before pushing:

```powershell
git ls-remote origin
git push --dry-run origin main
```

`git ls-remote origin` printing nothing is **correct** for a new empty repository. What
matters is that it does not error.

Only if both succeed:

```powershell
git push -u origin main
```

**IF `remote origin already exists`** → `git remote set-url origin <URL>`
**IF authentication fails** → `[NEEDS HUMAN]`. Suggest `gh auth login`, or a Personal
Access Token with `repo` and `write:packages` scopes used in place of the password.

Mark row 11 `DONE`, commit.

---

## TASK 12 — Verify CI

`[NEEDS HUMAN]` **Before CI finishes**, ask the user to set
`Settings → Actions → General → Workflow permissions` to **Read and write permissions**
and save. Without this the image push fails with 403.

Check the run:

```powershell
gh run list --limit 5
gh run view --log-failed
```

If `gh` is not installed, install it — it saves a lot of back and forth:

```powershell
winget install --id GitHub.cli -e
```

If that is blocked, `[NEEDS HUMAN]` ask the user to check
`https://github.com/karthikreddygudur-png/mlops2/actions`.

**EXPECTED:** jobs `test` then `build-and-push`, both green. CI takes 5–8 minutes; wait,
do not re-run it.

Then `[NEEDS HUMAN]` ask the user to make the package public:
`Packages → mlops2 → Package settings → Change visibility → Public`

Mark row 12 `DONE`, commit.

---

## TASK 13 — Self-hosted runner

`[NEEDS HUMAN]` — you cannot do this. Explain to the user:

> GitHub's servers cannot reach this machine through the firewall. A self-hosted runner
> solves that by connecting outward to GitHub and waiting for jobs. Without it, the CD
> pipeline cannot deploy here.

Ask them to:
1. Open `Settings → Actions → Runners → New self-hosted runner`
2. Choose Windows
3. Run the displayed commands: download, `config.cmd`, then `run.cmd`
4. Confirm the runner shows **Idle** in the Runners list

**If corporate policy forbids this, stop and tell the user.** A fallback will be needed.

Mark row 13 `DONE`, commit.

---

## TASK 14 — Verify CD and the smoke-test gate

### 14.1 — Deploy manually once

```powershell
$env:IMAGE = "ghcr.io/karthikreddygudur-png/mlops2:latest"
docker compose pull
docker compose up -d
Start-Sleep -Seconds 15
.\.venv\Scripts\python.exe scripts\smoke_test.py --base-url http://localhost:8000
```

**EXPECTED:** `[PASS] smoke test succeeded`

**IF `docker compose pull` fails with `denied` or `manifest unknown`** → the package is
private or was never published. Recheck Task 12.

### 14.2 — Prove it deploys automatically

```powershell
git commit --allow-empty -m "Trigger CI/CD pipeline"
git push
gh run list --limit 5
docker compose ps
```

**EXPECTED:** CI green, then CD green on the self-hosted runner, and a running container.

**IF CD NEVER STARTS** → the runner is offline. Return to Task 13.

### 14.3 — Prove the smoke test can fail the pipeline

The assignment requires this. In `src/api.py`, find:

```python
        model_loaded=STATE["model"] is not None,
```

Change that one line to:

```python
        model_loaded=False,
```

Do **not** change `status="ok"` instead — the smoke test only inspects the HTTP status
code and `model_loaded`, so changing the status text would change nothing.

```powershell
git add src/api.py
git commit -m "Temporarily break health check to prove smoke test gate"
git push
```

**EXPECTED:** CI passes, then **CD fails** at the `Smoke test` step and the rollback step
runs `docker compose down`.

Then revert immediately:

```powershell
git revert --no-edit HEAD
git push
```

Confirm CD goes green again before continuing.

Mark row 14 `DONE`, commit.

---

## TASK 15 — Demo video

`[NEEDS HUMAN]` — you cannot record a screen. Give the user this guidance.

Use **OBS Studio** (`obsproject.com`), not Xbox Game Bar — Game Bar refuses to capture
File Explorer and the desktop.

**The timing trap:** CI takes 5–8 minutes but the video must be under 5 minutes. Push
first, then narrate other material while CI runs.

| Time | Show |
| --- | --- |
| 0:00 | Edit one line in `src/api.py`, commit, **push** — starts CI |
| 0:30 | While CI runs: `mlflow ui` — params, metrics, confusion matrix, loss curves |
| 1:30 | While CI runs: `data/raw.dvc` and `dvc status` — dataset versioning |
| 2:00 | While CI runs: walk through `Dockerfile` and the workflow files |
| 2:45 | Back to Actions — CI green, image pushed to GHCR |
| 3:00 | CD starts automatically on the self-hosted runner |
| 3:30 | Smoke test passes; `docker compose ps` |
| 4:00 | `curl.exe` a live prediction |
| 4:30 | `/metrics` and `docker logs` |

Before recording: rehearse once, set terminal font to ~16pt, enable Focus Assist,
pre-open the Actions and Packages tabs, close chat and email apps.

Mark row 15 `DONE`.

---

## TASK 16 — Build the submission zip

```powershell
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

**EXPECTED:** 5–30 MB. It must **not** contain `.venv/`, `data/raw/` or `.dvc/cache/`.
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

## TASK 17 — Hand over

Give the user this summary, with real values filled in:

> **Your MLOps Assignment 2 is complete. Submit these two items.**
>
> **1. `submission_2024AD05132.zip`** — `<full path>`, `<size>` MB
> Contains all source code, DVC / CI-CD / Docker / Compose configuration, the trained
> model, MLflow history, and the training and post-deployment reports.
>
> **2. Screen recording** — `<full path>`, `<mm:ss>` (must be under 5 minutes)
>
> Repository: `https://github.com/karthikreddygudur-png/mlops2`
> Image: `ghcr.io/karthikreddygudur-png/mlops2:latest`
>
> Results: 70.2% test accuracy, 13 unit tests passing, 24,998 images versioned with DVC,
> CI and CD both verified, smoke-test failure path demonstrated and reverted.

**Also report anything that did not go to plan** — any workaround used, anything still
outstanding. Do not claim success for a step that did not actually pass.

Mark row 17 `DONE`. The assignment is finished.

---

## Final check before submitting

| # | Check |
| --- | --- |
| 1 | All status board rows say `DONE` |
| 2 | `pytest -q` → `13 passed` |
| 3 | `docker images catdog-api` lists the image |
| 4 | `/predict` returns a valid label |
| 5 | Code is on GitHub |
| 6 | CI ran green |
| 7 | Image published to GHCR |
| 8 | Self-hosted runner registered |
| 9 | CD deployed automatically |
| 10 | Smoke test passed in the pipeline |
| 11 | Smoke-test failure demonstrated (Task 14.3) |
| 12 | `src/api.py` reverted, CD green again |
| 13 | Video under 5 minutes |
| 14 | Zip verified, all `OK` |
