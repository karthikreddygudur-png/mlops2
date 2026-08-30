# Reply to readout

Below are concise answers to the blocking questions in `QUESTIONS-FOR-USER.md`, plus short notes and next steps.

## Answers (blocking first)

- Q1 — What changed in "1 file changed +5 -3"?
  - File edited: `README.md` (status-board and task progress updates). The edits were committed locally to record Task 8/8.5/8.6 progress.

- Q2 — Was `requirements.txt` restored to the pinned versions?
  - Yes. `requirements.txt` contains the pinned runtime deps including:

```
torch==2.5.1
torchvision==0.20.1
```

- Q3 — Did the Docker build finish, and what is the image size?
  - Yes. The build completed and produced image `catdog-api:local` with size ~1.43GB.

- Q4 — GitHub details needed for Task 11
  - Not available yet. Please provide these values so I can continue Task 11:

```
GitHub username: ______________________
Repository name: ______________________
Git author name: ______________________
Git author email: ______________________
```

## Additional environment notes

- Python: the working environment uses Python 3.12 (tested `py -3.12`), and `pytest` passed (13 tests).
- Docker: daemon verified; platform `linux`; `hello-world` ran successfully.
- `gh` (GitHub CLI) is not installed on this machine (command not found).
- Port 8000 was free when checked.

## Suggested next steps

1. If you want me to continue now, I can run Task 10 checks:

```powershell
docker run -d -p 8000:8000 --name catdog-test catdog-api:local
Start-Sleep -Seconds 15
curl http://localhost:8000/health
curl -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
docker logs catdog-test
docker stop catdog-test && docker rm catdog-test
```

2. Provide the GitHub details (Q4) if you want me to perform Task 11 (create remote + push). If you prefer to do Task 11 yourself, tell me and I will continue with Task 12 once the repo exists.

3. If you'd like the self-hosted runner path investigated (Task 13), confirm whether installing a runner on this machine is allowed by your environment/policy.

---
If you want me to run the health/predict checks now, reply `run checks`. If you prefer to supply GitHub details first, fill the placeholders above and reply `github info provided`.
# Reply to your readout

Thank you for the summary. **Yes — proceed.** But three of the questions you listed are
ones you can answer yourself right now by running commands. Do those first, then
continue to Task 10.

Only **Q4 (GitHub details)** genuinely needs the user.

---

## Step 1 — Answer Q1, Q2 and Q3 yourself

Run these and paste the actual output back. Do not summarise — show the real output.

```powershell
# Q1 — what file did you change earlier?
git status --short
git diff

# Q2 — are the version pins intact?
Get-Content requirements.txt

# Q3 — did the build finish, and how big is the image?
docker images catdog-api
```

### What the answers must look like

**Q1** — `git status --short` should be empty, or show only files you were told to
change. If `Dockerfile`, `requirements.txt`, `requirements-dev.txt` or anything under
`src/` appears as modified, revert immediately:

```powershell
git checkout -- Dockerfile requirements.txt requirements-dev.txt
git checkout -- src/
```

Then rebuild the image, because the one you built may be wrong.

**Q2** — `requirements.txt` must contain exactly:
```
torch==2.5.1
torchvision==0.20.1
```
If it shows anything else, restore it with `git checkout -- requirements.txt` and
rebuild.

**Q3** — expect a row for `catdog-api` tagged `local`, roughly 1.5–2.5 GB.
If the image is missing, Task 9 did not actually finish — rerun `docker build`.

---

## Step 2 — Then run the Task 10 checks

Once Q1–Q3 are clean, yes, run the checks. Use exactly this sequence:

```powershell
docker run -d -p 8000:8000 --name catdog catdog-api:local
Start-Sleep -Seconds 15
curl.exe http://localhost:8000/health
```

**EXPECTED:** `{"status":"ok","model_loaded":true,"requests_served":0}`

**`model_loaded` must be `true`.** If it is `false`, stop and report — it means
`models/model.pt` did not get into the image. Check with:

```powershell
Get-Item models\model.pt | Select-Object Length     # must be exactly 978168 bytes
```

Then the predictions:

```powershell
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
curl.exe -F "file=@samples/cat_10.jpg" http://localhost:8000/predict
```

**EXPECTED** — JSON with four keys, for example:
```json
{"label":"dog","probabilities":{"cat":0.31,"dog":0.69},"latency_ms":38.6,"request_id":"..."}
```

**The `label` may be wrong on some images. That is expected and acceptable** — the
baseline model is about 70% accurate and skews toward predicting "cat". Do not treat a
wrong label as a failure, and do not attempt to fix the model. What matters is that a
valid, well-formed response comes back.

Then check monitoring and stop the container:

```powershell
curl.exe http://localhost:8000/metrics
docker logs catdog
docker stop catdog
docker rm catdog
```

**EXPECTED:** `/metrics` includes `http_requests_total`. `docker logs` shows JSON lines
containing `"event": "prediction"`.

---

## Step 3 — Update the Status Board and commit

In `README.md`, set rows 9 and 10 to `DONE` with a short result, for example
`DONE — image 2.1 GB` and `DONE — predictions verified`. Then:

```powershell
git add README.md
git commit -m "Tasks 9 and 10 complete"
```

---

## Step 4 — Ask the user for the Task 11 details

You cannot proceed past Task 10 without these, and you must not invent them:

| Item | Value |
| --- | --- |
| GitHub username | `______________________` |
| Repository name | `______________________` |
| Git author name | `______________________` |
| Git author email | `______________________` |

While waiting, you may run Task 8.6 (Docker readiness checks) if you have not already,
and report that table.

---

## Reminders

- Do not change pinned versions in `requirements.txt` or `requirements-dev.txt`.
- Do not modify `Dockerfile`, `src/`, `tests/` or `.github/`.
- If a command fails twice, stop and report the task, the exact command, the exact
  error, and what you tried.
- Report actual command output rather than a summary of it.
