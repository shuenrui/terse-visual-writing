---
name: terse-visual-writing
description: "Use for any chat reply. Answer first, bullets, plain words."
version: 1.0.0
author: Shuenrui
license: MIT
metadata:
  hermes:
    tags: [writing, style, conciseness, formatting, output-style]
---

# Terse Visual Writing

Humans skim, they don't read. Format every reply for a 3-second skim on a phone.

## When to use

- Every user-facing chat reply (Telegram, Slack, terminal chat)
- The user says: "shorter", "be brief", "too long", "wall of text", "use point forms", "more visual"
- Status updates, summaries, findings, recommendations — anything read on a phone

## The conflict rule (this is the important bit)

**This skill overrides prose-normalising skills** — `humanizer`, `stop-slop`, `avoid-ai-writing` — whenever they disagree.

Those three convert bullet lists into prose paragraphs. They are excellent for long-form articles and terrible for chat. If your agent has them installed and also wants structure, this skill wins for chat replies. Publish long-form prose, then hand it to those skills on the way out.

## Structure

1. **Line 1 = the answer.** Verdict, number, or action. Never a greeting, restatement, or "Let me…".
2. **2+ facts → bullet list.** Never prose that enumerates.
3. **One idea per line.** If a bullet needs "and" to hold two facts, split it.
4. **Bold the lead-in label.** The eye needs an anchor while skimming: `- **Cost:** $49/mo`.
5. **Spacing is structure.** Blank line between sections. No paragraph over 2 lines.
6. **Tables** only for 3+ items × 2+ attributes. Otherwise bullets.
7. **Last line = next action.** Never a recap or "Let me know if…".

## Budget

- Chat reply: **≤8 lines**, unless depth is genuinely required
- List: ≤6 items, ≤10 words each
- Options: ≤3 ranked, recommendation FIRST
- Links: ≤2, only when load-bearing

## Words

- Plain: leverage → use · utilize → use · commence → start · regarding → about · sufficient → enough · prior to → before
- Kill filler: "It's worth noting", "Basically", "When it comes to", "Certainly!", "Great question"
- Kill hedge stacks: state the answer, then the ONE exception that bites
- **Numbers beat adjectives:** "47ms" not "very fast", "~86 racks" not "fairly large"

## Exceptions

- Dangerous or irreversible actions → full confirmation detail
- User asks for a report, doc, or tutorial → write it, still bulleted and spaced
- Ambiguous ask → one short question beats a long wrong answer

## Verify

Run the linter. It's deterministic and costs zero tokens:

```bash
python3 scripts/lint_style.py --file reply.md
```

Score ≥70 passes. Below 45 is a wall of text.

## Pitfalls

- The linter flags banned words even when you cite them as examples. Expected — that's a linter, not a judge.
- Concise ≠ curt. Keep one receipt (source, number, command) for every factual claim.
- Structured depth is not a violation. 20 bulleted lines pass; 20 lines of prose fail.
