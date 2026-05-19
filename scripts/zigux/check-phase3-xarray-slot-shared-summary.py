#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
TESTS_README_REL = "zigux/tests/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
SLICE_NOTE_REL = "Documentation/zigux/phase3-xarray-slot-slice.md"
VALIDATOR_SUPPORT_REL = "Documentation/zigux/phase3-validator-support-surface.md"

CHECKER_REL = "scripts/zigux/check-phase3-xarray-slot-shared-summary.py"

HELPER_MARKER = "zigux/helpers/xarray_slot_view.zig"
STARTER_MARKER = "zigux/tests/phase3_xarray_slot_starter_packet.zig"
DUMP_MARKER = "zigux/tests/phase3_xarray_slot_dump.zig"
MANIFEST_MARKER = "zigux/tests/fixtures/phase3_xarray_slot_manifest.json"
STARTER_CHECKER_MARKER = "scripts/zigux/check-phase3-xarray-slot-starter-packet.py"
DUMP_CHECKER_MARKER = "scripts/zigux/check-phase3-xarray-slot.py"
STARTER_ROUTE_MARKER = "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig"
DUMP_ROUTE_MARKER = "zig build phase3-xarray-slot-dump --build-file zigux/tests/build.zig"
VALIDATE_PHASE3_MARKER = "scripts/zigux/validate-phase3.py"
README_INVENTORY_MARKER = "scripts/zigux/check-phase3-readme-tooling-inventory.py"
SLICE_NOTE_MARKER = "Documentation/zigux/phase3-xarray-slot-slice.md"
VALIDATOR_SUPPORT_MARKER = "Documentation/zigux/phase3-validator-support-surface.md"

REQUIRED_FILES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    SLICE_NOTE_REL,
    VALIDATOR_SUPPORT_REL,
)

