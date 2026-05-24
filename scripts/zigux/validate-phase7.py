#!/usr/bin/env python3
"""Validate the bounded Phase 7 leaf-library evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_FILE_PATH = Path(__file__).resolve()
ROOT = _FILE_PATH.parents[2] if len(_FILE_PATH.parents) > 2 else _FILE_PATH.parent

CATALOG_PATH = Path("Documentation/zigux/phase7-leaf-library-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase7_leaf_library_evidence_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase7_build.zig")
CHECKER_PATH = Path("scripts/zigux/check-phase7-shared-surface.py")
BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

EXPECTED_PACKET = "phase7-leaf-library-evidence"
EXPECTED_PHASE = "Phase 7"
EXPECTED_SCOPE = "shared leaf-library evidence rows and validation foothold only"
EXPECTED_COMPANIONS = [
    "Documentation/zigux/phase7-leaf-library-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase7-shared-surface.py",
    "scripts/zigux/check-phase7-build-wiring.py",
    "scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase7_leaf_library_evidence_manifest.json",
    "zigux/tests/phase7_build.zig",
    "zigux/Makefile",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
]
EXPECTED_DIRECT_HELPER_EVIDENCE = [
    {
        "key": "string_helpers",
        "zig_helper": "lib/string_helpers.zig",
        "expected_markers": [
            "pub const STRING_UNITS_10",
            "pub const KasprintfStrarrayResult",
            "pub fn kstrdupQuotable",
            "pub fn kstrdupQuotableCmdline",
        ],
    },
    {
        "key": "string_helpers_parse_int_array",
        "zig_helper": "lib/string_helpers.zig",
        "expected_markers": [
            "pub const ParseIntArrayError",
            "pub fn parseIntArray",
        ],
    },
    {
        "key": "cmdline",
        "zig_helper": "lib/cmdline.zig",
        "expected_markers": ["pub fn parseOptionStr", "pub fn getOption"],
    },
    {
        "key": "argv_split",
        "zig_helper": "lib/argv_split.zig",
        "expected_markers": ["pub const ArgvSplitResult", "pub fn argvSplit"],
    },
    {
        "key": "rbtree",
        "zig_helper": "lib/rbtree.zig",
        "expected_markers": ["pub const Node = struct", "pub const RootCached = struct", "pub fn add(", "pub fn rb_find_add_cached("],
    },
]
EXPECTED_ROADMAP_ANCHORS = [
    "lib/string_helpers.c",
    "lib/cmdline.c",
    "lib/argv_split.c",
    "lib/rbtree.c",
]
EXPECTED_REPLAYS = [
    "python3 scripts/zigux/check-phase7-shared-surface.py",
    "python3 scripts/zigux/check-phase7-shared-surface.py --self-test",
    "python3 scripts/zigux/check-phase7-build-wiring.py",
    "python3 scripts/zigux/check-phase7-build-wiring.py --self-test",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
    "python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/validate-phase7.py",
    "python3 scripts/zigux/validate-phase7.py --self-test",
    "make -C zigux phase7-validate",
]
EXPECTED_GAPS: list[str] = []
EXPECTED_HELPER_MARKERS = {
    Path("lib/string_helpers.zig"): [
        "pub const STRING_UNITS_10",
        "pub const KasprintfStrarrayResult",
        "pub fn kstrdupQuotable",
        "pub fn kstrdupQuotableCmdline",
        "pub const ParseIntArrayError",
        "pub fn parseIntArray",
    ],
    Path("lib/cmdline.zig"): ["pub fn parseOptionStr", "pub fn getOption"],
    Path("lib/argv_split.zig"): ["pub const ArgvSplitResult", "pub fn argvSplit"],
    Path("lib/rbtree.zig"): ["pub const Node = struct", "pub const RootCached = struct", "pub fn add(", "pub fn rb_find_add_cached("],
}
EXPECTED_BUILD_WIRING_EVIDENCE = [
    {
        "path": "zigux/tests/phase7_build.zig",
        "expected_markers": [
            "../../lib/string_helpers.zig",
            "../../lib/cmdline.zig",
            "../../lib/argv_split.zig",
            "../../lib/rbtree.zig",
            "phase7-string-helpers-test",
            "phase7-string-helpers-survey",
            "phase7-string-helpers-sample-boundary",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "phase7-cmdline-test",
            "phase7-cmdline-survey",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)",
            "phase7-argv-split-test",
            "phase7-argv-split-survey",
            "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)",
            "phase7-rbtree-test",
            "phase7-rbtree-survey",
            "const test_step = b.step(\"test\", \"Run the Phase 7 runtime helper tests\");",
            "test_step.dependOn(&run_string_helpers_tests.step)",
            "test_step.dependOn(&run_string_helpers_survey_tests.step)",
            "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "test_step.dependOn(&run_cmdline_tests.step)",
            "test_step.dependOn(&run_cmdline_survey_tests.step)",
            "test_step.dependOn(&run_argv_split_tests.step)",
            "test_step.dependOn(&run_argv_split_survey_tests.step)",
            "test_step.dependOn(&run_rbtree_tests.step)",
            "test_step.dependOn(&run_rbtree_survey_tests.step)",
        ],
    },
    {
        "path": "zigux/Makefile",
        "expected_markers": [
            "phase7-validate:",
            "$(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "$(PYTHON) scripts/zigux/validate-phase7.py",
        ],
    },
]
REQUIRED_FILES = [
    CATALOG_PATH,
    MANIFEST_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
    CHECKER_PATH,
    BUILD_WIRING_CHECKER_PATH,
    MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
    ARGV_SPLIT_PACKET_CHECKER_PATH,
    REVIEW_CHECKLIST_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
    Path("lib/rbtree.zig"),
]
SELF_TEST_CASE_COUNT = 5


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def run_checker(root: Path, checker_path: Path, root_flag: str = "--repo-root") -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker_path), root_flag, str(root)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker_path.as_posix()} failed: {detail}")


def validate(root: Path) -> None:
    missing = [str(path) for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    manifest = read_json(root / MANIFEST_PATH)
    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase7 packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase7 phase drift")
    if manifest.get("lane_scope") != EXPECTED_SCOPE:
        raise ValidationError("phase7 scope drift")
    if manifest.get("current_direct_readback_companions") != EXPECTED_COMPANIONS:
        raise ValidationError("phase7 companion drift")
    if manifest.get("current_direct_helper_evidence") != EXPECTED_DIRECT_HELPER_EVIDENCE:
        raise ValidationError("phase7 direct helper evidence drift")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase7 roadmap anchor drift")
    if manifest.get("current_replay_inventory") != EXPECTED_REPLAYS:
        raise ValidationError("phase7 replay inventory drift")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_GAPS:
        raise ValidationError("phase7 repo-reality gaps drift")
    if manifest.get("current_build_wiring_evidence") != EXPECTED_BUILD_WIRING_EVIDENCE:
        raise ValidationError("phase7 build-wiring evidence drift")

    for rel_path, markers in EXPECTED_HELPER_MARKERS.items():
        helper_text = read_text(root / rel_path)
        for marker in markers:
            if marker not in helper_text:
                raise ValidationError(f"phase7 helper marker missing in {rel_path.as_posix()}: {marker}")

    build_text = read_text(root / BUILD_PATH)
    for marker in EXPECTED_BUILD_WIRING_EVIDENCE[0]["expected_markers"]:
        if marker not in build_text:
            raise ValidationError(f"phase7 build marker missing: {marker}")

    makefile = read_text(root / MAKEFILE_PATH)
    for marker in EXPECTED_BUILD_WIRING_EVIDENCE[1]["expected_markers"]:
        if marker not in makefile:
            raise ValidationError(f"phase7 make route missing: {marker}")

    run_checker(root, CHECKER_PATH)
    run_checker(root, BUILD_WIRING_CHECKER_PATH)
    run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")
    run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n")
    write(root / CATALOG_PATH, "phase7 leaf library evidence\n")
    write(root / MAKEFILE_PATH, "phase7-validate:\n$(PYTHON) scripts/zigux/validate-phase7.py --self-test\n$(PYTHON) scripts/zigux/validate-phase7.py\n")
    write(root / BUILD_PATH, "\n".join(EXPECTED_BUILD_WIRING_EVIDENCE[0]["expected_markers"]) + "\n")
    write(root / CHECKER_PATH, "#!/usr/bin/env python3\nimport argparse\nprint('PHASE7_SHARED_SURFACE=pass')\n")
    write(root / BUILD_WIRING_CHECKER_PATH, "#!/usr/bin/env python3\nimport argparse\nprint('PHASE7_BUILD_WIRING=pass')\n")
    write(root / MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "#!/usr/bin/env python3\nimport argparse\nprint('PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass')\n")
    write(root / ARGV_SPLIT_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\nimport argparse\nprint('PHASE7_ARGV_SPLIT_PACKET=pass')\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_COMPANIONS,
                "current_direct_helper_evidence": EXPECTED_DIRECT_HELPER_EVIDENCE,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_build_wiring_evidence": EXPECTED_BUILD_WIRING_EVIDENCE,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_GAPS,
            },
            indent=2,
        ) + "\n",
    )
    for rel_path, markers in EXPECTED_HELPER_MARKERS.items():
        write(root / rel_path, "\n".join(markers) + "\n")


def expect_failure(root: Path, rel_path: Path, marker: str, replacement: str = "") -> None:
    path = root / rel_path
    original = read_text(path)
    updated = original.replace(marker, replacement, 1)
    if updated == original:
        raise AssertionError(f"marker not found: {marker}")
    write(path, updated)
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases = [
            (MANIFEST_PATH, '"Documentation/zigux/review-checklist.md"', '"Documentation/zigux/review-notes.md"'),
            (MANIFEST_PATH, '"pub fn argvSplit"', '"pub fn argvSplitTokens"'),
            (BUILD_PATH, "../../lib/rbtree.zig", ""),
            (MAKEFILE_PATH, "phase7-validate:", ""),
            (Path("lib/rbtree.zig"), "pub fn rb_find_add_cached(", ""),
        ]
        cases_run = 0
        for rel_path, marker, replacement in cases:
            scaffold_repo(root)
            expect_failure(root, rel_path, marker, replacement)
            cases_run += 1
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE7_VALIDATE_SELF_TEST=pass")
    print(f"PHASE7_VALIDATE_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE7_VALIDATE=fail: {exc}")
        return 1
    print("PHASE7_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
