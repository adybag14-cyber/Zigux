#!/usr/bin/env python3
"""Fail-close duplicate-sensitive Phase 3 low-level-wrapper reminder markers."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXACT_ONCE_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder plus directly readable interop-policy raw-pointer bridge entrypoints, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, and one returned shared Makefile replay gate",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/README.md, zigux/tests/build.zig, and zigux/Makefile; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the shared narrow-unsafe interop-policy bridge entrypoints, the dedicated build companion, the shared tests-root reminder, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gate while the adjacent catalog-selftest guard stays outside this wrapper packet",
        "## Adjacent Directly Readable Phase 3 Support",
        "`scripts/zigux/check-phase3-catalog-selftest.py`",
        "`make -C zigux phase3-low-level-wrappers-test`",
    ),
    TESTS_README_PATH: (
        "## Phase 3 shared substrate packet",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
    ),
    MAKEFILE_PATH: (
        "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
        "phase3-low-level-wrappers-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    WORKFLOW_PATH: (
        "      - name: Self-test current Phase 3 low-level wrapper survey validator",
        "      - name: Check current Phase 3 low-level wrapper survey packet",
        "      - name: Run current Phase 3 low-level wrapper replay",
        "        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
}

DUPLICATE_SELF_TEST_CASES = (
    (NOTE_PATH, "## Adjacent Directly Readable Phase 3 Support"),
    (TESTS_README_PATH, "`zigux/tests/phase3_low_level_wrappers_build.zig`"),
    (MAKEFILE_PATH, "phase3-low-level-wrappers-test:"),
    (
        WORKFLOW_PATH,
        "      - name: Run current Phase 3 low-level wrapper replay",
    ),
)

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in EXACT_ONCE_MARKERS.items()
    for marker in markers
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _populate_repo(root: Path) -> None:
    for relative_path, markers in EXACT_ONCE_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in EXACT_ONCE_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            count = text.count(marker)
            if count == 0:
                issues.append(f"missing {relative_path.as_posix()} exact marker: {marker}")
            elif count != 1:
                issues.append(
                    f"duplicate {relative_path.as_posix()} exact marker (count={count}): {marker}"
                )
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_exact_counts_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} exact marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST=fail")
                print(f"expected missing exact marker was not reported: {expected}")
                return 1

        for relative_path, marker in DUPLICATE_SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path) + marker + "\n")
            issues = validate_repo(root)
            expected = (
                f"duplicate {relative_path.as_posix()} exact marker (count=2): {marker}"
            )
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST=fail")
                print(f"expected duplicate exact marker was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST=pass")
    print(
        "PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SELF_TEST_CASE_COUNT="
        f"{len(SELF_TEST_CASES) + len(DUPLICATE_SELF_TEST_CASES) + 1}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate duplicate-sensitive Phase 3 low-level-wrapper packet markers."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level-wrapper packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS=pass")
    print("PHASE3_LOW_LEVEL_WRAPPER_EXACT_COUNTS_SCOPE=duplicate-sensitive-reminder-markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
