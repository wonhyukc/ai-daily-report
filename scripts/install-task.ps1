# AI Daily Report - Windows Task Scheduler Registration
# Run as Administrator

param(
    [string]$TaskName = "AI Daily Report",
    [string]$TaskTime = "06:00",
    [switch]$Uninstall = $false
)

# Check if running as Administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ This script must be run as Administrator!"
    Write-Host "Please right-click PowerShell and select 'Run as administrator'"
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$RunScript = Join-Path $ScriptDir "run.ps1"

if ($Uninstall) {
    # Remove task
    Write-Host "🗑️ Removing scheduled task: '$TaskName'..."
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Host "✓ Task removed successfully"
    } catch {
        Write-Host "❌ Error removing task: $_"
        exit 1
    }
    exit 0
}

# Create task
Write-Host "📋 Creating scheduled task: '$TaskName'"
Write-Host "   Time: $TaskTime (Daily)"
Write-Host "   Script: $RunScript"
Write-Host ""

# Remove existing task if it exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "⚠️ Task already exists. Removing old task..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Start-Sleep -Seconds 1
}

# Create task trigger (Daily at specified time)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TaskTime

# Create task action (Run PowerShell script)
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$RunScript`"" `
    -WorkingDirectory $ProjectRoot

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstancePolicy IgnoreNew

# Create and register the task
try {
    $Task = New-ScheduledTask `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Description "Automatically generate AI Daily Report every morning"

    Register-ScheduledTask `
        -TaskName $TaskName `
        -InputObject $Task `
        -Force | Out-Null

    Write-Host "✅ Task registered successfully!"
    Write-Host ""
    Write-Host "📅 Task Details:"
    Write-Host "   Name: $TaskName"
    Write-Host "   Schedule: Daily at $TaskTime"
    Write-Host "   Status: Ready"
    Write-Host ""
    Write-Host "💡 To view the task: Open Task Scheduler and look for: $TaskName"
    Write-Host "💡 To run manually: Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host "💡 To uninstall: .\install-task.ps1 -Uninstall"

} catch {
    Write-Host "❌ Error creating task: $_"
    exit 1
}
