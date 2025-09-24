Write-Host "Testing with extended timeout for cold start..."

try {
    Write-Host "1. Testing health endpoint..."
    $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/health" -Method GET -TimeoutSec 60
    Write-Host "Health Status: $($response.StatusCode)"
    Write-Host "Health Response: $($response.Content)"
    
    Write-Host "`n2. Testing search endpoint with demo query..."
    $body = '{"query": "red shoes"}'
    $headers = @{
        'Content-Type' = 'application/json'
        'Origin' = 'https://contentstack-semantic-search-71c585.eu-contentstackapps.com'
    }
    
    $searchResponse = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/search" -Method POST -Body $body -Headers $headers -TimeoutSec 60
    Write-Host "Search Status: $($searchResponse.StatusCode)"
    Write-Host "CORS Header: $($searchResponse.Headers['Access-Control-Allow-Origin'])"
    Write-Host "Search Response Length: $($searchResponse.Content.Length) chars"
    
    # Parse JSON to show results count
    $json = $searchResponse.Content | ConvertFrom-Json
    if ($json.results) {
        Write-Host "Results found: $($json.results.Count)"
        Write-Host "First result: $($json.results[0].title)"
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)"
        Write-Host "Response Headers: $($_.Exception.Response.Headers)"
    }
}