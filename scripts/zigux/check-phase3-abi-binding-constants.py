#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent
FAIL_BANNER = "PHASE3_ABI_BINDING_CONSTANTS=fail"
PASS_BANNER = "PHASE3_ABI_BINDING_CONSTANTS=pass"
SELF_TEST_BANNER = "PHASE3_ABI_BINDING_CONSTANTS_SELF_TEST=pass"
HEADER_REL = "include/zigux/abi.h"
BINDINGS_REL = "zigux/bindings/abi.zig"

HEADER_CONSTANTS = {
    "abi_version": "ZIGUX_ABI_VERSION",
    "status_flag_error": "ZIGUX_STATUS_FLAG_ERROR",
    "facility_kernel": "ZIGUX_FACILITY_KERNEL",
    "facility_helpers": "ZIGUX_FACILITY_HELPERS",
    "facility_drivers": "ZIGUX_FACILITY_DRIVERS",
    "panic_abort": "ZIGUX_PANIC_ABORT",
    "panic_bug": "ZIGUX_PANIC_BUG",
    "panic_warn": "ZIGUX_PANIC_WARN",
    "allocator_caller_provided": "ZIGUX_ALLOC_CALLER_PROVIDED",
    "allocator_kernel_heap": "ZIGUX_ALLOC_KERNEL_HEAP",
    "allocator_arena": "ZIGUX_ALLOC_ARENA",
    "unsafe_scope_none": "ZIGUX_UNSAFE_NONE",
    "unsafe_scope_volatile_mmio": "ZIGUX_UNSAFE_VOLATILE_MMIO",
    "unsafe_scope_raw_pointer_bridge": "ZIGUX_UNSAFE_RAW_POINTER_BRIDGE",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped": "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied": "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
    "chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status_held": "ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD",
}

EXPECTED_VALUES = {
    "abi_version": 1,
    "status_flag_error": 1,
    "facility_kernel": 1,
    "facility_helpers": 2,
    "facility_drivers": 3,
    "panic_abort": 0,
    "panic_bug": 1,
    "panic_warn": 2,
    "allocator_caller_provided": 0,
    "allocator_kernel_heap": 1,
    "allocator_arena": 2,
    "unsafe_scope_none": 0,
    "unsafe_scope_volatile_mmio": 1,
    "unsafe_scope_raw_pointer_bridge": 2,
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped": 6,
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied": 1,
    "chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status_held": 7,
}

BINDING_CONST_NAMES = {
    "abi_version": "ABI_VERSION",
    "status_flag_error": "STATUS_FLAG_ERROR",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped": "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
    "chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied": "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
    "chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status_held": "CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD",
}

BINDING_ENUM_MEMBERS = {
    "facility_kernel": ("Facility", "kernel"),
    "facility_helpers": ("Facility", "helpers"),
    "facility_drivers": ("Facility", "drivers"),
    "panic_abort": ("PanicMode", "abort"),
    "panic_bug": ("PanicMode", "bug"),
    "panic_warn": ("PanicMode", "warn"),
    "allocator_caller_provided": ("AllocatorMode", "caller_provided"),
    "allocator_kernel_heap": ("AllocatorMode", "kernel_heap"),
    "allocator_arena": ("AllocatorMode", "arena"),
    "unsafe_scope_none": ("UnsafeScope", "none"),
    "unsafe_scope_volatile_mmio": ("UnsafeScope", "volatile_mmio"),
    "unsafe_scope_raw_pointer_bridge": ("UnsafeScope", "raw_pointer_bridge"),
}


def _parse_int(token: str) -> int:
    cleaned = re.sub(r"[uUlL]+$", "", token.strip())
    return int(cleaned, 0)


def _parse_header_constants(text: str) -> tuple[dict[str, int], set[str]]:
    constants: dict[str, int] = {}
    counts: dict[str, int] = {}
    for name, value in re.findall(r"^#define\s+(ZIGUX_[A-Z0-9_]+)\s+([^\s/]+)", text, re.MULTILINE):
        counts[name] = counts.get(name, 0) + 1
        try:
            constants[name] = _parse_int(value)
        except ValueError:
            continue
    duplicates = {name for name, count in counts.items() if count > 1}
    return constants, duplicates


