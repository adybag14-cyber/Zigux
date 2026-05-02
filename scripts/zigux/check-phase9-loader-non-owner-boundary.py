#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"

SURFACES = [
    {
        "surface": "scripts/zigux/kconfig/conf_bridge.zig",
        "owning_phase": "Phase 2",
        "boundary_kind": "config_surface_bridge",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "scripts/zigux/kconfig/confdata_bridge.zig",
        "owning_phase": "Phase 2",
        "boundary_kind": "config_surface_bridge",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "rust/exports.c",
        "owning_phase": "Phase 3",
        "boundary_kind": "export_boundary",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
    {
        "surface": "zigux/kernel/export_shim.zig",
        "owning_phase": "Phase 3",
        "boundary_kind": "export_boundary",
        "why_non_owner_fragment": "boundary reference instead of Phase 9 runtime evidence",
    },
]

REVIEW_CHECKLIST_LINE = (
    "if the change touches the shared Phase 9 runtime-loader evidence packet, do "
    "`scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, "
    "`rust/exports.c`, and `zigux/kernel/export_shim.zig` still stay explicit as "
    "Phase 2 or Phase 3 non-owner references instead of being silently counted as "
    "Phase 9 runtime evidence?"
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    survey_text = read_text(root, SURVEY_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    manifest = json.loads(read_text(root, MANIFEST_PATH))

    manifest_surfaces = manifest.get("non_owner_surfaces")
    if not isinstance(manifest_surfaces, list):
        return ["manifest:non_owner_surfaces_missing"]

    if len(manifest_surfaces) != len(SURFACES):
        failures.append(
            f"manifest:non_owner_surface_count:{len(manifest_surfaces)}"
        )

    for index, expected in enumerate(SURFACES):
        if index >= len(manifest_surfaces):
            failures.append(f"manifest:missing_surface:{expected['surface']}")
            continue

        actual = manifest_surfaces[index]
        for field in ("surface", "owning_phase", "boundary_kind"):
            if actual.get(field) != expected[field]:
                failures.append(
                    f"manifest:{expected['surface']}:{field}:{actual.get(field)!r}"
                )
        why_non_owner = actual.get("why_non_owner")
        if not isinstance(why_non_owner, str) or expected[
            "why_non_owner_fragment"
        ] not in why_non_owner:
            failures.append(f"manifest:{expected['surface']}:why_non_owner")

        if expected["surface"] not in survey_text:
            failures.append(f"survey:{expected['surface']}")

    if REVIEW_CHECKLIST_LINE not in review_checklist:
        failures.append("review_checklist:four_surface_non_owner_line")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)

    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Loader Gap Survey",
                "scripts/zigux/kconfig/conf_bridge.zig",
                "scripts/zigux/kconfig/confdata_bridge.zig",
                "rust/exports.c",
                "zigux/kernel/export_shim.zig",
                "boundary references instead of Phase 9 runtime evidence",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / REVIEW_CHECKLIST_PATH).write_text(
        "# Zigux Review Checklist\n\n- " + REVIEW_CHECKLIST_LINE + "\n",
        encoding="utf-8",
    )
    (root / MANIFEST_PATH).write_text(
        json.dumps(
            {
                "non_owner_surfaces": [
                    {
                        **surface,
                        "why_non_owner": (
                            f"{surface['surface']} stays as a "
                            f"{surface['why_non_owner_fragment']}."
                        ),
                    }
                    for surface in SURFACES
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_p9_non_owner_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline_failures = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(
                "phase9-loader-non-owner-selftest:baseline_failed:"
                + ",".join(baseline_failures)
            )

        review_path = tmp_root / REVIEW_CHECKLIST_PATH
        review_path.writeText("# Zigux Review Checklist\n", encoding="utf-8")
        failures = validate(tmp_root)
        if "review_checklist:four_surface_non_owner_line" not in failures:
            raise SystemExit(
                "phase9-loader-non-owner-selftest:expected_review_failure:"
                + ",".join(failures or ["none"])
            )

    print("PHASE9_LOADER_NON_OWNER_BOUNDARY_SELF_TEST=pass")
    print("PHASE9_LOADER_NON_OWNER_BOUNDARY_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Phase 9 runtime-loader packet's cross-phase "
            "non-owner config and export boundary."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in fixture-based self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_LOADER_NON_OWNER_BOUNDARY=fail")
        print("PHASE9_LOADER_NON_OWNER_BOUNDARY_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_LOADER_NON_OWNER_BOUNDARY_FAILURES_END")
        return 1

    print("PHASE9_LOADER_NON_OWNER_BOUNDARY=pass")
    print(f"PHASE9_LOADER_NON_OWNER_BOUNDARY_SURFACE_COUNT={len(SURFACES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
