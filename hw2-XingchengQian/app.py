"""
Customer Support Response Generator
Uses Google Gemini API to draft replies to customer messages.

Usage:
  Interactive mode:  python app.py
  Batch mode:        python app.py --batch
  Specify prompt:    python app.py --prompt-version v1  (v1, v2, v3)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; key can be set directly in environment

from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Prompt versions (mirrors prompts.md)
# ---------------------------------------------------------------------------

PROMPTS = {
    "v1": (
        "You are a customer support agent. "
        "Reply to the following customer message professionally."
    ),

    "v2": (
        "You are a customer support agent for an e-commerce company. "
        "Your job is to write a professional, empathetic, and helpful reply "
        "to the customer message below.\n\n"
        "Follow this structure:\n"
        "1. Greet the customer by name if available, otherwise use 'Hi there'\n"
        "2. Acknowledge their issue and express empathy\n"
        "3. Provide a clear next step or explanation\n"
        "4. Close with a polite sign-off and your name ('Support Team')\n\n"
        "Keep the tone warm but professional. Do not use overly casual language."
    ),

    "v3": (
        "You are a customer support agent for an e-commerce company. "
        "Your job is to write a professional, empathetic, and helpful reply "
        "to the customer message below.\n\n"
        "Follow this structure:\n"
        "1. Greet the customer by name if available, otherwise use 'Hi there'\n"
        "2. Acknowledge their issue and express genuine empathy\n"
        "3. Provide a clear next step or explanation\n"
        "4. Close with a polite sign-off: 'Best regards, Support Team'\n\n"
        "Tone guidelines:\n"
        "- Warm, professional, and calm — even if the customer is angry\n"
        "- Never match an angry customer's emotional intensity\n"
        "- Avoid overly formal or robotic language\n\n"
        "Hard constraints:\n"
        "- Do NOT promise specific refund amounts or exact delivery timelines "
        "you cannot guarantee\n"
        "- Do NOT make any admissions of liability or engage with legal claims\n"
        "- If the message involves a legal threat, compensation claim, or lawsuit, "
        "end your reply with this exact line: "
        "[ESCALATE TO HUMAN REVIEW — Legal/Compliance]\n"
        "- If the customer's message is too vague to address, ask up to three "
        "clarifying questions instead of guessing\n"
        "- Do not fabricate order details, product names, or policies"
    ),
}

DEFAULT_PROMPT_VERSION = "v3"
MODEL_NAME = "gemini-2.5-flash"


# ---------------------------------------------------------------------------
# Core API call
# ---------------------------------------------------------------------------

def generate_reply(customer_message: str, prompt_version: str = DEFAULT_PROMPT_VERSION) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "Error: GEMINI_API_KEY not found.\n"
            "Set it in a .env file or as an environment variable."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=customer_message,
        config=types.GenerateContentConfig(
            system_instruction=PROMPTS[prompt_version],
        ),
    )
    return response.text.strip()


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def save_output(content: str, filename: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def run_interactive(prompt_version: str) -> None:
    print(f"\n=== Customer Support Response Generator ===")
    print(f"Model : {MODEL_NAME}")
    print(f"Prompt: {prompt_version}")
    print("Type 'quit' or press Ctrl+C to exit.\n")

    session_lines = []

    while True:
        try:
            print("Paste the customer message (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "":
                    if lines:
                        break
                else:
                    lines.append(line)

            customer_message = "\n".join(lines).strip()
            if customer_message.lower() == "quit":
                break
            if not customer_message:
                continue

            print("\nGenerating reply...\n")
            reply = generate_reply(customer_message, prompt_version)

            print("--- DRAFT REPLY ---")
            print(reply)
            print("-------------------\n")

            block = (
                f"[{datetime.now().isoformat()}]\n"
                f"CUSTOMER:\n{customer_message}\n\n"
                f"REPLY ({prompt_version}):\n{reply}\n"
                f"{'=' * 60}\n"
            )
            session_lines.append(block)

        except KeyboardInterrupt:
            break

    if session_lines:
        filename = f"interactive_{timestamp()}.txt"
        path = save_output("\n".join(session_lines), filename)
        print(f"\nSession saved to {path}")


def run_batch(prompt_version: str) -> None:
    eval_path = Path("eval_set.json")
    if not eval_path.exists():
        sys.exit("Error: eval_set.json not found.")

    cases = json.loads(eval_path.read_text(encoding="utf-8"))

    print(f"\n=== Batch Evaluation ===")
    print(f"Model        : {MODEL_NAME}")
    print(f"Prompt       : {prompt_version}")
    print(f"Cases        : {len(cases)}")
    print(f"{'=' * 60}\n")

    report_lines = [
        f"Batch Evaluation Report",
        f"Model  : {MODEL_NAME}",
        f"Prompt : {prompt_version}",
        f"Run at : {datetime.now().isoformat()}",
        "=" * 60,
        "",
    ]

    for case in cases:
        case_id = case["id"]
        label = case["label"]
        case_type = case["type"]
        message = case["customer_message"]
        expected = case["expected_behavior"]

        print(f"[{case_id}] {label} ({case_type})")
        print(f"Customer: {message[:80]}{'...' if len(message) > 80 else ''}")

        reply = generate_reply(message, prompt_version)

        print(f"Reply preview: {reply[:120]}{'...' if len(reply) > 120 else ''}")
        print()

        block = "\n".join([
            f"Case {case_id}: {label}",
            f"Type    : {case_type}",
            f"",
            f"CUSTOMER MESSAGE:",
            message,
            f"",
            f"EXPECTED BEHAVIOR:",
            expected,
            f"",
            f"GENERATED REPLY ({prompt_version}):",
            reply,
            "-" * 60,
            "",
        ])
        report_lines.append(block)

    filename = f"batch_{prompt_version}_{timestamp()}.txt"
    path = save_output("\n".join(report_lines), filename)
    print(f"Full results saved to {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Customer Support Response Generator using Gemini"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run batch evaluation over eval_set.json",
    )
    parser.add_argument(
        "--prompt-version",
        choices=list(PROMPTS.keys()),
        default=DEFAULT_PROMPT_VERSION,
        help=f"Prompt version to use (default: {DEFAULT_PROMPT_VERSION})",
    )
    args = parser.parse_args()

    if args.batch:
        run_batch(args.prompt_version)
    else:
        run_interactive(args.prompt_version)


if __name__ == "__main__":
    main()
