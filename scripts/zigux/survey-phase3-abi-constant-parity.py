#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HEADER = ROOT / "include" / "zigux" / "abi.h"
DEFAULT_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
DEFAULT_DUMP = ROOT / "zigux" / "tests" / "phase3_abi_dump.zig"
DEFAULT_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi" / "phase3_abi_c_harness.c"
DEFAULT_EXPECTED = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi" / "expected.json"

BASELINE_CONSTANTS = (
    ("ZIGUX_FACILITY_KERNEL", "FACILITY_KERNEL", "facility_kernel", 1),
    ("ZIGUX_FACILITY_HELPERS", "FACILITY_HELPERS", "facility_helpers", 2),
    ("ZIGUX_FACILITY_DRIVERS", "FACILITY_DRIVERS", "facility_drivers", 3),
    ("ZIGUX_STATUS_FLAG_ERROR", "STATUS_FLAG_ERROR", "status_flag_error", 1),
    ("ZIGUX_PANIC_ABORT", "PANIC_ABORT", "panic_abort", 0),
    ("ZIGUX_PANIC_BUG", "PANIC_BUG", "panic_bug", 1),
    ("ZIGUX_PANIC_WARN", "PANIC_WARN", "panic_warn", 2),
    ("ZIGUX_ALLOC_CALLER_PROVIDED", "ALLOC_CALLER_PROVIDED", "allocator_caller_provided", 0),
    ("ZIGUX_ALLOC_KERNEL_HEAP", "ALLOC_KERNEL_HEAP", "allocator_kernel_heap", 1),
    ("ZIGUX_ALLOC_ARENA", "ALLOC_ARENA", "allocator_arena", 2),
    ("ZIGUX_UNSAFE_NONE", "UNSAFE_NONE", "unsafe_scope_none", 0),
    ("ZIGUX_UNSAFE_VOLATILE_MMIO", "UNSAFE_VOLATILE_MMIO", "unsafe_scope_volatile_mmio", 1),
    ("ZIGUX_UNSAFE_RAW_POINTER_BRIDGE", "UNSAFE_RAW_POINTER_BRIDGE", "unsafe_scope_raw_pointer_bridge", 2),
)

HEADER_DEFINE_RE = re.compile(r"^#define\s+(?P<name>[A-Z0-9_]+)\s+(?P<value>[0-9xa-fA-F]+)U?$")
BINDING_CONST_RE = re.compile(r"^pub const (?P<name>[A-Z0-9_]+): [^=]+ = (?P<value>[0-9xa-fA-F]+);$")


def parse_int(text: str) -> int:
    return int(text, 0)


def parse_header_constants(path: Path) -> dict[str, int]:
    constants: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADER_DEFINE_RE.match(line.strip())
        if match:
            constants[match.group("name")] = parse_int(match.group("value"))
    return constants


def parse_binding_constants(path: Path) -> dict[str, int]:
    constants: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = BINDING_CONST_RE.match(line.strip())
        if match:
            constants[match.group("name")] = parse_int(match.group("value"))
    return constants


