# DO THIS NOW — one step at a time

Read one step. Do it. Check the result. Then go to the next step.

**Do not skip steps. Do not do two steps at once.**

Your project folder is:

```
C:\karthik\bits\bits3\Bits\MLOPs
```

Run every command from there. Start each session with:

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
```

---

# STEP 1 — Install GitHub CLI

**You can do this yourself. Run it now.**

```powershell
winget install --id GitHub.cli -e
```

Wait for it to finish.

**If it says "No package found" or "winget is not recognised":**
Stop. Tell the user: *"winget is not available. Please install GitHub CLI from
https://cli.github.com/ manually."* Then wait for them.

**When it finishes, go to STEP 2.**

---

# STEP 2 — Open a NEW terminal

The `gh` command will not work in the old terminal. You must open a new one.

Then run:

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
gh --version
```

**You should see:** something like `gh version 2.x.x`

**If it says "not recognised":** stop and tell the user that GitHub CLI did not install.

**If you see a version, go to STEP 3.**

---

# STEP 3 — Log in to GitHub

```powershell
gh auth login
```

It will ask you questions. Answer like this:

| Question | Answer |
| --- | --- |
| What account do you want to log into? | `GitHub.com` |
| What is your preferred protocol? | `HTTPS` |
| Authenticate Git with your GitHub credentials? | `Yes` |
| How would you like to authenticate? | `Login with a web browser` |

It will show a code like `ABCD-1234`.

**STOP HERE.** Tell the user:

> *"Please open https://github.com/login/device in your browser and enter this code:
> ABCD-1234"*

Wait for the user to say they have done it.

**Then run:**

```powershell
gh auth status
```

**You should see:** `Logged in to github.com as karthikreddygudur-png`

**Then go to STEP 4.**

---

# STEP 4 — Cancel the two old runs

**You can do this yourself now.**

```powershell
gh run cancel 33310314478
gh run cancel 33310331051
```

**If it says the run is already completed or cancelled, that is fine. Continue.**

Then check:

```powershell
gh run list --workflow=cd.yml --limit 10
```

**Then go to STEP 5.**

---

# STEP 5 — Ask the user to install the runner

**You CANNOT do this step. It needs a human.**

Say exactly this to the user:

> **I need you to install the GitHub Actions runner. It takes about 5 minutes.**
>
> 1. Open this page in your browser:
>    `https://github.com/karthikreddygudur-png/mlops2/settings/actions/runners`
> 2. Click the green **New self-hosted runner** button
> 3. Click **Windows**
> 4. The page shows a list of PowerShell commands. Copy each one and run it in
>    PowerShell, in order, from top to bottom.
> 5. When it asks questions, answer like this:
>    - Runner group → just press Enter
>    - Runner name → type `mlops2-runner-win` then Enter
>    - Additional labels → just press Enter (do not type anything)
>    - Work folder → just press Enter
> 6. Last command to run: `.\run.cmd`
> 7. You should see the words **"Listening for Jobs"**
> 8. **Leave that window open.** Do not close it.
>
> Tell me when you see "Listening for Jobs".

**STOP. Wait for the user to reply.**

**When the user says it is running, go to STEP 6.**

---

# STEP 6 — Check the runner is connected

```powershell
gh api repos/karthikreddygudur-png/mlops2/actions/runners
```

**You should see:** JSON containing `"name": "mlops2-runner-win"` and
`"status": "online"`

**If it says the list is empty:** the runner is not connected. Ask the user to check the
window shows "Listening for Jobs".

**If the runner is online, go to STEP 7.**

---

# STEP 7 — Watch the CD job run

```powershell
gh run list --workflow=cd.yml --limit 3
```

The queued CD job should now start by itself.

Wait 2 minutes, then run the command again.

**You should see:** `completed  success` for the CD run.

**If it still says `queued` after 5 minutes**, start it manually:

```powershell
gh workflow run cd.yml
```

**If it says `failure`**, read the log:

```powershell
gh run view --log-failed
```

Copy the error and go to STEP 12 to report it.

**If it says `success`, go to STEP 8.**

---

# STEP 8 — Check the service is running

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs
docker compose ps
curl.exe http://localhost:8000/health
```

**You should see:** a running container, and this response:

```json
{"status":"ok","model_loaded":true,"requests_served":0}
```

`model_loaded` must be `true`.

**Then go to STEP 9.**

---

# STEP 9 — Test a prediction

```powershell
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
```

**You should see** JSON like this:

```json
{"label":"cat","probabilities":{"cat":0.6,"dog":0.4},"latency_ms":38.6,"request_id":"..."}
```

**IMPORTANT: the label may say "cat" for a dog picture. THIS IS FINE. This is not a
bug. Do not try to fix it.** The model is only 70% accurate. All that matters is that
you get a proper JSON response.

**Then go to STEP 10.**

---

# STEP 10 — Break the health check on purpose

The assignment requires you to prove the pipeline stops a bad release.

Open the file `src/api.py`.

Find this exact line (it is inside the `health` function):

```python
        model_loaded=STATE["model"] is not None,
```

Replace it with exactly this:

```python
        model_loaded=False,
```

**Change nothing else. Do not touch the line with `status="ok"`.**

Then run:

```powershell
git add src/api.py
git commit -m "Temporarily break health check to prove smoke test gate"
git push
```

Wait 8 minutes, then check:

```powershell
gh run list --workflow=cd.yml --limit 3
```

**You should see:** `completed  failure` — the CD run FAILED. **This is what we want.**

Save the evidence:

```powershell
gh run view --log-failed
```

**Then go to STEP 11.**

---

# STEP 11 — Undo the break

**Do this immediately. Do not leave the code broken.**

```powershell
git revert --no-edit HEAD
git push
```

Wait 8 minutes, then check:

```powershell
gh run list --workflow=cd.yml --limit 3
curl.exe http://localhost:8000/health
```

**You should see:** `completed  success`, and `model_loaded` is `true` again.

**Then go to STEP 12.**

---

# STEP 12 — Write your report

Create a file called `REPLY-TASK-14.md` in this folder.

Put the **real output** of these commands in it. Copy and paste the actual text. Do not
write a summary.

```powershell
gh run list --limit 10
docker compose ps
curl.exe http://localhost:8000/health
curl.exe -F "file=@samples/dog_10.jpg" http://localhost:8000/predict
git log --oneline -5
```

Also answer these questions:

1. Did STEP 4 cancel the old runs? Yes or no.
2. Is the runner online? Yes or no.
3. Did the CD run succeed in STEP 7? Yes or no.
4. Did the CD run FAIL in STEP 10 as expected? Yes or no.
5. Did you revert the change in STEP 11? Yes or no.
6. Did anything go wrong? Paste the exact error text.

**Then tell the user the report is ready.**

---

# Rules — do not break these

1. **Never** change version numbers in `requirements.txt` or `requirements-dev.txt`.
2. **Never** edit `Dockerfile`, `tests/` or `.github/`.
3. Only edit `src/api.py` in STEP 10, and undo it in STEP 11.
4. Always type `curl.exe`, never `curl`.
5. Always run commands from `C:\karthik\bits\bits3\Bits\MLOPs`.
6. If a command fails twice, **stop**. Tell the user the step number, the command, and
   the exact error.
7. Never ask the user to type a password or token into the chat.
8. A wrong prediction label is **not** an error.
