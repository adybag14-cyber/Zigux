#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
if (SCRIPT_DIR / "zigux").exists() and (SCRIPT_DIR / "lib").exists() and (SCRIPT_DIR / "Documentation").exists():
    ROOT = SCRIPT_DIR
else:
    ROOT = SCRIPT_DIR.parents[1]

REQUIRED_FILES = [
    SCRIPT_PATH,
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "scripts" / "zigux" / "check-phase7-argv-split-parity.py",
    ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md",
    ROOT / "lib" / "argv_split.zig",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase7_build.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_c_harness.c",
]

REQUIRED_DOC_MARKERS = [
    "lane state: helper, fixture, survey, and dedicated external parity slice landed; parked unless a new `argv_split.c` parity issue appears",
    "`scripts/zigux/check-phase7-argv-split-packet.py`",
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
    "`scripts/zigux/check-phase7-argv-split-parity.py`",
    "`python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
    "`python3 scripts/zigux/check-phase7-argv-split-parity.py`",
    "`make -C zigux phase7-validate`",
    "`make -C zigux phase7`",
    "leading-NUL truncation to zero argv entries",
]

REQUIRED_DOCS_ROOT_MARKERS = [
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
]

REQUIRED_DOCS_ROOT_EXACT_COUNT_MARKERS = {
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`": 1,
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py`": 1,
}

REQUIRED_SCRIPTS_ROOT_MARKERS = [
    "- `check-phase7-argv-split-packet.py`",
]

REQUIRED_SCRIPTS_ROOT_EXACT_COUNT_MARKERS = {
    "- `check-phase7-argv-split-packet.py`": 1,
}

REQUIRED_TESTS_ROOT_MARKERS = [
    "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    "`scripts/zigux/check-phase7-argv-split-packet.py`",
]

REQUIRED_TESTS_ROOT_EXACT_COUNT_MARKERS = {
    "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`": 1,
    "`scripts/zigux/check-phase7-argv-split-packet.py`": 2,
}

REQUIRED_PARITY_MARKERS = [
    'SELF_TEST_PAYLOAD_ENV = "PHASE7_ARGV_SPLIT_PARITY_SELFTEST_PAYLOAD"',
    'FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json"',
    'HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_c_harness.c"',
    'SOURCE = ROOT / "lib" / "argv_split.c"',
    'print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST=pass")',
    'print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST_CASE_COUNT=4")',
    'print("PHASE7_ARGV_SPLIT_PARITY=pass")',
]

REQUIRED_MAKE_MARKERS = [
    "scripts/zigux/check-phase7-argv-split-parity.py --self-test",
    "scripts/zigux/check-phase7-argv-split-parity.py",
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
]

REQUIRED_BUILD_MARKERS = [
    "../../lib/argv_split.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "run_argv_split_tests",
    "run_argv_split_survey_tests",
]

REQUIRED_TEST_MARKERS = [
    "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
    "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
    "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
]

REQUIRED_SURVEY_MARKERS = [
    "try std.testing.expectEqual(@as(usize, 0), ready_next_count);",
    'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);',
]

REQUIRED_HELPER_MARKERS = [
    "const leading_nul_expected = [_][]const u8{};",
    "pub fn argvSplitWithArgc",
    "pub fn argvFree",
]

EXPECTED_MANIFEST = {
    "lane_key": "P7-L09",
    "phase": "Phase 7",
    "surveyed_commit": "c9c1299e37e06c409264a94fbe4ab36a7dcc8b4f",
    "anchor": "lib/argv_split.c",
    "roadmap_destinations": ["lib/argv_split.zig"],
}

EXPECTED_SURVEY_SUMMARY = {
    "argv_split_c_lines": 95,
    "preexisting_phase7_test_files": 1,
    "preexisting_phase7_fixture_modules": 1,
    "preexisting_phase7_build_present": True,
    "preexisting_phase7_doc_present": True,
    "preexisting_phase7_helper_present": True,
}

