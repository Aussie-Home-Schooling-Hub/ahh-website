#!/usr/bin/env python3
"""
AHH module checker for one self-contained HTML file.

This is not a Teach Then Do checker. It looks at a single HTML module.

A pass is not a human fact check of every sentence. The script fails what
it can prove is leftover, invented, or off the approved lists.

Usage:
    python3 qa_module.py brainforge.html
    python3 qa_module.py brainforge.html --allow-online

Exits 1 if any check fails.

--allow-online permits only these remote hosts:
    cdn.tailwindcss.com
    the Font Awesome CDN (cdnjs.cloudflare.com font-awesome, or a fontawesome.com kit)
    api.languagetool.org
Anything else is a remote asset and fails. With no flag, every remote asset fails.
"""

from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

PASS: list[str] = []
FAIL: list[tuple[str, str]] = []
UNVERIFIED: list[tuple[int, str, str]] = []

# Pete's BrainForge activity statement. It is allowed only when this exact
# wording is the statement in the file. A changed sentence is checked like
# any other claim.
ALLOWED_ACTIVITY = (
    "The student conducted independent inquiry using digital research tools. "
    "To fulfill curriculum outcomes for creating informative texts, the student analyzed source data, "
    "extracted key evidence to mitigate plagiarism risks, and synthesised findings into an objective text structure. "
    "The student successfully applied textual hierarchies\u2014including structural main headings and subordinate subheadings\u2014"
    "to organize information logically before transferring the schema into physical media."
)

# Australian Curriculum v9.0 names from AHH AI Builder Brief section 7.
# Spellings are the brief's. Matching ignores case so "Language" and "language"
# are the same name; a different name still fails.
APPROVED_CURRICULUM = [
    "English",
    "Language",
    "Literature",
    "Literacy",
    "Mathematics",
    "Number",
    "Algebra",
    "Measurement",
    "Space",
    "Statistics",
    "Probability",
    "Science",
    "Science understanding",
    "Biological sciences",
    "Chemical sciences",
    "Earth and space sciences",
    "Physical sciences",
    "Science as a human endeavour",
    "Science inquiry",
    "HASS",
    "History",
    "Geography",
    "Civics and Citizenship",
    "Economics and Business",
    "Technologies",
    "Design and Technologies",
    "Digital Technologies",
    "The Arts",
    "Dance",
    "Drama",
    "Media Arts",
    "Music",
    "Visual Arts",
    "Health and Physical Education",
    "Personal, social and community health",
    "Movement and physical activity",
    "Languages",
    "Aboriginal and Torres Strait Islander Histories and Cultures",
    "Asia and Australia's Engagement with Asia",
    "Sustainability",
    "Critical and Creative Thinking",
    "Digital Literacy",
    "Ethical Understanding",
    "Intercultural Understanding",
    "Numeracy",
    "Personal and Social Capability",
    "Australian Curriculum",
    "Australian Curriculum v9.0",
]

# Words the brief uses for the lists themselves. They are not strand names.
CURRICULUM_META = [
    "learning areas",
    "learning area",
    "sub-strands",
    "sub-strand",
    "substrands",
    "substrand",
    "strands",
    "strand",
    "general capabilities",
    "general capability",
    "cross-curriculum priorities",
    "cross-curriculum priority",
    "v9.0",
    "version 9.0",
    "version 9",
]

VISIBLE_FORBIDDEN = [
    (r"\bTODO\b", "TODO"),
    (r"Lorem ipsum", "Lorem ipsum"),
    (r"Coming soon", "Coming soon"),
    (r"Sample text", "Sample text"),
    (r"Your text here", "Your text here"),
    (r"FACT-CHECKED", "FACT-CHECKED"),
    (r"As an AI", "As an AI"),
    (r"FIX:", "FIX:"),
    (r"FIXED:", "FIXED:"),
    (r"Corrected version", "Corrected version"),
    (r"\bdraft\b", "draft"),
    (r"\bplaceholder\b", "placeholder"),
]

MONTHS = (
    "January|February|March|April|May|June|July|August|"
    "September|October|November|December"
)

