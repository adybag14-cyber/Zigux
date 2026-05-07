#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-help-slice.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase8-help-packet.py",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_help.zig",
    "zigux/tests/phase8_help_only_build.zig",
    "tools/lib/subcmd/help.zig",
    "tools/lib/subcmd/help.c",
]

EXACT_ONCE_SECTION_MARKERS = {
    "zigux/tests/README.md": [
        {
            "start": "  * `zigux/tests/phase8_build.zig`\n",
            "end": "  * `zigux/tests/phase9_build.zig`\n",
            "needle": "  * `zigux/tests/phase8_help_only_build.zig`\n",
        },
    ],
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-help-slice.md": [
        "PHASE8_SLICE=help-command-source-and-terminal-starter",
        "serious repo-hosted tooling",
        "output-stable tooling behavior",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-help-test",
        "zig build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
        "make -C zigux phase8",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-help-slice.md",
        "scripts/zigux/check-phase8-help-packet.py",
        "zigux/tests/phase8_help.zig",
        "zigux/tests/phase8_help_only_build.zig",
        "make -C zigux phase8-help-test",
        "make -C zigux phase8-validate",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "scripts/zigux/check-phase8-help-packet.py",
        "Documentation/zigux/phase8-help-slice.md",
        "zigux/tests/phase8_help.zig",
        "zigux/tests/phase8_help_only_build.zig",
        "make -C zigux phase8-help-test",
    ],
    "zigux/tests/README.md": [
        "Phase 8 flow",
        "`zigux/tests/phase8_help.zig`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8`",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/check-phase8-help-packet.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase8-help-packet.py",
        "phase8-help-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_help_only_build.zig --summary all",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/subcmd/help.zig",
        "\"phase8_help.zig\"",
        "phase8-help-tests",
    ],
    "zigux/tests/phase8_help.zig": [
        "phase 8 help slice note keeps helper-first output-stable tooling posture and non-goals explicit",
        "output-stable pretty-print emission",
        "phase8_help_only_build.zig",
    ],
    "zigux/tests/phase8_help_only_build.zig": [
        "\"Documentation/zigux/phase8-help-slice.md\"",
        "../../tools/lib/subcmd/help.zig",
        "\"phase8_help.zig\"",
        "phase8-help-tests",
        "Run focused Phase 8 help tests",
    ],
    "tools/lib/subcmd/help.zig": [
        "pub fn splitPathEntries",
        "pub fn loadCommandListsFromSource",
        "pub fn loadCommandListsFromEnvPath",
        "pub fn resolveTerminalDimensions",
        "pub fn writePrettyPrintStringListForTerminal",
        "pub fn writeCommandSectionsForTerminal",
    ],
    "tools/lib/subcmd/help.c": [
        "void add_cmdname",
        "static void get_term_dimensions",
        "static void pretty_print_string_list",
        "void load_command_list",
        "void list_commands",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def collect_exact_section_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, section_specs in EXACT_ONCE_SECTION_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for spec in section_specs:
            start = text.find(spec["start"])
            if start == -1:
                errors.append(f"{rel}: missing_section_start:{spec['start'].strip()}")
                continue

            section_start = start + len(spec["start"])
            end = text.find(spec["end"], section_start)
            if end == -1:
                errors.append(f"{rel}: missing_section_end:{spec['end'].strip()}")
                continue

            section = text[section_start:end]
            if section.count(spec["needle"]) != 1:
                errors.append(
                    f"{rel}: exact_once_section_marker:{spec['needle'].rstrip()}"
                )
    return errors


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    missing_markers = collect_missing_markers(root)
    missing_markers.extend(collect_exact_section_errors(root))
    return [], missing_markers


def build_tests_readme_fixture() -> str:
    return "\n".join(
        [
            "Phase 8 flow",
            "  * `zigux/tests/phase8_build.zig`",
            "  * `zigux/tests/phase8_help.zig`",
            "  * `zigux/tests/phase8_help_only_build.zig`",
            "  * `make -C zigux phase8-help-test`",
            "  * `make -C zigux phase8`",
            "  * `zigux/tests/phase9_build.zig`",
        ]
    ) + "\n"


FIXTURE_OVERRIDES = {
    "zigux/tests/README.md": build_tests_readme_fixture(),
}


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        override = FIXTURE_OVERRIDES.get(rel)
        if override is not None:
            path.write_text(override, encoding="utf-8")
            continue
        markers = REQUIRED_MARKERS.get(rel)
        if markers is not None:
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")
        else:
            path.write_text("# fixture\n", encoding="utf-8")


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
        ("missing_slice", "Documentation/zigux/phase8-help-slice.md"),
        ("missing_docs_root", "Documentation/zigux/README.md"),
        ("missing_scripts_readme", "scripts/zigux/README.md"),
        ("missing_checker", "scripts/zigux/check-phase8-help-packet.py"),
        ("missing_tests_readme", "zigux/tests/README.md"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_help_test", "zigux/tests/phase8_help.zig"),
        ("missing_help_only_build", "zigux/tests/phase8_help_only_build.zig"),
        ("missing_help_helper", "tools/lib/subcmd/help.zig"),
        ("missing_help_c_anchor", "tools/lib/subcmd/help.c"),
    ]

    marker_cases = [
        (
            "slice_marker",
            "Documentation/zigux/phase8-help-slice.md",
            "PHASE8_SLICE=help-command-source-and-terminal-starter",
            "PHASE8_SLICE=help-drift",
            "Documentation/zigux/phase8-help-slice.md: PHASE8_SLICE=help-command-source-and-terminal-starter",
        ),
        (
            "slice_make_route",
            "Documentation/zigux/phase8-help-slice.md",
            "make -C zigux phase8-help-test",
            "make -C zigux phase8-help",
            "Documentation/zigux/phase8-help-slice.md: make -C zigux phase8-help-test",
        ),
        (
            "docs_root_checker",
            "Documentation/zigux/README.md",
            "scripts/zigux/check-phase8-help-packet.py",
            "scripts/zigux/check-phase8-help-surface.py",
            "Documentation/zigux/README.md: scripts/zigux/check-phase8-help-packet.py",
        ),
        (
            "scripts_readme_checker",
            "scripts/zigux/README.md",
            "scripts/zigux/check-phase8-help-packet.py",
            "scripts/zigux/check-phase8-help-surface.py",
            "scripts/zigux/README.md: scripts/zigux/check-phase8-help-packet.py",
        ),
        (
            "tests_readme_exact_once_duplicate",
            "zigux/tests/README.md",
            "  * `zigux/tests/phase8_help_only_build.zig`\n",
            "  * `zigux/tests/phase8_help_only_build.zig`\n  * `zigux/tests/phase8_help_only_build.zig`\n",
            "zigux/tests/README.md: exact_once_section_marker:  * `zigux/tests/phase8_help_only_build.zig`",
        ),
        (
            "makefile_checker_self_test",
            "zigux/Makefile",
            "scripts/zigux/check-phase8-help-packet.py --self-test",
            "scripts/zigux/check-phase8-help-surface.py --self-test",
            "zigux/Makefile: scripts/zigux/check-phase8-help-packet.py --self-test",
        ),
        (
            "shared_build_source",
            "zigux/tests/phase8_build.zig",
            "\"phase8_help.zig\"",
            "\"phase8_help_drift.zig\"",
            "zigux/tests/phase8_build.zig: \"phase8_help.zig\"",
        ),
        (
            "help_test_marker",
            "zigux/tests/phase8_help.zig",
            "phase8_help_only_build.zig",
            "phase8_help_build.zig",
            "zigux/tests/phase8_help.zig: phase8_help_only_build.zig",
        ),
        (
            "help_only_build_label",
            "zigux/tests/phase8_help_only_build.zig",
            "Run focused Phase 8 help tests",
            "Run focused Phase 8 command help tests",
            "zigux/tests/phase8_help_only_build.zig: Run focused Phase 8 help tests",
        ),
        (
            "help_helper_terminal_sections",
            "tools/lib/subcmd/help.zig",
            "pub fn writeCommandSectionsForTerminal",
            "pub fn writeCommandSections",
            "tools/lib/subcmd/help.zig: pub fn writeCommandSectionsForTerminal",
        ),
        (
            "help_c_anchor_command_loader",
            "tools/lib/subcmd/help.c",
            "void load_command_list",
            "void load_help_commands",
            "tools/lib/subcmd/help.c: void load_command_list",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_help_packet_") as tmp_dir_str:
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

    print("PHASE8_HELP_PACKET_SELF_TEST=pass")
    print(
        "PHASE8_HELP_PACKET_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 8 help command review packet."
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
        print("PHASE8_HELP_PACKET=fail")
        print("MISSING_PHASE8_HELP_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_HELP_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_HELP_PACKET=fail")
        print("MISSING_PHASE8_HELP_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_HELP_PACKET_MARKERS_END")
        return 1

    print("PHASE8_HELP_PACKET=pass")
    print(f"PHASE8_HELP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_HELP_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())