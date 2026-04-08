import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Searching for stable Text Generation models...")
print("-" * 50)

try:
    for model in client.models.list():
        # In the 2026 SDK, the attribute is 'supported_actions'
        # We use getattr() to be safe on Windows/Python environments
        actions = getattr(model, 'supported_actions', [])
        
        if 'generateContent' in actions:
            print(f"✅ USE THIS: {model.name}")
        elif 'generate_content' in actions: # Checking for snake_case variant
            print(f"✅ USE THIS: {model.name}")
            
except Exception as e:
    print(f"Attribute error caught: {e}")
    print("Falling back to a simple list of all IDs:")
    for model in client.models.list():
        print(f"Found: {model.name}")

print("-" * 50)