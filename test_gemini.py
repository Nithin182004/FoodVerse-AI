import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("API key not found. Check your .env file.")

# 30-second timeout and no hidden retries, so it never looks frozen
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

image = Image.open("test_food.jpg")

prompt = """You are a food expert. Look at this image and tell me:
1. The name of the dish
2. The main ingredients you can see
3. An estimated calorie count per serving
4. Whether it is vegetarian or non-vegetarian
Keep the answer short and clear."""

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
]

for model in MODELS:
    try:
        print(f"Trying {model}...")
        response = client.models.generate_content(
            model=model,
            contents=[image, prompt],
        )
        print("\nSUCCESS with", model)
        print(response.text)
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as e:
        print("  Failed:", str(e)[:150])

print("\nAll models failed. Paste the Failed lines to me.")