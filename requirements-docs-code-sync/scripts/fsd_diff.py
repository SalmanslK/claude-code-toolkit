"""Compare two FSD PDFs section by section.

Usage:
    python fsd_diff.py OLD.pdf NEW.pdf --out DIR [--pdftotext PATH]

Writes into DIR: old.txt / new.txt (pdftotext -raw), sections.txt (every body
heading whose line count or title changed) and body.diff (a unified diff of
the body with page numbers and table-of-contents lines stripped).

Why section sizes as well as a diff: a section growing from 1 line to 171
reads as an unremarkable run of additions in a diff, and a section that
shrank is nearly invisible. Measuring each heading's span catches both.
Expect the diff to be noisy — page breaks move paragraphs; read past them.
A table row that looks reordered is usually pdftotext, not the BA: confirm
against the Doc's own text (fsd_comments.py --out writes it) before
recording it as a change.
"""
import argparse
import os
import re
import subprocess
import sys

DEFAULT_PDFTOTEXT = r"C:\Program Files\Git\mingw64\bin\pdftotext.exe"
HEADING = re.compile(r"^(\d+(?:\.\d+)+)\.?\s+(\S.*)$")


def extract(pdftotext: str, pdf: str, dest: str) -> list:
    subprocess.run([pdftotext, "-raw", pdf, dest], check=True)
    return open(dest, encoding="utf-8", errors="replace").read().split("\n")


def is_toc(line: str) -> bool:
    return "...." in line or ". . ." in line


def sections(lines: list) -> dict:
    heads = [(i, m.group(1), m.group(2)[:60]) for i, line in enumerate(lines)
             if (m := HEADING.match(line.strip())) and not is_toc(line) and len(line) < 120]
    spans = {}
    for k, (start, number, title) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        spans[number] = (title, end - start)  # last occurrence wins: the body, not the TOC
    return spans


def body(lines: list) -> list:
    starts = [i for i, line in enumerate(lines) if re.match(r"^1\.?\s+Introduction", line.strip()) and not is_toc(line)]
    first = starts[-1] if starts else 0
    return [line for line in lines[first:] if not re.fullmatch(r"\s*\d+\s*|\f.*", line)]


def key(number: str) -> list:
    return [int(part) for part in number.split(".")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_pdf")
    parser.add_argument("new_pdf")
    parser.add_argument("--out", required=True)
    parser.add_argument("--pdftotext", default=DEFAULT_PDFTOTEXT)
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    old = extract(args.pdftotext, args.old_pdf, os.path.join(args.out, "old.txt"))
    new = extract(args.pdftotext, args.new_pdf, os.path.join(args.out, "new.txt"))
    pages_old, pages_new = sum(l.count("\f") for l in old), sum(l.count("\f") for l in new)

    a, b = sections(old), sections(new)
    report = [f"pages {pages_old} -> {pages_new}; lines {len(old)} -> {len(new)}", ""]
    for number in sorted(set(a) | set(b), key=key):
        title_a, size_a = a.get(number, ("-", 0))
        title_b, size_b = b.get(number, ("-", 0))
        if title_a != title_b or abs(size_a - size_b) >= 3:
            renamed = "" if title_a == title_b else f"  => {title_b!r}"
            report.append(f"{number:16} {size_a:5} -> {size_b:5}  {title_a!r}{renamed}")
    open(os.path.join(args.out, "sections.txt"), "w", encoding="utf-8").write("\n".join(report))

    old_body, new_body = os.path.join(args.out, "old-body.txt"), os.path.join(args.out, "new-body.txt")
    open(old_body, "w", encoding="utf-8").write("\n".join(body(old)))
    open(new_body, "w", encoding="utf-8").write("\n".join(body(new)))
    diff = subprocess.run(["git", "diff", "--no-index", "--unified=1", old_body, new_body],
                          capture_output=True, text=True, encoding="utf-8")
    open(os.path.join(args.out, "body.diff"), "w", encoding="utf-8").write(diff.stdout)

    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(report))
    print(f"\nbody.diff: {diff.stdout.count(chr(10))} lines in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
