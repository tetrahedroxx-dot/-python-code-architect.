import streamlit as st
import google.generativeai as genai

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

# Custom CSS for styling
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

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("[Get a free Gemini API Key here](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.markdown("### How to use:")
    st.markdown("1. Paste your Gemini API key above.")
    st.markdown("2. Input your broken Python code.")
    st.markdown("3. Click **Analyze & Repair Code**.")

# Main Interface
st.markdown('<div class="main-header">⚡ Python Code Architect</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated static analysis, logic evaluation, security patcher, and code optimizer.</div>', unsafe_allow_html=True)

# Code Input Area
input_code = st.text_area(
    "Paste your Python script below:",
    height=280,
    placeholder="# Paste broken Python code here...\ndef calculate(x, y)\n    return x + y"
)

# Process Button
if st.button("🔧 Analyze & Repair Code", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed.")
    elif not input_code.strip():
        st.warning("Please paste some Python code to analyze.")
    else:
        with st.spinner("Analyzing static syntax, evaluating control flows, and applying security patches..."):
            try:
                # Configure API
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-pro",
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Generate Repair
                response = model.generate_content(input_code)
                
                st.success("Analysis Complete!")
                st.markdown("### 📋 Repair Results & Output")
                st.markdown(response.text)

                # Download Option
                st.download_button(
                    label="📥 Download Debugged Code Summary",
                    data=response.text,
                    file_name="repaired_script.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
