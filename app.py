import streamlit as st
import google.generativeai as genai
import PyPDF2
from streamlit_mic_recorder import speech_to_text

# 1. Setup the Web Page
st.set_page_config(page_title="P&G Case Study Expert", page_icon="💡")
st.title("💡 P&G Case Study Expert")
st.write("Ask me anything about the *Applying Data Science and Analytics at P&G* case study!")

# 2. Get API Key securely
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Function to read the PDF automatically
@st.cache_data
def get_pdf_text(filename):
    text = ""
    with open(filename, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# Load the PDF we uploaded
pdf_text = get_pdf_text("pg_case.pdf")

# 4. Set up the AI model
model = genai.GenerativeModel('gemini-1.5-flash')

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
    # This creates the recording button
    voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='STT')

# This creates the typing box
text_input = st.chat_input("Type your question here...")

# 7. Generate Answer
prompt = voice_text if voice_text else text_input

if prompt:
    # Show user question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Give the AI the PDF text and the question
    full_prompt = f"""
    You are an expert on the Harvard Business School case study: "Applying Data Science and Analytics at P&G".
    Here is the full text of the case study:
    ---
    {pdf_text}
    ---
    Answer the user's question clearly and in detail, relying ONLY on the case study text provided above.
    If the answer is not in the text, politely let them know.
    
    User's Question: {prompt}
    """

    # Get answer and display
    with st.chat_message("assistant"):
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
