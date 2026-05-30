"""
INAMS-ASRU Neuro-Surgical Co-Pilot
Medical workshop AI showcase — Streamlit application.
"""
import base64
import json
import os
from io import BytesIO

import anthropic
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv()

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="INAMS-ASRU Neuro-Surgical Co-Pilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Colour palette — Minimal White & Blue ────────────────────────────────────
BG      = "#F0F4F8"   # light gray-blue page background
SURFACE = "#FFFFFF"   # white surface
CARD    = "#FFFFFF"   # white cards
BORDER  = "#DDE3ED"   # soft gray border
CYAN    = "#2563EB"   # primary blue accent (replaces neon cyan)
BLUE    = "#1E40AF"   # deep blue
TEXT    = "#1E293B"   # near-black body text
MUTED   = "#64748B"   # medium gray secondary text
SUCCESS = "#059669"   # emerald green
WARNING = "#D97706"   # amber
DANGER  = "#DC2626"   # red
ORANGE  = "#EA580C"   # orange

BBOX_COLORS = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#EA580C"]
CATEGORY_COLORS = {
    "Pathology": DANGER,
    "USMLE":     CYAN,
    "Surgical":  WARNING,
    "Imaging":   SUCCESS,
}

# ── Global CSS — Minimal White & Blue ────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    background-color: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}
.stApp {{ background-color: {BG} !important; }}
.main .block-container {{
    padding: 1.25rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}}

/* Hide default Streamlit chrome */
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ display: none; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {SURFACE} !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid {BORDER} !important;
    gap: 4px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {MUTED} !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
    font-size: 0.93rem !important;
    padding: 0.5rem 1.75rem !important;
    border: none !important;
    transition: all 0.18s ease !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: {CYAN} !important;
    background: #EFF6FF !important;
}}
.stTabs [aria-selected="true"] {{
    background: #EFF6FF !important;
    color: {CYAN} !important;
    border: 1px solid #BFDBFE !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding-top: 1.5rem !important;
}}

/* ── Primary button — solid blue ── */
.stButton > button {{
    background: {CYAN} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.3px !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.18) !important;
}}
.stButton > button:hover {{
    background: {BLUE} !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.28) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.18) !important;
}}

/* ── Download button — solid green ── */
.stDownloadButton > button {{
    background: {SUCCESS} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 8px rgba(5,150,105,0.18) !important;
}}
.stDownloadButton > button:hover {{
    background: #047857 !important;
    box-shadow: 0 4px 12px rgba(5,150,105,0.28) !important;
    transform: translateY(-1px) !important;
}}

/* ── Inputs ── */
.stTextInput > label, .stSelectbox > label,
.stMultiSelect > label, .stRadio > label {{
    color: {MUTED} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    text-transform: uppercase !important;
}}
.stTextInput input {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}}
.stTextInput input:focus {{
    border-color: {CYAN} !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}}
[data-baseweb="select"] > div, [data-baseweb="select"] > div:hover {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}}
[data-baseweb="menu"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
}}
[data-baseweb="option"] {{ background: {SURFACE} !important; color: {TEXT} !important; }}
[data-baseweb="option"]:hover {{ background: #EFF6FF !important; color: {CYAN} !important; }}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {{
    background: {SURFACE} !important;
    border: 1.5px dashed {BORDER} !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {CYAN} !important;
    background: #EFF6FF !important;
}}

/* ── Progress bar ── */
.stProgress > div > div {{ background: #E2E8F0 !important; border-radius: 4px !important; }}
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {CYAN}, {BLUE}) !important;
    border-radius: 4px !important;
}}

/* ── Radio option text (inner <p> tags) ── */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] div[role="radiogroup"] label,
.stRadio label {{ color: {TEXT} !important; }}

/* ── Checkbox label text ── */
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label span,
.stCheckbox label,
.stCheckbox > label,
.stCheckbox > label p {{ color: {TEXT} !important; }}

