#!/usr/bin/env python3
"""Keep the top-level contributor onboarding packet aligned."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "CONTRIBUTING.md": [
        "`Documentation/zigux/contributor-entrypoints.md`",
        "`Documentation/zigux/contributor-workflow.md`",
        "Top-level onboarding guard: `python3 scripts/zigux/check-contributor-onboarding-packet.py`",
        "If you update the top-level contributor onboarding packet, rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py` so the start-here entrypoint, onboarding guide, and routine workflow note stay aligned.",
        "any top-level onboarding wording still agrees across `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and `Documentation/zigux/contributor-workflow.md`",
    ],
    "Documentation/zigux/contributor-entrypoints.md": [
        "### Top-Level Contributor Onboarding",
        "- `CONTRIBUTING.md`",
        "- `Documentation/zigux/contributor-entrypoints.md`",
        "- `Documentation/zigux/contributor-workflow.md`",
        "- `python3 scripts/zigux/check-contributor-onboarding-packet.py`",
        "if the change touches top-level onboarding wording, keep `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and `Documentation/zigux/contributor-workflow.md` aligned and rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py`",
    ],
    "Documentation/zigux/contributor-workflow.md": [
        "Use it with `CONTRIBUTING.md`, `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`, `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/contributor-entrypoints.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.",
        "for top-level contributor onboarding changes, rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py` so `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and this workflow note stay aligned",
        "- `CONTRIBUTING.md`: top-level contributor starting map and bounded onboarding reminders",
        "- `Documentation/zigux/contributor-entrypoints.md`: bounded guide selection for docs, checklist, and workflow work",
    ],
}

FORBIDDEN_MARKERS = (
    "Top-level onboarding guard: `make -C zigux contributor-onboarding`",
    "for top-level contributor onboarding changes, rerun `make -C zigux contributor-onboarding`",
    "treat public-tree fallback as direct current-master proof",
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
    script_path = root / "scripts/zigux/check-contributor-onboarding-packet.py"
    if not script_path.exists():
        issues.append("missing_file:scripts/zigux/check-contributor-onboarding-packet.py")

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
    print("CONTRIBUTOR_ONBOARDING_PACKET=fail")
    print("CONTRIBUTOR_ONBOARDING_PACKET_ISSUES_START")
    for issue in issues:
        print(issue)
    print("CONTRIBUTOR_ONBOARDING_PACKET_ISSUES_END")
    return 1


def populate_repo(root: Path) -> None:
    write_text(
        root,
        "scripts/zigux/check-contributor-onboarding-packet.py",
        "#!/usr/bin/env python3\nprint('placeholder')\n",
    )
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def expect_issue(issues: list[str], expected: str) -> None:
    assert expected in issues, f"missing expected issue: {expected}"


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="contributor-onboarding-packet-"))
    checks_run = 0
    try:
        populate_repo(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        (tempdir / "scripts/zigux/check-contributor-onboarding-packet.py").unlink()
        expect_issue(
            collect_issues(tempdir),
            "missing_file:scripts/zigux/check-contributor-onboarding-packet.py",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "CONTRIBUTING.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Top-level onboarding guard: `python3 scripts/zigux/check-contributor-onboarding-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:CONTRIBUTING.md:Top-level onboarding guard: `python3 scripts/zigux/check-contributor-onboarding-packet.py`",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/contributor-entrypoints.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "### Top-Level Contributor Onboarding\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/contributor-entrypoints.md:### Top-Level Contributor Onboarding",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/contributor-workflow.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `CONTRIBUTING.md`: top-level contributor starting map and bounded onboarding reminders\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "missing_marker:Documentation/zigux/contributor-workflow.md:- `CONTRIBUTING.md`: top-level contributor starting map and bounded onboarding reminders",
        )
        checks_run += 1

        populate_repo(tempdir)
        path = tempdir / "Documentation/zigux/contributor-workflow.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "for top-level contributor onboarding changes, rerun `make -C zigux contributor-onboarding`\n",
            encoding="utf-8",
        )
        expect_issue(
            collect_issues(tempdir),
            "forbidden_marker:Documentation/zigux/contributor-workflow.md:for top-level contributor onboarding changes, rerun `make -C zigux contributor-onboarding`",
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("CONTRIBUTOR_ONBOARDING_PACKET_SELF_TEST=pass")
    print(f"CONTRIBUTOR_ONBOARDING_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the top-level contributor onboarding packet aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("CONTRIBUTOR_ONBOARDING_PACKET=pass")
    print(f"CONTRIBUTOR_ONBOARDING_PACKET_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())