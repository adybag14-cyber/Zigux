#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")

REQUIRED_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "## Current repo-reality gaps",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "- Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, archive-verification, staged-helper, or direct cross-route surfaces from the current packet.",
    "## Follow-through",
    "- Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, archive-verification truthfulness, staged-archive helper truthfulness, third_party archive README truthfulness, required-make-routes truthfulness, kbuild-route reminders, docs-shared-reminder truthfulness, tests-root truthfulness, tool-manifest truthfulness, artifact-tools-manifest truthfulness, primary artifact-diff helper truthfulness, fixdep governance truthfulness, fixdep parity truthfulness, kconfig bridge alignment, or fixture-backed artifact-support.",
    "- Do not widen this note into genksyms parser behavior, conf or confdata bridge semantics, or deeper cross-target execution claims beyond the returned `phase2_cross_targets.json` packet unless current `master` materializes the companion wider surfaces and their reminder checks.",
)

EXACT_COUNT_MARKERS = (
    "## Current repo-reality gaps",
    "- No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
    "## Follow-through",
)

FORBIDDEN_MARKERS = (
    "historical packet members until same-lane work rematerializes them on `master`",
    "without reviving missing installer or direct cross-route proof text",
    "stay framed as repo-reality gaps",
)

SAMPLE_TEXT = "\n".join(REQUIRED_MARKERS) + "\n"


def resolve_root(root: Path) -> Path:
    return root.resolve()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_all(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(root / PHASE2_NOTES)
    issues: list[tuple[str, str]] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(("MISSING_MARKER", marker))
    for marker in EXACT_COUNT_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_MISMATCH", f"{count}::{marker}"))
    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            issues.append(("FORBIDDEN_MARKER", marker))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_FOLLOW_THROUGH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    write_text(root / PHASE2_NOTES, SAMPLE_TEXT)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(REQUIRED_MARKERS) + len(EXACT_COUNT_MARKERS) + len(FORBIDDEN_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_follow_through_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_MARKERS:
            write_sample_root(root)
            path = root / PHASE2_NOTES
            path.write_text(replace_all(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MARKER", marker) in issues
            checks_run += 1

        for marker in EXACT_COUNT_MARKERS:
            write_sample_root(root)
            path = root / PHASE2_NOTES
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("EXACT_COUNT_MISMATCH", f"2::{marker}") in issues
            checks_run += 1

        for marker in FORBIDDEN_MARKERS:
            write_sample_root(root)
            path = root / PHASE2_NOTES
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_MARKER", marker) in issues
            checks_run += 1

        write_sample_root(root)
        (root / PHASE2_NOTES).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing file did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_FOLLOW_THROUGH_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_FOLLOW_THROUGH_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap note no-gap and follow-through boundary aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for focused checker replay",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_FOLLOW_THROUGH_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(resolve_root(args.root))
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_FOLLOW_THROUGH=pass")
    print(f"PHASE2_BOOTSTRAP_FOLLOW_THROUGH_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_FOLLOW_THROUGH_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_FOLLOW_THROUGH_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
