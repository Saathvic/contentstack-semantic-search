try {
    Write-Host "Testing health endpoint..."
    $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/health" -Method GET -TimeoutSec 15
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Response:"
    Write-Host $response.Content
    
    Write-Host "`nTesting search endpoint with timeout..."
    $body = '{"query": "red shoes"}'
    $headers = @{
        'Content-Type' = 'application/json'
        'Origin' = 'https://contentstack-semantic-search-71c585.eu-contentstackapps.com'
    }
    
    $searchResponse = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/search" -Method POST -Body $body -Headers $headers -TimeoutSec 45
    Write-Host "Search Status: $($searchResponse.StatusCode)"
    Write-Host "CORS Header: $($searchResponse.Headers['Access-Control-Allow-Origin'])"
    Write-Host "Search Response:"
    Write-Host $searchResponse.Content
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)"
    }
}