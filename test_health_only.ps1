Write-Host "Testing optimized service with longer timeout..."

try {
    Write-Host "Waiting for service to warm up..."
    Start-Sleep -Seconds 30
    
    Write-Host "Testing health endpoint with extended timeout..."
    $response = Invoke-WebRequest -Uri "https://contentstack-semantic-search-0qhl.onrender.com/health" -Method GET -TimeoutSec 60
    Write-Host "✅ Health Status: $($response.StatusCode)"
    
    $healthData = $response.Content | ConvertFrom-Json
    Write-Host "✅ Service: $($healthData.service)"
    Write-Host "✅ Status: $($healthData.status)"
    Write-Host "✅ Version: $($healthData.version)"
    
    if ($healthData.components) {
        Write-Host "✅ Components:"
        foreach ($comp in $healthData.components.PSObject.Properties) {
            Write-Host "  - $($comp.Name): $($comp.Value.status)"
        }
    }
    
    Write-Host "`n🎉 Health check passed! Service is optimized and working."
    
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)"
}