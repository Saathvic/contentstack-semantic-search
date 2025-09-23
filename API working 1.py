import requests

stack_api_key = "bltaec246e239ee5b66"
delivery_token = "cs9bc546f25d43cfbc9312632d"
environment = "development"
content_type = "product"  # Change to your actual content type UID

# Europe region endpoint
url = f"https://eu-cdn.contentstack.com/v3/content_types/{content_type}/entries?environment={environment}"

headers = {
    "api_key": stack_api_key,
    "access_token": delivery_token,
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    entries = data.get("entries", [])
    for entry in entries:
        print(entry)
else:
    print(f"Failed to fetch entries: {response.status_code} {response.text}")
