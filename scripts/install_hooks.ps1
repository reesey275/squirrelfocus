$hook = ".git/hooks/commit-msg"
$root = (git rev-parse --show-toplevel)
$emit = Join-Path $root "scripts/sqf_emit.py"
$body = @"
#!/usr/bin/env pwsh
try {
  $root = (git rev-parse --show-toplevel)
  $emit = Join-Path $root "scripts/sqf_emit.py"
  $trailers = python "$emit" trailers 2>$null
  if ($trailers) { Add-Content -Path $args[0] -Value "`n$trailers" }
} catch { }
"@
Set-Content -Path $hook -Value $body -NoNewline
git update-index --chmod=+x $hook 2>$null
Write-Host "Installed commit-msg hook (PowerShell)."
