#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS_README = Path("zigux/tests/README.md")

PHASE13_HEADING = "Phase 13 review packet"
PHASE13_SECTION_END = "Keep the shared validator-first release handle anchored to current repo reality:"

REQUIRED_MARKERS = (
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`fs/libfs.zig`",
    "`zigux/tests/phase13_libfs.zig`",
    "`zigux/tests/phase13_libfs_reviewability.zig`",
    "`zigux/tests/phase13_libfs_manifest.json`",
    "`lib/devres.zig`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_dma_coherent.zig`",
    "`zigux/tests/phase13_devres_boundary_evidence.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
    "`zigux/tests/phase13_landlock_ruleset.zig`",
    "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase13-validate`",
    "blocked convenience route `make -C zigux phase13`",
    "Current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py` or `Documentation/zigux/phase13-notifier-list-survey.md`",
)

FORBIDDEN_SHIPPED_LINES = (
    "- `Documentation/zigux/phase13-notifier-list-survey.md`",
    "- `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, rel_path: Path) -> Path:
    return root / rel_path


def extract_phase13_shipped_section(text: str) -> str:
    heading_index = text.find(PHASE13_HEADING)
    if heading_index == -1:
        raise SystemExit(f"missing heading: {PHASE13_HEADING}")
    end_index = text.find(PHASE13_SECTION_END, heading_index)
    if end_index == -1:
        raise SystemExit(f"missing section terminator: {PHASE13_SECTION_END}")
    return text[heading_index:end_index]


def collect_missing_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def collect_forbidden_markers(text: str) -> list[str]:
    section = extract_phase13_shipped_section(text)
    return [line for line in FORBIDDEN_SHIPPED_LINES if line in section]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    issues: list[tuple[str, str]] = []
    for marker in collect_missing_markers(tests_readme_text):
        issues.append(("MISSING_MARKER", marker))
    for marker in collect_forbidden_markers(tests_readme_text):
        issues.append(("FORBIDDEN_SHIPPED_MARKER", marker))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE13_TESTS_README_ALIGNMENT=fail")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_START")
    for code, value in issues:
        print(f"{code}:{value}")
    print("PHASE13_TESTS_README_ALIGNMENT_ISSUES_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    section_lines = [
        "# zigux/tests",
        "",
        "## Phase 13 review packet",
        "",
        "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:",
    ]
    section_lines.extend(f"- {marker}" for marker in REQUIRED_MARKERS[:-1])
    section_lines.append(f"Current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py` or `Documentation/zigux/phase13-notifier-list-survey.md`, so keep both paths framed as remaining shared-summary repo-reality gaps rather than as shipped tests-root evidence.")
    section_lines.append("")
    section_lines.append(PHASE13_SECTION_END)
    write_text(resolve_path(root, TESTS_README), "\n".join(section_lines) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 4
    with tempfile.TemporaryDirectory(prefix="zigux_p13_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve_path(root, TESTS_README)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), "`zigux/tests/phase13_devres_boundary_evidence.zig`"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MARKER", "`zigux/tests/phase13_devres_boundary_evidence.zig`") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(path.read_text(encoding="utf-8").replace("Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n", "Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:\n- `Documentation/zigux/phase13-notifier-list-survey.md`\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("FORBIDDEN_SHIPPED_MARKER", "- `Documentation/zigux/phase13-notifier-list-survey.md`") in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TESTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing tests readme did not abort")

    assert checks_run == expected_case_count
    print("PHASE13_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the current Phase 13 tests-root reminder packet aligned with shared-helper repo reality.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE13_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE13_TESTS_README_ALIGNMENT_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
