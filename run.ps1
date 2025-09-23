
# Command line parameters
param(
    [Parameter(Position = 0)]
    [string]$Mode,
    
    [string]$t = "100 years",
    [string]$cfg,
    [switch]$h
)

function Show-Help {
    Write-Host "Usage: .\run.ps1 -Mode <mode> [-t <time>] [-fileName <filename>]"
    Write-Host ""
    Write-Host "Modes:"
    Write-Host "  single        Single transfer mode"
    Write-Host "  parallel      Parallel transfer mode"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -t   <time>              Maximum simulation time (default: '100 years')"
    Write-Host "  -cfg <config>            Configuration file"
    Write-Host "  -h                       Show help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run.ps1 single -t '100 years'"
    Write-Host "  .\run.ps1 parallel -t '100 years'"
}

# Check if help was requested
if ($h -or $Mode -eq "-h" -or $Mode -eq "--help") {
    Show-Help
    exit 0
}

# Check if mode is provided
if ([string]::IsNullOrEmpty($Mode)) {
    Write-Error "Error: Mode required."
    Show-Help
    exit 1
}


if ([string]::IsNullOrEmpty($cfg)) {
    Write-Error "Error: Configuration file required."
    Show-Help
    exit 1
}

# Extract the file name from the config path
$cfgBaseName = [System.IO.Path]::GetFileNameWithoutExtension($cfg)

$MAX_T = $t
# Replace spaces with underscores for filename compatibility
$FILENAME = $MAX_T -replace ' ', '_'
$cmd = @(
    "python", ".\storage.py", $cfg,
    "--seed", 42,
    "--max-t", "$MAX_T"
)

switch ($Mode.toLower()) {
    "single" {
        $PLOT_DIR = "./plots/single"
        $RES_DIR = "./results/single"
        $NPZ = "$RES_DIR/${FILENAME}_$cfgBaseName" # without extension
        $IMG = "$PLOT_DIR/${FILENAME}_$cfgBaseName.png"
    }
    "parallel" {
        $PLOT_DIR = "./plots/parallel"
        $RES_DIR = "./results/parallel"
        $NPZ = "$RES_DIR/${FILENAME}_$cfgBaseName" # without extension
        $IMG = "$PLOT_DIR/${FILENAME}_$cfgBaseName.png"

        $cmd += "--parallel-transfers"
    }
    default {
        Write-Host "Error: Invalid mode specified."
        Show-Help
        exit 1
    }
}

New-Item -ItemType Directory -Force -Path $PLOT_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $RES_DIR | Out-Null

# Remove existing files
if (Test-Path $NPZ) { Remove-Item $NPZ* }
if (Test-Path $IMG) { Remove-Item $IMG* }

$cmd += "--save-metrics"
$cmd += $NPZ

Write-Host "Running simulation in '$Mode' mode for maximum time '$MAX_T'..."
Write-Host "$cmd"
& $cmd[0] $cmd[1..($cmd.Length - 1)]

if ($lastexitcode -ne 0) {
    write-error "simulation failed with exit code $lastexitcode"
    exit $lastexitcode
}

# Generate plots
& python .\analyze_transfers.py "${NPZ}.npz" --plot-name $IMG