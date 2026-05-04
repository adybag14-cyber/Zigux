#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux" / "tests" / "phase7_build.zig"
MAKEFILE_PATH = ROOT / "zigux" / "Makefile"
FIXTURE_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json"
REQUIRED_PATHS = [BUILD_PATH, MAKEFILE_PATH, FIXTURE_PATH]

IMPORTED_HELPER_RE = re.compile(
    r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"',
    re.S,
)
STANDALONE_SURVEY_RE = re.compile(
    r'createStandaloneTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)"',
    re.S,
)
RUN_CALL_RE = re.compile(
    r'const\s+\w+\s*=\s*addTestRun\(\s*'
    r'b,\s*"([^"]+)",\s*\w+,\s*(null|repo_root)\s*,?\s*\)',
    re.S,
)
DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_PATH_RE = re.compile(r'b\.path\("([^"]+)"\)')
PHASE7_VALIDATE_BLOCK_RE = re.compile(r"^phase7-validate:\n((?:\t.*\n)+)", re.M)
PHASE7_TEST_BLOCK_RE = re.compile(r"^phase7-test:\n((?:\t.*\n)+)", re.M)
MAKEFILE_COMMAND_RE = re.compile(
    r"\$\(PYTHON\)\s+(scripts/zigux/[A-Za-z0-9._-]+\.py(?: --self-test)?)"
)
MAKEFILE_TEST_COMMAND_RE = re.compile(
    r"\$\(ZIG\)\s+(build test --build-file zigux/tests/[A-Za-z0-9_]+\.zig(?: --summary all)?)"
)
UNEXPECTED_BUILD_MARKERS = ["../../tools/lib/", "zigux/tests/build.zig"]
EXPECTED_SHARED_TEST_COMMAND = "zig build test --build-file zigux/tests/phase7_build.zig --summary all"
EXPECTED_REPO_ROOT_RUN_CWDS = [
    "phase7-cmdline-survey-tests",
    "phase7-argv-split-survey-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-string-helpers-sample-boundary-tests",
    "phase7-rbtree-survey-tests",
]


def rel_or_abs(path: Path, root: Path = ROOT) -> str:
    if path.is_relative_to(root):
        return str(path.relative_to(root))
    return str(path)


def collect_missing_paths(
    paths: list[Path] | tuple[Path, ...], root: Path = ROOT
) -> list[str]:
    return [rel_or_abs(path, root) for path in paths if not path.exists()]


def print_missing_paths(missing: list[str]) -> None:
    print("PHASE7_BUILD_INVENTORY=fail")
    print("PHASE7_BUILD_INVENTORY_MISSING_FILES_START")
    for item in missing:
        print(item)
    print("PHASE7_BUILD_INVENTORY_MISSING_FILES_END")


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def collect_unexpected_build_hits(build_text: str) -> list[str]:
    return [marker for marker in UNEXPECTED_BUILD_MARKERS if marker in build_text]


def print_unexpected_build_hits(hits: list[str]) -> None:
    print("PHASE7_BUILD_INVENTORY=fail")
    print("PHASE7_BUILD_INVENTORY_STALE_MARKERS_START")
    for marker in hits:
        print(marker)
    print("PHASE7_BUILD_INVENTORY_STALE_MARKERS_END")


def render_validation_commands(makefile_text: str) -> list[str]:
    match = PHASE7_VALIDATE_BLOCK_RE.search(makefile_text)
    if match is None:
        raise ValueError("missing phase7-validate block")

    commands: list[str] = []
    for line in match.group(1).splitlines():
        command_match = MAKEFILE_COMMAND_RE.search(line)
        if command_match is not None:
            commands.append(command_match.group(1))
    return commands


def render_shared_test_command(makefile_text: str) -> str:
    match = PHASE7_TEST_BLOCK_RE.search(makefile_text)
    if match is None:
        raise ValueError("missing phase7-test block")

    for line in match.group(1).splitlines():
        command_match = MAKEFILE_TEST_COMMAND_RE.search(line)
        if command_match is not None:
            return f"zig {command_match.group(1)}"

    raise ValueError("missing phase7-test compile command")