INVENTED_PATTERNS = [
    (r"\btestimonials?\b", "testimonial"),
    (r"\b(?:customer|product)\s+reviews?\b", "review"),
    (r"\baward(?:-|\s)?winning\b", "award"),
    (r"\bawards?\b", "award"),
    (r"\b(?:5|five)[- ]star\b", "star rating"),
    (r"\b\d+(?:\.\d+)?\s*%", "percentage statistic"),
    (r"\b\d+\s+out\s+of\s+\d+\b", "statistic"),
    (r"\b(?:studies|research)\s+shows?\b", "unsourced research claim"),
    (r"\b\d[\d,]*\s+(?:people|families|parents|customers|mums|students|children|users|teachers)\b", "number of people"),
    (r"\b(?:thousands|millions|hundreds)\s+of\s+(?:people|families|parents|customers|students|children)\b", "number of people"),
    (r"\$\s?\d", "price"),
    (r"\b\d+(?:\.\d{2})?\s*(?:dollars|AUD)\b", "price"),
    (r"\bguaranteed\b", "promise to an authority"),
    (r"\bwill\s+(?:accept|approve|pass)\b", "promise that an authority will accept the work"),
    (r"\bpasses?\s+registration\b", "promise that an authority will accept the work"),
    (r"\bapproved\s+by\b", "promise that an authority will accept the work"),
    (r"[\u201c][^\u201d]{8,}[\u201d]", "quoted passage"),
    (r"\"[^\"\n]{12,}\"", "quoted passage"),
]


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASS.append(name)
        print(f"  PASS  {name}")
    else:
        FAIL.append((name, detail))
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def blank_kept(match: re.Match[str]) -> str:
    """Replace a region with spaces but keep newlines, so line numbers stay true."""
    return re.sub(r"[^\n]", " ", match.group(0))


def hide_non_visible(html: str) -> str:
    text = re.sub(r"<!--[\s\S]*?-->", blank_kept, html)
    text = re.sub(r"<script\b[\s\S]*?</script>", blank_kept, text, flags=re.I)
    text = re.sub(r"<style\b[\s\S]*?</style>", blank_kept, text, flags=re.I)
    return text


class Piece:
    def __init__(self, text: str, line: int, heading: bool) -> None:
        self.text = text
        self.line = line
        self.heading = heading


def visible_pieces(html: str) -> list[Piece]:
    """Customer-visible text: text nodes, title, and attributes a person can see."""
    masked = hide_non_visible(html)
    pieces: list[Piece] = []
    heading_depth = 0
    token = re.compile(r"<(/?)([a-zA-Z][\w:-]*)([^>]*)>|([^<]+)")
    for match in token.finditer(masked):
        if match.group(4) is not None:
            raw = unescape(match.group(4))
            text = norm(raw)
            if text:
                pieces.append(Piece(text, line_of(html, match.start()), heading_depth > 0))
            continue
        closing = match.group(1) == "/"
        name = match.group(2).lower()
        attrs = match.group(3) or ""
        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading_depth += -1 if closing else 1
            heading_depth = max(0, heading_depth)
            continue
        if closing:
            continue
        line = line_of(html, match.start())
        for attr in ("placeholder", "title", "alt", "aria-label"):
            found = re.search(
                rf"""\b{attr}\s*=\s*(['"])(.*?)\1""",
                attrs,
                re.I | re.S,
            )
            if not found:
                continue
            value = norm(unescape(found.group(2)))
            if value:
                pieces.append(Piece(value, line, False))
    return pieces


def sentences_of(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"\u201c])", text)
    return [part.strip() for part in parts if part.strip()]


def activity_allowed(pieces: list[Piece]) -> bool:
    blob = norm(" ".join(piece.text for piece in pieces if not piece.heading))
    return norm(ALLOWED_ACTIVITY) in blob


def sentence_is_activity(sentence: str, allowed: bool) -> bool:
    if not allowed:
        return False
    return norm(sentence) in norm(ALLOWED_ACTIVITY)


