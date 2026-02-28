import streamlit as st
from groq import Groq
import json
import re
import os
import base64

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Spam Detector",
    page_icon="🛡️",
    layout="centered"
)

# ── Load API Key ──────────────────────────────────────────────────────
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        pass
if not api_key:
    st.error("⚠️ GROQ_API_KEY missing. Add it in Render → Environment Variables.")
    st.stop()

client = Groq(api_key=api_key)

# ══════════════════════════════════════════════════════════════════════
# CSS — DocVault-inspired: light blue/periwinkle gradient, clean, modern
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;700;800;900&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

/* ── APP BACKGROUND — soft periwinkle/blue gradient ── */
.stApp {
    background:
        radial-gradient(ellipse 900px 600px at 10% 0%,   rgba(186,210,255,0.55) 0%, transparent 60%),
        radial-gradient(ellipse 700px 500px at 90% 10%,  rgba(200,185,255,0.40) 0%, transparent 60%),
        radial-gradient(ellipse 800px 600px at 50% 100%, rgba(186,225,255,0.35) 0%, transparent 60%),
        #f0f4ff !important;
    font-family: 'Instrument Sans', sans-serif !important;
    color: #1a1f3a !important;
    min-height: 100vh;
}

/* Subtle dot-grid texture overlay */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: radial-gradient(rgba(100,130,255,0.12) 1px, transparent 1px);
    background-size: 28px 28px;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

.block-container {
    position: relative; z-index: 1;
    padding-top: 0 !important;
    max-width: 760px !important;
    padding-bottom: 3rem !important;
}

/* ── NAVBAR ── */
.sd-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 0;
    margin-bottom: 0;
}
.sd-nav-logo {
    display: flex; align-items: center; gap: 10px;
}
.sd-nav-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #3b6fd4, #6b4fd4);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 14px rgba(59,111,212,0.35);
}
.sd-nav-name {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 1.05rem; font-weight: 800;
    color: #1a1f3a; letter-spacing: -0.3px;
}
.sd-nav-name span { color: #3b6fd4; }
.sd-nav-center {
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(59,111,212,0.18);
    border-radius: 100px;
    padding: 5px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; font-weight: 500;
    color: #5a6a9a; letter-spacing: 0.1em; text-transform: uppercase;
    backdrop-filter: blur(8px);
}
.sd-nav-status {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.82rem; font-weight: 600; color: #1a1f3a;
}
.sd-status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.22);
    animation: sdPulse 2.4s ease-in-out infinite;
}
@keyframes sdPulse { 0%,100%{box-shadow:0 0 0 3px rgba(34,197,94,0.22);} 50%{box-shadow:0 0 0 6px rgba(34,197,94,0.08);} }