def _parse_binding_constants(text: str) -> tuple[dict[str, int], set[str]]:
    constants: dict[str, int] = {}
    counts: dict[str, int] = {}
    for name, value in re.findall(r"^pub const\s+([A-Z0-9_]+)\s*:\s*[^=]+?=\s*([^;]+);", text, re.MULTILINE):
        counts[name] = counts.get(name, 0) + 1
        raw = value.strip().replace("_", "")
        if re.fullmatch(r"[-+]?0[xX][0-9a-fA-F]+|[-+]?[0-9]+", raw):
            constants[name] = int(raw, 0)
    duplicates = {name for name, count in counts.items() if count > 1}
    return constants, duplicates


def _parse_binding_enums(text: str) -> tuple[dict[str, dict[str, int]], dict[str, set[str]]]:
    enums: dict[str, dict[str, int]] = {}
    duplicate_members: dict[str, set[str]] = {}
    for enum_name, body in re.findall(
        r"pub const\s+([A-Za-z0-9_]+)\s*=\s*enum\([^\)]+\)\s*\{(.*?)\n\};",
        text,
        re.DOTALL,
    ):
        members: dict[str, int] = {}
        counts: dict[str, int] = {}
        for member, value in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^,\n]+)", body):
            counts[member] = counts.get(member, 0) + 1
            raw = value.strip().replace("_", "")
            if re.fullmatch(r"[-+]?0[xX][0-9a-fA-F]+|[-+]?[0-9]+", raw):
                members[member] = int(raw, 0)
        enums[enum_name] = members
        duplicate_members[enum_name] = {member for member, count in counts.items() if count > 1}
    return enums, duplicate_members


