#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux/tests/phase11_build.zig"
FIXTURE_PATH = ROOT / "zigux/tests/fixtures/phase11_build_inventory.json"

BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase11-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase11-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)
BUILD_STEP_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.step\(\s*"([^"]+)",\s*"([^"]+)",?\s*\);',
    re.S,
)

FORBIDDEN_BUILD_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
DEDICATED_SURVEY_REPLAY_TESTS = {
    "phase11-hvc-console-survey-tests": "zigux/tests/phase11_hvc_console_survey.zig",
}
SHARED_ADJUNCT_REPLAY_TESTS = {
    "phase11-dw-wdt-suspend-resume-tests": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
}
SHARED_REPLAY_MARKERS = [
    {
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        "marker": "    try std.testing.expect(summary.resume_preserves_timeout_programming);",
    },
    {
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "marker": "    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "marker": "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "marker": "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
    },
]
HVC_SYSRQ_MARKERS = [
    "pub fn summarizeSysrqHandoff(",
    "if (!slot.usable_for_console) return error.ConsoleUnavailable;",
    "const is_toggle = request.is_kernel_console and request.input_char == 0x0f;",
    ".consumes_input_without_flip = !emits_literal_char,",
    ".keeps_live_sysrq_execution_out_of_scope = true,",
]
REQUIRED_BUILD_STEPS = [
    ("test_step", "test", "Run Phase 11 starter and survey tests"),
    (
        "hvc_console_survey_step",
        "hvc-console-survey",
        "Run the dedicated Phase 11 hvc_console survey replay",
    ),
]
REQUIRED_BUILD_STEP_BINDINGS = [
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
SPLIT_TEST_SUFFIX = "-split-tests"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_inventory() -> dict[str, object]:
    build_text = BUILD_PATH.read_text(encoding="utf-8")
    module_root_source_files = [
        {"module": module_name, "path": root_path}
        for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
    ]
    test_root_modules = [
        {"test": test_name, "root_module": root_module}
        for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
    ]
    root_path_by_module = {
        item["module"]: item["path"]
        for item in module_root_source_files
    }
    dedicated_survey_replays = []
    shared_split_replays = []
    shared_adjunct_replays = []
    for item in test_root_modules:
        test_name = item["test"]
        root_path = root_path_by_module.get(item["root_module"])
        if root_path is None:
            continue
        test_path = (Path("zigux/tests") / root_path).as_posix()
        expected_dedicated_path = DEDICATED_SURVEY_REPLAY_TESTS.get(test_name)
        if expected_dedicated_path is not None and test_path == expected_dedicated_path:
            dedicated_survey_replays.append(
                {
                    "test": test_name,
                    "path": test_path,
                }
            )
            continue
        if test_name.endswith(SPLIT_TEST_SUFFIX):
            shared_split_replays.append(
                {
                    "test": test_name,
                    "path": test_path,
                }
            )
            continue
        expected_adjunct_path = SHARED_ADJUNCT_REPLAY_TESTS.get(test_name)
        if expected_adjunct_path is not None and test_path == expected_adjunct_path:
            shared_adjunct_replays.append(
                {
                    "test": test_name,
                    "path": test_path,
                }
            )
    return {
        "build_test_names": BUILD_TEST_NAME_RE.findall(build_text),
        "shared_test_depend_steps": BUILD_DEPEND_STEP_RE.findall(build_text),
        "module_root_source_files": module_root_source_files,
        "module_imports": [
            {
                "module": module_name,
                "import_name": import_name,
                "imported_module": imported_module,
            }
            for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
        ],
        "test_root_modules": test_root_modules,
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": dedicated_survey_replays,
        "shared_split_replays": shared_split_replays,
        "shared_adjunct_replays": shared_adjunct_replays,
        "shared_replay_markers": SHARED_REPLAY_MARKERS,
    }


def validate_module_roots(inventory: dict[str, object]) -> list[str]:
    module_roots = inventory.get("module_root_source_files")
    if not isinstance(module_roots, list):
        return ["phase11_build_inventory:module_root_source_files"]
    build_dir = BUILD_PATH.parent
    missing = []
    for item in module_roots:
        if not isinstance(item, dict):
            missing.append("phase11_build_inventory:module_root_source_files:item")
            continue
        module_name = item.get("module")
        root_path = item.get("path")
        if not isinstance(module_name, str) or not isinstance(root_path, str):
            missing.append("phase11_build_inventory:module_root_source_files:shape")
            continue
        if not (build_dir / root_path).exists():
            missing.append(f"{module_name}:{root_path}")
    return missing


def validate_shared_replay_markers() -> list[str]:
    missing = []
    for item in SHARED_REPLAY_MARKERS:
        replay_path = ROOT / item["path"]
        if not replay_path.exists():
            missing.append(f'{item["path"]}:missing')
            continue
        replay_text = replay_path.read_text(encoding="utf-8")
        if item["marker"] not in replay_text:
            missing.append(f'{item["path"]}:{item["marker"]}')
    return missing


def validate_hvc_sysrq_surface() -> list[str]:
    missing = []
    sysrq_path = ROOT / "drivers/tty/hvc/hvc_console_sysrq.zig"
    if not sysrq_path.exists():
        return ["drivers/tty/hvc/hvc_console_sysrq.zig:missing"]
    sysrq_text = sysrq_path.read_text(encoding="utf-8")
    for marker in HVC_SYSRQ_MARKERS:
        if marker not in sysrq_text:
            missing.append(f"drivers/tty/hvc/hvc_console_sysrq.zig:{marker}")
    return missing


def validate_build_steps(build_text: str) -> list[str]:
    missing = []
    build_steps = {
        symbol: {"name": name, "description": description}
        for symbol, name, description in BUILD_STEP_RE.findall(build_text)
    }
    for symbol, name, description in REQUIRED_BUILD_STEPS:
        if build_steps.get(symbol) != {"name": name, "description": description}:
            missing.append(f"{symbol}:name={name},description={description}")
    for marker in REQUIRED_BUILD_STEP_BINDINGS:
        if marker not in build_text:
            missing.append(f"binding:{marker}")
    return missing


def validate_fixture_match() -> int:
    fixture = load_json(FIXTURE_PATH)
    generated = render_inventory()

    missing_module_roots = validate_module_roots(generated)
    if missing_module_roots:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_START")
        for item in missing_module_roots:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_END")
        return 1

    missing_replay_markers = validate_shared_replay_markers()
    if missing_replay_markers:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_REPLAY_MARKERS_START")
        for item in missing_replay_markers:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_REPLAY_MARKERS_END")
        return 1

    missing_hvc_sysrq_markers = validate_hvc_sysrq_surface()
    if missing_hvc_sysrq_markers:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_HVC_SYSRQ_MARKERS_START")
        for item in missing_hvc_sysrq_markers:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_HVC_SYSRQ_MARKERS_END")
        return 1

    build_text = BUILD_PATH.read_text(encoding="utf-8")
    forbidden = [marker for marker in FORBIDDEN_BUILD_MARKERS if marker in build_text]
    if forbidden:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_FORBIDDEN_MARKERS_START")
        for item in forbidden:
            print(item)
        print("PHASE11_BUILD_INVENTORY_FORBIDDEN_MARKERS_END")
        return 1

    missing_steps = validate_build_steps(build_text)
    if missing_steps:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_BUILD_STEPS_START")
        for item in missing_steps:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_BUILD_STEPS_END")
        return 1

    if fixture != generated:
        print("ARTIFACT_DIFF=fail")
        print("PHASE11_BUILD_INVENTORY=fail")
        return 1

    print("ARTIFACT_DIFF=pass")
    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-build-inventory.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_stdout(label: str, result: subprocess.CompletedProcess[str], expected: str) -> None:
    if result.returncode == 0:
        raise SystemExit(f"phase11-build-inventory-self-test:{label}:unexpected_pass")
    if expected not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:expected:{expected}:actual:{actual}"
        )


