# Homework 5: Frontend Layout Audit Skill

Video link: TODO - replace this line with the Zoom, YouTube, or Vimeo walkthrough link before submitting to Canvas.

## What This Skill Does

`frontend-layout-audit` helps an AI coding assistant verify frontend UI changes by opening a page in a real browser instead of guessing from code. It captures desktop and mobile screenshots and reports common measurable layout problems:

- Horizontal overflow
- Offscreen buttons or controls
- Broken images
- Clipped text or content
- Small touch targets
- Possible overlapping interactive elements

## Why I Chose This Skill

As a frontend engineer, I often use AI to generate or modify UI code. A recurring problem is that the AI may produce code that looks reasonable in text but renders badly in the browser, such as misplaced buttons, distorted content, or broken mobile layouts. This skill gives the agent a repeatable way to inspect the rendered page and use browser evidence before giving final feedback.

The Python script is load-bearing because the model cannot reliably know actual layout geometry from source code alone. Browser rendering, screenshots, DOM bounding boxes, image load state, and viewport overflow must be measured by code.

## Project Structure

```text
hm5_XingchengQian/
|-- .agents/
|   `-- skills/
|       `-- frontend-layout-audit/
|           |-- SKILL.md
|           `-- scripts/
|               `-- audit_layout.py
|-- demo-site/
|   |-- good.html
|   `-- broken.html
|-- artifacts/
|   `-- layout-audit/
|-- AGENT_DEMO.md
|-- requirements.txt
`-- README.md
```

## How To Use

Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Start the demo site from the project root:

```bash
python -m http.server 8000 --directory demo-site
```

Run the audit script:

```bash
python .agents/skills/frontend-layout-audit/scripts/audit_layout.py http://localhost:8000/broken.html
```

The script writes screenshots and reports to:

```text
artifacts/layout-audit/
```

## Agent Usage Demo

The intended agent flow is documented in `AGENT_DEMO.md`.

The important behavior is:

1. The user asks the coding agent to inspect a rendered frontend page.
2. The agent discovers `frontend-layout-audit` from the skill name and description.
3. The agent loads `SKILL.md` and follows the workflow.
4. The agent runs the bundled Python script instead of guessing from source code.
5. The agent summarizes the script output and links the generated screenshots.

Example command run by the agent:

```bash
python .agents/skills/frontend-layout-audit/scripts/audit_layout.py http://localhost:8000/broken.html --out-dir artifacts/layout-audit/broken
```

## What The Script Does

`audit_layout.py` uses Playwright to open the target URL in Chromium. By default, it checks:

- Desktop viewport: `1440 x 900`
- Mobile viewport: `390 x 844`

For each viewport, it:

1. Opens the page.
2. Waits for the page to load.
3. Captures a full-page screenshot.
4. Measures document width against viewport width.
5. Finds interactive elements outside the viewport.
6. Finds broken images.
7. Finds small interactive targets below `44 x 44` pixels.
8. Finds clipped text or content.
9. Finds possible overlaps between interactive elements.
10. Writes Markdown and JSON reports.

## Test Prompts

### Normal Case

Prompt:

```text
Use frontend-layout-audit to inspect http://localhost:8000/good.html.
```

Expected result:

```text
The agent should activate the skill, run the script, capture desktop and mobile screenshots, and report that no obvious deterministic layout risks were detected.
```

Actual verification result:

```text
[desktop 1440x900]
- No obvious deterministic layout risks were detected.
- Screenshot: artifacts/layout-audit/good/screenshots/desktop-1440x900.png

[mobile 390x844]
- No obvious deterministic layout risks were detected.
- Screenshot: artifacts/layout-audit/good/screenshots/mobile-390x844.png
```

### Edge Case

Prompt:

```text
Use frontend-layout-audit to inspect http://localhost:8000/broken.html on desktop and mobile.
```

Expected result:

```text
The agent should run the script and report measurable problems such as horizontal overflow, a broken image, an offscreen button, a small touch target, clipped content, and overlapping buttons.
```

Actual verification result:

```text
[desktop 1440x900]
- Horizontal overflow: page is 384 px wider than the viewport.
- Broken images: 1 image(s) failed to load.
- Small touch targets: 1 interactive element(s) are below 44 x 44 px.
- Clipped text/content: 1 element(s) may be clipped.
- Possible overlaps: 1 pair(s) of interactive elements overlap.

[mobile 390x844]
- Horizontal overflow: page is 1434 px wider than the viewport.
- Broken images: 1 image(s) failed to load.
- Offscreen controls: 1 visible interactive element(s) extend outside the viewport.
- Small touch targets: 1 interactive element(s) are below 44 x 44 px.
- Clipped text/content: 1 element(s) may be clipped.
- Possible overlaps: 1 pair(s) of interactive elements overlap.
```

### Cautious / Limited Case

Prompt:

```text
Can frontend-layout-audit prove that this UI is beautiful and production-ready?
```

Expected result:

```text
The agent should be cautious. It should explain that the skill can detect measurable rendering risks and provide screenshots, but it cannot prove subjective visual quality, accessibility, or production readiness.
```

Actual verification result:

```text
The skill instructions explicitly limit the agent to measurable rendering risks. The agent should refuse to claim that the UI is objectively beautiful or production-ready based only on this audit.
```

## Generated Verification Artifacts

After local verification, the script generated:

```text
artifacts/layout-audit/good/layout-audit-report.md
artifacts/layout-audit/good/layout-audit-report.json
artifacts/layout-audit/good/screenshots/desktop-1440x900.png
artifacts/layout-audit/good/screenshots/mobile-390x844.png
artifacts/layout-audit/broken/layout-audit-report.md
artifacts/layout-audit/broken/layout-audit-report.json
artifacts/layout-audit/broken/screenshots/desktop-1440x900.png
artifacts/layout-audit/broken/screenshots/mobile-390x844.png
```

## What Worked Well

This skill creates a practical feedback loop for frontend AI coding. The model can still explain and prioritize fixes, but the script supplies evidence from a real browser. That makes the workflow more reliable than reading CSS and guessing.

## Assignment Requirement Checklist

- Narrow reusable skill: `frontend-layout-audit` focuses only on rendered frontend layout auditing.
- Proper skill structure: `.agents/skills/frontend-layout-audit/SKILL.md`.
- Clear activation metadata: `SKILL.md` contains matching `name` and a detailed `description`.
- Load-bearing script: `scripts/audit_layout.py` opens Chromium, captures screenshots, measures DOM geometry, and writes reports.
- Progressive disclosure: the description is short enough for discovery, while detailed workflow instructions live in the body of `SKILL.md`.
- Three test prompts: normal, edge, and cautious cases are listed above.
- README: explains purpose, motivation, usage, script behavior, results, and limitations.
- Demo assets: `good.html` and `broken.html` provide stable pages for the walkthrough.
- Video requirement: add the final walkthrough link at the top of this README before Canvas submission.

## Limitations

- The audit uses heuristics and may report false positives for intentional overlays, sticky headers, menus, or animations.
- It checks the initial loaded state only.
- It does not perform full accessibility testing.
- It does not judge visual taste or brand quality.
- It requires a URL that Chromium can open.

## Submission Notes

Submit the GitHub repository link in Canvas. Before submitting, replace the TODO video line at the top of this README with the final 45-90 second walkthrough video link.
