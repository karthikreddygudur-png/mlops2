# ANSWERS — read this and act on it

These are the answers to every question in `whattodonow.md`.

---

## CRITICAL — read this before anything else

**Do NOT change any version in `requirements.txt` or `requirements-dev.txt`.**

You reported this conflict:

> `torch==2.12.1+cpu` conflicts with `torchvision==0.28.0+cpu` (the latter requires `torch==2.13.0`)

**Those version numbers do not exist in this project, and `torch 2.12.1`, `torch 2.13.0`
and `torchvision 0.28.0` are not real releases.** Either the file was already edited, or
the versions were misread.

The committed, verified contents of `requirements.txt` are:

```
torch==2.5.1
torchvision==0.20.1
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pillow==11.0.0
numpy==2.1.3
python-multipart==0.0.20
prometheus-fastapi-instrumentator==7.0.0
pyyaml==6.0.2
```

`torchvision 0.20.1` is the correct partner for `torch 2.5.1`. **There is no conflict.**
This exact combination was installed and fully tested on Python 3.12.10.

### Step 1 — restore the original files before doing anything else

```powershell
git checkout -- requirements.txt requirements-dev.txt
git status --short
```

`git status --short` must print nothing for those two files. Then confirm:

```powershell
Get-Content requirements.txt
```

It must match the block above exactly. If it does not, stop and tell the user.

---

## Answers to your questions

### 1) Start at Task 8?
**YES.** Begin at Task 8 in `README.md` and work in order through Task 17.

### 2) Approve updating requirements.txt to `torch==2.13.0+cpu`?
**NO. Not approved.** See the section above. Restore the file with `git checkout`.

The real cause of your install failure is one of these two things:

**a) Wrong Python version.** You confirmed this machine has both Python 3.14 and 3.12.10.
Python 3.14 has no wheels for these libraries, so pip tries to build from source and
fails. **Always use `py -3.12`.**

**b) Missing extra index URL.** The `+cpu` builds only exist on PyTorch's own index. If
you run plain `pip install -r requirements.txt`, resolution fails. You must include
`--extra-index-url https://download.pytorch.org/whl/cpu`.

### 3) Git / GitHub details
**The user must fill these in. Do not invent them.**

| Item | Value |
| --- | --- |
| GitHub username | `_________________` |
| Repository name | `_________________` |
| Git author name | `_________________` |
| Git author email | `_________________` |

Ask the user for these before starting Task 11. They are not needed for Tasks 8 to 10,
so carry on with those in the meantime.

### 4) Recreate the venv with Python 3.12 and install?
**YES.** Use exactly these commands:

```powershell
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe --version
```

Confirm it prints **3.12.x** before continuing. Then:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-dev.txt
```

The `--extra-index-url` is mandatory. Do not omit it.

**Healthy output looks like:**
```
Downloading torch-2.5.1+cpu-cp312-cp312-win_amd64.whl (200.0 MB)
```
A `.whl` file, and `cp312` in the name.

**If you see any `.tar.gz` download or "Building wheel", stop** — the wrong Python is
being used. Delete `.venv` and start again with `py -3.12`.

### 5) Run pytest after install?
**YES.**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**Expected: `13 passed`.** If you get fewer, or `ModuleNotFoundError: src`, you are in
the wrong directory — `cd` to the folder containing `params.yaml`.

### 6) Run the Docker readiness checks (Task 8.6)?
**YES.** Run all of them and report the results as a table. Pay particular attention to:
- `docker info --format "{{.OSType}}"` must print **`linux`**, not `windows`
- `docker compose version` must be **v2 or later**

### 7) Continue using Python 3.12?
**YES.** Always `py -3.12`. Never plain `python` on this machine, because that resolves
to 3.14.

### 8) Should you skip installing torch to work around the problem?
**NO.** Torch is required for the model, the API and the tests. Nothing meaningful works
without it. Fix the Python version instead.

### 9) Should you also update `requirements-dev.txt`?
**NO.** No version changes to either file.

### 10) Update the Status Board in README.md as you go?
**YES.** After each task, edit the row in `README.md` from `TODO` to `DONE`, then commit:

```powershell
git add README.md
git commit -m "Task N complete"
```

If a task is blocked, mark it `BLOCKED` with a one-line reason rather than leaving it
as `TODO`.

### 11) Docker Desktop running? Proxy / CA / firewall constraints?
**Ask the user.** Do not assume. Run the Task 8.6 checks and report exactly what you
find.

---

## Your immediate next actions, in order

1. `git checkout -- requirements.txt requirements-dev.txt` — restore the pins
2. Verify `requirements.txt` matches the block above
3. Delete `.venv`, recreate with `py -3.12 -m venv .venv`
4. Confirm `.\.venv\Scripts\python.exe --version` prints 3.12.x
5. Install with the `--extra-index-url` flag included
6. Run `pytest -q`, expect `13 passed`
7. Mark Task 8 as `DONE` in the README status board, and commit
8. Run Task 8.5 (Git preflight), then Task 8.6 (Docker preflight)
9. Ask the user for the GitHub details before Task 11

## Rules to remember

- Never change pinned versions.
- Never invent a username, repository name or URL.
- If a command fails twice, stop and report: the task, the exact command, the exact
  error, and what you already tried.
- Never ask the user to paste a password or token to you — tell them to type it into
  the terminal themselves.