def write_self_test_fixture(root: Path) -> None:
    build_text = """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const dw_wdt_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/watchdog/dw_wdt.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_dw_wdt_suspend_resume_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_dw_wdt_suspend_resume.zig\"),
        .target = target,
        .optimize = optimize,
    });
    phase11_dw_wdt_suspend_resume_module.addImport(\"dw_wdt\", dw_wdt_module);
    const phase11_dw_wdt_remove_idle_split_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_dw_wdt_remove_idle_split.zig\"),
        .target = target,
        .optimize = optimize,
    });
    phase11_dw_wdt_remove_idle_split_module.addImport(\"dw_wdt\", dw_wdt_module);

    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/tty/hvc/hvc_console.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const hvc_console_sysrq_module = b.createModule(.{
        .root_source_file = b.path(\"../../drivers/tty/hvc/hvc_console_sysrq.zig\"),
        .target = target,
        .optimize = optimize,
    });
    const phase11_hvc_console_modem_control_split_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_console_modem_control_split.zig\"),
        .target = target,
        .optimize = optimize,
    });
    phase11_hvc_console_modem_control_split_module.addImport(\"hvc_console\", hvc_console_module);
    const phase11_hvc_console_poll_retry_split_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_console_poll_retry_split.zig\"),
        .target = target,
        .optimize = optimize,
    });
    phase11_hvc_console_poll_retry_split_module.addImport(\"hvc_console\", hvc_console_module);
    phase11_hvc_console_poll_retry_split_module.addImport(\"hvc_console_sysrq\", hvc_console_sysrq_module);
    const phase11_hvc_console_survey_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_console_survey.zig\"),
        .target = target,
        .optimize = optimize,
    });

    const phase11_dw_wdt_suspend_resume_tests = b.addTest(.{
        .name = \"phase11-dw-wdt-suspend-resume-tests\",
        .root_module = phase11_dw_wdt_suspend_resume_module,
    });
    const run_phase11_dw_wdt_suspend_resume_tests = b.addRunArtifact(
        phase11_dw_wdt_suspend_resume_tests,
    );
    const phase11_dw_wdt_remove_idle_split_tests = b.addTest(.{
        .name = \"phase11-dw-wdt-remove-idle-split-tests\",
        .root_module = phase11_dw_wdt_remove_idle_split_module,
    });
    const run_phase11_dw_wdt_remove_idle_split_tests = b.addRunArtifact(
        phase11_dw_wdt_remove_idle_split_tests,
    );
    const phase11_hvc_console_modem_control_split_tests = b.addTest(.{
        .name = \"phase11-hvc-console-modem-control-split-tests\",
        .root_module = phase11_hvc_console_modem_control_split_module,
    });
    const run_phase11_hvc_console_modem_control_split_tests = b.addRunArtifact(
        phase11_hvc_console_modem_control_split_tests,
    );
    const phase11_hvc_console_poll_retry_split_tests = b.addTest(.{
        .name = \"phase11-hvc-console-poll-retry-split-tests\",
        .root_module = phase11_hvc_console_poll_retry_split_module,
    });
    const run_phase11_hvc_console_poll_retry_split_tests = b.addRunArtifact(
        phase11_hvc_console_poll_retry_split_tests,
    );
    const phase11_hvc_console_survey_tests = b.addTest(.{
        .name = \"phase11-hvc-console-survey-tests\",
        .root_module = phase11_hvc_console_survey_module,
    });
    const run_phase11_hvc_console_survey_tests = b.addRunArtifact(
        phase11_hvc_console_survey_tests,
    );

    const test_step = b.step(\"test\", \"Run Phase 11 starter and survey tests\");
    test_step.dependOn(&run_phase11_dw_wdt_suspend_resume_tests.step);
    test_step.dependOn(&run_phase11_dw_wdt_remove_idle_split_tests.step);
    test_step.dependOn(&run_phase11_hvc_console_modem_control_split_tests.step);
    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);

    const hvc_console_survey_step = b.step(
        \"hvc-console-survey\",
        \"Run the dedicated Phase 11 hvc_console survey replay\",
    );
    hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);
}
"""
    write_text(root / "zigux/tests/phase11_build.zig", build_text)

    fixture = {
        "build_test_names": [
            "phase11-dw-wdt-suspend-resume-tests",
            "phase11-dw-wdt-remove-idle-split-tests",
            "phase11-hvc-console-modem-control-split-tests",
            "phase11-hvc-console-poll-retry-split-tests",
            "phase11-hvc-console-survey-tests",
        ],
        "shared_test_depend_steps": [
            "run_phase11_dw_wdt_suspend_resume_tests",
            "run_phase11_dw_wdt_remove_idle_split_tests",
            "run_phase11_hvc_console_modem_control_split_tests",
            "run_phase11_hvc_console_poll_retry_split_tests",
        ],
        "module_root_source_files": [
            {"module": "dw_wdt_module", "path": "../../drivers/watchdog/dw_wdt.zig"},
            {"module": "phase11_dw_wdt_suspend_resume_module", "path": "phase11_dw_wdt_suspend_resume.zig"},
            {"module": "phase11_dw_wdt_remove_idle_split_module", "path": "phase11_dw_wdt_remove_idle_split.zig"},
            {"module": "hvc_console_module", "path": "../../drivers/tty/hvc/hvc_console.zig"},
            {"module": "hvc_console_sysrq_module", "path": "../../drivers/tty/hvc/hvc_console_sysrq.zig"},
            {"module": "phase11_hvc_console_modem_control_split_module", "path": "phase11_hvc_console_modem_control_split.zig"},
            {"module": "phase11_hvc_console_poll_retry_split_module", "path": "phase11_hvc_console_poll_retry_split.zig"},
            {"module": "phase11_hvc_console_survey_module", "path": "phase11_hvc_console_survey.zig"},
        ],
        "module_imports": [
            {"module": "phase11_dw_wdt_suspend_resume_module", "import_name": "dw_wdt", "imported_module": "dw_wdt_module"},
            {"module": "phase11_dw_wdt_remove_idle_split_module", "import_name": "dw_wdt", "imported_module": "dw_wdt_module"},
            {"module": "phase11_hvc_console_modem_control_split_module", "import_name": "hvc_console", "imported_module": "hvc_console_module"},
            {"module": "phase11_hvc_console_poll_retry_split_module", "import_name": "hvc_console", "imported_module": "hvc_console_module"},
            {"module": "phase11_hvc_console_poll_retry_split_module", "import_name": "hvc_console_sysrq", "imported_module": "hvc_console_sysrq_module"},
        ],
        "test_root_modules": [
            {"test": "phase11-dw-wdt-suspend-resume-tests", "root_module": "phase11_dw_wdt_suspend_resume_module"},
            {"test": "phase11-dw-wdt-remove-idle-split-tests", "root_module": "phase11_dw_wdt_remove_idle_split_module"},
            {"test": "phase11-hvc-console-modem-control-split-tests", "root_module": "phase11_hvc_console_modem_control_split_module"},
            {"test": "phase11-hvc-console-poll-retry-split-tests", "root_module": "phase11_hvc_console_poll_retry_split_module"},
            {"test": "phase11-hvc-console-survey-tests", "root_module": "phase11_hvc_console_survey_module"},
        ],
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": [
            {"test": "phase11-hvc-console-survey-tests", "path": "zigux/tests/phase11_hvc_console_survey.zig"},
        ],
        "shared_split_replays": [
            {"test": "phase11-dw-wdt-remove-idle-split-tests", "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig"},
            {"test": "phase11-hvc-console-modem-control-split-tests", "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig"},
            {"test": "phase11-hvc-console-poll-retry-split-tests", "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig"},
        ],
        "shared_adjunct_replays": [
            {"test": "phase11-dw-wdt-suspend-resume-tests", "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig"},
        ],
        "shared_replay_markers": SHARED_REPLAY_MARKERS,
    }
    write_text(root / "zigux/tests/fixtures/phase11_build_inventory.json", json.dumps(fixture, indent=2) + "\n")

    for rel_path, content in {
        "drivers/watchdog/dw_wdt.zig": "// self-test placeholder\n",
        "drivers/tty/hvc/hvc_console.zig": "// self-test placeholder\n",
        "drivers/tty/hvc/hvc_console_sysrq.zig": "\n".join(HVC_SYSRQ_MARKERS) + "\n",
        "zigux/tests/phase11_dw_wdt_suspend_resume.zig": "    try std.testing.expect(summary.resume_preserves_timeout_programming);\n",
        "zigux/tests/phase11_dw_wdt_remove_idle_split.zig": "    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);\n",
        "zigux/tests/phase11_hvc_console_modem_control_split.zig": "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);\n",
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig": "    try std.testing.expect(dispatch.invokes_sysrq_handler);\n",
        "zigux/tests/phase11_hvc_console_survey.zig": "// self-test placeholder\n",
    }.items():
        write_text(root / rel_path, content)

    write_text(root / "scripts/zigux/check-phase11-build-inventory.py", Path(__file__).read_text(encoding="utf-8"))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_build_inventory_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_self_test_fixture(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-build-inventory-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        dw_split = tmp_root / "zigux/tests/phase11_dw_wdt_remove_idle_split.zig"
        dw_split_backup = dw_split.read_text(encoding="utf-8")
        dw_split.unlink()
        expect_stdout(
            "missing_dw_split",
            run_checker(tmp_root),
            "phase11_dw_wdt_remove_idle_split_module:phase11_dw_wdt_remove_idle_split.zig",
        )
        write_text(dw_split, dw_split_backup)

        dw_suspend = tmp_root / "zigux/tests/phase11_dw_wdt_suspend_resume.zig"
        dw_suspend_backup = dw_suspend.read_text(encoding="utf-8")
        dw_suspend.write_text("// marker removed\n", encoding="utf-8")
        expect_stdout(
            "missing_dw_suspend_marker",
            run_checker(tmp_root),
            "zigux/tests/phase11_dw_wdt_suspend_resume.zig:    try std.testing.expect(summary.resume_preserves_timeout_programming);",
        )
        write_text(dw_suspend, dw_suspend_backup)

        hvc_modem = tmp_root / "zigux/tests/phase11_hvc_console_modem_control_split.zig"
        hvc_modem_backup = hvc_modem.read_text(encoding="utf-8")
        hvc_modem.write_text("// marker removed\n", encoding="utf-8")
        expect_stdout(
            "missing_hvc_modem_marker",
            run_checker(tmp_root),
            "zigux/tests/phase11_hvc_console_modem_control_split.zig:    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
        )
        write_text(hvc_modem, hvc_modem_backup)

        hvc_poll_retry = tmp_root / "zigux/tests/phase11_hvc_console_poll_retry_split.zig"
        hvc_poll_retry_backup = hvc_poll_retry.read_text(encoding="utf-8")
        hvc_poll_retry.write_text("// marker removed\n", encoding="utf-8")
        expect_stdout(
            "missing_hvc_poll_retry_marker",
            run_checker(tmp_root),
            "zigux/tests/phase11_hvc_console_poll_retry_split.zig:    try std.testing.expect(dispatch.invokes_sysrq_handler);",
        )
        write_text(hvc_poll_retry, hvc_poll_retry_backup)

        hvc_sysrq = tmp_root / "drivers/tty/hvc/hvc_console_sysrq.zig"
        hvc_sysrq_backup = hvc_sysrq.read_text(encoding="utf-8")
        hvc_sysrq.unlink()
        expect_stdout(
            "missing_hvc_sysrq_module_root",
            run_checker(tmp_root),
            "hvc_console_sysrq_module:../../drivers/tty/hvc/hvc_console_sysrq.zig",
        )
        write_text(hvc_sysrq, hvc_sysrq_backup)

        hvc_sysrq.write_text("// marker removed\n", encoding="utf-8")
        expect_stdout(
            "missing_hvc_sysrq_surface_marker",
            run_checker(tmp_root),
            "drivers/tty/hvc/hvc_console_sysrq.zig:pub fn summarizeSysrqHandoff(",
        )
        write_text(hvc_sysrq, hvc_sysrq_backup)

        build_path = tmp_root / "zigux/tests/phase11_build.zig"
        build_backup = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build_backup.replace(
                "    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);\n",
                "    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);\n"
                "    test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_stdout(
            "forbidden_hvc_survey_dependency",
            run_checker(tmp_root),
            "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
        )
        write_text(build_path, build_backup)

        build_path.write_text(
            build_backup.replace(
                '    const test_step = b.step("test", "Run Phase 11 starter and survey tests");\n',
                '    const test_step = b.step("phase11", "Run Phase 11 starter and survey tests");\n',
                1,
            ),
            encoding="utf-8",
        )
        expect_stdout(
            "shared_test_step_name_drift",
            run_checker(tmp_root),
            "test_step:name=test,description=Run Phase 11 starter and survey tests",
        )
        write_text(build_path, build_backup)

        build_path.write_text(
            build_backup.replace(
                "    hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_stdout(
            "missing_hvc_survey_binding",
            run_checker(tmp_root),
            "binding:hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
        )
        write_text(build_path, build_backup)

        fixture_path = tmp_root / "zigux/tests/fixtures/phase11_build_inventory.json"
        fixture_backup = fixture_path.read_text(encoding="utf-8")
        fixture = json.loads(fixture_backup)
        fixture["shared_split_replays"] = fixture["shared_split_replays"][:-1]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_stdout(
            "shared_split_replay_fixture_drift",
            run_checker(tmp_root),
            "ARTIFACT_DIFF=fail",
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

        fixture = json.loads(fixture_backup)
        fixture["dedicated_survey_replays"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_stdout(
            "dedicated_survey_replay_fixture_drift",
            run_checker(tmp_root),
            "ARTIFACT_DIFF=fail",
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

        fixture = json.loads(fixture_backup)
        fixture["shared_adjunct_replays"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_stdout(
            "shared_adjunct_replay_fixture_drift",
            run_checker(tmp_root),
            "ARTIFACT_DIFF=fail",
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

        fixture = json.loads(fixture_backup)
        fixture["shared_replay_markers"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_stdout(
            "shared_replay_marker_fixture_drift",
            run_checker(tmp_root),
            "ARTIFACT_DIFF=fail",
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

    print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=13")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(validate_fixture_match())
