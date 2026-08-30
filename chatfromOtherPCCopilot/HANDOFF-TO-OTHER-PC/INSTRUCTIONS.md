# INSTRUCTIONS — read this whole file, then start at PART 1

You are continuing an MLOps university assignment. Most of it is finished. There are
three things left. Work through them in order.

**Project folder — run every command from here:**

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
```

**Project facts:**

| Item | Value |
| --- | --- |
| GitHub repository | `https://github.com/karthikreddygudur-png/mlops2` |
| Container image | `ghcr.io/karthikreddygudur-png/mlops2:latest` |
| Python | 3.12 — always use `py -3.12`, never plain `python` |
| GitHub CLI | `C:\Program Files\GitHub CLI\gh.exe` |

---

## Current state

| Thing | Status |
| --- | --- |
| Code, tests, model | Done and working |
| CI pipeline | **Passing** |
| Image published to GHCR | Done |
| Self-hosted runner | Registered and online |
| Container deployed locally, smoke test | Passing |
| **CD pipeline** | **FAILING — this is the main problem** |
| README on GitHub | Wrong file was pushed |
| Assignment brief files | Pushed by mistake, must be removed |
| Submission zip and PDF | Already built on the other machine — you do not need to make these |

---

## Rules

1. Work through the parts in order. Do not skip.
2. **Never** change version numbers in `requirements.txt` or `requirements-dev.txt`.
3. **Never** edit `Dockerfile`, `tests/`, or `.github/workflows/` — except by copying
   the files provided in this folder.
4. Only edit `src/api.py` in PART 3, and undo it straight after.
5. Always type `curl.exe`, never `curl`. In PowerShell, `curl` is an alias for
   `Invoke-WebRequest` and does not accept `-F`.
6. If a command fails twice, **stop**. Report the part number, the exact command, and
   the exact error.
7. Paste real command output. Do not summarise it.
8. Never ask the user to type a password or token into the chat.
9. A wrong prediction label is **not** an error. The model is ~70% accurate.

---
---

# PART 1 — Fix the GitHub repository

## Files in this folder

| File | Copy it to |
| --- | --- |
| `README.md` | `C:\karthik\bits\bits3\Bits\MLOPs\README.md` |
| `cd.yml` | `C:\karthik\bits\bits3\Bits\MLOPs\.github\workflows\cd.yml` |
| `docker-compose.yml` | `C:\karthik\bits\bits3\Bits\MLOPs\docker-compose.yml` |

`cd.yml` goes **inside `.github\workflows\`**, not the project root.

## Step 1.1 — Copy the files

`[NEEDS HUMAN]` Ask the user to copy all three files to the locations above,
overwriting the existing ones.

`.github` is a hidden folder. In Explorer: **View → Show → Hidden items**, or paste the
full path into the address bar.

## Step 1.2 — Verify

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
(Get-Item README.md).Length
(Get-Item .github\workflows\cd.yml).Length
(Get-Item docker-compose.yml).Length
```

**Must print exactly: 10741, 1921, 897**

If any number differs, that file was not copied. Stop and tell the user which one.

```powershell
Select-String -Path README.md -Pattern "Submission links" -Quiet   # must be True
Select-String -Path README.md -Pattern "Status Board" -Quiet       # must be False
```

## Step 1.3 — Remove the assignment brief files

```powershell
git rm --cached "Assignment 2.pdf" "Assignment 2.md"
```

`--cached` removes them from Git but keeps them on disk. **Do not use `Remove-Item`.**

## Step 1.4 — Commit and push

```powershell
git add -A
git status --short
git commit -m "Replace README with project documentation; remove assignment brief"
git push
```

`git status --short` should show `M README.md`, `D Assignment 2.md`, `D Assignment 2.pdf`.
`D` means removed from tracking — correct.

## Step 1.5 — Verify

```powershell
git ls-files | Select-String "Assignment"
```

**Must print nothing.**

`[NEEDS HUMAN]` Ask the user to open `https://github.com/karthikreddygudur-png/mlops2`
and confirm the front page starts with **"Cats vs Dogs — End-to-End MLOps Pipeline"**
and that neither Assignment file is listed.