EXPECTED_GAP_DESTINATIONS = {
    "phase7-build-gate": "zigux/tests/phase7_build.zig",
    "phase7-argv-split-helper": "lib/argv_split.zig",
    "phase7-argv-split-dedicated-tests": "zigux/tests/phase7_argv_split.zig",
    "phase7-argv-split-shared-fixtures": "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "phase7-argv-split-c-parity-fixture-layer": "zigux/tests/fixtures/phase7_argv_split.json",
    "phase7-argv-split-packet-checker": "scripts/zigux/check-phase7-argv-split-packet.py",
    "phase7-argv-split-slice-note": "Documentation/zigux/phase7-argv-split-slice.md",
    "phase7-argv-split-survey-gate": "zigux/tests/phase7_argv_split_survey.zig",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


SELF_TEST_FILE_CONTENTS = {
    "Documentation/zigux/README.md": "\n".join(
        [
            "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
            "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
            "",
        ]
    ),
    "scripts/zigux/README.md": "\n".join(
        [
            "- `check-phase7-argv-split-packet.py`",
            "",
        ]
    ),
    "zigux/tests/README.md": "\n".join(
        [
            "`scripts/zigux/check-phase7-argv-split-packet.py`",
            "`scripts/zigux/check-phase7-argv-split-packet.py --self-test` and `scripts/zigux/check-phase7-argv-split-packet.py`",
            "",
        ]
    ),
    "scripts/zigux/check-phase7-argv-split-parity.py": "\n".join(
        [
            'SELF_TEST_PAYLOAD_ENV = "PHASE7_ARGV_SPLIT_PARITY_SELFTEST_PAYLOAD"',
            'FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json"',
            'HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_c_harness.c"',
            'SOURCE = ROOT / "lib" / "argv_split.c"',
            'print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST=pass")',
            'print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST_CASE_COUNT=4")',
            'print("PHASE7_ARGV_SPLIT_PARITY=pass")',
            "",
        ]
    ),
    "Documentation/zigux/phase7-argv-split-slice.md": "\n".join(
        [
            "lane state: helper, fixture, survey, and dedicated external parity slice landed; parked unless a new `argv_split.c` parity issue appears",
            "`scripts/zigux/check-phase7-argv-split-packet.py`",
            "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
            "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
            "`scripts/zigux/check-phase7-argv-split-parity.py`",
            "`python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
            "`python3 scripts/zigux/check-phase7-argv-split-parity.py`",
            "`make -C zigux phase7-validate`",
            "`make -C zigux phase7`",
            "leading-NUL truncation to zero argv entries",
            "",
        ]
    ),
    "lib/argv_split.zig": "\n".join(
        [
            "const leading_nul_expected = [_][]const u8{};",
            "pub fn argvSplitWithArgc() void {}",
            "pub fn argvFree() void {}",
            "",
        ]
    ),
    "zigux/Makefile": "\n".join(
        [
            "scripts/zigux/check-phase7-argv-split-parity.py --self-test",
            "scripts/zigux/check-phase7-argv-split-parity.py",
            "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
            "",
        ]
    ),
    "zigux/tests/phase7_build.zig": "\n".join(
        [
            "../../lib/argv_split.zig",
            "phase7_argv_split.zig",
            "phase7_argv_split_survey.zig",
            "phase7-argv-split-tests",
            "phase7-argv-split-survey-tests",
            "run_argv_split_tests",
            "run_argv_split_survey_tests",
            "",
        ]
    ),
    "zigux/tests/phase7_argv_split.zig": "\n".join(
        [
            "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
            "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
            "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
            "",
        ]
    ),
    "zigux/tests/phase7_argv_split_survey.zig": "\n".join(
        [
            "try std.testing.expectEqual(@as(usize, 0), ready_next_count);",
            'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);',
            "",
        ]
    ),
    "zigux/tests/phase7_argv_split_manifest.json": json.dumps(
        {
            **EXPECTED_MANIFEST,
            "survey_summary": EXPECTED_SURVEY_SUMMARY,
            "gaps": [
                {
                    "id": gap_id,
                    "status": "starter_landed",
                    "zigux_destination": destination,
                    "why_now": "keep the dedicated argv_split Phase 7 packet reviewable",
                }
                for gap_id, destination in EXPECTED_GAP_DESTINATIONS.items()
            ],
        },
        indent=2,
    )
    + "\n",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig": "// self-test fixture\n",
    "zigux/tests/fixtures/phase7_argv_split.json": "{}\n",
    "zigux/tests/fixtures/phase7_argv_split_c_harness.c": "/* self-test harness */\n",
}


def clone_fixture_root(destination_root: Path) -> None:
    for relative_path, content in SELF_TEST_FILE_CONTENTS.items():
        target = destination_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    shutil.copyfile(__file__, destination_root / "check-phase7-argv-split-packet.py")


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "check-phase7-argv-split-packet.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_failure(label: str, root: Path, expected_marker: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase7-argv-split-packet-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "none"
        raise SystemExit(
            f"phase7-argv-split-packet-self-test:{label}:expected:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            actual = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"phase7-argv-split-packet-self-test:baseline_failed:{actual}")

        doc_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_doc = read(doc_path)
        doc_path.write_text(
            original_doc.replace("`scripts/zigux/check-phase7-argv-split-packet.py`", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "packet_doc_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: `scripts/zigux/check-phase7-argv-split-packet.py`",
        )
        doc_path.write_text(original_doc, encoding="utf-8")

        doc_path.write_text(
            original_doc.replace("`scripts/zigux/check-phase7-argv-split-parity.py`", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "doc_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: `scripts/zigux/check-phase7-argv-split-parity.py`",
        )
        doc_path.write_text(original_doc, encoding="utf-8")

        docs_root_path = tmp_root / "Documentation" / "zigux" / "README.md"
        original_docs_root = read(docs_root_path)
        docs_root_path.write_text(
            original_docs_root.replace(
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "docs_root_packet_self_test_marker",
            tmp_root,
            "Documentation/zigux/README.md: `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        docs_root_path.write_text(
            original_docs_root.replace(
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`, `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "docs_root_packet_self_test_duplicate",
            tmp_root,
            "Documentation/zigux/README.md: exact_count:`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`:2!=1",
        )
        docs_root_path.write_text(original_docs_root, encoding="utf-8")

        scripts_root_path = tmp_root / "scripts" / "zigux" / "README.md"
        original_scripts_root = read(scripts_root_path)
        scripts_root_path.write_text(
            original_scripts_root.replace("- `check-phase7-argv-split-packet.py`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "scripts_root_packet_marker",
            tmp_root,
            "scripts/zigux/README.md: - `check-phase7-argv-split-packet.py`",
        )
        scripts_root_path.write_text(original_scripts_root, encoding="utf-8")

        scripts_root_path.write_text(
            original_scripts_root.replace(
                "- `check-phase7-argv-split-packet.py`\n",
                "- `check-phase7-argv-split-packet.py`\n- `check-phase7-argv-split-packet.py`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "scripts_root_packet_duplicate",
            tmp_root,
            "scripts/zigux/README.md: exact_count:- `check-phase7-argv-split-packet.py`:2!=1",
        )
        scripts_root_path.write_text(original_scripts_root, encoding="utf-8")

        tests_root_path = tmp_root / "zigux" / "tests" / "README.md"
        original_tests_root = read(tests_root_path)
        tests_root_path.write_text(
            original_tests_root.replace(
                "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "tests_root_packet_self_test_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
        )
        tests_root_path.write_text(original_tests_root, encoding="utf-8")

        tests_root_path.write_text(
            original_tests_root.replace(
                "`scripts/zigux/check-phase7-argv-split-packet.py`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "tests_root_packet_marker",
            tmp_root,
            "zigux/tests/README.md: exact_count:`scripts/zigux/check-phase7-argv-split-packet.py`:1!=2",
        )
        tests_root_path.write_text(original_tests_root, encoding="utf-8")

        tests_root_path.write_text(
            original_tests_root.replace(
                "`scripts/zigux/check-phase7-argv-split-packet.py`",
                "`scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-argv-split-packet.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "tests_root_packet_duplicate",
            tmp_root,
            "zigux/tests/README.md: exact_count:`scripts/zigux/check-phase7-argv-split-packet.py`:3!=2",
        )
        tests_root_path.write_text(original_tests_root, encoding="utf-8")

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = read(makefile_path)
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase7-argv-split-parity.py --self-test", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            "makefile_marker",
            tmp_root,
            "zigux/Makefile: scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        parity_path = tmp_root / "scripts" / "zigux" / "check-phase7-argv-split-parity.py"
        original_parity = read(parity_path)
        parity_path.write_text(
            original_parity.replace('print("PHASE7_ARGV_SPLIT_PARITY=pass")', "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "parity_marker",
            tmp_root,
            'scripts/zigux/check-phase7-argv-split-parity.py: print("PHASE7_ARGV_SPLIT_PARITY=pass")',
        )
        parity_path.write_text(original_parity, encoding="utf-8")

        survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        original_survey = read(survey_path)
        survey_path.write_text(
            original_survey.replace(
                "try std.testing.expectEqual(@as(usize, 0), ready_next_count);", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            "survey_marker",
            tmp_root,
            "zigux/tests/phase7_argv_split_survey.zig: try std.testing.expectEqual(@as(usize, 0), ready_next_count);",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        helper_path = tmp_root / "lib" / "argv_split.zig"
        original_helper = read(helper_path)
        helper_path.write_text(
            original_helper.replace("pub fn argvFree() void {}\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "helper_ownership_marker",
            tmp_root,
            "lib/argv_split.zig: pub fn argvFree",
        )
        helper_path.write_text(original_helper, encoding="utf-8")

        manifest_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_manifest.json"
        manifest = json.loads(read(manifest_path))
        manifest["lane_key"] = "wrong"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "manifest_lane",
            tmp_root,
            "PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_START",
        )
        manifest_path.write_text(
            SELF_TEST_FILE_CONTENTS["zigux/tests/phase7_argv_split_manifest.json"],
            encoding="utf-8",
        )

        manifest = json.loads(read(manifest_path))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase7-argv-split-helper":
                gap["zigux_destination"] = "lib/cmdline.zig"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "manifest_gap_destination",
            tmp_root,
            "gaps:phase7-argv-split-helper:zigux_destination",
        )
        manifest_path.write_text(
            SELF_TEST_FILE_CONTENTS["zigux/tests/phase7_argv_split_manifest.json"],
            encoding="utf-8",
        )

        manifest = json.loads(read(manifest_path))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase7-argv-split-c-parity-fixture-layer":
                gap["zigux_destination"] = "zigux/tests/fixtures/phase7_argv_split_c_harness.c"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "manifest_c_parity_gap_destination",
            tmp_root,
            "gaps:phase7-argv-split-c-parity-fixture-layer:zigux_destination",
        )
        manifest_path.write_text(
            SELF_TEST_FILE_CONTENTS["zigux/tests/phase7_argv_split_manifest.json"],
            encoding="utf-8",
        )

        manifest = json.loads(read(manifest_path))
        for gap in manifest["gaps"]:
            if gap["id"] == "phase7-argv-split-packet-checker":
                gap["zigux_destination"] = "scripts/zigux/check-phase7-argv-split-parity.py"
                break
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            "manifest_packet_checker_gap_destination",
            tmp_root,
            "gaps:phase7-argv-split-packet-checker:zigux_destination",
        )
        manifest_path.write_text(
            SELF_TEST_FILE_CONTENTS["zigux/tests/phase7_argv_split_manifest.json"],
            encoding="utf-8",
        )

    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass")
    print("PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_CASE_COUNT=17")
    return 0


def assert_markers(label: str, content: str, markers: list[str], missing: list[tuple[str, str]]) -> None:
    for marker in markers:
        if marker not in content:
            missing.append((label, marker))


def assert_exact_count_markers(
    label: str,
    content: str,
    expected_counts: dict[str, int],
    missing: list[tuple[str, str]],
) -> None:
    for marker, expected_count in expected_counts.items():
        actual_count = content.count(marker)
        if actual_count != expected_count:
            missing.append((label, f"exact_count:{marker}:{actual_count}!={expected_count}"))


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())

missing_files = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
if missing_files:
    print("PHASE7_ARGV_SPLIT_PACKET=fail")
    print("PHASE7_ARGV_SPLIT_PACKET_MISSING_FILES_START")
    for item in missing_files:
        print(item)
    print("PHASE7_ARGV_SPLIT_PACKET_MISSING_FILES_END")
    raise SystemExit(1)

docs_root = read(ROOT / "Documentation" / "zigux" / "README.md")
scripts_root = read(ROOT / "scripts" / "zigux" / "README.md")
tests_root = read(ROOT / "zigux" / "tests" / "README.md")
doc = read(ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md")
parity = read(ROOT / "scripts" / "zigux" / "check-phase7-argv-split-parity.py")
makefile = read(ROOT / "zigux" / "Makefile")
build = read(ROOT / "zigux" / "tests" / "phase7_build.zig")
tests = read(ROOT / "zigux" / "tests" / "phase7_argv_split.zig")
survey = read(ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig")
helper = read(ROOT / "lib" / "argv_split.zig")
manifest = json.loads(read(ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json"))

missing_markers: list[tuple[str, str]] = []
assert_markers("Documentation/zigux/README.md", docs_root, REQUIRED_DOCS_ROOT_MARKERS, missing_markers)
assert_exact_count_markers(
    "Documentation/zigux/README.md",
    docs_root,
    REQUIRED_DOCS_ROOT_EXACT_COUNT_MARKERS,
    missing_markers,
)
assert_markers("scripts/zigux/README.md", scripts_root, REQUIRED_SCRIPTS_ROOT_MARKERS, missing_markers)
assert_exact_count_markers(
    "scripts/zigux/README.md",
    scripts_root,
    REQUIRED_SCRIPTS_ROOT_EXACT_COUNT_MARKERS,
    missing_markers,
)
assert_markers("zigux/tests/README.md", tests_root, REQUIRED_TESTS_ROOT_MARKERS, missing_markers)
assert_exact_count_markers(
    "zigux/tests/README.md",
    tests_root,
    REQUIRED_TESTS_ROOT_EXACT_COUNT_MARKERS,
    missing_markers,
)
assert_markers("Documentation/zigux/phase7-argv-split-slice.md", doc, REQUIRED_DOC_MARKERS, missing_markers)
assert_markers("scripts/zigux/check-phase7-argv-split-parity.py", parity, REQUIRED_PARITY_MARKERS, missing_markers)
assert_markers("zigux/Makefile", makefile, REQUIRED_MAKE_MARKERS, missing_markers)
assert_markers("zigux/tests/phase7_build.zig", build, REQUIRED_BUILD_MARKERS, missing_markers)
assert_markers("zigux/tests/phase7_argv_split.zig", tests, REQUIRED_TEST_MARKERS, missing_markers)
assert_markers("zigux/tests/phase7_argv_split_survey.zig", survey, REQUIRED_SURVEY_MARKERS, missing_markers)
assert_markers("lib/argv_split.zig", helper, REQUIRED_HELPER_MARKERS, missing_markers)

if missing_markers:
    print("PHASE7_ARGV_SPLIT_PACKET=fail")
    print("PHASE7_ARGV_SPLIT_PACKET_MISSING_MARKERS_START")
    for label, marker in missing_markers:
        print(f"{label}: {marker}")
    print("PHASE7_ARGV_SPLIT_PACKET_MISSING_MARKERS_END")
    raise SystemExit(1)

manifest_errors: list[str] = []
for key, expected_value in EXPECTED_MANIFEST.items():
    if manifest.get(key) != expected_value:
        manifest_errors.append(key)

survey_summary = manifest.get("survey_summary", {})
for key, expected_value in EXPECTED_SURVEY_SUMMARY.items():
    if survey_summary.get(key) != expected_value:
        manifest_errors.append(f"survey_summary:{key}")

gaps = manifest.get("gaps")
if not isinstance(gaps, list):
    manifest_errors.append("gaps")
else:
    for gap_id, destination in EXPECTED_GAP_DESTINATIONS.items():
        matches = [gap for gap in gaps if gap.get("id") == gap_id]
        if len(matches) != 1:
            manifest_errors.append(f"gaps:{gap_id}")
            continue
        gap = matches[0]
        if gap.get("status") != "starter_landed":
            manifest_errors.append(f"gaps:{gap_id}:status")
        if gap.get("zigux_destination") != destination:
            manifest_errors.append(f"gaps:{gap_id}:zigux_destination")
        if not gap.get("why_now"):
            manifest_errors.append(f"gaps:{gap_id}:why_now")

if manifest_errors:
    print("PHASE7_ARGV_SPLIT_PACKET=fail")
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_START")
    for item in manifest_errors:
        print(item)
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_END")
    raise SystemExit(1)

print("PHASE7_ARGV_SPLIT_PACKET=pass")
print(f"PHASE7_ARGV_SPLIT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(
    "PHASE7_ARGV_SPLIT_PACKET_REQUIRED_MARKER_COUNT="
    f"{len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_DOCS_ROOT_EXACT_COUNT_MARKERS) + len(REQUIRED_SCRIPTS_ROOT_MARKERS) + len(REQUIRED_SCRIPTS_ROOT_EXACT_COUNT_MARKERS) + len(REQUIRED_TESTS_ROOT_MARKERS) + len(REQUIRED_TESTS_ROOT_EXACT_COUNT_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_PARITY_MARKERS) + len(REQUIRED_MAKE_MARKERS) + len(REQUIRED_BUILD_MARKERS) + len(REQUIRED_TEST_MARKERS) + len(REQUIRED_SURVEY_MARKERS) + len(REQUIRED_HELPER_MARKERS)}"
)