def render_validation_gates(validation_commands: list[str]) -> list[str]:
    gates: list[str] = []
    for command in validation_commands:
        script = command.removesuffix(" --self-test")
        if script not in gates:
            gates.append(script)
    return gates


def render_inventory_from_text(
    build_text: str, makefile_text: str
) -> dict[str, object]:
    imported_helpers = [
        {
            "root_path": root_path,
            "import_name": import_name,
            "helper_path": helper_path,
        }
        for root_path, import_name, helper_path in IMPORTED_HELPER_RE.findall(build_text)
    ]
    standalone_surveys = STANDALONE_SURVEY_RE.findall(build_text)
    run_labels: list[str] = []
    run_cwds: dict[str, str | None] = {}
    for run_label, cwd in RUN_CALL_RE.findall(build_text):
        run_labels.append(run_label)
        run_cwds[run_label] = None if cwd == "null" else cwd

    expected_build_paths = set(BUILD_PATH_RE.findall(build_text))
    expected_build_paths.update(entry["root_path"] for entry in imported_helpers)
    expected_build_paths.update(entry["helper_path"] for entry in imported_helpers)
    expected_build_paths.update(standalone_surveys)
    validation_commands = render_validation_commands(makefile_text)

    return {
        "repo_root_path": "../..",
        "imported_helpers": imported_helpers,
        "standalone_surveys": standalone_surveys,
        "expected_build_paths": sorted(expected_build_paths),
        "run_labels": run_labels,
        "run_cwds": run_cwds,
        "shared_test_depend_steps": DEPEND_STEP_RE.findall(build_text),
        "shared_validation_gates": render_validation_gates(validation_commands),
        "shared_validation_commands": validation_commands,
        "shared_test_command": render_shared_test_command(makefile_text),
        "unexpected_build_markers": UNEXPECTED_BUILD_MARKERS,
    }


def render_inventory(
    build_path: Path = BUILD_PATH, makefile_path: Path = MAKEFILE_PATH
) -> dict[str, object]:
    return render_inventory_from_text(
        build_path.read_text(encoding="utf-8"),
        makefile_path.read_text(encoding="utf-8"),
    )


def print_mismatch(expected: dict[str, object], actual: dict[str, object]) -> None:
    print("PHASE7_BUILD_INVENTORY=fail")
    print("PHASE7_BUILD_INVENTORY_MISMATCH_START")
    print("EXPECTED_JSON_START")
    print(json.dumps(expected, indent=2))
    print("EXPECTED_JSON_END")
    print("ACTUAL_JSON_START")
    print(json.dumps(actual, indent=2))
    print("ACTUAL_JSON_END")
    print("PHASE7_BUILD_INVENTORY_MISMATCH_END")


