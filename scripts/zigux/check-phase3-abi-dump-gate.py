#!/usr/bin/env python3
"""Fail-close the focused Phase 3 ABI dump and interop-gate reminder surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
VALIDATE_PHASE3_PATH = Path("scripts/zigux/validate-phase3.py")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/build.zig")
DUMP_PATH = Path("zigux/tests/phase3_abi_dump.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_abi/expected.json")
HARNESS_PATH = Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c")

REQUIRED_PACKET_FILES = (
    BUILD_PATH,
    DUMP_PATH,
    EXPECTED_PATH,
    HARNESS_PATH,
)

SLICE_NOTE_MARKERS = (
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-dump-gate.py",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
)

SCRIPTS_README_MARKERS = (
    "check-phase3-abi-dump-gate.py",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)

VALIDATE_PHASE3_MARKERS = (
    'Path("zigux/tests/phase3_abi_dump.zig")',
    'Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c")',
    'Path("zigux/tests/fixtures/phase3_abi/expected.json")',
    'Path("scripts/zigux/check-phase3-abi-dump-gate.py")',
)

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)',
)

MAKEFILE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py",
    "phase3-interop:",
    "$(PYTHON) scripts/zigux/run-phase3-checks.py",
    "$(ZIG) build phase3-dump --build-file zigux/tests/build.zig",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/run-phase3-checks.py",
    "run: zig build phase3-dump --build-file zigux/tests/build.zig",
)

BUILD_MARKERS = (
    "phase3_abi_dump.zig",
    "phase3-dump",
)

REQUIRED_REPLAY_CONSTANT_KEYS = (
    "abi_version",
    "facility_kernel",
    "facility_helpers",
    "facility_drivers",
    "status_flag_error",
    "panic_abort",
    "panic_bug",
    "panic_warn",
    "allocator_caller_provided",
    "allocator_kernel_heap",
    "allocator_arena",
    "unsafe_scope_none",
    "unsafe_scope_volatile_mmio",
    "unsafe_scope_raw_pointer_bridge",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_flag_window_applied",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_status_skipped",
)

REQUIRED_EXPECTED_CONSTANT_VALUES = {
    "facility_kernel": 1,
    "facility_helpers": 2,
    "facility_drivers": 3,
    "status_flag_error": 1,
    "panic_abort": 0,
    "panic_bug": 1,
    "panic_warn": 2,
    "allocator_caller_provided": 0,
    "allocator_kernel_heap": 1,
    "allocator_arena": 2,
    "unsafe_scope_none": 0,
    "unsafe_scope_volatile_mmio": 1,
    "unsafe_scope_raw_pointer_bridge": 2,
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped": 1,
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied": 1,
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_flag_window_applied": 1,
    "chrdev_notify_ack_window_policy_budget_window_delivery_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED": 1,
}

REQUIRED_REPLAY_STRUCT_MARKERS = (
    "boundary_header",
    "export_status",
    "interop_policy",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_view",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_summary",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary",
)

REQUIRED_EXPECTED_STRUCT_LAYOUTS = {
    "boundary_header": {
        "size": 8,
        "align": 4,
        "offsets": {
            "size": 0,
            "abi_version": 4,
            "flags": 6,
        },
    },
    "export_status": {
        "size": 8,
        "align": 4,
        "offsets": {
            "code": 0,
            "facility": 4,
            "flags": 6,
        },
    },
    "interop_policy": {
        "size": 4,
        "align": 1,
        "offsets": {
            "panic_mode": 0,
            "allocator_mode": 1,
            "unsafe_scope": 2,
            "reserved": 3,
        },
    },
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_view": {
        "size": 12,
        "align": 4,
        "offsets": {
            "ack_window": 0,
            "delivery_window": 4,
            "status": 8,
        },
    },
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_summary": {
        "size": 12,
        "align": 4,
        "offsets": {
            "applied": 0,
            "skipped": 4,
            "delivered": 8,
        },
    },
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view": {
        "size": 12,
        "align": 4,
        "offsets": {
            "budget": 0,
            "window": 4,
            "flags": 8,
        },
    },
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary": {
        "size": 12,
        "align": 4,
        "offsets": {
            "attempted": 0,
            "applied": 4,
            "skipped": 8,
        },
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def _validate_replay_struct_markers(path: Path, label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}]
    return [
        f"missing {label} struct marker: {marker}"
        for marker in REQUIRED_REPLAY_STRUCT_MARKERS
        if marker not in text
    ]


def _validate_replay_constant_markers(path: Path, label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}]
    return [
        f"missing {label} constant marker: {marker}"
        for marker in REQUIRED_REPLAY_CONSTANT_KEYS
        if marker not in text
    ]


def _validate_expected_fixture(path: Path) -> list[str]:
    try:
        payload = json.loads(_read(path))
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}]
    except json.JSONDecodeError as exc:
        return [f"invalid expected fixture JSON: {exc.msg}"]

    constants = payload.get("constants")
    if not isinstance(constants, dict):
        return [f"{path}:missing_constants_object"]

    issues: list[str] = []
    for constant_name, expected_value in REQUIRED_EXPECTED_CONSTANT_VALUES.items():
        actual_value = constants.get(constant_name)
        if actual_value is None:
            issues.append(f"{path}:missing_expected_constant:{constant_name}")
        elif actual_value != expected_value:
            issues.append(f"{path}:wrong_expected_constant:{constant_name}:{actual_value}")

    structs = payload.get("structs")
    if not isinstance(structs, dict):
        issues.append(f"{path}:missing_structs_object")
        return issues

    for struct_name, expected_layout in REQUIRED_EXPECTED_STRUCT_LAYOUTS.items():
        actual_layout = structs.get(struct_name)
        if not isinstance(actual_layout, dict):
            issues.append(f"{path}:missing_expected_struct:{struct_name}")
            continue

        actual_size = actual_layout.get("size")
        if actual_size is None:
            issues.append(f"{path}:missing_expected_struct_size:{struct_name}")
        elif actual_size != expected_layout["size"]:
            issues.append(f"{path}:wrong_expected_struct_size:{struct_name}:{actual_size}")

        actual_align = actual_layout.get("align")
        if actual_align is None:
            issues.append(f"{path}:missing_expected_struct_align:{struct_name}")
        elif actual_align != expected_layout["align"]:
            issues.append(f"{path}:wrong_expected_struct_align:{struct_name}:{actual_align}")

        actual_offsets = actual_layout.get("offsets")
        if not isinstance(actual_offsets, dict):
            issues.append(f"{path}:missing_expected_struct_offsets:{struct_name}")
            continue

        for field_name, expected_offset in expected_layout["offsets"].items():
            actual_offset = actual_offsets.get(field_name)
            if actual_offset is None:
                issues.append(f"{path}:missing_expected_struct_offset:{struct_name}:{field_name}")
            elif actual_offset != expected_offset:
                issues.append(
                    f"{path}:wrong_expected_struct_offset:{struct_name}:{field_name}:{actual_offset}"
                )

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(_check_markers(repo_root / SLICE_NOTE_PATH, SLICE_NOTE_MARKERS, "slice note"))
    issues.extend(_check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README"))
    issues.extend(
        _check_markers(repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README")
    )
    issues.extend(
        _check_markers(repo_root / VALIDATE_PHASE3_PATH, VALIDATE_PHASE3_MARKERS, "phase3 validator")
    )
    issues.extend(
        _check_markers(
            repo_root / SELFTEST_DRIVER_PATH,
            SELFTEST_DRIVER_MARKERS,
            "phase3 selftest driver",
        )
    )
    issues.extend(_check_markers(repo_root / MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile"))
    issues.extend(_check_markers(repo_root / WORKFLOW_PATH, WORKFLOW_MARKERS, "workflow"))
    issues.extend(_check_markers(repo_root / BUILD_PATH, BUILD_MARKERS, "build file"))
    for rel_path in REQUIRED_PACKET_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    issues.extend(_validate_replay_struct_markers(repo_root / DUMP_PATH, "dump"))
    issues.extend(_validate_replay_constant_markers(repo_root / DUMP_PATH, "dump"))
    issues.extend(_validate_replay_struct_markers(repo_root / HARNESS_PATH, "harness"))
    issues.extend(_validate_replay_constant_markers(repo_root / HARNESS_PATH, "harness"))
    issues.extend(_validate_expected_fixture(repo_root / EXPECTED_PATH))
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _expected_fixture_stub() -> str:
    return json.dumps(
        {
            "constants": REQUIRED_EXPECTED_CONSTANT_VALUES,
            "structs": REQUIRED_EXPECTED_STRUCT_LAYOUTS,
        },
        indent=2,
    ) + "\n"


def _build_stub() -> str:
    return (
        'const phase3_abi_dump_module = b.createModule(.{\n'
        '    .root_source_file = b.path("phase3_abi_dump.zig"),\n'
        '});\n'
        'const phase3_dump_step = b.step("phase3-dump", "Run Phase 3 ABI interop dump");\n'
    )


def _populate_repo(root: Path) -> None:
    _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / VALIDATE_PHASE3_PATH, "\n".join(VALIDATE_PHASE3_MARKERS) + "\n")
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    _write(root / WORKFLOW_PATH, "\n".join(WORKFLOW_MARKERS) + "\n")
    _write(root / BUILD_PATH, _build_stub())
    _write(
        root / DUMP_PATH,
        "\n".join(REQUIRED_REPLAY_CONSTANT_KEYS + REQUIRED_REPLAY_STRUCT_MARKERS) + "\n",
    )
    _write(
        root / HARNESS_PATH,
        "\n".join(REQUIRED_REPLAY_CONSTANT_KEYS + REQUIRED_REPLAY_STRUCT_MARKERS) + "\n",
    )
    _write(root / EXPECTED_PATH, _expected_fixture_stub())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_dump_gate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        broken = root / SLICE_NOTE_PATH
        broken.write_text(
            _read(broken).replace(
                "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing slice note marker: "
            "python3 scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing slice-note dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / TESTS_README_PATH
        broken.write_text(
            _read(broken).replace("zigux/tests/phase3_abi_dump.zig\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing tests README marker: zigux/tests/phase3_abi_dump.zig"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing tests README dump marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / VALIDATE_PHASE3_PATH
        broken.write_text(
            _read(broken).replace('Path("scripts/zigux/check-phase3-abi-dump-gate.py")\n', "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = 'missing phase3 validator marker: Path("scripts/zigux/check-phase3-abi-dump-gate.py")'
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing validator dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / SELFTEST_DRIVER_PATH
        broken.write_text(
            _read(broken).replace(
                'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            'missing phase3 selftest driver marker: '
            'Path("scripts/zigux/check-phase3-abi-dump-gate.py"), ("--self-test",)'
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing selftest-driver dump-gate marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / MAKEFILE_PATH
        broken.write_text(
            _read(broken).replace(
                "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing makefile marker: "
            "$(PYTHON) scripts/zigux/check-phase3-abi-dump-gate.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing makefile dump-gate self-test marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / MAKEFILE_PATH
        broken.write_text(
            _read(broken).replace("phase3-interop:\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing makefile marker: phase3-interop:"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing makefile interop target was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / WORKFLOW_PATH
        broken.write_text(
            _read(broken).replace("run: python3 scripts/zigux/run-phase3-checks.py\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing workflow marker: run: python3 scripts/zigux/run-phase3-checks.py"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing workflow interop replay marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / BUILD_PATH
        broken.write_text(
            _read(broken).replace("phase3-dump", "phase3-shadow-dump", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing build file marker: phase3-dump"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing build-step marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        missing_packet_file = REQUIRED_PACKET_FILES[0]
        (root / missing_packet_file).unlink()
        issues = validate_repo(root)
        expected = f"missing repo file: {missing_packet_file.as_posix()}"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing dump packet file was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / DUMP_PATH
        broken.write_text(
            _read(broken).replace("boundary_header\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing dump struct marker: boundary_header"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing core dump struct marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / DUMP_PATH
        broken.write_text(
            _read(broken).replace("allocator_arena\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing dump constant marker: allocator_arena"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing dump constant marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / HARNESS_PATH
        broken.write_text(
            _read(broken).replace(
                "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing harness struct marker: "
            "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing harness struct marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / HARNESS_PATH
        broken.write_text(
            _read(broken).replace("panic_warn\n", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing harness constant marker: panic_warn"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing harness constant marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["constants"].pop("unsafe_scope_raw_pointer_bridge", None)
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = f"{root / EXPECTED_PATH}:missing_expected_constant:unsafe_scope_raw_pointer_bridge"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing expected-fixture constant was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["constants"]["status_flag_error"] = 7
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = f"{root / EXPECTED_PATH}:wrong_expected_constant:status_flag_error:7"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected wrong expected-fixture constant was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["structs"].pop("boundary_header", None)
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = f"{root / EXPECTED_PATH}:missing_expected_struct:boundary_header"
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing expected-fixture core struct was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["structs"]["interop_policy"]["offsets"]["reserved"] = 5
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = (
            f"{root / EXPECTED_PATH}:wrong_expected_struct_offset:"
            "interop_policy:reserved:5"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected wrong core expected-fixture struct offset was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["structs"][
            "chrdev_notify_ack_window_policy_budget_window_delivery_window_view"
        ]["size"] = 16
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = (
            f"{root / EXPECTED_PATH}:wrong_expected_struct_size:"
            "chrdev_notify_ack_window_policy_budget_window_delivery_window_view:16"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected wrong expected-fixture struct size was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        broken = root / EXPECTED_PATH
        payload = json.loads(_read(broken))
        payload["structs"][
            "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary"
        ]["offsets"].pop("skipped", None)
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = (
            f"{root / EXPECTED_PATH}:missing_expected_struct_offset:"
            "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary:skipped"
        )
        if expected not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing expected-fixture struct offset was not reported")
            return 1
        case_count += 1

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print(f"PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI dump-gate reminder surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI dump packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_DUMP_GATE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SLICE_NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
