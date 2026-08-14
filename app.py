import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. Page Configuration
st.set_page_config(
    page_title="P&G Case Study Expert",
    page_icon="💡",
    layout="centered"
)

# 2. Advanced Neumorphism Styling (CSS)
neumorphic_css = """
<style>
    /* Overall App Background */
    .stApp {
        background-color: #e6ecf5;
        color: #313e52;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Fix the white background bar at the bottom */
    [data-testid="stBottom"] {
        background-color: transparent !important;
    }
    [data-testid="stBottom"] > div {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Neumorphic Chat Input Box */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: #e6ecf5 !important;
        border-radius: 25px !important;
        box-shadow: inset 4px 4px 8px #c5c9d1, inset -4px -4px 8px #ffffff !important;
        border: none !important;
        padding: 5px 15px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #2b3a4a !important;
    }

    /* Attribution Header Card */
    .attribution-card {
        background: #e6ecf5;
        border-radius: 15px;
        box-shadow: 6px 6px 12px #c5c9d1, -6px -6px 12px #ffffff;
        padding: 14px 20px;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    .attribution-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #2b3a4a;
        margin: 0;
    }
    .attribution-sub {
        font-size: 0.85rem;
        color: #5c6b7d;
        margin: 3px 0 0 0;
    }

    /* Main Title Header Card */
    .header-card {
        background: #e6ecf5;
        border-radius: 20px;
        box-shadow: 8px 8px 16px #c5c9d1, -8px -8px 16px #ffffff;
        padding: 24px;
        text-align: center;
        margin-bottom: 35px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0369a1; 
        margin-top: 10px;
        letter-spacing: 0.5px;
    }

    /* Neumorphic Chat Messages */
    [data-testid="stChatMessage"] {
        background: #e6ecf5 !important;
        border-radius: 18px !important;
        box-shadow: 6px 6px 12px #c5c9d1, -6px -6px 12px #ffffff !important;
        padding: 16px 20px !important;
        margin-bottom: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Mic Section Spacing */
    .mic-label {
        text-align: center;
        font-weight: 700;
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }

    /* Clean UI */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(neumorphic_css, unsafe_allow_html=True)

# 3. Attribution Card
st.markdown("""
<div class="attribution-card">
    <p class="attribution-title">Developed by <strong>Mohith Yadav</strong></p>
    <p class="attribution-sub">Under the Guidance of <strong>Dr. Shweta Puneet</strong></p>
</div>
""", unsafe_allow_html=True)

# 4. Header Card with NEW Professional Subtitle
st.markdown("""
<div class="header-card">
    <h1 class="header-title">💡 P&G Case Study Expert</h1>
    <p class="header-subtitle">Executive Decision-Support: Decoding P&G's Data-Driven Transformation</p>
</div>
""", unsafe_allow_html=True)

# 5. Get API Key securely
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 6. AI Model Setup
model = genai.GenerativeModel('gemini-2.5-flash')

# 7. Read PDF directly into memory
@st.cache_data
def get_pdf_bytes():
    with open("pg_case.pdf", "rb") as file:
        return file.read()

pdf_bytes = get_pdf_bytes()

# 8. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. Voice & Text Controls (Centered and visually dynamic)
st.markdown('<p class="mic-label">🎙️ Speak Your Question Below:</p>', unsafe_allow_html=True)

# Using columns to perfectly center the mic button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Dynamic prompts act as our visual highlight when clicked
    voice_text = speech_to_text(
        language='en', 
        use_container_width=True, 
        just_once=True, 
        key='STT',
        start_prompt="🟢 Start Voice Recording",
        stop_prompt="🔴 🎙️ RECORDING... (Click to Stop)"
    )

st.write("---")

text_input = st.chat_input("Or type your case study question here...")
prompt = voice_text if voice_text else text_input

# 10. Generate and Display Response
if prompt:
    # Display user's question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    instructions = f"""
    You are an expert on the Harvard Business School case study: "Applying Data Science and Analytics at P&G".
    Please read the attached case study document.
    Answer the user's question clearly and in detail, relying ONLY on the case study document provided.
    If the answer is not in the text, politely let them know.
    
    User's Question: {prompt}
    """

    with st.chat_message("assistant"):
        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
        
        response = model.generate_content([pdf_part, instructions])
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