def approved_name(phrase: str) -> bool:
    folded = norm(phrase).casefold()
    if not folded:
        return True
    for name in APPROVED_CURRICULUM + CURRICULUM_META:
        if folded == name.casefold():
            return True
    if re.fullmatch(r"years?\s+\d+(?:\s*[\u2013-]\s*\d+)?", folded):
        return True
    if re.fullmatch(r"ages?\s+\d+(?:\s*[\u2013-]\s*\d+)?", folded):
        return True
    return False


def curriculum_phrase_after_label(sentence: str) -> str:
    """The words after 'Australian Curriculum' that are not a version, year, or approved name."""
    match = re.search(r"\bAustralian Curriculum\b\s*(.*)$", sentence, re.I)
    if not match:
        return ""
    rest = match.group(1).strip()
    rest = re.sub(r"^(?:v9(?:\.0)?|version\s+9(?:\.0)?)\b[,:\s]*", "", rest, flags=re.I).strip()
    rest = re.sub(
        r"^(?:years?|ages?)\s+\d[\d\s\u2013\-toand]*[,:\s]*",
        "",
        rest,
        flags=re.I,
    ).strip()
    names = sorted(APPROVED_CURRICULUM + CURRICULUM_META, key=len, reverse=True)
    changed = True
    while rest and changed:
        changed = False
        for name in names:
            if rest.casefold().startswith(name.casefold()):
                rest = rest[len(name):].lstrip(" ,:;>-").strip()
                changed = True
                break
    if not rest or re.match(r"^(?:These|This|It|The)\b", rest):
        return ""
    name = re.match(
        r"([A-Za-z][A-Za-z\s]{1,80}?)(?=\s+(?:require|requires|required|must|include|includes|cover|covers)\b|[.]|$)",
        rest,
    )
    if not name:
        return ""
    phrase = norm(name.group(1))
    if approved_name(phrase):
        return ""
    return phrase


def path_names_off_list(sentence: str) -> list[str]:
    off: list[str] = []
    for match in re.finditer(
        r"\b([A-Z][^<>\n.]{0,40}?)\s*>\s*([A-Z][^<>\n.]{0,40})",
        sentence,
    ):
        for part in (match.group(1), match.group(2)):
            cleaned = norm(re.sub(r"^(?:Subject:\s*)", "", part))
            if cleaned and not approved_name(cleaned):
                off.append(cleaned)
    return off


def curriculum_codes(sentence: str) -> list[str]:
    codes = re.findall(r"\bAC9[A-Z0-9]{3,}\b", sentence)
    codes += re.findall(r"\bAC[A-Z]{2,}\d{3,}[A-Z0-9]*\b", sentence)
    return codes


def has_date(sentence: str) -> bool:
    if re.search(rf"\b\d{{1,2}}\s+(?:{MONTHS})\b", sentence):
        return True
    if re.search(rf"\b(?:{MONTHS})\s+\d{{4}}\b", sentence):
        return True
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", sentence):
        return True
    if re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", sentence):
        return True
    return False


def fact_problems(sentence: str, allowed: bool) -> list[str]:
    if sentence_is_activity(sentence, allowed):
        return []
    problems: list[str] = []
    if re.search(r"\bNESA\b", sentence):
        problems.append(
            "NESA is not the current NSW home-schooling body; home schooling moved to the NSW Department of Education"
        )
    for code in curriculum_codes(sentence):
        problems.append(f"curriculum-looking code {code} is not an approved v9.0 name")
    for name in path_names_off_list(sentence):
        problems.append(f"curriculum name {name!r} is not on the approved v9.0 list")
    phrase = curriculum_phrase_after_label(sentence)
    if phrase:
        problems.append(
            f"curriculum name {phrase!r} is not on the approved v9.0 list"
        )
    if re.search(r"\b(?:outcomes?|achievement standards?)\b", sentence, re.I):
        problems.append("curriculum outcome is not Pete's activity statement and not an approved name")
    if re.search(r"\bAustralian Curriculum\b", sentence, re.I) and re.search(
        r"\b(?:require|requires|required|must)\b", sentence, re.I
    ):
        if not any("not on the approved" in item or "curriculum outcome" in item for item in problems):
            problems.append("curriculum requirement is not Pete's activity statement and not an approved name")
    if has_date(sentence):
        problems.append("states a date that is not in Pete's activity statement")
    for pattern, label in INVENTED_PATTERNS:
        if re.search(pattern, sentence, re.I):
            problems.append(f"looks like an invented {label}")
    # Quotes used as grammar examples inside short UI strings are still quotes.
    # A one-word label such as "Saved" is not a testimonial. The pattern above
    # already requires a longer quoted span.
    return problems


