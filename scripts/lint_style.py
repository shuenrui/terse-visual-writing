#!/usr/bin/env python3
"""
lint_style.py — machine-check a reply for visual-skimmability.

Answers one question: can a human get the point in 3 seconds on a phone?

Usage:
    python3 lint_style.py --file reply.md
    echo "your reply" | python3 lint_style.py --stdin
    python3 lint_style.py --file reply.md --json

Exit code: 0 = pass, 1 = violations found, 2 = usage error.

Rules are deliberately hard-coded and countable. No model in the loop,
so it cannot be argued with, and it costs zero tokens to run.
"""

import argparse
import json
import re
import sys

# ---------------------------------------------------------------- rules

BANNED_OPENERS = [
    "sure", "certainly", "of course", "great question", "good question",
    "happy to help", "let me", "i'll help", "here's", "here is",
    "so,", "well,", "okay,", "ok,", "thanks for", "thank you for",
    "i understand", "that's a", "to answer your question",
    "regarding your", "as requested", "absolutely",
]

BANNED_CLOSERS = [
    "in summary", "to summarize", "in conclusion", "i hope this helps",
    "let me know", "feel free to", "don't hesitate", "hope that helps",
    "to recap", "overall,", "all in all", "in essence",
]

FILLER = [
    "it's worth noting", "it is worth noting", "needless to say",
    "as a matter of fact", "at the end of the day", "in today's world",
    "it should be noted", "interestingly", "actually,", "basically",
    "genuinely", "very much", "really quite", "when it comes to",
    "the fact that", "in terms of", "a few things", "some considerations",
]

COMPLEX_WORDS = {
    "leverage": "use", "utilise": "use", "utilize": "use",
    "commence": "start", "terminate": "end/stop", "regarding": "about",
    "sufficient": "enough", "prior to": "before", "subsequent": "later",
    "facilitate": "help", "endeavor": "try", "ascertain": "find out",
    "methodology": "method", "individual": "person", "remuneration": "pay",
    "additionally": "also", "furthermore": "also", "moreover": "also",
    "nevertheless": "but", "notwithstanding": "despite", "consequently": "so",
    "therefore": "so", "auxiliary": "extra", "optimize": "improve",
    "robust": "strong", "comprehensive": "full", "innovative": "new",
    "cutting-edge": "new", "state-of-the-art": "best", "paradigm": "model",
    "synergy": "teamwork", "holistic": "whole", "scalable": "grows",
    "streamline": "simplify", "touchpoint": "point of contact",
}

HEDGE_STACK = ["generally", "typically", "usually", "in most cases",
               "it depends", "broadly speaking", "arguably", "perhaps"]

EMPHATIC_ADVERBS = ["extremely", "incredibly", "highly", "tremendously",
                    "remarkably", "exceptionally", "significantly"]

# thresholds (ceilings, not targets)
MAX_PARA_LINES = 2
MAX_PARA_WORDS = 45      # catches prose that arrives unwrapped on one line
MAX_LIST_ITEMS = 6
MAX_CHAT_LINES = 8

# ---------------------------------------------------------------- helpers

def is_list(line):
    return bool(re.match(r"^\s*([-*•]|\d+[.)])\s+", line))

def is_heading(line):
    return bool(re.match(r"^\s*#{1,6}\s+", line))

def is_table(line):
    return line.strip().startswith("|")

def is_code_delim(line):
    return line.strip().startswith("```")

# ---------------------------------------------------------------- core

