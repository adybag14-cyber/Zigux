#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

MAKEFILE_MARKERS = [
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase7-test:",
    "phase7:",
]

CATALOG_REQUIRED_SNIPPETS = [
    "## Current direct-readback companions",
    "- `zigux/tests/phase7_build.zig`",
    "## Current repo-reality gaps",
    "- `make -C zigux phase7-test`",
    "- `make -C zigux phase7`",
]

BUILD_REQUIRED_SNIPPETS = [
    'b.path("phase7_string_helpers.zig")',
    'b.path("phase7_cmdline.zig")',
    'b.path("phase7_argv_split.zig")',
    'b.path("phase7_rbtree.zig")',
    '"phase7-string-helpers-test"',
    '"phase7-cmdline-test"',
    '"phase7-argv-split-test"',
    '"phase7-rbtree-test"',
    '"phase7-string-helpers-survey"',
    '"phase7-cmdline-survey"',
    '"phase7-argv-split-survey"',
    '"phase7-rbtree-survey"',
    'b.step("test", "Run Phase 7 runtime helper tests")',
]

MANIFEST_REQUIRED_GAPS = [
    "make -C zigux phase7-test",
    "make -C zigux phase7",
]

REQUIRED_FILES = (VALIDATOR_PATH, CATALOG_PATH, MANIFEST_PATH, BUILD_PATH, MAKEFILE_PATH)
REQUIRED_PRESENT_MARKERS = {
    MAKEFILE_PATH: MAKEFILE_MARKERS,
    CATALOG_PATH: CATALOG_REQUIRED_SNIPPETS,
    BUILD_PATH: BUILD_REQUIRED_SNIPPETS,
}
FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: FORBIDDEN_MAKEFILE_MARKERS,
}

FIXTURE_TEXTS = {
    VALIDATOR_PATH: "#!/usr/bin/env python3\nprint('PHASE7_VALIDATE=pass')\n",
    CATALOG_PATH: "\n".join(
        [
            "- packet: `phase7-leaf-library-evidence`",
            "- phase: `Phase 7`",
            "- lane scope: shared leaf-library evidence rows and validation foothold only",
            "",
            "## Current direct-readback companions",
            "- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`",
            "- `zigux/tests/phase7_build.zig`",
            "",
            "## Current repo-reality gaps",
            "- `make -C zigux phase7-test`",
            "- `make -C zigux phase7`",
        ]
    )
    + "\n",
    MANIFEST_PATH: json.dumps(
        {
            "packet": "phase7-leaf-library-evidence",
            "phase": "Phase 7",
            "lane_scope": "shared leaf-library evidence rows and validation foothold only",
            "current_direct_readback_companions": [
                "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
                "Documentation/zigux/README.md",
                "scripts/zigux/check-phase7-shared-surface.py",
                "scripts/zigux/validate-phase7.py",
                "scripts/zigux/README.md",
                "zigux/tests/README.md",
                "zigux/tests/phase7_leaf_library_evidence_manifest.json",
                "zigux/tests/phase7_build.zig",
                "zigux/Makefile",
                "lib/string_helpers.zig",
                "lib/string_helpers_parse_int_array.zig",
                "lib/cmdline.zig",
                "lib/argv_split.zig",
                "lib/rbtree.zig",
            ],
            "current_repo_reality_gaps": MANIFEST_REQUIRED_GAPS,
            "current_replay_inventory": [
                "python3 scripts/zigux/check-phase7-shared-surface.py",
                "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
                "python3 scripts/zigux/validate-phase7.py",
                "python3 scripts/zigux/validate-phase7.py --self-test",
                "make -C zigux phase7-validate",
            ],
        },
        indent=2,
    )
    + "\n",
    BUILD_PATH: "\n".join(
        [
            'const std = @import("std");',
            "pub fn build(b: *std.Build) void {",
            '    _ = b.path("phase7_string_helpers.zig");',
            '    _ = b.path("phase7_cmdline.zig");',
            '    _ = b.path("phase7_argv_split.zig");',
            '    _ = b.path("phase7_rbtree.zig");',
            '    _ = "phase7-string-helpers-test";',
            '    _ = "phase7-cmdline-test";',
            '    _ = "phase7-argv-split-test";',
            '    _ = "phase7-rbtree-test";',
            '    _ = "phase7-string-helpers-survey";',
            '    _ = "phase7-cmdline-survey";',
            '    _ = "phase7-argv-split-survey";',
            '    _ = "phase7-rbtree-survey";',
            '    _ = b.step("test", "Run Phase 7 runtime helper tests");',
            "}",
        ]
    )
    + "\n",
    MAKEFILE_PATH: "\n".join(
        [
            "PYTHON ?= python3",
            "ZIG ?= zig",
            "ZIGUX_ROOT := ..",
            ".PHONY: phase7-validate",
            "phase7-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
        ]
    )
    + "\n",
}


