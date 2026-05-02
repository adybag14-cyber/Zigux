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
ARTIFACT_DIFF_PATH = ROOT / "scripts/zigux/artifact_diff.py"

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
DEDICATED_SURVEY_REPLAYS = [
    "zigux/tests/phase11_hvc_console_survey.zig",
]
REQUIRED_BUILD_STEPS = [
    {
        "symbol": "test_step",
        "name": "test",
        "description": "Run Phase 11 starter and survey tests",
    },
    {
        "symbol": "hvc_console_survey_step",
        "name": "hvc-console-survey",
        "description": "Run the dedicated Phase 11 hvc_console survey replay",
    },
]
REQUIRED_BUILD_STEP_BINDINGS = [
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
SPLIT_TEST_SUFFIX = "-split-tests"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_shared_split_replays(
    module_roots: list[dict[str, str]],
    test_root_modules: list[dict[str, str]],
) -> list[dict[str, str]]:
    root_path_by_module = {
        item["module"]: item["path"]
        for item in module_roots
    }
    shared_split_replays: list[dict[str, str]] = []
    for item in test_root_modules:
        test_name = item["test"]
        if not test_name.endswith(SPLIT_TEST_SUFFIX):
            continue
        root_path = root_path_by_module.get(item["root_module"])
        if root_path is None:
            continue
        shared_split_replays.append(
            {
                "test": test_name,
                "path": (Path("zigux/tests") / root_path).as_posix(),
            }
        )
    return shared_split_replays


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
        "dedicated_survey_replays": DEDICATED_SURVEY_REPLAYS,
        "shared_split_replays": render_shared_split_replays(module_root_source_files, test_root_modules),
    }


def validate_module_root_paths_exist(inventory: dict[str, object]) -> list[str]:
    missing: list[str] = []
    module_roots = inventory.get("module_root_source_files")
    if not isinstance(module_roots, list):
        return ["phase11_build_inventory:module_root_source_files"]

    build_dir = BUILD_PATH.parent
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