def validate_constants(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    header_path = root / HEADER_REL
    bindings_path = root / BINDINGS_REL
    if not header_path.exists():
        return [f"abi-binding-constants: missing {HEADER_REL}"]
    if not bindings_path.exists():
        return [f"abi-binding-constants: missing {BINDINGS_REL}"]

    header_text = header_path.read_text(encoding="utf-8")
    bindings_text = bindings_path.read_text(encoding="utf-8")
    header_constants, header_duplicates = _parse_header_constants(header_text)
    binding_constants, binding_duplicates = _parse_binding_constants(bindings_text)
    binding_enums, binding_enum_duplicates = _parse_binding_enums(bindings_text)

    for key, expected in EXPECTED_VALUES.items():
        header_name = HEADER_CONSTANTS[key]
        if header_name in header_duplicates:
            issues.append(f"abi-binding-constants: duplicate header definition for {header_name}")
        header_value = header_constants.get(header_name)
        if header_value is None:
            issues.append(f"abi-binding-constants: header missing {header_name}")
        elif header_value != expected:
            issues.append(f"abi-binding-constants: header {header_name}={header_value} expected {expected}")

        binding_value: int | None = None
        if key in BINDING_CONST_NAMES:
            binding_name = BINDING_CONST_NAMES[key]
            if binding_name in binding_duplicates:
                issues.append(f"abi-binding-constants: duplicate binding definition for {binding_name}")
            binding_value = binding_constants.get(binding_name)
            if binding_value is None:
                issues.append(f"abi-binding-constants: binding missing {binding_name}")
        else:
            enum_name, member_name = BINDING_ENUM_MEMBERS[key]
            if member_name in binding_enum_duplicates.get(enum_name, set()):
                issues.append(
                    f"abi-binding-constants: duplicate binding enum member {enum_name}.{member_name}"
                )
            enum_members = binding_enums.get(enum_name)
            if enum_members is None:
                issues.append(f"abi-binding-constants: binding missing enum {enum_name}")
            else:
                binding_value = enum_members.get(member_name)
                if binding_value is None:
                    issues.append(
                        f"abi-binding-constants: binding missing enum member {enum_name}.{member_name}"
                    )

        if binding_value is not None and binding_value != expected:
            issues.append(f"abi-binding-constants: binding {key}={binding_value} expected {expected}")
        if header_value is not None and binding_value is not None and header_value != binding_value:
            issues.append(
                f"abi-binding-constants: header/binding mismatch for {key}: {header_value}!={binding_value}"
            )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_binding_constants_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "include" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "bindings").mkdir(parents=True, exist_ok=True)
        (root / HEADER_REL).write_text(
            "\n".join(
                (
                    "#define ZIGUX_ABI_VERSION 1U",
                    "#define ZIGUX_STATUS_FLAG_ERROR 1U",
                    "#define ZIGUX_FACILITY_KERNEL 1U",
                    "#define ZIGUX_FACILITY_HELPERS 2U",
                    "#define ZIGUX_FACILITY_DRIVERS 3U",
                    "#define ZIGUX_PANIC_ABORT 0U",
                    "#define ZIGUX_PANIC_BUG 1U",
                    "#define ZIGUX_PANIC_WARN 2U",
                    "#define ZIGUX_ALLOC_CALLER_PROVIDED 0U",
                    "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
                    "#define ZIGUX_ALLOC_ARENA 2U",
                    "#define ZIGUX_UNSAFE_NONE 0U",
                    "#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U",
                    "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
                    "#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 6U",
                    "#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U",
                    "#define ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD 7U",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        bindings_path = root / BINDINGS_REL
        bindings_path.write_text(
            "\n".join(
                (
                    "pub const ABI_VERSION: u16 = 1;",
                    "pub const STATUS_FLAG_ERROR: u16 = 1;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;",
                    "pub const CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD: u32 = 7;",
                    "pub const Facility = enum(u16) {",
                    "    kernel = 1,",
                    "    helpers = 2,",
                    "    drivers = 3,",
                    "};",
                    "pub const PanicMode = enum(u8) {",
                    "    abort = 0,",
                    "    bug = 1,",
                    "    warn = 2,",
                    "};",
                    "pub const AllocatorMode = enum(u8) {",
                    "    caller_provided = 0,",
                    "    kernel_heap = 1,",
                    "    arena = 2,",
                    "};",
                    "pub const UnsafeScope = enum(u8) {",
                    "    none = 0,",
                    "    volatile_mmio = 1,",
                    "    raw_pointer_bridge = 2,",
                    "};",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_constants(root) == []

        header_path = root / HEADER_REL
        header_path.write_text(
            header_path.read_text(encoding="utf-8")
            + "#define ZIGUX_STATUS_FLAG_ERROR 1U\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert "abi-binding-constants: duplicate header definition for ZIGUX_STATUS_FLAG_ERROR" in issues
        header_path.write_text(
            header_path.read_text(encoding="utf-8").rsplit("#define ZIGUX_STATUS_FLAG_ERROR 1U\n", 1)[0]
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8")
            + "pub const STATUS_FLAG_ERROR: u16 = 1;\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert "abi-binding-constants: duplicate binding definition for STATUS_FLAG_ERROR" in issues
        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").rsplit("pub const STATUS_FLAG_ERROR: u16 = 1;\n", 1)[0]
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").replace("    kernel = 1,\n", "    kernel = 1,\n    kernel = 1,\n", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert "abi-binding-constants: duplicate binding enum member Facility.kernel" in issues
        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").replace("    kernel = 1,\n    kernel = 1,\n", "    kernel = 1,\n", 1),
            encoding="utf-8",
            newline="\n",
        )

        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").replace("    kernel = 1,\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert "abi-binding-constants: binding missing enum member Facility.kernel" in issues

        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").replace(
                "pub const STATUS_FLAG_ERROR: u16 = 1;",
                "pub const STATUS_FLAG_ERROR: u16 = 9;",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert "abi-binding-constants: binding status_flag_error=9 expected 1" in issues

        bindings_path.write_text(
            bindings_path.read_text(encoding="utf-8").replace(
                "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constants(root)
        assert (
            "abi-binding-constants: binding missing "
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED"
        ) in issues

    print(SELF_TEST_BANNER)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bounded Phase 3 ABI header constants stay mirrored by the Zig bindings."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_constants(ROOT)
    if issues:
        print(FAIL_BANNER)
        for issue in issues:
            print(issue)
        return 1

    print(PASS_BANNER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
