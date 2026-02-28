import streamlit as st
from groq import Groq
import json, re, os, base64
import streamlit.components.v1 as components

st.set_page_config(page_title="SpamShield AI", page_icon="🛡️", layout="centered")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try: api_key = st.secrets["GROQ_API_KEY"]
    except: pass
if not api_key:
    st.error("⚠️ GROQ_API_KEY missing.")
    st.stop()
client = Groq(api_key=api_key)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');

:root {
  --P:  #1a3fa8;
  --PB: #2563eb;
  --PA: #dbeafe;
  --PS: #eff6ff;
  --TX: #0f172a;
  --SB: #334155;
  --MT: #64748b;
  --BD: rgba(26,63,168,0.15);
  --BM: rgba(26,63,168,0.30);
  --SH: rgba(26,63,168,0.10);
  --SM: rgba(26,63,168,0.20);
}
*, *::before, *::after { box-sizing: border-box; }
html, body { margin:0; padding:0; }

.stApp {
    background:
        radial-gradient(ellipse 1100px 700px at 0% 0%,   rgba(219,234,254,.70) 0%, transparent 55%),
        radial-gradient(ellipse  800px 600px at 100% 0%,  rgba(191,219,254,.50) 0%, transparent 55%),
        radial-gradient(ellipse  700px 500px at 80% 100%, rgba(219,234,254,.40) 0%, transparent 55%),
        #f0f6ff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--TX) !important;
}
.stApp::before {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image: radial-gradient(rgba(26,63,168,.09) 1px, transparent 1px);
    background-size: 24px 24px;
}
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"] {
    display:none !important;
}
.block-container {
    position:relative; z-index:1;
    padding-top:.5rem !important;
    max-width:820px !important;
    padding-bottom:3rem !important;
}

