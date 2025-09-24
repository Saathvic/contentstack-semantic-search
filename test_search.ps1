$body = '{"query": "red shoes"}'
$headers = @{
    'Content-Type' = 'application/json'
    'Origin' = 'https://contentstack-semantic-search-71c585.eu-contentstackapps.com'
}

try {
    Write-Host "Testing search endpoint..."
    $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/search" -Method POST -Body $body -Headers $headers -TimeoutSec 30
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "CORS Header: $($response.Headers['Access-Control-Allow-Origin'])"
    Write-Host "Response:"
    Write-Host $response.Content
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)"
    }
}