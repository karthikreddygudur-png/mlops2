# Questions I need answered

Ordered by how much they block progress. The first four matter most.

---

## BLOCKING — needed to keep going safely

### Q1. What was changed in "1 file changed +5 -3"?

Your screenshot of the other machine showed a file edit during the Docker build step.
I need to know which file and what changed. Ask the other agent to run:

```powershell
git status --short
git diff
```

**Why it matters:** if it edited `Dockerfile`, `requirements.txt` or anything in `src/`,
the build may now produce a broken image, and the version-pinning requirement (M2) is
compromised. Anything unexpected should be reverted:

```powershell
git checkout -- Dockerfile requirements.txt requirements-dev.txt
```

**Answer:** `______________________________`

---

### Q2. Was `requirements.txt` restored to the pinned versions?

Earlier it was mid-way through changing `torch` / `torchvision` pins.

Confirm it now reads exactly:
```
torch==2.5.1
torchvision==0.20.1
```

**Answer (yes / no):** `______________________________`

---

### Q3. Did the Docker build finish, and what is the image size?

```powershell
docker images catdog-api
```

Expected: roughly 1.5–2.5 GB.

**Answer:** `______________________________`

---

### Q4. GitHub details for Task 11

The other agent cannot proceed past Task 10 without these, and must not invent them.

| Item | Value |
| --- | --- |
| GitHub username | `______________________` |
| Repository name | `______________________` |
| Git author name | `______________________` |
| Git author email | `______________________` |

Also: is the account personal or corporate GitHub Enterprise? Actions and GHCR behave
differently on Enterprise.

**Answer:** `______________________________`

---

## IMPORTANT — affects whether M4 can be completed at all

### Q5. Can you install a self-hosted GitHub Actions runner on that machine?

This is the single biggest remaining risk. Task 13 needs a background agent that polls
GitHub and executes jobs locally. Some corporate IT policies forbid this.

If it is blocked, M4's "deploy automatically" requirement cannot be met the intended
way, and we would need a fallback — for example a `watchtower` container that auto-pulls
new images, or a documented manual deploy step. Tell me early if this is a problem.

**Answer:** `______________________________`

---

### Q6. Is that machine behind a corporate proxy, or does it intercept TLS?

Symptoms would be certificate errors from `pip`, `docker pull` or `git`. If so I need
the proxy address and whether a corporate CA certificate must be trusted.

**Answer:** `______________________________`

---

### Q7. Is Docker Desktop set to Linux containers?

```powershell
docker info --format "{{.OSType}}"
```

Must print `linux`. If it prints `windows`, the image cannot build and the fix is
right-click the Docker tray icon → **Switch to Linux containers**.

**Answer:** `______________________________`

---

## USEFUL — helps me tailor the remaining instructions

### Q8. Is GitHub CLI (`gh`) installed on that machine?

```powershell
gh --version
```

If yes, the agent can check CI status itself with `gh run list` instead of asking you to
read the Actions tab each time. It makes Tasks 12 and 14 much smoother.

**Answer:** `______________________________`

---

### Q9. Is port 8000 free on that machine?

If something else is using it, we change the port mapping once now rather than debugging
confusing results later.

**Answer:** `______________________________`

---

### Q10. When is the assignment due?

If time is short I would prioritise differently — for example demonstrating CD manually
rather than spending time on the self-hosted runner.

**Answer:** `______________________________`

---

### Q11. Do you want a better model for the demo video?

The current baseline is **70.2%** accurate and biased toward predicting "cat" (86%
recall on cats, 55% on dogs). That is fine for marks — the assignment asks for a
baseline and grades no accuracy threshold.

But if you want predictions that look convincing on camera, I can retrain here with a
pretrained MobileNetV2 backbone and reach roughly 95% in about the same time. I would
then send you the new `models/model.pt`.

**Answer (yes / no):** `______________________________`

---

## My current assumptions — correct me if any are wrong

1. The other machine is Windows with Docker Desktop installed and working.
2. It has both Python 3.14 and 3.12.10; we are using 3.12 via `py -3.12`.
3. You will use a **public** GitHub repository, so Actions minutes and GHCR are free.
4. Deployment target is **Docker Compose**, not Kubernetes.
5. You will record the video yourself on the other machine once Tasks 8–14 pass.
6. This machine (`c:\work\GLSS\Bits\MLOPs`) stays the reference copy — verified,
   working, and untouched by the other agent.
