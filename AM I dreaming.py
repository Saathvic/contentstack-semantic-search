import contentstack
stack = contentstack.Stack(api_key='blt7751c3a674b2d458', delivery_token='cs18ce2f24759b33d20d1eecb8',environment= 'development')

print("Stack initialized successfully!")
print(f"API Key: {stack.api_key}")
print(f"Environment: {stack.environment}")
print("Testing connection...")

# Try to get content types
try:
    content_types = stack.content_type("").fetch()
    print("✅ Connection successful!")
    print(f"Content types response: {content_types}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
