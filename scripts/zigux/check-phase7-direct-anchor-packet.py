#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


DIRECT_ANCHOR = "zigux/tests/phase7_rbtree_survey.zig"
BROADER_PACKET_PATHS = (
    "Documentation/zigux/phase7-helper-lane-sequencing.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "zigux/tests/phase7_build.zig",
)
TESTS_README_MARKERS = (
    "Phase 7 review packet",
    f"current direct-readback Phase 7 anchor: `{DIRECT_ANCHOR}`",
    "repo-reality warning for the broader Phase 7 rbtree packet:",
    "treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again",
    "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone",
    "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
)
DIRECT_NOTE_MARKERS = (
    f"Current direct-readback Phase 7 anchor: `{DIRECT_ANCHOR}`",
    "Broader Phase 7 rbtree packet currently missing on `master`:",
    "Treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented as shipped direct evidence.",
    "Leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond the surviving rbtree anchor.",
)
SURVEY_MARKERS = (
    'const active_lane_key = "P7-L13";',
    'try std.testing.expectEqualStrings("P7-L13", active_lane_key);',
    f'"current direct-readback Phase 7 anchor: `{DIRECT_ANCHOR}`"',
    '"repo-reality warning for the broader Phase 7 rbtree packet:"',
    '"treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again"',
    '"keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone"',
    '"leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree"',
)


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    return path.read_text(encoding="utf-8")


def require_markers(path: str, text: str, markers: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{path}: missing marker: {marker}")
    return missing


def check_root(root: Path) -> list[str]:
    tests_readme = read_text(root, "zigux/tests/README.md")
    direct_note = read_text(root, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md")
    survey = read_text(root, DIRECT_ANCHOR)

    errors: list[str] = []
    errors.extend(require_markers("zigux/tests/README.md", tests_readme, TESTS_README_MARKERS))
    errors.extend(
        require_markers(
            "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
            direct_note,
            DIRECT_NOTE_MARKERS,
        )
    )
    errors.extend(require_markers(DIRECT_ANCHOR, survey, SURVEY_MARKERS))

    for relpath in BROADER_PACKET_PATHS:
        tests_marker = f"`{relpath}`"
        direct_note_marker = f"- `{relpath}`"
        survey_marker = f'"`{relpath}`"'
        if tests_marker not in tests_readme:
            errors.append(f"zigux/tests/README.md: missing broader packet path {relpath}")
        if direct_note_marker not in direct_note:
            errors.append(
                "Documentation/zigux/phase7-rbtree-direct-anchor-note.md: "
                f"missing broader packet path {relpath}"
            )
        if survey_marker not in survey:
            errors.append(f"{DIRECT_ANCHOR}: missing broader packet path {relpath}")

    return errors


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    broader_packet_block = "\n".join(f"    `{path}`" for path in BROADER_PACKET_PATHS)
    broader_note_block = "\n".join(f"- `{path}`" for path in BROADER_PACKET_PATHS)
    broader_survey_block = "\n".join(f'        "`{path}`",' for path in BROADER_PACKET_PATHS)

    write(
        root / "zigux/tests/README.md",
        "# zigux/tests\n\n"
        "Phase 7 review packet\n"
        f"current direct-readback Phase 7 anchor: `{DIRECT_ANCHOR}`\n"
        "repo-reality warning for the broader Phase 7 rbtree packet:\n"
        f"{broader_packet_block}\n"
        "treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again\n"
        "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone\n"
        "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree\n",
    )
    write(
        root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md",
        "# Phase 7 Rbtree Direct Anchor Note\n\n"
        f"Current direct-readback Phase 7 anchor: `{DIRECT_ANCHOR}`\n\n"
        "Broader Phase 7 rbtree packet currently missing on `master`:\n"
        f"{broader_note_block}\n\n"
        "Treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented as shipped direct evidence.\n\n"
        "Leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond the surviving rbtree anchor.\n",
    )
    write(
        root / DIRECT_ANCHOR,
        "const std = @import(\"std\");\n\n"
        'const active_lane_key = "P7-L13";\n\n'
        "test \"phase 7 direct anchor packet stays aligned\" {\n"
        '    try std.testing.expectEqualStrings("P7-L13", active_lane_key);\n'
        '    _ = "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`";\n'
        '    _ = "repo-reality warning for the broader Phase 7 rbtree packet:";\n'
        "    const broader_packet_paths = [_][]const u8{\n"
        f"{broader_survey_block}\n"
        "    };\n"
        '    _ = "treat those paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that need fresh reread or re-materialization before they are presented here as shipped direct evidence again";\n'
        '    _ = "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor instead of reconstructing the broader helper packet from older route names alone";\n'
        '    _ = "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree";\n'
        "    _ = broader_packet_paths;\n"
        "}\n",
    )


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase7_direct_anchor_"))
    try:
        build_self_test_fixture(tmp_root)
        assert not check_root(tmp_root)

        tests_path = tmp_root / "zigux/tests/README.md"
        original_tests = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(
            original_tests.replace(
                "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert any("widening beyond rbtree" in error for error in check_root(tmp_root))
        tests_path.write_text(original_tests, encoding="utf-8")

        note_path = tmp_root / "Documentation/zigux/phase7-rbtree-direct-anchor-note.md"
        original_note = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            original_note.replace(
                "- `zigux/tests/phase7_build.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert any("phase7_build.zig" in error for error in check_root(tmp_root))
        note_path.write_text(original_note, encoding="utf-8")

        survey_path = tmp_root / DIRECT_ANCHOR
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                '    try std.testing.expectEqualStrings("P7-L13", active_lane_key);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert any("P7-L13" in error for error in check_root(tmp_root))
        print("PHASE7_DIRECT_ANCHOR_PACKET_SELF_TEST=pass")
        print("PHASE7_DIRECT_ANCHOR_PACKET_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(tmp_root)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the surviving Phase 7 direct-anchor packet for rbtree reminder drift."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing Documentation/zigux and zigux/tests.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check_root(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE7_DIRECT_ANCHOR_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
