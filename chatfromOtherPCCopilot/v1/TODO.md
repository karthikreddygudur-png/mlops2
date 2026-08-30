# TODO — current state and what is left

Snapshot taken on the main machine. This folder (`v1/`) is a complete, verified copy of
every tracked project file, including the fixed `cd.yml` and `docker-compose.yml`.

**Repository:** `https://github.com/karthikreddygudur-png/mlops2`
**Image:** `ghcr.io/karthikreddygudur-png/mlops2:latest` (lowercase — registries
require it)

---

## Status

| # | Task | State | Who |
| --- | --- | --- | --- |
| 1 | Project scaffold, all source code | DONE | main machine |
| 2 | Unit tests (13 tests) | DONE — 13 passed | main machine |
| 3 | Git repo + local commit history | DONE — 26 commits | main machine |
| 4 | DVC init, dataset tracked + pushed | DONE — 24,998 files | main machine |
| 5 | Dataset downloaded | DONE — 12,499 cat / 12,499 dog | main machine |
| 6 | Model trained → `models/model.pt` | DONE — 70.2% test accuracy | main machine |
| 7 | API verified with uvicorn | DONE — predictions served | main machine |
| 8 | Environment setup | DONE — Python 3.12, 13 tests pass | other machine |
| 8.5 | Preflight: Git + GitHub readiness | DONE | other machine |
| 8.6 | Preflight: Docker readiness | DONE — linux mode, port 8000 free | other machine |
| 9 | Build the Docker image | DONE — `catdog-api:local`, 1.43 GB | other machine |
| 10 | Run container, verify prediction | **IN PROGRESS** | other machine |
| 11 | Create GitHub repo + first push | **TODO** | human + agent |
| 12 | Verify CI pipeline is green | **TODO** | agent |
| 13 | Register self-hosted runner | **TODO** | human only |
| 14 | Verify CD deploys + smoke test | **TODO** | agent |
| 15 | Record the demo video | **TODO** | human only |
| 16 | Build the submission zip | **TODO** | agent |
| 17 | Hand over with submission summary | **TODO** | agent |

**Roughly 78% complete.**

---

## Use these files

This `v1/` folder supersedes anything currently on the other machine. Two files in
particular were fixed after the earlier copy and **must** be used:

| File | What changed |
| --- | --- |
| `.github/workflows/cd.yml` | Lowercase image name, `shell: bash`, smoke-test deps |
| `docker-compose.yml` | Default image set to the real GHCR path |

### Verify they are the fixed versions

```powershell
Select-String -Path .github\workflows\cd.yml -Pattern "tr '\[:upper:\]'"
Select-String -Path .github\workflows\cd.yml -Pattern "shell: bash"
Select-String -Path .github\workflows\cd.yml -Pattern "requests pillow"
Select-String -Path docker-compose.yml -Pattern "mlops2"
```

All four must return a match.

### Why these fixes matter

1. **Uppercase repo name.** `mlops2` is uppercase; container registries reject
   uppercase image names. Without the fix: `invalid reference format: repository name
   must be lowercase`.
2. **Windows self-hosted runners default to PowerShell**, but the CD steps are written
   in bash.
3. **The runner's system Python has no virtualenv on PATH**, so `smoke_test.py` would
   fail with `ModuleNotFoundError: requests` and look like a deployment failure.

---

## What is left, in order

### Task 10 — finish container verification
```powershell
docker run -d -p 8000:8000 --name catdog catdog-api:local
Start-Sleep -Seconds 15
curl.exe http://localhost:8000/health
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
curl.exe http://localhost:8000/metrics
docker logs catdog
docker stop catdog; docker rm catdog
```
`model_loaded` must be `true`. A wrong `label` is **not** a failure — the baseline model
is ~70% accurate.

### Task 11 — push to GitHub
```powershell
git config user.name "Karthik Reddy"
git config user.email "karthikreddy.gudur@gmail.com"
git remote add origin https://github.com/karthikreddygudur-png/mlops2.git
git branch -M main
git ls-remote origin            # test connectivity
git push --dry-run origin main  # test without uploading
git push -u origin main         # only if both above succeed
```

### Task 12 — verify CI
Enable `Settings → Actions → General → Workflow permissions` → **Read and write**
*before* CI finishes, or the image push returns 403.
Then make the package public under `Packages → Package settings`.

### Task 13 — self-hosted runner
`Settings → Actions → Runners → New self-hosted runner`. **Still unconfirmed whether
policy allows this.**

### Task 14 — verify CD
Deploy manually, then push a commit and confirm CD runs automatically. Then demonstrate
the failure path: change `model_loaded=STATE["model"] is not None` to
`model_loaded=False` in `src/api.py`, push, confirm CD goes red, then
`git revert --no-edit HEAD` and push again.

### Tasks 15–17
Record the video (under 5 minutes), build the submission zip, hand over.

---

## Rules

- Never change pinned versions in `requirements.txt` or `requirements-dev.txt`.
- Never modify `Dockerfile`, `src/`, `tests/` or `.github/` except where Task 14.3 says.
- Use `curl.exe`, not `curl` — in PowerShell, `curl` is an alias for `Invoke-WebRequest`
  and does not accept `-F`.
- Report actual command output, not a summary.
- If a command fails twice, stop and report the task, command, error, and what you tried.
- Never ask the user to paste a password or token — they type it into the terminal.

Full instructions are in `README.md` in this folder.
