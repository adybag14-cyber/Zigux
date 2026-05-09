#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=docs_root_smoke_summary

Fail-closed checker for the docs-root summary of the shared Phase 14 smoke packet.
This checker keeps `Documentation/zigux/README.md` aligned with the compact
study-only replay route, the shared smoke note, and the manifest-backed checker
inventory without demanding every anchor-local manifest from the docs root.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=docs_root_smoke_summary"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
SMOKE_SURVEY_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
MAKEFILE_PATH = "zigux/Makefile"
MANIFEST_PATH = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
CHECKER_PATH = "scripts/zigux/check-phase14-docs-root-smoke-summary.py"

COMPILE_SHARD_SMOKE_MARKERS = [
    "PHASE14_COMPILE_ARTIFACT_COUNT=6",
    "PHASE14_FOCUSED_SHARD_COUNT=1",
    "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=5",
    "- `phase14-workqueue-bridge-tests`: root `phase14_workqueue_bridge.zig`, coverage `full_bundle_only`",
    "- `phase14-workqueue-reviewability-tests`: root `phase14_workqueue_reviewability.zig`, coverage `full_bundle_only`",
    "- `phase14-skbuff-bridge-tests`: root `phase14_skbuff_bridge.zig`, coverage `full_bundle_only`",
    "- `phase14-ring-buffer-survey-tests`: root `phase14_ring_buffer_survey.zig`, coverage `full_bundle_only`",
    "- `phase14-rcu-tree-survey-tests`: root `phase14_rcu_tree_survey.zig`, coverage `full_bundle_only`",
    "- `phase14-end-to-end-smoke-tests`: root `phase14_end_to_end_smoke_survey.zig`, coverage `focused_and_full_bundle`",
]

SURFACE_COUNT_SMOKE_MARKERS = [
    "PHASE14_SHARED_SURFACE_COUNT=29",
    "PHASE14_DOC_SURFACE_COUNT=6",
    "PHASE14_SCRIPT_SURFACE_COUNT=5",
    "PHASE14_TEST_SURFACE_COUNT=13",
    "PHASE14_BRIDGE_ROOT_SURFACE_COUNT=3",
    "PHASE14_WORKFLOW_SURFACE_COUNT=1",
    "PHASE14_MAKEFILE_SURFACE_COUNT=1",
]

DOCS_ROOT_REQUIRED_MARKERS = [
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/validate-phase14.py",
    CHECKER_PATH,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge.zig",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_survey.zig",
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/Makefile",
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]

DOCS_ROOT_EXACT_COUNT_MARKERS = [
    CHECKER_PATH,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]

SMOKE_SURVEY_REQUIRED_MARKERS = [
    CHECKER_PATH,
    "Use the attached-toolchain fallback only when `zig` is not already on `PATH`.",
    "make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig",
    *COMPILE_SHARD_SMOKE_MARKERS,
    *SURFACE_COUNT_SMOKE_MARKERS,
]

