import streamlit as st
import joblib
import os

# Set page configuration
st.set_page_config(
    page_title="Emotion Detector 😊",
    page_icon="😊",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load model and vectorizer
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "models", "emotion_classifier.pkl")
vectorizer_path = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")

@st.cache_resource
def load_model():
    try:
        with open(vectorizer_path, "rb") as f:
            vectorizer = joblib.load(f)
        model = joblib.load(model_path)
        return model, vectorizer
    except FileNotFoundError:
        st.error("❌ Model or vectorizer file not found. Please upload them.")
        return None, None

# Load components
model, vectorizer = load_model()

# Relative path to the background image in the 'assets' folder
background_image = "assets/background.jpg"  # Make sure the image is in the 'assets' folder

# Ensure the file exists before using it
if not os.path.exists(background_image):
    st.error(f"❌ Background image not found at {background_image}")
else:
    st.markdown(f"""
        <style>
            body {{
                background-image: url("{background_image}");
                background-size: cover;
                background-attachment: fixed;
                background-position: center;
            }}
            .main-container {{
                background: rgba(255, 255, 255, 0.85);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
                width: 70%;
                margin: auto;
            }}
            h1 {{
                color: #4CAF50;
                text-align: center;
                font-family: 'Arial', sans-serif;
            }}
            textarea {{
                font-size: 16px;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 10px;
                width: 100%;
                background: rgba(255, 255, 255, 0.7);
            }}
            .stButton>button {{
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                width: 100%;
            }}
            .stButton>button:hover {{
                background-color: #45a049;
            }}
        </style>
    """, unsafe_allow_html=True)

# Sidebar for additional info
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3209/3209993.png", width=150)
st.sidebar.title("About the App")
st.sidebar.info(
    "This **Emotion Detection App** analyzes your text and predicts the **emotion** behind it. "
    "Simply enter a sentence, click **Predict**, and get the result instantly! 😊"
)

# Main UI
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("Emotion Detection App 😊")

st.write("✍️ **Enter a sentence, and the model will predict the emotion!**")

# User input
text_input = st.text_area("🔹 Enter your text here:")

# Prediction button
if st.button("🎯 Predict Emotion"):
    if text_input.strip():
        if model and vectorizer:
            with st.spinner('🔍 Analyzing emotion...'):
                text_vectorized = vectorizer.transform([text_input])
                prediction = model.predict(text_vectorized)
                st.success(f"🎉 **Predicted Emotion:** {prediction[0]} 😊")
        else:
            st.warning("⚠️ Model not loaded. Check file paths.")
    else:
        st.warning("⚠️ Please enter some text.")

st.markdown('</div>', unsafe_allow_html=True)
