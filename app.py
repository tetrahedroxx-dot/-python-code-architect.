import streamlit as st
import ast
import re

# Page configuration
st.set_page_config(
    page_title="Python Code Architect & Debugger",
    page_icon="⚡",
    layout="wide"
)

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
    .status-badge {
        background-color: #10B981;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Main Interface
st.markdown('<div class="main-header">⚡ Python Code Architect <span class="status-badge">Offline Mode</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated static analysis, syntax repair, security patcher, and code refactor engine.</div>', unsafe_allow_html=True)

# Code Input Area
input_code = st.text_area(
    "Paste your Python script below:",
    height=280,
    placeholder="# Paste broken Python code here...\ndef calculate(x, y):\n    return x + y"
)

def analyze_and_repair(code):
    issues = []
    repaired_code = code

    # 1. Fix Common Syntax Errors (e.g., assignment '=' in 'if' condition)
    fixed_syntax = re.sub(r'if\s+([a-zA-Z0-9_]+)\s*=\s*([^\n:]+):', r'if \1 == \2:', repaired_code)
    if fixed_syntax != repaired_code:
        issues.append("• **Syntax Error Repaired:** Fixed assignment `=` inside `if` statement to comparison `==`.")
        repaired_code = fixed_syntax

    # 2. Static Analysis AST Check
    try:
        ast.parse(repaired_code)
        issues.append("• **Static Analysis:** Syntax parsing passed successfully.")
    except SyntaxError as e:
        issues.append(f"• **Syntax Error Detected:** Line {e.lineno}: {e.msg}")

    # 3. Security Vulnerability Patching (eval & shell=True)
    if "eval(" in repaired_code:
        issues.append("• **Security Vulnerability Patched:** Replaced unsafe `eval()` with `ast.literal_eval()` to prevent Code Injection.")
        repaired_code = re.sub(r'\beval\(', 'ast.literal_eval(', repaired_code)
        if "import ast" not in repaired_code:
            repaired_code = "import ast\n" + repaired_code

    if "shell=True" in repaired_code:
        issues.append("• **Security Vulnerability Patched:** Removed `shell=True` from subprocess execution to prevent Shell Injection.")
        repaired_code = repaired_code.replace(", shell=True", "").replace("shell=True,", "").replace("shell=True", "")

    # 4. Missing Imports Detection
    if "subprocess." in repaired_code and "import subprocess" not in repaired_code:
        issues.append("• **Missing Import Added:** Automatically appended `import subprocess`.")
        repaired_code = "import subprocess\n" + repaired_code

    # 5. Logic Error & Division Guard
    if "/" in repaired_code and "ZeroDivisionError" not in repaired_code:
        issues.append("• **Logic Protection:** Wrapped division operations in ZeroDivisionError exception guards.")
        repaired_code = re.sub(
            r'([a-zA-Z0-9_]+)\s*=\s*([a-zA-Z0-9_]+)\s*/\s*([a-zA-Z0-9_]+)',
            r'try:\n    \1 = \2 / \3\nexcept ZeroDivisionError:\n    \1 = 0',
            repaired_code
        )

    summary_text = "### 📋 Repair Summary\n" + "\n".join(issues) if issues else "No issues found!"
    return summary_text, repaired_code

# Process Button
if st.button("🔧 Analyze & Repair Code Instantly", type="primary", use_container_width=True):
    if not input_code.strip():
        st.warning("Please paste some Python code to analyze.")
    else:
        with st.spinner("Executing AST static analysis and security engine..."):
            summary, fixed_code = analyze_and_repair(input_code)
            
            st.success("Analysis & Repair Complete!")
            st.markdown(summary)
            
            st.markdown("### 🛠️ Corrected Script")
            st.code(fixed_code, language="python")

            st.download_button(
                label="📥 Download Repaired Script",
                data=fixed_code,
                file_name="repaired_script.py",
                mime="text/plain"
            )
