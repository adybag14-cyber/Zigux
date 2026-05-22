#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LANE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-toolchain-lane-sequencing.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

REQUIRED_PATHS = (
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

REQUIRED_NOTE_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-cross`",
)

FORBIDDEN_NOTE_MARKERS = (
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = 17


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lane_note_text = read_text(resolve_path(root, LANE_NOTE))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in lane_note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    for marker in FORBIDDEN_NOTE_MARKERS:
        if marker in lane_note_text:
            issues.append(("FORBIDDEN_NOTE_MARKER", marker))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for rel_path in REQUIRED_PATHS:
        if not (root / rel_path).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel_path))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_note() -> str:
    markers = "\n".join(f"- {marker}" for marker in REQUIRED_NOTE_MARKERS)
    return (
        "# Phase 2 Toolchain Lane Sequencing\n\n"
        "## Owner Split\n\n"
        "Keep the current owner map explicit:\n"
        f"{markers}\n"
    )


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, LANE_NOTE), build_sample_note())
    write_text(resolve_path(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    for rel_path in REQUIRED_PATHS:
        write_text(root / rel_path, "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def write_sample_root(destination: Path) -> int:
    build_self_test_root(destination.resolve())
    print(f"PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_SAMPLE_ROOT={destination.resolve()}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane21_seq_note_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, LANE_NOTE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, LANE_NOTE)
        forbidden = FORBIDDEN_NOTE_MARKERS[0]
        path.write_text(path.read_text(encoding="utf-8") + f"\n- {forbidden}\n", encoding="utf-8")
        assert ("FORBIDDEN_NOTE_MARKER", forbidden) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_MAKEFILE_LINE",
            f"{REQUIRED_MAKEFILE_LINES[1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        missing_path = root / REQUIRED_PATHS[0]
        missing_path.unlink()
        assert ("MISSING_REQUIRED_PATH", REQUIRED_PATHS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, LANE_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing lane note did not abort")

        build_self_test_root(root)
        resolve_path(root, MAKEFILE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing makefile did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the corrected Phase 2 lane-sequencing shared-surface note against stale helper names."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing synthetic root for replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE=pass")
    print(f"PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_REQUIRED_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    print(f"PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_NOTE_MARKERS)}")
    print(f"PHASE2_CROSS_SEQUENCING_NOTE_SHARED_SURFACE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
