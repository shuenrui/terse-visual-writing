# Terse Visual Writing

**Make AI replies skimmable in 3 seconds on a phone.**

A writing-structure skill + a linter that proves the structure happened.

## The point, in one example

**❌ Before — 123 words, no verdict**

> Great question! When it comes to choosing a scheduler for your Python pipeline, there are a few things to consider. It's worth noting that Apache Airflow is generally regarded as the industry standard, and it should be noted that it has a very large community, whereas Prefect is a more modern alternative...

**✅ After — same facts, 60% fewer words**

> **Pick Prefect. Don't pick Airflow for this.**
>
> - **Airflow** — 2,800 config keys, one cron daemon you now operate forever
> - **Prefect** — retries in Python, deploy in 20 minutes
> - **Dagster** — best asset model, worst learning curve
>
> **The exception:** if you already run Airflow for another team, add this to it.

Full set with failure modes: [before/after examples](references/before-after.md).

[SKILL.md](SKILL.md) is the agent-facing rulebook. This README is for humans.

## The problem

AI assistants answer in walls of prose. 200 words to say 10. No bullets, no spacing, no point.

The famous "write better" skills make this **worse**. We checked their rule files:

| Skill | Stars | What it does to your bullets |
|---|---|---|
| `avoid-ai-writing` | 3.2k | 🔴 Flags "bullet-heavy" as an AI tell → rewrites to prose |
| `humanizer` | 48.7k | 🔴 Rule 16: converts inline-header lists to prose |
| `stop-slop` | 17.2k | 🟡 Prose-focused, but cuts filler usefully |

They optimise for long-form *articles*. Applying them to chat strips out exactly the structure a human skimming a phone screen needs.

**This repo is the opposite.** Same anti-slop discipline, applied to *structure* instead of prose.

## Quick start

```bash
git clone https://github.com/shuenrui/terse-visual-writing.git

# Claude Code
cp -r terse-visual-writing ~/.claude/skills/

# Hermes
mkdir -p ~/.hermes/skills/communication
cp -r terse-visual-writing ~/.hermes/skills/communication/

# Any agent: paste the rules into your system prompt
cat SKILL.md
```

## The linter

Rules you can't argue with, because they're counted, not felt:

```bash
$ echo "Sure! Let me help. It's worth noting this is fairly large..." | python3 scripts/lint_style.py --stdin
❌ FAIL  score 0/100 (stdin)
    1 lines · 123 words · 0% structured · 1 wall-of-text
  🔴 [answer-first] line 1 is a preamble, not the answer
  🔴 [wall-of-text] 123-word prose block (max 45) — convert to bullets
  🔴 [filler] filler phrase: "it is worth noting"
  🟡 [quantify] adjective where a number belongs: fairly large
```

```bash
$ python3 scripts/lint_style.py --file good.md
✅ PASS  score 100/100 good.md
    9 lines · 74 words · 67% structured · 0 walls-of-text
```

**Zero dependencies, zero tokens.** Add it to CI, a git hook, or an agent's self-check loop.

### What it checks

| Rule | Fires when |
|---|---|
| `answer-first` | Line 1 is a preamble, not the answer |
| `wall-of-text` | Prose block >2 lines or >45 words |
| `list-length` | A list runs past 6 items |
| `reply-length` | Chat reply past 8 lines *and* under 45% structured |
| `filler` | "It's worth noting", "Basically", "Certainly!" |
| `plain-words` | ~30 complex words with a plain swap |
| `quantify` | Adjective where a number belongs |
| `hedging` | "Generally", "typically", "it depends" |
| `no-recap` | Last line summarises instead of acting |
| `scannable-labels` | Bullets without bold lead-ins |

### Flags

```
--file PATH    lint a file
--stdin        lint piped text
--json         machine-readable output (for agent self-checks)
--prose        document mode — skips the ≤8-line chat ceiling
```

Exit code: `0` pass, `1` violations, `2` usage error.

## What changed, mechanically

| Move | Effect |
|---|---|
| Verdict to line 1 | Reader can stop after one line and still be informed |
| Numbers inline with units | "6x slower" beats "a bit longer than anticipated" |
| Bold lead-ins | Eye finds anchors while skimming |
| Blank lines | Sections read as sections, not texture |
| Trailing action | Reply ends with what happens next |

## Where the rules came from

Ported and merged from three upstream projects, then hardened with a linter none of them had:

- [`daronthedragon/terse`](https://github.com/daronthedragon/terse) — answer-first procedure, honest benchmark design
- [`baoalvin1/terse`](https://github.com/baoalvin1/terse) — hard numeric budgets
- [`Vuk97/unslop`](https://github.com/Vuk97/unslop) — Google dev-docs word rules + lint-hook pattern

Plus a negative constraint learned the hard way: **what to reject from the popular writing skills, and why.** That's the `SKILL.md` conflict rule, and it's the part upstream projects get wrong.

## Honest limits

- The linter is regex. It flags banned words you cite *as examples* — which is why `references/before-after.md` scores 0: it deliberately contains the bad prose. Judge, don't obey.
- "45% structure ratio" is a tuned threshold, not a law. Tune it to your taste.
- Banned-phrase lists are English-only and English-centric.
- Star counts are as of Sep 2026. The three upstream brevity repos have ~2 stars each — I read their mechanics, not their popularity.

## License

MIT. Steal it freely.
