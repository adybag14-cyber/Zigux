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
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase7-string-helpers-test:",
    "phase7-string-helpers-survey:",
    "phase7-string-helpers-sample-boundary:",
    "phase7-cmdline-test:",
    "phase7-cmdline-survey:",
    "phase7-argv-split-test:",
    "phase7-argv-split-survey:",
    "phase7-rbtree-test:",
    "phase7-rbtree-survey:",
    "phase7-test:",
    "phase7:",
]

CATALOG_REQUIRED_SNIPPETS = [
    "## Current replay inventory",
    "- `make -C zigux phase7-validate`",
    "## Current repo-reality gaps",
    "- `zigux/tests/phase7_build.zig`",
]

MANIFEST_REQUIRED_GAPS = [
    "lib/rbtree.zig",
    "zigux/tests/phase7_build.zig",
]

REQUIRED_FILES = (VALIDATOR_PATH, CATALOG_PATH, MANIFEST_PATH, MAKEFILE_PATH)
REQUIRED_PRESENT_MARKERS = {
    MAKEFILE_PATH: MAKEFILE_MARKERS,
    CATALOG_PATH: CATALOG_REQUIRED_SNIPPETS,
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
            "## Current replay inventory",
            "- `make -C zigux phase7-validate`",
            "",
            "## Current repo-reality gaps",
            "- `lib/rbtree.zig`",
            "- `zigux/tests/phase7_build.zig`",
        ]
    )
    + "\n",
    MANIFEST_PATH: json.dumps(
        {
            "packet": "phase7-leaf-library-evidence",
            "phase": "Phase 7",
            "lane_scope": "shared leaf-library evidence rows and validation foothold only",
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
    MAKEFILE_PATH: "\n".join(
        [
            "PYTHON ?= python3",
            "ZIG ?= zig",
            "ZIGUX_ROOT := ..",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
            ".PHONY: phase2 phase3 phase7-validate",
            "phase2:",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
            "phase3:",
            "\tcd .. && $(PYTHON) scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
            "phase7-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
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

    if (root / BUILD_PATH).exists():
        unexpected_markers.append(f"{BUILD_PATH}: unexpected rematerialized parked build file")

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
            "missing_catalog_build_gap_marker",
            CATALOG_PATH,
            "- `zigux/tests/phase7_build.zig`",
            "- `zigux/tests/phase7_build_missing.zig`",
        ),
        (
            "missing_phase7_validate_route",
            MAKEFILE_PATH,
            "phase7-validate:",
            "phase7-verify:",
        ),
        (
            "missing_phase7_validate_selftest",
            MAKEFILE_PATH,
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "$(PYTHON) scripts/zigux/validate-phase7.py --check-only",
        ),
        (
            "missing_phase7_validate_run",
            MAKEFILE_PATH,
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n",
            "$(PYTHON) scripts/zigux/check-phase7-shared-surface.py\n",
        ),
        (
            "missing_manifest_build_gap",
            MANIFEST_PATH,
            "zigux/tests/phase7_build.zig",
            "zigux/tests/phase7_build_missing.zig",
        ),
    ]
    unexpected_marker_cases = [
        ("phase7_cmdline_route_returned", "phase7-cmdline-survey:\n\tzig test zigux/tests/phase7_cmdline_survey.zig\n"),
        ("phase7_bundle_route_returned", "phase7: phase7-validate phase7-test\n"),
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

        build_path = root / BUILD_PATH
        build_path.parent.mkdir(parents=True, exist_ok=True)
        build_path.write_text("const std = @import(\"std\");\n", encoding="utf-8")
        assert validate(root) == (
            [],
            [],
            [f"{BUILD_PATH}: unexpected rematerialized parked build file"],
        ), "unexpected_build_file_returned"

    print("PHASE7_BUILD_WIRING=pass")
    print(
        "PHASE7_BUILD_WIRING_CASE_COUNT=%d"
        % (len(missing_file_cases) + len(marker_cases) + len(unexpected_marker_cases) + 1)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shipped Phase 7 validation foothold stays aligned with "
            "the current parked-build posture by keeping `phase7-validate` present, "
            "helper-local wrapper routes absent, and the missing `phase7_build.zig` "
            "path recorded as an explicit repo-reality gap."
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
        % (sum(len(markers) for markers in FORBIDDEN_MARKERS.values()) + 1)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
