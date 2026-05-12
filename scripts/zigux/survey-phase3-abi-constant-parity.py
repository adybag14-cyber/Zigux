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
DEFAULT_LAYOUT_ASSERT = ROOT / "zigux" / "helpers" / "layout_assert.zig"
DEFAULT_DUMP = ROOT / "zigux" / "tests" / "phase3_abi_dump.zig"
DEFAULT_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi" / "phase3_abi_c_harness.c"
DEFAULT_EXPECTED = ROOT / "zigux" / "tests" / "fixtures" / "phase3_abi" / "expected.json"
PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT = 21

REQUIRED_ABI_VERSION = ("ZIGUX_ABI_VERSION", "ABI_VERSION", 1)

REQUIRED_CONSTANTS = (
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
REQUIRED_FAMILY_CONSTANT_MARKERS = (
    (
        "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
        "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
    ),
    (
        "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
        "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
    ),
    (
        "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED",
        "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED",
    ),
    (
        "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED",
        "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED",
    ),
)
REQUIRED_FAMILY_TYPE_MARKERS = (
    (
        "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {",
        "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {",
    ),
    (
        "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {",
        "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {",
    ),
    (
        "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {",
        "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView = extern struct {",
    ),
    (
        "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {",
        "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary = extern struct {",
    ),
)
REQUIRED_LAYOUT_ASSERT_HELPER_MARKERS = (
    "fn assertThreeU32FieldLayout(",
    "    try size(T, 12);",
    "    try alignment(T, 4);",
    "    try offset(T, first, 0);",
    "    try offset(T, second, 4);",
    "    try offset(T, third, 8);",
    "    fieldType(T, first, u32);",
    "    fieldType(T, second, u32);",
    "    fieldType(T, third, u32);",
)
REQUIRED_LAYOUT_ASSERT_FUNCTIONS = (
    (
        "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout",
        '        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView,',
        '        "ack_window",',
        '        "delivery_window",',
        '        "status",',
    ),
    (
        "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout",
        '        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary,',
        '        "applied",',
        '        "skipped",',
        '        "delivered",',
    ),
    (
        "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout",
        '        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView,',
        '        "budget",',
        '        "window",',
        '        "flags",',
    ),
    (
        "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout",
        '        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary,',
        '        "attempted",',
        '        "applied",',
        '        "skipped",',
    ),
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


def collect_duplicate_header_constants(path: Path) -> list[str]:
    seen: dict[str, list[int]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = HEADER_DEFINE_RE.match(line.strip())
        if match:
            seen.setdefault(match.group("name"), []).append(line_no)
    issues: list[str] = []
    for name, lines in seen.items():
        if len(lines) > 1:
            issues.append(f"{path}:duplicate_header_constant:{name}:{','.join(str(line) for line in lines)}")
    return issues


def collect_duplicate_binding_constants(path: Path) -> list[str]:
    seen: dict[str, list[int]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = BINDING_CONST_RE.match(line.strip())
        if match:
            seen.setdefault(match.group("name"), []).append(line_no)
    issues: list[str] = []
    for name, lines in seen.items():
        if len(lines) > 1:
            issues.append(f"{path}:duplicate_binding_constant:{name}:{','.join(str(line) for line in lines)}")
    return issues


def collect_duplicate_exact_markers(path: Path, markers: tuple[str, ...], issue_kind: str) -> list[str]:
    seen: dict[str, list[int]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped in markers:
            seen.setdefault(stripped, []).append(line_no)
    issues: list[str] = []
    for marker, lines in seen.items():
        if len(lines) > 1:
            issues.append(f"{path}:{issue_kind}:{marker}:{','.join(str(line) for line in lines)}")
    return issues


def source_contains_json_key(source: str, json_key: str) -> bool:
    raw_marker = f'"{json_key}":'
    escaped_marker = f'\\"{json_key}\\":'
    return raw_marker in source or escaped_marker in source


def validate_layout_assert(layout_assert_path: Path) -> list[str]:
    layout_assert_source = layout_assert_path.read_text(encoding="utf-8")
    issues: list[str] = []

    for marker in REQUIRED_LAYOUT_ASSERT_HELPER_MARKERS:
        if marker not in layout_assert_source:
            issues.append(f"{layout_assert_path}:missing_layout_assert_helper_marker:{marker}")

    for function_name, *call_markers in REQUIRED_LAYOUT_ASSERT_FUNCTIONS:
        signature = f"pub fn {function_name}() !void {{"
        if signature not in layout_assert_source:
            issues.append(f"{layout_assert_path}:missing_layout_assert_function:{function_name}")
        for marker in call_markers:
            if marker not in layout_assert_source:
                issues.append(f"{layout_assert_path}:missing_layout_assert_call_marker:{function_name}:{marker.strip()}")
        self_test_marker = f"    try {function_name}();"
        if self_test_marker not in layout_assert_source:
            issues.append(f"{layout_assert_path}:missing_layout_assert_self_test_call:{function_name}")

    return issues


def validate_constant_parity(
    header_path: Path,
    bindings_path: Path,
    layout_assert_path: Path,
    dump_path: Path,
    harness_path: Path,
    expected_path: Path,
) -> list[str]:
    issues = [
        *collect_duplicate_header_constants(header_path),
        *collect_duplicate_binding_constants(bindings_path),
        *collect_duplicate_exact_markers(
            header_path,
            tuple(header_marker for header_marker, _ in REQUIRED_FAMILY_TYPE_MARKERS),
            "duplicate_header_type_marker",
        ),
        *collect_duplicate_exact_markers(
            bindings_path,
            tuple(bindings_marker for _, bindings_marker in REQUIRED_FAMILY_TYPE_MARKERS),
            "duplicate_binding_type_marker",
        ),
    ]
    header_constants = parse_header_constants(header_path)
    binding_constants = parse_binding_constants(bindings_path)
    dump_source = dump_path.read_text(encoding="utf-8")
    harness_source = harness_path.read_text(encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    expected_constants = expected.get("constants")

    issues.extend(validate_layout_assert(layout_assert_path))

    if not isinstance(expected_constants, dict):
        issues.append(f"{expected_path}:missing_constants_object")
        expected_constants = {}

    header_version_name, binding_version_name, expected_version = REQUIRED_ABI_VERSION
    header_version = header_constants.get(header_version_name)
    if header_version is None:
        issues.append(f"{header_path}:missing_header_constant:{header_version_name}")
    elif header_version != expected_version:
        issues.append(f"{header_path}:wrong_header_value:{header_version_name}:{header_version}")

    binding_version = binding_constants.get(binding_version_name)
    if binding_version is None:
        issues.append(f"{bindings_path}:missing_binding_constant:{binding_version_name}")
    elif binding_version != expected_version:
        issues.append(f"{bindings_path}:wrong_binding_value:{binding_version_name}:{binding_version}")

    if not source_contains_json_key(dump_source, "abi_version"):
        issues.append(f"{dump_path}:missing_dump_key:abi_version")
    if not source_contains_json_key(harness_source, "abi_version"):
        issues.append(f"{harness_path}:missing_harness_key:abi_version")

    fixture_version = expected.get("abi_version")
    if fixture_version is None:
        issues.append(f"{expected_path}:missing_expected_key:abi_version")
    elif fixture_version != expected_version:
        issues.append(f"{expected_path}:wrong_expected_value:abi_version:{fixture_version}")

    for header_name, binding_name, json_key, expected_value in REQUIRED_CONSTANTS:
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

        if not source_contains_json_key(dump_source, json_key):
            issues.append(f"{dump_path}:missing_dump_key:{json_key}")
        if not source_contains_json_key(harness_source, json_key):
            issues.append(f"{harness_path}:missing_harness_key:{json_key}")

        fixture_value = expected_constants.get(json_key)
        if fixture_value is None:
            issues.append(f"{expected_path}:missing_expected_key:{json_key}")
        elif fixture_value != expected_value:
            issues.append(f"{expected_path}:wrong_expected_value:{json_key}:{fixture_value}")

    header_source = header_path.read_text(encoding="utf-8")
    bindings_source = bindings_path.read_text(encoding="utf-8")
    for header_marker, binding_marker in REQUIRED_FAMILY_CONSTANT_MARKERS:
        if header_marker not in header_source:
            issues.append(f"{header_path}:missing_header_family_constant:{header_marker}")
        if binding_marker not in binding_constants:
            issues.append(f"{bindings_path}:missing_binding_family_constant:{binding_marker}")

    for header_marker, bindings_marker in REQUIRED_FAMILY_TYPE_MARKERS:
        if header_marker not in header_source:
            issues.append(f"{header_path}:missing_header_type_marker:{header_marker}")
        if bindings_marker not in bindings_source:
            issues.append(f"{bindings_path}:missing_binding_type_marker:{bindings_marker}")

    return issues


def _layout_assert_text() -> str:
    helper_block = "\n".join(REQUIRED_LAYOUT_ASSERT_HELPER_MARKERS) + "\n"
    function_blocks = []
    for function_name, *call_markers in REQUIRED_LAYOUT_ASSERT_FUNCTIONS:
        block_lines = [f"pub fn {function_name}() !void {{"] + call_markers + ["}"]
        function_blocks.append("\n".join(block_lines))
    self_test_lines = ['test "phase3 layout assertions cover canonical bindings" {']
    self_test_lines.extend(f"    try {function_name}();" for function_name, *_ in REQUIRED_LAYOUT_ASSERT_FUNCTIONS)
    self_test_lines.append("}")
    return helper_block + "\n".join(function_blocks) + "\n" + "\n".join(self_test_lines) + "\n"


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase3_abi_constant_parity_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        header = root / "include" / "zigux" / "abi.h"
        bindings = root / "zigux" / "bindings" / "abi.zig"
        layout_assert = root / "zigux" / "helpers" / "layout_assert.zig"
        dump = root / "zigux" / "tests" / "phase3_abi_dump.zig"
        harness = root / "zigux" / "tests" / "fixtures" / "phase3_abi" / "phase3_abi_c_harness.c"
        expected = root / "zigux" / "tests" / "fixtures" / "phase3_abi" / "expected.json"

        for path in (header.parent, bindings.parent, layout_assert.parent, dump.parent, harness.parent, expected.parent):
            path.mkdir(parents=True, exist_ok=True)

        def reset_all() -> None:
            header.write_text(
                "\n".join(
                    [f"#define {REQUIRED_ABI_VERSION[0]} {REQUIRED_ABI_VERSION[2]}U"]
                    + [f"#define {header_name} {value}U" for header_name, _, _, value in REQUIRED_CONSTANTS]
                    + [f"#define {header_name} 1U" for header_name, _ in REQUIRED_FAMILY_CONSTANT_MARKERS]
                    + [header_marker for header_marker, _ in REQUIRED_FAMILY_TYPE_MARKERS]
                ) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            bindings.write_text(
                "\n".join(
                    [f"pub const {REQUIRED_ABI_VERSION[1]}: u16 = {REQUIRED_ABI_VERSION[2]};"]
                    + [*(f"pub const {binding_name}: u32 = {value};" for _, binding_name, _, value in REQUIRED_CONSTANTS)]
                    + [f"pub const {binding_name}: u32 = 1;" for _, binding_name in REQUIRED_FAMILY_CONSTANT_MARKERS]
                    + [bindings_marker for _, bindings_marker in REQUIRED_FAMILY_TYPE_MARKERS]
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
            layout_assert.write_text(_layout_assert_text(), encoding="utf-8", newline="\n")
            dump.write_text(
                '\n'.join(['// "abi_version":'] + [f'// "{json_key}":' for _, _, json_key, _ in REQUIRED_CONSTANTS]) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            harness.write_text(
                '\n'.join(['/* "abi_version": */'] + [f'/* "{json_key}": */' for _, _, json_key, _ in REQUIRED_CONSTANTS]) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            expected.write_text(
                json.dumps(
                    {
                        "abi_version": REQUIRED_ABI_VERSION[2],
                        "constants": {json_key: value for _, _, json_key, value in REQUIRED_CONSTANTS},
                    }
                ),
                encoding="utf-8",
                newline="\n",
            )

        reset_all()
        assert validate_constant_parity(header, bindings, layout_assert, dump, harness, expected) == []
        case_count += 1

        dump.write_text(
            '\n'.join(['// \\"abi_version\\":'] + [f'// \\"{json_key}\\":' for _, _, json_key, _ in REQUIRED_CONSTANTS]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        harness.write_text(
            '\n'.join(['/* \\"abi_version\\": */'] + [f'/* \\"{json_key}\\": */' for _, _, json_key, _ in REQUIRED_CONSTANTS]) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_constant_parity(header, bindings, layout_assert, dump, harness, expected) == []
        case_count += 1

        reset_all()
        bindings.write_text("pub const STATUS_FLAG_ERROR: u16 = 1;\n", encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:missing_binding_constant:FACILITY_KERNEL" in issues
        assert f"{bindings}:missing_binding_constant:{REQUIRED_ABI_VERSION[1]}" in issues
        assert f"{bindings}:missing_binding_family_constant:{REQUIRED_FAMILY_CONSTANT_MARKERS[0][1]}" in issues
        case_count += 1

        reset_all()
        dump.write_text('// "facility_kernel":\n', encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{dump}:missing_dump_key:abi_version" in issues
        assert f"{dump}:missing_dump_key:status_flag_error" in issues
        case_count += 1

        reset_all()
        harness.write_text('/* "facility_kernel": */\n', encoding="utf-8", newline="\n")
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{harness}:missing_harness_key:abi_version" in issues
        assert f"{harness}:missing_harness_key:status_flag_error" in issues
        case_count += 1

        reset_all()
        header.write_text(
            "\n".join(
                [f"#define {REQUIRED_ABI_VERSION[0]} {REQUIRED_ABI_VERSION[2] + 1}U"]
                + [f"#define {header_name} {value}U" for header_name, _, _, value in REQUIRED_CONSTANTS]
                + [f"#define {header_name} 1U" for header_name, _ in REQUIRED_FAMILY_CONSTANT_MARKERS]
                + [header_marker for header_marker, _ in REQUIRED_FAMILY_TYPE_MARKERS]
            ) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:wrong_header_value:{REQUIRED_ABI_VERSION[0]}:2" in issues
        case_count += 1

        reset_all()
        expected.write_text(
            json.dumps({"abi_version": REQUIRED_ABI_VERSION[2] + 1, "constants": {"facility_kernel": 7}}),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{expected}:wrong_expected_value:abi_version:2" in issues
        assert f"{expected}:wrong_expected_value:facility_kernel:7" in issues
        assert f"{expected}:missing_expected_key:status_flag_error" in issues
        case_count += 1

        reset_all()
        header.write_text(
            "\n".join(
                [
                    f"#define {REQUIRED_CONSTANTS[0][0]} {REQUIRED_CONSTANTS[0][3]}U",
                    f"#define {REQUIRED_CONSTANTS[0][0]} {REQUIRED_CONSTANTS[0][3]}U",
                    *[
                        f"#define {header_name} {value}U"
                        for header_name, _, _, value in REQUIRED_CONSTANTS[1:]
                    ],
                    f"#define {REQUIRED_ABI_VERSION[0]} {REQUIRED_ABI_VERSION[2]}U",
                    *[f"#define {header_name} 1U" for header_name, _ in REQUIRED_FAMILY_CONSTANT_MARKERS],
                    *[header_marker for header_marker, _ in REQUIRED_FAMILY_TYPE_MARKERS],
                ]
            ) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:duplicate_header_constant:{REQUIRED_CONSTANTS[0][0]}:1,2" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            "\n".join(
                [
                    f"pub const {REQUIRED_CONSTANTS[0][1]}: u32 = {REQUIRED_CONSTANTS[0][3]};",
                    f"pub const {REQUIRED_CONSTANTS[0][1]}: u32 = {REQUIRED_CONSTANTS[0][3]};",
                    f"pub const {REQUIRED_ABI_VERSION[1]}: u16 = {REQUIRED_ABI_VERSION[2]};",
                    *[
                        f"pub const {binding_name}: u32 = {value};"
                        for _, binding_name, _, value in REQUIRED_CONSTANTS[1:]
                    ],
                    *[f"pub const {binding_name}: u32 = 1;" for _, binding_name in REQUIRED_FAMILY_CONSTANT_MARKERS],
                    *[bindings_marker for _, bindings_marker in REQUIRED_FAMILY_TYPE_MARKERS],
                ]
            ) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:duplicate_binding_constant:{REQUIRED_CONSTANTS[0][1]}:1,2" in issues
        case_count += 1

        reset_all()
        header.write_text(
            header.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[0][0] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:missing_header_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[0][0]}" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            bindings.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[1][1] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:missing_binding_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[1][1]}" in issues
        case_count += 1

        reset_all()
        header.write_text(
            header.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[2][0] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:missing_header_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[2][0]}" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            bindings.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[3][1] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:missing_binding_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[3][1]}" in issues
        case_count += 1

        reset_all()
        header.write_text(
            header.read_text(encoding="utf-8").replace(
                f"#define {REQUIRED_FAMILY_CONSTANT_MARKERS[3][0]} 1U\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:missing_header_family_constant:{REQUIRED_FAMILY_CONSTANT_MARKERS[3][0]}" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            bindings.read_text(encoding="utf-8").replace(
                f"pub const {REQUIRED_FAMILY_CONSTANT_MARKERS[2][1]}: u32 = 1;\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:missing_binding_family_constant:{REQUIRED_FAMILY_CONSTANT_MARKERS[2][1]}" in issues
        case_count += 1

        reset_all()
        header.write_text(
            header.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[0][0] + "\n",
                REQUIRED_FAMILY_TYPE_MARKERS[0][0] + "\n" + REQUIRED_FAMILY_TYPE_MARKERS[0][0] + "\n",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{header}:duplicate_header_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[0][0]}:19,20" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            bindings.read_text(encoding="utf-8").replace(
                REQUIRED_FAMILY_TYPE_MARKERS[0][1] + "\n",
                REQUIRED_FAMILY_TYPE_MARKERS[0][1] + "\n" + REQUIRED_FAMILY_TYPE_MARKERS[0][1] + "\n",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:duplicate_binding_type_marker:{REQUIRED_FAMILY_TYPE_MARKERS[0][1]}:19,20" in issues
        case_count += 1

        reset_all()
        bindings.write_text(
            bindings.read_text(encoding="utf-8").replace(
                f"pub const {REQUIRED_ABI_VERSION[1]}: u16 = {REQUIRED_ABI_VERSION[2]};\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{bindings}:missing_binding_constant:{REQUIRED_ABI_VERSION[1]}" in issues
        case_count += 1

        reset_all()
        expected.write_text(
            json.dumps({"constants": {json_key: value for _, _, json_key, value in REQUIRED_CONSTANTS}}),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        assert f"{expected}:missing_expected_key:abi_version" in issues
        case_count += 1

        reset_all()
        layout_assert.write_text(
            layout_assert.read_text(encoding="utf-8").replace(
                '        "flags",\n',
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        missing_call_issue = (
            f'{layout_assert}:missing_layout_assert_call_marker:'
            "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout:\"flags\","
        )
        assert missing_call_issue in issues
        case_count += 1

        reset_all()
        layout_assert.write_text(
            layout_assert.read_text(encoding="utf-8").replace(
                "    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();\n",
                "",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_constant_parity(header, bindings, layout_assert, dump, harness, expected)
        missing_self_test_issue = (
            f"{layout_assert}:missing_layout_assert_self_test_call:"
            "assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout"
        )
        assert missing_self_test_issue in issues
        case_count += 1

    print("PHASE3_ABI_CONSTANT_PARITY_SELF_TEST=pass")
    print(f"PHASE3_ABI_CONSTANT_PARITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Survey shipped Phase 3 ABI constant parity across the C header, curated Zig bindings, layout-assert helpers, dump replay, C harness, and committed expected fixture."
    )
    parser.add_argument("--header-path", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--bindings-path", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--layout-assert-path", type=Path, default=DEFAULT_LAYOUT_ASSERT)
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
        args.layout_assert_path,
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
