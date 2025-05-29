import streamlit as st
import io
from PyPDF2 import PdfReader
import google.generativeai as genai
import os

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file.
    """
    text = ""
    try:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None
    return text

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello! 👋 Upload a PDF to start our conversation!"})

# Initialize PDF text and filename in session state
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "file_name" not in st.session_state:
    st.session_state.file_name = ""

# --- Streamlit Page Configuration (always runs) ---
st.set_page_config(page_title="📝 Talk to the Doc!", layout="centered")

# --- Custom CSS for design (always runs, as it affects the overall page) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Main container styling */
    .main .block-container {
        max-width: 900px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }

    .css-1jc7ptx, .css-1dp5vir { /* Specific Streamlit classes for main content area */
        /* These were removed in the previous step to get rid of the outer blue box */
        min-height: 85vh; /* Ensure it takes up most of the viewport height */
        display: flex;
        flex-direction: column;
    }

    /* Header styling */
    h1 {
        color: #E74C3C; /* A pleasant red */
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }

    /* Subheader/description */
    .stMarkdown p {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 1.5em;
    }

    /* Style for the internal 'Browse files' button within the uploader (still applies) */
    .stFileUploader span[data-testid="stFileUploadDropzone"] button {
        background-color: #4A90E2 !important; /* Blue for 'Browse files' */
        color: white !important;
        border: none !important;
        padding: 8px 15px !important;
        border-radius: 8px !important;
        font-size: 0.9em !important;
        transition: background-color 0.3s ease, transform 0.3s ease !important;
    }
    .stFileUploader span[data-testid="stFileUploadDropzone"] button:hover {
        background-color: #357ABD !important;
        transform: translateY(-1px) !important;
    }

    /* Clear File Button styling */
    .clear-file-button button {
        background-color: #E74C3C; /* Red fill */
        color: white; /* White text */
        border-radius: 8px;
        padding: 8px 15px;
        font-size: 0.9em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: none;
        display: block;
        margin: 10px auto;
        width: fit-content;
    }
    .clear-file-button button:hover {
        background-color: #C0392B;
        transform: translateY(-1px);
    }

    /* Clear Chat Button styling (global, centered as before) */
    .clear-chat-button-global button {
        background-color: #F7CAC9; /* Light red for clear */
        color: #C0392B; /* Darker red text */
        border-radius: 8px;
        padding: 8px 15px;
        font-size: 0.9em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: none;
        display: block;
        margin: 5px auto;
        width: fit-content;
    }
    .clear-chat-button-global button:hover {
        background-color: #F5B7B1;
        transform: translateY(-2px);
    }

    /* Chat messages container (transparent, no fixed height) */
    .chat-messages-container {
        flex-grow: 1;
        overflow-y: auto;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Individual chat message styling */
    .chat-message {
        padding: 12px 18px;
        border-radius: 20px;
        margin-bottom: 15px;
        max-width: 80%;
        word-wrap: break-word;
        font-size: 0.95em;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .user-message {
        background-color: #c45b5b;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    .bot-message {
        background-color: #e59892;
        color: black;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }

    /* Input text area and send button - FORCING FULL WIDTH */
    .st-chat-input {
        width: 100% !important;
        margin-top: 10px;
    }
    .st-chat-input > div:first-child {
        width: 100% !important;
    }
    .st-emotion-cache-1c9v6q8 {
        width: 100% !important;
    }
    .st-emotion-cache-12t9k89 {
        width: 100% !important;
    }
    .stTextInput > div:first-child > div:first-child {
        width: 100% !important;
    }
    .stTextInput div div input {
        width: 100% !important;
    }

    /* Loading spinner for AI thinking */
    .ai-thinking-spinner {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin-top: 10px;
        margin-bottom: 10px;
        color: #E74C3C;
        font-size: 0.9em;
        gap: 8px;
        padding-left: 15px;
    }

    .ai-thinking-dots span {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #E74C3C;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    .ai-thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
    .ai-thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
    .ai-thinking-dots span:nth-child(3) { animation-delay: 0s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1.0); }
    }

    /* Spinner for PDF processing */
    .stSpinner > div > div {
        color: #4A90E2;
        text-align: center;
        width: 100%;
    }
    .stSpinner > div > div > div {
        border-top-color: #4A90E2 !important;
    }
    .stSpinner {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("📝 Talk to the Doc!")
st.markdown("Upload a PDF document and let's discuss its content!")

# --- API Key Input Section ---
# Retrieve API key from session state or environment variable
# Priority: 1. Input field (if filled), 2. Environment variable
api_key_from_env = os.environ.get("GOOGLE_API_KEY")

if "gemini_api_key_input" not in st.session_state:
    st.session_state.gemini_api_key_input = "" # Initialize if not present

# Use a placeholder if no env var, otherwise show masked env var
placeholder_text = "Enter your Google Gemini API key here"
if api_key_from_env:
    placeholder_text = "API key loaded from environment variable (or enter new key)"
    if not st.session_state.gemini_api_key_input: # If input is empty, pre-fill with env var if available
        st.session_state.gemini_api_key_input = api_key_from_env

gemini_api_key = st.text_input(
    "Google Gemini API Key",
    type="password",
    value=st.session_state.gemini_api_key_input,
    placeholder=placeholder_text,
    help="You can get your API key from https://aistudio.google.com/app/apikey",
    key="gemini_api_key_input_widget" # Use a distinct key for the widget
)

# Store the input value back into session state for persistence
st.session_state.gemini_api_key_input = gemini_api_key

current_api_key = st.session_state.gemini_api_key_input.strip() # Use the one from the input field


# Only proceed if an API key is available
if not current_api_key:
    st.warning("Please enter your Google Gemini API Key to proceed.")
    st.stop() # Stop the execution of the rest of the app

# Configure the Gemini API key now that we have it
try:
    genai.configure(api_key=current_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    # Test a small call to ensure the key is valid (optional, but good for feedback)
    # model.generate_content("hello", generation_config=genai.types.GenerationConfig(max_output_tokens=1))
except Exception as e:
    st.error(f"Failed to initialize Gemini model or API key is invalid. Error: {e}")
    st.stop() # Stop if the API key is problematic

# --- Rest of your application code goes here (it will only run if API key is valid) ---

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "", # Label is empty
    type="pdf",
    key="pdf_uploader",
    accept_multiple_files=False
)

# --- Clear File button (appears only if a file is loaded) ---
if st.session_state.file_name:
    st.markdown('<div class="clear-file-button"></div>', unsafe_allow_html=True)
    if st.button("Clear File", key="clear_file_button"):
        st.session_state.pdf_text = ""
        st.session_state.file_name = ""
        st.rerun()

# --- PDF Processing Logic ---
if uploaded_file is not None and uploaded_file.name != st.session_state.file_name:
    st.session_state.pdf_text = ""
    st.session_state.file_name = uploaded_file.name
    st.session_state.messages = [{"role": "assistant", "content": "Hello! 👋 Upload a PDF to start our conversation!"}]

    with st.spinner(f"✨ Processing '{uploaded_file.name}'... This might take a moment."):
        pdf_content = extract_text_from_pdf(uploaded_file)
        if pdf_content:
            st.session_state.pdf_text = pdf_content
            st.session_state.messages.append({"role": "assistant", "content": f"🎉 Successfully loaded \"{uploaded_file.name}\". What would you like to know about it?"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Oops! 😔 Failed to process PDF. Please try a different file."})
    st.rerun()

# --- Global Clear Chat Button (centered, as it was before) ---
st.markdown('<div class="clear-chat-button-global"></div>', unsafe_allow_html=True)
if st.button("Clear Chat & Start Over", key="clear_all_button"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello! 👋 Upload a PDF to start our conversation!"}]
    st.session_state.pdf_text = ""
    st.session_state.file_name = ""
    st.rerun()

# --- Chat Message Display Area ---
st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- User Input and AI Response Logic ---
user_query = st.chat_input(
    placeholder="Ask a question about the PDF...",
    disabled=st.session_state.pdf_text == ""
)

if user_query:
    if st.session_state.pdf_text == "":
        st.warning("Please upload a PDF first to start chatting.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.markdown(f'<div class="chat-message user-message">{user_query}</div>', unsafe_allow_html=True)

        ai_thinking_placeholder = st.empty()
        ai_thinking_placeholder.markdown(
            f'<div class="ai-thinking-spinner">AI is thinking <div class="ai-thinking-dots"><span></span><span></span><span></span></div></div>',
            unsafe_allow_html=True
        )

        try:
            prompt = f"""Based on the following PDF content, answer the user's question. If the answer is not in the PDF, state that you cannot find the information.

            PDF Content:
            \"\"\"
            {st.session_state.pdf_text}
            \"\"\"

            User Question: {user_query}

            Bot Answer:"""

            response = model.generate_content(prompt)
            bot_response = response.text

            ai_thinking_placeholder.empty()
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.markdown(f'<div class="chat-message bot-message">{bot_response}</div>', unsafe_allow_html=True)

        except Exception as e:
            ai_thinking_placeholder.empty()
            st.error(f"Error communicating with Gemini API: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't get a response from the AI. Please try again."})
            st.markdown(f'<div class="chat-message bot-message">Sorry, I couldn\'t get a response from the AI. Please try again.</div>', unsafe_allow_html=True)