**PART 1 done. Go to PART 2.**

---
---

# PART 2 — Fix the CD pipeline

This is the main problem. CD has never succeeded.

**Why it matters:** the assignment requires proving the pipeline deploys automatically
*and* that it blocks a bad release. PART 3 deliberately makes CD fail. If CD is already
failing for an unrelated reason, that demonstration proves nothing.

## Step 2.1 — Get the failure log

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 5 --json databaseId,number,conclusion --jq '.'
```

Take the `databaseId` of the most recent failed run, then:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run view <DATABASE_ID> --log-failed
```

**Paste the entire output into your reply. Do not summarise it.**

## Step 2.2 — Identify the failing step

The log will name one of these:

| Step | What it does |
| --- | --- |
| `Resolve image reference` | Lowercases the image name |
| `Log in to GHCR` | Authenticates to the registry |
| `Pull the newly published image` | `docker compose pull api` |
| `Deploy` | `docker compose up -d` |
| `Install smoke test dependencies` | `pip install requests pillow` |
| `Smoke test` | Runs `scripts/smoke_test.py` |

Report the step name and the exact error.

## Step 2.3 — Run these checks

The runner is a Windows machine. These are the usual causes.

```powershell
where.exe bash
where.exe python
python --version
where.exe docker
docker compose version
```

**Expected:** a path for each, and version numbers.

`bash` matters most — the CD workflow uses `shell: bash`, which on Windows needs Git
Bash on the PATH.

## Step 2.4 — Restart the runner and retry

**The runner inherits its PATH from when it started.** If `gh`, Python or Docker were
installed after the runner launched, it cannot see them. This alone may be the entire
problem.

Close the runner window, open a new PowerShell, then:

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs\actions-runner
.\run.cmd
```

Wait for **"Listening for Jobs"** and leave the window open.

Then re-run the failed job:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run rerun <DATABASE_ID>
```

Wait 3 minutes, then check:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 3
```

**If it now shows `completed success`, go to PART 3.**

**If it still fails**, paste the new log in your reply and **stop**. Do not edit
`cd.yml` yourself — report the cause and wait for a fix.

---
---

# PART 3 — Prove the smoke test blocks a bad release

**Only start this once PART 2 shows `completed success`.**

## Step 3.1 — Break the health check

Open `src/api.py`. Find this exact line:

```python
        model_loaded=STATE["model"] is not None,
```

Change **that one line only** to:

```python
        model_loaded=False,
```

**Do not change the `status="ok"` line instead.** The smoke test only inspects the HTTP
status code and `model_loaded`, so changing the status text would change nothing and the
pipeline would stay green — making the demonstration worthless.

```powershell
git add src/api.py
git commit -m "Temporarily break health check to prove smoke test gate"
git push
```

Wait about 8 minutes, then:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 3
```

**Expected: `completed failure`.** That is the desired result — it proves the gate works.

Save the evidence:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run view --log-failed
```

## Step 3.2 — Undo it immediately

**Do not leave the code broken.**

```powershell
git revert --no-edit HEAD
git push
```

Wait about 8 minutes, then verify it recovered:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" run list --workflow=cd.yml --limit 3
docker compose ps
curl.exe http://localhost:8000/health
```

**Expected:** `completed success`, a running container, and `model_loaded` back to `true`.

---
---

# PART 4 — Report back

Create a new file called `REPLY.md` in this folder with:

1. The three size numbers from Step 1.2.
2. Output of `git ls-files | Select-String "Assignment"` — should be empty.
3. The full CD failure log from Step 2.1.
4. Which step failed, and the outputs from Step 2.3.
5. Whether restarting the runner fixed it.
6. PART 3: did CD go red as expected, and was the revert pushed and green again?
7. Anything that failed, with the exact error text.

---

## What you do NOT need to do

- Do not build a submission zip — already done on the other machine.
- Do not create a PDF or Word document — already done.
- Do not record the video — the user will do that.
- Do not retrain the model — it is finished, 70.2% accuracy.
