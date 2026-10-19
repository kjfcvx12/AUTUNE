# Off-hours runner for dataset / evaluation-set work. Started every 30 minutes by
# the Windows scheduled task "AutuneDatasetAuto"; decides by itself whether this
# slot may spend tokens, and if so starts ONE headless Claude run (see PROMPT.md).
#
#   -DryRun   print the decision for now (or for -At "2026-09-23 10:00") and exit
param([switch]$DryRun, [string]$At)

$Root = 'F:\0final\AUTUNE'
$Auto = Join-Path $Root 'dataset\auto'
$Claude = 'C:\Users\hi\.local\bin\claude.exe'

# --- when the user works (local time, 24h). Edit these, nothing else. ---------
$Usage = @{
    Monday = @(12, 21); Tuesday = @(9, 18); Wednesday = @(9, 18)
    Thursday = @(12, 21); Friday = @(9, 18)          # Saturday, Sunday: day off
}
# One-off days: 'yyyy-MM-dd' = @(start, end), or @() for a day off (holiday).
$Override = @{
    '2026-09-23' = @(12, 21)
}
# Stop this many hours BEFORE the user starts. The usage limit is a rolling
# five-hour window, so tokens spent at 08:00 are still counted against the user at
# 09:00; ending five hours early hands them a fresh window.
$LeadHours = 5
$MaxRunsWorkday = 8      # per calendar day on a day the user works
$MaxRunsDayOff = 0       # 0 = no cap: the queue is the limit
$RunTimeoutMinutes = 50
# Model for the unattended runs. The CLI default on this machine is
# claude-fable-5-1[1m], the heaviest against the usage limit; '' = use that default.
$Model = 'opus'
# -------------------------------------------------------------------------------

function Get-UsageHours([datetime]$d) {
    $key = $d.ToString('yyyy-MM-dd')
    if ($Override.ContainsKey($key)) { return , $Override[$key] }
    $name = $d.DayOfWeek.ToString()
    if ($Usage.ContainsKey($name)) { return , $Usage[$name] }
    return , @()
}

function Write-Log([string]$msg) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    if ($DryRun) { $line } else { Add-Content -Path (Join-Path $Auto 'runner.log') -Value $line -Encoding utf8 }
}

$now = if ($At) { [datetime]::Parse($At) } else { Get-Date }
$hours = Get-UsageHours $now
$dayOff = ($hours.Count -eq 0)

if (-not $dayOff) {
    $h = $now.Hour + $now.Minute / 60.0
    if ($h -ge ($hours[0] - $LeadHours) -and $h -lt $hours[1]) {
        if ($DryRun) { Write-Log "BLOCKED  $($now.DayOfWeek) usage $($hours[0])-$($hours[1]), closed from $($hours[0] - $LeadHours):00" }
        exit 0
    }
}

$eligible = @(Select-String -Path (Join-Path $Auto 'QUEUE.md') -Pattern '^- \[ \] (?!BLOCKED:)' -Encoding utf8).Count
if ($eligible -eq 0) {
    if ($DryRun) { Write-Log 'IDLE     queue has no eligible unit' }
    exit 0
}

$cap = if ($dayOff) { $MaxRunsDayOff } else { $MaxRunsWorkday }
$log = Join-Path $Auto 'runner.log'
$today = $now.ToString('yyyy-MM-dd')
$ranToday = if (Test-Path $log) { @(Select-String -Path $log -Pattern "^$today \S+ (END  |KILLED) " -Encoding utf8).Count } else { 0 }
if ($cap -gt 0 -and $ranToday -ge $cap) {
    if ($DryRun) { Write-Log "CAPPED   $ranToday runs today, cap $cap" }
    exit 0
}

$lock = Join-Path $Auto 'runner.lock'
if (Test-Path $lock) {
    $lockPid = [int](Get-Content $lock -TotalCount 1)
    if (Get-Process -Id $lockPid -ErrorAction SilentlyContinue) {
        if ($DryRun) { Write-Log "BUSY     run $lockPid still going" }
        exit 0
    }
    Remove-Item $lock -Force -Confirm:$false
}

if ($DryRun) {
    Write-Log "WOULD RUN  dayOff=$dayOff eligible=$eligible ranToday=$ranToday cap=$cap"
    exit 0
}

$stamp = $now.ToString('yyyyMMdd-HHmm')
$runsDir = Join-Path $Auto 'runs'
New-Item -ItemType Directory -Force $runsDir | Out-Null
$out = Join-Path $runsDir "$stamp.out.txt"
$err = Join-Path $runsDir "$stamp.err.txt"

# No MCP servers (their tool descriptions cost context on every run), no
# subagents, no web. Bash stays: the checkers are python scripts.
$claudeArgs = @(
    '-p', '"Read dataset/auto/PROMPT.md and do exactly what it says: one unit, then stop."',
    '--permission-mode', 'acceptEdits',
    '--allowedTools', 'Read,Write,Edit,Glob,Grep,Bash',
    '--disallowedTools', 'Agent,WebFetch,WebSearch,Workflow',
    '--strict-mcp-config'
)
if ($Model) { $claudeArgs += @('--model', $Model) }
$p = Start-Process -FilePath $Claude -ArgumentList $claudeArgs -WorkingDirectory $Root `
    -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden -PassThru
Set-Content -Path $lock -Value $p.Id -Encoding ascii
Write-Log "START pid=$($p.Id) dayOff=$dayOff eligible=$eligible run=$($ranToday + 1)"

if (-not $p.WaitForExit($RunTimeoutMinutes * 60 * 1000)) {
    Stop-Process -Id $p.Id -Force -Confirm:$false
    Write-Log "KILLED pid=$($p.Id) after $RunTimeoutMinutes min"
} else {
    # A run refused by the usage limit did no work; mark it so it is not counted
    # against the day's cap.
    $limited = [bool](Select-String -Path $out -Pattern 'hit your .*limit' -Quiet)
    $tag = if ($limited) { 'LIMIT' } else { 'END  ' }
    Write-Log "$tag pid=$($p.Id) exit=$($p.ExitCode)"
}
Remove-Item $lock -Force -Confirm:$false -ErrorAction SilentlyContinue
