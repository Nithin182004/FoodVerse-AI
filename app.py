import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

# Key from .env (your laptop) or Streamlit secrets (when deployed online)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
]

PROMPT = """You are a food expert. Look at this image and reply with ONLY a JSON object
with exactly these keys:
{
  "dish_name": "name of the dish",
  "cuisine": "cuisine or region, e.g. Hyderabadi",
  "description": "one short sentence about the dish",
  "ingredients": ["main visible ingredients"],
  "calories": 0,
  "protein_g": 0,
  "carbs_g": 0,
  "fat_g": 0,
  "diet": "Vegetarian or Non-vegetarian",
  "health_tip": "one short, practical health tip"
}
Numbers are estimates for one typical serving. If the image is not food,
set dish_name to "Not a food image" and use 0 for the numbers."""

st.set_page_config(page_title="FoodVerse AI", page_icon="🍽️", layout="wide")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("About")
    st.write(
        "FoodVerse AI looks at a food photo and tells you the dish, "
        "ingredients, estimated nutrition and diet type. You can then "
        "chat with it about the dish."
    )
    st.caption("Calories and nutrients are AI estimates, not medical advice.")
    if "model_used" in st.session_state:
        st.divider()
        st.caption(f"Model used: {st.session_state['model_used']}")
    if st.session_state.get("chat"):
        if st.button("Clear chat"):
            st.session_state["chat"] = []
            st.rerun()

# ---------- Header ----------
st.title("🍽️ FoodVerse AI")
st.write("Upload a photo of food and get an instant breakdown.")

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


def analyze(image):
    """Try each model in order. Returns (result_dict, model_name) or (None, None)."""
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=[image, PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text), model
        except Exception:
            continue
    return None, None


def chat_reply(image, result, history, question):
    """Answer a follow-up question about the dish. Returns text or None."""
    instructions = (
        "You are FoodVerse AI, a friendly food and nutrition assistant. "
        "The user uploaded the photo of a dish. Here is the earlier analysis: "
        f"{json.dumps(result)}\n"
        "Answer the user's follow-up questions about this dish clearly and briefly. "
        "For health questions, give general information and remind them that "
        "you are not a doctor or dietitian when it matters."
    )
    convo = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history)
    prompt = f"{instructions}\n\nConversation so far:\n{convo}\n\nUser: {question}\nAssistant:"

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model, contents=[image, prompt]
            )
            return response.text
        except Exception:
            continue
    return None


uploaded = st.file_uploader("Choose a food photo", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")

    left, right = st.columns([1, 1.3], gap="large")

    with left:
        st.image(image, caption="Your photo", width="stretch")
        analyze_clicked = st.button("Analyze food", type="primary")

    if analyze_clicked:
        with st.spinner("Looking at your food..."):
            result, model_used = analyze(image)
        if result:
            st.session_state["result"] = result
            st.session_state["model_used"] = model_used
            st.session_state["chat"] = []  # new dish, start a fresh chat
        else:
            st.session_state.pop("result", None)
            st.error("All models are busy right now. Try again in a minute.")

    with right:
        result = st.session_state.get("result")
        if result:
            st.subheader(result.get("dish_name", "Unknown dish"))
            st.caption(result.get("cuisine", ""))
            st.write(result.get("description", ""))

            diet = result.get("diet", "")
            if diet.lower().startswith("veg"):
                st.success("🟢 Vegetarian")
            else:
                st.error("🔴 Non-vegetarian")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{result.get('calories', 0)} kcal")
            c2.metric("Protein", f"{result.get('protein_g', 0)} g")
            c3.metric("Carbs", f"{result.get('carbs_g', 0)} g")
            c4.metric("Fat", f"{result.get('fat_g', 0)} g")

            st.markdown("**Main ingredients**")
            ingredients = result.get("ingredients", [])
            st.markdown(" ".join(f"`{i}`" for i in ingredients))

            st.info(f"💡 {result.get('health_tip', '')}")
        else:
            st.write("Click **Analyze food** to see the results here.")

    # ---------- Chat ----------
    result = st.session_state.get("result")
    if result:
        st.divider()
        st.subheader("💬 Ask about this dish")
        st.caption('Try: "Is this healthy?", "Give me the recipe", "Make it vegetarian"')

        if "chat" not in st.session_state:
            st.session_state["chat"] = []

        for msg in st.session_state["chat"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("Ask a question about this dish...")
        if question:
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = chat_reply(
                        image, result, st.session_state["chat"], question
                    )
                if answer:
                    st.write(answer)
                else:
                    answer = "Sorry, all models are busy right now. Please try again."
                    st.error(answer)
            st.session_state["chat"].append({"role": "user", "content": question})
            st.session_state["chat"].append({"role": "assistant", "content": answer})