import streamlit as st
import requests

# Page configuration
st.set_page_config(
    page_title="Python Code Architect & Debugger",
    page_icon="⚡",
    layout="wide"
)

# System Prompt Definition
SYSTEM_PROMPT = """
You are an elite, autonomous Python Code Architect and automated debugging agent. Your sole purpose is to analyze broken Python scripts, find errors, and return fully functional, corrected code without changing the original logic.

Apply this strict, step-by-step resolution chain to the provided script:
1. STATIC ANALYSIS: Check for syntax errors, improper indentation, missing imports, typos, or undefined variables.
2. LOGIC EVALUATION: Analyze control flows, loop conditions, data mutations, and type mismatches.
3. ERROR HANDLING & SECURITY: Implement missing Try-Except blocks for risky operations (I/O, API calls) and fix any vulnerable patterns (e.g., shell=True in subprocess).
4. REFACTOR & OPTIMIZE: Apply PEP 8 styling guidelines and optimize slow or redundant operations while keeping the original architecture intact.

OUTPUT FORMAT REQUIREMENTS:
- Provide a brief 3-sentence summary of what broke and why.
- Provide the FULL corrected script inside a single Markdown python code block. Do not use placeholders or comments like "# insert original code here".
"""

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("[Get a free Gemini API Key here](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    selected_model = st.selectbox(
        "Select AI Model:",
        ["Auto-Fallback (Recommended)", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    )
    
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("1. Paste your Gemini API key above.")
    st.markdown("2. Input your broken Python code.")
    st.markdown("3. Click **Analyze & Repair Code**.")

# Main Interface
st.markdown('<div class="main-header">⚡ Python Code Architect</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered static analysis, logic evaluation, security patcher, and code optimizer.</div>', unsafe_allow_html=True)

# Code Input Area
input_code = st.text_area(
    "Paste your Python script below:",
    height=280,
    placeholder="# Paste broken Python code here...\ndef calculate(x, y):\n    return x + y"
)

def call_gemini_api(model_name, key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key.strip()}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, json=payload)

# Process Button
if st.button("🔧 Analyze & Repair Code", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed.")
    elif not input_code.strip():
        st.warning("Please paste some Python code to analyze.")
    else:
        with st.spinner("AI Agent analyzing syntax, control flows, and security..."):
            full_prompt = f"{SYSTEM_PROMPT}\n\nHere is the broken Python script to analyze and repair:\n\n{input_code}"
            
            # Determine candidate models to attempt
            if selected_model == "Auto-Fallback (Recommended)":
                candidate_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
            else:
                candidate_models = [selected_model]
            
            success = False
            last_error = ""

            for model_name in candidate_models:
                try:
                    res = call_gemini_api(model_name, api_key, full_prompt)
                    data = res.json()
                    
                    if res.status_code == 200:
                        output_text = data['candidates'][0]['content']['parts'][0]['text']
                        st.success(f"Analysis Complete! (Powered by {model_name})")
                        st.markdown("### 📋 Repair Results & Output")
                        st.markdown(output_text)

                        st.download_button(
                            label="📥 Download Debugged Code Summary",
                            data=output_text,
                            file_name="repaired_script.md",
                            mime="text/markdown"
                        )
                        success = True
                        break
                    else:
                        last_error = data.get('error', {}).get('message', 'Unknown Error')
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if not success:
                st.error(f"API Attempt Failed: {last_error}\n\nTip: Please wait 30 seconds for the free tier quota to reset, or click the link in the sidebar to create a fresh API key.")
