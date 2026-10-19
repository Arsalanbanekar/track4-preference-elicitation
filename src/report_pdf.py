"""Render a Markdown report to PDF (Markdown -> styled HTML -> headless Chrome).

    python -m src.report_pdf REPORT_inbox_study.md

Images are embedded from the repository; links to repository files point to
their GitHub copies so they work from the PDF.
"""
import re, subprocess, sys, tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/Arsalanbanekar/track4-preference-elicitation/blob/agentic-inbox-study/"
CHROME = [Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
          Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")]

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
body { font-family: "Segoe UI", system-ui, sans-serif; font-size: 10pt; line-height: 1.5;
       color: #0b0b0b; background: #ffffff; }
h1 { font-size: 19pt; line-height: 1.25; margin: 0 0 6pt; }
h2 { font-size: 13pt; margin: 18pt 0 6pt; padding-top: 6pt; border-top: 1px solid #e1e0d9;
     break-after: avoid; }
h3 { font-size: 11pt; margin: 12pt 0 4pt; break-after: avoid; }
p, li { margin: 0 0 6pt; }
ul, ol { padding-left: 18pt; margin: 0 0 6pt; }
a { color: #1c5cab; text-decoration: none; }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: #f4f3f0; padding: 0 2pt;
       border-radius: 2pt; }
pre { background: #f4f3f0; padding: 6pt 8pt; border-radius: 3pt; font-size: 8.5pt; overflow: hidden;
      break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 8.8pt;
        break-inside: avoid; }
th { background: #f0efec; text-align: left; font-weight: 600; }
th, td { border: 1px solid #e1e0d9; padding: 3pt 5pt; vertical-align: top; }
img { display: block; max-width: 86%; max-height: 112mm; margin: 6pt auto 0; break-inside: avoid; }
em { color: #52514e; }
hr { display: none; }
strong { font-weight: 600; }
"""


def to_html(md_path):
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    # Images: absolute file URIs so Chrome can load them.
    body = re.sub(r'<img alt="([^"]*)" src="([^"]+)"',
                  lambda m: f'<img alt="{m.group(1)}" src="{(ROOT / m.group(2)).resolve().as_uri()}"', body)
    # Relative links to repository files: point to GitHub.
    body = re.sub(r'href="(?!https?://|#|mailto:)([^"]+)"', lambda m: f'href="{GITHUB}{m.group(1)}"', body)
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{CSS}</style></head><body>{body}</body></html>")


def main(md_name):
    md_path = (ROOT / md_name).resolve()
    out = md_path.with_suffix(".pdf")
    chrome = next((c for c in CHROME if c.exists()), None)
    if chrome is None:
        raise SystemExit("Chrome or Edge not found.")
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "report.html"
        html.write_text(to_html(md_path), encoding="utf-8")
        subprocess.run([str(chrome), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", html.as_uri()], check=True, capture_output=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "REPORT_inbox_study.md")
