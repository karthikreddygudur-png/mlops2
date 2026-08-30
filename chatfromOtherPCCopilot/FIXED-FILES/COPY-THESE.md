# COPY THESE TWO FILES

The other machine has stale versions of `cd.yml` and `docker-compose.yml`. Its CD
pipeline will fail until these are replaced.

## What to copy

The two correct files are in this folder, flat and ready:

```
c:\work\GLSS\Bits\MLOPs\chatfromOtherPCCopilot\FIXED-FILES\cd.yml               (1921 bytes)
c:\work\GLSS\Bits\MLOPs\chatfromOtherPCCopilot\FIXED-FILES\docker-compose.yml   (897 bytes)
```

## Where they go on the other machine

| Copy this | To here |
| --- | --- |
| `FIXED-FILES\cd.yml` | `C:\karthik\bits\bits3\Bits\MLOPs\.github\workflows\cd.yml` |
| `FIXED-FILES\docker-compose.yml` | `C:\karthik\bits\bits3\Bits\MLOPs\docker-compose.yml` |

Note `cd.yml` goes **inside `.github\workflows\`**, not the project root.
`.github` is a hidden folder — in Explorer, enable **View → Show → Hidden items**, or
paste the full path into the address bar.

## Current versus required

| File | On other machine now | Must become |
| --- | --- | --- |
| `cd.yml` | 1401 bytes | **1921 bytes** |
| `docker-compose.yml` | 885 bytes | **897 bytes** |

## After copying, on the other machine

```powershell
cd C:\karthik\bits\bits3\Bits\MLOPs

(Get-Item .github\workflows\cd.yml).Length      # must be 1921
(Get-Item docker-compose.yml).Length            # must be 897

git add .github/workflows/cd.yml docker-compose.yml
git commit -m "Apply CD fixes: lowercase image, bash shell, smoke test deps"
git push
```

## Then tell the other Copilot

> Files copied and pushed. Continue from Step 2 in NEXT-STEP-2.md.

Plus your yes or no on installing a self-hosted GitHub Actions runner — that is the last
thing blocking Task 14.
