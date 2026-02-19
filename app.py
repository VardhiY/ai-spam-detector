import streamlit as st
from groq import Groq
import json
import re
import base64
import io

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Extractor",
    page_icon="📄",
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

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem; font-weight: 800;
    background: linear-gradient(135deg, #e8e8f0 30%, #6c63ff 70%, #ff6584 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.2rem;
}
.subtitle { text-align: center; color: #6b6b8a; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2rem; }
.badge { display: flex; justify-content: center; margin-bottom: 1rem; }
.badge span {
    background: linear-gradient(135deg, #6c63ff, #ff6584);
    color: white; padding: 0.3rem 1rem; border-radius: 999px;
    font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.result-box {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 14px;
    padding: 1.4rem; margin-top: 1rem; font-size: 0.88rem;
    line-height: 1.8; color: #e8e8f0; white-space: pre-wrap; word-break: break-word;
    position: relative;
}
.result-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #6c63ff, transparent);
}
.redacted { background: #ff165d22; border: 1px solid #ff165d55; border-radius: 6px; padding: 0.2rem 0.5rem; color: #ff6584; font-size: 0.78rem; }
.stat-card {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 12px;
    padding: 1rem; text-align: center;
}
.stat-num { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: #6c63ff; }
.stat-label { font-size: 0.72rem; color: #6b6b8a; letter-spacing: 0.05em; }
.tag {
    display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
    font-size: 0.72rem; margin: 0.15rem;
}
.tag-redacted { background: rgba(255,101,132,0.15); border: 1px solid rgba(255,101,132,0.4); color: #ff8fa3; }
.tag-clean    { background: rgba(67,233,123,0.12);  border: 1px solid rgba(67,233,123,0.35); color: #43e97b; }

div[data-testid="stFileUploader"] {
    background: #12121a !important; border: 2px dashed #2a2a3d !important;
    border-radius: 14px !important; padding: 1rem !important;
}
div[data-testid="stFileUploader"]:hover { border-color: #6c63ff !important; }
.stButton > button {
    width: 100%; background: linear-gradient(135deg, #6c63ff, #9b59f7) !important;
    color: white !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 12px !important; padding: 0.75rem !important;
}
.stButton > button:hover { box-shadow: 0 8px 30px rgba(108,99,255,0.4) !important; }
section[data-testid="stSidebar"] { background: #12121a !important; border-right: 1px solid #2a2a3d; }
div[data-testid="stSelectbox"] > div { background: #0a0a0f !important; border: 1px solid #2a2a3d !important; color: #e8e8f0 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────
st.markdown('<div class="badge"><span>📄 AI Document Extractor · Smart Redaction</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">AI Document Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extract text from any document or image · Sensitive data auto-redacted.</div>', unsafe_allow_html=True)

# ── Sidebar toggle friendly ───────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { min-width: 250px !important; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Settings ──────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Settings")
st.sidebar.markdown("**Redact sensitive data:**")
redact_ids       = st.sidebar.checkbox("🪪 ID / Aadhaar / SSN numbers",  value=True)
redact_phones    = st.sidebar.checkbox("📞 Phone numbers & emails",       value=True)
redact_banking   = st.sidebar.checkbox("💳 Bank / credit card numbers",   value=True)
redact_passwords = st.sidebar.checkbox("🔑 Passwords & secret keys",      value=True)
redact_names     = st.sidebar.checkbox("👤 Personal names",                value=False)
redact_dates     = st.sidebar.checkbox("📅 Dates of birth",                value=False)
show_redacted    = st.sidebar.checkbox("Show [REDACTED] placeholders",     value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#6b6b8a'>AI Document Extractor · v1.0</small>", unsafe_allow_html=True)

# ── Build Redaction Rules ─────────────────────────────────────────────
def build_redaction_prompt():
    rules = []
    if redact_ids:       rules.append("Aadhaar numbers (12-digit, may be spaced as XXXX XXXX XXXX), SSN, PAN card numbers (format: ABCDE1234F), passport numbers, driving license numbers, voter ID, any government ID number")
    if redact_phones:    rules.append("phone numbers, mobile numbers (+91 or 10-digit), email addresses, contact numbers")
    if redact_banking:   rules.append("bank account numbers, IFSC codes, credit card numbers, debit card numbers, CVV, UPI IDs, MICR codes")
    if redact_passwords: rules.append("passwords, API keys, secret keys, tokens, OTPs, PINs")
    if redact_names:     rules.append("full names of any person — INCLUDING names on Aadhaar cards, identity documents, official documents. Names usually appear after labels like 'Name:', 'नाम:', or at the top of the document")
    if redact_dates:     rules.append("dates of birth in ANY format (DD/MM/YYYY, YYYY-MM-DD, written like '15 August 1990'), DOB, Year of Birth, जन्म तिथि")
    return rules

# ── Extract text from PDF ─────────────────────────────────────────────
def extract_from_pdf(file_bytes):
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except ImportError:
        return None

# ── Extract text from DOCX ────────────────────────────────────────────
def extract_from_docx(file_bytes):
    try:
        import docx
        doc  = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text.strip()
    except ImportError:
        return None

# ── Extract text from XLSX ────────────────────────────────────────────
def extract_from_xlsx(file_bytes):
    try:
        import openpyxl
        wb   = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        rows = []
        for sheet in wb.worksheets:
            rows.append(f"[Sheet: {sheet.title}]")
            for row in sheet.iter_rows(values_only=True):
                line = " | ".join(str(c) for c in row if c is not None)
                if line.strip():
                    rows.append(line)
        return "\n".join(rows).strip()
    except ImportError:
        return None

# ── Extract text from PPTX ────────────────────────────────────────────
def extract_from_pptx(file_bytes):
    try:
        from pptx import Presentation
        prs   = Presentation(io.BytesIO(file_bytes))
        lines = []
        for i, slide in enumerate(prs.slides, 1):
            lines.append(f"[Slide {i}]")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines).strip()
    except ImportError:
        return None

# ── Extract text from Image using Groq vision ─────────────────────────
def extract_from_image(file_bytes, mime_type):
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{b64}"}
                },
                {
                    "type": "text",
                    "text": "Extract ALL text from this image exactly as it appears. Return only the raw extracted text, nothing else. Preserve formatting and line breaks."
                }
            ]
        }],
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

# ── Redact sensitive info via Groq ────────────────────────────────────
def redact_sensitive(text, rules):
    if not rules:
        return text, [], 0

    placeholder = "[REDACTED]" if show_redacted else "████"

    prompt = f"""You are a strict data privacy and redaction engine. Redact ALL sensitive data from the text below.

SENSITIVE CATEGORIES (be extremely thorough — missing even one is a privacy violation):
{chr(10).join(f'- {r}' for r in rules)}

CRITICAL RULES:
- This text may come from an Aadhaar card, passport, or government ID document
- You MUST find and replace EVERY single instance without exception
- Replace ONLY the sensitive value itself with "{placeholder}", keep all surrounding text
- Names on Aadhaar appear after "Name:", "नाम:" or at the very top — REDACT them
- DOB appears after "DOB:", "Date of Birth:", "जन्म तिथि:" — REDACT the date value
- Aadhaar numbers are 12 digits (may be spaced: XXXX XXXX XXXX) — REDACT them
- When in doubt about whether something is sensitive — REDACT it
- Do NOT keep any sensitive data visible under any circumstance

Return a JSON object with:
  - "clean_text": the full text with ALL sensitive parts replaced with "{placeholder}"
  - "redacted_items": list of strings describing each redacted item (e.g. ["name: John Doe", "DOB: 01/01/1990"])
  - "redaction_count": total number of replacements made

Return ONLY valid JSON. No markdown fences, no explanation.

TEXT TO REDACT:
{text[:6000]}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a strict data privacy engine. You must redact ALL sensitive information without exception. Never leave any sensitive data visible. Always return only valid JSON with no extra text."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=4000
    )
    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```', '', raw).strip()

    try:
        result = json.loads(cleaned)
        clean  = result.get("clean_text", text)
        items  = result.get("redacted_items", [])
        count  = result.get("redaction_count", 0)

        # Double-check with regex as safety net
        clean, extra_items, extra_count = regex_redact(clean, placeholder)
        items  = items + extra_items
        count  = count + extra_count

        return clean, items, count
    except:
        return regex_redact(text, placeholder)

# ── Regex fallback redaction ──────────────────────────────────────────
def regex_redact(text, placeholder="[REDACTED]"):
    count   = 0
    removed = []

    if redact_ids:
        # Aadhaar: 12 digits optionally spaced
        new = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', placeholder, text)
        if new != text: count += 1; removed.append("Aadhaar number"); text = new
        # PAN
        new = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', placeholder, text)
        if new != text: count += 1; removed.append("PAN number"); text = new

    if redact_phones:
        new = re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b', placeholder, text)
        if new != text: count += 1; removed.append("phone number"); text = new
        new = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', placeholder, text)
        if new != text: count += 1; removed.append("email address"); text = new

    if redact_banking:
        new = re.sub(r'\b(?:\d[ -]*?){13,16}\b', placeholder, text)
        if new != text: count += 1; removed.append("card number"); text = new
        new = re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', placeholder, text)
        if new != text: count += 1; removed.append("IFSC code"); text = new

    if redact_dates:
        # DD/MM/YYYY or DD-MM-YYYY
        new = re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b', placeholder, text)
        if new != text: count += 1; removed.append("date of birth"); text = new
        # DOB: label followed by date
        new = re.sub(r'(DOB|Date of Birth|जन्म तिथि)\s*[:\-]?\s*[\d\/\-\w ]+', lambda m: m.group(0).split(':')[0] + ': ' + placeholder if ':' in m.group(0) else placeholder, text)
        if new != text: count += 1; removed.append("DOB field"); text = new

    if redact_names:
        # Name: label followed by value
        new = re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}', lambda m: m.group(0).split(':')[0] + ': ' + placeholder, text)
        if new != text: count += 1; removed.append("name field"); text = new

    return text, removed, count

# ── Main UI ───────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload a document or image",
    type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "pptx", "ppt"],
    label_visibility="collapsed"
)

if uploaded:
    st.markdown(f"**📎 {uploaded.name}** · `{uploaded.type}` · `{uploaded.size/1024:.1f} KB`")

run = st.button("🔍 Extract & Redact", use_container_width=True)

if run and uploaded:
    file_bytes = uploaded.read()
    mime       = uploaded.type
    name       = uploaded.name.lower()
    raw_text   = None

    # ── Step 1: Extract text ──────────────────────────────────────────
    with st.spinner("📖 Extracting text from document..."):
        try:
            if name.endswith(".pdf"):
                raw_text = extract_from_pdf(file_bytes)
                if not raw_text:
                    st.warning("Could not extract text from PDF — trying AI vision...")
                    raw_text = extract_from_image(file_bytes, "application/pdf")

            elif name.endswith((".png", ".jpg", ".jpeg")):
                raw_text = extract_from_image(file_bytes, mime)

            elif name.endswith(".docx"):
                raw_text = extract_from_docx(file_bytes)

            elif name.endswith(".xlsx"):
                raw_text = extract_from_xlsx(file_bytes)

            elif name.endswith((".pptx", ".ppt")):
                raw_text = extract_from_pptx(file_bytes)
                if not raw_text:
                    st.warning("Could not extract text from PPT — trying AI vision...")
                    raw_text = extract_from_image(file_bytes, mime)

        except Exception as e:
            st.error(f"Extraction error: {e}")
            raw_text = None

    if not raw_text or len(raw_text.strip()) < 5:
        st.error("❌ Could not extract any text from this file. Try a different file.")
        st.stop()

    # ── Step 2: Redact sensitive info ─────────────────────────────────
    rules      = build_redaction_prompt()
    clean_text = raw_text
    items      = []
    count      = 0

    if rules:
        with st.spinner("🔒 Scanning and redacting sensitive information..."):
            try:
                clean_text, items, count = redact_sensitive(raw_text, rules)
            except Exception as e:
                st.warning(f"AI redaction failed, using regex fallback: {e}")
                clean_text, items, count = regex_redact(raw_text)
    else:
        st.info("ℹ️ No redaction rules selected — showing full extracted text.")

    # ── Step 3: Show results ──────────────────────────────────────────
    st.markdown("---")

    # Stats
    word_count = len(clean_text.split())
    char_count = len(clean_text)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{word_count:,}</div><div class="stat-label">WORDS EXTRACTED</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{count}</div><div class="stat-label">ITEMS REDACTED</div></div>', unsafe_allow_html=True)
    with c3:
        status = "✅ CLEAN" if count == 0 else "🔒 REDACTED"
        color  = "#43e97b" if count == 0 else "#ff8fa3"
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{color};font-size:1.1rem;padding-top:.4rem">{status}</div><div class="stat-label">DOCUMENT STATUS</div></div>', unsafe_allow_html=True)

    # Redacted items tags
    if items:
        st.markdown("<br>**🔒 Redacted categories:**", unsafe_allow_html=True)
        tags = "".join(f'<span class="tag tag-redacted">🚫 {i}</span>' for i in set(items))
        st.markdown(f'<div style="margin:.5rem 0">{tags}</div>', unsafe_allow_html=True)

    # Extracted text
    st.markdown("<br>**📝 Extracted Text:**", unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{clean_text}</div>', unsafe_allow_html=True)

    # Download buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    col_a.download_button(
        "⬇️ Download Clean Text (.txt)",
        clean_text, f"{uploaded.name}_extracted.txt", "text/plain",
        use_container_width=True
    )
    col_b.download_button(
        "⬇️ Download as JSON",
        json.dumps({"filename": uploaded.name, "extracted_text": clean_text,
                    "redacted_count": count, "redacted_categories": list(set(items))}, indent=2),
        f"{uploaded.name}_extracted.json", "application/json",
        use_container_width=True
    )

elif run and not uploaded:
    st.error("Please upload a file first.")