/* ── HERO SECTION ── */
.sd-hero {
    text-align: center;
    padding: 3.5rem 0 2.8rem;
}
.sd-hero-tag {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.7);
    border: 1.5px solid rgba(59,111,212,0.22);
    border-radius: 100px; padding: 6px 18px;
    font-size: 0.8rem; font-weight: 600; color: #3b6fd4;
    margin-bottom: 1.6rem;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 12px rgba(59,111,212,0.12);
}
.sd-hero-tag-dot {
    width: 7px; height: 7px; border-radius: 50%; background: #3b6fd4;
    box-shadow: 0 0 0 3px rgba(59,111,212,0.2);
    animation: sdPulse 2s ease-in-out infinite;
}
.sd-h1 {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: clamp(2.6rem, 5vw, 4rem);
    font-weight: 900; line-height: 1.0; letter-spacing: -1.5px;
    color: #1a1f3a; margin: 0 0 0.1rem;
}
.sd-h1-accent {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: clamp(2.6rem, 5vw, 4rem);
    font-weight: 900; line-height: 1.1; letter-spacing: -1.5px;
    background: linear-gradient(135deg, #3b6fd4 0%, #6b4fd4 50%, #3b9fd4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 1.2rem;
}
.sd-hero-sub {
    font-size: 1.05rem; color: #5a6a9a; font-weight: 500;
    max-width: 460px; margin: 0 auto 2rem; line-height: 1.7;
}
.sd-badge-row {
    display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
}
.sd-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.75);
    border: 1.5px solid rgba(59,111,212,0.18);
    border-radius: 100px; padding: 6px 16px;
    font-size: 0.78rem; font-weight: 600;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.sd-badge.spam    { color: #dc2626; border-color: rgba(220,38,38,0.25);  background: rgba(255,240,240,0.8); }
.sd-badge.warn    { color: #d97706; border-color: rgba(217,119,6,0.25);  background: rgba(255,251,235,0.8); }
.sd-badge.clean   { color: #16a34a; border-color: rgba(22,163,74,0.25);  background: rgba(240,255,244,0.8); }

/* ── GLASS INPUT CARD ── */
.sd-input-card {
    background: rgba(255,255,255,0.72);
    border: 1.5px solid rgba(59,111,212,0.16);
    border-radius: 22px;
    padding: 2rem 2rem 1.5rem;
    backdrop-filter: blur(16px);
    box-shadow:
        0 4px 32px rgba(59,111,212,0.10),
        0 1px 0 rgba(255,255,255,0.8) inset;
    margin-bottom: 0;
}
.sd-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: #8a9abf;
    margin-bottom: 0.7rem;
}

/* ── TEXTAREA ── */
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.9) !important;
    border: 1.5px solid rgba(59,111,212,0.18) !important;
    border-radius: 14px !important;
    color: #1a1f3a !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.95rem !important; line-height: 1.7 !important;
    padding: 1rem 1.1rem !important; resize: none !important;
    box-shadow: 0 2px 8px rgba(59,111,212,0.07) !important;
    transition: all 0.2s !important;
    caret-color: #3b6fd4 !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3b6fd4 !important;
    box-shadow: 0 0 0 4px rgba(59,111,212,0.12), 0 2px 8px rgba(59,111,212,0.1) !important;
    background: #ffffff !important;
}
div[data-testid="stTextArea"] textarea::placeholder { color: #b0bcd8 !important; }
div[data-testid="stTextArea"] label { display: none !important; }

/* ── SELECTBOX ── */
div[data-testid="stSelectbox"] label { display: none !important; }
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(59,111,212,0.18) !important;
    border-radius: 12px !important; color: #1a1f3a !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
div[data-baseweb="select"] span { color: #1a1f3a !important; font-weight: 500 !important; }
[data-baseweb="popover"] > div {
    background: #ffffff !important;
    border: 1.5px solid rgba(59,111,212,0.18) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(59,111,212,0.18) !important;
}
[role="option"] { color: #1a1f3a !important; font-family: 'Instrument Sans', sans-serif !important; padding: 0.6rem 1rem !important; }
[role="option"]:hover { background: #f0f4ff !important; }

/* ── ANALYZE BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #3b6fd4, #6b4fd4) !important;
    color: #ffffff !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 800 !important; font-size: 1rem !important;
    border: none !important; border-radius: 14px !important;
    padding: 0.9rem 2rem !important;
    box-shadow: 0 4px 20px rgba(59,111,212,0.35) !important;
    transition: all 0.18s !important; letter-spacing: 0.01em !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(59,111,212,0.5) !important;
    background: linear-gradient(135deg, #2d5bc4, #5c40c4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── RESULT CARDS ── */
.sd-result {
    border-radius: 20px; padding: 1.8rem 2rem;
    margin-top: 1.4rem;
    backdrop-filter: blur(16px);
    position: relative; overflow: hidden;
}
.sd-result::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 20px 20px 0 0;
}
.sd-result.spam  { background: rgba(255,240,240,0.88); border: 1.5px solid rgba(220,38,38,0.22);  box-shadow: 0 8px 32px rgba(220,38,38,0.10); }
.sd-result.warn  { background: rgba(255,251,235,0.88); border: 1.5px solid rgba(217,119,6,0.22);  box-shadow: 0 8px 32px rgba(217,119,6,0.10); }
.sd-result.clean { background: rgba(240,255,244,0.88); border: 1.5px solid rgba(22,163,74,0.22);  box-shadow: 0 8px 32px rgba(22,163,74,0.10); }
.sd-result.spam::before  { background: linear-gradient(90deg, transparent, #dc2626, transparent); }
.sd-result.warn::before  { background: linear-gradient(90deg, transparent, #d97706, transparent); }
.sd-result.clean::before { background: linear-gradient(90deg, transparent, #16a34a, transparent); }

.sd-verdict {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 1.9rem; font-weight: 900; letter-spacing: -0.5px; margin-bottom: 4px;
}
.sd-verdict.spam  { color: #dc2626; }
.sd-verdict.warn  { color: #d97706; }
.sd-verdict.clean { color: #16a34a; }

.sd-meta {
    font-size: 0.78rem; color: #8a9abf; letter-spacing: 0.05em;
    text-transform: uppercase; margin-bottom: 1rem; font-weight: 500;
}
.sd-conf-track {
    height: 7px; background: rgba(0,0,0,0.07);
    border-radius: 100px; overflow: hidden; margin-bottom: 1rem;
}
.sd-conf-fill { height: 100%; border-radius: 100px; }
.sd-reason {
    background: rgba(255,255,255,0.65); border-radius: 12px;
    padding: 0.9rem 1.1rem; font-size: 0.9rem; line-height: 1.7;
    color: #3a4a6a; margin-bottom: 1rem; border: 1px solid rgba(0,0,0,0.06);
}
.sd-signals-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; font-weight: 500; letter-spacing: 0.12em;
    text-transform: uppercase; color: #8a9abf; margin-bottom: 8px;
}
.sd-tag {
    display: inline-block; padding: 4px 12px; border-radius: 100px;
    font-size: 0.74rem; font-weight: 600; margin: 3px 3px 3px 0;
}
.sd-tag.high   { background: rgba(220,38,38,0.1);  border: 1px solid rgba(220,38,38,0.3);  color: #dc2626; }
.sd-tag.medium { background: rgba(217,119,6,0.1);  border: 1px solid rgba(217,119,6,0.3);  color: #d97706; }
.sd-tag.low    { background: rgba(22,163,74,0.1);  border: 1px solid rgba(22,163,74,0.3);  color: #16a34a; }

/* ── STATS ROW ── */
.sd-stats {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 12px; margin-top: 1.2rem;
}
.sd-stat {
    background: rgba(255,255,255,0.72);
    border: 1.5px solid rgba(59,111,212,0.14);
    border-radius: 14px; padding: 1rem 0.75rem; text-align: center;
    backdrop-filter: blur(8px);
}
.sd-stat-num {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 1.7rem; font-weight: 900; line-height: 1;
}
.sd-stat-lbl {
    font-size: 0.65rem; color: #8a9abf; text-transform: uppercase;
    letter-spacing: 0.08em; margin-top: 4px; font-weight: 500;
}

/* ── HISTORY ── */
.sd-history-item {
    background: rgba(255,255,255,0.65);
    border: 1.5px solid rgba(59,111,212,0.12);
    border-radius: 12px; padding: 0.75rem 1rem;
    margin-bottom: 8px; display: flex; align-items: center; gap: 10px;
    backdrop-filter: blur(8px);
    transition: all 0.15s;
}
.sd-history-item:hover { background: rgba(255,255,255,0.85); border-color: rgba(59,111,212,0.22); }
.sd-hist-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }

/* ── DIVIDER ── */
.sd-divider {
    height: 1px; margin: 1.8rem 0;
    background: linear-gradient(90deg, transparent, rgba(59,111,212,0.18), transparent);
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(240,244,255,0.95) !important;
    border-right: 1px solid rgba(59,111,212,0.12) !important;
    backdrop-filter: blur(20px) !important;
}
section[data-testid="stSidebar"] .stMarkdown p { color: #3a4a6a !important; font-size: 0.88rem !important; }
.stCheckbox label { color: #3a4a6a !important; font-size: 0.85rem !important; }
.stSlider [data-testid="stSlider"] { accent-color: #3b6fd4 !important; }

/* ── SCREENSHOT BUTTON ── */
.sd-screenshot-btn {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.8);
    border: 1.5px solid rgba(59,111,212,0.22);
    border-radius: 100px; padding: 7px 18px;
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 0.82rem; font-weight: 700; color: #3b6fd4;
    cursor: pointer; transition: all 0.18s;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(59,111,212,0.1);
}
.sd-screenshot-btn:hover {
    background: #3b6fd4; color: #fff;
    box-shadow: 0 4px 16px rgba(59,111,212,0.35);
    transform: translateY(-1px);
}

/* ── ALERTS ── */
div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.8) !important;
    border: 1.5px solid rgba(59,111,212,0.2) !important;
    border-radius: 14px !important;
    color: #1a1f3a !important;
}
.stSpinner > div { border-top-color: #3b6fd4 !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(59,111,212,0.25); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── html2canvas screenshot injector ──────────────────────────────────
import streamlit.components.v1 as components

def inject_screenshot_button():
    """Renders a floating screenshot button using html2canvas."""
    components.html("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
body { margin:0; background:transparent; }
#_sc_btn {
  position: fixed; bottom: 24px; right: 24px; z-index: 999999;
  display: flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #3b6fd4, #6b4fd4);
  color: #fff; border: none; border-radius: 100px;
  padding: 12px 22px;
  font-family: 'Cabinet Grotesk', 'Instrument Sans', sans-serif;
  font-size: 0.88rem; font-weight: 800; cursor: pointer;
  box-shadow: 0 4px 20px rgba(59,111,212,0.45);
  transition: all 0.18s; letter-spacing: 0.01em;
  border-bottom: 3px solid #2a4faa;
}
#_sc_btn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(59,111,212,0.6); }
#_sc_btn:active { transform: translateY(0); border-bottom-width: 1px; }
#_sc_btn.busy { opacity:0.6; cursor:wait; pointer-events:none; }

#_sc_toast {
  display: none; position: fixed; top: 20px; left:50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg,#3b6fd4,#6b4fd4);
  color:#fff; padding:10px 26px; border-radius:100px;
  font-family:'Instrument Sans',sans-serif; font-size:0.88rem; font-weight:700;
  box-shadow:0 4px 24px rgba(59,111,212,0.4); z-index:999999;
  white-space:nowrap; animation:_toastIn 0.25s ease;
}
@keyframes _toastIn { from{opacity:0;transform:translateX(-50%) translateY(-12px)} to{opacity:1;transform:translateX(-50%) translateY(0)} }
</style>

<div id="_sc_toast"></div>
<button id="_sc_btn" onclick="_takeScreenshot()">📸 Screenshot</button>

<script>
function _takeScreenshot() {
  var btn   = document.getElementById('_sc_btn');
  var toast = document.getElementById('_sc_toast');

  // Message the Streamlit parent frame to take the screenshot
  window.parent.postMessage({ action: 'sd_screenshot' }, '*');
  btn.classList.add('busy');
  btn.innerHTML = '⏳ Capturing…';

  setTimeout(function(){
    btn.classList.remove('busy');
    btn.innerHTML = '📸 Screenshot';
  }, 5000);
}

// Listen for success/fail back from parent
window.addEventListener('message', function(e){
  var toast = document.getElementById('_sc_toast');
  var btn   = document.getElementById('_sc_btn');
  if(e.data && e.data.action === 'sd_captured') {
    btn.classList.remove('busy');
    btn.innerHTML = '✅ Saved!';
    toast.textContent = '✅ Screenshot saved!';
    toast.style.display = 'block';
    setTimeout(function(){
      toast.style.display = 'none';
      btn.innerHTML = '📸 Screenshot';
    }, 3000);
  }
});
</script>
""", height=0)

# ── Session State ─────────────────────────────────────────────────────
for k, v in [("history", []), ("last_result", None), ("screenshot_trigger", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Detection Settings")
st.sidebar.markdown("**Detection mode**")
mode = st.sidebar.selectbox("Mode", ["Auto (Balanced)", "Strict (Low Tolerance)", "Lenient (High Tolerance)"], label_visibility="collapsed")
st.sidebar.markdown("**Content type**")
content_type = st.sidebar.selectbox("Type", ["Auto-detect", "Email", "SMS / Text", "Social Media Post", "Comment / Review", "Chat Message"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("**Additional checks**")
check_phishing    = st.sidebar.checkbox("🎣 Phishing link detection",    value=True)
check_urgency     = st.sidebar.checkbox("⏰ Urgency / pressure tactics", value=True)
check_offers      = st.sidebar.checkbox("💰 Fake offers & prizes",       value=True)
check_impersonate = st.sidebar.checkbox("🎭 Impersonation patterns",     value=True)
check_sentiment   = st.sidebar.checkbox("🧠 Sentiment analysis",         value=False)
st.sidebar.markdown("---")
threshold = st.sidebar.slider("Spam threshold (%)", 10, 90, 50, 5)
st.sidebar.markdown(f"<small style='color:#8a9abf'>Messages ≥ {threshold}% confidence → flagged as spam</small>", unsafe_allow_html=True)
st.sidebar.markdown("---")
if st.session_state.history:
    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()
st.sidebar.markdown("<small style='color:#b0bcd8'>AI Spam Detector · v2.0<br>Powered by Groq + LLaMA 3.1</small>", unsafe_allow_html=True)

# ── NAV BAR ──────────────────────────────────────────────────────────
st.markdown("""
<div class="sd-nav">
  <div class="sd-nav-logo">
    <div class="sd-nav-icon">🛡️</div>
    <div class="sd-nav-name">Spam<span>Shield</span></div>
  </div>
  <div class="sd-nav-center">AI DETECTION PLATFORM</div>
  <div class="sd-nav-status">
    <div class="sd-status-dot"></div>
    Active
  </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sd-hero">
  <div class="sd-hero-tag">
    <div class="sd-hero-tag-dot"></div>
    Real-time AI Analysis
  </div>
  <h1 class="sd-h1">Detect Spam,</h1>
  <span class="sd-h1-accent">Phishing & Scams</span>
  <p class="sd-hero-sub">
    Paste any message — SpamShield analyzes it for threats, scams,
    urgency tactics, and phishing patterns instantly.
  </p>
  <div class="sd-badge-row">
    <span class="sd-badge spam">🚨 Spam Detection</span>
    <span class="sd-badge warn">⚠️ Suspicious Flags</span>
    <span class="sd-badge clean">✅ Clean Verification</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── INPUT CARD ────────────────────────────────────────────────────────
st.markdown('<div class="sd-input-card">', unsafe_allow_html=True)

# Sample picker row
st.markdown('<div class="sd-section-label">Input Source</div>', unsafe_allow_html=True)
sample_texts = {
    "— Try a sample —": "",
    "🔴 Phishing Email":     "URGENT: Your account has been suspended! Click here immediately to verify your identity and restore access: http://secure-bank-login.xyz/verify?token=abc123. Failure to do so within 24 hours will result in permanent account closure.",
    "🟡 Suspicious Offer":   "Congratulations! You've been selected as today's lucky winner of an iPhone 15 Pro! Just pay a small $2 shipping fee to claim your prize. Visit claimprize.info now before it expires!",
    "🟢 Legitimate Message": "Hi, just a reminder that our team meeting is scheduled for tomorrow at 10am in Conference Room B. Please review the agenda I shared last week. Let me know if you have questions.",
    "🔴 Scam SMS":           "FREE MSG: Your loan of Rs.50,000 is approved! Call us now at 9988776655 to claim. Limited time offer. Reply STOP to opt out.",
}
col_sample, col_spacer = st.columns([1, 2])
with col_sample:
    selected = st.selectbox("Sample", list(sample_texts.keys()), label_visibility="collapsed")

default_text = sample_texts.get(selected, "")
user_input = st.text_area(
    "Message",
    value=default_text,
    height=160,
    placeholder="Paste an email, SMS, social post, or any message here…",
    label_visibility="collapsed"
)

char_count = len(user_input)
word_count = len(user_input.split()) if user_input.strip() else 0
st.markdown(
    f"<small style='color:#b0bcd8;font-family:JetBrains Mono,monospace;font-size:0.72rem;'>"
    f"{char_count} chars · {word_count} words</small>",
    unsafe_allow_html=True
)

analyze_btn = st.button("🔍 Analyze Message", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)  # close sd-input-card

# ── ANALYZE FUNCTION ──────────────────────────────────────────────────
def analyze_spam(text: str) -> dict:
    checks = []
    if check_phishing:    checks.append("phishing links, deceptive URLs, lookalike domains")
    if check_urgency:     checks.append("urgency tactics, pressure language, countdown threats")
    if check_offers:      checks.append("fake prize claims, lottery wins, suspicious offers")
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
  "reason": "<2-3 sentence explanation>",
  "signals": [
    {{"label": "<signal name>", "severity": "high" | "medium" | "low"}}
  ],
  "spam_score": <integer 0-100>,
  "category": "<Phishing | Scam | Promotional | Malware | Social Engineering | Legitimate | Unknown>",
  "sentiment": "<Neutral | Alarming | Enticing | Threatening | Friendly>"
}}

MESSAGE:
\"\"\"{text[:3000]}\"\"\"
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a precision spam detection engine. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1, max_tokens=800
    )
    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```', '', raw).strip()
    result  = json.loads(cleaned)
    if result.get("confidence", 0) >= threshold and result.get("verdict") == "SUSPICIOUS":
        result["verdict"] = "SPAM"
    return result

# ── RUN ANALYSIS ──────────────────────────────────────────────────────
if analyze_btn:
    if not user_input.strip():
        st.error("⚠️ Please enter a message to analyze.")
    elif len(user_input.strip()) < 5:
        st.warning("Message is too short to analyze meaningfully.")
    else:
        with st.spinner("🧠 Analyzing with AI…"):
            try:
                result = analyze_spam(user_input)
            except json.JSONDecodeError:
                st.error("❌ AI returned malformed response. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.stop()

        st.session_state.last_result = result
        verdict    = result.get("verdict", "UNKNOWN")
        confidence = result.get("confidence", 0)
        reason     = result.get("reason", "No explanation provided.")
        signals    = result.get("signals", [])
        category   = result.get("category", "Unknown")
        sentiment  = result.get("sentiment", "Neutral")

        css_cls, label, bar_color = {
            "SPAM":       ("spam",  "🚨 SPAM DETECTED", "#dc2626"),
            "SUSPICIOUS": ("warn",  "⚠️ SUSPICIOUS",    "#d97706"),
            "CLEAN":      ("clean", "✅ CLEAN",          "#16a34a"),
        }.get(verdict, ("warn", "⚠️ UNKNOWN", "#d97706"))

        st.session_state.history.insert(0, {
            "verdict": verdict, "confidence": confidence,
            "category": category,
            "preview": user_input[:55] + ("…" if len(user_input) > 55 else ""),
        })
        if len(st.session_state.history) > 10:
            st.session_state.history = st.session_state.history[:10]

        # Result card
        st.markdown(f"""
<div class="sd-result {css_cls}" id="sd-result-card">
  <div class="sd-verdict {css_cls}">{label}</div>
  <div class="sd-meta">Confidence: {confidence}% &nbsp;·&nbsp; {category} &nbsp;·&nbsp; {sentiment}</div>
  <div class="sd-conf-track">
    <div class="sd-conf-fill" style="width:{confidence}%;background:{bar_color};"></div>
  </div>
  <div class="sd-reason">{reason}</div>
""", unsafe_allow_html=True)

        if signals:
            tags_html = "".join(
                f'<span class="sd-tag {s.get("severity","low")}">'
                f'{"🔴" if s.get("severity")=="high" else "🟡" if s.get("severity")=="medium" else "🟢"}'
                f' {s.get("label","")}</span>'
                for s in signals
            )
            st.markdown(f'<div class="sd-signals-title">🔎 Detected Signals</div><div>{tags_html}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Stats row
        n_spam  = sum(1 for h in st.session_state.history if h["verdict"] == "SPAM")
        n_sus   = sum(1 for h in st.session_state.history if h["verdict"] == "SUSPICIOUS")
        n_clean = sum(1 for h in st.session_state.history if h["verdict"] == "CLEAN")
        total   = len(st.session_state.history)
        st.markdown(f"""
<div class="sd-stats">
  <div class="sd-stat"><div class="sd-stat-num" style="color:#dc2626">{n_spam}</div><div class="sd-stat-lbl">Spam</div></div>
  <div class="sd-stat"><div class="sd-stat-num" style="color:#d97706">{n_sus}</div><div class="sd-stat-lbl">Suspicious</div></div>
  <div class="sd-stat"><div class="sd-stat-num" style="color:#16a34a">{n_clean}</div><div class="sd-stat-lbl">Clean</div></div>
  <div class="sd-stat"><div class="sd-stat-num" style="color:#3b6fd4">{total}</div><div class="sd-stat-lbl">Scanned</div></div>
</div>
""", unsafe_allow_html=True)

# ── HISTORY ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="sd-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sd-section-label" style="margin-bottom:0.7rem;">📜 Recent Scans</div>', unsafe_allow_html=True)
    dot_map  = {"SPAM": "#dc2626", "CLEAN": "#16a34a", "SUSPICIOUS": "#d97706"}
    icon_map = {"SPAM": "🚨", "CLEAN": "✅", "SUSPICIOUS": "⚠️"}
    for h in st.session_state.history:
        dot_color = dot_map.get(h["verdict"], "#d97706")
        st.markdown(f"""
<div class="sd-history-item">
  <div class="sd-hist-dot" style="background:{dot_color};box-shadow:0 0 0 3px {dot_color}28;"></div>
  <div style="flex:1;overflow:hidden">
    <span style="color:#1a1f3a;font-weight:700;font-size:0.88rem">{icon_map.get(h["verdict"],"❓")} {h["verdict"]}</span>
    <span style="color:#b0bcd8;margin:0 6px;font-size:0.8rem">·</span>
    <span style="color:#8a9abf;font-size:0.78rem">{h["confidence"]}% · {h["category"]}</span>
    <div style="color:#b0bcd8;font-size:0.76rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px">{h["preview"]}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── SCREENSHOT SECTION ────────────────────────────────────────────────
st.markdown('<div class="sd-divider"></div>', unsafe_allow_html=True)

# Screenshot widget — uses html2canvas to capture the full Streamlit page
components.html("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
  body { margin:0; background:transparent; }
  #_cap_btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.82);
    border: 1.5px solid rgba(59,111,212,0.28);
    border-radius: 100px; padding: 9px 22px;
    font-family: 'Cabinet Grotesk','Instrument Sans',sans-serif;
    font-size: 0.85rem; font-weight: 700; color: #3b6fd4;
    cursor: pointer; transition: all 0.18s;
    backdrop-filter: blur(8px);
    box-shadow: 0 2px 12px rgba(59,111,212,0.15);
  }
  #_cap_btn:hover { background: #3b6fd4; color:#fff; box-shadow:0 4px 18px rgba(59,111,212,0.4); transform:translateY(-1px); }
  #_cap_btn.busy  { opacity:0.55; cursor:wait; pointer-events:none; }
  #_cap_toast {
    display:none; position:fixed; top:18px; left:50%; transform:translateX(-50%);
    background:linear-gradient(135deg,#3b6fd4,#6b4fd4); color:#fff;
    padding:9px 24px; border-radius:100px;
    font-family:'Instrument Sans',sans-serif; font-size:0.86rem; font-weight:700;
    box-shadow:0 4px 22px rgba(59,111,212,0.4); z-index:999999; white-space:nowrap;
    animation:_toastIn 0.22s ease;
  }
  @keyframes _toastIn{from{opacity:0;transform:translateX(-50%) translateY(-10px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
</style>

<div id="_cap_toast">✅ Screenshot saved to Downloads!</div>
<button id="_cap_btn" onclick="_capturePage()">📸 &nbsp;Save Screenshot</button>

<script>
function _capturePage() {
  var btn   = document.getElementById('_cap_btn');
  var toast = document.getElementById('_cap_toast');
  btn.classList.add('busy');
  btn.innerHTML = '⏳ &nbsp;Capturing…';

  // Walk up to the Streamlit root frame and capture it
  var targetWin = window.parent;
  var targetDoc = targetWin.document;
  var targetEl  = targetDoc.getElementById('root') ||
                  targetDoc.querySelector('.stApp') ||
                  targetDoc.body;

  // Load html2canvas in parent if not already there
  if (typeof targetWin.html2canvas === 'undefined') {
    var s = targetDoc.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
    s.onload = function(){ _doCapture(targetEl, btn, toast); };
    targetDoc.head.appendChild(s);
  } else {
    _doCapture(targetEl, btn, toast);
  }
}

function _doCapture(el, btn, toast) {
  var targetWin = window.parent;
  targetWin.html2canvas(el, {
    scale: 2,
    useCORS: true,
    allowTaint: true,
    backgroundColor: '#f0f4ff',
    logging: false,
    scrollX: 0,
    scrollY: -targetWin.scrollY,
    windowWidth: targetWin.document.documentElement.scrollWidth,
    windowHeight: targetWin.document.documentElement.scrollHeight
  }).then(function(canvas){
    var a = targetWin.document.createElement('a');
    a.download = 'spamshield-screenshot.png';
    a.href = canvas.toDataURL('image/png', 1.0);
    targetWin.document.body.appendChild(a);
    a.click();
    targetWin.document.body.removeChild(a);

    btn.classList.remove('busy');
    btn.innerHTML = '✅ &nbsp;Saved!';
    toast.style.display = 'block';
    setTimeout(function(){
      toast.style.display = 'none';
      btn.innerHTML = '📸 &nbsp;Save Screenshot';
    }, 3200);
  }).catch(function(err){
    btn.classList.remove('busy');
    btn.innerHTML = '📸 &nbsp;Save Screenshot';
    alert('Screenshot failed: ' + err.message);
  });
}
</script>
""", height=58)

# ── FOOTER ────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#b0bcd8;font-size:0.72rem;
     font-family:'JetBrains Mono',monospace;letter-spacing:0.07em;
     padding-bottom:1.5rem;margin-top:0.5rem;">
  SPAMSHIELD AI · POWERED BY GROQ + LLAMA 3.1 · NOT A SUBSTITUTE FOR PROFESSIONAL SECURITY TOOLS
</div>
""", unsafe_allow_html=True)
