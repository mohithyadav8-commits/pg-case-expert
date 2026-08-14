import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. Setup the Web Page
st.set_page_config(page_title="P&G Case Study Expert", page_icon="💡")
st.title("💡 P&G Case Study Expert")
st.write("Ask me anything about the *Applying Data Science and Analytics at P&G* case study!")

# 2. Get API Key securely
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Set up the AI model
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. Upload the PDF to Gemini directly (handles scanned images perfectly!)
@st.cache_resource
def get_pdf_file():
    # This securely uploads the file to Gemini's servers so it can "read" the scanned images
    return genai.upload_file(path="pg_case.pdf")

pdf_file = get_pdf_file()

# 5. Setup Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Voice and Text Inputs
st.write("---")
st.write("**Use your microphone or type below:**")
col1, col2 = st.columns([1, 4])

with col1:
    voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

text_input = st.chat_input("Type your question here...")
prompt = voice_text if voice_text else text_input

# 7. Generate Answer
if prompt:
    # Show user question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Give the AI the PDF file and the question
    instructions = f"""
    You are an expert on the Harvard Business School case study: "Applying Data Science and Analytics at P&G".
    Please read the attached case study document.
    Answer the user's question clearly and in detail, relying ONLY on the case study document provided.
    If the answer is not in the text, politely let them know.
    
    User's Question: {prompt}
    """

    # Get answer and display
    with st.chat_message("assistant"):
        # We pass BOTH the actual visual file and the text instructions!
        response = model.generate_content([pdf_file, instructions])
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
