"""Build the rules knowledge base from dom6manual.pdf.

The manual is 449 pages / ~344k tokens, so it can never be loaded wholesale.
This produces a tiered corpus an agent can navigate without reading the book:

    kb/index.md          routing table + the manual's full section index
    kb/sections/*.md     one file per chapter, loaded on demand
    kb/nations/*.md      one file per nation (the Nation Index is 138k tokens)
    kb/manual.txt        page-anchored full text, for grep when the above miss

Sectioning is driven by the PDF's own outline (407 entries with page numbers),
not by heading regexes, so it follows the structure Illwinter authored.

Every page is marked `[p.N]` so the agent can cite a page and you can check it.

    py scripts/build_manual_kb.py
    py scripts/build_manual_kb.py --pdf dom6manual.pdf --out kb
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Chapters split one-file-per-subsection because they are reference lists
#: rather than prose. The Nation Index alone is 189 pages.
SPLIT_CHAPTERS = {"Nation Index"}

#: Chapters that carry the mechanics a battle advisor reasons from. Flagged in
#: the index so the routing table can put them first.
CORE_CHAPTERS = {
    "The Basics",
    "Units",
    "Movement",
    "Combat",
    "Magic",
    "Dominion",
}


@dataclass
class Entry:
    depth: int
    title: str
    page: int


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "untitled"


def load_outline(reader) -> list[Entry]:
    out: list[Entry] = []

    def walk(node, depth=0):
        for item in node or []:
            if isinstance(item, list):
                walk(item, depth + 1)
            else:
                try:
                    page = reader.get_destination_page_number(item)
                except Exception:  # noqa: BLE001 - broken destinations are skipped
                    continue
                title = str(item.title).strip()
                if title:
                    out.append(Entry(depth, title, page))

    walk(reader.outline)
    out.sort(key=lambda e: (e.page, e.depth))
    return out


def render(pages: list[str], lo: int, hi: int, entries: list[Entry], title: str) -> str:
    """Render pages [lo, hi) with page anchors and outline headings."""
    heads: dict[int, list[Entry]] = {}
    for e in entries:
        if lo <= e.page < hi and e.title != title:
            heads.setdefault(e.page, []).append(e)

    parts = [f"# {title}", "", f"*Manual pages {lo + 1}–{hi} (1-based).*", ""]
    for pg in range(lo, hi):
        for e in heads.get(pg, []):
            parts.append(f"{'#' * min(6, e.depth + 2)} {e.title}")
            parts.append("")
        parts.append(f"[p.{pg + 1}]")
        text = (pages[pg] or "").strip()
        if text:
            parts.append(text)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, default=ROOT / "dom6manual.pdf")
    ap.add_argument("--out", type=Path, default=ROOT / "kb")
    args = ap.parse_args()

    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf is required:  py -m pip install pypdf")
        return 1
    if not args.pdf.exists():
        print(f"manual not found: {args.pdf}")
        return 1

    reader = PdfReader(str(args.pdf))
    pages = [(p.extract_text() or "") for p in reader.pages]
    entries = load_outline(reader)
    tops = [e for e in entries if e.depth == 0]
    print(f"{len(pages)} pages, {len(entries)} outline entries, "
          f"{len(tops)} chapters")

    sections = args.out / "sections"
    nations = args.out / "nations"
    for d in (args.out, sections, nations):
        d.mkdir(parents=True, exist_ok=True)

    written: list[tuple[str, Path, int, int, int]] = []  # title, path, lo, hi, chars

    for i, top in enumerate(tops):
        lo = top.page
        hi = tops[i + 1].page if i + 1 < len(tops) else len(pages)

        if top.title in SPLIT_CHAPTERS:
            subs = [e for e in entries if e.depth == 1 and lo <= e.page < hi]
            for j, sub in enumerate(subs):
                s_lo = sub.page
                s_hi = subs[j + 1].page if j + 1 < len(subs) else hi
                if s_hi <= s_lo:
                    s_hi = s_lo + 1
                path = nations / f"{slug(sub.title)}.md"
                body = render(pages, s_lo, s_hi, entries, sub.title)
                path.write_text(body, encoding="utf-8")
                written.append((sub.title, path, s_lo, s_hi, len(body)))
            continue

        path = sections / f"{i:02d}-{slug(top.title)}.md"
        body = render(pages, lo, hi, entries, top.title)
        path.write_text(body, encoding="utf-8")
        written.append((top.title, path, lo, hi, len(body)))

    # Page-anchored full text, for grep when the curated files miss.
    full = []
    for pg, text in enumerate(pages):
        full.append(f"[[page {pg + 1}]]")
        full.append((text or "").strip())
    (args.out / "manual.txt").write_text("\n".join(full), encoding="utf-8")

    # Routing index.
    idx = [
        "# Dominions 6 manual — knowledge base index",
        "",
        "**Start with [`rules-cheatsheet.md`](rules-cheatsheet.md)** — the ~20",
        "mechanics that decide battles, with page citations. It answers most",
        "questions without opening a chapter. That file is hand-written and is",
        "*not* regenerated by this script.",
        "",
        "Generated by `scripts/build_manual_kb.py` from `dom6manual.pdf`.",
        "Sectioning follows the PDF's own outline. Pages are 1-based and marked",
        "`[p.N]` in every file, so any claim can be cited and checked.",
        "",
        "Read **one** file, not the corpus. `manual.txt` is for grep only — it is",
        f"the whole book (~{sum(len(p) for p in pages) // 4:,} tokens).",
        "",
        "## Core rules — start here for battle questions",
        "",
        "| Chapter | File | Pages | ~tokens |",
        "|---|---|---|---|",
    ]
    for title, path, lo, hi, chars in written:
        if title in CORE_CHAPTERS:
            rel = path.relative_to(args.out).as_posix()
            idx.append(f"| {title} | `{rel}` | {lo + 1}–{hi} | {chars // 4:,} |")

    idx += ["", "## Reference chapters", "",
            "| Chapter | File | Pages | ~tokens |", "|---|---|---|---|"]
    for title, path, lo, hi, chars in written:
        if title not in CORE_CHAPTERS and path.parent.name != "nations":
            rel = path.relative_to(args.out).as_posix()
            idx.append(f"| {title} | `{rel}` | {lo + 1}–{hi} | {chars // 4:,} |")

    nat = [w for w in written if w[1].parent.name == "nations"]
    idx += ["", f"## Nations ({len(nat)} files in `nations/`)", "",
            "One file per nation. Named by slug, e.g. `nations/ulm.md`.", ""]
    idx.append(", ".join(f"`{w[1].stem}`" for w in nat))

    idx += ["", "## Full section index", "",
            "Every outline entry, for locating a topic precisely.", ""]
    for e in entries:
        idx.append(f"{'  ' * e.depth}- {e.title} — p.{e.page + 1}")
    index_text = "\n".join(idx) + "\n"
    (args.out / "index.md").write_text(index_text, encoding="utf-8")

    total = sum(c for *_, c in written)
    print(f"\nwrote {len(written)} files to {args.out}")
    print(f"  sections: {len(written) - len(nat)}   nations: {len(nat)}")
    print(f"  curated total ~{total // 4:,} tokens; "
          f"index ~{len(index_text) // 4:,} tokens")
    print("\ncore chapters:")
    for title, path, lo, hi, chars in written:
        if title in CORE_CHAPTERS:
            print(f"  {title:14s} p{lo + 1:3d}-{hi:3d}  ~{chars // 4:6,} tok  "
                  f"{path.relative_to(args.out).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
