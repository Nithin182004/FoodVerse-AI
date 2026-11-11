# 🍽️ FoodVerse AI

A multimodal food intelligence app. Upload a photo of a dish and the AI identifies it, lists the visible ingredients, estimates calories, and tells you if it is vegetarian or non-vegetarian.

**Live demo:** https://foodverse-ai-nithin.streamlit.app/

## Features

- Upload a food photo (JPG or PNG)
- Dish name and main ingredients
- Estimated calories per serving
- Vegetarian / non-vegetarian detection
- Automatic fallback to another model when one is busy

## Tech Stack

- Python
- Streamlit (web interface)
- Google Gemini API (`google-genai`)
- Pillow (image handling)
- python-dotenv (API key management)

## Getting Started

### 1. Clone the repository

```
git clone https://github.com/Nithin182004/FoodVerse-AI.git
cd FoodVerse-AI
```

### 2. Create and activate a virtual environment

```
python -m venv venv
venv\Scripts\activate
```

On Mac/Linux, use `source venv/bin/activate` instead.

### 3. Install the dependencies

```
pip install -r requirements.txt
```

### 4. Add your API key

Get a free key at [aistudio.google.com](https://aistudio.google.com). Create a file named `.env` in the project folder with this line:

```
GEMINI_API_KEY=your_key_here
```

The `.env` file is listed in `.gitignore`, so your key is never uploaded.

### 5. Run the app

```
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Project Structure

```
FoodVerse-AI/
├── app.py            # Streamlit app
├── test_gemini.py    # Quick API test script
├── requirements.txt  # Python dependencies
├── .gitignore        # Keeps .env and venv out of Git
└── README.md
```

## Roadmap

- [x] Photo analysis with Gemini
- [x] Streamlit interface
- [x] Improved layout with result cards
- [x] Chat for follow-up questions ("Is this healthy?")
- [ ] Accurate nutrition lookup with the USDA API
- [ ] Barcode scanning with Open Food Facts
- [ ] Deployment on Streamlit Community Cloud

## Note

Calorie values are AI estimates, not medical or dietary advice.