def lint(text, chat_mode=True):
    """Return (score_0_100, findings, stats)."""
    findings = []
    # strip blockquote markers once, so "> - bullet" counts as a bullet
    # everywhere (rules, ratios, and word-level scans all see `lines`)
    lines = [re.sub(r"^\s*>\s?", "", l) for l in text.splitlines()]
    content = [l for l in lines if l.strip()]

    if not content:
        return 100, [], {"lines": 0}

    def add(rule, severity, detail, evidence=""):
        findings.append({"rule": rule, "severity": severity,
                         "detail": detail, "evidence": evidence[:90]})

    # --- R1: answer on line 1
    first = content[0].strip().lower().strip("*_`")
    for op in BANNED_OPENERS:
        if first.startswith(op):
            add("answer-first", "high",
                "line 1 is a preamble, not the answer", content[0])
            break

    # --- R2: no closing recap
    last = content[-1].strip().lower().strip("*_`")
    for cl in BANNED_CLOSERS:
        if last.startswith(cl):
            add("no-recap", "medium",
                "last line is a summary/farewell, not an action", content[-1])
            break

    # --- walk blocks, respecting fences
    in_code = False
    para = []
    para_start = 0
    list_run = []
    list_start = 0
    stats = {"paras": 0, "lists": 0, "bullet_lines": 0, "long_paras": 0}

    def flush_para(idx):
        # unwrapped prose: judge by word count, not source line count
        block = " ".join(para)
        words = len(block.split())
        hit = None
        if len(para) > MAX_PARA_LINES:
            hit = f"{len(para)}-line prose paragraph (max {MAX_PARA_LINES})"
        elif words > MAX_PARA_WORDS:
            hit = f"{words}-word prose block (max {MAX_PARA_WORDS})"
        if hit:
            add("wall-of-text", "high",
                hit + " — convert to bullets", block[:90])
            stats["long_paras"] += 1
        stats["paras"] += 1
        para.clear()

    def flush_list(idx):
        if len(list_run) > MAX_LIST_ITEMS:
            add("list-length", "medium",
                f"{len(list_run)} items in one list (max {MAX_LIST_ITEMS})"
                " — group or cut",
                list_run[0])
        stats["lists"] += 1
        list_run.clear()

    for i, raw in enumerate(lines):
        if is_code_delim(raw):
            in_code = not in_code
            if para:
                flush_para(i)
            if list_run:
                flush_list(i)
            continue
        if in_code:
            continue
        if not raw.strip():
            if para:
                flush_para(i)
            if list_run:
                flush_list(i)
            continue
        if is_heading(raw):
            if para:
                flush_para(i)
            if list_run:
                flush_list(i)
            continue
        if is_table(raw):
            if para:
                flush_para(i)
            continue
        if is_list(raw):
            if para:
                flush_para(i)
            stats["bullet_lines"] += 1
            list_run.append(raw.strip())
            continue
        if list_run:
            flush_list(i)
        para.append(raw.strip())

    if para:
        flush_para(len(lines))
    if list_run:
        flush_list(len(lines))

    # --- R3: chat length
    if chat_mode and len(content) > MAX_CHAT_LINES:
        # depth is allowed if it's structured
        structured = (stats["bullet_lines"] + sum(1 for l in content
                        if is_heading(l) or is_table(l))) / len(content)
        if structured < 0.45:
            add("reply-length", "medium",
                f"{len(content)} content lines with only "
                f"{structured:.0%} structure — trim or bullet",
                "")
        else:
            add("reply-length", "info",
                f"{len(content)} lines but {structured:.0%} structured"
                " — acceptable for depth", "")

    # --- R4: word-level (whole text, case-insensitive)
    low = text.lower()
    for w in FILLER:
        if w in low:
            add("filler", "high", f"filler phrase: “{w}”", w)
    for w, repl in COMPLEX_WORDS.items():
        if re.search(rf"\b{re.escape(w)}\b", low):
            add("plain-words", "medium", f"“{w}” → “{repl}”", w)
    for h in HEDGE_STACK:
        if re.search(rf"\b{re.escape(h)}\b", low):
            add("hedging", "low", f"hedge: “{h}” — state the answer + the one exception", h)
    for a in EMPHATIC_ADVERBS:
        if re.search(rf"\b{re.escape(a)}\b", low):
            add("emphasis-adverb", "low", f"cut “{a}”", a)

    # --- R5: one idea per line
    long_bullets = [l.strip() for l in content
                    if is_list(l) and len(l.strip().split()) > 14
                    and " · " not in l and " — " not in l]
    if len(long_bullets) > 2:
        add("one-idea", "low",
            f"{len(long_bullets)} bullets carry 15+ words — split or shorten",
            long_bullets[0])

    # --- R6: numbers over adjectives
    vague = re.findall(r"\b(very fast|quite good|fairly large|pretty quick|"
                       r"significantly faster|much better|a lot of|"
                       r"relatively cheap|somewhat expensive)\b", low)
    if vague:
        add("quantify", "medium",
            f"adjective where a number belongs: {', '.join(sorted(set(vague))[:3])}",
            vague[0])

    # --- R7: bold label present when listing (normalized, quote-stripped text)
    norm = "\n".join(lines)
    if stats["lists"] and not re.search(r"^\s*[-*] \*\*.+?\*\*", norm, re.M):
        add("scannable-labels", "low",
            "bullets lack bold lead-in labels — eye has no anchor", "")

    # score
    penalty = {"high": 12, "medium": 6, "low": 3, "info": 0}
    score = 100 - sum(penalty.get(f["severity"], 0) for f in findings)
    score = max(0, score)

    structure = (stats["bullet_lines"] + sum(1 for l in content
                 if is_heading(l) or is_table(l)))
    stats["structure_ratio"] = round(structure / max(len(content), 1), 2)
    stats["content_lines"] = len(content)
    stats["word_count"] = len(text.split())

    return score, findings, stats

# ---------------------------------------------------------------- report

def render(score, findings, stats, src=""):
    verdict = "✅ PASS" if score >= 70 else ("⚠️  REWRITE" if score >= 45 else "❌ FAIL")
    out = []
    out.append(f"{verdict}  score {score}/100 {src}")
    out.append(f"    {stats.get('content_lines',0)} lines · "
               f"{stats.get('word_count',0)} words · "
               f"{int(stats.get('structure_ratio',0)*100)}% structured · "
               f"{stats.get('long_paras',0)} wall(s)-of-text")
    if not findings:
        out.append("    no violations")
        return "\n".join(out)
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    for f in sorted(findings, key=lambda x: order.get(x["severity"], 9)):
        mark = {"high": "🔴", "medium": "🟡", "low": "🔵", "info": "⚪"}[f["severity"]]
        out.append(f"  {mark} [{f['rule']}] {f['detail']}")
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser(description="Lint a reply for skimmability.")
    ap.add_argument("--file")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--prose", action="store_true",
                    help="document mode: skip the ≤8-line chat ceiling")
    a = ap.parse_args()

    if a.file:
        text = open(a.file, encoding="utf-8").read()
        src = a.file
    elif a.stdin:
        text = sys.stdin.read()
        src = "(stdin)"
    else:
        ap.error("pass --file PATH or --stdin")
        return 2

    score, findings, stats = lint(text, chat_mode=not a.prose)
    if a.json:
        print(json.dumps({"score": score, "stats": stats,
                          "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(render(score, findings, stats, src))
    return 0 if score >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())
