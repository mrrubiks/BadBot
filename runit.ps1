# Check if Python is installed
Write-Output "Checking if Python is installed..."

# Ensure Python 3 is added to the PATH
$env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python312\Scripts"
$env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python312"
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonInstalled) {
    Write-Output "Python is not installed. Downloading and installing Python..."

    # Set the URL to download Python installer
    $pythonInstallerUrl = "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"
    $installerPath = "$PSScriptRoot\python-installer.exe"

    # Download the Python installer
    Write-Output "Downloading Python installer..."
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

    # Install Python silently
    Write-Output "Installing Python..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1" -NoNewWindow -Wait

    # Check if Python was successfully installed
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonInstalled) {
        Write-Output "Python installation failed. Exiting..."
        exit 1
    }
    Write-Output "Python installed successfully."
} else {
    Write-Output "Python is already installed."
}

# Create a virtual environment named 'badbot'
Write-Output "Creating a virtual environment named 'badbot'..."
python -m venv badbot

# Activate the virtual environment
Write-Output "Activating the virtual environment..."
& "$PSScriptRoot\badbot\Scripts\Activate.ps1"

# Install the packages from requirements.txt
Write-Output "Installing packages from requirements.txt..."
pip install -r "$PSScriptRoot\requirements.txt"

# Run the badbot.py script
Write-Output "Running the badbot.py script..."
python "$PSScriptRoot\badbot.py"

# Deactivate the virtual environment
Write-Output "Deactivating the virtual environment..."
deactivate

Write-Output "Process completed successfully."
