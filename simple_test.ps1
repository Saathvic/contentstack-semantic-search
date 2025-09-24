Write-Host "Trying a simple curl test to health endpoint..."

# Use curl if available, otherwise use Invoke-WebRequest
try {
    $curlExists = Get-Command curl -ErrorAction SilentlyContinue
    if ($curlExists) {
        Write-Host "Using curl for the test..."
        $output = curl -s -w "`nStatus: %{http_code}`nTime: %{time_total}s`n" "https://contentstack-semantic-search-0qhl.onrender.com/health" --max-time 60
        Write-Host $output
    } else {
        Write-Host "Using Invoke-WebRequest for the test..."
        $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/health" -Method GET -TimeoutSec 60
        Write-Host "Status: $($response.StatusCode)"
        Write-Host "Content: $($response.Content)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}