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
CMDLINE_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-cmdline-packet.py")
ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")
STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py")
RBTREE_PARITY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-rbtree-parity.py")

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
    "scripts/zigux/check-phase7-cmdline-packet.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
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
    "python3 scripts/zigux/check-phase7-cmdline-packet.py",
    "python3 scripts/zigux/check-phase7-cmdline-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py",
    "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py",
    "python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
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
    Path("lib/rbtree.zig"): [
        "pub const Node = struct",
        "pub const RootCached = struct",
        "pub fn add(",
        "pub fn rb_find_add_cached(",
    ],
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
            "phase7-string-helpers-format-boundary",
            "string_helpers_sample_boundary_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "string_helpers_format_boundary_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
            "phase7-cmdline-test",
            "phase7-cmdline-survey",
            "cmdline_survey_step.dependOn(&run_cmdline_survey_tests.step)",
            "phase7-argv-split-test",
            "phase7-argv-split-survey",
            "argv_split_survey_step.dependOn(&run_argv_split_survey_tests.step)",
            "phase7-rbtree-test",
            "phase7-rbtree-survey",
            'const test_step = b.step("test", "Run the Phase 7 runtime helper tests");',
            "test_step.dependOn(&run_string_helpers_tests.step)",
            "test_step.dependOn(&run_string_helpers_survey_tests.step)",
            "test_step.dependOn(&run_string_helpers_sample_boundary_tests.step)",
            "test_step.dependOn(&run_string_helpers_format_boundary_tests.step)",
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
    CMDLINE_PACKET_CHECKER_PATH,
    ARGV_SPLIT_PACKET_CHECKER_PATH,
    STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH,
    RBTREE_PARITY_PACKET_CHECKER_PATH,
    Path("lib/string_helpers.zig"),
    Path("lib/cmdline.zig"),
    Path("lib/argv_split.zig"),
    Path("lib/rbtree.zig"),
]
REQUIRED_MAKEFILE_LINES = [
    "phase7-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
]
SELF_TEST_CASE_COUNT = 11


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    normalized_marker = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized_marker)


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


