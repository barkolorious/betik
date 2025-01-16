# Requires PowerShell 5.0 or later
#Requires -RunAsAdministrator

# Function to check if a command exists
function Test-Command {
    param ($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Function to display status messages
function Write-Status {
    param($Message, $Type = "Info")
    
    switch ($Type) {
        "Info" { 
            Write-Host "[*] $Message" -ForegroundColor Yellow 
        }
        "Success" { 
            Write-Host "[+] $Message" -ForegroundColor Green 
        }
        "Error" { 
            Write-Host "[-] $Message" -ForegroundColor Red 
        }
    }
}

# Check if Chocolatey is installed
Write-Status "Checking for Chocolatey installation..."
if (-not (Test-Command "choco")) {
    Write-Status "Installing Chocolatey..."
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        
        # Reload PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Status "Chocolatey installed successfully" -Type "Success"
    }
    catch {
        Write-Status "Failed to install Chocolatey. Error: $_" -Type "Error"
        exit 1
    }
}

# Check Python installation
Write-Status "Checking Python installation..."
if (-not (Test-Command "python")) {
    Write-Status "Installing Python..."
    try {
        choco install python -y
        # Reload PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Status "Python installed successfully" -Type "Success"
    }
    catch {
        Write-Status "Failed to install Python. Error: $_" -Type "Error"
        exit 1
    }
}
else {
    Write-Status "Python is already installed" -Type "Success"
}

# Install MiKTeX (LaTeX distribution)
Write-Status "Checking MiKTeX installation..."
if (-not (Test-Command "latex")) {
    Write-Status "Installing MiKTeX..."
    try {
        choco install miktex -y
        # Reload PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Status "MiKTeX installed successfully" -Type "Success"
        
        # Initialize MiKTeX settings
        Write-Status "Initializing MiKTeX..."
        initexmf --admin --set-config-value [MPM]AutoInstall=1
        
        # Update MiKTeX
        Write-Status "Updating MiKTeX..."
        miktex --admin update
    }
    catch {
        Write-Status "Failed to install MiKTeX. Error: $_" -Type "Error"
        exit 1
    }
}
else {
    Write-Status "MiKTeX is already installed" -Type "Success"
}

# Verify installations
Write-Status "Verifying installations..."
$allInstalled = $true

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Status "Python is installed: $pythonVersion" -Type "Success"
}
else {
    Write-Status "Python verification failed" -Type "Error"
    $allInstalled = $false
}

# Check LaTeX
if (Test-Command "latex") {
    Write-Status "LaTeX is installed" -Type "Success"
}
else {
    Write-Status "LaTeX verification failed" -Type "Error"
    $allInstalled = $false
}

# Check dvipng
if (Test-Command "dvipng") {
    Write-Status "dvipng is installed" -Type "Success"
}
else {
    Write-Status "dvipng verification failed" -Type "Error"
    $allInstalled = $false
}

# Final status
if ($allInstalled) {
    Write-Status "`nAll dependencies installed successfully!" -Type "Success"
    Write-Status "You can now use the LaTeX to PNG converter." -Type "Success"
}
else {
    Write-Status "`nSome dependencies are missing. Please try running the script again or install them manually." -Type "Error"
    exit 1
}

# Create a test file to verify LaTeX installation
Write-Status "Testing LaTeX installation..."
$testDir = Join-Path $env:TEMP "latex_test"
New-Item -ItemType Directory -Force -Path $testDir | Out-Null
Set-Location $testDir

@"
\documentclass{article}
\begin{document}
Test
\end{document}
"@ | Out-File -FilePath "test.tex" -Encoding utf8

try {
    latex -interaction=nonstopmode test.tex > $null 2>&1
    Write-Status "LaTeX test compilation successful" -Type "Success"
}
catch {
    Write-Status "LaTeX test compilation failed" -Type "Error"
}

# Clean up test files
Remove-Item -Path $testDir -Recurse -Force