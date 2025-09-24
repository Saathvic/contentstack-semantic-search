Write-Host "Testing optimized Render deployment..."

try {
    Write-Host "1. Testing health endpoint..."
    $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/health" -Method GET -TimeoutSec 30
    Write-Host "✅ Health Status: $($response.StatusCode)"
    $healthData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Service: $($healthData.service)"
    Write-Host "✅ Status: $($healthData.status)"
    
    Write-Host "`n2. Testing search endpoint..."
    $body = '{"query": "red shoes", "top_k": 3}'
    $headers = @{
        'Content-Type' = 'application/json'
        'Origin' = 'https://contentstack-semantic-search-71c585.eu-contentstackapps.com'
    }
    
    $searchResponse = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/search" -Method POST -Body $body -Headers $headers -TimeoutSec 45
    Write-Host "✅ Search Status: $($searchResponse.StatusCode)"
    Write-Host "✅ CORS Header: $($searchResponse.Headers['Access-Control-Allow-Origin'])"
    
    $searchData = $searchResponse.Content | ConvertFrom-Json
    Write-Host "✅ Query: $($searchData.query)"
    Write-Host "✅ Results Count: $($searchData.total_results)"
    Write-Host "✅ Status: $($searchData.status)"
    
    if ($searchData.results -and $searchData.results.Count -gt 0) {
        Write-Host "✅ First Result: $($searchData.results[0].title)"
    }
    
    Write-Host "`n🎉 All tests passed! Service is working properly."
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)"
    }
}