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

# Configure the Gemini API key
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"Failed to initialize Gemini model. Ensure your API key is correctly set as an environment variable (GOOGLE_API_KEY). Error: {e}")
    st.stop()

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="📝 Talk to the Doc!", layout="centered") # Title remains "Talk to the Doc!"

# --- Custom CSS for design ---
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
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%); /* Soft gradient background */
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        min-height: 85vh; /* Ensure it takes up most of the viewport height */
        display: flex;
        flex-direction: column;
    }

    /* Header styling */
    h1 {
        color: #E74C3C; /* A pleasant blue */
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
        display: block; /* Ensures it takes up full width for margin auto to work */
        margin: 10px auto; /* Centered horizontally */
        width: fit-content; /* Adjust width to content */
    }
    .clear-file-button button:hover {
        background-color: #C0392B; /* Darker red on hover */
        transform: translateY(-1px);
    }

    /* Clear Chat Button styling (global, centered as before) */
    .clear-chat-button-global button {
        background-color: #F7CAC9; /* Light red for clear */
        color: #C0392B; /* Darker red text */
        border-radius: 8px;
        padding: 8px 15px; /* Back to original size */
        font-size: 0.9em; /* Back to original font size */
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: none;
        display: block; /* For centering */
        margin: 5px auto; /* Centered */
        width: fit-content;
    }
    .clear-chat-button-global button:hover {
        background-color: #F5B7B1;
        transform: translateY(-2px);
    }

    /* Chat messages container (transparent, no fixed height) */
    .chat-messages-container {
        flex-grow: 1; /* Allows the chat area to fill available space */
        overflow-y: auto; /* Enable scrolling for chat history if content overflows naturally */
        padding: 15px;
        border-radius: 10px;
        /* Reverted: Removed background-color, border, box-shadow for a seamless look */
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Individual chat message styling */
    .chat-message {
        padding: 12px 18px;
        border-radius: 20px; /* More rounded corners */
        margin-bottom: 15px;
        max-width: 80%; /* Slightly wider messages */
        word-wrap: break-word;
        font-size: 0.95em;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .user-message {
        background-color: #c45b5b; 
        color: white;
        margin-left: auto; /* Align to right */
        border-bottom-right-radius: 5px; /* Tweak one corner for a chat bubble look */
    }
    .bot-message {
        background-color: #e59892; /* Bot message light gray */
        color: black;
        margin-right: auto; /* Align to left */
        border-bottom-left-radius: 5px; /* Tweak one corner for a chat bubble look */
    }

    /* Input text area and send button - FORCING FULL WIDTH */
    /* Target the main st.chat_input container */
    .st-chat-input {
        width: 100% !important;
        margin-top: 10px; /* Space from chat window */
    }
    /* Target internal divs that might be restricting width */
    .st-chat-input > div:first-child { /* This targets the container that holds the actual text area and send button */
        width: 100% !important;
    }
    /* Further specific targeting for the internal input element */
    .st-emotion-cache-1c9v6q8 { /* Specific class for the overall chat input container often used by Streamlit */
        width: 100% !important;
    }
    .st-emotion-cache-12t9k89 { /* Another common internal container */
        width: 100% !important;
    }
    .stTextInput > div:first-child > div:first-child { /* General target for the actual input box div */
        width: 100% !important;
    }
    .stTextInput div div input { /* Ensure the input field itself spans */
        width: 100% !important;
    }


    /* Loading spinner for AI thinking */
    .ai-thinking-spinner {
        display: flex;
        align-items: center;
        justify-content: flex-start; /* Align left with bot messages */
        margin-top: 10px;
        margin-bottom: 10px;
        color: #E74C3C; /* Match theme */
        font-size: 0.9em;
        gap: 8px; /* Space between text and dots */
        padding-left: 15px; /* Indent to match bot message padding */
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
        color: #4A90E2; /* Matching theme color */
        text-align: center;
        width: 100%; /* Center the spinner and text */
    }
    .stSpinner > div > div > div { /* The actual spinner icon */
        border-top-color: #4A90E2 !important; /* Force color change */
    }
    .stSpinner {
        text-align: center; /* Center the spinner container */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📝  Talk to the Doc!")
st.markdown("Upload a PDF document and let's discuss its content!")

# --- File Uploader ---
# This remains full width as it was before the columns for buttons
uploaded_file = st.file_uploader(
    "Drag and drop your PDF here",
    type="pdf",
    key="pdf_uploader",
    accept_multiple_files=False
)

# --- Clear File button (appears only if a file is loaded) ---
# Now it's not in columns, but is displayed if a file is loaded, centered.
if st.session_state.file_name:
    st.markdown('<div class="clear-file-button"></div>', unsafe_allow_html=True)
    if st.button("Clear File", key="clear_file_button"):
        st.session_state.pdf_text = ""
        st.session_state.file_name = ""
        st.rerun() # Rerun to clear the display


# --- PDF Processing Logic ---
if uploaded_file is not None and uploaded_file.name != st.session_state.file_name:
    st.session_state.pdf_text = "" # Clear previous text
    st.session_state.file_name = uploaded_file.name
    st.session_state.messages = [{"role": "assistant", "content": "Hello! 👋 Upload a PDF to start our conversation!"}] # Reset messages on new PDF upload

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
st.markdown('</div>', unsafe_allow_html=True) # Close the chat messages container


# --- User Input and AI Response Logic ---
user_query = st.chat_input(
    placeholder="Ask a question about the PDF...",
    disabled=st.session_state.pdf_text == ""
)

if user_query:
    if st.session_state.pdf_text == "":
        st.warning("Please upload a PDF first to start chatting.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_query})
        # Immediately display user message
        st.markdown(f'<div class="chat-message user-message">{user_query}</div>', unsafe_allow_html=True) # Display in the current run

        # Display AI thinking indicator
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

            # Clear thinking indicator
            ai_thinking_placeholder.empty()

            # Add bot message to chat history and display it
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.markdown(f'<div class="chat-message bot-message">{bot_response}</div>', unsafe_allow_html=True) # Display in the current run

        except Exception as e:
            ai_thinking_placeholder.empty() # Clear thinking indicator
            st.error(f"Error communicating with Gemini API: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't get a response from the AI. Please try again."})
            st.markdown(f'<div class="chat-message bot-message">Sorry, I couldn\'t get a response from the AI. Please try again.</div>', unsafe_allow_html=True)
