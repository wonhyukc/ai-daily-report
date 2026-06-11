# AI Daily Report - Main Execution Script
# Windows PowerShell compatible

param(
    [switch]$DryRun = $false,
    [string]$LogOutput = $null
)

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot "venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

# Check if venv exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python virtual environment not found at: $VenvPath"
    Write-Host "Please run: python -m venv venv"
    exit 1
}

# Set working directory
Set-Location $ProjectRoot

# Prepare environment
$env:PYTHONUNBUFFERED = "1"
if ($DryRun) {
    $env:DRY_RUN = "true"
} else {
    $env:DRY_RUN = "false"
}

# Load .env if it exists
$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $Key = $matches[1]
            $Value = $matches[2]
            [Environment]::SetEnvironmentVariable($Key, $Value)
        }
    }
}

# Run main script
Write-Host "🚀 Starting AI Daily Report Pipeline..."
Write-Host "Project Root: $ProjectRoot"
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Dry Run: $DryRun"
Write-Host ""

# Execute Python script
& $PythonExe -u "$ProjectRoot\src\main.py" @args

$ExitCode = $LASTEXITCODE

# Log to file if requested
if ($LogOutput) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - Exit Code: $ExitCode" | Out-File -Append -FilePath $LogOutput
}

exit $ExitCode
