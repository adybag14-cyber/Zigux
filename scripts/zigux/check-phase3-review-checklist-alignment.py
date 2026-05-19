#!/usr/bin/env python3
"""Fail-close the shared Phase 3 review-checklist reminder surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
VALIDATOR_SUPPORT_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 3 validator-support packet",
    "`Documentation/zigux/phase3-validator-support-surface.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase3-review-checklist-alignment.py`",
    "`scripts/zigux/check-phase3-selftest-surface.py`",
    "`scripts/zigux/check-phase3-dev-t-starter-packet.py`",
    "`scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`",
    "`scripts/zigux/check-phase3-policy-starter-packet.py`",
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "broader validator-support, export/UAPI survey, catalog, IDR, and IDA routes stay framed as repo-reality gaps rather than shipped tests-root evidence",
)

VALIDATOR_SUPPORT_MARKERS = (
    "# Phase 3 Validator Support Surface",
    "`zigux/tests/README.md` now keeps the returned packet-local export/UAPI survey note and validator explicit beside the starter, helper, policy, and layout-replay packet",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.",
    "`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.",
)

TESTS_README_MARKERS = (
    "## Phase 3 review packet",
    "`Documentation/zigux/phase3-validator-support-surface.md`",
    "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
    "`scripts/zigux/check-phase3-selftest-surface.py`",
    "`scripts/zigux/check-phase3-dev-t-starter-packet.py`",
    "`scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`",
    "`scripts/zigux/check-phase3-policy-starter-packet.py`",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
    "`Documentation/zigux/phase3-shared-reminder-gap.md` should remain the tracker for any later shared-summary follow-through",
    "broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(
        _check_markers(
            repo_root / REVIEW_CHECKLIST_PATH,
            REVIEW_CHECKLIST_MARKERS,
            "review checklist",
        )
    )
    issues.extend(
        _check_markers(
            repo_root / VALIDATOR_SUPPORT_PATH,
            VALIDATOR_SUPPORT_MARKERS,
            "validator-support note",
        )
    )
    issues.extend(
        _check_markers(
            repo_root / TESTS_README_PATH,
            TESTS_README_MARKERS,
            "tests README",
        )
    )
    return issues


def run_repo_check(repo_root: Path) -> int:
    issues = validate_repo(repo_root)
    if issues:
        print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT=fail")
        print("\n".join(issues))
        return 1
    print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT=pass")
    print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_FILE_COUNT=3")
    print(
        "PHASE3_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_MARKERS) + len(VALIDATOR_SUPPORT_MARKERS) + len(TESTS_README_MARKERS)}"
    )
    return 0


def _base_review_checklist() -> str:
    return """# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Scope

  * is the target phase named explicitly?
## Validation
  * if the change touches the shared Phase 3 validator-support packet, do `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase3-review-checklist-alignment.py`, `scripts/zigux/check-phase3-selftest-surface.py`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, `scripts/zigux/check-phase3-policy-starter-packet.py`, and `Documentation/zigux/phase3-export-uapi-boundary-survey.md` still agree on the bounded starter, helper, policy, and export/UAPI-layout reminder packet, while the broader validator-support, export/UAPI survey, catalog, IDR, and IDA routes stay framed as repo-reality gaps rather than shipped tests-root evidence?
"""


def _base_validator_support() -> str:
    return """# Phase 3 Validator Support Surface

`zigux/tests/README.md` now keeps the returned packet-local export/UAPI survey note and validator explicit beside the starter, helper, policy, and layout-replay packet, so keep any broader shared-summary follow-through parked unless a fresh reread reopens same-packet drift on current `master`.

`Documentation/zigux/phase3-shared-reminder-gap.md` now records the aligned docs-root and tests-root reminders together while keeping scripts-root inventory work separate.

`scripts/zigux/README.md` remains a separate scripts-root reminder surface and should be handled through its own inventory-truthfulness follow-up instead of through this validator-support note.
"""


def _base_tests_readme() -> str:
    return """# zigux/tests

## Phase 3 review packet

Keep the current bounded Phase 3 ABI/runtime tests-root reminder explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `scripts/zigux/check-phase3-selftest-surface.py` explicit as the shared Phase 3 reminder guard instead of letting the tests-root summary drift away from the bounded current-tree packet.

Current `master` keeps the tests-root Phase 3 reminder anchored to one bounded `dev_t` starter packet, one focused helper-local `err_ptr` / `xarray` slice, one focused helper-local policy slice, the returned packet-local export/UAPI survey note and validator, and the focused export/UAPI layout replay pair instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence.

Keep the current starter and helper packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `include/zigux/abi.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.

Keep the returned packet-local export/UAPI survey note and validator explicit through `Documentation/zigux/phase3-export-uapi-boundary-survey.md` and `scripts/zigux/validate-phase3-export-uapi-survey.py`, while `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/phase3_catalog.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` stay explicit as broader repo-reality gaps. `Documentation/zigux/phase3-shared-reminder-gap.md` should remain the tracker for any later shared-summary follow-through, and `scripts/zigux/README.md` should keep scripts-root inventory work separate from this tests-root reminder packet.
"""


def _populate_root(root: Path) -> None:
    _write(root / REVIEW_CHECKLIST_PATH, _base_review_checklist())
    _write(root / VALIDATOR_SUPPORT_PATH, _base_validator_support())
    _write(root / TESTS_README_PATH, _base_tests_readme())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_review_checklist_alignment_") as temp_dir:
        root = Path(temp_dir)
        _populate_root(root)

        if validate_repo(root):
            print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=fail")
            print("expected synthetic packet to validate")
            return 1

        cases_run = 1
        cases = (
            (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS[0], "expected checklist heading marker removal to fail"),
            (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS[-1], "expected checklist gap marker removal to fail"),
            (VALIDATOR_SUPPORT_PATH, VALIDATOR_SUPPORT_MARKERS[1], "expected validator-support reminder removal to fail"),
            (VALIDATOR_SUPPORT_PATH, VALIDATOR_SUPPORT_MARKERS[-1], "expected validator-support scripts-root boundary removal to fail"),
            (TESTS_README_PATH, TESTS_README_MARKERS[0], "expected tests heading removal to fail"),
            (TESTS_README_PATH, TESTS_README_MARKERS[3], "expected tests guard marker removal to fail"),
            (TESTS_README_PATH, TESTS_README_MARKERS[-1], "expected tests gap wording removal to fail"),
        )

        for rel_path, marker, message in cases:
            _populate_root(root)
            target = root / rel_path
            target.write_text(target.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            if not validate_repo(root):
                print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=fail")
                print(message)
                return 1
            cases_run += 1

        print("PHASE3_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE3_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases_run}")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-close the shared Phase 3 review-checklist reminder surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains Documentation/ and zigux/tests/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_repo_check(args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())