"""Tests for the Bookkeeping Basics Workbook build.

Run:  python3 -m pytest
"""

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build as build_mod  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


# --------------------------------------------------------------------------
# Markdown renderer unit tests
# --------------------------------------------------------------------------

class TestInline:
    def test_bold_italic_code(self):
        assert build_mod.render_inline("**a** *b* `c|d`") == "<strong>a</strong> <em>b</em> <code>c|d</code>"

    def test_link(self):
        assert build_mod.render_inline("[x](y.html)") == '<a href="y.html">x</a>'

    def test_html_escaped(self):
        out = build_mod.render_inline("<script> & stuff")
        assert "<script>" not in out
        assert "&amp;" in out or "&lt;script&gt;" in out

    def test_placeholder_code_leaks_nothing(self):
        out = build_mod.render_inline("`a**b**`")
        assert "<strong>" not in out
        assert "<code>a**b**</code>" in out

    def test_dollar_signs_survive(self):
        assert "$580" in build_mod.render_inline("$580")


class TestBlocks:
    def test_headings(self):
        out = build_mod.render_markdown("## Hi")
        assert "<h2>Hi</h2>" in out

    def test_fenced_code(self):
        out = build_mod.render_markdown("```\na < b\n```")
        assert "<pre><code>" in out and "a &lt; b" in out

    def test_table_renders_rows_and_cells(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        out = build_mod.render_markdown(md)
        assert "<th>A</th>" in out and "<td>3</td>" in out

    def test_lists(self):
        out = build_mod.render_markdown("- a\n- b\n\n1. c\n2. d")
        assert "<ul><li>a</li><li>b</li></ul>" in out
        assert "<ol><li>c</li><li>d</li></ol>" in out

    def test_checkbox_list(self):
        out = build_mod.render_markdown("- [ ] todo\n- [x] done")
        assert 'type="checkbox" disabled' in out
        assert " checked" in out

    def test_blockquote(self):
        out = build_mod.render_markdown("> note\n> more")
        assert "<blockquote>" in out and "note" in out and "more" in out

    def test_hr_and_paragraph(self):
        out = build_mod.render_markdown("to be\n\n-----\n\nthat is")
        assert "<hr>" in out
        assert "<p>to be</p>" in out
        assert "<p>that is</p>" in out

    def test_paragraph_lazy_continuation(self):
        out = build_mod.render_markdown("line one\nline two")
        assert "<p>line one<br>line two</p>" in out

    def test_quote_block_containing_table(self):
        # Nested pipeline reuse (blockquote containing other blocks)
        out = build_mod.render_markdown("> | A |\n> |---|\n> | 1 |")
        assert "<table>" in out


# --------------------------------------------------------------------------
# Content tests
# --------------------------------------------------------------------------

class TestDocsContent:
    def test_all_nine_docs_exist(self):
        for fname, _ in build_mod.DOC_ORDER:
            assert (DOCS / fname).is_file(), f"missing {fname}"

    def test_six_accounts_chapter_mentions_all_six(self):
        text = (DOCS / "01-six-accounts.md").read_text(encoding="utf-8")
        for term in ("Business Checking", "Income", "Operating Expenses",
                     "Big Purchases", "Pay Me", "Set-Aside"):
            assert term in text, f"six-accounts doc missing {term}"

    def test_cash_basis_core_sentence_present(self):
        text = (DOCS / "02-cash-basis.md").read_text(encoding="utf-8")
        assert "money counts when it actually moves" in text

    def test_checklist_doc_is_fenced_and_single_page(self):
        text = (DOCS / "07-monthly-close-checklist.md").read_text(encoding="utf-8")
        assert text.count("```") == 2, "checklist content should be one fenced block"

    def test_ledger_worksheet_has_yearly_tracker(self):
        text = (DOCS / "08-ledger-worksheet.md").read_text(encoding="utf-8")
        assert "Yearly Tracker" in text and "Set-Aside" in text

    def test_glossary_defines_key_terms(self):
        text = (DOCS / "09-glossary.md").read_text(encoding="utf-8")
        for term in ("Cash basis", "Reconciliation", "Owner Draws", "P&L"):
            assert term in text

    def test_no_english_cjk_or_stray_nonascii_misuse(self):
        # Content must stay in plain English (allow real punctuation/dashes/curly quotes/marks)
        allowed = set("—–‘’“”…·✓&©→" + "│└├─┬")
        for f in sorted(DOCS.glob("*.md")):
            t = f.read_text(encoding="utf-8")
            for ch in t:
                if ord(ch) > 127 and ch not in allowed and not ch.isspace():
                    raise AssertionError(f"{f.name}: unexpected non-ASCII {ch!r}")

    def test_no_secret_like_strings(self):
        pat = re.compile(
            r"(?i)\b(sk-[a-z0-9]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+|password\s*[:=]\s*['\"][^'\"]+|BEGIN [A-Z ]*PRIVATE KEY)\b")
        for f in sorted(DOCS.glob("*.md")):
            m = pat.search(f.read_text(encoding="utf-8"))
            assert not m, f"secret-like string in {f.name}"

    def test_disclaimer_present_in_each_chapter(self):
        for fname in [n for n, _ in build_mod.DOC_ORDER]:
            t = (DOCS / fname).read_text(encoding="utf-8")
            assert re.search(r"(?i)(not tax advice|never tax|education|licensed professional|not advice)", t), fname


# --------------------------------------------------------------------------
# Build pipeline tests (run against a throwaway copy of site/)
# --------------------------------------------------------------------------

class TestBuildPipeline:
    def test_build_and_self_check(self, tmp_path=None):
        # build.py writes into ROOT/site; clean before/after for a fresh test
        build_mod.clean_site()
        pages = build_mod.build_site()
        problems = build_mod.self_check(pages)
        assert problems == [], problems
        # expected page files exist
        for fname, _ in build_mod.DOC_ORDER:
            assert (build_mod.SITE / (fname[:-3] + ".html")).is_file()
        assert (build_mod.SITE / "index.html").is_file()

    def test_index_links_and_local_only(self):
        html_text = (build_mod.SITE / "index.html").read_text(encoding="utf-8")
        for fname, _ in build_mod.DOC_ORDER:
            assert ('href="%s.html"' % fname[:-3]) in html_text
        assert not re.search(r'(href|src)=["\']https?://', html_text)

    def test_every_page_has_footer_disclaimer_and_lang(self):
        for page in sorted(build_mod.SITE.glob("*.html")):
            t = page.read_text(encoding="utf-8")
            assert '<html lang="en">' in t, page.name
            assert "Asdale Dynamics, LLC" in t, page.name
            assert "&mdash; never tax, legal, or accounting advice" in t or "Education only" in t, page.name

    def test_license_exact_copyright_line(self):
        lic = (ROOT / "LICENSE").read_text(encoding="utf-8")
        first_lines = "\n".join(lic.splitlines()[:3])
        assert "Copyright (c) 2026 Asdale Dynamics, LLC" in first_lines
        # exactly that string
        assert "Copyright (c) 2026 Asdale Dynamics, LLC" in lic.splitlines()[2]

    def test_readme_credits_and_companion(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "Asdale Dynamics, LLC" in readme
        assert "cashflow-simple-ledger" in readme
        assert "python3 build.py" in readme
