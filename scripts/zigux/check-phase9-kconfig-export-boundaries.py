#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"

DOCS_PHASE9_NON_OWNER_MARKER = (
    "- the same shared Phase 9 summary should keep the older non-owner boundaries explicit: "
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain "
    "Phase 2 config-surface bridge references, while `rust/exports.c` and "
    "`zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than "
    "runtime-pilot evidence."
)

REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER = (
    "the Phase 2 config-surface references `scripts/zigux/kconfig/conf_bridge.zig` and "
    "`scripts/zigux/kconfig/confdata_bridge.zig`, and the Phase 3 export-boundary references "
    "`rust/exports.c` and `zigux/kernel/export_shim.zig`"
)

LANE_SEQUENCING_PHASE2_MARKER = (
    "- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` "
    "remain Phase 2 config-surface bridge references"
)

LANE_SEQUENCING_PHASE3_MARKER = (
    "- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references"
)

REQUIRED_MARKERS = {
    DOCS_README_PATH: [DOCS_PHASE9_NON_OWNER_MARKER],
    REVIEW_CHECKLIST_PATH: [REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER],
    LANE_SEQUENCING_PATH: [LANE_SEQUENCING_PHASE2_MARKER, LANE_SEQUENCING_PHASE3_MARKER],
}

REQUIRED_EXACT_COUNTS = {
    DOCS_README_PATH: {DOCS_PHASE9_NON_OWNER_MARKER: 1},
    REVIEW_CHECKLIST_PATH: {REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER: 1},
    LANE_SEQUENCING_PATH: {
        LANE_SEQUENCING_PHASE2_MARKER: 1,
        LANE_SEQUENCING_PHASE3_MARKER: 1,
    },
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_MARKERS:
        file_path = root / rel_path
        if not file_path.exists():
            failures.append(f"missing_file:{rel_path}")
            continue

        text = read_text(root, rel_path)
        for marker in REQUIRED_MARKERS[rel_path]:
            if marker not in text:
                failures.append(f"{rel_path}:missing:{marker}")

        for marker, expected_count in REQUIRED_EXACT_COUNTS[rel_path].items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                failures.append(
                    f"{rel_path}:exact_count:{marker}:expected={expected_count}:actual={actual_count}"
                )

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    for rel_path, markers in REQUIRED_MARKERS.items():
        title = Path(rel_path).name
        write_text(root / rel_path, "\n".join([f"# {title}", *markers, ""]))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-kconfig-export-boundaries-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        docs_path = base / DOCS_README_PATH
        checklist_path = base / REVIEW_CHECKLIST_PATH
        lane_path = base / LANE_SEQUENCING_PATH

        docs_text = docs_path.read_text(encoding="utf-8")
        docs_path.write_text(docs_text.replace(DOCS_PHASE9_NON_OWNER_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"{DOCS_README_PATH}:missing:{DOCS_PHASE9_NON_OWNER_MARKER}")

        write_fixture_tree(base)
        docs_text = docs_path.read_text(encoding="utf-8")
        docs_path.write_text(docs_text + DOCS_PHASE9_NON_OWNER_MARKER + "\n", encoding="utf-8")
        expect_failure(
            base,
            f"{DOCS_README_PATH}:exact_count:{DOCS_PHASE9_NON_OWNER_MARKER}:expected=1:actual=2",
        )

        write_fixture_tree(base)
        checklist_text = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist_text.replace(REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"{REVIEW_CHECKLIST_PATH}:missing:{REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER}",
        )

        write_fixture_tree(base)
        checklist_text = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist_text + REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER + "\n",
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"{REVIEW_CHECKLIST_PATH}:exact_count:{REVIEW_CHECKLIST_PHASE9_BOUNDARY_MARKER}:expected=1:actual=2",
        )

        write_fixture_tree(base)
        lane_text = lane_path.read_text(encoding="utf-8")
        lane_path.write_text(lane_text.replace(LANE_SEQUENCING_PHASE2_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"{LANE_SEQUENCING_PATH}:missing:{LANE_SEQUENCING_PHASE2_MARKER}")

        write_fixture_tree(base)
        lane_text = lane_path.read_text(encoding="utf-8")
        lane_path.write_text(lane_text + LANE_SEQUENCING_PHASE2_MARKER + "\n", encoding="utf-8")
        expect_failure(
            base,
            f"{LANE_SEQUENCING_PATH}:exact_count:{LANE_SEQUENCING_PHASE2_MARKER}:expected=1:actual=2",
        )

        write_fixture_tree(base)
        lane_text = lane_path.read_text(encoding="utf-8")
        lane_path.write_text(lane_text.replace(LANE_SEQUENCING_PHASE3_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"{LANE_SEQUENCING_PATH}:missing:{LANE_SEQUENCING_PHASE3_MARKER}")

        write_fixture_tree(base)
        lane_text = lane_path.read_text(encoding="utf-8")
        lane_path.write_text(lane_text + LANE_SEQUENCING_PHASE3_MARKER + "\n", encoding="utf-8")
        expect_failure(
            base,
            f"{LANE_SEQUENCING_PATH}:exact_count:{LANE_SEQUENCING_PHASE3_MARKER}:expected=1:actual=2",
        )

        print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER_SELF_TEST=pass")
        print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER_SELF_TEST_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 9 Kconfig-versus-export non-owner boundary wording."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER=fail")
        print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER_FAILURES_END")
        return 1

    print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER=pass")
    print("PHASE9_KCONFIG_EXPORT_BOUNDARY_CHECKER_MARKER_COUNT=4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
