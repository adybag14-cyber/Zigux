#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

NOTES_MARKERS = (
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

WORKFLOW_EXACT_COUNT_MARKERS = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, relative_path: Path) -> Path:
    try:
        return root / relative_path.relative_to(ROOT)
    except ValueError:
        return root / relative_path


def collect_missing(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_count(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in text.splitlines()]
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing(notes_text, NOTES_MARKERS, "MISSING_NOTES_MARKERS"))
    issues.extend(collect_missing(workflow_text, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKERS"))
    issues.extend(
        collect_exact_line_count(
            workflow_text,
            WORKFLOW_EXACT_COUNT_MARKERS,
            "EXACT_COUNT_WORKFLOW_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_STAGED_ARCHIVE_HELPER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")


def replace_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(NOTES_MARKERS) + len(WORKFLOW_MARKERS) + len(WORKFLOW_EXACT_COUNT_MARKERS) + 2

    with tempfile.TemporaryDirectory(prefix="phase2_staged_archive_helper_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_NOTES_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("EXACT_COUNT_WORKFLOW_MARKERS", f"2::{marker}") in collect_issues(root)
            checks_run += 1

        for rel_path in (PHASE2_NOTES, WORKFLOW):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_STAGED_ARCHIVE_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_STAGED_ARCHIVE_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 staged archive helper packet aligned between the bootstrap note and workflow."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_STAGED_ARCHIVE_HELPER_PACKET=pass")
    print(
        "PHASE2_STAGED_ARCHIVE_HELPER_PACKET_MARKER_COUNT="
        f"{len(NOTES_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    print(
        "PHASE2_STAGED_ARCHIVE_HELPER_PACKET_EXACT_COUNT_MARKER_COUNT="
        f"{len(WORKFLOW_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
