REPLY FOR TASK 12

1) STEP 0 — File-integrity check (FULL OUTPUT)

MISSING  src\__init__.py
MISSING  src\config.py
MISSING  src\data.py
MISSING  src\model.py
MISSING  src\train.py
MISSING  src\api.py
MISSING  tests\test_data.py
MISSING  tests\test_inference.py
MISSING  scripts\smoke_test.py
MISSING  scripts\replay_batch.py
MISSING  scripts\download_data.py
MISSING  .github\workflows\ci.yml
MISSING  .github\workflows\cd.yml
MISSING  Dockerfile
MISSING  docker-compose.yml
MISSING  .dockerignore
MISSING  requirements.txt
MISSING  requirements-dev.txt
MISSING  params.yaml
MISSING  pytest.ini
MISSING  models\model.pt
MISSING  data\raw.dvc
MISSING  .dvc\config
MISSING  .dvcignore
MISSING  monitoring\prometheus.yml
MISSING  README.md
MISSING  samples\cat_10.jpg
MISSING  samples\dog_10.jpg

model.pt bytes : ABSENT   (must be 978168)
samples count  : 0   (must be 6)

Select-String : Cannot find path 'C:\karthik\bits\bits3\Bits\.github\workflows\cd.yml' because it does not exist.
(several Select-String errors for cd.yml/docker-compose/requirements.txt appeared when run from top-level)

TOTAL MISSING FILES: 28

-- NOTE: The above output is from running STEP 0 at the top-level workspace. The NEXT-STEP
         instructions require running this check from the project root (the folder that
         contains `params.yaml`). I re-ran the check from the `MLOPs` folder below.


STEP 0 (re-run from `MLOPs` project root) — FULL OUTPUT

OK       src\__init__.py
OK       src\config.py
OK       src\data.py
OK       src\model.py
OK       src\train.py
OK       src\api.py
OK       tests\test_data.py
OK       tests\test_inference.py
OK       scripts\smoke_test.py
OK       scripts\replay_batch.py
OK       scripts\download_data.py
OK       .github\workflows\ci.yml
OK       .github\workflows\cd.yml
OK       Dockerfile
OK       docker-compose.yml
OK       .dockerignore
OK       requirements.txt
OK       requirements-dev.txt
OK       params.yaml
OK       pytest.ini
OK       models\model.pt
OK       data\raw.dvc
OK       .dvc\config
OK       .dvcignore
OK       monitoring\prometheus.yml
OK       README.md
OK       samples\cat_10.jpg
OK       samples\dog_10.jpg

model.pt bytes : 978168   (must be 978168)
samples count  : 6   (must be 6)

cd.yml lowercase fix : MISSING
cd.yml bash shell    : MISSING
cd.yml smoke deps    : MISSING
compose image mlops2 : MISSING
torch pin 2.5.1      : OK
torchvision 0.20.1   : OK

TOTAL MISSING FILES: 0


2) STEP 1 — Verification of pushed files (FULL OUTPUT)

--- STEP 1: git ls-files ---

.github/workflows/cd.yml
.github/workflows/ci.yml
Dockerfile
docker-compose.yml
models/model.pt
src/api.py

--- model size in repo (git cat-file -s) ---
978168

--- .github/workflows on disk ---

Name   : cd.yml
Length : 1401

Name   : ci.yml
Length : 2237


3) Are `.github/workflows/ci.yml` and `cd.yml` tracked by git?

Yes — both `.github/workflows/ci.yml` and `.github/workflows/cd.yml` are present in
the `git ls-files` output above, so they are tracked.


4) CI run result — which jobs ran and whether they passed

Recent workflow runs (summary extracted from the Actions API):

name: CD | path: .github/workflows/cd.yml | event: workflow_run | status: queued | conclusion: (queued)
name: CD | path: .github/workflows/cd.yml | event: workflow_run | status: queued | conclusion: (queued)
name: CI | path: .github/workflows/ci.yml | event: push | status: completed | conclusion: success | created_at: 2026-08-30T11:56:13Z
name: CI | path: .github/workflows/ci.yml | event: push | status: completed | conclusion: success | created_at: 2026-08-30T11:56:00Z

Detailed jobs for the two recent successful `CI` runs:

RUN_ID: 33310164167 created_at: 2026-08-30T11:56:13Z status: completed conclusion: success
  JOB: Lint & unit tests | status: completed | conclusion: success
  JOB: Build & publish image | status: completed | conclusion: success

RUN_ID: 33310155579 created_at: 2026-08-30T11:56:00Z status: completed conclusion: success
  JOB: Lint & unit tests | status: completed | conclusion: success
  JOB: Build & publish image | status: completed | conclusion: success

The latest `CD` run is queued and its job `Deploy & smoke test` shows `status: queued` and
is labeled `self-hosted` (see jobs output). It has not run to completion because it is
waiting for a self-hosted runner.


5) Does the GHCR package exist and is it public?

I could not determine package visibility programmatically without authenticated access.
The GitHub Packages API requires authentication to list user packages. The `CI` runs
show `Build & publish image` completed successfully, so the package should have been
pushed to GHCR at `ghcr.io/karthikreddygudur-png/mlops2` by the workflow, but
visibility (public/private) must be confirmed in the GitHub UI.

Action for you (human):
- Open https://github.com/karthikreddygudur-png?tab=packages, click the `mlops2` package,
  then in Package settings change visibility to Public (Step 4 in NEXT-STEP.md).


6) Self-hosted runner question (Step 6)

The `CD` job is labeled `self-hosted` and is currently queued (no runner picked it up).
Can you install a self-hosted GitHub Actions runner on this machine (yes/no)?

If yes: I will provide the exact runner registration steps and then re-run the CD job.
If no: we must choose an alternative deployment approach (explain constraints and next steps).


7) Anything that failed (exact errors)

- When STEP 0 was run from the top-level workspace (not the `MLOPs` project root) many
  files were reported MISSING (28 files). Exact text shown above. This was due to running
  the check from the wrong directory — the correct project root is `MLOPs`.
- Inside `MLOPs` the content check passed file presence and `models/model.pt` size is
  correct (978168). However several content checks against `.github/workflows/cd.yml`
  (the `tr '[:upper:]'` fix, `shell: bash`, and `requests pillow` deps) returned
  `MISSING` indicating those specific strings were not found in `cd.yml` (see STEP 0 output).
- Querying the GitHub Packages API returned `Requires authentication` — exact response
  from the API: `{ "message": "Requires authentication", "documentation_url": "https://docs.github.com/rest", "status": "401" }`.


--- END OF REPLY ---
