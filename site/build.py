#!/usr/bin/env python3
"""Build the oif.md site into docs/, generating everything from this repo.

Nothing here is hand-copied. The spec, the skill, the schemas and the
profiles are served verbatim from their source files, so the site cannot
drift from the specification it publishes.

    python3 site/build.py

GitHub Pages serves docs/ on the main branch. The CNAME makes that
oif.md.
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
SITE = "https://oif.md"

TAGLINE = "Issues and review comments as files, in any git repository, about anything in it."
SUBHEAD = (
    "An issue is a Markdown file; its directory is its status. A comment is a file "
    "nobody edits. No server, no account, nothing installed, and any agent can read "
    "the board cold."
)


def md_to_html(md: str) -> str:
    """A deliberately small Markdown subset: enough for the skill, no dependencies."""
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(block)) + "</code></pre>")
        elif re.match(r"^#{1,6} ", line):
            n = len(line) - len(line.lstrip("#"))
            text = inline(line[n:].strip())
            slug = re.sub(r"[^a-z0-9]+", "-", line[n:].strip().lower()).strip("-")
            out.append(f'<h{n} id="{slug}">{text}</h{n}>')
        elif re.match(r"^\s*[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(inline(re.sub(r"^\s*[-*] ", "", lines[i]))); i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            out.append(table(rows))
            continue
        elif line.strip() == "":
            pass
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6} |```|\||\s*[-*] )", lines[i]):
                para.append(lines[i]); i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            continue
        i += 1
    return "\n".join(out)


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(set(c) <= set("-: ") for c in r)]
    if not cells:
        return ""
    head, body = cells[0], cells[1:]
    h = "".join(f"<th>{inline(c)}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>"


CSS = """
:root{--ink:#2d2d2d;--amber:#e0a03c;--bg:#f9f5ea;--rule:#e2dccb;--mute:#6b6557}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.65 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:48rem;margin:0 auto;padding:3.5rem 1.5rem 6rem}
header{border-bottom:1px solid var(--rule);padding-bottom:2rem;margin-bottom:2.5rem}
h1{font-size:2.1rem;line-height:1.2;margin:0 0 .6rem;letter-spacing:-.01em}
h1 .md{color:var(--amber)}
.tag{font-size:1.15rem;margin:0 0 .8rem}
.sub{color:var(--mute);margin:0 0 1.6rem}
.btns{display:flex;gap:.6rem;flex-wrap:wrap}
.btn{display:inline-block;padding:.45rem .9rem;border:1px solid var(--ink);border-radius:5px;
 text-decoration:none;color:var(--ink);font-size:.92rem}
.btn:hover{background:var(--ink);color:var(--bg)}
h2{margin:2.6rem 0 .8rem;font-size:1.3rem;border-bottom:1px solid var(--rule);padding-bottom:.35rem}
h3{margin:1.8rem 0 .5rem;font-size:1.05rem}
code{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.88em;
 background:#efe9d8;padding:.1em .35em;border-radius:3px}
pre{background:#efe9d8;padding:.9rem 1.1rem;border-radius:6px;overflow-x:auto;border:1px solid var(--rule)}
pre code{background:none;padding:0;font-size:.85rem;line-height:1.55}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.93rem}
th,td{text-align:left;padding:.45rem .6rem;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:600}
a{color:#9a6b12}
ul{padding-left:1.25rem}
footer{margin-top:4rem;padding-top:1.5rem;border-top:1px solid var(--rule);
 color:var(--mute);font-size:.88rem}
@media(prefers-color-scheme:dark){
 :root{--ink:#e8e4d8;--bg:#1c1b18;--rule:#3a3730;--mute:#9b9585}
 code,pre{background:#26241f}
 .btn:hover{background:var(--ink);color:var(--bg)}
 a{color:var(--amber)}
}
"""


def page(title: str, body: str, desc: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE}/oif-header-1500x500.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/oif-avatar-32.png">
<link rel="apple-touch-icon" href="/oif-avatar-180.png">
<style>{CSS}</style>
<div class="wrap">
{body}
<footer>
Apache-2.0 &middot; <a href="https://github.com/oifmd/oifmd">github.com/oifmd/oifmd</a>
&middot; <a href="/SPEC.md">spec</a> &middot; <a href="/skill.md">skill</a>
&middot; <a href="/llms.txt">llms.txt</a>
</footer>
</div>
</html>
"""


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    spec = (ROOT / "SPEC.md").read_text()
    skill = (ROOT / "skill" / "SKILL.md").read_text()
    # strip the skill's YAML frontmatter for display; it is a harness header, not content
    skill_body = re.sub(r"^---\n.*?\n---\n", "", skill, count=1, flags=re.S)

    # raw files, served verbatim
    (OUT / "SPEC.md").write_text(spec)
    (OUT / "skill.md").write_text(skill)
    for d in ("schema", "profiles"):
        shutil.copytree(ROOT / d, OUT / d)
    for img in ("oif-avatar-32.png", "oif-avatar-180.png", "oif-avatar-192.png",
                "oif-avatar-512.png", "oif-header-1500x500.png"):
        shutil.copy(ROOT / "brand" / img, OUT / img)

    # the root page IS the instructions: an agent handed only this URL must be able to act
    header = f"""<header>
<h1>oif<span class="md">.md</span></h1>
<p class="tag"><strong>{html.escape(TAGLINE)}</strong></p>
<p class="sub">{html.escape(SUBHEAD)}</p>
<div class="btns">
<a class="btn" href="/SPEC.md">Specification</a>
<a class="btn" href="/skill.md">Skill for agents</a>
<a class="btn" href="https://github.com/oifmd/oifmd">GitHub</a>
</div>
</header>

<h2>Install the skill</h2>
<pre><code>mkdir -p .claude/skills/oif &amp;&amp; curl -fsSL https://oif.md/skill.md -o .claude/skills/oif/SKILL.md</code></pre>
<p>Nothing executes. It is a Markdown file, and it works the same in any
harness that reads the Agent Skills convention. To check a board against
the specification, <code>pip install oifmd</code> then
<code>oifmd validate &lt;board&gt;</code>.</p>

<h2>Everything an agent needs, below</h2>
<p>The rest of this page is the skill in full. An agent handed only this
URL can create a board, file an issue, move it, comment and close it
without fetching anything else.</p>
"""
    (OUT / "index.html").write_text(
        page("Open Issue Format", header + md_to_html(skill_body), TAGLINE))

    (OUT / "llms.txt").write_text(f"""# Open Issue Format (OIF)

> {TAGLINE}

An issue is a Markdown file whose directory is its workflow status. Its
filename carries a random six-character identity. Comments are
create-only files. Records may point at any path in the repository. A
board is also a conforming Open Knowledge Format bundle.

## Docs

- [Specification]({SITE}/SPEC.md): the normative document, RFC 2119 language
- [Agent skill]({SITE}/skill.md): how to create, move, comment on and close issues
- [Everything in one file]({SITE}/llms-full.txt): spec and skill concatenated

## Profiles

- [Kanban]({SITE}/profiles/kanban.md)
- [Scrum]({SITE}/profiles/scrum.md)
- [Shape Up]({SITE}/profiles/shape-up.md)

## Schemas

- [board.md]({SITE}/schema/board.schema.json)
- [issue]({SITE}/schema/issue.schema.json)
- [column.md]({SITE}/schema/column.schema.json)
- [comment]({SITE}/schema/comment.schema.json)
""")

    (OUT / "llms-full.txt").write_text(
        f"# Open Issue Format (OIF)\n\n> {TAGLINE}\n\n"
        f"Source: {SITE} — github.com/oifmd/oifmd — Apache-2.0\n\n"
        "=" * 72 + "\n# AGENT SKILL\n" + "=" * 72 + "\n\n" + skill_body +
        "\n\n" + "=" * 72 + "\n# SPECIFICATION\n" + "=" * 72 + "\n\n" + spec)

    (OUT / "CNAME").write_text("oif.md\n")
    (OUT / ".nojekyll").write_text("")          # serve _-prefixed paths and skip Jekyll
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{SITE}/{p}</loc></url>\n"
                  for p in ("", "SPEC.md", "skill.md", "llms.txt"))
        + "</urlset>\n")

    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"built {n} files into {OUT}")


if __name__ == "__main__":
    main()
