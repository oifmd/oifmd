"""The claim in SPEC.md section 7 is testable, so test it.

Two branches each add a comment to the same issue, with bodies that share
lines. In the comment-file form the merge keeps both comments whole. In
the inline form it does not, which is why section 4.4 is the default and
section 7.1 documents the hazard.

Run: python3 -m pytest tests/ -q     (or: python3 tests/test_concurrent_comments.py)
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

# bodies that share lines: the case that breaks inline appends
BODY_A = "Root cause identified.\n\nSteps:\n- reproduce\n- fix\n- test\n"
BODY_B = "Root cause identified.\n\nSteps:\n- reproduce\n- fix\n- test\n"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", *args],
        cwd=repo, capture_output=True, text=True,
    )


def new_repo(tmp: Path) -> Path:
    repo = tmp / "board"
    (repo / "issues" / "doing").mkdir(parents=True)
    (repo / "issues" / "doing" / "column.md").write_text(
        "---\ntype: column\ntitle: Doing\n---\n\nIn progress.\n")
    (repo / "board.md").write_text(
        '---\ntype: board\noif: "0.1"\nkey: app\ncolumns:\n  - name: doing\n---\n\nTest board.\n')
    (repo / "issues" / "doing" / "thing-abc123.md").write_text(
        "---\ntype: issue\ntitle: A thing\n---\n\nBody.\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    return repo


def branch_write(repo: Path, branch: str, path: str, text: str) -> None:
    git(repo, "checkout", "-q", "-b", branch, "main")
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists():
        f.write_text(f.read_text() + text)
    else:
        f.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", branch)


def test_comment_files_survive_a_concurrent_merge() -> None:
    """The default form (4.4): two branches, two files, nothing lost."""
    with tempfile.TemporaryDirectory() as td:
        repo = new_repo(Path(td))
        branch_write(repo, "a", "comments/abc123/aaa111.md",
                     f"---\ntype: comment\nat: 2026-09-15T10:00:00Z\nby: agent/alpha\n---\n\n{BODY_A}")
        branch_write(repo, "b", "comments/abc123/bbb222.md",
                     f"---\ntype: comment\nat: 2026-09-15T10:00:30Z\nby: agent/beta\n---\n\n{BODY_B}")
        git(repo, "checkout", "-q", "a")
        merge = git(repo, "merge", "b", "-m", "merge")

        assert merge.returncode == 0, f"merge should not conflict:\n{merge.stdout}{merge.stderr}"
        files = sorted(p.name for p in (repo / "comments" / "abc123").iterdir())
        assert files == ["aaa111.md", "bbb222.md"], files
        for name, actor in (("aaa111.md", "agent/alpha"), ("bbb222.md", "agent/beta")):
            text = (repo / "comments" / "abc123" / name).read_text()
            assert actor in text
            assert "Root cause identified." in text, f"{name} lost its body"


def test_inline_appends_lose_a_body_under_union_merge() -> None:
    """The hazard in 7.1, pinned so it cannot be quietly reintroduced."""
    with tempfile.TemporaryDirectory() as td:
        repo = new_repo(Path(td))
        (repo / ".gitattributes").write_text("issues/**/*.md merge=union\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "union")
        issue = "issues/doing/thing-abc123.md"
        (repo / issue).write_text((repo / issue).read_text() + "\n## Comments\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "comments section")
        git(repo, "branch", "-f", "main", "HEAD")

        branch_write(repo, "a", issue, f"\n### 2026-09-15T10:00:00Z agent/alpha\n\n{BODY_A}")
        branch_write(repo, "b", issue, f"\n### 2026-09-15T10:00:30Z agent/beta\n\n{BODY_B}")
        git(repo, "checkout", "-q", "a")
        git(repo, "merge", "b", "-m", "merge")

        merged = (repo / issue).read_text()
        assert merged.count("### ") == 2, "both headings should survive"
        # the shared body is emitted once: one comment's body is gone.
        assert merged.count("Root cause identified.") == 1, (
            "if this is 2, union merge no longer collapses shared lines and "
            "SPEC.md section 7.1 needs revisiting"
        )


if __name__ == "__main__":
    test_comment_files_survive_a_concurrent_merge()
    test_inline_appends_lose_a_body_under_union_merge()
    print("both properties hold: comment files merge cleanly, inline appends lose a body")
