#!/usr/bin/env python3
"""Build script for the Bookkeeping Basics Workbook.

Converts docs/*.md into a static HTML site in site/ using a small,
dependency-free Markdown renderer (headings, paragraphs, lists,
tables, blockquotes, code blocks, fenced blocks, horizontal rules,
links, bold/italic/inline code/escape sequences).

Usage:
    python3 build.py            # build site/
    python3 build.py --clean    # remove site/ first, then build
    python3 build.py --check    # build, then run internal self-checks

No network access, no external dependencies.
"""

import argparse
import datetime
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
ASSETS = ROOT / "assets"

TITLE = "Bookkeeping Basics — A First-Year Workbook for Solopreneurs"
FOOTER = (
    "Bookkeeping Basics Workbook &middot; "
    "Copyright (c) 2026 Asdale Dynamics, LLC &middot; "
    "Education only &mdash; never tax, legal, or accounting advice."
)

DOC_ORDER = [
    ("01-six-accounts.md", "The Six Accounts You Actually Need"),
    ("02-cash-basis.md", "Cash Basis, in Plain English"),
    ("03-monthly-close.md", "The 30-Minute Monthly Close Ritual"),
    ("04-receipt-habits.md", "Shoebox-to-System Receipt Habits"),
    ("05-cpa-day.md", "CPA Day — What to Have Ready"),
    ("06-reading-pnl.md", "Reading a One-Page P&L Without Fear"),
    ("07-monthly-close-checklist.md", "Monthly Close Checklist (One-Page)"),
    ("08-ledger-worksheet.md", "Fill-In Ledger Worksheet"),
    ("09-glossary.md", "Glossary — Plain-English Edition"),
]

WORKSHEET_INTRO = (
    "A friendly first-year bookkeeping workbook for solopreneurs: six accounts, "
    "cash basis in plain English, a 30-minute monthly close, receipt habits, "
    "CPA Day prep, and reading a one-page P&L without fear."
)


# --------------------------------------------------------------------------
# Inline markdown rendering
# --------------------------------------------------------------------------

def render_inline(text):
    """Render inline markdown (links, code, bold, italic, esc-h) to HTML."""
    # Placeholder out inline code first so other rules never touch it.
    code_spans = []

    def stash_code(m):
        code_spans.append(html.escape(m.group(1)))
        return "\x00CODE%d\x00" % (len(code_spans) - 1)

    text = re.sub(r"`([^`]+)`", stash_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)),
                  text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    for i, c in enumerate(code_spans):
        text = text.replace("\x00CODE%d\x00" % i, "<code>%s</code>" % c)
    return text


# --------------------------------------------------------------------------
# Block-level markdown rendering
# --------------------------------------------------------------------------