def validate_constant_parity(
    header_path: Path,
    bindings_path: Path,
    dump_path: Path,
    harness_path: Path,
    expected_path: Path,
) -> list[str]:
    issues: list[str] = []
    header_constants = parse_header_constants(header_path)
    binding_constants = parse_binding_constants(bindings_path)
    dump_source = dump_path.read_text(encoding="utf-8")
    harness_source = harness_path.read_text(encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    expected_constants = expected.get("constants")

    if not isinstance(expected_constants, dict):
        issues.append(f"{expected_path}:missing_constants_object")
        expected_constants = {}

    for header_name, binding_name, json_key, expected_value in BASELINE_CONSTANTS:
        header_value = header_constants.get(header_name)
        if header_value is None:
            issues.append(f"{header_path}:missing_header_constant:{header_name}")
        elif header_value != expected_value:
            issues.append(f"{header_path}:wrong_header_value:{header_name}:{header_value}")

        binding_value = binding_constants.get(binding_name)
        if binding_value is None:
            issues.append(f"{bindings_path}:missing_binding_constant:{binding_name}")
        elif binding_value != expected_value:
            issues.append(f"{bindings_path}:wrong_binding_value:{binding_name}:{binding_value}")

        if f"\"{json_key}\":" not in dump_source:
            issues.append(f"{dump_path}:missing_dump_key:{json_key}")
        if f"\"{json_key}\":" not in harness_source:
            issues.append(f"{harness_path}:missing_harness_key:{json_key}")

        fixture_value = expected_constants.get(json_key)
        if fixture_value is None:
            issues.append(f"{expected_path}:missing_expected_key:{json_key}")
        elif fixture_value != expected_value:
            issues.append(f"{expected_path}:wrong_expected_value:{json_key}:{fixture_value}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_constant_parity_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        header = root / "include" / "zigux" / "abi.h"
        bindings = root / "zigux" / "bindings" / "abi.zig"
        dump = root / "zigux" / "tests" / "phase3_abi_dump.zig"
        harness = root / "zigux" / "tests" / "fixtures" / "phase3_abi" / "phase3_abi_c_harness.c"
        expected = root / "zigux" / "tests" / "fixtures" / "phase3_abi" / "expected.json"

        for path in (header.parent, bindings.parent, dump.parent, harness.parent, expected.parent):
            path.mkdir(parents=True, exist_ok=True)

        header.write_text(
            "\n".join(f"#define {header_name} {value}U" for header_name, _, _, value in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        bindings.write_text(
            "\n".join(f"pub const {binding_name}: u32 = {value};" for _, binding_name, _, value in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        dump.write_text(
            "\n".join(f"// \"{json_key}\":" for _, _, json_key, _ in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        harness.write_text(
            "\n".join(f"/* \"{json_key}\": */" for _, _, json_key, _ in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        expected.write_text(
            json.dumps({"constants": {json_key: value for _, _, json_key, value in BASELINE_CONSTANTS}}),
            encoding="utf-8",
            newline="\n",
        )

        assert validate_constant_parity(header, bindings, dump, harness, expected) == []

        bindings.write_text("pub const STATUS_FLAG_ERROR: u16 = 1;\n", encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, dump, harness, expected)
        assert f"{bindings}:missing_binding_constant:FACILITY_KERNEL" in issues

        bindings.write_text(
            "\n".join(f"pub const {binding_name}: u32 = {value};" for _, binding_name, _, value in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        dump.write_text("// \"facility_kernel\":\n", encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, dump, harness, expected)
        assert f"{dump}:missing_dump_key:facility_helpers" in issues

        dump.write_text(
            "\n".join(f"// \"{json_key}\":" for _, _, json_key, _ in BASELINE_CONSTANTS) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        expected.write_text(json.dumps({"constants": {"facility_kernel": 7}}), encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, dump, harness, expected)
        assert f"{expected}:wrong_expected_value:facility_kernel:7" in issues
        assert f"{expected}:missing_expected_key:facility_helpers" in issues

    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Survey baseline Phase 3 ABI constant parity across the C header, curated Zig bindings, dump replay, C harness, and committed expected fixture."
    )
    parser.add_argument("--header-path", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--bindings-path", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--dump-path", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--harness-path", type=Path, default=DEFAULT_HARNESS)
    parser.add_argument("--expected-path", type=Path, default=DEFAULT_EXPECTED)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_constant_parity(
        args.header_path,
        args.bindings_path,
        args.dump_path,
        args.harness_path,
        args.expected_path,
    )
    if issues:
        print("PHASE3_ABI_CONSTANT_PARITY=fail")
        print("PHASE3_ABI_CONSTANT_PARITY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_CONSTANT_PARITY_ISSUES_END")
        return 1

    print("PHASE3_ABI_CONSTANT_PARITY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