/* ── FORCE TEXT VISIBILITY ── */
.stApp * { color: var(--TX) !important; }
.hero-accent { color: transparent !important; }
.hero-accent * { color: transparent !important; }
.badge.spam  { color: #dc2626 !important; }
.badge.warn  { color: #d97706 !important; }
.badge.clean { color: #059669 !important; }
.verdict.spam  { color: #dc2626 !important; }
.verdict.warn  { color: #d97706 !important; }
.verdict.clean { color: #059669 !important; }
.sig.high   { color: #dc2626 !important; }
.sig.medium { color: #d97706 !important; }
.sig.low    { color: #059669 !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid var(--BD) !important;
    box-shadow: 4px 0 24px var(--SH) !important;
}
section[data-testid="stSidebar"] * { color: var(--TX) !important; }
section[data-testid="stSidebar"] h2 {
    font-size:1rem !important; font-weight:800 !important;
    color: var(--P) !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size:.86rem !important; font-weight:600 !important; color: var(--SB) !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: var(--PS) !important;
    border: 1.5px solid var(--BD) !important;
    border-radius:10px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: var(--PS) !important; color: var(--P) !important;
    border: 1.5px solid var(--BD) !important; border-bottom: 1.5px solid var(--BD) !important;
    border-radius:10px !important; font-size:.84rem !important; font-weight:700 !important;
    box-shadow:none !important; transform:none !important; margin-top:0 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--PA) !important; border-color: var(--P) !important; transform:none !important;
}
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span { color: var(--TX) !important; font-size:.86rem !important; }

/* ── NAVBAR ── */
.nav { display:flex; align-items:center; justify-content:space-between; padding:1.2rem 0 0; }
.nav-logo { display:flex; align-items:center; gap:11px; }
.nav-icon {
    width:40px; height:40px;
    background:linear-gradient(145deg,var(--P),var(--PB));
    border-radius:11px; display:flex; align-items:center; justify-content:center;
    font-size:1.15rem; box-shadow:0 4px 16px var(--SM);
}
.nav-name { font-size:1.1rem; font-weight:900; letter-spacing:-.5px; }
.nav-name b { color: var(--P) !important; font-weight:900; }
.nav-pill {
    background:rgba(255,255,255,.9); border:1.5px solid var(--BD); border-radius:100px;
    padding:5px 18px; font-family:'Fira Code',monospace; font-size:.66rem;
    color: var(--MT) !important; letter-spacing:.12em; text-transform:uppercase;
}
.nav-status { display:flex; align-items:center; gap:7px; font-size:.82rem; font-weight:700; }
.status-dot {
    width:8px; height:8px; border-radius:50%; background:#10b981;
    box-shadow:0 0 0 3px rgba(16,185,129,.22);
    animation:pulse 2.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100%{box-shadow:0 0 0 3px rgba(16,185,129,.22);}
    50%{box-shadow:0 0 0 7px rgba(16,185,129,.05);}
}

/* ── HERO ── */
.hero { text-align:center; padding:3.2rem 0 2.6rem; }
.hero-tag {
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(255,255,255,.95); border:1.5px solid var(--BM);
    border-radius:100px; padding:7px 20px;
    font-size:.8rem; font-weight:700; color: var(--P) !important;
    margin-bottom:1.6rem; box-shadow:0 2px 16px var(--SH);
}
.hero-tag-dot {
    width:7px; height:7px; border-radius:50%; background:var(--P);
    box-shadow:0 0 0 3px rgba(26,63,168,.2);
    animation:pulse2 2s ease-in-out infinite;
}
@keyframes pulse2{0%,100%{box-shadow:0 0 0 3px rgba(26,63,168,.2);}50%{box-shadow:0 0 0 7px rgba(26,63,168,.05);}}
.hero h1 {
    font-size:clamp(2.6rem,5vw,3.8rem); font-weight:900; line-height:1;
    letter-spacing:-2px; color: var(--TX) !important; margin:0 0 .1rem;
}
.hero-accent {
    font-size:clamp(2.6rem,5vw,3.8rem); font-weight:900; line-height:1.1;
    letter-spacing:-2px; display:block; margin-bottom:1.2rem;
    background:linear-gradient(135deg,var(--P) 0%,var(--PB) 55%,#0ea5e9 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero p { font-size:1rem; color: var(--SB) !important; font-weight:500; max-width:460px; margin:0 auto 1.8rem; line-height:1.75; }
.badges { display:flex; justify-content:center; gap:10px; flex-wrap:wrap; }
.badge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(255,255,255,.92); border:1.5px solid var(--BD);
    border-radius:100px; padding:7px 16px; font-size:.78rem; font-weight:700;
    box-shadow:0 2px 10px rgba(0,0,0,.06);
}
.badge.spam  { border-color:rgba(220,38,38,.22);  background:rgba(255,241,241,.92); }
.badge.warn  { border-color:rgba(217,119,6,.22);  background:rgba(255,253,235,.92); }
.badge.clean { border-color:rgba(5,150,105,.22);  background:rgba(236,253,245,.92); }

/* ── INPUT CARD ── */
.input-card {
    background:rgba(255,255,255,.94); border:1.5px solid var(--BD);
    border-top:3px solid var(--P); border-radius:20px;
    padding:1.6rem 1.8rem 1.4rem;
    box-shadow:0 8px 40px var(--SH);
}
.input-row-label { display:flex; align-items:center; margin-bottom:.7rem; }
.col-label {
    flex:1; font-family:'Fira Code',monospace; font-size:.65rem; font-weight:600;
    letter-spacing:.14em; text-transform:uppercase; color: var(--MT) !important;
}
.or-pill {
    flex-shrink:0;
    background:linear-gradient(135deg,var(--P),var(--PB));
    color:#fff !important; font-size:.65rem; font-weight:900;
    letter-spacing:.12em; padding:5px 14px; border-radius:100px;
    margin:0 14px; box-shadow:0 2px 10px var(--SM);
}

/* ── TEXTAREA ── */
div[data-testid="stTextArea"] label { display:none !important; }
div[data-testid="stTextArea"] textarea {
    background:#ffffff !important;
    border:1.5px solid rgba(26,63,168,.2) !important;
    border-radius:12px !important; color: var(--TX) !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:.93rem !important; line-height:1.75 !important;
    padding:.9rem 1rem !important; resize:none !important;
    caret-color:var(--P) !important; transition:border-color .18s, box-shadow .18s !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color:var(--P) !important; box-shadow:0 0 0 4px rgba(26,63,168,.10) !important; outline:none !important;
}
div[data-testid="stTextArea"] textarea::placeholder { color:#cbd5e1 !important; }

/* ── SELECTBOX ── */
div[data-testid="stSelectbox"] label { display:none !important; }
div[data-baseweb="select"] > div {
    background:#ffffff !important; border:1.5px solid rgba(26,63,168,.2) !important;
    border-radius:11px !important; color: var(--TX) !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:.88rem !important;
}
div[data-baseweb="select"] span { color: var(--TX) !important; font-weight:600 !important; }
[data-baseweb="popover"] > div {
    background:#fff !important; border:1.5px solid var(--BD) !important;
    border-radius:12px !important; box-shadow:0 12px 40px var(--SM) !important;
}
[role="option"] { color: var(--TX) !important; font-family:'Plus Jakarta Sans',sans-serif !important; padding:.6rem 1rem !important; font-size:.88rem !important; }
[role="option"]:hover { background: var(--PS) !important; color: var(--P) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] { background:transparent !important; }
[data-testid="stFileUploader"] label { display:none !important; }
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] section {
    background: var(--PS) !important;
    border:2px dashed rgba(26,63,168,.28) !important; border-radius:14px !important;
    min-height:200px !important; display:flex !important; flex-direction:column !important;
    align-items:center !important; justify-content:center !important;
    padding:1.2rem !important; transition:all .2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] section:hover {
    border-color:var(--P) !important; background:var(--PA) !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span { color: var(--MT) !important; font-size:.82rem !important; }
[data-testid="stFileUploader"] button {
    background:#fff !important; border:1.5px solid var(--BM) !important;
    border-radius:10px !important; color: var(--P) !important;
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-weight:800 !important; font-size:.82rem !important; padding:6px 18px !important;
    box-shadow:none !important; transform:none !important;
    border-bottom:1.5px solid var(--BM) !important; margin-top:0 !important;
    transition:all .18s !important;
}
[data-testid="stFileUploader"] button:hover { background:var(--P) !important; color:#fff !important; }

.img-preview { border-radius:12px; overflow:hidden; border:1.5px solid var(--BD); box-shadow:0 4px 18px var(--SH); background:#f0f6ff; margin-top:.4rem; }
.img-meta { padding:6px 12px; font-family:'Fira Code',monospace; font-size:.7rem; color: var(--P) !important; font-weight:500; background:var(--PS); border-top:1px solid var(--BD); }

[data-testid="column"]:first-child { border-right:1.5px solid var(--BD) !important; padding-right:1.2rem !important; }
[data-testid="column"]:last-child { padding-left:1.2rem !important; }

/* ── ANALYZE BUTTON ── */
.stButton > button {
    width:100% !important;
    background:linear-gradient(135deg,var(--P) 0%,var(--PB) 100%) !important;
    color:#fff !important; font-family:'Plus Jakarta Sans',sans-serif !important;
    font-weight:800 !important; font-size:1rem !important; border:none !important;
    border-radius:12px !important; padding:.88rem 2rem !important;
    box-shadow:0 4px 20px var(--SM) !important;
    border-bottom:3px solid rgba(0,0,0,.18) !important;
    transition:all .18s !important; margin-top:.6rem !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 32px rgba(26,63,168,.45) !important; }
.stButton > button:active { transform:translateY(0) !important; border-bottom-width:1px !important; }

/* ── RESULT CARDS ── */
.result { border-radius:18px; padding:1.8rem 2rem; margin-top:1.4rem; position:relative; overflow:hidden; }
.result::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0; }
.result.spam  { background:rgba(255,241,241,.97); border:1.5px solid rgba(220,38,38,.2);  box-shadow:0 8px 36px rgba(220,38,38,.08); }
.result.warn  { background:rgba(255,253,235,.97); border:1.5px solid rgba(217,119,6,.2);  box-shadow:0 8px 36px rgba(217,119,6,.08); }
.result.clean { background:rgba(236,253,245,.97); border:1.5px solid rgba(5,150,105,.2);  box-shadow:0 8px 36px rgba(5,150,105,.08); }
.result.spam::before  { background:linear-gradient(90deg,transparent,#dc2626,transparent); }
.result.warn::before  { background:linear-gradient(90deg,transparent,#f59e0b,transparent); }
.result.clean::before { background:linear-gradient(90deg,transparent,#10b981,transparent); }
.verdict { font-size:2rem; font-weight:900; letter-spacing:-.5px; margin-bottom:4px; }
.vmeta { font-size:.76rem; color: var(--MT) !important; letter-spacing:.06em; text-transform:uppercase; margin-bottom:1rem; font-weight:600; }
.conf-track { height:7px; background:rgba(0,0,0,.07); border-radius:100px; overflow:hidden; margin-bottom:1rem; }
.conf-fill { height:100%; border-radius:100px; }
.reason { background:rgba(255,255,255,.85); border-radius:11px; padding:.9rem 1.1rem; font-size:.9rem; line-height:1.75; color: var(--SB) !important; margin-bottom:1rem; border:1px solid rgba(0,0,0,.07); }
.sig-title { font-family:'Fira Code',monospace; font-size:.64rem; font-weight:500; letter-spacing:.14em; text-transform:uppercase; color: var(--MT) !important; margin-bottom:8px; }
.sig { display:inline-block; padding:4px 13px; border-radius:100px; font-size:.74rem; font-weight:700; margin:3px 3px 3px 0; }
.sig.high   { background:rgba(220,38,38,.10);  border:1px solid rgba(220,38,38,.28); }
.sig.medium { background:rgba(217,119,6,.10);  border:1px solid rgba(217,119,6,.28); }
.sig.low    { background:rgba(5,150,105,.10); border:1px solid rgba(5,150,105,.28); }

/* ── STATS ── */
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:1.2rem; }
.stat { background:#fff; border:1.5px solid var(--BD); border-radius:14px; padding:1rem .75rem; text-align:center; box-shadow:0 2px 10px var(--SH); }
.stat-num { font-size:1.75rem; font-weight:900; line-height:1; }
.stat-lbl { font-size:.64rem; color: var(--MT) !important; text-transform:uppercase; letter-spacing:.1em; margin-top:5px; font-weight:600; }

/* ── HISTORY ── */
.hist-item { background:#fff; border:1.5px solid var(--BD); border-radius:12px; padding:.8rem 1rem; margin-bottom:8px; display:flex; align-items:center; gap:10px; transition:all .15s; box-shadow:0 2px 8px var(--SH); }
.hist-item:hover { border-color:var(--BM); box-shadow:0 4px 16px var(--SM); transform:translateX(3px); }
.hist-dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
.hist-preview { font-size:.76rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:2px; color: var(--MT) !important; }

.divider { height:1px; margin:1.8rem 0; background:linear-gradient(90deg,transparent,var(--BD),transparent); }
.lbl { font-family:'Fira Code',monospace; font-size:.65rem; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color: var(--MT) !important; }

div[data-testid="stAlert"] { background:#fff !important; border:1.5px solid var(--BD) !important; border-radius:14px !important; }
div[data-testid="stAlert"] p { color: var(--TX) !important; }
.stSpinner > div { border-top-color: var(--P) !important; }
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:var(--BM); border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────
for k, v in [("history", []), ("last_result", None)]:
    if k not in st.session_state: st.session_state[k] = v

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
st.sidebar.caption(f"Messages ≥ {threshold}% confidence → flagged as spam")
st.sidebar.markdown("---")
if st.session_state.history:
    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.history = []; st.rerun()
st.sidebar.caption("SpamShield AI · v2.0\nPowered by Groq + LLaMA 3")

# ── Navbar ────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav">
  <div class="nav-logo">
    <div class="nav-icon">🛡️</div>
    <div class="nav-name">Spam<b>Shield</b></div>
  </div>
  <div class="nav-pill">AI DETECTION PLATFORM</div>
  <div class="nav-status"><div class="status-dot"></div> Active</div>
</div>""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag"><div class="hero-tag-dot"></div> Real-time AI Analysis</div>
  <h1>Detect Spam,</h1>
  <span class="hero-accent">Phishing & Scams</span>
  <p>Paste a message or upload a screenshot — SpamShield analyzes for threats,
     scams, urgency tactics, and phishing patterns instantly.</p>
  <div class="badges">
    <span class="badge spam">🚨 Spam Detection</span>
    <span class="badge warn">⚠️ Suspicious Flags</span>
    <span class="badge clean">✅ Clean Verification</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── Input Card — Text LEFT | Image RIGHT ─────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown("""
<div class="input-row-label">
  <div class="col-label">📝 Paste Message</div>
  <div class="or-pill">OR</div>
  <div class="col-label" style="text-align:right;">🖼️ Upload Image</div>
</div>""", unsafe_allow_html=True)

col_txt, col_img = st.columns(2, gap="medium")
user_input = ""; uploaded_img = None; img_b64 = None; img_mime = None

with col_txt:
    SAMPLES = {
        "— Try a sample —": "",
        "🔴 Phishing Email":   "URGENT: Your account has been suspended! Click here to verify: http://secure-bank-login.xyz/verify?token=abc123. Failure within 24h = permanent closure.",
        "🟡 Suspicious Offer": "Congratulations! You've been selected as today's lucky winner of an iPhone 15 Pro! Just pay $2 shipping: claimprize.info",
        "🟢 Legit Message":    "Hi, just a reminder that our team meeting is tomorrow at 10am in Conference Room B. Please review the agenda I shared last week.",
        "🔴 Scam SMS":         "FREE MSG: Your loan of Rs.50,000 is approved! Call 9988776655 now to claim. Limited time. Reply STOP to opt out.",
    }
    selected   = st.selectbox("sample", list(SAMPLES.keys()), label_visibility="collapsed")
    user_input = st.text_area("msg", value=SAMPLES.get(selected,""), height=200,
                              placeholder="Paste an email, SMS, social post, or any suspicious message here…",
                              label_visibility="collapsed")
    chars = len(user_input); words = len(user_input.split()) if user_input.strip() else 0
    st.markdown(f"<span style='font-family:Fira Code,monospace;font-size:.7rem;color:#94a3b8;'>{chars} chars · {words} words</span>", unsafe_allow_html=True)

with col_img:
    uploaded_img = st.file_uploader("img", type=["png","jpg","jpeg","webp","gif"],
                                    label_visibility="collapsed", key="img_upload")
    if uploaded_img:
        img_bytes = uploaded_img.read()
        img_b64   = base64.b64encode(img_bytes).decode()
        img_mime  = uploaded_img.type or "image/png"
        st.markdown(f"""
<div class="img-preview">
  <img src="data:{img_mime};base64,{img_b64}"
       style="width:100%;display:block;max-height:195px;object-fit:contain;padding:6px;"/>
  <div class="img-meta">✅ {uploaded_img.name} · {len(img_bytes)/1024:.1f} KB</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="text-align:center;padding:1.5rem .5rem;pointer-events:none;">
  <div style="font-size:2rem;margin-bottom:.5rem;">📸</div>
  <div style="font-size:.82rem;font-weight:700;color:#475569;">Drop a screenshot here</div>
  <div style="font-size:.74rem;color:#94a3b8;margin-top:4px;line-height:1.6;">
    PNG · JPG · WEBP · GIF<br>Spam SMS · Phishing emails<br>WhatsApp scams
  </div>
</div>""", unsafe_allow_html=True)

analyze_btn = st.button("🔍  Analyze", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Analysis Logic ────────────────────────────────────────────────────
def _ctx():
    checks = []
    if check_phishing:    checks.append("phishing links, deceptive URLs, lookalike domains")
    if check_urgency:     checks.append("urgency tactics, pressure language, countdown threats")
    if check_offers:      checks.append("fake prize claims, lottery wins, suspicious offers")
    if check_impersonate: checks.append("impersonation of banks, government, brands, support teams")
    if check_sentiment:   checks.append("overall sentiment and emotional manipulation")
    cs = "\n".join(f"- {c}" for c in checks) if checks else "- General spam patterns"
    ms = {"Auto (Balanced)":"Use balanced judgment.",
          "Strict (Low Tolerance)":"Be strict — flag anything remotely suspicious.",
          "Lenient (High Tolerance)":"Only flag clear, obvious spam."}[mode]
    hint = f" Content type: {content_type}." if content_type != "Auto-detect" else ""
    return cs, ms, hint

SCHEMA = '{"verdict":"SPAM|SUSPICIOUS|CLEAN","confidence":0-100,"reason":"...","signals":[{"label":"...","severity":"high|medium|low"}],"spam_score":0-100,"category":"...","sentiment":"..."}'

def _parse(raw):
    c = re.sub(r'```json|```','',raw).strip()
    m = re.search(r'\{.*\}', c, re.DOTALL)
    return json.loads(m.group() if m else c)

def analyze_text(text):
    cs, ms, hint = _ctx()
    prompt = f"""Spam detection AI. Analyze this message.{hint}
MODE: {ms}
CHECK: {cs}
Return ONLY valid JSON: {SCHEMA}
MESSAGE: \"\"\"{text[:3000]}\"\"\""""
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"Return valid JSON only."},{"role":"user","content":prompt}],
        temperature=0.1, max_tokens=800)
    result = _parse(r.choices[0].message.content)
    if result.get("confidence",0) >= threshold and result.get("verdict") == "SUSPICIOUS":
        result["verdict"] = "SPAM"
    return result

def analyze_image(b64, mime):
    cs, ms, hint = _ctx()
    prompt = f"""Spam detection AI with vision.{hint}
Image contains screenshot of message/email/SMS.
STEP 1: Extract ALL visible text. STEP 2: Analyze for spam.
MODE: {ms} CHECK: {cs}
Return ONLY valid JSON: {SCHEMA}
If no text visible, return CLEAN with low confidence."""
    r = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":prompt}]}],
        temperature=0.1, max_tokens=900)
    result = _parse(r.choices[0].message.content)
    if result.get("confidence",0) >= threshold and result.get("verdict") == "SUSPICIOUS":
        result["verdict"] = "SPAM"
    return result

# ── Run ───────────────────────────────────────────────────────────────
if analyze_btn:
    use_img  = uploaded_img is not None and img_b64 is not None
    use_text = bool(user_input.strip())
    if not use_img and not use_text:
        st.error("⚠️ Please paste a message or upload an image.")
    elif use_text and len(user_input.strip()) < 5:
        st.warning("Message is too short to analyze.")
    else:
        with st.spinner("🧠 Analyzing image with AI Vision…" if use_img else "🧠 Analyzing message…"):
            try:
                result = analyze_image(img_b64, img_mime) if use_img else analyze_text(user_input)
            except json.JSONDecodeError:
                st.error("❌ AI returned malformed response. Please try again."); st.stop()
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}"); st.stop()

        verdict    = result.get("verdict","UNKNOWN")
        confidence = result.get("confidence",0)
        reason     = result.get("reason","No explanation provided.")
        signals    = result.get("signals",[])
        category   = result.get("category","Unknown")
        sentiment  = result.get("sentiment","Neutral")
        preview    = f"[Image: {uploaded_img.name}]" if use_img else (user_input[:55]+("…" if len(user_input)>55 else ""))

        css, lbl, bar = {
            "SPAM":       ("spam",  "🚨 SPAM DETECTED", "#dc2626"),
            "SUSPICIOUS": ("warn",  "⚠️ SUSPICIOUS",    "#d97706"),
            "CLEAN":      ("clean", "✅ CLEAN",          "#059669"),
        }.get(verdict, ("warn","⚠️ UNKNOWN","#d97706"))

        st.session_state.history.insert(0,{"verdict":verdict,"confidence":confidence,"category":category,"preview":preview})
        if len(st.session_state.history) > 10: st.session_state.history = st.session_state.history[:10]

        st.markdown(f"""
<div class="result {css}">
  <div class="verdict {css}">{lbl}</div>
  <div class="vmeta">Confidence: {confidence}% &nbsp;·&nbsp; {category} &nbsp;·&nbsp; {sentiment}</div>
  <div class="conf-track"><div class="conf-fill" style="width:{confidence}%;background:{bar};"></div></div>
  <div class="reason">{reason}</div>""", unsafe_allow_html=True)
        if signals:
            tags_html = []
            for s in signals:
                sev = s.get("severity","low")
                ico = "🔴" if sev=="high" else "🟡" if sev=="medium" else "🟢"
                tags_html.append(f'<span class="sig {sev}">{ico} {s.get("label","")}</span>')
            tags = "".join(tags_html)
            st.markdown(f'<div class="sig-title">🔎 Detected Signals</div><div>{tags}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        n_spam  = sum(1 for h in st.session_state.history if h["verdict"]=="SPAM")
        n_sus   = sum(1 for h in st.session_state.history if h["verdict"]=="SUSPICIOUS")
        n_clean = sum(1 for h in st.session_state.history if h["verdict"]=="CLEAN")
        total   = len(st.session_state.history)
        st.markdown(f"""
<div class="stats">
  <div class="stat"><div class="stat-num" style="color:#dc2626">{n_spam}</div><div class="stat-lbl">Spam</div></div>
  <div class="stat"><div class="stat-num" style="color:#d97706">{n_sus}</div><div class="stat-lbl">Suspicious</div></div>
  <div class="stat"><div class="stat-num" style="color:#059669">{n_clean}</div><div class="stat-lbl">Clean</div></div>
  <div class="stat"><div class="stat-num" style="color:#1a3fa8">{total}</div><div class="stat-lbl">Scanned</div></div>
</div>""", unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin-bottom:.7rem;">📜 Recent Scans</div>', unsafe_allow_html=True)
    DOT  = {"SPAM":"#dc2626","CLEAN":"#059669","SUSPICIOUS":"#d97706"}
    ICON = {"SPAM":"🚨","CLEAN":"✅","SUSPICIOUS":"⚠️"}
    for h in st.session_state.history:
        dc = DOT.get(h["verdict"],"#d97706")
        st.markdown(f"""
<div class="hist-item">
  <div class="hist-dot" style="background:{dc};box-shadow:0 0 0 3px {dc}30;"></div>
  <div style="flex:1;overflow:hidden">
    <span style="font-weight:700;font-size:.88rem;">{ICON.get(h["verdict"],"❓")} {h["verdict"]}</span>
    <span style="margin:0 6px;color:#cbd5e1;">·</span>
    <span style="font-size:.78rem;color:#64748b;">{h["confidence"]}% · {h["category"]}</span>
    <div class="hist-preview">{h["preview"]}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Screenshot ────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
components.html("""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
body{margin:0;background:transparent;}
#btn{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1.5px solid rgba(26,63,168,.28);border-radius:100px;padding:9px 22px;font-family:'Plus Jakarta Sans',sans-serif;font-size:.85rem;font-weight:700;color:#1a3fa8;cursor:pointer;transition:all .18s;box-shadow:0 2px 12px rgba(26,63,168,.12);}
#btn:hover{background:#1a3fa8;color:#fff;box-shadow:0 4px 18px rgba(26,63,168,.38);transform:translateY(-1px);}
#btn.busy{opacity:.55;cursor:wait;pointer-events:none;}
#toast{display:none;position:fixed;top:18px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#1a3fa8,#2563eb);color:#fff;padding:9px 24px;border-radius:100px;font-family:sans-serif;font-size:.86rem;font-weight:700;box-shadow:0 4px 22px rgba(26,63,168,.4);z-index:999999;white-space:nowrap;}
</style>
<div id="toast">✅ Screenshot saved!</div>
<button id="btn" onclick="go()">📸 &nbsp;Save Screenshot</button>
<script>
function go(){
  var b=document.getElementById('btn'),t=document.getElementById('toast');
  b.classList.add('busy');b.innerHTML='⏳ Capturing…';
  var tw=window.parent,td=tw.document,el=td.getElementById('root')||td.querySelector('.stApp')||td.body;
  function run(){tw.html2canvas(el,{scale:2,useCORS:true,allowTaint:true,backgroundColor:'#f0f6ff',logging:false,scrollX:0,scrollY:-tw.scrollY,windowWidth:td.documentElement.scrollWidth,windowHeight:td.documentElement.scrollHeight}).then(function(c){var a=td.createElement('a');a.download='spamshield.png';a.href=c.toDataURL('image/png',1);td.body.appendChild(a);a.click();td.body.removeChild(a);b.classList.remove('busy');b.innerHTML='✅ Saved!';t.style.display='block';setTimeout(function(){t.style.display='none';b.innerHTML='📸 Save Screenshot';},3200);}).catch(function(e){b.classList.remove('busy');b.innerHTML='📸 Save Screenshot';alert('Failed: '+e.message);});}
  if(typeof tw.html2canvas==='undefined'){var s=td.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';s.onload=run;td.head.appendChild(s);}else{run();}
}
</script>
""", height=58)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#94a3b8;font-size:.72rem;font-family:'Fira Code',monospace;letter-spacing:.07em;padding-bottom:1.5rem;margin-top:.5rem;">
  SPAMSHIELD AI · GROQ + LLAMA 3.1 · NOT A SUBSTITUTE FOR PROFESSIONAL SECURITY TOOLS
</div>""", unsafe_allow_html=True)
