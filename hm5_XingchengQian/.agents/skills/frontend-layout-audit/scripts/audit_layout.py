"""Audit rendered frontend layouts with Playwright.

This script opens a URL in real Chromium viewports, captures screenshots, and
reports deterministic layout risks that are hard to verify from code alone.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_VIEWPORTS = {
    "desktop": (1440, 900),
    "mobile": (390, 844),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a frontend URL in Chromium and audit common layout problems."
    )
    parser.add_argument("url", help="URL to audit, for example http://localhost:8000/broken.html")
    parser.add_argument(
        "--out-dir",
        default="artifacts/layout-audit",
        help="Directory for screenshots and reports. Defaults to artifacts/layout-audit.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=15000,
        help="Page navigation timeout in milliseconds. Defaults to 15000.",
    )
    parser.add_argument(
        "--viewport",
        action="append",
        default=[],
        metavar="NAME:WIDTHxHEIGHT",
        help="Additional or replacement viewport. Example: tablet:768x1024.",
    )
    return parser.parse_args()


def parse_viewports(values: list[str]) -> dict[str, tuple[int, int]]:
    if not values:
        return dict(DEFAULT_VIEWPORTS)

    parsed: dict[str, tuple[int, int]] = {}
    pattern = re.compile(r"^([a-zA-Z0-9_-]+):(\d{2,5})x(\d{2,5})$")
    for value in values:
        match = pattern.match(value)
        if not match:
            raise ValueError(f"Invalid viewport format: {value}. Use NAME:WIDTHxHEIGHT.")
        name, width, height = match.groups()
        parsed[name] = (int(width), int(height))
    return parsed


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-").lower() or "page"


def evaluate_layout_script() -> str:
    return r"""
