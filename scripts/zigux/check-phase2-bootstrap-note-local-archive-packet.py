#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
LOCAL_ARCHIVE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-local-archive-contract.md"

PHASE2_NOTES_MARKERS = (
    "`Documentation/zigux/phase2-local-archive-contract.md` and `scripts/zigux/check-phase2-local-archive-contract.py` keep the still-missing repo-local archive payload wording fail-closed: `third_party/README.md` owns the exact archive-path replay, while the broader Phase 2 reminder packet keeps `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` explicit until current `master` actually materializes `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`.",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
)

PHASE2_NOTES_EXACT_COUNT_MARKERS = (
    PHASE2_NOTES_MARKERS[0],
)

LOCAL_ARCHIVE_MARKERS = (
    "# Phase 2 Local Archive Contract",
    "`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` remain the current direct-readback anchors for the pinned archive contract, the local-first `third_party`, mirror, then direct-download bootstrap order, and the shipped Lane 05 reminder guards.",
    "`scripts/zigux/check-phase2-local-archive-contract.py` keeps this focused Phase 2 note fail-closed against current repo reality: when `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` is still absent it requires the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay, and it only allows the exact archive-path replay back into this note after that pinned payload lands on current `master`.",
    "current `master` still does not materialize `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, so keep the repo-local archive wording tied to `third_party/README.md`, the two Lane 05 reminder guards, and the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay until that pinned payload actually lands.",
)

LOCAL_ARCHIVE_EXACT_COUNT_MARKERS = (
    LOCAL_ARCHIVE_MARKERS[2],
    LOCAL_ARCHIVE_MARKERS[3],
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    phase2_notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    local_archive_text = read_text(resolve_path(root, LOCAL_ARCHIVE_NOTE))
    issues.extend(
        collect_missing_markers(
            phase2_notes_text,
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_exact_count_markers(
            phase2_notes_text,
            PHASE2_NOTES_EXACT_COUNT_MARKERS,
            "EXACT_COUNT_PHASE2_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            local_archive_text,
            LOCAL_ARCHIVE_MARKERS,
            "MISSING_LOCAL_ARCHIVE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_count_markers(
            local_archive_text,
            LOCAL_ARCHIVE_EXACT_COUNT_MARKERS,
            "EXACT_COUNT_LOCAL_ARCHIVE_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET=fail")
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
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, LOCAL_ARCHIVE_NOTE), "\n".join(LOCAL_ARCHIVE_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_all(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + 1
        + len(PHASE2_NOTES_MARKERS)
        + len(PHASE2_NOTES_EXACT_COUNT_MARKERS)
        + len(LOCAL_ARCHIVE_MARKERS)
        + len(LOCAL_ARCHIVE_EXACT_COUNT_MARKERS)
        + 2
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_local_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        repeated_marker = PHASE2_NOTES_MARKERS[0]
        repeated_text = "\n".join((repeated_marker, repeated_marker, "tail")) + "\n"
        replaced_text = replace_once(repeated_text, repeated_marker)
        assert replaced_text == f"\n{repeated_marker}\ntail\n"
        checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_NOTES_MARKERS", marker) in issues
            checks_run += 1

        for marker in PHASE2_NOTES_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_PHASE2_NOTES_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for marker in LOCAL_ARCHIVE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, LOCAL_ARCHIVE_NOTE)
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_LOCAL_ARCHIVE_MARKERS", marker) in issues
            checks_run += 1

        for marker in LOCAL_ARCHIVE_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, LOCAL_ARCHIVE_NOTE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_LOCAL_ARCHIVE_MARKERS", f"2::{marker}") in issues
            checks_run += 1

        for rel_path in (PHASE2_NOTES, LOCAL_ARCHIVE_NOTE):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, rel_path)) in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap-note local-archive packet aligned with the dedicated local-archive contract note."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET=pass")
    print(
        "PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_MARKER_COUNT="
        f"{len(PHASE2_NOTES_MARKERS) + len(LOCAL_ARCHIVE_MARKERS)}"
    )
    print(
        "PHASE2_BOOTSTRAP_NOTE_LOCAL_ARCHIVE_PACKET_EXACT_COUNT_MARKER_COUNT="
        f"{len(PHASE2_NOTES_EXACT_COUNT_MARKERS) + len(LOCAL_ARCHIVE_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
