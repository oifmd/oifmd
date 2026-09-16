"""oifmd — validate and operate an OIF board with nothing but the filesystem.

Usage:
  oifmd validate [BOARD]          exit 0 if BOARD conforms to OIF 0.1
  oifmd ls [BOARD] [COLUMN]       list issues by column
  oifmd new BOARD COLUMN TITLE    create an issue with a fresh id, print its path
  oifmd id                        print a fresh id
  oifmd index [BOARD]             write an OKF-shaped root index.md
  oifmd about TARGET [BOARD]      list records about a path or resource
"""
from __future__ import annotations

import re
import secrets
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
ID_RE = r"[0-9a-hjkmnp-tv-z]{6}"
SLUG_RE = r"[a-z0-9]+(?:-[a-z0-9]+)*"
FILENAME_RE = re.compile(rf"^(?P<slug>{SLUG_RE})-(?P<id>{ID_RE})\.md$")
COLUMN_RE = re.compile(r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$")
KEY_RE = re.compile(r"^[a-z][a-z0-9]{1,15}$")
REF_RE = re.compile(rf"^(?:[a-z][a-z0-9]{{1,15}}-)?(?P<id>{ID_RE})$")
# Prose tokens may carry the slug: <key>-<slug>-<id>. Only key and id resolve
# (spec 5.1). Kept separate from REF_RE, which governs frontmatter values.
TOKEN_RE = re.compile(
    rf"(?<![a-z0-9-])(?P<key>[a-z][a-z0-9]{{1,15}})"
    rf"(?:-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*))?-(?P<id>{ID_RE})(?![a-z0-9-])")
COMMENT_RE = re.compile(
    r"^### (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2}))"
    r" (?P<actor>\S+)(?P<kv>(?: [a-z][a-z0-9_]*=[A-Za-z0-9_.:/@-]+)*)\s*$"
)
RESERVED = ("id", "status", "state", "column")
RESERVED_FILES = ("column.md", "index.md", "log.md")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
LIST_OF_STR = ("assignees", "tags", "aliases")
OFFSET_RE = re.compile(r"(?:Z|[+-]\d{2}:?\d{2})$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})$")
RESOURCE_RE = re.compile(rf"^oif:[a-z][a-z0-9]{{1,15}}/{ID_RE}$")
LIST_OF_REF = ("depends_on", "related")


def new_id() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(6))


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60].rstrip("-") or "issue"


@dataclass
class Finding:
    level: str  # "error" | "warn"
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level}: {self.path}: {self.message}"


