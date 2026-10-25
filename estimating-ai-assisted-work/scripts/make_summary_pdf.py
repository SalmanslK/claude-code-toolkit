#!/usr/bin/env python3
"""Turn an estimate summary (Markdown) into a clean A4 PDF.

Usage: python make_summary_pdf.py <summary.md> [<out.pdf>] [--title "Document title"]

Needs: Python 3, the `markdown` package (pip install markdown), and Microsoft Edge or Google Chrome
(used headless to print the PDF). Falls back to writing the HTML next to the PDF if no browser is found.

Formatting rules baked in (learned from a client summary):
- a blank line is inserted between a bold lead-in line and the list under it, so lists do not merge into one paragraph;
- small tables never split across pages; the long work-breakdown table (its header starts "Work item") may split and repeats its header;
- the "## Files" section (local paths) is left out of the PDF;
- rows that are only "Backend" or "Web" in the first cell are shaded as section rows.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]

CSS = """@page{size:A4;margin:14mm}
body{font-family:Segoe UI,Arial,sans-serif;font-size:10pt;color:#1a1a1a;line-height:1.4}
h1{font-size:18pt;margin:0 0 6px}
h2{font-size:13pt;margin:13px 0 5px;border-bottom:1px solid #ccc;padding-bottom:2px;page-break-after:avoid}
table{border-collapse:collapse;width:100%;margin:6px 0;font-size:9.5pt}
th,td{border:1px solid #bbb;padding:3px 6px;text-align:left;vertical-align:top}
th{background:#eef1f5}tr{page-break-inside:avoid}thead{display:table-header-group}
table.keep{page-break-inside:avoid}td.sec{background:#f6f8fb}
li,p{orphans:3;widows:3}ol{page-break-inside:avoid}ul,ol{margin:4px 0 4px 18px;padding:0}"""


def find_browser():
    for b in BROWSERS:
        if os.path.isfile(b) or shutil.which(b):
            return b
    return None


def build_html(md_text, title):
    import markdown
    cut = md_text.find("\n## Files")
    if cut != -1:
        md_text = md_text[:cut]
    md_text = re.sub(r"(?m)^(\*\*[^\n]+\*\*)\n(?=[-*] |\d+\. )", r"\1\n\n", md_text)
    body = markdown.markdown(md_text, extensions=["tables"])
    body = re.sub(r"<table>(?![\s\S]{0,300}Work item)", '<table class="keep">', body)
    body = re.sub(r"<td><strong>(Backend|Web|Mobile)</strong></td>", r'<td class="sec"><strong>\1</strong></td>', body)
    return f"<!doctype html><meta charset='utf-8'><title>{title}</title><style>{CSS}</style>{body}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--title", default="Estimate summary")
    a = ap.parse_args()
    pdf = a.pdf or os.path.splitext(a.md)[0] + ".pdf"
    html = build_html(open(a.md, encoding="utf-8").read(), a.title)
    tmp = tempfile.mkdtemp()
    hp = os.path.join(tmp, "summary.html")
    open(hp, "w", encoding="utf-8").write(html)
    br = find_browser()
    if not br:
        alt = os.path.splitext(pdf)[0] + ".html"
        shutil.copy(hp, alt)
        sys.exit(f"No Edge or Chrome found. HTML written to {alt}; print it to PDF from a browser.")
    uri = "file:///" + hp.replace("\\", "/")
    subprocess.run([br, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(pdf)}", uri],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.isfile(pdf):
        sys.exit("The browser did not produce a PDF.")
    print(pdf)


if __name__ == "__main__":
    main()
