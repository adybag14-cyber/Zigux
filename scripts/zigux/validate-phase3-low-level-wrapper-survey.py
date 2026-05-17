#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level wrapper survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
ABI_SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
ATOMIC_PATH = Path("zigux/helpers/atomic.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, but current master now directly exposes one atomic helper shard, one shared narrow-unsafe decoder, this dedicated survey note, and a dedicated survey validator rather than the full helper trio and focused replay packet that earlier continuity notes described",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback on 2026-05-17 reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while repeated authenticated contents reads still return missing for zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, and zigux/tests/phase3_low_level_wrappers_build.zig",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through in survey-and-gap-accounting mode with the dedicated survey validator keeping the current atomic-plus-narrow reminder packet fail-closed until current master materializes one more bounded companion beside zigux/helpers/atomic.zig and zigux/unsafe/narrow.zig, with the next honest implementation step being either one directly readable barrier-or-mmio helper shard or one equally bounded focused replay companion",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
        "`zigux/helpers/atomic.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "It also now exposes the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, which keeps the current atomic-plus-narrow reminder surface fail-closed even while the broader wrapper family stays absent.",
        "Reviewers should treat the low-level wrapper family as partially materialized on current `master`: one atomic helper shard, the shared narrow-unsafe decoder, and the dedicated survey validator are directly readable, while the broader barrier, MMIO, and replay companions remain current repo-reality gaps.",
    ),
    ABI_SLICE_PATH: (
        "one adjacent low-level-wrapper reminder surface built around the surviving atomic helper shard, shared unsafe-scope decoder, and dedicated survey validator",
        "one adjacent low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, but it still lacks the broader shared Phase 3 ABI replay route, shared tests-root wiring for the policy packet, the full barrier-and-MMIO helper follow-through, the focused low-level-wrapper replay route, the broader export/UAPI layout family, and the wider shared validator packet that earlier shared reminders described",
        "and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while representative broader Phase 3 paths still remain absent, including zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/phase3_abi.zig, zigux/tests/phase3_abi_dump.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, and zigux/tests/phase3_export_uapi_layout.zig",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "Current `master` also separately exposes only a partial low-level-wrapper reminder surface through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`.",
        "the partial low-level-wrapper reminder surface built around `zigux/helpers/atomic.zig`, `zigux/unsafe/narrow.zig`, the dedicated survey note, and the dedicated survey validator;",
    ),
    ATOMIC_PATH: (
        "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {",
        'test "phase3 atomic helper keeps compare-exchange ordering rules explicit" {',
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        'test "phase3 narrow unsafe surface keeps the capability split explicit" {',
    ),
}

SELF_TEST_CASES = (
    (NOTE_PATH, "It also now exposes the dedicated survey validator through `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, which keeps the current atomic-plus-narrow reminder surface fail-closed even while the broader wrapper family stays absent."),
    (NOTE_PATH, "Reviewers should treat the low-level wrapper family as partially materialized on current `master`: one atomic helper shard, the shared narrow-unsafe decoder, and the dedicated survey validator are directly readable, while the broader barrier, MMIO, and replay companions remain current repo-reality gaps."),
    (ABI_SLICE_PATH, "and it separately reaches one adjacent low-level-wrapper reminder surface through Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/unsafe/narrow.zig, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py, while representative broader Phase 3 paths still remain absent, including zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/phase3_abi.zig, zigux/tests/phase3_abi_dump.zig, scripts/zigux/check-phase3-abi.py, scripts/zigux/validate-phase3.py, and zigux/tests/phase3_export_uapi_layout.zig"),
    (ABI_SLICE_PATH, "Current `master` also separately exposes only a partial low-level-wrapper reminder surface through `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/unsafe/narrow.zig`, and `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`."),
    (ATOMIC_PATH, "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {"),
    (NARROW_PATH, "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level wrapper survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level wrapper survey packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