@dataclass
class Issue:
    path: Path
    column: str
    slug: str
    id: str
    front: dict = field(default_factory=dict)
    body: str = ""


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter, body, error)."""
    if not text.startswith("---\n"):
        return None, text, "missing frontmatter"
    end = text.find("\n---\n", 4)
    if end < 0:
        if text.rstrip("\n").endswith("\n---"):
            end = len(text.rstrip("\n")) - 3
        else:
            return None, text, "unterminated frontmatter"
    raw = text[4:end]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:  # pragma: no cover - message passthrough
        return None, text, f"frontmatter is not valid YAML: {exc}"
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, text, "frontmatter must be a YAML mapping"
    return data, text[end + 5:], None


def load_board(root: Path) -> tuple[dict | None, list[Finding]]:
    findings: list[Finding] = []
    bm = root / "board.md"
    if not bm.is_file():
        return None, [Finding("error", str(bm), "board.md is required")]
    front, _, err = split_frontmatter(bm.read_text(encoding="utf-8"))
    if err:
        return None, [Finding("error", str(bm), err)]
    key = front.get("key")
    if front.get("type") != "board":
        findings.append(Finding("error", str(bm), "board.md must have type: board"))
    if str(front.get("oif", "")) != "0.1":
        findings.append(Finding("error", str(bm), "oif must be \"0.1\""))
    if key is not None and not (isinstance(key, str) and KEY_RE.match(key)):
        findings.append(Finding("error", str(bm), f"key {key!r} must match {KEY_RE.pattern}"))
    cols = front.get("columns")
    if not isinstance(cols, list) or not cols:
        findings.append(Finding("error", str(bm), "columns must be a non-empty list"))
        return front, findings
    names = []
    for c in cols:
        if not isinstance(c, dict) or "name" not in c:
            findings.append(Finding("error", str(bm), f"column entry {c!r} needs a name"))
            continue
        n = str(c["name"])
        if not COLUMN_RE.match(n):
            findings.append(Finding("error", str(bm), f"column name {n!r} must match {COLUMN_RE.pattern}"))
        if n in names:
            findings.append(Finding("error", str(bm), f"duplicate column {n!r}"))
        names.append(n)
    front["_column_names"] = names
    front["_complete"] = {str(c["name"]) for c in (front.get("columns") or [])
                          if isinstance(c, dict) and c.get("complete")}
    if key is None:
        findings.append(Finding("warn", str(bm),
            "board.md has no key: records cannot be referenced by token and have no resource (spec 5.1)"))
    cmode = front.get("comments", "sidecar")
    if cmode not in ("sidecar", "inline"):
        findings.append(Finding("error", str(bm), "comments must be 'sidecar' or 'inline'"))
    front["_comments_mode"] = cmode if cmode in ("sidecar", "inline") else "sidecar"
    kinds = front.get("kinds")
    if kinds is not None:
        if not isinstance(kinds, list) or not all(isinstance(k, dict) and "name" in k for k in kinds):
            findings.append(Finding("error", str(bm), "kinds must be a list of {name, contains?}"))
        else:
            front["_kinds"] = {str(k["name"]): [str(c) for c in (k.get("contains") or [])] for k in kinds}
            declared = set(front["_kinds"])
            for name, contains in front["_kinds"].items():
                for c in contains:
                    if c not in declared:
                        findings.append(Finding("error", str(bm),
                            f"kind {name!r} contains undeclared kind {c!r}"))
    return front, findings


def scan_issues(root: Path, board: dict) -> tuple[list[Issue], list[Finding]]:
    findings: list[Finding] = []
    issues: list[Issue] = []
    idir = root / "issues"
    if not idir.is_dir():
        return issues, [Finding("error", str(idir), "issues/ directory is required")]
    declared = set(board.get("_column_names", []))
    for name in sorted(declared):
        cm = idir / name / "column.md"
        if not (idir / name).is_dir():
            findings.append(Finding("error", str(idir / name), "declared column has no directory (add a column.md)"))
        elif not cm.is_file():
            findings.append(Finding("error", str(cm), "every column directory must contain column.md"))
        else:
            front, _, err = split_frontmatter(cm.read_text(encoding="utf-8"))
            if err:
                findings.append(Finding("error", str(cm), err))
            elif front.get("type") != "column":
                findings.append(Finding("error", str(cm), "column.md must have type: column"))
            elif any(k in front for k in ("wip", "complete", "hidden", "order")):
                findings.append(Finding("error", str(cm), "column config belongs in board.md, not column.md"))
    for col in sorted(p for p in idir.iterdir() if p.is_dir()):
        if col.name not in declared:
            findings.append(Finding("error", str(col), "directory is not a declared column"))
        for f in sorted(col.iterdir()):
            if f.name in RESERVED_FILES:
                if f.name == "index.md" and f.read_text(encoding="utf-8").startswith("---\n"):
                    findings.append(Finding("warn", str(f), "index.md inside a column must not carry frontmatter (OKF section 8)"))
                continue
            if f.is_dir():
                findings.append(Finding("error", str(f), "subdirectories inside a column are not allowed"))
                continue
            if f.suffix != ".md":
                findings.append(Finding("warn", str(f), "non-markdown file in a column is ignored"))
                continue
            m = FILENAME_RE.match(f.name)
            if not m:
                findings.append(Finding("error", str(f), "filename must be <slug>-<id>.md with a 6-char Crockford id"))
                continue
            issues.append(Issue(f, col.name, m["slug"], m["id"]))
    return issues, findings


def check_prose_tokens(text: str, p: str, key: str | None,
                       ids: set[str]) -> list[Finding]:
    """Spec 5.1: resolve on the id, ignore the slug entirely.

    A token naming this board whose id resolves to nothing is broken. A
    token whose slug has since changed is not: the slug is display, and a
    stale one is dropped rather than reported.
    """
    out: list[Finding] = []
    for m in TOKEN_RE.finditer(text):
        if key is None or m["key"] != key:
            continue
        if m["id"] not in ids:
            out.append(Finding("error", p,
                f"{m.group(0)} does not resolve within this board"))
    return out


def check_about(p: str, front: dict, required: bool, repo_root: Path | None = None) -> list[Finding]:
    """Validate the `about` key (spec 3.4)."""
    out: list[Finding] = []
    about = front.get("about")
    if about is None:
        if required:
            out.append(Finding("error", p, "a standalone comment must carry about (spec 4.4)"))
        return out
    if not isinstance(about, list) or not about:
        out.append(Finding("error", p, "about must be a non-empty list of targets"))
        return out
    for e in about:
        if not isinstance(e, dict):
            out.append(Finding("error", p, f"about entry {e!r} must be a mapping")); continue
        if not (e.get("path") or e.get("resource")):
            out.append(Finding("error", p, "each about entry needs path or resource"))
        c = e.get("commit")
        if c is not None and not (isinstance(c, str) and COMMIT_RE.match(c)):
            out.append(Finding("error", p, f"about commit {c!r} must be 7-40 hex characters"))
        # spec 8: a path naming nothing now, with no commit to resolve it from,
        # is a warning. Never an error: the target may live in another repository.
        path = e.get("path")
        if repo_root is not None and isinstance(path, str) and not e.get("repo") and c is None:
            if not (repo_root / path).exists():
                out.append(Finding("warn", p,
                    f"about path {path!r} does not exist at HEAD and carries no commit to resolve it from"))
    return out


def find_repo_root(start: Path) -> Path | None:
    for d in [start, *start.parents]:
        if (d / ".git").exists():
            return d
    return None


def check_comment_file(f: Path, standalone: bool, repo_root: Path | None = None) -> list[Finding]:
    out: list[Finding] = []
    p = str(f)
    front, _, err = split_frontmatter(f.read_text(encoding="utf-8"))
    if err:
        return [Finding("error", p, err)]
    if front.get("type") != "comment":
        out.append(Finding("error", p, "comment must have type: comment"))
    at = front.get("at")
    if at is None:
        out.append(Finding("error", p, "comment requires at"))
    elif isinstance(at, datetime):
        if at.tzinfo is None:
            out.append(Finding("error", p, "at must carry Z or a numeric offset"))
    elif not (isinstance(at, str) and TS_RE.match(at)):
        out.append(Finding("error", p, "at must be an ISO 8601 extended-form datetime with Z or a numeric offset"))
    if not isinstance(front.get("by"), str) or not front.get("by"):
        out.append(Finding("error", p, "comment requires by (an actor)"))
    out += check_about(p, front, required=standalone, repo_root=repo_root)
    return out


def check_comments_dir(root: Path, ids: set[str], repo_root: Path | None = None) -> list[Finding]:
    """Validate comments/ (spec 4.4): per-issue dirs and standalone files."""
    out: list[Finding] = []
    cdir = root / "comments"
    seen_comment_ids: set[str] = set()
    if not cdir.is_dir():
        return out
    for sub in sorted(p for p in cdir.iterdir()):
        if sub.is_file():
            if sub.name in ("index.md", "log.md"):
                continue
            if not re.fullmatch(rf"{ID_RE}\.md", sub.name):
                out.append(Finding("error", str(sub), "standalone comment filename must be <id>.md"))
                continue
            if sub.stem in ids:
                out.append(Finding("error", str(sub), f"id {sub.stem} is already an issue id"))
            if sub.stem in seen_comment_ids:
                out.append(Finding("error", str(sub), f"duplicate comment id {sub.stem}"))
            seen_comment_ids.add(sub.stem)
            out += check_comment_file(sub, standalone=True, repo_root=repo_root)
            continue
        if not re.fullmatch(ID_RE, sub.name):
            out.append(Finding("error", str(sub), f"{sub.name!r} is not an issue id"))
            continue
        if sub.name not in ids:
            out.append(Finding("error", str(sub), f"no issue with id {sub.name} on this board"))
            continue
        for f in sorted(sub.iterdir()):
            if f.name in ("index.md", "log.md"):
                continue
            if not re.fullmatch(rf"{ID_RE}\.md", f.name):
                out.append(Finding("error", str(f), "comment filename must be <id>.md with a 6-char id"))
                continue
            if f.stem in ids:
                out.append(Finding("error", str(f), f"id {f.stem} is already an issue id"))
            if f.stem in seen_comment_ids:
                out.append(Finding("error", str(f), f"duplicate comment id {f.stem}"))
            seen_comment_ids.add(f.stem)
            out += check_comment_file(f, standalone=False, repo_root=repo_root)
    return out


def check_issue(issue: Issue, ids: set[str], key: str | None = None,
                repo_root: Path | None = None, complete: set[str] | None = None) -> list[Finding]:
    p = str(issue.path)
    out: list[Finding] = []
    front, body, err = split_frontmatter(issue.path.read_text(encoding="utf-8"))
    if err:
        return [Finding("error", p, err)]
    issue.front, issue.body = front, body
    if front.get("type") != "issue":
        out.append(Finding("error", p, "frontmatter must have type: issue"))
    res = front.get("resource")
    if res is not None and not (isinstance(res, str) and RESOURCE_RE.match(res)):
        out.append(Finding("error", p, "resource must be oif:<key>/<id>"))
    elif isinstance(res, str) and not res.endswith("/" + issue.id):
        out.append(Finding("error", p, f"resource {res} does not end with this file's id {issue.id}"))
    out += check_about(p, front, required=False, repo_root=repo_root)
    res = front.get("resolution")
    if res is not None and complete is not None and issue.column not in complete:
        out.append(Finding("warn", p,
            f"resolution is set but {issue.column!r} is not a complete column (spec 3.2)"))
    if isinstance(res, str) and ("\n" in res or len(res) > 40):
        out.append(Finding("warn", p,
            "resolution should be a short token; put prose in a comment or the body (spec 3.2)"))
    for k in ("kind", "description", "priority"):
        if k in front and not isinstance(front[k], str):
            out.append(Finding("error", p, f"{k} must be a string"))
    for k in RESERVED:
        if k in front:
            out.append(Finding("error", p, f"reserved key {k!r} must not appear in frontmatter"))
    for k in LIST_OF_STR:
        v = front.get(k)
        if v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            out.append(Finding("error", p, f"{k} must be a list of strings"))
    for k in LIST_OF_REF:
        v = front.get(k)
        if v is None:
            continue
        if not isinstance(v, list):
            out.append(Finding("error", p, f"{k} must be a list of issue references"))
            continue
        for r in v:
            out.extend(_check_ref(p, k, r, ids, key))
    if front.get("parent") is not None:
        out.extend(_check_ref(p, "parent", front["parent"], ids, key))
    ext = front.get("external_ids")
    if ext is not None and not (isinstance(ext, dict) and all(isinstance(v, str) for v in ext.values())):
        out.append(Finding("error", p, "external_ids must be a map of string to string"))
    created = front.get("created")
    if created is not None:
        if isinstance(created, datetime):
            if created.tzinfo is None:
                out.append(Finding("error", p, "created must carry Z or a numeric offset"))
        elif not (isinstance(created, str) and TS_RE.match(created)):
            out.append(Finding("error", p, "created must be an ISO 8601 extended-form datetime with Z or a numeric offset"))
    if "title" not in front:
        out.append(Finding("warn", p, "title is recommended"))
    if key and "resource" not in front:
        out.append(Finding("warn", p, f"resource oif:{key}/{issue.id} is recommended"))
    out.extend(_check_comments(p, body))
    return out


def _check_ref(p: str, k: str, r, ids: set[str], key: str | None = None) -> list[Finding]:
    """Spec 5.1/8.6: a bare id, or a token whose key is this board's, must resolve."""
    if not isinstance(r, str) or not REF_RE.match(r):
        return [Finding("error", p, f"{k}: {r!r} is not an issue reference")]
    m = REF_RE.match(r)
    prefix = r.rsplit("-", 1)[0] if "-" in r else None
    local = prefix is None or (key is not None and prefix == key)
    if local and m["id"] not in ids:
        return [Finding("error", p, f"{k}: {r} does not resolve within this board")]
    return []


