import streamlit as st
import json
from src.utils import extract_text_from_file
from src.logic import calculate_health_score
from src.agents import analyst_model, consultant_model, negotiator_model, reporter_model

# --- CACHED AI FUNCTION (The Fix for Consistency) ---
@st.cache_data(show_spinner=False)
def run_ai_analysis(contract_text):
    """
    This function caches the result. If you upload the same file text,
    it returns the saved JSON immediately without calling Gemini again.
    This guarantees 100% identical scores for identical files.
    """
    prompt = f"""
    Analyze contract: "{contract_text[:30000]}" ...
    
    Find specific risks. Return a JSON list.
    
    1. Unlimited Liability -> ID: "LIABILITY"
    2. Asymmetric Termination -> ID: "TERMINATION"
    3. IP Overreach (personal time) -> ID: "IP"
    4. Non-compete (>1yr) -> ID: "NON_COMPETE"
    5. Payment Terms (>Net-45) -> ID: "PAYMENT"
    6. Auto-renewal (Hard to cancel) -> ID: "AUTO_RENEWAL"
    7. Missing Security Clauses -> ID: "SECURITY"
    8. Unrestricted Subcontracting -> ID: "SUBCONTRACTING"
    
    Return format: 
    [
      {{ "risk_id": "LIABILITY", "detected": true, "explanation": "...", "exact_text": "..." }}
    ]
    """
    try:
        resp = analyst_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(resp.text)
    except Exception as e:
        return []

def main():
    # --- UI CONFIG ---
    st.set_page_config(page_title="Contract Sentinel Pro", page_icon="🛡️", layout="wide")
    st.markdown("""
    <style>
        .metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 20px;}
        h1 {color: #1E3A8A;} 
        .stChatInput {position: fixed; bottom: 0; padding-bottom: 20px; z-index: 100;}
    </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/950/950299.png", width=50)
        st.header("Document Engine")
        vendor_name = st.text_input("Vendor Name", placeholder="e.g. Acme Corp")
        uploaded_file = st.file_uploader("Upload Contract", type=["txt", "pdf"])
        st.divider()
        st.caption("⚡ **System Logs**")

    def log(msg):
        with st.sidebar: st.caption(f"✓ {msg}")

    # --- MAIN PAGE ---
    st.title("🛡️ Contract Risk Sentinel")
    st.markdown("### Enterprise Vendor Risk Assessment Dashboard")

    if uploaded_file:
        # 1. EXTRACT
        contract_text = extract_text_from_file(uploaded_file)
        if not contract_text:
            st.error("Failed to read file.")
            st.stop()
        
        # 2. ANALYZE (Using Cached Function)
        # We check if file changed, but rely on caching for the heavy lift
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            st.session_state.current_file = uploaded_file.name
            st.session_state.messages = [] 
            st.session_state.report = None
        
        # This function call is now CACHED. Same text = Same Result.
        with st.spinner("🔍 AI Analyst is auditing clauses..."):
            raw_result = run_ai_analysis(contract_text)
            st.session_state.analysis_result = [r for r in raw_result if r.get('detected') == True]

        risks = st.session_state.get("analysis_result", [])
        
        # 3. SCORE (Logic)
        health_score, enriched_risks, high_count, med_count = calculate_health_score(risks)

        # 4. DASHBOARD
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Health Score", f"{health_score}/100", delta=f"-{100-health_score} Penalty", delta_color="inverse")
        with col2: st.metric("Critical Risks", f"{high_count}", delta="High Severity", delta_color="inverse")
        with col3: st.metric("Warnings", f"{med_count}", delta="Medium Severity", delta_color="off")
        with col4: st.metric("Status", "Review Needed" if health_score < 90 else "Approved", delta_color="off")

        st.divider()

        # 5. TABS
        tab1, tab2, tab3, tab4 = st.tabs(["🚨 Findings", "📝 Report", "💬 Chat", "✉️ Action"])

        # TAB 1: FINDINGS
        with tab1:
            if not enriched_risks:
                st.success("✅ Clean Contract.")
            else:
                for r in enriched_risks:
                    if r['level'] == "HIGH":
                        with st.expander(f"🔴 HIGH RISK: {r['label']}", expanded=True):
                            st.error(f"**Analysis:** {r['explanation']}")
                            st.caption(f"📜 **Clause:** \"{r['exact_text']}\"")
                    else:
                        with st.expander(f"🟠 MEDIUM RISK: {r['label']}", expanded=False):
                            st.warning(f"**Analysis:** {r['explanation']}")
                            st.caption(f"📜 **Clause:** \"{r['exact_text']}\"")

        # TAB 2: REPORT (Agent 4)
        with tab2:
            if not st.session_state.get("report"):
                log("Reporter: Drafting...")
                with st.spinner("Writing Report..."):
                    risk_list = "\n".join([f"- {r['label']}: {r['explanation']}" for r in enriched_risks])
                    report_prompt = f"Write an Executive Risk Report for {vendor_name or 'the Vendor'}:\n{risk_list}"
                    resp = reporter_model.generate_content(report_prompt)
                    st.session_state.report = resp.text
            st.markdown(st.session_state.report)

        # TAB 3: CHAT (Agent 2)
        with tab3:
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.messages:
                    st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Ex: Is the indemnity clause standard?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                history = [{"role": "user", "parts": [f"Context: {contract_text}"]}, {"role": "model", "parts": ["Ready."]}]
                for m in st.session_state.messages[:-1]:
                    history.append({"role": "model" if m["role"]=="assistant" else "user", "parts": [m["content"]]})

                with st.chat_message("assistant"): pass 
                
                log("Consultant: Thinking...")
                chat = consultant_model.start_chat(history=history, enable_automatic_function_calling=True)
                response = chat.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()

        # TAB 4: ACTION (Agent 3)
        with tab4:
            if not enriched_risks:
                st.success("🎉 No negotiation needed.")
            else:
                if st.button("Draft Negotiation Email", type="primary"):
                    log("Negotiator: Drafting...")
                    with st.spinner("Drafting..."):
                        risk_list = "\n".join([f"- {r['label']}: {r['explanation']}" for r in enriched_risks])
                        email_prompt = f"Write a negotiation email to {vendor_name or 'the Vendor'} asking to fix: \n{risk_list}"
                        email = negotiator_model.generate_content(email_prompt).text
                        st.text_area("📧 Draft Email", value=email, height=300)

    else:
        st.info("👆 **Upload a Contract** to initialize.")
        st.markdown("<div style='text-align: center; color: gray;'><p>Liability • Payment • IP • Termination • Non-Competes</p></div>", unsafe_allow_html=True)

    st.divider()
    st.caption("⚠️ **Disclaimer:** AI Prototype. Not legal advice.")