def run_structure(html: str) -> None:
    section("Structure")
    check("file is non-empty", len(html.strip()) > 0, f"size={len(html)}")
    check(
        "starts with <!DOCTYPE html>",
        html.lstrip().lower().startswith("<!doctype html>"),
    )
    head = re.search(r"<head\b[^>]*>", html, re.I)
    if not head:
        check("meta charset is the first element in head", False, "no <head>")
        return
    rest = html[head.end():]
    rest_stripped = rest.lstrip()
    offset = head.end() + (len(rest) - len(rest_stripped))
    charset_ok = bool(
        re.match(
            r"""<meta\s+charset\s*=\s*(['"])UTF-8\1\s*/?>""",
            rest_stripped,
            re.I,
        )
    )
    check(
        "<meta charset=\"UTF-8\"> is first in <head>",
        charset_ok,
        f"line {line_of(html, offset)}: {rest_stripped[:80]!r}",
    )


def run_leftovers(html: str, pieces: list[Piece]) -> None:
    section("Customer-visible leftovers")
    visible = "\n".join(piece.text for piece in pieces)
    any_forbidden = False
    for pattern, label in VISIBLE_FORBIDDEN:
        hits = []
        for piece in pieces:
            if re.search(pattern, piece.text, re.I):
                hits.append(f"line {piece.line}: {piece.text[:140]}")
        if hits:
            any_forbidden = True
            check(f"no customer-visible {label!r}", False, hits[0])
    if not any_forbidden:
        check("no customer-visible build leftovers", True)
    if not visible and html.strip():
        check("visible text could be read", False, "no customer-visible text found")

    log_hits = []
    for match in re.finditer(r"<script\b[\s\S]*?</script>", html, re.I):
        body = match.group(0)
        for found in re.finditer(r"\bconsole\.log\s*\(", body):
            log_hits.append(line_of(html, match.start() + found.start()))
    if log_hits:
        check("no console.log left in script", False, "line " + ", ".join(str(n) for n in log_hits))
    else:
        check("no console.log left in script", True)


def run_inner_html(html: str) -> None:
    section("Inserted text")
    hits = [line_of(html, match.start()) for match in re.finditer(r"\binnerHTML\b", html)]
    if hits:
        check(
            "user text is not written with innerHTML",
            False,
            "line " + ", ".join(str(n) for n in hits),
        )
    else:
        check("user text is not written with innerHTML", True)


