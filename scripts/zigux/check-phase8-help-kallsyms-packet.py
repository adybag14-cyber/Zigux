#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/phase8-kallsyms-slice.md",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase8-help-kallsyms-packet.py",
    "tools/lib/subcmd/help.zig",
    "tools/lib/symbol/kallsyms.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "zigux/tests/phase8_help_kallsyms_only_build.zig",
    "zigux/tests/phase8_kallsyms.zig",
    "zigux/tests/phase8_kallsyms_only_build.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-help-slice.md": [
        "serious repo-hosted tooling",
        "output-stable pretty-print emission",
        "make -C zigux phase8-help-kallsyms-test",
    ],
    "Documentation/zigux/phase8-kallsyms-slice.md": [
        "PHASE8_SLICE=kallsyms-parse-wrapper-parked",
        "one direct `kallsymsParse()` wrapper",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "make -C zigux phase8-help-kallsyms-test",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "make -C zigux phase8-help-kallsyms-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 help and kallsyms tests",
        "make -C zigux phase8-help-kallsyms-test",
    ],
    "tools/lib/subcmd/help.zig": [
        "pub fn loadCommandListsFromSource",
        "pub fn loadCommandListsFromEnvPath",
        "pub fn resolveTerminalDimensions",
        "pub fn writeCommandSectionsForTerminal",
    ],
    "tools/lib/symbol/kallsyms.zig": [
        "pub fn parseLine",
        "pub fn forEachParsedChunked",
        "pub fn forEachParsedReader",
        "pub fn kallsymsParseFile",
        "pub fn kallsymsParse",
        "parseLine truncates oversized names instead of failing them",
        "weak object symbol classes keep the current C helper classification",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-kallsyms-packet.py",
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase8_help_kallsyms_only_build.zig",
        "make -C zigux phase8-help-kallsyms-test",
        "shared help-and-symbol replay",
    ],
    "zigux/tests/phase8_help.zig": [
        "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit",
        "full `cmd_help()`-adjacent CLI surface",
        "phase8_help_kallsyms_only_build.zig",
    ],
    "zigux/tests/phase8_help_only_build.zig": [
        "\"Documentation/zigux/phase8-help-slice.md\"",
        "\"phase8_help.zig\"",
        "phase8-help-tests",
        "Run focused Phase 8 help tests",
    ],
    "zigux/tests/phase8_help_kallsyms_only_build.zig": [
        "\"Documentation/zigux/phase8-help-slice.md\"",
        "\"Documentation/zigux/phase8-kallsyms-slice.md\"",
        "\"phase8_help.zig\"",
        "\"phase8_kallsyms.zig\"",
        "phase8-help-tests",
        "phase8-kallsyms-tests",
        "Run focused Phase 8 help and kallsyms tests",
    ],
    "zigux/tests/phase8_kallsyms.zig": [
        "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit",
        "oversized symbol names now truncate to `KSYM_NAME_LEN`",
        "weak-object `V` and `v` classes still follow the current C header contract",
        "phase8_help_kallsyms_only_build.zig",
    ],
    "zigux/tests/phase8_kallsyms_only_build.zig": [
        "\"Documentation/zigux/phase8-kallsyms-slice.md\"",
        "\"phase8_kallsyms.zig\"",
        "phase8-kallsyms-tests",
        "Run focused Phase 8 kallsyms tests",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    return collect_missing_files(root), collect_missing_markers(root)


def fixture_text(rel: str) -> str:
    if rel == "scripts/zigux/check-phase8-help-kallsyms-packet.py":
        return "# fixture\n"
    return "\n".join(REQUIRED_MARKERS.get(rel, ["# fixture"])) + "\n"


def write_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fixture_text(rel), encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_checker", "scripts/zigux/check-phase8-help-kallsyms-packet.py"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_workflow", ".github/workflows/zigux-bootstrap.yml"),
        ("missing_help_slice", "Documentation/zigux/phase8-help-slice.md"),
        ("missing_kallsyms_slice", "Documentation/zigux/phase8-kallsyms-slice.md"),
        ("missing_help_helper", "tools/lib/subcmd/help.zig"),
        ("missing_kallsyms_helper", "tools/lib/symbol/kallsyms.zig"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_combined_build", "zigux/tests/phase8_help_kallsyms_only_build.zig"),
    ]

    marker_cases = [
        (
            "help_slice_combined_route",
            "Documentation/zigux/phase8-help-slice.md",
            "make -C zigux phase8-help-kallsyms-test",
            "make -C zigux phase8-help-test",
            "Documentation/zigux/phase8-help-slice.md: make -C zigux phase8-help-kallsyms-test",
        ),
        (
            "kallsyms_slice_truncation_guard",
            "Documentation/zigux/phase8-kallsyms-slice.md",
            "oversized symbol names now truncate to `KSYM_NAME_LEN`",
            "oversized symbol names now stay bounded",
            "Documentation/zigux/phase8-kallsyms-slice.md: oversized symbol names now truncate to `KSYM_NAME_LEN`",
        ),
        (
            "kallsyms_slice_weak_object_note",
            "Documentation/zigux/phase8-kallsyms-slice.md",
            "weak-object `V` and `v` classes still follow the current C header contract",
            "weak-object classes stay aligned",
            "Documentation/zigux/phase8-kallsyms-slice.md: weak-object `V` and `v` classes still follow the current C header contract",
        ),
        (
            "scripts_readme_combined_checker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase8-help-kallsyms-packet.py",
            "scripts/zigux/check-phase8-help-kallsyms-surface.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase8-help-kallsyms-packet.py",
        ),
        (
            "workflow_combined_step",
            ".github/workflows/zigux-bootstrap.yml",
            "Run focused Phase 8 help and kallsyms tests",
            "Run focused Phase 8 help tests",
            ".github/workflows/zigux-bootstrap.yml: Run focused Phase 8 help and kallsyms tests",
        ),
        (
            "kallsyms_helper_truncation_test",
            "tools/lib/symbol/kallsyms.zig",
            "parseLine truncates oversized names instead of failing them",
            "parseLine keeps oversized names explicit",
            "tools/lib/symbol/kallsyms.zig: parseLine truncates oversized names instead of failing them",
        ),
        (
            "kallsyms_helper_weak_object_test",
            "tools/lib/symbol/kallsyms.zig",
            "weak object symbol classes keep the current C helper classification",
            "weak object classes stay explicit",
            "tools/lib/symbol/kallsyms.zig: weak object symbol classes keep the current C helper classification",
        ),
        (
            "makefile_phase8_checker_self_test",
            "zigux/Makefile",
            "scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
            "scripts/zigux/check-phase8-help-kallsyms-surface.py --self-test",
            "zigux/Makefile: scripts/zigux/check-phase8-help-kallsyms-packet.py --self-test",
        ),
        (
            "tests_readme_combined_anchor",
            "zigux/tests/README.md",
            "zigux/tests/phase8_help_kallsyms_only_build.zig",
            "zigux/tests/phase8_help_symbol_only_build.zig",
            "zigux/tests/README.md: zigux/tests/phase8_help_kallsyms_only_build.zig",
        ),
        (
            "help_test_combined_build_anchor",
            "zigux/tests/phase8_help.zig",
            "phase8_help_kallsyms_only_build.zig",
            "phase8_help_symbol_only_build.zig",
            "zigux/tests/phase8_help.zig: phase8_help_kallsyms_only_build.zig",
        ),
        (
            "combined_build_workflow_label",
            "zigux/tests/phase8_help_kallsyms_only_build.zig",
            "Run focused Phase 8 help and kallsyms tests",
            "Run focused Phase 8 help tests",
            "zigux/tests/phase8_help_kallsyms_only_build.zig: Run focused Phase 8 help and kallsyms tests",
        ),
        (
            "kallsyms_test_truncation_contract",
            "zigux/tests/phase8_kallsyms.zig",
            "phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit",
            "phase 8 kallsyms slice note keeps the parser contract explicit",
            "zigux/tests/phase8_kallsyms.zig: phase 8 kallsyms slice note keeps the C-aligned truncation contract explicit",
        ),
        (
            "kallsyms_test_weak_object_anchor",
            "zigux/tests/phase8_kallsyms.zig",
            "weak-object `V` and `v` classes still follow the current C header contract",
            "weak-object classes stay explicit",
            "zigux/tests/phase8_kallsyms.zig: weak-object `V` and `v` classes still follow the current C header contract",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_help_kallsyms_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    print("PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST=pass")
    print(
        "PHASE8_HELP_KALLSYMS_PACKET_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 8 help and kallsyms review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_HELP_KALLSYMS_PACKET=fail")
        print("MISSING_PHASE8_HELP_KALLSYMS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_HELP_KALLSYMS_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_HELP_KALLSYMS_PACKET=fail")
        print("MISSING_PHASE8_HELP_KALLSYMS_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_HELP_KALLSYMS_MARKERS_END")
        return 1

    print("PHASE8_HELP_KALLSYMS_PACKET=pass")
    print(f"PHASE8_HELP_KALLSYMS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_HELP_KALLSYMS_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