def render_markdown(md):
    """Convert a markdown string to an HTML fragment (no wrapping tags)."""
    lines = md.replace("\r\n", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Fenced code block
        m = re.match(r"^```\s*(\S*)\s*$", line)
        if m:
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code)))
            continue

        # Table
        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?[\s:\-|]+\|", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "<thead><tr>%s</tr></thead>" % "".join(
                "<th>%s</th>" % render_inline(c) for c in header)
            tbody = "<tbody>%s</tbody>" % "".join(
                "<tr>%s</tr>" % "".join("<td>%s</td>" % render_inline(c) for c in row)
                for row in rows)
            out.append("<table>%s%s</table>" % (thead, tbody))
            continue

        # Horizontal rule
        if re.match(r"^\s*_{5,}\s*$", line) or re.match(r"^\s*-{5,}\s*$", line) or re.match(r"^\s*={5,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, render_inline(m.group(2).strip()), level))
            i += 1
            continue

        # Blockquote (only single-level needed for this content)
        if line.startswith(">"):
            quote = []
            while i < n and lines[i].startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % render_blocks(quote))
            continue

        # Checkbox list item (- [ ] / - [x])
        m = re.match(r"^\s*-\s+\[([ xX])\]\s+(.*)$", line)
        if m:
            items = []
            while i < n:
                mm = re.match(r"^\s*-\s+\[([ xX])\]\s+(.*)$", lines[i])
                if not mm:
                    break
                checked = mm.group(1).lower() == "x"
                box = '<input type="checkbox" disabled%s> ' % (" checked" if checked else "")
                items.append('<li class="checkbox">%s%s</li>' % (box, render_inline(mm.group(2))))
                i += 1
            out.append('<ul class="checklist">%s</ul>' % "".join(items))
            continue

        # Unordered list
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>%s</li>" % render_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue

        # Ordered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append("<li>%s</li>" % render_inline(re.sub(r"^\s*\d+[.)]\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (lazy continuation until blank/block start)
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|>|\s*[-*]\s|\s*\d+[.)]\s|```|\||\s*[-=]{5,}\s*$)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % "<br>".join(render_inline(p.strip()) for p in para))

    return "\n".join(out)


def render_blocks(lines):
    """Render a list of raw lines through the same block pipeline."""
    return render_markdown("\n".join(lines))


def extract_title(md):
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    return m.group(1).strip() if m else "Untitled"


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def page(title, body_html, active_slug, header_title=None, header_sub=None):
    toc = []
    for fname, label in DOC_ORDER:
        slug = fname[:-3]
        cls = ' class="active"' if slug == active_slug else ""
        toc.append('<a href="%s.html"%s>%s</a>' % (slug, cls, html.escape(label)))

    home_cls = ' class="active"' if active_slug == "" else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="index.html"{home_cls}>Bookkeeping Basics</a></div>
  <div class="tagline">A first-year workbook for solopreneurs &mdash; friendly, plain-English, education only</div>
</header>
<div class="wrap">
  <nav class="toc">
    <p class="toc-title">Read the workbook</p>
    <a href="index.html"{home_cls}>Start here</a>
    {"".join(toc)}
    <p class="toc-note">Companion project: <em>cashflow-simple-ledger</em> &mdash; an even simpler cash-only ledger.</p>
  </nav>
  <main class="doc">
{body_html}
  </main>
</div>
<footer>{FOOTER}</footer>
</body>
</html>
"""


def slug_of(fname):
    return fname[:-3]


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build_site():
    if not DOCS.is_dir():
        sys.exit(f"error: docs/ not found at {DOCS}")

    SITE.mkdir(exist_ok=True)
    pages = {}

    # Convert each markdown doc
    for fname, label in DOC_ORDER:
        src = DOCS / fname
        if not src.is_file():
            sys.exit(f"error: missing doc {src}")
        md = src.read_text(encoding="utf-8")
        title = extract_title(md)
        body = render_markdown(md)
        pages[slug_of(fname)] = (title, body)

    # Landing page: intro card + chapter cards
    cards = []
    for i, (fname, label) in enumerate(DOC_ORDER, 1):
        slug = slug_of(fname)
        blurb = {
            "01": "Six, not forty: Business Checking, Income, Operating Expenses, Big Purchases, Pay Me, Set-Aside.",
            "02": "Money counts when it moves, not when it's promised. One idea, patiently.",
            "03": "A timer, six steps, zero all-nighters. The ritual is the skill.",
            "04": "Drop and dot: two words per receipt, two minutes per day, a tray that empties monthly.",
            "05": "The seven things to bring so the professional's hour stays short and calm.",
            "06": "Three moves, one page: is it positive, are the ingredients sane, how does it compare.",
            "07": "The printable one-pager that runs the monthly close.",
            "08": "A full-year paper ledger: monthly blocks, totals, and a Yearly Tracker strip.",
            "09": "Every term, defined across a kitchen table.",
        }.get(fname[:2], "")
        kind = "Reference" if fname[:2] in ("07", "08", "09") else ""
        cards.append(
            '<a class="card" href="%s.html"><span class="card-num">%02d</span>'
            '<span class="card-kind">%s</span><span class="card-title">%s</span>'
            '<span class="card-blurb">%s</span></a>'
            % (slug, i, kind, html.escape(label), html.escape(blurb))
        )

    intro = f"""<section class="hero">
<h1>Bookkeeping Basics</h1>
<p class="lede">{html.escape(WORKSHEET_INTRO)}</p>
<div class="not-advice"><strong>Education, never advice.</strong> Everything here is a plain-English
explanation of beginner bookkeeping habits &mdash; it is never tax, legal, or accounting advice.
Licensed professionals (a CPA, for example) are the ones whose job is the advice part; Chapter 5
shows you how to meet one prepared.</div>
</section>
<section class="cards">{''.join(cards)}</section>
<section class="start">
<h2>How to use this workbook</h2>
<ol>
<li><strong>Skim Chapters 1&ndash;2</strong> (about 20 minutes) and set up your six accounts.</li>
<li><strong>Run one monthly close</strong> with the checklist at your elbow &mdash; paper worksheet, even if you plan to use software.</li>
<li><strong>Build the receipt habit</strong> in the same month; the two reinforce each other.</li>
<li><strong>Pack for CPA Day</strong> when the first real money (or the first real question) shows up.</li>
</ol>
<p>This workbook is a friendly companion to <em>cashflow-simple-ledger</em>, an even simpler
cash-only ledger for people who want fewer moving parts. If six accounts ever feel like too many,
that's the bridge back.</p>
</section>"""

    pages[""] = ("Bookkeeping Basics — Start Here", intro)

    # Write pages
    for slug, (title, body) in pages.items():
        out = SITE / ((slug + ".html") if slug else "index.html")
        out.write_text(page(title, body, slug), encoding="utf-8")

    # Styles
    css = ASSETS / "styles.css"
    (SITE / "styles.css").write_text(css.read_text(encoding="utf-8"), encoding="utf-8")

    return pages


def self_check(pages):
    problems = []
    # Every listed doc produced exactly one page
    for fname, _label in DOC_ORDER:
        slug = slug_of(fname)
        if slug in ("", None) or slug not in pages:
            problems.append(f"missing page for {slug}")
    # Cross-links on the landing page must resolve
    index_html = (SITE / "index.html").read_text(encoding="utf-8")
    for fname, _label in DOC_ORDER:
        link = fname[:-3] + ".html"
        if ('href="%s"' % link) not in index_html:
            problems.append(f"index.html missing link {link}")
    # Each built page references the stylesheet
    for out in SITE.glob("*.html"):
        if 'href="styles.css"' not in out.read_text(encoding="utf-8"):
            problems.append(f"{out.name} missing stylesheet link")
    # No external resource references (local-first)
    for out in SITE.glob("*.html"):
        txt = out.read_text(encoding="utf-8")
        if re.search(r'(href|src)=["\']https?://', txt):
            problems.append(f"{out.name} references a remote resource")
    return problems


def clean_site():
    if SITE.is_dir():
        shutil.rmtree(SITE)


def main():
    parser = argparse.ArgumentParser(description="Build the workbook site.")
    parser.add_argument("--clean", action="store_true", help="remove site/ before building")
    parser.add_argument("--check", action="store_true", help="run self-checks after building")
    args = parser.parse_args()

    if args.clean:
        clean_site()

    pages = build_site()
    built = sorted(p.name for p in SITE.glob("*"))
    print(f"Built {len(pages)} pages into site/:")
    for name in built:
        print("  site/" + name)

    problems = self_check(pages)
    if problems:
        for p in problems:
            print("FAIL: " + p, file=sys.stderr)
        sys.exit(1)
    print("Self-check: OK (%d pages, all links local and resolvable)" % len(pages))


if __name__ == "__main__":
    main()