def extract_print_blocks(html: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    for match in re.finditer(r"@media\s+print\b[^{]*\{", html, re.I):
        start = match.end() - 1
        depth = 0
        for index in range(start, len(html)):
            char = html[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    blocks.append((line_of(html, match.start()), html[start:index + 1]))
                    break
    return blocks


def run_print_css(html: str) -> None:
    section("Print")
    blocks = extract_print_blocks(html)
    check("print CSS exists", len(blocks) > 0, "no @media print block")
    hides = False
    for _line, block in blocks:
        if re.search(
            r"(?:button|\bnav\b|\.no-print|\binput\b|\bselect\b|\btextarea\b|\.controls\b)[^{]*\{[^}]*display\s*:\s*none",
            block,
            re.I | re.S,
        ):
            hides = True
    check(
        "print CSS hides controls",
        hides,
        "print CSS does not hide buttons, navigation, or .no-print",
    )


def remote_urls(html: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    tag_re = re.compile(
        r"<(script|link|img|audio|video|source|iframe|a)\b[^>]*>",
        re.I,
    )
    for match in tag_re.finditer(html):
        tag = match.group(0)
        for attr in re.finditer(r"""(?:src|href)\s*=\s*(['"])(.*?)\1""", tag, re.I | re.S):
            url = attr.group(2).strip()
            if url.lower().startswith("data:") or url.startswith("#") or url.lower().startswith("mailto:"):
                continue
            if re.match(r"https?://", url, re.I):
                found.append((line_of(html, match.start()), url))
    for match in re.finditer(r"""url\(\s*(['"]?)(https?://[^)'"]+)""", html, re.I):
        found.append((line_of(html, match.start()), match.group(2)))
    for match in re.finditer(
        r"""(?:fetch|open|sendBeacon)\(\s*(['"])(https?://.*?)\1""",
        html,
        re.I,
    ):
        found.append((line_of(html, match.start()), match.group(2)))
    return found


def url_allowed(url: str, allow_online: bool) -> bool:
    if not allow_online:
        return False
    host = (urlparse(url).hostname or "").lower()
    if host == "cdn.tailwindcss.com":
        return True
    if host == "api.languagetool.org":
        return True
    if host == "cdnjs.cloudflare.com" and "font-awesome" in url.lower():
        return True
    if host in {"use.fontawesome.com", "kit.fontawesome.com", "cdn.fontawesome.com"}:
        return True
    return False


def run_remote(html: str, allow_online: bool) -> None:
    section("Remote assets")
    bad = []
    for line, url in remote_urls(html):
        if url_allowed(url, allow_online):
            continue
        bad.append(f"line {line}: {url}")
    if allow_online:
        label = "remote assets are only Tailwind, Font Awesome, or LanguageTool"
    else:
        label = "no remote assets"
    check(label, len(bad) == 0, "; ".join(bad[:6]))


def run_facts(pieces: list[Piece]) -> None:
    section("Facts")
    allowed = activity_allowed(pieces)
    if allowed:
        check("Pete's BrainForge activity statement matches the verbatim sentence", True)
    seen: set[tuple[int, str]] = set()
    for piece in pieces:
        if piece.heading:
            continue
        for sentence in sentences_of(piece.text):
            problems = fact_problems(sentence, allowed)
            if not problems:
                continue
            key = (piece.line, sentence)
            if key in seen:
                continue
            seen.add(key)
            reason = "; ".join(problems)
            detail = f"line {piece.line}: {sentence}"
            check("visible sentence is not an invented or off-list claim", False, f"{detail} ({reason})")
            UNVERIFIED.append((piece.line, sentence, reason))
    if not seen:
        check(
            "no invented statistic, quote, testimonial, review, award, customer number, authority promise, date, price, people count, or off-list curriculum claim",
            True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="AHH checker for one self-contained HTML module")
    parser.add_argument("html", help="Path to one HTML module, for example brainforge.html")
    parser.add_argument(
        "--allow-online",
        action="store_true",
        help="Permit only the Tailwind CDN, the Font Awesome CDN, and api.languagetool.org",
    )
    args = parser.parse_args()
    path = Path(args.html)
    if not path.is_file():
        print(f"File not found: {path}")
        sys.exit(1)
    html = path.read_text(encoding="utf-8", errors="replace")
    pieces = visible_pieces(html)

    print(f"Checking {path}")
    run_structure(html)
    run_leftovers(html, pieces)
    run_inner_html(html)
    run_print_css(html)
    run_remote(html, args.allow_online)
    run_facts(pieces)

    if UNVERIFIED:
        section("Unverified")
        print("  A pass is not a human fact check of every sentence.")
        print("  These lines are what the script can prove is invented or off the approved lists.")
        for line, sentence, reason in UNVERIFIED:
            print(f"  line {line}: {sentence}")
            print(f"    {reason}")

    section("SUMMARY")
    print(f"  Passed: {len(PASS)}")
    print(f"  Failed: {len(FAIL)}")
    if FAIL:
        print("\n  Failures:")
        for name, detail in FAIL:
            print(f"    - {name}" + (f" ({detail})" if detail else ""))
        sys.exit(1)
    print("  ALL MODULE CHECKS PASSED")
    print("  A pass is not a human fact check of every sentence.")
    sys.exit(0)


if __name__ == "__main__":
    main()
