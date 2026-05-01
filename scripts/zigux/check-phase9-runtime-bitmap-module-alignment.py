#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/phase9_build.zig",
]

REQUIRED_MODULE_MARKERS = [
    "`PHASE9_LANE_KEY=P9-L08`",
    "`PHASE9_SURVEYED_COMMIT=",
    "adjacent loader scaffold plus shared loader-request binding",
    "zigux/kernel/runtime_loader.zig",
    "direct post-selftest mutation replay proof",
    "direct `phase9-runtime-bitmap-sample-tests` and `phase9-runtime-bitmap-loader-tests` legs",
    "bounded two-word runtime bitmap backing store",
    "bounded parse-and-print replay",
    "duplicate bit-list normalization and empty formatting",
    "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`",
    "it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor",
    "No parity scorecard entry or Architecture Council status-change request is attached to this runtime bitmap starter packet.",
    "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
    "parity or ownership for `kernel/workqueue.c`",
    "any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision",
]

REQUIRED_SURVEY_MARKERS = [
    "`PHASE9_LANE_KEY=P9-L08`",
    "`PHASE9_SURVEYED_COMMIT=",
    "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`",
]

REQUIRED_BUILD_MARKERS = [
    "phase9-runtime-bitmap-sample-tests",
    "phase9-runtime-bitmap-loader-tests",
]

REQUIRED_FREEZE_MAP_MARKERS = [
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "Architecture Council decision",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def extract_marker_commit(document: str) -> str | None:
    match = re.search(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`", document)
    if not match:
        return None
    return match.group(1)


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    survey_doc = read_text(root, "Documentation/zigux/phase9-runtime-bitmap-survey.md")
    module_doc = read_text(root, "Documentation/zigux/phase9-runtime-bitmap-module-slice.md")
    manifest_text = read_text(root, "zigux/tests/runtime_bitmap_manifest.json")
    phase9_build = read_text(root, "zigux/tests/phase9_build.zig")

    missing_markers: list[str] = []

    for marker in REQUIRED_FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            missing_markers.append(f"freeze_map:{marker}")
    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_doc:
            missing_markers.append(f"survey:{marker}")
    for marker in REQUIRED_MODULE_MARKERS:
        if marker not in module_doc:
            missing_markers.append(f"module:{marker}")
    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in phase9_build:
            missing_markers.append(f"phase9_build:{marker}")

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        missing_markers.append("manifest:json_decode_failed")
        return [], missing_markers

    manifest_commit = manifest.get("surveyed_commit")
    if not isinstance(manifest_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest_commit):
        missing_markers.append("manifest:invalid_surveyed_commit")
        return [], missing_markers

    survey_commit = extract_marker_commit(survey_doc)
    module_commit = extract_marker_commit(module_doc)
    if survey_commit != manifest_commit:
        missing_markers.append("survey:surveyed_commit_mismatch")
    if module_commit != manifest_commit:
        missing_markers.append("module:surveyed_commit_mismatch")

    return [], missing_markers


def clone_fixture_tree(root: Path) -> None:
    files = {
        "Documentation/zigux/freeze-map.md": """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`

## Governance For Freeze-Map Changes
- changes require an explicit Architecture Council decision with written rationale
""",
        "Documentation/zigux/phase9-runtime-bitmap-survey.md": """# Phase 9 Runtime Bitmap Survey

- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=f15b316029bc067aacb393be773744950fcb7486`

`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`.
""",
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md": """# Phase 9 Runtime Bitmap Module Slice

- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=f15b316029bc067aacb393be773744950fcb7486`

adjacent loader scaffold plus shared loader-request binding
zigux/kernel/runtime_loader.zig
direct post-selftest mutation replay proof
direct `phase9-runtime-bitmap-sample-tests` and `phase9-runtime-bitmap-loader-tests` legs
bounded two-word runtime bitmap backing store
bounded parse-and-print replay
duplicate bit-list normalization and empty formatting

`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this starter may describe the bounded in-memory sample, the sample-side loader scaffold, and the shared loader-request binding, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this runtime bitmap starter packet.

zig build test --build-file zigux/tests/phase9_build.zig --summary all

parity or ownership for `kernel/workqueue.c`
any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision
""",
        "zigux/tests/runtime_bitmap_manifest.json": """{
  \"surveyed_commit\": \"f15b316029bc067aacb393be773744950fcb7486\"
}
""",
        "zigux/tests/phase9_build.zig": """const _ = \"phase9-runtime-bitmap-sample-tests phase9-runtime-bitmap-loader-tests\";
""",
    }

    for rel_path, content in files.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"unexpected_missing_files:{','.join(missing_files)}")
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"expected_missing_marker:{expected}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase9_bitmap_module_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        clone_fixture_tree(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        module_doc = root / "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"
        original_module = module_doc.read_text(encoding="utf-8")
        module_doc.write_text(
            original_module.replace(
                "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
                "zig build test --build-file zigux/tests/phase9_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "module:zig build test --build-file zigux/tests/phase9_build.zig --summary all",
        )
        module_doc.write_text(original_module, encoding="utf-8")

        module_doc.write_text(
            original_module.replace(
                "`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this starter may describe the bounded in-memory sample, the sample-side loader scaffold, and the shared loader-request binding, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            root,
            "module:`Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`",
        )
        module_doc.write_text(original_module, encoding="utf-8")

        manifest_path = root / "zigux/tests/runtime_bitmap_manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            original_manifest.replace(
                '\"surveyed_commit\": \"f15b316029bc067aacb393be773744950fcb7486\"',
                '\"surveyed_commit\": \"1111111111111111111111111111111111111111\"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(root, "survey:surveyed_commit_mismatch")
        manifest_path.write_text(original_manifest, encoding="utf-8")

    print("PHASE9_BITMAP_MODULE_ALIGNMENT_SELF_TEST=pass")
    print("PHASE9_BITMAP_MODULE_ALIGNMENT_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 9 runtime bitmap module-slice review packet."
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE9_BITMAP_MODULE_ALIGNMENT=fail")
        print("MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_FILES_END")
        return 1
    if missing_markers:
        print("PHASE9_BITMAP_MODULE_ALIGNMENT=fail")
        print("MISSING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE9_BITMAP_MODULE_ALIGNMENT=pass")
    print(f"PHASE9_BITMAP_MODULE_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE9_BITMAP_MODULE_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_FREEZE_MAP_MARKERS) + len(REQUIRED_SURVEY_MARKERS) + len(REQUIRED_MODULE_MARKERS) + len(REQUIRED_BUILD_MARKERS) + 2}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