/* ── General markdown text inside widgets ── */
div[data-testid="stMarkdownContainer"] p {{ color: {TEXT} !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{ color: {TEXT} !important; }}

/* ── Images ── */
.stImage img {{
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}}

/* ── Alerts ── */
.stAlert {{ border-radius: 8px !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {CYAN}; }}
</style>
""", unsafe_allow_html=True)

# ── System prompts ────────────────────────────────────────────────────────────
ANATOMIST_SYSTEM_PROMPT = """You are The Anatomist — an expert neuro-anatomical AI assistant for porcine brain and eye dissection workshops in medical education.

Context:
- Specimens are formalin-fixed Sus scrofa (porcine) brains (~70 g) or eyes
- Human brain comparison: ~1400 g
- Audience: MBBS students learning anatomy through comparative dissection

CRITICAL OUTPUT RULE: Return ONLY a single valid JSON object. No markdown fences, no preamble, no text outside the JSON. The full response must be parseable by json.loads().

JSON schema:
{
  "structures": [
    {"name": "string", "confidence": 0-100, "location": "string", "bbox": [x%, y%, w%, h%]}
  ],
  "human_equivalents": [
    {"porcine": "string", "human": "string", "similarity": "High|Moderate|Low", "clinical_note": "string"}
  ],
  "clinical_pearls": [
    {"category": "Pathology|USMLE|Surgical|Imaging", "pearl": "string"}
  ],
  "safety_warnings": [
    {"level": "critical|moderate|advisory", "structure": "string", "warning": "string"}
  ],
  "summary": "2-3 sentence expert summary"
}

Rules:
- Never fabricate structures not visible in the image
- Minimum 3 clinical pearls
- Always flag cranial nerves, major vessels, and eloquent cortex in safety_warnings
- confidence: integer 0-100; bbox values: percentage floats 0-100
- If image is not a neurological dissection specimen return: {"error": "Image does not appear to show a neurological dissection specimen. Please upload a dissection photograph."}
"""

COMMUNICATOR_SYSTEM_PROMPT = """You are The Communicator — an expert medical communication specialist who creates patient-friendly consent form explanations.

Your role:
- Generate clear, compassionate consent form explanations for medical procedures
- Adapt language complexity and tone to the specified patient profile
- Evidence-based only — never fabricate statistics or outcomes
- For paediatric guardian mode: address parent/guardian and refer to "your child"
- For elderly/low health literacy: short sentences, simple vocabulary

CRITICAL OUTPUT RULE: Return ONLY a single valid JSON object. No markdown fences, no preamble, no text outside the JSON. The full response must be parseable by json.loads().

JSON schema:
{
  "procedure_title": "Full formal procedure name",
  "sections": [
    {"heading": "string", "content": "2-4 sentence patient-friendly explanation", "important": true|false}
  ],
  "key_risks": ["risk 1", "risk 2", "risk 3"],
  "questions_to_ask": ["Question 1?", "Question 2?"],
  "disclaimer": "Standard medical disclaimer text"
}

Rules:
- Mark "important": true ONLY for sections containing risk, complication, or critical decision information
- Always include a disclaimer stating this is AI-generated and must be reviewed by a qualified doctor before clinical use
- If the procedure is not a recognised medical procedure return: {"error": "The specified procedure is not a recognised medical procedure. Please enter a valid procedure name."}
"""

# ── Anthropic client (cached) ─────────────────────────────────────────────────
@st.cache_resource
def get_client() -> anthropic.Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


# ── Image utilities ───────────────────────────────────────────────────────────
def _resize_to_jpeg(image_bytes: bytes, max_px: int = 1024) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    if max(img.size) > max_px:
        ratio = max_px / max(img.size)
        img = img.resize(
            (int(img.width * ratio), int(img.height * ratio)),
            Image.LANCZOS,
        )
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def analyse_image(image_bytes: bytes, mode: str) -> dict:
    client = get_client()
    if not client:
        return {"error": "API key not configured. Add ANTHROPIC_API_KEY to your .env file."}
    try:
        jpeg = _resize_to_jpeg(image_bytes)
        b64 = base64.standard_b64encode(jpeg).decode("utf-8")
        mode_label = "porcine (Sus scrofa)" if mode == "Porcine mode" else "human"
        user_text = (
            f"Analyse this {mode_label} neurological dissection specimen photograph. "
            "Identify all visible anatomical structures, provide porcine-to-human equivalency "
            "mappings, generate relevant clinical pearls for MBBS students, and flag any "
            "safety-relevant structures. Return the analysis as a single valid JSON object."
        )
        response = get_client().messages.create(
            model="claude-opus-4-6",
            max_tokens=2500,
            system=ANATOMIST_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                        },
                        {"type": "text", "text": user_text},
                    ],
                }
            ],
        )
        raw = response.content[0].text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        return {"error": f"Failed to parse AI response as JSON: {exc}"}
    except anthropic.APIError as exc:
        return {"error": f"Anthropic API error: {exc}"}
    except Exception as exc:
        return {"error": f"Unexpected error: {exc}"}


def draw_bboxes(image_bytes: bytes, structures: list) -> bytes:
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        for i, struct in enumerate(structures):
            color = BBOX_COLORS[i % len(BBOX_COLORS)]
            bbox = struct.get("bbox", [])
            if len(bbox) != 4:
                continue
            x_p, y_p, w_p, h_p = bbox
            x = int(x_p / 100 * img.width)
            y = int(y_p / 100 * img.height)
            w = int(w_p / 100 * img.width)
            h = int(h_p / 100 * img.height)
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            label = struct.get("name", f"S{i + 1}")
            # Background pill for label
            try:
                tb = draw.textbbox((x + 4, y + 4), label)
                draw.rectangle([tb[0] - 2, tb[1] - 2, tb[2] + 4, tb[3] + 2], fill=(2, 11, 26, 200))
            except Exception:
                pass
            draw.text((x + 4, y + 4), label, fill=color)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()
    except Exception:
        return image_bytes


# ── Consent generator ─────────────────────────────────────────────────────────
def generate_consent(
    procedure: str,
    patient_profile: str,
    complexity: str,
    sections: list,
) -> tuple[dict, dict]:
    client = get_client()
    if not client:
        return {"error": "API key not configured. Add ANTHROPIC_API_KEY to your .env file."}, {}
    try:
        sections_str = "\n".join(f"  - {s}" for s in sections)
        user_text = (
            f"Generate a patient consent form explanation.\n\n"
            f"Procedure: {procedure}\n"
            f"Patient profile: {patient_profile}\n"
            f"Language complexity: {complexity}\n"
            f"Required sections:\n{sections_str}\n\n"
            "Return the complete consent form as a single valid JSON object."
        )
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=COMMUNICATOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1].lstrip("json").strip() if len(parts) > 1 else raw
        usage = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
        return json.loads(raw), usage
    except json.JSONDecodeError as exc:
        return {"error": f"Failed to parse AI response: {exc}"}, {}
    except anthropic.APIError as exc:
        return {"error": f"Anthropic API error: {exc}"}, {}
    except Exception as exc:
        return {"error": f"Unexpected error: {exc}"}, {}


# ── HTML component helpers ────────────────────────────────────────────────────
def _badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
        f'border-radius:20px;padding:2px 10px;font-size:0.72rem;font-weight:600;">{text}</span>'
    )


def _warning_card(level: str, structure: str, warning: str) -> str:
    colors = {"critical": DANGER, "moderate": WARNING, "advisory": CYAN}
    icons  = {"critical": "🚨", "moderate": "⚠️", "advisory": "ℹ️"}
    c = colors.get(level, MUTED)
    ico = icons.get(level, "•")
    return (
        f'<div style="background:{SURFACE};border:1px solid {c}33;border-left:4px solid {c};'
        f'border-radius:8px;padding:0.9rem 1rem;margin-bottom:0.75rem;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05);">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">'
        f'<span>{ico}</span>'
        f'<span style="color:{c};font-weight:600;font-size:0.88rem;">{level.upper()}</span>'
        f'<span style="color:{MUTED};font-size:0.8rem;">— {structure}</span>'
        f'</div>'
        f'<p style="color:{TEXT};margin:0;font-size:0.88rem;line-height:1.55;">{warning}</p>'
        f'</div>'
    )


def _section_card(heading: str, content: str, important: bool = False) -> str:
    border = DANGER if important else CYAN
    prefix = "⚠️ " if important else ""
    return (
        f'<div style="background:{SURFACE};border:1px solid {border}22;border-left:4px solid {border};'
        f'border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.8rem;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05);">'
        f'<h4 style="color:{border};margin:0 0 0.45rem 0;font-size:0.92rem;">{prefix}{heading}</h4>'
        f'<p style="color:{TEXT};margin:0;line-height:1.62;font-size:0.88rem;">{content}</p>'
        f'</div>'
    )


# ── Session state initialisation ──────────────────────────────────────────────
for key, default in [
    ("specimen_result",     None),
    ("specimen_img_bytes",  None),
    ("specimen_annotated",  None),
    ("consent_result",      None),
    ("consent_usage",       {}),
    ("consent_procedure",   ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── App header ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div style="text-align:center;padding:1.75rem 0 1.5rem 0;
            border-bottom:1px solid {BORDER};margin-bottom:1.5rem;
            background:{SURFACE};border-radius:12px;
            box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:1.5rem;">
  <h1 style="color:{CYAN};font-size:1.85rem;font-weight:700;margin:0;letter-spacing:0.5px;">
    🧠 INAMS-ASRU NEURO-SURGICAL CO-PILOT
  </h1>
  <p style="color:{MUTED};font-size:0.78rem;margin:0.5rem 0 0 0;
            letter-spacing:2.5px;text-transform:uppercase;">
    BY THE PROFESSIONALS, FOR THE UPCOMING PROFESSIONALS
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# API key banner
if not os.getenv("ANTHROPIC_API_KEY"):
    st.markdown(
        f"""
<div style="background:{DANGER}0D;border:1px solid {DANGER}55;border-left:4px solid {DANGER};
            border-radius:8px;padding:0.9rem 1.1rem;margin-bottom:1.25rem;">
  <strong style="color:{DANGER};">⚠ API Key Not Found</strong>
  <p style="color:{TEXT};margin:0.3rem 0 0 0;font-size:0.88rem;">
    Set <code style="color:{CYAN};">ANTHROPIC_API_KEY</code> in your
    <code style="color:{CYAN};">.env</code> file and restart the app.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🔬 Specimen Analyser", "📋 Consent Generator"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — SPECIMEN ANALYSER
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1.65], gap="large")

    # ── Left panel ──────────────────────────────────────────────────────────────
    with col_left:
        # Upload card
        st.markdown(
            f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;'
            f'padding:1.2rem;margin-bottom:1rem;">'
            f'<p style="color:{CYAN};font-size:0.8rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:1px;margin:0 0 0.8rem 0;">📤 Upload Specimen</p>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload dissection photo",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Store image bytes whenever a new file is uploaded
        if uploaded_file is not None:
            st.session_state.specimen_img_bytes = uploaded_file.read()

        # Settings card
        st.markdown(
            f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;'
            f'padding:1.2rem;margin-bottom:1rem;">'
            f'<p style="color:{CYAN};font-size:0.8rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:1px;margin:0 0 0.8rem 0;">⚙ Analysis Settings</p>',
            unsafe_allow_html=True,
        )
        mode = st.radio("Specimen Mode", ["Porcine mode", "Human mode"], horizontal=True)
        show_overlays = st.checkbox("Show structure overlays", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

        run_btn = st.button("▶ RUN ANALYSIS", use_container_width=True)

        # Preview
        if st.session_state.specimen_img_bytes:
            st.markdown(
                f'<p style="color:{MUTED};font-size:0.78rem;margin:0.8rem 0 0.3rem 0;">Preview</p>',
                unsafe_allow_html=True,
            )
            st.image(st.session_state.specimen_img_bytes, use_container_width=True)

        # Trigger analysis
        if run_btn:
            if not st.session_state.specimen_img_bytes:
                st.error("Please upload a specimen image first.")
            else:
                with st.spinner("🔬 Analysing specimen with Vision AI…"):
                    result = analyse_image(st.session_state.specimen_img_bytes, mode)
                    st.session_state.specimen_result = result
                    if show_overlays and isinstance(result, dict) and "structures" in result:
                        st.session_state.specimen_annotated = draw_bboxes(
                            st.session_state.specimen_img_bytes, result["structures"]
                        )
                    else:
                        st.session_state.specimen_annotated = None
                if "error" not in (st.session_state.specimen_result or {}):
                    st.success("Analysis complete.")
                else:
                    st.error((st.session_state.specimen_result or {}).get("error", "Unknown error."))

    # ── Right panel ──────────────────────────────────────────────────────────────
    with col_right:
        if st.session_state.specimen_result is None:
            st.markdown(
                f'<div style="background:{SURFACE};border:1.5px dashed {BORDER};border-radius:12px;'
                f'padding:4rem 2rem;text-align:center;min-height:420px;">'
                f'<div style="font-size:3rem;margin-bottom:1rem;">🔬</div>'
                f'<h3 style="color:{MUTED};font-weight:500;margin:0 0 0.4rem 0;">Upload a specimen image</h3>'
                f'<p style="color:#94A3B8;font-size:0.84rem;margin:0;">'
                f'and click <strong style="color:{CYAN};">▶ RUN ANALYSIS</strong> to begin</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            result = st.session_state.specimen_result

            if "error" in result:
                st.error(result["error"])
            else:
                # Summary banner
                summary = result.get("summary", "")
                if summary:
                    st.markdown(
                        f'<div style="background:{CARD};border:1px solid {CYAN}33;'
                        f'border-left:4px solid {CYAN};border-radius:10px;'
                        f'padding:1rem 1.25rem;margin-bottom:1rem;">'
                        f'<p style="color:{TEXT};margin:0;font-size:0.88rem;line-height:1.6;">'
                        f'<span style="color:{CYAN};font-weight:600;">Summary — </span>{summary}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Annotated image
                if st.session_state.specimen_annotated:
                    st.image(
                        st.session_state.specimen_annotated,
                        caption="Annotated specimen — structure overlays",
                        use_container_width=True,
                    )

                # Result sub-tabs
                s1, s2, s3, s4 = st.tabs(
                    ["◈ Structures", "⇌ Bridge", "◆ Clinical Pearls", "⚠ Safety"]
                )

                # ── Structures ──────────────────────────────────────────────
                with s1:
                    structures = result.get("structures", [])
                    if not structures:
                        st.info("No structures identified.")
                    else:
                        for i, s in enumerate(structures):
                            color = BBOX_COLORS[i % len(BBOX_COLORS)]
                            conf  = max(0, min(100, int(s.get("confidence", 0))))
                            st.markdown(
                                f'<div style="background:{CARD};border:1px solid {color}33;'
                                f'border-left:4px solid {color};border-radius:8px;'
                                f'padding:0.85rem 1rem;margin-bottom:0.5rem;">'
                                f'<div style="display:flex;justify-content:space-between;'
                                f'align-items:center;margin-bottom:0.35rem;">'
                                f'<span style="color:{color};font-weight:600;font-size:0.9rem;">'
                                f'{s.get("name","Unknown")}</span>'
                                f'<span style="color:{MUTED};font-size:0.78rem;">{conf}% confidence</span>'
                                f'</div>'
                                f'<p style="color:{MUTED};font-size:0.82rem;margin:0 0 0.45rem 0;">'
                                f'{s.get("location","")}</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            st.progress(conf / 100)

                # ── Bridge ──────────────────────────────────────────────────
                with s2:
                    equivalents = result.get("human_equivalents", [])
                    if not equivalents:
                        st.info("No equivalency mappings available.")
                    else:
                        for eq in equivalents:
                            sim = eq.get("similarity", "")
                            sim_color = {"High": SUCCESS, "Moderate": WARNING, "Low": DANGER}.get(sim, MUTED)
                            st.markdown(
                                f'<div style="background:{CARD};border:1px solid {BORDER};'
                                f'border-radius:8px;padding:0.85rem 1rem;margin-bottom:0.65rem;">'
                                f'<div style="display:flex;align-items:center;gap:0.65rem;'
                                f'flex-wrap:wrap;margin-bottom:0.4rem;">'
                                f'<span style="color:{WARNING};font-weight:600;font-size:0.88rem;">'
                                f'🐷 {eq.get("porcine","")}</span>'
                                f'<span style="color:{MUTED};">→</span>'
                                f'<span style="color:{TEXT};font-weight:600;font-size:0.88rem;">'
                                f'🧠 {eq.get("human","")}</span>'
                                f'{_badge(sim, sim_color)}'
                                f'</div>'
                                f'<p style="color:{MUTED};font-size:0.82rem;margin:0;">'
                                f'{eq.get("clinical_note","")}</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                # ── Clinical Pearls ─────────────────────────────────────────
                with s3:
                    pearls = result.get("clinical_pearls", [])
                    if not pearls:
                        st.info("No clinical pearls generated.")
                    else:
                        for p in pearls:
                            cat   = p.get("category", "")
                            color = CATEGORY_COLORS.get(cat, MUTED)
                            icon  = {"Pathology": "🔴", "USMLE": "🔵",
                                     "Surgical": "🟡", "Imaging": "🟢"}.get(cat, "⚪")
                            st.markdown(
                                f'<div style="background:{color}0A;border:1px solid {color}33;'
                                f'border-left:4px solid {color};border-radius:8px;'
                                f'padding:0.85rem 1rem;margin-bottom:0.65rem;">'
                                f'<div style="margin-bottom:0.35rem;">'
                                f'{_badge(f"{icon} {cat}", color)}</div>'
                                f'<p style="color:{TEXT};margin:0;font-size:0.88rem;line-height:1.58;">'
                                f'{p.get("pearl","")}</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                # ── Safety ──────────────────────────────────────────────────
                with s4:
                    warnings = result.get("safety_warnings", [])
                    if not warnings:
                        st.info("No safety warnings identified.")
                    else:
                        for w in warnings:
                            st.markdown(
                                _warning_card(
                                    w.get("level", "advisory"),
                                    w.get("structure", ""),
                                    w.get("warning", ""),
                                ),
                                unsafe_allow_html=True,
                            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONSENT GENERATOR
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    _, col_main, _ = st.columns([0.08, 0.84, 0.08])

    with col_main:
        # ── Input card ────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="background:{CARD};border:1px solid {BORDER};'
            f'border-left:4px solid {CYAN};border-radius:12px;'
            f'padding:1.5rem;margin-bottom:1.25rem;">'
            f'<p style="color:{CYAN};font-size:0.8rem;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:1px;margin:0 0 1.1rem 0;">📝 Procedure Details</p>',
            unsafe_allow_html=True,
        )

        ALL_SECTIONS = [
            "What is this procedure?",
            "Why is it recommended?",
            "How is it performed?",
            "Risks and complications",
            "Benefits",
            "Alternatives",
            "What happens after?",
            "Questions to ask your doctor",
        ]

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            procedure = st.text_input(
                "Procedure / Surgery name",
                placeholder="e.g. Craniotomy, Lumbar Puncture, Vitrectomy",
                value=st.session_state.consent_procedure,
            )
            patient_profile = st.selectbox(
                "Patient profile",
                [
                    "Adult patient (general)",
                    "Elderly patient (simplified)",
                    "Paediatric guardian (parent-friendly)",
                    "Low health literacy",
                ],
            )
        with c2:
            complexity = st.selectbox(
                "Language complexity",
                [
                    "Simple (Class 8 reading level)",
                    "Moderate (undergraduate level)",
                    "Detailed (medical student level)",
                ],
            )
            sections = st.multiselect(
                "Include sections",
                options=ALL_SECTIONS,
                default=ALL_SECTIONS,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        gen_btn = st.button("📋 GENERATE CONSENT FORM", use_container_width=True)

        if gen_btn:
            if not procedure.strip():
                st.error("Please enter a procedure name.")
            elif not sections:
                st.error("Please select at least one section.")
            else:
                st.session_state.consent_procedure = procedure
                with st.spinner("✍ Generating consent form…"):
                    result, usage = generate_consent(procedure, patient_profile, complexity, sections)
                    st.session_state.consent_result = result
                    st.session_state.consent_usage  = usage
                if "error" not in result:
                    st.success("Consent form generated.")
                else:
                    st.error(result["error"])

        # ── Output section ────────────────────────────────────────────────────
        if st.session_state.consent_result is None:
            st.markdown(
                f'<div style="background:{SURFACE};border:1.5px dashed {BORDER};border-radius:12px;'
                f'padding:3.5rem 2rem;text-align:center;margin-top:1rem;">'
                f'<div style="font-size:3rem;margin-bottom:1rem;">📋</div>'
                f'<h3 style="color:{MUTED};font-weight:500;margin:0 0 0.4rem 0;">'
                f'Enter procedure details above</h3>'
                f'<p style="color:#94A3B8;font-size:0.84rem;margin:0;">'
                f'and click <strong style="color:{CYAN};">📋 GENERATE</strong> to create the form</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            result = st.session_state.consent_result

            if "error" in result:
                st.error(result["error"])
            else:
                title = result.get("procedure_title", "Consent Form")

                # Title card
                st.markdown(
                    f'<div style="background:{CARD};border:1px solid {CYAN}33;border-radius:12px;'
                    f'padding:1.25rem 1.5rem;margin:1rem 0 0.85rem 0;">'
                    f'<h2 style="color:{CYAN};margin:0;font-size:1.25rem;">{title}</h2>'
                    f'<p style="color:{MUTED};font-size:0.78rem;margin:0.3rem 0 0 0;">'
                    f'Patient Information & Consent Explanation</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Section cards
                for sec in result.get("sections", []):
                    st.markdown(
                        _section_card(sec.get("heading", ""), sec.get("content", ""), sec.get("important", False)),
                        unsafe_allow_html=True,
                    )

                # Key risks
                key_risks = result.get("key_risks", [])
                if key_risks:
                    risks_li = "".join(
                        f'<li style="color:{TEXT};margin-bottom:0.3rem;font-size:0.88rem;">{r}</li>'
                        for r in key_risks
                    )
                    st.markdown(
                        f'<div style="background:{DANGER}0A;border:1px solid {DANGER}33;'
                        f'border-left:4px solid {DANGER};border-radius:10px;'
                        f'padding:1rem 1.25rem;margin-bottom:0.8rem;">'
                        f'<h4 style="color:{DANGER};margin:0 0 0.5rem 0;font-size:0.92rem;">⚠️ Key Risks</h4>'
                        f'<ul style="margin:0;padding-left:1.2rem;">{risks_li}</ul>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Questions to ask
                questions = result.get("questions_to_ask", [])
                if questions:
                    q_li = "".join(
                        f'<li style="color:{TEXT};margin-bottom:0.3rem;font-size:0.88rem;">{q}</li>'
                        for q in questions
                    )
                    st.markdown(
                        f'<div style="background:{BLUE}0A;border:1px solid {BLUE}33;'
                        f'border-left:4px solid #4FC3F7;border-radius:10px;'
                        f'padding:1rem 1.25rem;margin-bottom:0.8rem;">'
                        f'<h4 style="color:#4FC3F7;margin:0 0 0.5rem 0;font-size:0.92rem;">'
                        f'💬 Questions to Ask Your Doctor</h4>'
                        f'<ul style="margin:0;padding-left:1.2rem;">{q_li}</ul>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Disclaimer
                disclaimer = result.get("disclaimer", "")
                if disclaimer:
                    st.markdown(
                        f'<div style="background:{SURFACE};border:1px solid {MUTED}22;'
                        f'border-radius:8px;padding:0.75rem 1rem;margin-bottom:1rem;">'
                        f'<p style="color:{MUTED};font-size:0.78rem;margin:0;font-style:italic;">'
                        f'{disclaimer}</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                # Build plain-text download content
                dl_lines = [f"CONSENT FORM — {title}", "=" * 60, ""]
                for sec in result.get("sections", []):
                    dl_lines += [f"## {sec.get('heading', '')}", sec.get("content", ""), ""]
                if key_risks:
                    dl_lines.append("## Key Risks")
                    dl_lines += [f"  • {r}" for r in key_risks]
                    dl_lines.append("")
                if questions:
                    dl_lines.append("## Questions to Ask Your Doctor")
                    dl_lines += [f"  • {q}" for q in questions]
                    dl_lines.append("")
                if disclaimer:
                    dl_lines += ["---", disclaimer]
                dl_txt = "\n".join(dl_lines)

                st.download_button(
                    label="⬇ Download Consent Form (.txt)",
                    data=dl_txt,
                    file_name="procedure_consent.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

                # Token usage
                usage = st.session_state.consent_usage
                if usage:
                    st.markdown(
                        f'<p style="color:{MUTED};font-size:0.73rem;text-align:right;margin-top:0.4rem;">'
                        f'⚡ Tokens — Input: {usage.get("input", 0):,} | Output: {usage.get("output", 0):,}'
                        f'</p>',
                        unsafe_allow_html=True,
                    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:1.5rem 0 0.5rem 0;margin-top:2rem;'
    f'border-top:1px solid {BORDER};">'
    f'<p style="color:{MUTED};font-size:0.78rem;margin:0;">'
    f'⚡ Powered by Claude AI &nbsp;·&nbsp; INAMS-ASRU Neuro-Surgical Co-Pilot'
    f'&nbsp;·&nbsp; <span style="color:#94A3B8;">For educational use only</span>'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True,
)
