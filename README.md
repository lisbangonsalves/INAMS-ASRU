# 🧠 INAMS-ASRU Neuro-Surgical Co-Pilot

> **BY THE PROFESSIONALS, FOR THE UPCOMING PROFESSIONALS**

An AI-powered web application built for MBBS students at the INAMS-ASRU medical workshop. Combines two tools — a Vision AI specimen analyser and a consent form generator — into one clean, dark-mode interface.

---

## Features

| Tool | AI Model | What it does |
|---|---|---|
| 🔬 Specimen Analyser | `claude-opus-4-6` (Vision) | Identifies anatomical structures in porcine/human brain dissection photos, maps them to human equivalents, generates clinical pearls and safety warnings |
| 📋 Consent Generator | `claude-sonnet-4-6` (Text) | Produces patient-friendly consent form explanations tailored to profile and reading level |

---

## Prerequisites

- Python 3.10 or higher
- An [Anthropic API key](https://console.anthropic.com)

---

## Setup

### 1. Clone / navigate to the project folder
```bash
cd inams-copilot
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Edit `.env` and replace the placeholder:
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

### 5. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

### Tab 1 — Specimen Analyser
1. Upload a JPG/PNG/WEBP dissection photograph
2. Select **Porcine mode** or **Human mode**
3. Toggle **Show structure overlays** if you want bounding boxes drawn on the image
4. Click **▶ RUN ANALYSIS**
5. Browse results across four sub-tabs:
   - **◈ Structures** — identified structures with confidence bars
   - **⇌ Bridge** — porcine → human equivalency table
   - **◆ Clinical Pearls** — colour-coded pearls by category
   - **⚠ Safety** — critical / moderate / advisory warnings

### Tab 2 — Consent Generator
1. Enter the procedure name (e.g. *Craniotomy*, *Lumbar Puncture*)
2. Choose patient profile and language complexity
3. Select which sections to include
4. Click **📋 GENERATE CONSENT FORM**
5. Review the output and download it as a `.txt` file

---

## Project structure

```
inams-copilot/
├── app.py           # Full Streamlit application
├── .env             # API key (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Important notes

- All results are AI-generated and intended for **educational purposes only**.
- Consent forms must be reviewed by a qualified doctor before clinical use.
- Never commit `.env` or hard-code your API key anywhere in the source.
