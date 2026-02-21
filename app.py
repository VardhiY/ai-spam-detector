import streamlit as st
from groq import Groq
import json
import re

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Spam Detector",
    page_icon="🛡️",
    layout="centered"
)

# ── Load API Key ──────────────────────────────────────────────────────
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured.")
    st.info("Add to Streamlit Secrets:\n\n`GROQ_API_KEY = \"gsk_your_key_here\"`")
    st.stop()

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
.stApp { background: #07070f; color: #e0e0f0; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

.hero-wrap { text-align: center; padding: 2rem 0 1.5rem; }
.hero-icon {
    font-size: 3.5rem; display: block; margin-bottom: 0.4rem;
    filter: drop-shadow(0 0 24px #ff3e6c88);
    animation: pulse-icon 3s ease-in-out infinite;
}
@keyframes pulse-icon {
    0%, 100% { filter: drop-shadow(0 0 16px #ff3e6c88); }
    50%       { filter: drop-shadow(0 0 36px #ff3e6ccc); }
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #ffffff 20%, #ff3e6c 55%, #ff9b3e 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.1; margin-bottom: 0.4rem;
}
.hero-sub { color: #5a5a7a; font-size: 0.82rem; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 0.5rem; }
.badge-wrap { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.7rem; }
.badge        { background: rgba(255,62,108,0.1);  border: 1px solid rgba(255,62,108,0.35);  color: #ff8fa3; padding: 0.22rem 0.8rem; border-radius: 999px; font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; }
.badge-green  { background: rgba(67,233,123,0.1);  border: 1px solid rgba(67,233,123,0.35);  color: #43e97b; }
.badge-yellow { background: rgba(255,193,63,0.1);  border: 1px solid rgba(255,193,63,0.35);  color: #ffc13f; }

.divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #2a2a3d, transparent); margin: 1.5rem 0; }

.input-label { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.88rem; color: #a0a0c0; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem; }

div[data-testid="stTextArea"] textarea {
    background: #10101c !important; border: 1px solid #2a2a3d !important;
    border-radius: 14px !important; color: #e0e0f0 !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.9rem !important;
    line-height: 1.7 !important; padding: 1rem !important; resize: vertical !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #ff3e6c !important; box-shadow: 0 0 0 2px rgba(255,62,108,0.15) !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #ff3e6c, #ff7e3e) !important;
    color: white !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 1.05rem !important;
    border: none !important; border-radius: 12px !important; padding: 0.8rem !important;
}
.stButton > button:hover { box-shadow: 0 8px 32px rgba(255,62,108,0.45) !important; }

.result-card { border-radius: 16px; padding: 1.6rem 1.8rem; margin-top: 1.4rem; position: relative; overflow: hidden; }
.result-card-spam       { background: #1a0810; border: 1.5px solid #ff3e6c88; }
.result-card-clean      { background: #081a10; border: 1.5px solid #43e97b88; }
.result-card-suspicious { background: #1a150a; border: 1.5px solid #ffc13f88; }
.result-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.result-card-spam::before       { background: linear-gradient(90deg, transparent, #ff3e6c, transparent); }
.result-card-clean::before      { background: linear-gradient(90deg, transparent, #43e97b, transparent); }
.result-card-suspicious::before { background: linear-gradient(90deg, transparent, #ffc13f, transparent); }

.result-verdict { font-family: 'Syne', sans-serif; font-size: 1.7rem; font-weight: 800; margin-bottom: 0.3rem; }
.verdict-spam       { color: #ff3e6c; }
.verdict-clean      { color: #43e97b; }
.verdict-suspicious { color: #ffc13f; }

.result-confidence { font-size: 0.78rem; color: #5a5a7a; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 1rem; }
.result-reason { background: rgba(255,255,255,0.03); border-left: 3px solid #2a2a3d; border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; font-size: 0.87rem; line-height: 1.7; color: #b0b0cc; margin-bottom: 1rem; }

.signals-title { font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 700; color: #5a5a7a; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem; }
.signal-tag    { display: inline-block; padding: 0.22rem 0.75rem; border-radius: 999px; font-size: 0.72rem; margin: 0.2rem 0.15rem; letter-spacing: 0.03em; }
.signal-red    { background: rgba(255,62,108,0.12); border: 1px solid rgba(255,62,108,0.4); color: #ff8fa3; }
.signal-yellow { background: rgba(255,193,63,0.10); border: 1px solid rgba(255,193,63,0.4); color: #ffc13f; }
.signal-green  { background: rgba(67,233,123,0.10); border: 1px solid rgba(67,233,123,0.4); color: #43e97b; }

.conf-bar-wrap { margin: 0.8rem 0; }
.conf-bar-bg   { background: #1e1e2a; border-radius: 999px; height: 6px; width: 100%; overflow: hidden; }
.conf-bar-fill { height: 100%; border-radius: 999px; }

.stat-row  { display: flex; gap: 0.75rem; margin-top: 1.2rem; }
.stat-card { flex: 1; background: #10101c; border: 1px solid #2a2a3d; border-radius: 12px; padding: 0.85rem 0.6rem; text-align: center; }
.stat-num  { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; }
.stat-label { font-size: 0.65rem; color: #5a5a7a; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 0.15rem; }

.history-item { background: #10101c; border: 1px solid #1e1e2a; border-radius: 10px; padding: 0.7rem 0.9rem; margin-bottom: 0.5rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.6rem; }
.history-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-spam        { background: #ff3e6c; }
.dot-clean       { background: #43e97b; }
.dot-suspicious  { background: #ffc13f; }

section[data-testid="stSidebar"] { background: #0c0c18 !important; border-right: 1px solid #1e1e2a; }
.stCheckbox label { font-size: 0.85rem !important; color: #b0b0cc !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Detection Settings")
st.sidebar.markdown("**Detection mode:**")
mode = st.sidebar.selectbox("Mode", ["Auto (Balanced)", "Strict (Low Tolerance)", "Lenient (High Tolerance)"], label_visibility="collapsed")
st.sidebar.markdown("**Content type:**")
content_type = st.sidebar.selectbox("Type", ["Auto-detect", "Email", "SMS / Text", "Social Media Post", "Comment / Review", "Chat Message"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("**Additional checks:**")
check_phishing    = st.sidebar.checkbox("🎣 Phishing link detection",    value=True)
check_urgency     = st.sidebar.checkbox("⏰ Urgency / pressure tactics", value=True)
check_offers      = st.sidebar.checkbox("💰 Fake offers & prizes",       value=True)
check_impersonate = st.sidebar.checkbox("🎭 Impersonation patterns",     value=True)
check_sentiment   = st.sidebar.checkbox("🧠 Sentiment analysis",         value=False)
st.sidebar.markdown("---")
threshold = st.sidebar.slider("Spam threshold (%)", 10, 90, 50, 5)
st.sidebar.markdown(f"<small style='color:#5a5a7a'>Messages ≥ {threshold}% confidence → flagged as spam</small>", unsafe_allow_html=True)
st.sidebar.markdown("---")
if st.session_state.history:
    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()
st.sidebar.markdown("<small style='color:#3a3a5a'>AI Spam Detector · v1.0<br>Powered by Groq + LLaMA 3.1</small>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <span class="hero-icon">🛡️</span>
  <div class="hero-title">AI Spam Detector</div>
  <div class="hero-sub">Real-time spam · phishing · scam analysis</div>
  <div class="badge-wrap">
    <span class="badge">🔴 Spam</span>
    <span class="badge badge-yellow">⚠️ Suspicious</span>
    <span class="badge badge-green">✅ Clean</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Analyze Function ──────────────────────────────────────────────────
def analyze_spam(text: str) -> dict:
    checks = []
    if check_phishing:    checks.append("phishing links, deceptive URLs, lookalike domains")
    if check_urgency:     checks.append("urgency tactics, pressure language, countdown threats")
    if check_offers:      checks.append("fake prize claims, lottery wins, suspicious offers, 'too good to be true' deals")
    if check_impersonate: checks.append("impersonation of banks, government, brands, support teams")
    if check_sentiment:   checks.append("overall sentiment and emotional manipulation")

    mode_instruction = {
        "Auto (Balanced)":          "Use balanced judgment.",
        "Strict (Low Tolerance)":   "Be strict — flag anything remotely suspicious.",
        "Lenient (High Tolerance)": "Only flag clear, obvious spam.",
    }[mode]

    content_hint = f" The content type is: {content_type}." if content_type != "Auto-detect" else ""
    checks_str   = "\n".join(f"- {c}" for c in checks) if checks else "- General spam patterns"

    prompt = f"""You are an expert spam and scam detection AI. Analyze the following message thoroughly.{content_hint}

DETECTION MODE: {mode_instruction}

CHECK FOR:
{checks_str}
- General spam indicators (excessive caps, excessive punctuation, grammar errors)
- Social engineering tactics
- Request for personal information, passwords, OTPs, money transfers

Respond ONLY with a valid JSON object (no markdown, no extra text):
{{
  "verdict": "SPAM" | "SUSPICIOUS" | "CLEAN",
  "confidence": <integer 0-100>,
  "reason": "<2-3 sentence explanation of the verdict>",
  "signals": [
    {{"label": "<signal name>", "severity": "high" | "medium" | "low"}}
  ],
  "spam_score": <integer 0-100>,
  "category": "<one of: Phishing | Scam | Promotional | Malware | Social Engineering | Legitimate | Unknown>",
  "sentiment": "<Neutral | Alarming | Enticing | Threatening | Friendly>"
}}

MESSAGE TO ANALYZE:
\"\"\"
{text[:3000]}
\"\"\"
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a precision spam detection engine. Always return valid JSON only. No extra text, no markdown fences."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=800
    )

    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```', '', raw).strip()
    result  = json.loads(cleaned)

    # Apply threshold override
    if result.get("confidence", 0) >= threshold and result.get("verdict") == "SUSPICIOUS":
        result["verdict"] = "SPAM"

    return result

# ── Sample Messages ───────────────────────────────────────────────────
sample_texts = {
    "— Try a sample —": "",
    "🔴 Phishing Email":     "URGENT: Your account has been suspended! Click here immediately to verify your identity and restore access: http://secure-bank-login.xyz/verify?token=abc123. Failure to do so within 24 hours will result in permanent account closure.",
    "🟡 Suspicious Offer":   "Congratulations! You've been selected as today's lucky winner of an iPhone 15 Pro! Just pay a small $2 shipping fee to claim your prize. Visit claimprize.info now before it expires!",
    "🟢 Legitimate Message": "Hi, just a reminder that our team meeting is scheduled for tomorrow at 10am in Conference Room B. Please review the agenda I shared last week. Let me know if you have questions.",
    "🔴 Scam SMS":           "FREE MSG: Your loan of Rs.50,000 is approved! Call us now at 9988776655 to claim. Limited time offer. Reply STOP to opt out.",
}

# ── Input ─────────────────────────────────────────────────────────────
st.markdown('<div class="input-label">📋 Paste message to analyze</div>', unsafe_allow_html=True)

col_sample, _ = st.columns([1, 2])
with col_sample:
    selected = st.selectbox("Sample", list(sample_texts.keys()), label_visibility="collapsed")

default_text = sample_texts.get(selected, "")
user_input = st.text_area(
    "Message",
    value=default_text,
    height=180,
    placeholder="Paste an email, SMS, social media post, or any message here...",
    label_visibility="collapsed"
)

char_count = len(user_input)
word_count = len(user_input.split()) if user_input.strip() else 0
st.markdown(f"<small style='color:#3a3a5a'>{char_count} chars · {word_count} words</small>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🔍 Analyze Message", use_container_width=True)

# ── Run Analysis ──────────────────────────────────────────────────────
if analyze_btn:
    if not user_input.strip():
        st.error("⚠️ Please enter a message to analyze.")
    elif len(user_input.strip()) < 5:
        st.warning("Message is too short to analyze meaningfully.")
    else:
        with st.spinner("🧠 Analyzing message with AI..."):
            try:
                result = analyze_spam(user_input)
            except json.JSONDecodeError:
                st.error("❌ AI returned malformed response. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.stop()

        verdict    = result.get("verdict", "UNKNOWN")
        confidence = result.get("confidence", 0)
        reason     = result.get("reason", "No explanation provided.")
        signals    = result.get("signals", [])
        category   = result.get("category", "Unknown")
        sentiment  = result.get("sentiment", "Neutral")

        v_map = {
            "SPAM":       ("result-card-spam",       "verdict-spam",       "🚨 SPAM DETECTED", "#ff3e6c"),
            "SUSPICIOUS": ("result-card-suspicious", "verdict-suspicious", "⚠️ SUSPICIOUS",    "#ffc13f"),
            "CLEAN":      ("result-card-clean",      "verdict-clean",      "✅ CLEAN",          "#43e97b"),
        }
        card_cls, verdict_cls, verdict_label, bar_color = v_map.get(verdict, v_map["SUSPICIOUS"])

        # Save history
        st.session_state.history.insert(0, {
            "verdict": verdict, "confidence": confidence,
            "category": category,
            "preview": user_input[:55] + ("..." if len(user_input) > 55 else ""),
        })
        if len(st.session_state.history) > 10:
            st.session_state.history = st.session_state.history[:10]

        # ── Result card ───────────────────────────────────────────────
        st.markdown(f"""
        <div class="result-card {card_cls}">
            <div class="result-verdict {verdict_cls}">{verdict_label}</div>
            <div class="result-confidence">Confidence: {confidence}% &nbsp;·&nbsp; Category: {category} &nbsp;·&nbsp; Sentiment: {sentiment}</div>
            <div class="conf-bar-wrap">
                <div class="conf-bar-bg">
                    <div class="conf-bar-fill" style="width:{confidence}%; background:{bar_color};"></div>
                </div>
            </div>
            <div class="result-reason">{reason}</div>
        """, unsafe_allow_html=True)

        if signals:
            sev_cls  = {"high": "signal-red", "medium": "signal-yellow", "low": "signal-green"}
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            tags_html = "".join(
                f'<span class="signal-tag {sev_cls.get(s.get("severity","low"), "signal-green")}">'
                f'{sev_icon.get(s.get("severity","low"),"🟢")} {s.get("label","")}</span>'
                for s in signals
            )
            st.markdown(f'<div class="signals-title">🔎 Detected Signals</div><div>{tags_html}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Stats row
        n_spam  = sum(1 for h in st.session_state.history if h["verdict"] == "SPAM")
        n_sus   = sum(1 for h in st.session_state.history if h["verdict"] == "SUSPICIOUS")
        n_clean = sum(1 for h in st.session_state.history if h["verdict"] == "CLEAN")
        total   = len(st.session_state.history)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card"><div class="stat-num" style="color:#ff3e6c">{n_spam}</div><div class="stat-label">Spam Found</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#ffc13f">{n_sus}</div><div class="stat-label">Suspicious</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#43e97b">{n_clean}</div><div class="stat-label">Clean</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#6c6caa">{total}</div><div class="stat-label">Total Scanned</div></div>
        </div>
        """, unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="input-label">📜 Recent Scans</div>', unsafe_allow_html=True)
    dot_map  = {"SPAM": "dot-spam", "CLEAN": "dot-clean", "SUSPICIOUS": "dot-suspicious"}
    icon_map = {"SPAM": "🚨", "CLEAN": "✅", "SUSPICIOUS": "⚠️"}
    for h in st.session_state.history:
        st.markdown(f"""
        <div class="history-item">
            <div class="history-dot {dot_map.get(h['verdict'], 'dot-suspicious')}"></div>
            <div style="flex:1; overflow:hidden">
                <span style="color:#e0e0f0">{icon_map.get(h['verdict'],'❓')} {h['verdict']}</span>
                <span style="color:#3a3a5a; margin:0 0.4rem">·</span>
                <span style="color:#5a5a7a; font-size:0.76rem">{h['confidence']}% · {h['category']}</span>
                <div style="color:#3a3a5a; font-size:0.75rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:0.1rem">{h['preview']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#2a2a3d; font-size:0.72rem; padding-bottom:1rem; letter-spacing:0.05em">
    AI SPAM DETECTOR · POWERED BY GROQ + LLAMA 3.1 · NOT A SUBSTITUTE FOR PROFESSIONAL SECURITY TOOLS
</div>
""", unsafe_allow_html=True)
