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
# (Using gemini-2.5-flash as it is highly stable for direct document reading)
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. Read the PDF directly into memory as raw bytes
@st.cache_data
def get_pdf_bytes():
    with open("pg_case.pdf", "rb") as file:
        return file.read()

pdf_bytes = get_pdf_bytes()

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

    # Give the AI the instructions
    instructions = f"""
    You are an expert on the Harvard Business School case study: "Applying Data Science and Analytics at P&G".
    Please read the attached case study document.
    Answer the user's question clearly and in detail, relying ONLY on the case study document provided.
    If the answer is not in the text, politely let them know.
    
    User's Question: {prompt}
    """

    # Get answer and display
    with st.chat_message("assistant"):
        # We package the raw PDF bytes and hand them directly to the model
        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
        
        response = model.generate_content([pdf_part, instructions])
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
