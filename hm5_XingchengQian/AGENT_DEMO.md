# Agent Demo Transcript

This file documents the expected coding-agent demonstration for the `frontend-layout-audit` skill.

## Setup

From the project root:

```bash
python -m http.server 8000 --directory demo-site
```

## Normal Case

User prompt:

```text
Use frontend-layout-audit to inspect http://localhost:8000/good.html.
```

Agent behavior:

```text
The request matches the frontend-layout-audit skill because the user wants to inspect how a frontend page actually renders. I will run the bundled audit script instead of judging the layout from code alone.
```

Command:

```bash
python .agents/skills/frontend-layout-audit/scripts/audit_layout.py http://localhost:8000/good.html --out-dir artifacts/layout-audit/good
```

Result summary:

```text
Desktop 1440x900: no obvious deterministic layout risks detected.
Mobile 390x844: no obvious deterministic layout risks detected.
Screenshots were written to artifacts/layout-audit/good/screenshots/.
```

## Edge Case

User prompt:

```text
Use frontend-layout-audit to inspect http://localhost:8000/broken.html on desktop and mobile.
```

Agent behavior:

```text
The request asks for rendered frontend validation, so I will activate frontend-layout-audit, open the page in Chromium, capture screenshots, and report measurable layout risks.
```

Command:

```bash
python .agents/skills/frontend-layout-audit/scripts/audit_layout.py http://localhost:8000/broken.html --out-dir artifacts/layout-audit/broken
```

Result summary:

```text
Desktop found horizontal overflow, one broken image, one small touch target, clipped content, and one possible interactive overlap.
Mobile found horizontal overflow, one broken image, one offscreen control, one small touch target, clipped content, and one possible interactive overlap.
Screenshots were written to artifacts/layout-audit/broken/screenshots/.
```

## Cautious Case

User prompt:

```text
Can frontend-layout-audit prove that this UI is beautiful and production-ready?
```

Agent behavior:

```text
The skill should be limited here. It can report measurable rendering risks and provide screenshots, but it cannot prove subjective visual quality, full accessibility, or production readiness.
```

Appropriate final answer:

```text
No. frontend-layout-audit can detect measurable layout risks such as overflow, offscreen controls, failed images, clipping, and overlap. It can also produce screenshots for human review. It cannot prove that the UI is beautiful, accessible, or production-ready.
```

## Video Recording Checklist

Show these items in the 45-90 second walkthrough:

1. Folder structure under `.agents/skills/frontend-layout-audit/`.
2. `SKILL.md` name and description.
3. `scripts/audit_layout.py`.
4. The local demo site running.
5. The agent prompt that activates the skill.
6. The script command being run.
7. The generated report and screenshots.
8. A short explanation that browser rendering evidence is needed because source code alone cannot reliably reveal layout problems.
