import streamlit as st
import base64
import os

# ==========================================
# 1. CORE CONVERSION LOGIC & MAPPING
# ==========================================
def get_anmollipi_to_unicode_map():
    return {
        # Base Consonants & Vowel Carriers
        'E': '\u0A73', 'A': '\u0A05', 'e': '\u0A72', 's': '\u0A38', 'h': '\u0A39',
        'k': '\u0A15', 'K': '\u0A16', 'g': '\u0A17', 'G': '\u0A18', '|': '\u0A19',
        'c': '\u0A1A', 'C': '\u0A1B', 'j': '\u0A1C', 'J': '\u0A1D', '\\': '\u0A1E',
        't': '\u0A1F', 'T': '\u0A20', 'f': '\u0A21', 'F': '\u0A22', 'x': '\u0A23',
        'q': '\u0A24', 'Q': '\u0A25', 'd': '\u0A26', 'D': '\u0A27', 'n': '\u0A28',
        'p': '\u0A2A', 'P': '\u0A2B', 'b': '\u0A2C', 'B': '\u0A2D', 'm': '\u0A2E',
        'X': '\u0A2F', 'r': '\u0A30', 'l': '\u0A32', 'v': '\u0A35', 'V': '\u0A5C',
        'L': '\u0A33', 'S': '\u0A36', 'z': '\u0A5B', 
        
        # Vowels & Modifiers (Includes fixes for 'a' and bindis)
        'a': '\u0A13', 'Z': '\u0A5A', '^': '\u0A59', '&': '\u0A5E', 
        'w': '\u0A3E', 'i': '\u0A3F', 'I': '\u0A40', 'u': '\u0A41', 'U': '\u0A42',
        'y': '\u0A47', 'Y': '\u0A48', 'o': '\u0A4B', 'O': '\u0A4C',
        'N': '\u0A02', 'M': '\u0A70', '~': '\u0A71', '`': '\u0A71',
        
        # Pairin (Foot) Characters (Virama + Consonant)
        'H': '\u0A4D\u0A39', 'R': '\u0A4D\u0A30', 'W': '\u0A4D\u0A35',
        
        # Numbers
        '1': '\u0A67', '2': '\u0A68', '3': '\u0A69', '4': '\u0A6A', '5': '\u0A6B',
        '6': '\u0A6C', '7': '\u0A6D', '8': '\u0A6E', '9': '\u0A6F', '0': '\u0A66'
    }

def convert_anmollipi_text(input_text):
    if not input_text:
        return ""
        
    mapping_dict = get_anmollipi_to_unicode_map()
    output_text = ""
    skip_count = 0
    
    # --- PHASE 1: Character Swapping and Direct Mapping ---
    for index in range(len(input_text)):
        if skip_count > 0:
            skip_count -= 1
            continue
            
        char = input_text[index]
        
        # Advanced Sihari Swap Logic
        if char == 'i':
            if index + 1 < len(input_text):
                next_char = input_text[index + 1]
                
                # Check for Adhak typed right after the Sihari
                if next_char in ['~', '`'] and index + 2 < len(input_text):
                    adhak = next_char
                    base_cons = input_text[index + 2]
                    
                    if index + 3 < len(input_text) and input_text[index + 3] in ['H', 'R', 'W']:
                        pairin_char = input_text[index + 3]
                        output_text += mapping_dict.get(adhak, adhak)
                        output_text += mapping_dict.get(base_cons, base_cons)
                        output_text += mapping_dict.get(pairin_char, pairin_char)
                        output_text += '\u0A3F'
                        skip_count = 3
                    else:
                        output_text += mapping_dict.get(adhak, adhak)
                        output_text += mapping_dict.get(base_cons, base_cons)
                        output_text += '\u0A3F'
                        skip_count = 2
                        
                else:
                    base_cons = next_char
                    if index + 2 < len(input_text) and input_text[index + 2] in ['H', 'R', 'W']:
                        pairin_char = input_text[index + 2]
                        output_text += mapping_dict.get(base_cons, base_cons)
                        output_text += mapping_dict.get(pairin_char, pairin_char)
                        output_text += '\u0A3F'
                        skip_count = 2
                    else:
                        output_text += mapping_dict.get(base_cons, base_cons)
                        output_text += '\u0A3F'
                        skip_count = 1
            else:
                output_text += '\u0A3F'
        else:
            output_text += mapping_dict.get(char, char)
            
    # --- PHASE 2: Unicode Normalization (Independent Vowels) ---
    output_text = output_text.replace('\u0A73\u0A41', '\u0A09')
    output_text = output_text.replace('\u0A73\u0A42', '\u0A0A')
    output_text = output_text.replace('\u0A73\u0A4B', '\u0A13')
    
    output_text = output_text.replace('\u0A05\u0A3E', '\u0A06')
    output_text = output_text.replace('\u0A05\u0A48', '\u0A10')
    output_text = output_text.replace('\u0A05\u0A4C', '\u0A14')
    
    output_text = output_text.replace('\u0A72\u0A3F', '\u0A07')
    output_text = output_text.replace('\u0A72\u0A40', '\u0A08')
    output_text = output_text.replace('\u0A72\u0A47', '\u0A0F')
                
    return output_text


