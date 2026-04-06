# Report — Customer Support Response Generator

**Course**: BU.330.760 Generative AI
**Author**: Xingcheng Qian

---

## Business Use Case

This prototype addresses a common bottleneck in e-commerce operations: customer service representatives spend significant time drafting replies to repetitive inquiries such as order status questions, refund requests, and complaints. The system uses a large language model to generate a professional first-draft reply given a raw customer message. The human agent then reviews, adjusts if needed, and sends the reply. The goal is to reduce drafting time while maintaining quality and flagging high-risk messages for human escalation.

---

## Model Choice

**Model used**: `gemini-2.5-flash` via Google AI Studio API.

Gemini 2.5 Flash was chosen because it is freely accessible, fast, and produces high-quality short-form text suitable for customer correspondence. For a task like this — structured, tone-sensitive, short-output — a capable but efficient model is sufficient. During setup, `gemini-2.0-flash` and `gemini-2.0-flash-lite` were also attempted but were unavailable for new users; `gemini-2.5-flash` proved to be the most accessible current option with strong output quality.

---

## Baseline vs. Final Design

### Prompt v1 (Baseline)

> *"You are a customer support agent. Reply to the following customer message professionally."*

**Observed problems (from actual batch output):**
- Inconsistent sign-offs: some replies ended with `[Your Name/Customer Support Team]` — an unfilled placeholder left visible to the customer
- Over-promised on timelines: Case 1 committed to *"within the next 24 hours"* with no basis for that guarantee
- Legal case (Case 5): extensively engaged with legal specifics, acknowledged the customer's 48-hour deadline (*"We acknowledge your 48-hour timeframe"*), and requested detailed incident reports — all legally risky behaviors with no escalation flag
- Case 4 (vague): handled reasonably well, asking clarifying questions without fabricating details

### Prompt v2 (Revision 1)

Added persona, 4-part structure, and tone guidance.

**Observed improvements and new problems:**
- Consistent greeting ("Hi there") and sign-off ("Support Team") appeared in all replies
- Empathy improved notably on the angry customer case
- New problem: Case 1 fabricated an order lookup — *"I've looked up your order, and I can confirm it is currently being prepared for shipment"* — the model has no access to any order system
- Case 2 over-committed: *"we will promptly review your case and arrange your full refund"* — promising a full refund without seeing photos or verifying the claim
- Legal case (Case 5): still no escalation flag, still engaged with legal details

### Prompt v3 (Final)

Added hard constraints: no specific promises, no legal engagement, mandatory escalation flag, clarifying questions for vague inputs.

**Observed improvements:**
- All replies follow a consistent 4-part structure (greeting → empathy → next step → sign-off)
- Refund reply (Case 2) requested photos before any commitment, no refund amount or timeline promised
- Legal case (Case 5) correctly ends with `[ESCALATE TO HUMAN REVIEW — Legal/Compliance]`
- Vague message (Case 4) responded with three targeted clarifying questions

**Example comparison — Case 5 (Legal Threat):**

| | v1 Output | v2 Output | v3 Output |
|---|---|---|---|
| Liability engagement | Acknowledged 48-hr deadline, requested incident report | Engaged with claim details, asked for documentation | Acknowledged concern only, no engagement with legal specifics |
| Escalation flag | None | None | `[ESCALATE TO HUMAN REVIEW — Legal/Compliance]` |
| Risk level | High | High | Low |

---

## Where the Prototype Still Fails

Even with the final prompt, the system has clear limitations:

1. **Policy hallucination**: The model occasionally references a "30-day return policy" or "free replacement" that was never provided. It has no access to actual company policies.
2. **Nuanced emotional cases**: Extremely hostile messages sometimes receive replies that are technically correct but feel hollow or scripted.
3. **Multi-turn context**: The system handles only single-message inputs. It cannot read prior conversation history, which limits usefulness for ongoing threads.
4. **Legal boundary**: While the escalation flag helps, the model's pre-flag text may still contain language a lawyer would object to.

---

## Deployment Recommendation

**Conditional yes** — with mandatory human review before sending.

This prototype is suitable as a **drafting assistant**, not an autonomous responder. It meaningfully reduces the time a representative spends on routine cases (estimated 40–60% reduction in drafting time for standard inquiries). However, it should not send replies without a human checking the output, particularly for:

- Any message involving refunds, returns, or compensation
- Legal threats or formal complaints
- Emotionally escalated customers
- Any case where the model flags `[ESCALATE TO HUMAN REVIEW]`

A deployment with these guardrails in place is reasonable. Full automation without human review is not recommended at this stage.
