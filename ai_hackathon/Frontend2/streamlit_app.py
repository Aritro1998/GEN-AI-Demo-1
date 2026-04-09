import streamlit as st

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="AI Hackathon Frontend",
    layout="wide"
)

# --- Custom CSS ---
def set_custom_css():
    st.markdown('''
        <style>
            .main {
                background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%) !important;
            }
            .stButton > button {
                background-color: #6366f1;
                color: white;
                border-radius: 8px;
                padding: 0.5em 2em;
                font-weight: 600;
                font-size: 1.1em;
                border: none;
                transition: background 0.2s;
            }
            .stButton > button:hover {
                background: #4338ca;
            }
            .stTextInput > div > input, .stTextArea textarea {
                border-radius: 8px;
                border: 1px solid #6366f1;
                padding: 0.5em;
            }
            .stFileUploader label {
                color: #6366f1;
                font-weight: 600;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                color: #6366f1;
            }
            .block-container {
                padding-top: 2rem;
            }
        </style>
    ''', unsafe_allow_html=True)

# Apply CSS
set_custom_css()

# --- Banner ---
st.markdown("""
    <div style='display: flex; align-items: center; gap: 1em; margin-bottom: 1.5em;'>
        <img src='https://img.icons8.com/color/96/000000/artificial-intelligence.png' width='60' style='border-radius: 12px;'/>
        <div>
            <h1 style='margin-bottom: 0;'>AI Hackathon Backend API Frontend</h1>
            <p style='color: #6366f1; margin-top: 0;'>Modern, AI-powered interface for your hackathon project</p>
        </div>
    </div>
    <hr style='border: 1px solid #6366f1; margin-top: 1em; margin-bottom: 2em;'>
""", unsafe_allow_html=True)

# --- Example UI ---
st.subheader("Upload File")
uploaded_file = st.file_uploader("Choose a file")

st.subheader("Enter Prompt")
user_input = st.text_area("Your input")

if st.button("Submit"):
    st.success("Submitted successfully!")