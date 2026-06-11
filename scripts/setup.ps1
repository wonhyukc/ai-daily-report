# AI Daily Report - Setup Script
# Initialize the project and install dependencies

param(
    [switch]$SkipPip = $false,
    [switch]$SkipEnv = $false
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "🚀 AI Daily Report - Setup Script"
Write-Host "=================================="
Write-Host ""

# Step 1: Check Python installation
Write-Host "Step 1: Checking Python installation..."
try {
    $PythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $PythonVersion"
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ first."
    exit 1
}

# Step 2: Create virtual environment
Write-Host ""
Write-Host "Step 2: Creating virtual environment..."
$VenvPath = Join-Path $ProjectRoot "venv"

if (Test-Path $VenvPath) {
    Write-Host "⚠️ Virtual environment already exists at: $VenvPath"
} else {
    try {
        python -m venv $VenvPath
        Write-Host "✓ Virtual environment created"
    } catch {
        Write-Host "❌ Failed to create virtual environment: $_"
        exit 1
    }
}

# Step 3: Activate virtual environment
Write-Host ""
Write-Host "Step 3: Activating virtual environment..."
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-Host "❌ Activation script not found at: $ActivateScript"
    exit 1
}

try {
    & $ActivateScript
    Write-Host "✓ Virtual environment activated"
} catch {
    Write-Host "⚠️ Could not activate venv. Trying alternative method..."
    $env:Path = "$VenvPath\Scripts;" + $env:Path
}

# Step 4: Install dependencies
if (-not $SkipPip) {
    Write-Host ""
    Write-Host "Step 4: Installing Python dependencies..."
    $RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

    if (-not (Test-Path $RequirementsFile)) {
        Write-Host "❌ requirements.txt not found"
        exit 1
    }

    try {
        python -m pip install --upgrade pip
        python -m pip install -r $RequirementsFile
        Write-Host "✓ Dependencies installed"
    } catch {
        Write-Host "❌ Failed to install dependencies: $_"
        exit 1
    }
}

# Step 5: Setup environment file
if (-not $SkipEnv) {
    Write-Host ""
    Write-Host "Step 5: Setting up .env file..."
    $EnvFile = Join-Path $ProjectRoot ".env"
    $EnvExampleFile = Join-Path $ProjectRoot ".env.example"

    if ((Test-Path $EnvFile)) {
        Write-Host "⚠️ .env file already exists. Skipping..."
    } else {
        if (Test-Path $EnvExampleFile) {
            Copy-Item $EnvExampleFile -Destination $EnvFile
            Write-Host "✓ .env created from .env.example"
            Write-Host "⚠️ Please edit .env and add your API keys!"
        } else {
            Write-Host "❌ .env.example not found"
        }
    }
}

# Step 6: Create necessary directories
Write-Host ""
Write-Host "Step 6: Creating data directories..."
@('data\logs', 'data\cache', 'reports') | ForEach-Object {
    $Dir = Join-Path $ProjectRoot $_
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
        Write-Host "✓ Created: $_"
    }
}

# Step 7: Test run
Write-Host ""
Write-Host "Step 7: Testing the setup..."
try {
    $PythonExe = Join-Path $VenvPath "Scripts\python.exe"
    & $PythonExe "$ProjectRoot\src\main.py" --help 2>&1 | Out-Null
    # If we get here, basic Python import works
    Write-Host "✓ Basic Python environment working"
} catch {
    Write-Host "⚠️ Could not run test: $_"
}

Write-Host ""
Write-Host "=================================="
Write-Host "✅ Setup completed successfully!"
Write-Host ""
Write-Host "📝 Next steps:"
Write-Host "  1. Edit .env file with your API keys:"
Write-Host "     - ANTHROPIC_API_KEY (required)"
Write-Host "     - NEWSAPI_KEY (optional)"
Write-Host ""
Write-Host "  2. Test the system (dry run):"
Write-Host "     .\scripts\run.ps1 -DryRun"
Write-Host ""
Write-Host "  3. Register scheduled task (requires admin):"
Write-Host "     .\scripts\install-task.ps1"
Write-Host ""
Write-Host "  4. View documentation: README.md"
Write-Host ""