def _read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _read_manifest_gaps(root: Path) -> list[str]:
    data = json.loads(_read_text(root, MANIFEST_PATH))
    gaps = data.get("current_repo_reality_gaps")
    if not isinstance(gaps, list):
        raise ValueError("current_repo_reality_gaps missing")
    return [item for item in gaps if isinstance(item, str)]


def validate(root: Path) -> tuple[list[str], list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []
    unexpected_markers: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            missing_files.append(str(rel))

    if missing_files:
        return missing_files, missing_markers, unexpected_markers

    for rel, markers in REQUIRED_PRESENT_MARKERS.items():
        text = _read_text(root, rel)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{rel}: {marker}")

    try:
        manifest_gaps = _read_manifest_gaps(root)
    except (json.JSONDecodeError, ValueError):
        missing_markers.append(f"{MANIFEST_PATH}: current_repo_reality_gaps")
    else:
        for gap in MANIFEST_REQUIRED_GAPS:
            if gap not in manifest_gaps:
                missing_markers.append(f"{MANIFEST_PATH}: {gap}")

    for rel, markers in FORBIDDEN_MARKERS.items():
        text = _read_text(root, rel)
        for marker in markers:
            if marker in text:
                unexpected_markers.append(f"{rel}: {marker}")

    return missing_files, missing_markers, unexpected_markers


def _write_fixture_root(root: Path) -> None:
    for rel, text in FIXTURE_TEXTS.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _mutate_text(root: Path, rel: Path, old: str, new: str, case: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    assert updated != text, case
    path.write_text(updated, encoding="utf-8")


def _append_text(root: Path, rel: Path, extra: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [(f"missing_{rel.name}", rel) for rel in REQUIRED_FILES]
    marker_cases = [
        (
            "missing_catalog_build_companion_marker",
            CATALOG_PATH,
            "- `zigux/tests/phase7_build.zig`",
            "- `zigux/tests/phase7_build_missing.zig`",
        ),
        (
            "missing_build_argv_split_route",
            BUILD_PATH,
            '"phase7-argv-split-test"',
            '"phase7-argv-split-proof"',
        ),
        (
            "missing_build_test_step",
            BUILD_PATH,
            'b.step("test", "Run Phase 7 runtime helper tests")',
            'b.step("phase7", "Run Phase 7 runtime helper tests")',
        ),
        (
            "missing_phase7_validate_route",
            MAKEFILE_PATH,
            "phase7-validate:",
            "phase7-verify:",
        ),
        (
            "missing_phase7_validate_run",
            MAKEFILE_PATH,
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-shared-surface.py",
        ),
        (
            "missing_manifest_phase7_test_gap",
            MANIFEST_PATH,
            "make -C zigux phase7-test",
            "make -C zigux phase7-run",
        ),
    ]
    unexpected_marker_cases = [
        ("phase7_test_route_returned", "phase7-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig\n"),
        ("phase7_aggregate_route_returned", "phase7: phase7-validate phase7-test\n"),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_build_wiring_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write_fixture_root(root)
        assert validate(root) == ([], [], [])

        for case, rel in missing_file_cases:
            (root / rel).unlink()
            assert validate(root) == ([str(rel)], [], []), case
            _write_fixture_root(root)

        for case, rel, old, new in marker_cases:
            _mutate_text(root, rel, old, new, case)
            assert validate(root) == ([], [f"{rel}: {old}"], []), case
            _write_fixture_root(root)

        for case, extra in unexpected_marker_cases:
            _append_text(root, MAKEFILE_PATH, extra)
            expected = []
            for marker in FORBIDDEN_MAKEFILE_MARKERS:
                if marker in extra:
                    expected.append(f"{MAKEFILE_PATH}: {marker}")
            assert validate(root) == ([], [], expected), case
            _write_fixture_root(root)

    print("PHASE7_BUILD_WIRING=pass")
    print(
        "PHASE7_BUILD_WIRING_CASE_COUNT=%d"
        % (len(missing_file_cases) + len(marker_cases) + len(unexpected_marker_cases))
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 7 integration posture keeps the shared "
            "phase7_build.zig foothold explicit while phase7 make-wrapper test "
            "routes stay absent."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers, unexpected_markers = validate(Path("."))
    if missing_files:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE7_BUILD_WIRING=fail")
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    if unexpected_markers:
        print("PHASE7_BUILD_WIRING=fail")
        print("UNEXPECTED_PHASE7_BUILD_WIRING_MARKERS_START")
        for item in unexpected_markers:
            print(item)
        print("UNEXPECTED_PHASE7_BUILD_WIRING_MARKERS_END")
        return 1

    print("PHASE7_BUILD_WIRING=pass")
    print(f"PHASE7_BUILD_WIRING_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE7_BUILD_WIRING_PRESENT_MARKER_COUNT=%d"
        % (
            sum(len(markers) for markers in REQUIRED_PRESENT_MARKERS.values())
            + len(MANIFEST_REQUIRED_GAPS)
        )
    )
    print(
        "PHASE7_BUILD_WIRING_FORBIDDEN_MARKER_COUNT=%d"
        % sum(len(markers) for markers in FORBIDDEN_MARKERS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())