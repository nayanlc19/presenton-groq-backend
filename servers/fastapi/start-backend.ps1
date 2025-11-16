# Start Presenton FastAPI Backend

# Create app_data directory if it doesn't exist
$appDataPath = "D:\Claude\Projects\presenton-local\app_data"
if (-not (Test-Path $appDataPath)) {
    New-Item -ItemType Directory -Path $appDataPath -Force | Out-Null
}

$env:APP_DATA_DIRECTORY = $appDataPath
$env:CAN_CHANGE_KEYS = "false"
$env:LLM = "custom"
$env:CUSTOM_LLM_URL = "https://api.groq.com/openai/v1"
# Set CUSTOM_LLM_API_KEY environment variable before running this script
$env:CUSTOM_MODEL = "openai/gpt-oss-20b"
$env:TOOL_CALLS = "false"
$env:DISABLE_THINKING = "true"
$env:IMAGE_PROVIDER = "pixabay"
$env:PIXABAY_API_KEY = ""
$env:DISABLE_ANONYMOUS_TELEMETRY = "true"

Write-Host "Starting FastAPI Backend on http://localhost:8000"
uv run python server.py --port 8000 --reload false