def validate_named_build_steps(build_text: str) -> list[str]:
    missing: list[str] = []
    build_steps = {
        symbol: {"name": name, "description": description}
        for symbol, name, description in BUILD_STEP_RE.findall(build_text)
    }
    for expected in REQUIRED_BUILD_STEPS:
        actual = build_steps.get(expected["symbol"])
        if actual != {
            "name": expected["name"],
            "description": expected["description"],
        }:
            missing.append(
                f'{expected["symbol"]}:name={expected["name"]},'
                f'description={expected["description"]}'
            )
    for marker in REQUIRED_BUILD_STEP_BINDINGS:
        if marker not in build_text:
            missing.append(f"binding:{marker}")
    return missing


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    const phase11_hvc_console_poll_retry_split_module = b.createModule(.{
        .root_source_file = b.path(\"phase11_hvc_console_poll_retry_split.zig\"),
        .target = target,
        .optimize = optimize,
    });
    phase11_hvc_console_poll_retry_split_module.addImport(\"hvc_console\", hvc_console_module);

    const phase11_dw_wdt_remove_idle_split_tests = b.addTest(.{
        .name = \"phase11-dw-wdt-remove-idle-split-tests\",
        .root_module = phase11_dw_wdt_remove_idle_split_module,
    });
    const run_phase11_dw_wdt_remove_idle_split_tests = b.addRunArtifact(
        phase11_dw_wdt_remove_idle_split_tests,
    );
    const phase11_hvc_console_poll_retry_split_tests = b.addTest(.{
        .name = \"phase11-hvc-console-poll-retry-split-tests\",
        .root_module = phase11_hvc_console_poll_retry_split_module,
    });
    const run_phase11_hvc_console_poll_retry_split_tests = b.addRunArtifact(
        phase11_hvc_console_poll_retry_split_tests,
    );

    const test_step = b.step(\"test\", \"Run Phase 11 starter and survey tests\");
    test_step.dependOn(&run_phase11_dw_wdt_remove_idle_split_tests.step);
    test_step.dependOn(&run_phase11_hvc_console_poll_retry_split_tests.step);

    const hvc_console_survey_step = b.step(
        \"hvc-console-survey\",
        \"Run the dedicated Phase 11 hvc_console survey replay\",
    );
    hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);
    const phase11_hvc_console_survey_tests = b.addTest(.{
        .name = \"phase11-hvc-console-survey-tests\",
        .root_module = phase11_hvc_console_poll_retry_split_module,
    });
    _ = phase11_hvc_console_survey_tests;
}
"""
    write_text(root / "zigux/tests/phase11_build.zig", build_text)

    fixture = {
        "build_test_names": [
            "phase11-dw-wdt-remove-idle-split-tests",
            "phase11-hvc-console-poll-retry-split-tests",
            "phase11-hvc-console-survey-tests",
        ],
        "shared_test_depend_steps": [
            "run_phase11_dw_wdt_remove_idle_split_tests",
            "run_phase11_hvc_console_poll_retry_split_tests",
        ],
        "module_root_source_files": [
            {"module": "dw_wdt_module", "path": "../../drivers/watchdog/dw_wdt.zig"},
            {
                "module": "phase11_dw_wdt_remove_idle_split_module",
                "path": "phase11_dw_wdt_remove_idle_split.zig",
            },
            {"module": "hvc_console_module", "path": "../../drivers/tty/hvc/hvc_console.zig"},
            {
                "module": "phase11_hvc_console_poll_retry_split_module",
                "path": "phase11_hvc_console_poll_retry_split.zig",
            },
        ],
        "module_imports": [
            {
                "module": "phase11_dw_wdt_remove_idle_split_module",
                "import_name": "dw_wdt",
                "imported_module": "dw_wdt_module",
            },
            {
                "module": "phase11_hvc_console_poll_retry_split_module",
                "import_name": "hvc_console",
                "imported_module": "hvc_console_module",
            },
        ],
        "test_root_modules": [
            {
                "test": "phase11-dw-wdt-remove-idle-split-tests",
                "root_module": "phase11_dw_wdt_remove_idle_split_module",
            },
            {
                "test": "phase11-hvc-console-poll-retry-split-tests",
                "root_module": "phase11_hvc_console_poll_retry_split_module",
            },
            {
                "test": "phase11-hvc-console-survey-tests",
                "root_module": "phase11_hvc_console_poll_retry_split_module",
            },
        ],
        "forbidden_markers": FORBIDDEN_BUILD_MARKERS,
        "dedicated_survey_replays": DEDICATED_SURVEY_REPLAYS,
        "shared_split_replays": [
            {
                "test": "phase11-dw-wdt-remove-idle-split-tests",
                "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
            },
            {
                "test": "phase11-hvc-console-poll-retry-split-tests",
                "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
            },
        ],
    }
    write_text(
        root / "zigux/tests/fixtures/phase11_build_inventory.json",
        json.dumps(fixture, indent=2) + "\n",
    )

    artifact_diff = """#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode")
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args()
    left = json.loads(Path(args.left).read_text(encoding=\"utf-8\"))
    right = json.loads(Path(args.right).read_text(encoding=\"utf-8\"))
    if left != right:
        print(\"ARTIFACT_DIFF=fail\")
        return 1
    print(\"ARTIFACT_DIFF=pass\")
    return 0


if __name__ == \"__main__\":
    raise SystemExit(main())
"""
    write_text(root / "scripts/zigux/artifact_diff.py", artifact_diff)

    for rel_path in [
        "drivers/watchdog/dw_wdt.zig",
        "drivers/tty/hvc/hvc_console.zig",
        "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    ]:
        write_text(root / rel_path, "// self-test placeholder\n")

    write_text(root / "scripts/zigux/check-phase11-build-inventory.py", Path(__file__).read_text(encoding="utf-8"))


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase11-build-inventory.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def expect_missing_root(label: str, root: Path, expected_marker: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-build-inventory-self-test:{label}:unexpected_pass")
    if "PHASE11_BUILD_INVENTORY=fail" not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:missing_fail_token:{actual}"
        )
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:expected_missing_root:{expected_marker}:actual:{actual}"
        )


def expect_inventory_drift(label: str, root: Path) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-build-inventory-self-test:{label}:unexpected_pass")
    if "PHASE11_BUILD_INVENTORY=fail" not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:missing_fail_token:{actual}"
        )
    if "ARTIFACT_DIFF=fail" not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:missing_artifact_diff_fail:{actual}"
        )


def expect_build_step_drift(label: str, root: Path, expected_marker: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-build-inventory-self-test:{label}:unexpected_pass")
    if "PHASE11_BUILD_INVENTORY=fail" not in result.stdout:
        actual = result.stdout.strip() or result.stderr.strip() or "no_output"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:missing_fail_token:{actual}"
        )
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase11-build-inventory-self-test:{label}:expected_missing_build_step:{expected_marker}:actual:{actual}"
        )


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
        dw_backup = dw_split.read_text(encoding="utf-8")
        dw_split.unlink()
        expect_missing_root(
            "missing_dw_split",
            tmp_root,
            "phase11_dw_wdt_remove_idle_split_module:phase11_dw_wdt_remove_idle_split.zig",
        )
        write_text(dw_split, dw_backup)

        hvc_split = tmp_root / "zigux/tests/phase11_hvc_console_poll_retry_split.zig"
        hvc_backup = hvc_split.read_text(encoding="utf-8")
        hvc_split.unlink()
        expect_missing_root(
            "missing_hvc_split",
            tmp_root,
            "phase11_hvc_console_poll_retry_split_module:phase11_hvc_console_poll_retry_split.zig",
        )
        write_text(hvc_split, hvc_backup)

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
        expect_inventory_drift(
            "shared_test_step_includes_dedicated_hvc_survey",
            tmp_root,
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
        expect_build_step_drift(
            "shared_test_step_name_drift",
            tmp_root,
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
        expect_build_step_drift(
            "dedicated_hvc_survey_binding_missing",
            tmp_root,
            "binding:hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
        )
        write_text(build_path, build_backup)

        fixture_path = tmp_root / "zigux/tests/fixtures/phase11_build_inventory.json"
        fixture_backup = fixture_path.read_text(encoding="utf-8")
        fixture = json.loads(fixture_backup)
        fixture["forbidden_markers"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_inventory_drift(
            "forbidden_markers_fixture_drift",
            tmp_root,
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

        fixture = json.loads(fixture_backup)
        fixture["dedicated_survey_replays"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_inventory_drift(
            "dedicated_survey_replays_fixture_drift",
            tmp_root,
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

        fixture = json.loads(fixture_backup)
        fixture["shared_split_replays"] = []
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        expect_inventory_drift(
            "shared_split_replays_fixture_drift",
            tmp_root,
        )
        fixture_path.write_text(fixture_backup, encoding="utf-8")

    print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
    print("PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    _ = load_json(FIXTURE_PATH)
    generated = render_inventory()
    missing_module_roots = validate_module_root_paths_exist(generated)

    if missing_module_roots:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_START")
        for item in missing_module_roots:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_MODULE_ROOTS_END")
        return 1

    build_text = BUILD_PATH.read_text(encoding="utf-8")
    missing_build_steps = validate_named_build_steps(build_text)
    if missing_build_steps:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_MISSING_BUILD_STEPS_START")
        for item in missing_build_steps:
            print(item)
        print("PHASE11_BUILD_INVENTORY_MISSING_BUILD_STEPS_END")
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase11_inventory_") as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / "phase11_build_inventory.json"
        actual_path.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACT_DIFF_PATH),
                "--mode",
                "json",
                str(FIXTURE_PATH),
                str(actual_path),
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        print("PHASE11_BUILD_INVENTORY=fail")
        return result.returncode

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(run_self_test())
    raise SystemExit(main())
