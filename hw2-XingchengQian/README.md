# HW2 — Customer Support Response Generator

**Course**: BU.330.760 Generative AI
**Author**: Xingcheng Qian

---

## Business Workflow

This prototype automates the first-draft generation of customer support replies for an e-commerce company.

| | |
|---|---|
| **Workflow** | Customer support response drafting |
| **User** | Customer service representatives |
| **Input** | Raw customer message (email or chat text) |
| **Output** | A professional, empathetic reply draft ready for human review |
| **Value** | Reduces time spent on repetitive inquiries, ensures consistent tone, and flags high-risk messages (legal threats) for immediate human escalation |

---

## Setup

### 1. Install dependencies

```bash
pip install google-genai python-dotenv
```

### 2. Set your Gemini API key

A `.env` file is required but is not included in this repository for security reasons.
A template is provided as `.env.example`. Copy it and fill in your key:

```bash
cp .env.example .env
# then open .env and replace the placeholder with your actual key
```

The `.env` file should contain:

```
GEMINI_API_KEY=your_key_here
```

You can get a free API key at [aistudio.google.com](https://aistudio.google.com) → Get API key.

### 3. Run the app

**Interactive mode** (type a customer message, get a reply):
```bash
python app.py
```

**Batch mode** (runs all 5 eval cases from eval_set.json):
```bash
python app.py --batch
```

**Choose a prompt version** (v1, v2, or v3):
```bash
python app.py --batch --prompt-version v1
python app.py --prompt-version v2
```

Results are saved to the `output/` folder automatically.

---

## Repository Structure

```
hw2-XingchengQian/
├── README.md         — this file
├── app.py            — main Python prototype
├── prompts.md        — three prompt versions with iteration notes
├── eval_set.json     — 5 evaluation test cases
├── report.md         — analysis and deployment recommendation
└── output/           — generated outputs (created at runtime)
```

---

## Video Walkthrough

[https://youtu.be/VU2R8ynKXgc]
