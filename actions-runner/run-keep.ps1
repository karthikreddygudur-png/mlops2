while ($true) {
    $ts = Get-Date -Format o
    Write-Output "[$ts] Starting runner..."
    & "${PSScriptRoot}\run.cmd"
    $rc = $LASTEXITCODE
    $ts2 = Get-Date -Format o
    Write-Output "[$ts2] Runner exited with code $rc. Sleeping 5s before restart..."
    Start-Sleep -Seconds 5
}
