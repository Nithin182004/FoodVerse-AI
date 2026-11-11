import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]

PROMPT = """You are a food expert. Look at this image and tell me:
1. The name of the dish
2. The main ingredients you can see
3. An estimated calorie count per serving
4. Whether it is vegetarian or non-vegetarian
Keep the answer short and clear."""

st.set_page_config(page_title="FoodVerse AI", page_icon="🍽️")
st.title("🍽️ FoodVerse AI")
st.write("Upload a photo of food and I'll tell you what it is.")

if not api_key:
    st.error("API key not found. Check your .env file.")
    st.stop()

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

uploaded = st.file_uploader("Choose a food photo", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Your photo", use_container_width=True)

    if st.button("Analyze food"):
        with st.spinner("Looking at your food..."):
            answer = None
            for model in MODELS:
                try:
                    response = client.models.generate_content(
                        model=model, contents=[image, PROMPT]
                    )
                    answer = response.text
                    break
                except Exception:
                    continue

        if answer:
            st.subheader("Result")
            st.write(answer)
        else:
            st.error("All models are busy right now. Try again in a minute.")