def run_self_test() -> int:
    fixture = load_fixture()
    first = render_inventory()
    second = render_inventory()

    if first != second:
        raise SystemExit("phase7-build-inventory:self-test:repeat_run_stability")
    if first != fixture:
        raise SystemExit("phase7-build-inventory:self-test:fixture_match")
    if len(first["run_labels"]) != len(first["shared_test_depend_steps"]):
        raise SystemExit("phase7-build-inventory:self-test:depend_step_count")
    for run_label in EXPECTED_REPO_ROOT_RUN_CWDS:
        if first["run_cwds"].get(run_label) != "repo_root":
            raise SystemExit(
                f"phase7-build-inventory:self-test:repo_root_cwd_baseline:{run_label}"
            )
    if len(first["shared_validation_gates"]) != 7:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_count")
    if len(first["shared_validation_commands"]) != 14:
        raise SystemExit("phase7-build-inventory:self-test:validation_command_count")
    if first["shared_validation_commands"][2:4] != [
        "scripts/zigux/check-phase7-build-inventory.py --self-test",
        "scripts/zigux/check-phase7-build-inventory.py",
    ]:
        raise SystemExit("phase7-build-inventory:self-test:build_inventory_command_pair")
    if first["shared_validation_commands"][8:10] != [
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
    ]:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_packet_command_pair")
    if first["shared_validation_commands"][10:12] != [
        "scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "scripts/zigux/check-phase7-argv-split-parity.py",
    ]:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_command_pair")
    if first["shared_test_command"] != EXPECTED_SHARED_TEST_COMMAND:
        raise SystemExit("phase7-build-inventory:self-test:shared_test_command")

    drifted = dict(first)
    drifted["run_labels"] = ["phase7-mismatch"]
    if drifted == fixture:
        raise SystemExit("phase7-build-inventory:self-test:drift_detection")

    if first["expected_build_paths"] != sorted(first["expected_build_paths"]):
        raise SystemExit("phase7-build-inventory:self-test:path_sorting")

    build_text = BUILD_PATH.read_text(encoding="utf-8")
    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")

    if collect_unexpected_build_hits(build_text):
        raise SystemExit("phase7-build-inventory:self-test:unexpected_marker_baseline")

    with tempfile.TemporaryDirectory(prefix="phase7_build_inventory_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        existing = tmp_root / "present.txt"
        existing.write_text("ok\n", encoding="utf-8")
        missing = tmp_root / "missing.txt"
        missing_paths = collect_missing_paths([existing, missing], tmp_root)
        if missing_paths != ["missing.txt"]:
            raise SystemExit("phase7-build-inventory:self-test:missing_path_preflight")

    try:
        render_validation_commands("phase7-test:\n\t@true\n")
    except ValueError as exc:
        if str(exc) != "missing phase7-validate block":
            raise SystemExit("phase7-build-inventory:self-test:validate_block_error_shape")
    else:
        raise SystemExit("phase7-build-inventory:self-test:validate_block_error_missing")

    try:
        render_shared_test_command("phase7-validate:\n\t@true\n")
    except ValueError as exc:
        if str(exc) != "missing phase7-test block":
            raise SystemExit("phase7-build-inventory:self-test:test_block_error_shape")
    else:
        raise SystemExit("phase7-build-inventory:self-test:test_block_error_missing")

    try:
        render_shared_test_command("phase7-test:\n\t@true\n")
    except ValueError as exc:
        if str(exc) != "missing phase7-test compile command":
            raise SystemExit("phase7-build-inventory:self-test:test_command_error_shape")
    else:
        raise SystemExit("phase7-build-inventory:self-test:test_command_error_missing")

    stale_marker_drift_text = (
        build_text
        + "\n// stale phase7 drift markers: zigux/tests/build.zig ../../tools/lib/\n"
    )
    stale_marker_hits = collect_unexpected_build_hits(stale_marker_drift_text)
    if stale_marker_hits != UNEXPECTED_BUILD_MARKERS:
        raise SystemExit("phase7-build-inventory:self-test:stale_marker_detection")

    cwd_drift_text, replacements = re.subn(
        r'("phase7-argv-split-survey-tests",\s*argv_split_survey_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:cwd_drift_rewrite")

    cwd_drift = render_inventory_from_text(cwd_drift_text, makefile_text)
    if cwd_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:cwd_drift_detection")
    if first["run_cwds"].get("phase7-argv-split-survey-tests") != "repo_root":
        raise SystemExit("phase7-build-inventory:self-test:argv_split_repo_root_baseline")
    if cwd_drift["run_cwds"].get("phase7-argv-split-survey-tests") is not None:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_repo_root_drift")

    cmdline_cwd_drift_text, replacements = re.subn(
        r'("phase7-cmdline-survey-tests",\s*cmdline_survey_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:cmdline_cwd_drift_rewrite")

    cmdline_cwd_drift = render_inventory_from_text(cmdline_cwd_drift_text, makefile_text)
    if cmdline_cwd_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:cmdline_cwd_drift_detection")
    if first["run_cwds"].get("phase7-cmdline-survey-tests") != "repo_root":
        raise SystemExit("phase7-build-inventory:self-test:cmdline_repo_root_baseline")
    if cmdline_cwd_drift["run_cwds"].get("phase7-cmdline-survey-tests") is not None:
        raise SystemExit("phase7-build-inventory:self-test:cmdline_repo_root_drift")

    string_helpers_cwd_drift_text, replacements = re.subn(
        r'("phase7-string-helpers-survey-tests",\s*string_helpers_survey_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_cwd_drift_rewrite"
        )

    string_helpers_cwd_drift = render_inventory_from_text(
        string_helpers_cwd_drift_text,
        makefile_text,
    )
    if string_helpers_cwd_drift == fixture:
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_cwd_drift_detection"
        )
    if first["run_cwds"].get("phase7-string-helpers-survey-tests") != "repo_root":
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_repo_root_baseline"
        )
    if (
        string_helpers_cwd_drift["run_cwds"].get("phase7-string-helpers-survey-tests")
        is not None
    ):
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_repo_root_drift"
        )

    string_helpers_sample_boundary_cwd_drift_text, replacements = re.subn(
        r'("phase7-string-helpers-sample-boundary-tests",\s*string_helpers_sample_boundary_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_sample_boundary_cwd_drift_rewrite"
        )

    string_helpers_sample_boundary_cwd_drift = render_inventory_from_text(
        string_helpers_sample_boundary_cwd_drift_text,
        makefile_text,
    )
    if string_helpers_sample_boundary_cwd_drift == fixture:
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_sample_boundary_cwd_drift_detection"
        )
    if (
        first["run_cwds"].get("phase7-string-helpers-sample-boundary-tests")
        != "repo_root"
    ):
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_sample_boundary_repo_root_baseline"
        )
    if (
        string_helpers_sample_boundary_cwd_drift["run_cwds"].get(
            "phase7-string-helpers-sample-boundary-tests"
        )
        is not None
    ):
        raise SystemExit(
            "phase7-build-inventory:self-test:string_helpers_sample_boundary_repo_root_drift"
        )

    rbtree_cwd_drift_text, replacements = re.subn(
        r'("phase7-rbtree-survey-tests",\s*rbtree_survey_root_module,\s*)repo_root(\s*,\s*\))',
        r"\1null\2",
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:rbtree_cwd_drift_rewrite")

    rbtree_cwd_drift = render_inventory_from_text(
        rbtree_cwd_drift_text,
        makefile_text,
    )
    if rbtree_cwd_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:rbtree_cwd_drift_detection")
    if first["run_cwds"].get("phase7-rbtree-survey-tests") != "repo_root":
        raise SystemExit("phase7-build-inventory:self-test:rbtree_repo_root_baseline")
    if rbtree_cwd_drift["run_cwds"].get("phase7-rbtree-survey-tests") is not None:
        raise SystemExit("phase7-build-inventory:self-test:rbtree_repo_root_drift")

    string_helpers_helper_path_drift_text, replacements = re.subn(
        r'("phase7_string_helpers\.zig",\s*"string_helpers",\s*")\.\./\.\./lib/string_helpers\.zig("\s*,)',
        r'\1../../lib/cmdline.zig\2',
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:string_helpers_helper_path_drift_rewrite")

    string_helpers_helper_path_drift = render_inventory_from_text(
        string_helpers_helper_path_drift_text,
        makefile_text,
    )
    if string_helpers_helper_path_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:string_helpers_helper_path_drift_detection")
    if first["imported_helpers"][0]["helper_path"] != "../../lib/string_helpers.zig":
        raise SystemExit("phase7-build-inventory:self-test:string_helpers_helper_path_baseline")
    if (
        string_helpers_helper_path_drift["imported_helpers"][0]["helper_path"]
        != "../../lib/cmdline.zig"
    ):
        raise SystemExit("phase7-build-inventory:self-test:string_helpers_helper_path_drift")

    cmdline_helper_path_drift_text, replacements = re.subn(
        r'("phase7_cmdline\.zig",\s*"cmdline",\s*")\.\./\.\./lib/cmdline\.zig("\s*,)',
        r'\1../../lib/rbtree.zig\2',
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:cmdline_helper_path_drift_rewrite")

    cmdline_helper_path_drift = render_inventory_from_text(
        cmdline_helper_path_drift_text,
        makefile_text,
    )
    if cmdline_helper_path_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:cmdline_helper_path_drift_detection")
    if first["imported_helpers"][1]["helper_path"] != "../../lib/cmdline.zig":
        raise SystemExit("phase7-build-inventory:self-test:cmdline_helper_path_baseline")
    if cmdline_helper_path_drift["imported_helpers"][1]["helper_path"] != "../../lib/rbtree.zig":
        raise SystemExit("phase7-build-inventory:self-test:cmdline_helper_path_drift")

    helper_path_drift_text, replacements = re.subn(
        r'("phase7_argv_split\.zig",\s*"argv_split",\s*")\.\./\.\./lib/argv_split\.zig("\s*,)',
        r'\1../../lib/cmdline.zig\2',
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_rewrite")

    helper_path_drift = render_inventory_from_text(helper_path_drift_text, makefile_text)
    if helper_path_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_detection")
    if helper_path_drift["imported_helpers"][2]["helper_path"] != "../../lib/cmdline.zig":
        raise SystemExit("phase7-build-inventory:self-test:helper_path_drift_shape")

    rbtree_helper_path_drift_text, replacements = re.subn(
        r'("phase7_rbtree\.zig",\s*"rbtree",\s*")\.\./\.\./lib/rbtree\.zig("\s*,)',
        r'\1../../lib/string_helpers.zig\2',
        build_text,
        count=1,
        flags=re.S,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:rbtree_helper_path_drift_rewrite")

    rbtree_helper_path_drift = render_inventory_from_text(
        rbtree_helper_path_drift_text,
        makefile_text,
    )
    if rbtree_helper_path_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:rbtree_helper_path_drift_detection")
    if first["imported_helpers"][3]["helper_path"] != "../../lib/rbtree.zig":
        raise SystemExit("phase7-build-inventory:self-test:rbtree_helper_path_baseline")
    if rbtree_helper_path_drift["imported_helpers"][3]["helper_path"] != "../../lib/string_helpers.zig":
        raise SystemExit("phase7-build-inventory:self-test:rbtree_helper_path_drift")

    dependency_drift_text = build_text.replace(
        "    test_step.dependOn(&run_rbtree_tests.step);\n",
        "",
        1,
    )
    if dependency_drift_text == build_text:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_rewrite")

    dependency_drift = render_inventory_from_text(dependency_drift_text, makefile_text)
    if dependency_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_detection")
    dependency_steps = dependency_drift["shared_test_depend_steps"]
    if "run_rbtree_tests" in dependency_steps:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_shape")
    if len(dependency_steps) != len(first["shared_test_depend_steps"]) - 1:
        raise SystemExit("phase7-build-inventory:self-test:dependency_drift_count")

    survey_dependency_drift_text = build_text.replace(
        "    test_step.dependOn(&run_string_helpers_survey_tests.step);\n",
        "",
        1,
    )
    if survey_dependency_drift_text == build_text:
        raise SystemExit("phase7-build-inventory:self-test:survey_dependency_drift_rewrite")

    survey_dependency_drift = render_inventory_from_text(
        survey_dependency_drift_text,
        makefile_text,
    )
    if survey_dependency_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:survey_dependency_drift_detection")
    survey_dependency_steps = survey_dependency_drift["shared_test_depend_steps"]
    if "run_string_helpers_survey_tests" in survey_dependency_steps:
        raise SystemExit("phase7-build-inventory:self-test:survey_dependency_drift_shape")
    if len(survey_dependency_steps) != len(first["shared_test_depend_steps"]) - 1:
        raise SystemExit("phase7-build-inventory:self-test:survey_dependency_drift_count")

    validation_gate_drift_text, replacements = re.subn(
        r"scripts/zigux/check-phase7-build-inventory\.py",
        "scripts/zigux/check-phase7-build-inventory-drift.py",
        makefile_text,
        count=1,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_drift_rewrite")

    validation_gate_drift = render_inventory_from_text(
        build_text,
        validation_gate_drift_text,
    )
    if validation_gate_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_drift_detection")
    if (
        "scripts/zigux/check-phase7-build-inventory-drift.py"
        not in validation_gate_drift["shared_validation_gates"]
    ):
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_drift_shape")
    if (
        "scripts/zigux/check-phase7-build-inventory-drift.py --self-test"
        not in validation_gate_drift["shared_validation_commands"]
    ):
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_command_shape")

    validation_command_pair_drift_text = makefile_text.replace(
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py --self-test\n",
        "",
        1,
    )
    if validation_command_pair_drift_text == makefile_text:
        raise SystemExit("phase7-build-inventory:self-test:validation_command_pair_drift_rewrite")

    validation_command_pair_drift = render_inventory_from_text(
        build_text,
        validation_command_pair_drift_text,
    )
    if validation_command_pair_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:validation_command_pair_drift_detection")
    if (
        "scripts/zigux/check-phase7-build-inventory.py --self-test"
        in validation_command_pair_drift["shared_validation_commands"]
    ):
        raise SystemExit("phase7-build-inventory:self-test:validation_command_pair_drift_shape")
    if validation_command_pair_drift["shared_validation_gates"] != fixture["shared_validation_gates"]:
        raise SystemExit("phase7-build-inventory:self-test:validation_command_pair_gate_shape")

    argv_split_packet_command_pair_drift_text = makefile_text.replace(
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-packet.py --self-test\n",
        "",
        1,
    )
    if argv_split_packet_command_pair_drift_text == makefile_text:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_packet_command_pair_drift_rewrite")

    argv_split_packet_command_pair_drift = render_inventory_from_text(
        build_text,
        argv_split_packet_command_pair_drift_text,
    )
    if argv_split_packet_command_pair_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_packet_command_pair_drift_detection")
    if (
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test"
        in argv_split_packet_command_pair_drift["shared_validation_commands"]
    ):
        raise SystemExit("phase7-build-inventory:self-test:argv_split_packet_command_pair_drift_shape")
    if argv_split_packet_command_pair_drift["shared_validation_gates"] != fixture["shared_validation_gates"]:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_packet_command_pair_gate_shape")

    argv_split_command_pair_drift_text = makefile_text.replace(
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n",
        "",
        1,
    )
    if argv_split_command_pair_drift_text == makefile_text:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_command_pair_drift_rewrite")

    argv_split_command_pair_drift = render_inventory_from_text(
        build_text,
        argv_split_command_pair_drift_text,
    )
    if argv_split_command_pair_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_command_pair_drift_detection")
    if (
        "scripts/zigux/check-phase7-argv-split-parity.py --self-test"
        in argv_split_command_pair_drift["shared_validation_commands"]
    ):
        raise SystemExit("phase7-build-inventory:self-test:argv_split_command_pair_drift_shape")
    if argv_split_command_pair_drift["shared_validation_gates"] != fixture["shared_validation_gates"]:
        raise SystemExit("phase7-build-inventory:self-test:argv_split_command_pair_gate_shape")

    validation_gate_order_drift_text, replacements = re.subn(
        r'(\tcd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase7-build-inventory\.py --self-test\n)'
        r'(\tcd \$\(ZIGUX_ROOT\) && \$\(PYTHON\) scripts/zigux/check-phase7-build-inventory\.py\n)',
        r'\2\1',
        makefile_text,
        count=1,
    )
    if replacements != 1:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_order_drift_rewrite")

    validation_gate_order_drift = render_inventory_from_text(
        build_text,
        validation_gate_order_drift_text,
    )
    if validation_gate_order_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_order_drift_detection")
    if validation_gate_order_drift["shared_validation_gates"] != fixture["shared_validation_gates"]:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_order_gate_shape")
    if validation_gate_order_drift["shared_validation_commands"] == fixture["shared_validation_commands"]:
        raise SystemExit("phase7-build-inventory:self-test:validation_gate_order_command_shape")

    shared_test_command_drift_text = makefile_text.replace(
        "$(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all",
        "$(ZIG) build test --build-file zigux/tests/build.zig",
        1,
    )
    if shared_test_command_drift_text == makefile_text:
        raise SystemExit("phase7-build-inventory:self-test:shared_test_command_drift_rewrite")

    shared_test_command_drift = render_inventory_from_text(
        build_text,
        shared_test_command_drift_text,
    )
    if shared_test_command_drift == fixture:
        raise SystemExit("phase7-build-inventory:self-test:shared_test_command_drift_detection")
    if shared_test_command_drift["shared_test_command"] != "zig build test --build-file zigux/tests/build.zig":
        raise SystemExit("phase7-build-inventory:self-test:shared_test_command_drift_shape")

    print("PHASE7_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE7_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=26")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild and compare the Phase 7 shared build inventory fixture."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in repeat-run stability and fixture drift checks.",
    )
    args = parser.parse_args(argv)

    missing = collect_missing_paths(REQUIRED_PATHS)
    if missing:
        print_missing_paths(missing)
        return 1

    build_text = BUILD_PATH.read_text(encoding="utf-8")
    unexpected_hits = collect_unexpected_build_hits(build_text)
    if unexpected_hits:
        print_unexpected_build_hits(unexpected_hits)
        return 1

    if args.self_test:
        return run_self_test()

    fixture = load_fixture()
    try:
        generated = render_inventory()
    except ValueError as exc:
        print("PHASE7_BUILD_INVENTORY=fail")
        print("PHASE7_BUILD_INVENTORY_ERROR_START")
        print(str(exc))
        print("PHASE7_BUILD_INVENTORY_ERROR_END")
        return 1
    if generated != fixture:
        print_mismatch(fixture, generated)
        return 1

    build_inventory_errors: list[str] = []
    if generated.get("repo_root_path") != "../..":
        build_inventory_errors.append("repo_root_path")
    if generated.get("shared_validation_gates") != [
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-build-inventory.py",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-cmdline-parity.py",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-argv-split-parity.py",
        "scripts/zigux/check-phase7-rbtree-parity.py",
    ]:
        build_inventory_errors.append("shared_validation_gates")
    if generated.get("shared_validation_commands") != [
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
        "scripts/zigux/check-phase7-build-inventory.py --self-test",
        "scripts/zigux/check-phase7-build-inventory.py",
        "scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "scripts/zigux/check-phase7-make-wrapper.py",
        "scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "scripts/zigux/check-phase7-cmdline-parity.py",
        "scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "scripts/zigux/check-phase7-argv-split-packet.py",
        "scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "scripts/zigux/check-phase7-argv-split-parity.py",
        "scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "scripts/zigux/check-phase7-rbtree-parity.py",
    ]:
        build_inventory_errors.append("shared_validation_commands")
    if generated.get("unexpected_build_markers") != UNEXPECTED_BUILD_MARKERS:
        build_inventory_errors.append("unexpected_build_markers")
    if len(generated.get("run_labels", [])) != 9:
        build_inventory_errors.append("run_labels")
    if len(generated.get("shared_test_depend_steps", [])) != 9:
        build_inventory_errors.append("shared_test_depend_steps")
    for run_label in EXPECTED_REPO_ROOT_RUN_CWDS:
        if generated.get("run_cwds", {}).get(run_label) != "repo_root":
            build_inventory_errors.append(f"run_cwds:{run_label}")
    if build_inventory_errors:
        print("PHASE7_BUILD_INVENTORY=fail")
        print("PHASE7_BUILD_INVENTORY_SHAPE_START")
        for item in build_inventory_errors:
            print(f"zigux/tests/fixtures/phase7_build_inventory.json: {item}")
        print("PHASE7_BUILD_INVENTORY_SHAPE_END")
        return 1

    print("PHASE7_BUILD_INVENTORY=pass")
    print(f"PHASE7_BUILD_INVENTORY_RUN_COUNT={len(generated['run_labels'])}")
    print(f"PHASE7_BUILD_INVENTORY_DEPENDENCY_COUNT={len(generated['shared_test_depend_steps'])}")
    print(
        "PHASE7_BUILD_INVENTORY_VALIDATION_GATE_COUNT="
        f"{len(generated['shared_validation_gates'])}"
    )
    print(
        "PHASE7_BUILD_INVENTORY_VALIDATION_COMMAND_COUNT="
        f"{len(generated['shared_validation_commands'])}"
    )
    print(
        "PHASE7_BUILD_INVENTORY_SHARED_TEST_COMMAND="
        f"{generated['shared_test_command']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