(() => {
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  };

  const doc = document.documentElement;
  const body = document.body;
  const scrollWidth = Math.max(
    doc ? doc.scrollWidth : 0,
    body ? body.scrollWidth : 0
  );
  const scrollHeight = Math.max(
    doc ? doc.scrollHeight : 0,
    body ? body.scrollHeight : 0
  );

  function cssPath(el) {
    if (!el || !el.tagName) return "unknown";
    const tag = el.tagName.toLowerCase();
    if (el.id) return `${tag}#${el.id}`;
    const className = String(el.className || "")
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .join(".");
    if (className) return `${tag}.${className}`;
    const parent = el.parentElement;
    if (!parent) return tag;
    const index = Array.from(parent.children).indexOf(el) + 1;
    return `${tag}:nth-child(${index})`;
  }

  function rectFor(el) {
    const rect = el.getBoundingClientRect();
    return {
      x: Math.round(rect.x),
      y: Math.round(rect.y),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      right: Math.round(rect.right),
      bottom: Math.round(rect.bottom)
    };
  }

  function visible(el) {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 &&
      rect.height > 0 &&
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || "1") > 0.01;
  }

  function textSample(el) {
    return String(el.innerText || el.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 80);
  }

  const interactiveSelector = [
    "a",
    "button",
    "input",
    "select",
    "textarea",
    "[role='button']",
    "[onclick]",
    "[tabindex]"
  ].join(",");

  const interactive = Array.from(document.querySelectorAll(interactiveSelector))
    .filter(visible)
    .map((el) => ({
      selector: cssPath(el),
      tag: el.tagName.toLowerCase(),
      text: textSample(el),
      rect: rectFor(el)
    }));

  const offscreenControls = interactive.filter((item) =>
    item.rect.left < 0 ||
    item.rect.right > viewport.width ||
    item.rect.top < 0
  );

  const smallTouchTargets = interactive.filter((item) =>
    item.rect.width < 44 || item.rect.height < 44
  );

  const brokenImages = Array.from(document.images)
    .filter((img) => !img.complete || img.naturalWidth === 0 || img.naturalHeight === 0)
    .map((img) => ({
      selector: cssPath(img),
      src: img.currentSrc || img.src || "",
      rect: rectFor(img)
    }));

  const clippedText = Array.from(document.querySelectorAll("body *"))
    .filter((el) => {
      if (!visible(el)) return false;
      if (!textSample(el)) return false;
      const style = window.getComputedStyle(el);
      const clipsX = el.scrollWidth > el.clientWidth + 2 && style.overflowX !== "visible";
      const clipsY = el.scrollHeight > el.clientHeight + 2 && style.overflowY !== "visible";
      return clipsX || clipsY;
    })
    .slice(0, 20)
    .map((el) => ({
      selector: cssPath(el),
      text: textSample(el),
      rect: rectFor(el),
      scrollWidth: el.scrollWidth,
      clientWidth: el.clientWidth,
      scrollHeight: el.scrollHeight,
      clientHeight: el.clientHeight
    }));

  const interactiveNodes = Array.from(document.querySelectorAll(interactiveSelector))
    .filter(visible)
    .slice(0, 120);
  const overlaps = [];

  for (let i = 0; i < interactiveNodes.length; i += 1) {
    for (let j = i + 1; j < interactiveNodes.length; j += 1) {
      const a = interactiveNodes[i];
      const b = interactiveNodes[j];
      if (a.contains(b) || b.contains(a)) continue;
      const ar = a.getBoundingClientRect();
      const br = b.getBoundingClientRect();
      const x = Math.max(0, Math.min(ar.right, br.right) - Math.max(ar.left, br.left));
      const y = Math.max(0, Math.min(ar.bottom, br.bottom) - Math.max(ar.top, br.top));
      const overlapArea = x * y;
      if (overlapArea >= 64) {
        overlaps.push({
          first: { selector: cssPath(a), text: textSample(a), rect: rectFor(a) },
          second: { selector: cssPath(b), text: textSample(b), rect: rectFor(b) },
          overlapArea: Math.round(overlapArea)
        });
      }
      if (overlaps.length >= 20) break;
    }
    if (overlaps.length >= 20) break;
  }

  return {
    title: document.title || "",
    viewport,
    scrollWidth,
    scrollHeight,
    horizontalOverflow: scrollWidth > viewport.width + 2,
    horizontalOverflowPixels: Math.max(0, scrollWidth - viewport.width),
    interactiveCount: interactive.length,
    offscreenControls: offscreenControls.slice(0, 20),
    smallTouchTargets: smallTouchTargets.slice(0, 20),
    brokenImages,
    clippedText,
    overlaps
  };
})();
"""


def summarize_findings(result: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if result["horizontalOverflow"]:
        findings.append(
            f"Horizontal overflow: page is {result['horizontalOverflowPixels']} px wider than the viewport."
        )
    if result["brokenImages"]:
        findings.append(f"Broken images: {len(result['brokenImages'])} image(s) failed to load.")
    if result["offscreenControls"]:
        findings.append(
            f"Offscreen controls: {len(result['offscreenControls'])} visible interactive element(s) extend outside the viewport."
        )
    if result["smallTouchTargets"]:
        findings.append(
            f"Small touch targets: {len(result['smallTouchTargets'])} interactive element(s) are below 44 x 44 px."
        )
    if result["clippedText"]:
        findings.append(f"Clipped text/content: {len(result['clippedText'])} element(s) may be clipped.")
    if result["overlaps"]:
        findings.append(
            f"Possible overlaps: {len(result['overlaps'])} pair(s) of interactive elements overlap."
        )
    if not findings:
        findings.append("No obvious deterministic layout risks were detected.")
    return findings


def format_detail_list(items: list[dict[str, Any]], empty: str, limit: int = 5) -> str:
    if not items:
        return f"- {empty}\n"

    lines = []
    for item in items[:limit]:
        text = f" text={item.get('text')!r}" if item.get("text") else ""
        src = f" src={item.get('src')!r}" if item.get("src") else ""
        lines.append(f"- `{item.get('selector', 'unknown')}`{text}{src} rect={item.get('rect')}")
    if len(items) > limit:
        lines.append(f"- ... {len(items) - limit} more")
    return "\n".join(lines) + "\n"


def write_markdown_report(
    url: str,
    output_dir: Path,
    viewport_reports: dict[str, dict[str, Any]],
    screenshot_paths: dict[str, str],
) -> str:
    lines = [
        "# Frontend Layout Audit Report",
        "",
        f"URL: `{url}`",
        f"Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## Summary",
        "",
    ]

    for name, result in viewport_reports.items():
        width = result["viewport"]["width"]
        height = result["viewport"]["height"]
        lines.append(f"### {name} ({width} x {height})")
        lines.append("")
        lines.extend(f"- {finding}" for finding in summarize_findings(result))
        lines.append(f"- Screenshot: `{screenshot_paths[name]}`")
        lines.append("")

    lines.append("## Details")
    lines.append("")
    for name, result in viewport_reports.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("Offscreen controls:")
        lines.append(format_detail_list(result["offscreenControls"], "None detected.").rstrip())
        lines.append("")
        lines.append("Small touch targets:")
        lines.append(format_detail_list(result["smallTouchTargets"], "None detected.").rstrip())
        lines.append("")
        lines.append("Broken images:")
        lines.append(format_detail_list(result["brokenImages"], "None detected.").rstrip())
        lines.append("")
        lines.append("Clipped text/content:")
        lines.append(format_detail_list(result["clippedText"], "None detected.").rstrip())
        lines.append("")
        lines.append("Possible interactive overlaps:")
        if result["overlaps"]:
            for overlap in result["overlaps"][:5]:
                first = overlap["first"]
                second = overlap["second"]
                lines.append(
                    f"- `{first['selector']}` overlaps `{second['selector']}` "
                    f"by about {overlap['overlapArea']} px^2"
                )
            if len(result["overlaps"]) > 5:
                lines.append(f"- ... {len(result['overlaps']) - 5} more")
        else:
            lines.append("- None detected.")
        lines.append("")

    lines.append("## Recommended Review Order")
    lines.append("")
    lines.append("1. Fix horizontal overflow first because it usually breaks mobile layouts.")
    lines.append("2. Fix offscreen or overlapping controls next because they block user actions.")
    lines.append("3. Replace broken images and review clipped text.")
    lines.append("4. Manually inspect screenshots for visual polish and intentional design choices.")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append(
        "This script reports measurable rendering risks. It does not prove that a UI is beautiful, accessible, or production-ready."
    )

    report = "\n".join(lines) + "\n"
    report_path = output_dir / "layout-audit-report.md"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)


def run_audit(url: str, output_dir: Path, viewports: dict[str, tuple[int, int]], timeout_ms: int) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright is not installed. Run: python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_dir = output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    viewport_reports: dict[str, dict[str, Any]] = {}
    screenshot_paths: dict[str, str] = {}

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for name, (width, height) in viewports.items():
                    page = browser.new_page(viewport={"width": width, "height": height})
                    page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                    page.wait_for_timeout(500)
                    screenshot_path = screenshot_dir / f"{safe_slug(name)}-{width}x{height}.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    result = page.evaluate(evaluate_layout_script())
                    viewport_reports[name] = result
                    screenshot_paths[name] = str(screenshot_path)
                    page.close()
            finally:
                browser.close()
    except Exception as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        print(
            "If Chromium is missing, run: python -m playwright install chromium",
            file=sys.stderr,
        )
        return 1

    json_path = output_dir / "layout-audit-report.json"
    json_path.write_text(
        json.dumps(
            {
                "url": url,
                "generatedAt": datetime.now().isoformat(timespec="seconds"),
                "screenshots": screenshot_paths,
                "viewports": viewport_reports,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    markdown_path = write_markdown_report(url, output_dir, viewport_reports, screenshot_paths)

    print(f"Audit complete for {url}")
    print(f"Markdown report: {markdown_path}")
    print(f"JSON report: {json_path}")
    print("")
    for name, result in viewport_reports.items():
        width = result["viewport"]["width"]
        height = result["viewport"]["height"]
        print(f"[{name} {width}x{height}]")
        for finding in summarize_findings(result):
            print(f"- {finding}")
        print(f"- Screenshot: {screenshot_paths[name]}")
        print("")

    return 0


def main() -> int:
    args = parse_args()
    try:
        viewports = parse_viewports(args.viewport)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return run_audit(
        url=args.url,
        output_dir=Path(args.out_dir),
        viewports=viewports,
        timeout_ms=args.timeout_ms,
    )


if __name__ == "__main__":
    raise SystemExit(main())
