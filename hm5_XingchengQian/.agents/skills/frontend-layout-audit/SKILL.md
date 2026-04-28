---
name: frontend-layout-audit
description: Opens a local or remote frontend page in a real browser, captures desktop and mobile screenshots, and detects common layout problems such as horizontal overflow, offscreen controls, failed images, clipped content, small touch targets, and overlapping interactive elements. Use after HTML, CSS, React, Vue, or other frontend UI changes when the user wants to verify how the page actually renders instead of guessing from code.
---

# Frontend Layout Audit

Use this skill when the user wants a browser-based check of a frontend page after UI code changes. The goal is to help the agent see what the page actually renders like, not infer layout quality from source code alone.

## When to Use

- The user asks whether a page has obvious layout problems.
- The user reports buttons being misplaced, text looking distorted, or content overflowing.
- The user has changed HTML, CSS, React, Vue, or another frontend implementation and wants a real rendering check.
- The user provides a local or remote URL that can be opened in a browser.

## When Not to Use

- Do not use this skill for backend-only API testing.
- Do not claim that this skill proves the UI is beautiful, accessible, or production-ready.
- Do not use this skill when no runnable URL or static HTML file is available.
- Do not treat script findings as a replacement for human visual review.

## Expected Inputs

- A URL, such as `http://localhost:3000`, `http://localhost:8000/broken.html`, or a remote URL.
- Optional viewport needs if the user asks for a specific device size.

## Workflow

1. Confirm that the page has a runnable URL. If not, ask the user to start the frontend dev server or provide a static file URL.
2. Run the bundled Python script from the project root:

   ```bash
   python .agents/skills/frontend-layout-audit/scripts/audit_layout.py <url>
   ```

3. If Playwright or Chromium is missing, install dependencies as described by the script error and try again.
4. Read the generated report and screenshot paths.
5. Summarize the most important findings first, especially horizontal overflow, failed images, offscreen controls, clipped content, small touch targets, and overlapping interactive elements.
6. Mention the screenshots so the user can visually inspect the rendered page.
7. Be explicit about limits: this audit detects measurable layout risks but does not prove subjective visual quality.

## Expected Output

Return a concise report with:

- URL checked
- Viewports checked
- Screenshot paths
- High-priority layout issues
- Lower-priority warnings
- Suggested next fixes
- Any limitations or uncertainty

## Important Limitations

- The script uses heuristics. It can produce false positives for intentional overlays, menus, sticky headers, or animations.
- It does not replace manual design review.
- It only checks the page state after initial load unless the user asks for a more specific interaction flow.
- It can only audit pages that the local browser can reach.
