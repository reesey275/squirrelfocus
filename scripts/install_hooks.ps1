#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

$root = git rev-parse --show-toplevel
$hooks = Join-Path $root '.git/hooks'
$cmdHook = Join-Path $hooks 'commit-msg.cmd'
$psHook = Join-Path $hooks 'commit-msg.ps1'

$psContent = @'
param([string]$Path)

$root = git rev-parse --show-toplevel
try {
  $trailers = python "$root/scripts/sqf_emit.py" trailers
} catch {
  $trailers = ""
}
if (-not $trailers) { exit 0 }
Add-Content -Path $Path -Value ""
Add-Content -Path $Path -Value $trailers
'@

$psContent | Set-Content -Path $psHook -Encoding UTF8

$cmdContent = @'
@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0commit-msg.ps1" %*
'@

$cmdContent | Set-Content -Path $cmdHook -Encoding ASCII

Write-Output 'Installed commit-msg hook.'