SMOKE_SURVEY_EXACT_COUNT_MARKERS = [
    CHECKER_PATH,
    "Use the attached-toolchain fallback only when `zig` is not already on `PATH`.",
    "make -C zigux phase14-validate ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14-test ZIG=/absolute/path/to/attached-zig/zig",
    "make -C zigux phase14 ZIG=/absolute/path/to/attached-zig/zig",
    "PHASE14_COMPILE_ARTIFACT_COUNT=6",
    "PHASE14_FOCUSED_SHARD_COUNT=1",
    "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=5",
    *SURFACE_COUNT_SMOKE_MARKERS,
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_marker_count(errors: list[str], rel_path: str, text: str, marker: str) -> None:
    count = text.count(marker)
    if count != 1:
        errors.append(f"marker count drift in {rel_path}: {marker} (expected 1, found {count})")


def collect_checker_surfaces(errors: list[str], surfaces: object) -> list[dict[str, str]]:
    if not isinstance(surfaces, list):
        errors.append("phase14 shared smoke manifest surfaces payload is not a list")
        return []

    checker_surfaces: list[dict[str, str]] = []
    for surface in surfaces:
        if not isinstance(surface, dict):
            errors.append("phase14 shared smoke manifest surface entry is not an object")
            continue
        path = surface.get("path")
        if not isinstance(path, str):
            errors.append("phase14 shared smoke manifest surface entry is missing a string path")
            continue
        if path != CHECKER_PATH:
            continue
        required_marker = surface.get("required_marker")
        if not isinstance(required_marker, str):
            errors.append(
                "phase14 docs-root smoke-summary checker surface is missing a string required_marker "
                f"in {MANIFEST_PATH}"
            )
            continue
        checker_surfaces.append({"path": path, "required_marker": required_marker})
    return checker_surfaces


def check_manifest(errors: list[str], root: Path) -> None:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        errors.append(f"missing file: {MANIFEST_PATH}")
        return
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {MANIFEST_PATH}: {exc}")
        return
    checker_surfaces = collect_checker_surfaces(errors, manifest.get("surfaces"))
    if errors:
        return
    if len(checker_surfaces) != 1:
        errors.append(
            "phase14 docs-root smoke-summary checker surface count drift in "
            f"{MANIFEST_PATH} (expected 1, found {len(checker_surfaces)})"
        )
        return
    if checker_surfaces[0]["required_marker"] != MARKER:
        errors.append(
            "missing docs-root smoke-summary checker surface in zigux/tests/phase14_end_to_end_smoke_manifest.json"
        )


def check_text_file(
    errors: list[str],
    root: Path,
    rel_path: str,
    required_markers: list[str],
    exact_count_markers: list[str],
) -> None:
    path = root / rel_path
    if not path.exists():
        errors.append(f"missing file: {rel_path}")
        return
    text = read_text(path)
    for marker in required_markers:
        if marker not in text:
            errors.append(f"missing marker in {rel_path}: {marker}")
    for marker in exact_count_markers:
        require_exact_marker_count(errors, rel_path, text, marker)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")

    check_text_file(errors, root, DOCS_ROOT_PATH, DOCS_ROOT_REQUIRED_MARKERS, DOCS_ROOT_EXACT_COUNT_MARKERS)
    check_text_file(errors, root, SMOKE_SURVEY_PATH, SMOKE_SURVEY_REQUIRED_MARKERS, SMOKE_SURVEY_EXACT_COUNT_MARKERS)
    check_text_file(errors, root, MAKEFILE_PATH, [CHECKER_PATH], [CHECKER_PATH])
    check_manifest(errors, root)
    return errors


def good_manifest_text() -> str:
    return json.dumps(
        {
            "surfaces": [
                {
                    "path": CHECKER_PATH,
                    "required_marker": MARKER,
                }
            ]
        },
        indent=2,
    ) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        current_checker_path = Path(__file__)
        original_checker_source = current_checker_path.read_text(encoding="utf-8")

        good_docs_root = "\n".join(DOCS_ROOT_REQUIRED_MARKERS) + "\n"
        good_smoke = "\n".join(SMOKE_SURVEY_REQUIRED_MARKERS) + "\n"
        good_makefile = f"phase14-validate:\n\tpython3 {CHECKER_PATH}\n"

        write_text(root / DOCS_ROOT_PATH, good_docs_root)
        write_text(root / SMOKE_SURVEY_PATH, good_smoke)
        write_text(root / MAKEFILE_PATH, good_makefile)
        write_text(root / MANIFEST_PATH, good_manifest_text())

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        write_text(
            root / DOCS_ROOT_PATH,
            good_docs_root.replace(
                f"{CHECKER_PATH}\n",
                f"{CHECKER_PATH}\n{CHECKER_PATH}\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            f"marker count drift in {DOCS_ROOT_PATH}: {CHECKER_PATH} (expected 1, found 2)" in error
            for error in errors
        ):
            print("self-test expected duplicate docs-root checker-path failure", file=sys.stderr)
            return 1
        write_text(root / DOCS_ROOT_PATH, good_docs_root)

        write_text(
            root / SMOKE_SURVEY_PATH,
            good_smoke.replace(
                "make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig\n",
                "",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-end-to-end-smoke-survey.md: make -C zigux phase14-smoke ZIG=/absolute/path/to/attached-zig/zig"
            in error
            for error in errors
        ):
            print("self-test expected missing attached-toolchain smoke route failure", file=sys.stderr)
            return 1
        write_text(root / SMOKE_SURVEY_PATH, good_smoke)

        write_text(
            root / SMOKE_SURVEY_PATH,
            good_smoke.replace(
                "PHASE14_SHARED_SURFACE_COUNT=29\n",
                "PHASE14_SHARED_SURFACE_COUNT=29\nPHASE14_SHARED_SURFACE_COUNT=29\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: PHASE14_SHARED_SURFACE_COUNT=29 (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate shared-surface-count failure", file=sys.stderr)
            return 1
        write_text(root / SMOKE_SURVEY_PATH, good_smoke)

        write_text(
            root / MAKEFILE_PATH,
            good_makefile.replace(
                f"python3 {CHECKER_PATH}\n",
                f"python3 {CHECKER_PATH}\n\tpython3 {CHECKER_PATH}\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            f"marker count drift in {MAKEFILE_PATH}: {CHECKER_PATH} (expected 1, found 2)" in error
            for error in errors
        ):
            print("self-test expected duplicate makefile checker-route failure", file=sys.stderr)
            return 1
        write_text(root / MAKEFILE_PATH, good_makefile)

        write_text(root / MANIFEST_PATH, json.dumps({"surfaces": []}, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 docs-root smoke-summary checker surface count drift in zigux/tests/phase14_end_to_end_smoke_manifest.json (expected 1, found 0)" in error for error in errors):
            print("self-test expected missing manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        {
                            "path": CHECKER_PATH,
                            "required_marker": "PHASE14_CHECK_PACKET=broken_marker",
                        }
                    ]
                },
                indent=2,
            ) + "\n",
        )
        errors = check(root)
        if not any(
            "missing docs-root smoke-summary checker surface in zigux/tests/phase14_end_to_end_smoke_manifest.json"
            in error
            for error in errors
        ):
            print("self-test expected manifest required-marker drift failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(root / MANIFEST_PATH, "{\n")
        errors = check(root)
        if not any(
            error.startswith("invalid json in zigux/tests/phase14_end_to_end_smoke_manifest.json:")
            for error in errors
        ):
            print("self-test expected invalid manifest json failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(root / MANIFEST_PATH, json.dumps({"surfaces": "not-a-list"}, indent=2) + "\n")
        errors = check(root)
        if "phase14 shared smoke manifest surfaces payload is not a list" not in errors:
            print("self-test expected non-list manifest surfaces failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        17,
                        {
                            "path": CHECKER_PATH,
                            "required_marker": MARKER,
                        },
                    ]
                },
                indent=2,
            ) + "\n",
        )
        errors = check(root)
        if "phase14 shared smoke manifest surface entry is not an object" not in errors:
            print("self-test expected non-object manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        {
                            "required_marker": MARKER,
                        }
                    ]
                },
                indent=2,
            ) + "\n",
        )
        errors = check(root)
        if "phase14 shared smoke manifest surface entry is missing a string path" not in errors:
            print("self-test expected missing-path manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        {
                            "path": CHECKER_PATH,
                        }
                    ]
                },
                indent=2,
            ) + "\n",
        )
        errors = check(root)
        if not any(
            "phase14 docs-root smoke-summary checker surface is missing a string required_marker in zigux/tests/phase14_end_to_end_smoke_manifest.json"
            in error
            for error in errors
        ):
            print("self-test expected missing required-marker manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        write_text(
            root / MANIFEST_PATH,
            json.dumps(
                {
                    "surfaces": [
                        {
                            "path": CHECKER_PATH,
                            "required_marker": MARKER,
                        },
                        {
                            "path": CHECKER_PATH,
                            "required_marker": MARKER,
                        },
                    ]
                },
                indent=2,
            ) + "\n",
        )
        errors = check(root)
        if not any(
            "phase14 docs-root smoke-summary checker surface count drift in zigux/tests/phase14_end_to_end_smoke_manifest.json (expected 1, found 2)"
            in error
            for error in errors
        ):
            print("self-test expected duplicate manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / MANIFEST_PATH, good_manifest_text())

        current_checker_path.write_text(
            original_checker_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"),
            encoding="utf-8",
        )
        errors = check(root)
        if "checker marker missing from checker source" not in errors:
            print("self-test expected checker source marker failure", file=sys.stderr)
            current_checker_path.write_text(original_checker_source, encoding="utf-8")
            return 1
        current_checker_path.write_text(original_checker_source, encoding="utf-8")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 docs-root smoke summary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
