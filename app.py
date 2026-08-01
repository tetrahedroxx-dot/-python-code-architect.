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
3. ERROR HANDLING & SECURITY: Implement missing Try-Except blocks for risky operations (I/O, API calls) and fix any vulnerable patterns (e.g., shell=True in subprocess, pickle deserialization).
4. REFACTOR & OPTIMIZE: Apply PEP 8 styling guidelines and optimize slow or redundant operations while keeping the original architecture intact.

OUTPUT FORMAT REQUIREMENTS:
- Provide a brief 3-sentence summary of what broke and why.
- Provide the FULL corrected script inside a single Markdown python code block. Do not use placeholders or comments like "# insert original code here".
"""

# Sample Buggy Code Snippets for 1-Click Testing
SAMPLE_CODES = {
    "Select an example...": "",
    "🔥 RCE & Command Injection": """import subprocess, pickle, base64

def process_data(user_input, session_b64):
    # Security Flaws: Insecure pickle & shell=True command injection
    data = pickle.loads(base64.b64decode(session_b64))
    subprocess.run("echo " + user_input, shell=True)
    return data""",
    
    "⚠️ Syntax & Typo Bug": """def calculate_average(numbers):
    # Syntax Error (= instead of ==) and Typo in variable
    if numbers = []:
        return 0
    total_sum = sum(num_list) # Typo: num_list
    return total_sum / len(numbers)""",
    
    "⚡ Unhandled File I/O & ZeroDivision": """def read_and_divide(filename, divisor):
    # Missing Try-Except and unclosed file handle
    f = open(filename, 'r')
    content = f.read()
    result = len(content) / divisor
    return result"""
}

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
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    provider = st.radio("Select AI Provider:", ["Groq API (Free & Fast)", "Google Gemini API (Stable v1)"])
    
    st.markdown("---")
    
    # Auto-load key from Streamlit secrets if available
    saved_groq_key = st.secrets.get("GROQ_API_KEY", "")
    saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if provider == "Groq API (Free & Fast)":
        if saved_groq_key:
            api_key = saved_groq_key
            st.success("✅ Saved Groq API Key Active!")
        else:
            api_key = st.text_input("Enter Groq API Key:", type="password")
            st.markdown("[Get free Groq Key](https://console.groq.com/keys)")
    else:
        if saved_gemini_key:
            api_key = saved_gemini_key
            st.success("✅ Saved Gemini API Key Active!")
        else:
            api_key = st.text_input("Enter Gemini API Key:", type="password")
            st.markdown("[Get free Gemini Key](https://aistudio.google.com/app/apikey)")

    st.markdown("---")
    st.markdown("### 🧪 Quick Test Presets:")
    selected_sample = st.selectbox("Load Sample Buggy Code:", list(SAMPLE_CODES.keys()))

# Main Header
st.markdown('<div class="main-header">⚡ Python Code Architect & Debugger</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated static analysis, logic evaluation, security patcher, and PEP 8 code optimizer.</div>', unsafe_allow_html=True)

# Code Input Logic (Auto-populates if sample selected)
default_code = SAMPLE_CODES[selected_sample] if selected_sample != "Select an example..." else ""
input_code = st.text_area(
    "Paste your Python script below:",
    value=default_code,
    height=240,
    placeholder="# Paste broken Python code here or select a sample preset from the sidebar..."
)

def call_gemini_v1(key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key.strip()}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, json=payload)

def call_groq(key, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    return requests.post(url, headers=headers, json=payload)

# Process Button
if st.button("🔧 Analyze & Repair Code", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter or save an API Key in the sidebar.")
    elif not input_code.strip():
        st.warning("Please paste some Python code to analyze.")
    elif len(input_code) > 10000:
        st.error("Code snippet is too large! Please input scripts under 10,000 characters.")
    else:
        with st.spinner("AI Architect running static analysis, logic checks, and security patches..."):
            
            # Input Sanitization Guardrail
            guarded_prompt = f"{SYSTEM_PROMPT}\n\nStrict Task: Analyze and fix ONLY the following Python code:\n{input_code}"
            
            if provider == "Groq API (Free & Fast)":
                res = call_groq(api_key, guarded_prompt)
                data = res.json()
                if res.status_code == 200:
                    output_text = data['choices'][0]['message']['content']
                    success = True
                else:
                    err = data.get('error', {}).get('message', 'API Error')
                    st.error(f"Groq API Error ({res.status_code}): {err}")
                    success = False
            else:
                res = call_gemini_v1(api_key, guarded_prompt)
                data = res.json()
                if res.status_code == 200:
                    output_text = data['candidates'][0]['content']['parts'][0]['text']
                    success = True
                else:
                    err = data.get('error', {}).get('message', 'API Error')
                    st.error(f"Gemini API Error ({res.status_code}): {err}")
                    success = False

            if success:
                st.success("Analysis & Code Architecture Complete!")
                
                # Dual-Column Display Layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🔴 Original Input Code")
                    st.code(input_code, language="python")
                    
                with col2:
                    st.markdown("### 📋 AI Architect Diagnosis & Fixed Code")
                    st.markdown(output_text)

                st.download_button(
                    label="📥 Download Full Report & Fixed Code",
                    data=output_text,
                    file_name="repaired_script.md",
                    mime="text/markdown"
                )
