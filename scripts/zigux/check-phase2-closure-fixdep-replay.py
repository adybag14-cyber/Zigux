#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
    "`zig test scripts/zigux/fixdep.zig`",
)

CLOSURE_EXACT_COUNT_MARKERS = (
    "`zig test scripts/zigux/fixdep.zig`",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/cases.json` keep the returned fixdep governance, parity, helper, and fixture packet explicit beside the reminder guards, and `make -C zigux phase2-fixdep` keeps its wrapper route inside the same returned make-wrapper packet.",
    "`zig test scripts/zigux/fixdep.zig`",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
)


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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    issues.extend(
        collect_missing_markers(
            closure_text,
            CLOSURE_MARKERS,
            "MISSING_CLOSURE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_count_markers(
            closure_text,
            CLOSURE_EXACT_COUNT_MARKERS,
            "EXACT_COUNT_CLOSURE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            notes_text,
            NOTES_MARKERS,
            "MISSING_NOTES_MARKERS",
        )
    )

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINES", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINES", f"{marker}:count={count}"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_FIXDEP_REPLAY=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")


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


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(CLOSURE_MARKERS) + len(CLOSURE_EXACT_COUNT_MARKERS) + len(NOTES_MARKERS) + 2 + 3
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_fixdep_replay_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in CLOSURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in CLOSURE_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("EXACT_COUNT_CLOSURE_MARKERS", f"2::{marker}") in collect_issues(root)
            checks_run += 1

        for marker in NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_NOTES_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), MAKEFILE_LINES[0]), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINES", MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[-1]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINES", f"{MAKEFILE_LINES[-1]}:count=2") in collect_issues(root)
        checks_run += 1

        for rel_path in (PHASE2_CLOSURE, PHASE2_NOTES, MAKEFILE):
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
    print("PHASE2_CLOSURE_FIXDEP_REPLAY_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_FIXDEP_REPLAY_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 closure note aligned with the live fixdep replay surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_FIXDEP_REPLAY=pass")
    print(f"PHASE2_CLOSURE_FIXDEP_REPLAY_CLOSURE_MARKER_COUNT={len(CLOSURE_MARKERS)}")
    print(f"PHASE2_CLOSURE_FIXDEP_REPLAY_CLOSURE_EXACT_COUNT_MARKER_COUNT={len(CLOSURE_EXACT_COUNT_MARKERS)}")
    print(f"PHASE2_CLOSURE_FIXDEP_REPLAY_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    print(f"PHASE2_CLOSURE_FIXDEP_REPLAY_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
