import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Deep Audit Architecture", layout="wide")

# Specialized Prompts for Multi-Pass Analysis
TAINT_ANALYSIS_PROMPT = """
You are a Static Code Analysis Engine specializing in Taint Analysis.
Your ONLY job in this pass is to list every untrusted user input source and trace its movement through the code to identify potential unvalidated data sinks (e.g., file I/O, system commands, evaluation blocks).

Return a structured checklist of:
1. Input Sources found.
2. Untrusted Data Traversal paths.
3. Potentially Unsafe Sinks.
"""

DEEP_AUDIT_PROMPT = """
You are a Senior Security Auditor and Principal Software Architect.
Using the provided code AND the Taint Analysis report below, perform a complete security and logic audit.

Your audit MUST cover:
1. Every OWASP Top 10 / CWE vulnerability found.
2. Every potential logic bug, edge case, missing exception block, or syntax error.
3. The fully remediated, hardened Python script.

Be exhaustive. Do not skip minor edge cases or missing imports.
"""

# App Interface
st.title("🛡️ Multi-Pass Deep Code Auditor")
input_code = st.text_area("Paste Python Code for Deep Audit:", height=250)

# Retrieve Saved Secrets
api_key = st.secrets.get("GROQ_API_KEY", "")

def call_groq_api(system_prompt, user_content):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1 # Low temperature for more deterministic/strict outputs
    }
    return requests.post(url, headers=headers, json=payload)

if st.button("🚀 Run Deep Multi-Pass Audit", type="primary"):
    if not api_key:
        st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    elif not input_code.strip():
        st.warning("Please enter code to audit.")
    else:
        # Pass 1: Taint & Flow Analysis
        with st.status("Running Multi-Pass Audit Pipeline...", expanded=True) as status:
            st.write("🔍 Pass 1/2: Tracing data flows & untrusted inputs...")
            res1 = call_groq_api(TAINT_ANALYSIS_PROMPT, input_code)
            
            if res1.status_code == 200:
                taint_report = res1.json()['choices'][0]['message']['content']
                st.write("✅ Pass 1 Complete: Data flows mapped.")
                
                # Pass 2: Deep Vulnerability & Logic Audit
                st.write("🛡️ Pass 2/2: Performing comprehensive logic & security verification...")
                combined_context = f"TAINT ANALYSIS REPORT:\n{taint_report}\n\nORIGINAL CODE:\n{input_code}"
                res2 = call_groq_api(DEEP_AUDIT_PROMPT, combined_context)
                
                if res2.status_code == 200:
                    audit_result = res2.json()['choices'][0]['message']['content']
                    status.update(label="Audit Complete!", state="complete", expanded=False)
                    
                    st.markdown("### 📋 Final Multi-Pass Audit Report")
                    st.markdown(audit_result)
                else:
                    st.error("Pass 2 failed to execute.")
            else:
                st.error("Pass 1 failed to execute.")