def _check_comments(p: str, body: str) -> list[Finding]:
    out: list[Finding] = []
    lines = body.splitlines()
    h2 = [(i, l) for i, l in enumerate(lines) if l.startswith("## ")]
    idx = [i for i, l in h2 if l.strip() == "## Comments"]
    if not idx:
        return out
    if len(idx) > 1:
        out.append(Finding("error", p, "more than one ## Comments section"))
    start = idx[0]
    if any(i > start for i, _ in h2):
        out.append(Finding("error", p, "## Comments must be the last level-2 section"))
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if l.startswith("### ") and not COMMENT_RE.match(l):
            out.append(Finding("error", p, f"line {i + 1}: comment heading does not match '### <timestamp> <actor> [k=v ...]'"))
    return out


def validate(root: Path) -> list[Finding]:
    board, findings = load_board(root)
    if board is None:
        return findings
    issues, more = scan_issues(root, board)
    findings += more
    seen: dict[str, Path] = {}
    for it in issues:
        if it.id in seen:
            findings.append(Finding("error", str(it.path), f"duplicate id {it.id} (also {seen[it.id]})"))
        seen[it.id] = it.path
    ids = set(seen)
    key = board.get("key") if isinstance(board.get("key"), str) else None
    repo_root = find_repo_root(root.resolve())
    for it in issues:
        findings += check_issue(it, ids, key, repo_root, board.get("_complete"))
    findings += check_comments_dir(root, ids, repo_root)
    for it in issues:
        findings += check_prose_tokens(it.body, str(it.path), key, ids)
    cdir = root / "comments"
    if cdir.is_dir():
        for f in sorted(cdir.rglob("*.md")):
            if f.name in RESERVED_FILES:
                continue
            _, body, err = split_frontmatter(f.read_text(encoding="utf-8"))
            if not err:
                findings += check_prose_tokens(body, str(f), key, ids)
    if board.get("_comments_mode") == "sidecar":
        for it in issues:
            if "\n## Comments" in it.body or it.body.startswith("## Comments"):
                findings.append(Finding("warn", str(it.path),
                    "inline ## Comments on a board declaring comments: sidecar (spec 4.3)"))
    kinds = board.get("_kinds")
    if kinds is not None:
        by_id = {it.id: it for it in issues}
        for it in issues:
            k = it.front.get("kind")
            if k is not None and k not in kinds:
                findings.append(Finding("error", str(it.path), f"kind {k!r} is not declared in board.md kinds"))
            parent = it.front.get("parent")
            if isinstance(parent, str) and k is not None:
                pm = REF_RE.match(parent)
                pit = by_id.get(pm["id"]) if pm else None
                if pit is not None:
                    pk = pit.front.get("kind")
                    if pk in kinds and k not in kinds[pk]:
                        findings.append(Finding("error", str(it.path), f"kind {k!r} may not be a child of {pk!r} (board.md kinds)"))
    return findings


