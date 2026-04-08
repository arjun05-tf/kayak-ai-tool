import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

if api_key:
    try:
        # Testing the specific 3.1 Flash model from your list
        response = client.models.generate_content(
            model="gemini-3.1-flash-live-preview", 
            contents="Confirming text generation for Berlin Kayak project."
        )
        print(f"Gemini 3.1 Response: {response.text}")
        print("---")
        print("Everything is green. System is ready.")
    except Exception as e:
        print(f"Connection failed: {e}")
else:
    print("Error: API Key not found.")