#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

INVENTORY_PATH = "zigux/tests/fixtures/phase11_build_inventory.json"
SURVEY_PATH = "zigux/tests/phase11_dw_wdt_survey.zig"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_BUILD_TEST_NAMES = [
    "phase11-dw-wdt-tests",
    "phase11-dw-wdt-suspend-resume-tests",
    "phase11-dw-wdt-remove-idle-split-tests",
    "phase11-dw-wdt-survey-tests",
]

REQUIRED_SHARED_TEST_DEPEND_STEPS = [
    "run_phase11_dw_wdt_tests",
    "run_phase11_dw_wdt_suspend_resume_tests",
    "run_phase11_dw_wdt_remove_idle_split_tests",
    "run_phase11_dw_wdt_survey_tests",
]

REQUIRED_MODULE_ROOT_SOURCE_FILES = [
    {
        "module": "phase11_dw_wdt_suspend_resume_module",
        "path": "phase11_dw_wdt_suspend_resume.zig",
    },
    {
        "module": "phase11_dw_wdt_remove_idle_split_module",
        "path": "phase11_dw_wdt_remove_idle_split.zig",
    },
]

REQUIRED_MODULE_IMPORTS = [
    {
        "module": "phase11_dw_wdt_suspend_resume_module",
        "import_name": "dw_wdt",
        "imported_module": "dw_wdt_module",
    },
    {
        "module": "phase11_dw_wdt_remove_idle_split_module",
        "import_name": "dw_wdt",
        "imported_module": "dw_wdt_module",
    },
]

REQUIRED_TEST_ROOT_MODULES = [
    {
        "test": "phase11-dw-wdt-suspend-resume-tests",
        "root_module": "phase11_dw_wdt_suspend_resume_module",
    },
    {
        "test": "phase11-dw-wdt-remove-idle-split-tests",
        "root_module": "phase11_dw_wdt_remove_idle_split_module",
    },
]

REQUIRED_SHARED_SPLIT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-remove-idle-split-tests",
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
    }
]

REQUIRED_SHARED_ADJUNCT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-suspend-resume-tests",
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
    }
]

