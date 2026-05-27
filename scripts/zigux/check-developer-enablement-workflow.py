#!/usr/bin/env python3
"""Keep the developer-enablement contributor workflow packet aligned."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/contributor-entrypoints.md": [
        "### Developer Enablement Reminder Work",
        "Use `Documentation/zigux/developer-enablement-contributor-workflow.md` when the change stays inside docs-only reminder work, checklist maintenance, or contributor workflow guidance and does not reopen implementation lanes.",
        "- `python3 scripts/zigux/check-developer-enablement-workflow.py`",
        "2. reread one phase-local guide or `Documentation/zigux/developer-enablement-contributor-workflow.md` that matches the actual change",
    ],
    "Documentation/zigux/developer-enablement-contributor-workflow.md": [
        "Use it with `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "Matching guard: `python3 scripts/zigux/check-developer-enablement-workflow.py`",
        "6. if the change touches this guide or its contributor-entrypoint handoff, rerun `python3 scripts/zigux/check-developer-enablement-workflow.py`",
        "If no checker exists, keep the change docs-only unless adding a new checker is clearly the smallest honest way to keep the workflow trustworthy.",
    ],
    "Documentation/zigux/contributor-workflow.md": [
        "Use it with `CONTRIBUTING.md`, `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`, `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/developer-enablement-contributor-workflow.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "- for docs-only reminder, checklist, or contributor workflow guidance changes, rerun `python3 scripts/zigux/check-developer-enablement-workflow.py` so `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/developer-enablement-contributor-workflow.md`, and this workflow note keep the same docs-only handoff",
        "- `Documentation/zigux/developer-enablement-contributor-workflow.md`: docs-only reminder, checklist, and contributor workflow guidance handoff",
    ],
}

FORBIDDEN_MARKERS = (
    "Matching guard: `make -C zigux developer-enablement`",
    "promote public-tree fallback into current-head proof",
)


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    script_path = root / "scripts/zigux/check-developer-enablement-workflow.py"
    if not script_path.exists():
        issues.append("missing_file:scripts/zigux/check-developer-enablement-workflow.py")

    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("DEVELOPER_ENABLEMENT_WORKFLOW=fail")
    print("DEVELOPER_ENABLEMENT_WORKFLOW_ISSUES_START")
    for issue in issues:
        print(issue)
    print("DEVELOPER_ENABLEMENT_WORKFLOW_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(
        root,
        "scripts/zigux/check-developer-enablement-workflow.py",
        "#!/usr/bin/env python3\nprint('placeholder')\n",
    )
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="developer-enablement-workflow-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "scripts/zigux/check-developer-enablement-workflow.py").unlink()
        expect_issue(
            collect_issues(tempdir),
            "missing_file:scripts/zigux/check-developer-enablement-workflow.py",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/contributor-entrypoints.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `python3 scripts/zigux/check-developer-enablement-workflow.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/contributor-entrypoints.md:- `python3 scripts/zigux/check-developer-enablement-workflow.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/developer-enablement-contributor-workflow.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Matching guard: `python3 scripts/zigux/check-developer-enablement-workflow.py`\n",
                "Matching guard: `make -C zigux developer-enablement`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "forbidden_marker:Documentation/zigux/developer-enablement-contributor-workflow.md:Matching guard: `make -C zigux developer-enablement`",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/contributor-workflow.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `Documentation/zigux/developer-enablement-contributor-workflow.md`: docs-only reminder, checklist, and contributor workflow guidance handoff\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/contributor-workflow.md:- `Documentation/zigux/developer-enablement-contributor-workflow.md`: docs-only reminder, checklist, and contributor workflow guidance handoff",
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("DEVELOPER_ENABLEMENT_WORKFLOW_SELF_TEST=pass")
    print(f"DEVELOPER_ENABLEMENT_WORKFLOW_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the developer-enablement contributor workflow packet aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("DEVELOPER_ENABLEMENT_WORKFLOW=pass")
    print(f"DEVELOPER_ENABLEMENT_WORKFLOW_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())