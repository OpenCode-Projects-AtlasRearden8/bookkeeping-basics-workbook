# STATUS.md

**Project:** Bookkeeping Basics — A First-Year Workbook for Solopreneurs
**Owner:** Asdale Dynamics, LLC
**Date:** 2026-10-29
**License:** MIT (`LICENSE`)

## What was built

A friendly, plain-English workbook covering a solopreneur's first year of books,
published as Markdown docs plus a generated static HTML site. **Education only —
never tax, legal, or accounting advice** (stated in every chapter, the site
footer, and the README).

Content (9 documents in `docs/`):

1. **The Six Accounts You Actually Need** — Business Checking, Income, Operating
   Expenses, Big Purchases, Pay Me (Owner Draws), Set-Aside; kitchen-table tests
   for each; a worked mini-month.
2. **Cash Basis, in Plain English** — "money counts when it moves," four ways
   money arrives, three flavors of spending, common mistakes.
3. **The 30-Minute Monthly Close Ritual** — six timed phases (gather, match,
   foot, jar check, receipt sweep, close the book) plus recovery moves when a
   month goes sideways.
4. **Shoebox-to-System Receipt Habits** — the "drop and dot" two-minute daily
   habit, digital-receipts setup, monthly sweep, a re-entry ramp for missed days.
5. **CPA Day — What to Have Ready** — a seven-item packing list, basics sheet,
   and questions list for the first professional visit.
6. **Reading a One-Page P&L Without Fear** — a three-move read, the "laptop
   trap" (Big Purchases vs Operating), Draws-aren't-expenses, and the timing
   wobble.
7. **Monthly Close Checklist** (one-page printable).
8. **Fill-In Ledger Worksheet** — monthly blocks, totals block, Yearly Tracker strip.
9. **Glossary — Plain-English Edition.**

Every chapter explicitly disclaims tax/legal/accounting advice and points to
licensed professionals; the README credits **Asdale Dynamics, LLC**, and the
workbook names its simpler companion project **cashflow-simple-ledger**.

## How to run it

```bash
python3 build.py            # generates site/ from docs/ (10 HTML pages + styles)
python3 build.py --check    # build, then self-check links/local-only traversal
python3 build.py --clean    # wipe site/ first
python3 -m pytest           # run tests/tests (28 tests)
```

Then open `site/index.html` in a browser. Fully static and local-first: no web
fonts, no remote assets, no analytics, no network calls at build or run time.

## Verification results (2026-10-29)

- `python3 build.py --check` → built 10 pages into `site/`; self-check OK
  (all chapter links resolve, stylesheet referenced by every page, zero remote
  resource references in any HTML file).
- `python3 -m pytest` → **28 passed**. Coverage includes: markdown renderer
  unit tests (bold/italic/code, links, HTML escaping, tables, lists, checkbox
  lists, blockquotes, paragraphs, fenced code), content tests (six accounts
  named, cash-basis core sentence present, checklist is a single fenced page,
  glossary covers key terms, disclaimer language present in every doc, no
  secret-like strings, plain-English-only character set), permission tests, and
  build-pipeline tests (site builds, index links all docs, footer/`lang="en"`
  on every page, exact LICENSE copyright line, README credits).
- HTML well-formedness check (tag-balance via `html.parser`) → all 10 pages
  balanced, no unclosed tags.
- LICENSE copyright line verified exactly: `Copyright (c) 2026 Asdale Dynamics, LLC`.

## Known gaps

- The markdown renderer is intentionally minimal (single-level blockquotes,
  no nested tables, no images). If docs grow richer syntax, extend
  `render_markdown` and the test suite accordingly.
- No search or dark mode; single shared stylesheet only.
- Only a skeleton git history (initial commit); no CI workflow yet.
- Dollar examples are generic fictional figures; nothing here resolves
  jurisdiction-specific requirements — the CPA Day chapter exists precisely
  because those calls belong to licensed professionals.
