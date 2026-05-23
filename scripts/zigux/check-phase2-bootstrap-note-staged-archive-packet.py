#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
NOTE = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "third_party/README.md",
)

REQUIRED_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
)

FORBIDDEN_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
)

EXACT_COUNT_MARKERS = (
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "returned archive-verification and staged-archive helper packet",
    "archive-verification truthfulness, staged-archive helper truthfulness",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(root / NOTE.relative_to(ROOT))

    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    for marker in REQUIRED_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_MARKER", marker))

    for marker in FORBIDDEN_MARKERS:
        if marker in note_text:
            issues.append(("FORBIDDEN_MARKER", marker))

    for marker in EXACT_COUNT_MARKERS:
        count = note_text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_MARKER", f"{count}::{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root / NOTE.relative_to(ROOT), "\n".join(REQUIRED_MARKERS) + "\n")
    for rel in REQUIRED_PATHS:
        if rel == "Documentation/zigux/phase2-toolchain-bootstrap-notes.md":
            continue
        write_text(resolve(root, rel), "present\n")


def run_self_test() -> int:
    checks = 0
    expected = 1 + len(REQUIRED_MARKERS) + len(FORBIDDEN_MARKERS) + len(EXACT_COUNT_MARKERS) + len(REQUIRED_PATHS)
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_stage_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in FORBIDDEN_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            note_path = root / NOTE.relative_to(ROOT)
            note_path.write_text(note_path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("EXACT_COUNT_MARKER", f"2::{marker}") in collect_issues(root)
            checks += 1

        for rel in REQUIRED_PATHS:
            if rel == "Documentation/zigux/phase2-toolchain-bootstrap-notes.md":
                continue
            build_self_test_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_PATH", rel) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        (root / NOTE.relative_to(ROOT)).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing note did not abort")

    assert checks == expected, (checks, expected)
    print("PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap note aligned to the returned staged-archive helper packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_NOTE_STAGED_ARCHIVE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