# ==========================================
# 2. STREAMLIT DYNAMIC FONT LOADER
# ==========================================
def load_custom_font(font_filename="AnmolLipi.ttf"):
    """
    Reads the local .ttf file, encodes it to Base64, and dynamically injects 
    it into the Streamlit CSS so the browser can render it without installation.
    """
    if not os.path.exists(font_filename):
        st.warning(f"⚠️ '{font_filename}' not found in the directory. Input text will render as standard English characters.")
        return

    with open(font_filename, "rb") as f:
        font_data = base64.b64encode(f.read()).decode("utf-8")
        
    custom_css = f"""
    <style>
    @font-face {{
        font-family: 'AnmolLipi';
        src: url(data:font/ttf;base64,{font_data}) format('truetype');
    }}
    
    /* Target the textarea inside the FIRST column (AnmolLipi Input) */
    div[data-testid="column"]:nth-of-type(1) textarea {{
        font-family: 'AnmolLipi', sans-serif !important;
        font-size: 1.6rem !important; 
    }}
    
    /* Target the textarea inside the SECOND column (Unicode Output) */
    div[data-testid="column"]:nth-of-type(2) textarea {{
        font-family: 'Raavi', 'Noto Sans Gurmukhi','Nirmala UI', sans-serif !important;
        font-size: 1.4rem !important;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# 3. STREAMLIT WEB APP UI
# ==========================================
st.set_page_config(page_title="Gurmukhi Data Standardizer", layout="wide")

# Inject the font CSS
load_custom_font()

st.title("🏛️ Legacy Gurmukhi Data Standardizer")
st.markdown("**MCA Capstone Project:** Standardize legacy ASCII AnmolLipi documents into universally accessible Unicode (Raavi) for modern databases and searchability.")

st.divider()

# --- File Upload Section ---
st.subheader("Batch Process a Document")
uploaded_file = st.file_uploader("Upload a .txt file containing AnmolLipi text", type=["txt"])

# Initialize session state for text input so we can update it from the file uploader
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

if uploaded_file is not None:
    # Read and decode the uploaded text file
    st.session_state["input_text"] = uploaded_file.getvalue().decode("utf-8")
    st.success("File successfully loaded! Check the input box below.")

st.divider()

# --- Interactive Text Areas Section (Split Columns) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input (AnmolLipi ASCII)")
    st.info("Paste or type keystrokes here. (e.g. `ieqihws`)")
    
    # Text area for user input. Renders in AnmolLipi due to the injected CSS.
    user_input = st.text_area(
        "ASCII Text", 
        value=st.session_state["input_text"], 
        height=350, 
        label_visibility="collapsed"
    )

with col2:
    st.subheader("2. Output (Unicode/Raavi)")
    st.info("Standardized text automatically updates below. (e.g. `ਇਤਿਹਾਸ`)")
    
    # Process the text
    converted_text = convert_anmollipi_text(user_input)
    
    # Text area for output (read-only). Renders in standard Unicode fonts.
    st.text_area(
        "Unicode Text", 
        value=converted_text, 
        height=350, 
        label_visibility="collapsed", 
        disabled=True
    )
    
    # Download Button for the converted results
    if converted_text:
        st.download_button(
            label="⬇️ Download Converted Unicode as .txt",
            data=converted_text,
            file_name="standardized_punjabi_output.txt",
            mime="text/plain",
            use_container_width=True
        )