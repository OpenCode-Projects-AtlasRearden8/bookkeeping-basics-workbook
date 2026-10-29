# Bookkeeping Basics — A First-Year Workbook for Solopreneurs

A friendly, plain-English workbook for your **first year of small-business books**:
the six accounts you actually need, cash-basis accounting explained without jargon,
a 30-minute monthly close ritual, shoebox-to-system receipt habits, "CPA Day"
preparation, and how to read a one-page P&L without fear.

**Education, never advice.** Nothing here is tax, legal, or accounting advice.
Licensed professionals — a CPA, for example — are the ones whose job is the advice
part; the workbook teaches beginner habits and prepares you for that conversation.

## What's inside

| Doc | What it is |
|-----|------------|
| `docs/01-six-accounts.md` | The six accounts that carry a first year: Business Checking, Income, Operating Expenses, Big Purchases, Pay Me (Draws), Set-Aside |
| `docs/02-cash-basis.md` | Cash basis in plain English: money counts when it moves |
| `docs/03-monthly-close.md` | The 30-minute monthly close ritual, phase by phase |
| `docs/04-receipt-habits.md` | Shoebox-to-system receipt habits: drop and dot |
| `docs/05-cpa-day.md` | CPA Day: the seven things to have ready |
| `docs/06-reading-pnl.md` | Reading a one-page P&L without fear |
| `docs/07-monthly-close-checklist.md` | Print-and-go one-page monthly close checklist |
| `docs/08-ledger-worksheet.md` | Fill-in ledger worksheet: monthly blocks + Yearly Tracker |
| `docs/09-glossary.md` | Plain-English glossary of every term used |

## Build & run

The `site/` HTML is generated from `docs/*.md` by a dependency-free Python script
(no markdown libraries, no pandoc, no network access):

```bash
python3 build.py            # build site/ from docs/
python3 build.py --check    # build, then run internal self-checks
python3 build.py --clean    # remove site/ first, then build

python3 -m pytest           # run the test suite (tests/)
```

Then open `site/index.html` in any browser — the site is fully static and
local-first (no web fonts, no remote assets, no cookies, no analytics).

## Design notes

- **Six accounts, one page, half an hour a month.** The whole system fits on paper.
- **Warm, not condescending.** Explained the way a friend would, step by step.
- **Local-first.** Static HTML, no external resources; your browser never phones home.
- **ADHD-friendly.** Small steps, timers, re-entry ramps for when you fall off the wagon.

## Companion project

This workbook complements **cashflow-simple-ledger**, an even simpler cash-only
ledger for people who want fewer moving parts than six accounts.

## Copyright & license

Copyright (c) 2026 Asdale Dynamics, LLC — see [LICENSE](LICENSE). Released under
the MIT license.