FILE_MARKERS = {
    DOCS_README_REL: (
        "Phase 3 notes",
        HELPER_MARKER,
        STARTER_MARKER,
        DUMP_MARKER,
        MANIFEST_MARKER,
        STARTER_CHECKER_MARKER,
        DUMP_CHECKER_MARKER,
        SLICE_NOTE_MARKER,
    ),
    REVIEW_CHECKLIST_REL: (
        "shared Phase 3 xarray-slot packet",
        HELPER_MARKER,
        STARTER_MARKER,
        DUMP_MARKER,
        STARTER_CHECKER_MARKER,
        DUMP_CHECKER_MARKER,
        STARTER_ROUTE_MARKER,
        DUMP_ROUTE_MARKER,
        SLICE_NOTE_MARKER,
    ),
    TESTS_README_REL: (
        "Phase 3 shared substrate packet",
        HELPER_MARKER,
        STARTER_MARKER,
        DUMP_MARKER,
        MANIFEST_MARKER,
        STARTER_ROUTE_MARKER,
        DUMP_ROUTE_MARKER,
        SLICE_NOTE_MARKER,
    ),
    SCRIPTS_README_REL: (
        "Phase 3 flow",
        HELPER_MARKER,
        STARTER_MARKER,
        DUMP_MARKER,
        STARTER_CHECKER_MARKER,
        DUMP_CHECKER_MARKER,
        VALIDATE_PHASE3_MARKER,
        README_INVENTORY_MARKER,
        SLICE_NOTE_MARKER,
        VALIDATOR_SUPPORT_MARKER,
    ),
    SLICE_NOTE_REL: (
        CHECKER_REL,
        DOCS_README_REL,
        REVIEW_CHECKLIST_REL,
        TESTS_README_REL,
        SCRIPTS_README_REL,
        VALIDATOR_SUPPORT_MARKER,
    ),
    VALIDATOR_SUPPORT_REL: (
        README_INVENTORY_MARKER,
        VALIDATE_PHASE3_MARKER,
        HELPER_MARKER,
        STARTER_MARKER,
        DUMP_MARKER,
        STARTER_CHECKER_MARKER,
        DUMP_CHECKER_MARKER,
        SLICE_NOTE_MARKER,
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    for rel, markers in FILE_MARKERS.items():
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel}:missing:{marker}")

    return issues


def _seed(root: Path) -> None:
    _write(
        root / DOCS_README_REL,
        "\n".join(
            (
                "# docs",
                "Phase 3 notes",
                HELPER_MARKER,
                STARTER_MARKER,
                DUMP_MARKER,
                MANIFEST_MARKER,
                STARTER_CHECKER_MARKER,
                DUMP_CHECKER_MARKER,
                SLICE_NOTE_MARKER,
                "",
            )
        ),
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        "\n".join(
            (
                "# review",
                "shared Phase 3 xarray-slot packet",
                HELPER_MARKER,
                STARTER_MARKER,
                DUMP_MARKER,
                STARTER_CHECKER_MARKER,
                DUMP_CHECKER_MARKER,
                STARTER_ROUTE_MARKER,
                DUMP_ROUTE_MARKER,
                SLICE_NOTE_MARKER,
                "",
            )
        ),
    )
    _write(
        root / TESTS_README_REL,
        "\n".join(
            (
                "# tests",
                "Phase 3 shared substrate packet",
                HELPER_MARKER,
                STARTER_MARKER,
                DUMP_MARKER,
                MANIFEST_MARKER,
                STARTER_ROUTE_MARKER,
                DUMP_ROUTE_MARKER,
                SLICE_NOTE_MARKER,
                "",
            )
        ),
    )
    _write(
        root / SCRIPTS_README_REL,
        "\n".join(
            (
                "# scripts",
                "Phase 3 flow",
                HELPER_MARKER,
                STARTER_MARKER,
                DUMP_MARKER,
                STARTER_CHECKER_MARKER,
                DUMP_CHECKER_MARKER,
                VALIDATE_PHASE3_MARKER,
                README_INVENTORY_MARKER,
                SLICE_NOTE_MARKER,
                VALIDATOR_SUPPORT_MARKER,
                "",
            )
        ),
    )
    _write(
        root / SLICE_NOTE_REL,
        "\n".join(
            (
                "# slice",
                CHECKER_REL,
                DOCS_README_REL,
                REVIEW_CHECKLIST_REL,
                TESTS_README_REL,
                SCRIPTS_README_REL,
                VALIDATOR_SUPPORT_MARKER,
                "",
            )
        ),
    )
    _write(
        root / VALIDATOR_SUPPORT_REL,
        "\n".join(
            (
                "# validator support",
                README_INVENTORY_MARKER,
                VALIDATE_PHASE3_MARKER,
                HELPER_MARKER,
                STARTER_MARKER,
                DUMP_MARKER,
                STARTER_CHECKER_MARKER,
                DUMP_CHECKER_MARKER,
                SLICE_NOTE_MARKER,
                "",
            )
        ),
    )


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase3-xarray-slot-shared-summary-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_xarray_slot_shared_summary_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace(DUMP_CHECKER_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{DOCS_README_REL}:missing:{DUMP_CHECKER_MARKER}"],
            "docs_readme_missing_dump_checker",
        )
        _seed(root)
        case_count += 1

        path = root / REVIEW_CHECKLIST_REL
        _write(path, _read(path).replace(DUMP_ROUTE_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{REVIEW_CHECKLIST_REL}:missing:{DUMP_ROUTE_MARKER}"],
            "review_checklist_missing_dump_route",
        )
        _seed(root)
        case_count += 1

        path = root / TESTS_README_REL
        _write(path, _read(path).replace(MANIFEST_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{TESTS_README_REL}:missing:{MANIFEST_MARKER}"],
            "tests_readme_missing_manifest",
        )
        _seed(root)
        case_count += 1

        path = root / SCRIPTS_README_REL
        _write(path, _read(path).replace(VALIDATOR_SUPPORT_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{SCRIPTS_README_REL}:missing:{VALIDATOR_SUPPORT_MARKER}"],
            "scripts_readme_missing_validator_support_note",
        )
        _seed(root)
        case_count += 1

        path = root / SLICE_NOTE_REL
        _write(path, _read(path).replace(CHECKER_REL + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{SLICE_NOTE_REL}:missing:{CHECKER_REL}"],
            "slice_note_missing_checker",
        )
        _seed(root)
        case_count += 1

        path = root / VALIDATOR_SUPPORT_REL
        _write(path, _read(path).replace(DUMP_MARKER + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"{VALIDATOR_SUPPORT_REL}:missing:{DUMP_MARKER}"],
            "validator_support_missing_dump_packet",
        )
        _seed(root)
        case_count += 1

        (root / VALIDATOR_SUPPORT_REL).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{VALIDATOR_SUPPORT_REL}"],
            "missing_validator_support_file",
        )
        case_count += 1

    print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST=pass")
    print(f"PHASE3_XARRAY_SLOT_SHARED_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 3 xarray-slot shared summaries keep the helper, starter packet, "
            "dump parity packet, validator-support note, and shared route markers aligned across the "
            "docs-root, review-checklist, tests-root, scripts-root, and lane-note reminder surfaces."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY=fail")
        print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY_ISSUES_END")
        return 1

    print("PHASE3_XARRAY_SLOT_SHARED_SUMMARY=pass")
    print(f"PHASE3_XARRAY_SLOT_SHARED_SUMMARY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE3_XARRAY_SLOT_SHARED_SUMMARY_REQUIRED_MARKER_COUNT={sum(len(v) for v in FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