def run_checker_self_test(root: Path, checker_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker_path), "--self-test"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker_path.as_posix()} self-test failed: {detail}")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
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
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            raise ValidationError(f"phase7 make route missing: {marker}")
        if count != 1:
            raise ValidationError(f"phase7 make route count drift: {marker} ({count} != 1)")

    run_checker_self_test(root, CHECKER_PATH)
    run_checker(root, CHECKER_PATH)
    run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)
    run_checker(root, BUILD_WIRING_CHECKER_PATH)
    run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)
    run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")
    run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)
    run_checker(root, CMDLINE_PACKET_CHECKER_PATH)
    run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)
    run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)
    run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)
    run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "--root")
    run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)
    run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / CATALOG_PATH, "phase7 leaf-library evidence catalog\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write(root / BUILD_PATH, "\n".join(EXPECTED_BUILD_WIRING_EVIDENCE[0]["expected_markers"]) + "\n")
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": EXPECTED_SCOPE,
                "current_direct_readback_companions": EXPECTED_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "current_direct_helper_evidence": [
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
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/cmdline.zig")],
                    },
                    {
                        "key": "argv_split",
                        "zig_helper": "lib/argv_split.zig",
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/argv_split.zig")],
                    },
                    {
                        "key": "rbtree",
                        "zig_helper": "lib/rbtree.zig",
                        "expected_markers": EXPECTED_HELPER_MARKERS[Path("lib/rbtree.zig")],
                    },
                ],
                "current_build_wiring_evidence": EXPECTED_BUILD_WIRING_EVIDENCE,
                "current_replay_inventory": EXPECTED_REPLAYS,
                "current_repo_reality_gaps": EXPECTED_GAPS,
            },
            indent=2,
        ) + "\n",
    )
    write(
        root / Path("lib/string_helpers.zig"),
        "\n".join(EXPECTED_HELPER_MARKERS[Path("lib/string_helpers.zig")]) + "\n",
    )
    write(
        root / Path("lib/cmdline.zig"),
        "\n".join(EXPECTED_HELPER_MARKERS[Path("lib/cmdline.zig")]) + "\n",
    )
    write(
        root / Path("lib/argv_split.zig"),
        "\n".join(EXPECTED_HELPER_MARKERS[Path("lib/argv_split.zig")]) + "\n",
    )
    write(
        root / Path("lib/rbtree.zig"),
        "\n".join(EXPECTED_HELPER_MARKERS[Path("lib/rbtree.zig")]) + "\n",
    )
    write(
        root / Path("scripts/zigux/validate-phase7.py"),
        "\n".join(
            [
                'CHECKER_PATH = Path("scripts/zigux/check-phase7-shared-surface.py")',
                'BUILD_WIRING_CHECKER_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")',
                'MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")',
                'CMDLINE_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-cmdline-packet.py")',
                'ARGV_SPLIT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-argv-split-packet.py")',
                'STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py")',
                'RBTREE_PARITY_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase7-rbtree-parity.py")',
                'run_checker_self_test(root, CHECKER_PATH)',
                'run_checker(root, CHECKER_PATH)',
                'run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)',
                'run_checker(root, BUILD_WIRING_CHECKER_PATH)',
                'run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)',
                'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")',
                'run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)',
                'run_checker(root, CMDLINE_PACKET_CHECKER_PATH)',
                'run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)',
                'run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)',
                'run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)',
                'run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "--root")',
                'run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)',
                'run_checker(root, RBTREE_PARITY_PACKET_CHECKER_PATH)',
            ]
        ) + "\n",
    )
    write(
        root / CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--repo-root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_SHARED_SURFACE_SELF_TEST=pass' if args.self_test else 'PHASE7_SHARED_SURFACE=pass')\n",
    )
    write(
        root / BUILD_WIRING_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--repo-root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_BUILD_WIRING_SELF_TEST=pass' if args.self_test else 'PHASE7_BUILD_WIRING=pass')\n",
    )
    write(
        root / MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "from pathlib import Path\n"
        "REQUIRED_VALIDATOR_MARKERS = [\n"
        "    'run_checker_self_test(root, CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, BUILD_WIRING_CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, CMDLINE_PACKET_CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)',\n"
        "    'run_checker_self_test(root, RBTREE_PARITY_PACKET_CHECKER_PATH)',\n"
        "]\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--root', default='.')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "validator = (Path(args.root) / 'scripts/zigux/validate-phase7.py').read_text(encoding='utf-8')\n"
        "for marker in REQUIRED_VALIDATOR_MARKERS:\n"
        "    if marker not in validator:\n"
        "        raise SystemExit(f'missing validator marker: {marker}')\n"
        "print('PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass' if args.self_test else 'PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass')\n",
    )
    write(
        root / CMDLINE_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--repo-root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_CMDLINE_PACKET_SELF_TEST=pass' if args.self_test else 'PHASE7_CMDLINE_PACKET=pass')\n",
    )
    write(
        root / ARGV_SPLIT_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--repo-root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_ARGV_SPLIT_PACKET_SELF_TEST=pass' if args.self_test else 'PHASE7_ARGV_SPLIT_PACKET=pass')\n",
    )
    write(
        root / STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET_SELF_TEST=pass' if args.self_test else 'PHASE7_STRING_HELPERS_FORMAT_BOUNDARY_PACKET=pass')\n",
    )
    write(
        root / RBTREE_PARITY_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\n"
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--repo-root')\n"
        "parser.add_argument('--self-test', action='store_true')\n"
        "args = parser.parse_args()\n"
        "print('PHASE7_RBTREE_PARITY_SELF_TEST=pass' if args.self_test else 'PHASE7_RBTREE_PARITY=pass')\n",
    )


def _expect_failure(root: Path) -> None:
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise AssertionError(f"marker not found: {old}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0

        (root / ARGV_SPLIT_PACKET_CHECKER_PATH).unlink()
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(
            root / MAKEFILE_PATH,
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-shared-surface.py --self-test",
        )
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / Path("scripts/zigux/validate-phase7.py"), "run_checker_self_test(root, CHECKER_PATH)", "run_checker(root, CHECKER_PATH)")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / Path("scripts/zigux/validate-phase7.py"), "run_checker_self_test(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH)", "run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, \"--root\")")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / Path("scripts/zigux/validate-phase7.py"), "run_checker_self_test(root, ARGV_SPLIT_PACKET_CHECKER_PATH)", "run_checker(root, ARGV_SPLIT_PACKET_CHECKER_PATH)")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / Path("scripts/zigux/validate-phase7.py"), "run_checker_self_test(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH)", "run_checker(root, STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, \"--root\")")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / BUILD_PATH, "phase7-string-helpers-format-boundary", "phase7-string-helpers-format-gap")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / Path("lib/argv_split.zig"), "pub fn argvSplit", "pub fn splitArgv")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / STRING_HELPERS_FORMAT_BOUNDARY_PACKET_CHECKER_PATH, "parser.add_argument('--self-test', action='store_true')", "parser.add_argument('--self-check', action='store_true')")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / ARGV_SPLIT_PACKET_CHECKER_PATH, "parser.add_argument('--self-test', action='store_true')", "parser.add_argument('--self-check', action='store_true')")
        _expect_failure(root)
        cases_run += 1

        scaffold_repo(root)
        _replace_once(root / CHECKER_PATH, "parser.add_argument('--self-test', action='store_true')", "parser.add_argument('--self-check', action='store_true')")
        _expect_failure(root)
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE7_VALIDATE_SELF_TEST=pass")
    print(f"PHASE7_VALIDATE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


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
