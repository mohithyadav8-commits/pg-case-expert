import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. Page Configuration
st.set_page_config(
    page_title="P&G Case Study Expert",
    page_icon="💡",
    layout="centered"
)

# 2. Neumorphism Custom Styling (CSS)
neumorphic_css = """
<style>
    /* Background color for the whole app */
    .stApp {
        background-color: #e6ecf5;
        color: #313e52;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Attribution Header Card */
    .attribution-card {
        background: #e6ecf5;
        border-radius: 15px;
        box-shadow: 6px 6px 12px #c5c9d1, -6px -6px 12px #ffffff;
        padding: 14px 20px;
        text-align: center;
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
        margin-bottom: 25px;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-top: 8px;
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

    /* Voice / Control Section Card */
    .controls-card {
        background: #e6ecf5;
        border-radius: 16px;
        box-shadow: inset 4px 4px 8px #c5c9d1, inset -4px -4px 8px #ffffff;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Chat Input Box (Inset Neumorphism) */
    [data-testid="stChatInput"] input {
        background-color: #e6ecf5 !important;
        border-radius: 25px !important;
        box-shadow: inset 4px 4px 8px #c5c9d1, inset -4px -4px 8px #ffffff !important;
        border: none !important;
        color: #2b3a4a !important;
        padding: 12px 20px !important;
    }

    /* Streamlit default header/footer cleanup */
    #MainMenu {visibility: hidden;}
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

# 4. Header Card
st.markdown("""
<div class="header-card">
    <h1 class="header-title">💡 P&G Case Study Expert</h1>
    <p class="header-subtitle">Interactive AI Consultant for <em>Applying Data Science & Analytics at P&G</em></p>
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

# 9. Voice & Text Controls
st.markdown('<div class="controls-card"><b>🎙️ Click below to ask via voice, or use the chat bar below:</b></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

text_input = st.chat_input("Ask a question about the case study...")
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
