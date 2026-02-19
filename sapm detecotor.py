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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
.stApp { background: #0a0a0f; color: #e8e8f0; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

[data-testid="stSidebar"] { min-width: 250px !important; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem; font-weight: 800;
    background: linear-gradient(135deg, #e8e8f0 30%, #ff6584 70%, #ff3860 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.2rem;
}
.subtitle { text-align: center; color: #6b6b8a; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2rem; }
.badge { display: flex; justify-content: center; margin-bottom: 1rem; }
.badge span {
    background: linear-gradient(135deg, #ff3860, #ff6584);
    color: white; padding: 0.3rem 1rem; border-radius: 999px;
    font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
}

/* Result cards */
.verdict-spam {
    background: rgba(255,56,96,0.1); border: 2px solid rgba(255,56,96,0.5);
    border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0;
}
.verdict-safe {
    background: rgba(67,233,123,0.1); border: 2px solid rgba(67,233,123,0.5);
    border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0;
}
.verdict-label-spam { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #ff3860; }
.verdict-label-safe { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #43e97b; }
.verdict-sub { font-size: 0.78rem; color: #6b6b8a; margin-top: 0.3rem; letter-spacing: 0.05em; }

.stat-card {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 12px;
    padding: 1rem; text-align: center;
}
.stat-num { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; }
.stat-label { font-size: 0.7rem; color: #6b6b8a; letter-spacing: 0.05em; text-transform: uppercase; }

.reason-box {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 12px;
    padding: 1.2rem; margin: 0.5rem 0; position: relative; overflow: hidden;
}
.reason-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #ff6584, transparent);
}
.reason-title { font-size: 0.72rem; letter-spacing: 0.08em; color: #6b6b8a; text-transform: uppercase; margin-bottom: 0.6rem; }
.reason-text { font-size: 0.88rem; line-height: 1.7; color: #e8e8f0; }

.tag-spam    { display:inline-block; background:rgba(255,56,96,0.15);  border:1px solid rgba(255,56,96,0.4);  color:#ff6584; padding:.2rem .6rem; border-radius:999px; font-size:.75rem; margin:.15rem; }
.tag-safe    { display:inline-block; background:rgba(67,233,123,0.12); border:1px solid rgba(67,233,123,0.35); color:#43e97b; padding:.2rem .6rem; border-radius:999px; font-size:.75rem; margin:.15rem; }
.tag-warning { display:inline-block; background:rgba(255,193,7,0.12);  border:1px solid rgba(255,193,7,0.35);  color:#ffc107; padding:.2rem .6rem; border-radius:999px; font-size:.75rem; margin:.15rem; }

.highlight-spam { background: rgba(255,56,96,0.25); border-radius: 4px; padding: 0 3px; color: #ff8fa3; font-weight: 500; }
.highlight-warn { background: rgba(255,193,7,0.2);  border-radius: 4px; padding: 0 3px; color: #ffc107; font-weight: 500; }

.text-preview {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 12px;
    padding: 1.2rem; font-size: 0.86rem; line-height: 1.8; margin: 0.5rem 0;
    max-height: 200px; overflow-y: auto;
}
.history-item {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 10px;
    padding: 0.8rem 1rem; margin: 0.4rem 0; display: flex;
    align-items: center; justify-content: space-between; gap: 1rem;
}
.history-text { font-size: 0.8rem; color: #a0a0b8; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: #0a0a0f !important; border: 1px solid #2a2a3d !important;
    color: #e8e8f0 !important; font-family: 'DM Mono', monospace !important;
    border-radius: 10px !important;
}
div[data-testid="stSelectbox"] > div {
    background: #0a0a0f !important; border: 1px solid #2a2a3d !important;
    color: #e8e8f0 !important; border-radius: 8px !important;
}
.stButton > button {
    width: 100%; background: linear-gradient(135deg, #ff3860, #ff6584) !important;
    color: white !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 12px !important; padding: 0.75rem !important;
}
.stButton > button:hover { box-shadow: 0 8px 30px rgba(255,56,96,0.4) !important; }
section[data-testid="stSidebar"] { background: #12121a !important; border-right: 1px solid #2a2a3d; }
div[data-testid="stSelectbox"] > div { background: #0a0a0f !important; border: 1px solid #2a2a3d !important; color: #e8e8f0 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────
st.markdown('<div class="badge"><span>🛡️ AI Spam Detector · Powered by Groq</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">AI Spam Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Detect spam in emails, SMS, comments & URLs — instantly with AI.</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Settings")
content_type = st.sidebar.selectbox(
    "Content Type",
    ["Email", "SMS / Text Message", "Social Media Comment", "URL / Link"],
    index=0
)
sensitivity = st.sidebar.selectbox(
    "Detection Sensitivity",
    ["Low (fewer false positives)", "Medium (balanced)", "High (strict)"],
    index=1
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Session Stats")
if "history" not in st.session_state:
    st.session_state.history  = []
    st.session_state.spam_count = 0
    st.session_state.safe_count = 0

total = len(st.session_state.history)
st.sidebar.metric("Total Checked", total)
st.sidebar.metric("Spam Found",    st.session_state.spam_count)
st.sidebar.metric("Safe",          st.session_state.safe_count)

if total > 0 and st.sidebar.button("🗑️ Clear History", use_container_width=True):
    st.session_state.history   = []
    st.session_state.spam_count = 0
    st.session_state.safe_count = 0
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#6b6b8a'>AI Spam Detector · v1.0</small>", unsafe_allow_html=True)

# ── Spam Detection Function ───────────────────────────────────────────
def detect_spam(text, content_type, sensitivity):
    sensitivity_map = {
        "Low (fewer false positives)":  "Be lenient. Only flag obvious spam. Prefer safe over spam when uncertain.",
        "Medium (balanced)":            "Be balanced. Flag clear spam patterns but avoid false positives.",
        "High (strict)":                "Be strict. Flag anything suspicious, even if mildly spammy."
    }

    prompt = f"""You are an expert AI spam detection engine. Analyze the following {content_type} content and determine if it is spam or not.

DETECTION SENSITIVITY: {sensitivity_map[sensitivity]}

SPAM INDICATORS TO CHECK:
- Unsolicited promotions, offers, prizes, lottery wins
- Urgency language: "Act now!", "Limited time!", "You won!", "Claim your prize!"
- Suspicious URLs, phishing links, unknown domains
- Requests for personal info, passwords, OTPs, bank details
- Excessive capitalization, exclamation marks, emojis used manipulatively
- Too-good-to-be-true claims (free money, weight loss, miracle cures)
- Impersonation of banks, government, celebrities
- Grammatical errors typical of spam
- Suspicious sender patterns

Analyze this {content_type}:
\"\"\"{text[:3000]}\"\"\"

Return ONLY a valid JSON object with these exact fields:
{{
  "verdict": "SPAM" or "NOT SPAM",
  "confidence": <number 0-100>,
  "spam_score": <number 0-100>,
  "category": <one of: "Phishing", "Promotional", "Scam", "Malware", "Social Engineering", "Legitimate", "Suspicious">,
  "reasons": [<list of 2-4 specific reasons for the verdict>],
  "suspicious_words": [<list of specific words/phrases that are suspicious, empty list if none>],
  "safe_words": [<list of 2-3 words that indicate legitimacy, empty list if spam>],
  "recommendation": <one short action sentence for the user>
}}

Return ONLY valid JSON. No markdown, no explanation."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a spam detection expert. Analyze content accurately and return only valid JSON."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1000
    )

    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```', '', raw).strip()
    return json.loads(cleaned)

# ── Highlight suspicious words in text ───────────────────────────────
def highlight_text(text, suspicious_words, safe_words):
    highlighted = text
    for word in sorted(suspicious_words, key=len, reverse=True):
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(f'<span class="highlight-spam">{word}</span>', highlighted)
    for word in sorted(safe_words, key=len, reverse=True):
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted = pattern.sub(f'<span class="highlight-warn">{word}</span>', highlighted)
    return highlighted

# ── Input ─────────────────────────────────────────────────────────────
type_placeholders = {
    "Email":                  "Paste the full email content here including subject, body...",
    "SMS / Text Message":     "Paste the SMS or text message here...",
    "Social Media Comment":   "Paste the comment or post here...",
    "URL / Link":             "Paste the URL or link here (e.g. https://suspicious-site.com/offer?id=123)..."
}

user_input = st.text_area(
    "Input",
    height=180,
    placeholder=type_placeholders.get(content_type, "Paste content here..."),
    label_visibility="collapsed"
)

col_a, col_b = st.columns([3, 1])
with col_a:
    run = st.button("🔍 Analyze for Spam", use_container_width=True)
with col_b:
    clear = st.button("✕ Clear", use_container_width=True)

if clear:
    st.rerun()

# ── Run Detection ─────────────────────────────────────────────────────
if run:
    if not user_input.strip():
        st.error("Please enter some content to analyze.")
    elif len(user_input.strip()) < 5:
        st.error("Content too short to analyze. Please enter more text.")
    else:
        with st.spinner("🧠 Analyzing content with AI..."):
            try:
                result = detect_spam(user_input, content_type, sensitivity)

                is_spam    = result.get("verdict", "NOT SPAM") == "SPAM"
                confidence = result.get("confidence", 0)
                spam_score = result.get("spam_score", 0)
                category   = result.get("category", "Unknown")
                reasons    = result.get("reasons", [])
                susp_words = result.get("suspicious_words", [])
                safe_words = result.get("safe_words", [])
                recommend  = result.get("recommendation", "")

                # Update history & stats
                st.session_state.history.insert(0, {
                    "text":    user_input[:80] + "..." if len(user_input) > 80 else user_input,
                    "verdict": "SPAM" if is_spam else "NOT SPAM",
                    "score":   spam_score,
                    "type":    content_type
                })
                if is_spam:
                    st.session_state.spam_count += 1
                else:
                    st.session_state.safe_count += 1

                # ── Verdict Banner ────────────────────────────────────
                st.markdown("---")
                if is_spam:
                    st.markdown(f"""
                    <div class="verdict-spam">
                        <div class="verdict-label-spam">🚨 SPAM DETECTED</div>
                        <div class="verdict-sub">CONFIDENCE: {confidence}% · CATEGORY: {category.upper()}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="verdict-safe">
                        <div class="verdict-label-safe">✅ NOT SPAM</div>
                        <div class="verdict-sub">CONFIDENCE: {confidence}% · CATEGORY: {category.upper()}</div>
                    </div>""", unsafe_allow_html=True)

                # ── Stats Row ─────────────────────────────────────────
                c1, c2, c3 = st.columns(3)
                score_color = "#ff3860" if spam_score > 60 else "#ffc107" if spam_score > 30 else "#43e97b"
                with c1:
                    st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{score_color}">{spam_score}/100</div><div class="stat-label">Spam Score</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#6c63ff">{confidence}%</div><div class="stat-label">Confidence</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="stat-card"><div class="stat-num" style="font-size:1rem;padding-top:.5rem">{category}</div><div class="stat-label">Category</div></div>', unsafe_allow_html=True)

                # ── Reasons ───────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**🔎 Why this verdict:**")
                reason_text = "\n".join(f"• {r}" for r in reasons)
                st.markdown(f'<div class="reason-box"><div class="reason-text">{reason_text}</div></div>', unsafe_allow_html=True)

                # ── Suspicious / Safe Word Tags ───────────────────────
                if susp_words:
                    st.markdown("**🚩 Suspicious words/phrases:**")
                    tags = "".join(f'<span class="tag-spam">⚠ {w}</span>' for w in susp_words)
                    st.markdown(f'<div style="margin:.4rem 0">{tags}</div>', unsafe_allow_html=True)

                if safe_words and not is_spam:
                    st.markdown("**✅ Legitimacy indicators:**")
                    tags = "".join(f'<span class="tag-safe">✓ {w}</span>' for w in safe_words)
                    st.markdown(f'<div style="margin:.4rem 0">{tags}</div>', unsafe_allow_html=True)

                # ── Highlighted Text Preview ──────────────────────────
                if susp_words or safe_words:
                    st.markdown("**📝 Content with highlights:**")
                    highlighted = highlight_text(user_input, susp_words, safe_words if not is_spam else [])
                    st.markdown(f'<div class="text-preview">{highlighted}</div>', unsafe_allow_html=True)

                # ── Recommendation ────────────────────────────────────
                rec_color = "#ff6584" if is_spam else "#43e97b"
                st.markdown(f"""
                <div class="reason-box" style="border-color:{rec_color}33; margin-top:.5rem">
                    <div class="reason-title">💡 Recommendation</div>
                    <div class="reason-text" style="color:{rec_color}">{recommend}</div>
                </div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Detection failed: {e}")

# ── History ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("**🕓 Recent Checks:**")
    for item in st.session_state.history[:5]:
        badge_color = "#ff3860" if item["verdict"] == "SPAM" else "#43e97b"
        badge_text  = "🚨 SPAM" if item["verdict"] == "SPAM" else "✅ SAFE"
        st.markdown(f"""
        <div class="history-item">
            <span class="history-text">{item['text']}</span>
            <span style="color:#6b6b8a;font-size:.72rem">{item['type']}</span>
            <span style="color:{badge_color};font-size:.78rem;font-weight:600;white-space:nowrap">{badge_text} · {item['score']}/100</span>
        </div>""", unsafe_allow_html=True)