REQUIRED_SHARED_REPLAY_MARKERS = [
    {
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        "marker": "try std.testing.expect(summary.resume_preserves_timeout_programming);",
    },
    {
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "marker": "try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    },
]

REQUIRED_SURVEY_MARKERS = [
    '"phase11-build-gate"',
    '"phase11-dw-wdt-survey-gate"',
    '"phase11-dw-wdt-registration-handoff"',
    '"phase11-dw-wdt-platform-and-pm"',
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase11-validate phase11-test phase11-hvc-survey phase11",
    "phase11-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-validate phase11-test phase11-hvc-survey",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_exact_line(text: str, target: str) -> str:
    kept_lines = [line for line in text.splitlines() if line != target]
    return "\n".join(kept_lines) + "\n"


def contains_dict(items: list[dict[str, object]], expected: dict[str, str]) -> bool:
    return any(all(item.get(key) == value for key, value in expected.items()) for item in items)


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in [INVENTORY_PATH, SURVEY_PATH, MAKEFILE_PATH]:
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    inventory = json.loads(read_text(root, INVENTORY_PATH))
    survey = read_text(root, SURVEY_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    makefile_lines = makefile.splitlines()

    build_test_names = inventory.get("build_test_names", [])
    for test_name in REQUIRED_BUILD_TEST_NAMES:
        if build_test_names.count(test_name) != 1:
            issues.append(f"build_test_names:{test_name}")

    shared_steps = inventory.get("shared_test_depend_steps", [])
    for step_name in REQUIRED_SHARED_TEST_DEPEND_STEPS:
        if shared_steps.count(step_name) != 1:
            issues.append(f"shared_test_depend_steps:{step_name}")

    module_root_source_files = inventory.get("module_root_source_files", [])
    for entry in REQUIRED_MODULE_ROOT_SOURCE_FILES:
        if not contains_dict(module_root_source_files, entry):
            issues.append(
                "module_root_source_files:"
                f"{entry['module']}->{entry['path']}"
            )

    module_imports = inventory.get("module_imports", [])
    for entry in REQUIRED_MODULE_IMPORTS:
        if not contains_dict(module_imports, entry):
            issues.append(
                "module_imports:"
                f"{entry['module']}->{entry['import_name']}->{entry['imported_module']}"
            )

    test_root_modules = inventory.get("test_root_modules", [])
    for entry in REQUIRED_TEST_ROOT_MODULES:
        if not contains_dict(test_root_modules, entry):
            issues.append(
                "test_root_modules:"
                f"{entry['test']}->{entry['root_module']}"
            )

    shared_split_replays = inventory.get("shared_split_replays", [])
    for entry in REQUIRED_SHARED_SPLIT_REPLAYS:
        if not contains_dict(shared_split_replays, entry):
            issues.append(
                "shared_split_replays:"
                f"{entry['test']}->{entry['path']}"
            )

    shared_adjunct_replays = inventory.get("shared_adjunct_replays", [])
    for entry in REQUIRED_SHARED_ADJUNCT_REPLAYS:
        if not contains_dict(shared_adjunct_replays, entry):
            issues.append(
                "shared_adjunct_replays:"
                f"{entry['test']}->{entry['path']}"
            )

    shared_replay_markers = inventory.get("shared_replay_markers", [])
    for entry in REQUIRED_SHARED_REPLAY_MARKERS:
        if not contains_dict(shared_replay_markers, entry):
            issues.append(
                "shared_replay_markers:"
                f"{entry['path']}->{entry['marker']}"
            )

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            issues.append(f"survey:{marker}")

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile_lines:
            issues.append(f"makefile:{marker}")

    return issues


def seed_fixture_tree(root: Path) -> None:
    inventory = {
        "build_test_names": REQUIRED_BUILD_TEST_NAMES,
        "shared_test_depend_steps": REQUIRED_SHARED_TEST_DEPEND_STEPS,
        "module_root_source_files": REQUIRED_MODULE_ROOT_SOURCE_FILES,
        "module_imports": REQUIRED_MODULE_IMPORTS,
        "test_root_modules": REQUIRED_TEST_ROOT_MODULES,
        "shared_split_replays": REQUIRED_SHARED_SPLIT_REPLAYS,
        "shared_adjunct_replays": REQUIRED_SHARED_ADJUNCT_REPLAYS,
        "shared_replay_markers": REQUIRED_SHARED_REPLAY_MARKERS,
    }
    write_text(root / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                "const sentinel = struct {",
                "    const build_gate = \"phase11-build-gate\";",
                "    const survey_gate = \"phase11-dw-wdt-survey-gate\";",
                "    const registration_handoff = \"phase11-dw-wdt-registration-handoff\";",
                "    const platform_pm = \"phase11-dw-wdt-platform-and-pm\";",
                "};",
            ]
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n",
    )


def assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase11-build-inventory-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_inventory_") as tmp_dir:
        root = Path(tmp_dir)
        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        inventory_path = root / INVENTORY_PATH
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["build_test_names"].remove("phase11-dw-wdt-suspend-resume-tests")
        write_text(inventory_path, json.dumps(inventory, indent=2) + "\n")
        assert_only(
            validate(root),
            ["build_test_names:phase11-dw-wdt-suspend-resume-tests"],
            "missing_suspend_resume_test_name",
        )
        seed_fixture_tree(root)
        case_count += 1

        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["shared_test_depend_steps"].remove("run_phase11_dw_wdt_remove_idle_split_tests")
        write_text(inventory_path, json.dumps(inventory, indent=2) + "\n")
        assert_only(
            validate(root),
            ["shared_test_depend_steps:run_phase11_dw_wdt_remove_idle_split_tests"],
            "missing_remove_idle_step",
        )
        seed_fixture_tree(root)
        case_count += 1

        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["shared_adjunct_replays"] = []
        write_text(inventory_path, json.dumps(inventory, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                "shared_adjunct_replays:phase11-dw-wdt-suspend-resume-tests->zigux/tests/phase11_dw_wdt_suspend_resume.zig"
            ],
            "missing_adjunct_replay",
        )
        seed_fixture_tree(root)
        case_count += 1

        survey_path = root / SURVEY_PATH
        survey_path.write_text("const stale = \"phase11-build-gate\";\n", encoding="utf-8")
        assert_only(
            validate(root),
            [
                'survey:"phase11-dw-wdt-survey-gate"',
                'survey:"phase11-dw-wdt-registration-handoff"',
                'survey:"phase11-dw-wdt-platform-and-pm"',
            ],
            "missing_survey_markers",
        )
        seed_fixture_tree(root)
        case_count += 1

        makefile_path = root / MAKEFILE_PATH
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            remove_exact_line(
                makefile_text,
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test",
            ),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            [
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py --self-test"
            ],
            "missing_makefile_self_test_route",
        )
        seed_fixture_tree(root)
        case_count += 1

        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            remove_exact_line(
                makefile_text,
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py",
            ),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            [
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-build-inventory.py"
            ],
            "missing_makefile_live_route",
        )
        case_count += 1

    print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
    print(f"PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 11 DesignWare build-inventory packet and its make-based replay route."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE11_BUILD_INVENTORY=fail")
        print("PHASE11_BUILD_INVENTORY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE11_BUILD_INVENTORY_ISSUES_END")
        return 1

    print("PHASE11_BUILD_INVENTORY=pass")
    print(
        "PHASE11_BUILD_INVENTORY_MARKER_COUNT="
        f"{len(REQUIRED_BUILD_TEST_NAMES) + len(REQUIRED_SHARED_TEST_DEPEND_STEPS) + len(REQUIRED_MODULE_ROOT_SOURCE_FILES) + len(REQUIRED_MODULE_IMPORTS) + len(REQUIRED_TEST_ROOT_MODULES) + len(REQUIRED_SHARED_SPLIT_REPLAYS) + len(REQUIRED_SHARED_ADJUNCT_REPLAYS) + len(REQUIRED_SHARED_REPLAY_MARKERS) + len(REQUIRED_SURVEY_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())