def cmd_validate(root: Path) -> int:
    findings = validate(root)
    for f in findings:
        print(f)
    errors = sum(1 for f in findings if f.level == "error")
    n = sum(1 for f in (root / "issues").rglob("*.md") if f.name not in RESERVED_FILES) if (root / "issues").is_dir() else 0
    c = sum(1 for f in (root / "comments").rglob("*.md") if f.name not in RESERVED_FILES) if (root / "comments").is_dir() else 0
    print(f"{root}: {n} issue file(s), {c} comment file(s), {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


def cmd_ls(root: Path, column: str | None) -> int:
    board, findings = load_board(root)
    if board is None:
        print(findings[0]); return 1
    issues, _ = scan_issues(root, board)
    for col in board["_column_names"]:
        if column and col != column:
            continue
        rows = [i for i in issues if i.column == col]
        print(f"{col} ({len(rows)})")
        for i in rows:
            front, _, _ = split_frontmatter(i.path.read_text(encoding="utf-8"))
            title = (front or {}).get("title", i.slug)
            print(f"  {i.id}  {title}")
    return 0


def cmd_new(root: Path, column: str, title: str) -> int:
    board, findings = load_board(root)
    if board is None:
        print(findings[0]); return 1
    if column not in board["_column_names"]:
        print(f"error: {column!r} is not a declared column"); return 1
    d = root / "issues" / column
    d.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    iid = new_id()
    path = d / f"{slugify(title)}-{iid}.md"
    key = board.get("key")
    res = f"resource: oif:{key}/{iid}\n" if isinstance(key, str) else ""
    path.write_text(f"---\ntype: issue\n{res}title: {yaml.safe_dump(title).strip()}\ncreated: {now}\n---\n\n", encoding="utf-8")
    print(path)
    return 0


def cmd_index(root: Path) -> int:
    """Write an OKF-shaped root index.md linking board.md and every column.md."""
    board, findings = load_board(root)
    if board is None:
        print(findings[0]); return 1
    title = board.get("title") or "Board"
    lines = ['---', 'okf_version: "0.2"', '---', f"# {title}", "", "## Board", "",
             f"- [{title}](board.md) — columns, kinds and charter", "", "## Columns", ""]
    for col in board["_column_names"]:
        cm = root / "issues" / col / "column.md"
        desc = ""
        if cm.is_file():
            front, _, _ = split_frontmatter(cm.read_text(encoding="utf-8"))
            desc = (front or {}).get("description", "")
        lines.append(f"- [{col}](issues/{col}/column.md)" + (f" — {desc}" if desc else ""))
    (root / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(root / "index.md")
    return 0


def cmd_about(root: Path, target: str) -> int:
    """List records naming a target path (spec 5.2)."""
    hits = []
    for d in ("issues", "comments"):
        base = root / d
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*.md")):
            if f.name in RESERVED_FILES:
                continue
            front, _, err = split_frontmatter(f.read_text(encoding="utf-8"))
            if err or not front:
                continue
            for e in front.get("about") or []:
                if isinstance(e, dict) and (e.get("path") == target or e.get("resource") == target):
                    hits.append((f, front, e))
                    break
    for f, front, e in hits:
        where = f.parent.name if f.parent.parent.name == "issues" else "comment"
        label = front.get("title") or front.get("kind") or "comment"
        print(f"{f.stem.rsplit('-', 1)[-1]}  [{where}]  {label}"
              + (f"  @{e['commit']}" if e.get("commit") else ""))
    if not hits:
        print(f"no records about {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip()); return 0
    cmd, rest = args[0], args[1:]
    if cmd == "id":
        print(new_id()); return 0
    if cmd == "validate":
        return cmd_validate(Path(rest[0] if rest else "."))
    if cmd == "ls":
        return cmd_ls(Path(rest[0] if rest else "."), rest[1] if len(rest) > 1 else None)
    if cmd == "about":
        if not rest:
            print("usage: oifmd about TARGET [BOARD]"); return 2
        return cmd_about(Path(rest[1] if len(rest) > 1 else "."), rest[0])
    if cmd == "index":
        return cmd_index(Path(rest[0] if rest else "."))
    if cmd == "new":
        if len(rest) < 3:
            print("usage: oifmd new BOARD COLUMN TITLE"); return 2
        return cmd_new(Path(rest[0]), rest[1], " ".join(rest[2:]))
    print(f"unknown command {cmd!r}\n\n{__doc__.strip()}"); return 2
