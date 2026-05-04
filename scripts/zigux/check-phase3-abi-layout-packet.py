#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

from validate_phase3_core import PHASE3_SHARED_RBTREE_RECORD_MARKERS


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PHASE3_ABI_REL = "zigux/tests/phase3_abi.zig"
PHASE3_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
PHASE3_ABI_C_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"

CANONICAL_LAYOUTS = (
    ("zigux_boundary_header", "BoundaryHeader", "assertBoundaryHeaderLayout", "abi"),
    ("zigux_export_status", "ExportStatus", "assertExportStatusLayout", "abi"),
    ("zigux_mmio_range", "MmioRange", "assertMmioRangeLayout", "abi"),
    ("zigux_interop_policy", "InteropPolicy", "assertInteropPolicyLayout", "abi"),
    ("zigux_bitmap_view", "BitmapView", "assertBitmapViewLayout", "abi"),
    ("zigux_cpumask_view", "CpuMaskView", "assertCpumaskViewLayout", "abi"),
    ("zigux_list_head_ref", "ListHeadRef", "assertListHeadRefLayout", "abi"),
    ("zigux_list_view", "ListView", "assertListViewLayout", "abi"),
    ("zigux_list_summary", "ListSummary", "assertListSummaryLayout", "abi"),
    ("zigux_hlist_head_ref", "HListHeadRef", "assertHlistHeadRefLayout", "abi"),
    ("zigux_hlist_node_ref", "HListNodeRef", "assertHlistNodeRefLayout", "abi"),
    ("zigux_hlist_view", "HListView", "assertHlistViewLayout", "abi"),
    ("zigux_hlist_summary", "HListSummary", "assertHlistSummaryLayout", "abi"),
    ("zigux_rbtree_root_view", "RootView", "assertRbtreeRootViewLayout", "rbtree"),
)

REQUIRED_CONSTANTS = (
    ("list_flag_empty", "abi", "LIST_FLAG_EMPTY", "ZIGUX_LIST_FLAG_EMPTY"),
    ("list_flag_singular", "abi", "LIST_FLAG_SINGULAR", "ZIGUX_LIST_FLAG_SINGULAR"),
    ("list_flag_circular", "abi", "LIST_FLAG_CIRCULAR", "ZIGUX_LIST_FLAG_CIRCULAR"),
    ("list_flag_truncated", "abi", "LIST_FLAG_TRUNCATED", "ZIGUX_LIST_FLAG_TRUNCATED"),
    ("hlist_flag_empty", "abi", "HLIST_FLAG_EMPTY", "ZIGUX_HLIST_FLAG_EMPTY"),
    ("hlist_flag_singular", "abi", "HLIST_FLAG_SINGULAR", "ZIGUX_HLIST_FLAG_SINGULAR"),
    ("hlist_flag_terminated", "abi", "HLIST_FLAG_TERMINATED", "ZIGUX_HLIST_FLAG_TERMINATED"),
    ("hlist_flag_truncated", "abi", "HLIST_FLAG_TRUNCATED", "ZIGUX_HLIST_FLAG_TRUNCATED"),
    ("minor_alloc_flag_truncated", "abi", "MINOR_ALLOC_FLAG_TRUNCATED", "ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED"),
    ("minor_alloc_flag_found", "abi", "MINOR_ALLOC_FLAG_FOUND", "ZIGUX_MINOR_ALLOC_FLAG_FOUND"),
    ("minor_alloc_flag_exhausted", "abi", "MINOR_ALLOC_FLAG_EXHAUSTED", "ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED"),
    ("root_flag_empty", "rbtree", "ROOT_FLAG_EMPTY", "ZIGUX_RBTREE_ROOT_FLAG_EMPTY"),
    ("root_flag_cached", "rbtree", "ROOT_FLAG_CACHED", "ZIGUX_RBTREE_ROOT_FLAG_CACHED"),
    ("root_flag_leftmost_valid", "rbtree", "ROOT_FLAG_LEFTMOST_VALID", "ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID"),
)

SELF_TEST_EXTRA_CONSTANT_KEYS = (
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
)

SHARED_RBTREE_SAMPLE_MARKER = "PHASE3_SHARED_RBTREE_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root"
SHARED_RBTREE_PHASE3_MARKERS = {
    "rbtree_empty_root": PHASE3_SHARED_RBTREE_RECORD_MARKERS[:2],
    "rbtree_cached_leftmost_root": PHASE3_SHARED_RBTREE_RECORD_MARKERS[2:4],
    "rbtree_uncached_root": PHASE3_SHARED_RBTREE_RECORD_MARKERS[4:6],
}
SHARED_RBTREE_SAMPLE_RECORDS = {
    "rbtree_empty_root": {
        "phase3_value_snippet": "try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_EMPTY), empty_root.flags);",
        "dump_snippet": '"rbtree_empty_root"',
        "dump_value_snippet": 'try writer.print("{d}", .{rbtree.ROOT_FLAG_EMPTY});\n    try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":");',
        "harness_snippet": '"rbtree_empty_root"',
        "harness_value_snippet": 'fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_EMPTY);\n    fputs(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":", stdout);',
        "record": {
            "root_addr": 0,
            "leftmost_addr": 0,
            "flags": 1,
            "reserved": 0,
        },
    },
    "rbtree_cached_leftmost_root": {
        "phase3_value_snippet": "try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);",
        "phase3_presence_snippets": (
            "try std.testing.expect(rbtree.isValid(cached_root));",
            "try std.testing.expect(!rbtree.isEmpty(cached_root));",
            "try std.testing.expect(rbtree.isCached(cached_root));",
            "try std.testing.expect(rbtree.hasLeftmost(cached_root));",
            "try std.testing.expect(rbtree.isCanonical(cached_root));",
        ),
        "dump_snippet": '"rbtree_cached_leftmost_root"',
        "harness_snippet": '"rbtree_cached_leftmost_root"',
        "record": {
            "root_addr": 0x2000,
            "leftmost_addr": 0x1800,
            "flags": 0x6,
            "reserved": 0,
        },
    },
    "rbtree_uncached_root": {
        "phase3_value_snippet": "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
        "phase3_presence_snippets": (
            "try std.testing.expect(rbtree.isValid(uncached_root));",
            "try std.testing.expect(!rbtree.isEmpty(uncached_root));",
            "try std.testing.expect(!rbtree.isCached(uncached_root));",
            "try std.testing.expect(!rbtree.hasLeftmost(uncached_root));",
            "try std.testing.expect(rbtree.isCanonical(uncached_root));",
        ),
        "dump_snippet": '"rbtree_uncached_root"',
        "harness_snippet": '"rbtree_uncached_root"',
        "record": {
            "root_addr": 0x2400,
            "leftmost_addr": 0,
            "flags": 0,
            "reserved": 0,
        },
    },
}

DUMP_CONSTANT_PACKET_START = 'try writer.writeAll(",\\\"constants\\\":{\\\"facility_kernel\\\":");'
DUMP_CONSTANT_PACKET_END = 'try writer.writeAll("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":");'
HARNESS_CONSTANT_PACKET_START = 'fputs(",\\\"constants\\\":{\\\"facility_kernel\\\":", stdout);'
HARNESS_CONSTANT_PACKET_END = 'fputs("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":", stdout);'
DUMP_UNCACHED_RECORD_TRAILER = 'try writer.writeAll(",\\\"leftmost_addr\\\":0,\\\"flags\\\":0,\\\"reserved\\\":0}},\\\"structs\\\":{");'
HARNESS_UNCACHED_RECORD_TRAILER = 'fputs(",\\\"leftmost_addr\\\":0,\\\"flags\\\":0,\\\"reserved\\\":0}},\\\"structs\\\":{", stdout);'
CONSTANT_PACKET_KEY_RE = re.compile(r'\\\"([a-z0-9_]+)\\\":')


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _extract_constant_packet_keys(
    text: str,
    *,
    start_marker: str,
    end_marker: str,
    rel: str,
) -> tuple[list[str], list[str]]:
    start = text.find(start_marker)
    if start == -1:
        return [], [f"missing_constant_packet_start:{rel}"]

    end = text.find(end_marker, start)
    if end == -1:
        return [], [f"missing_constant_packet_end:{rel}"]

    keys: list[str] = []
    seen: set[str] = set()
    for key in CONSTANT_PACKET_KEY_RE.findall(text[start:end]):
        if key == "constants" or key in seen:
            continue
        seen.add(key)
        keys.append(key)

    if not keys:
        return [], [f"missing_constant_packet_keys:{rel}"]
    return keys, []


def _append_constant_set_issues(
    issues: list[str],
    baseline_keys: list[str],
    actual_keys: list[str],
    *,
    baseline_rel: str,
    actual_rel: str,
) -> None:
    if len(actual_keys) != len(baseline_keys):
        issues.append(
            f"constant_count_mismatch:{actual_rel}:{len(actual_keys)}:{baseline_rel}:{len(baseline_keys)}"
        )

    missing = sorted(set(baseline_keys).difference(actual_keys))
    unexpected = sorted(set(actual_keys).difference(baseline_keys))
    if missing or unexpected:
        issues.append(
            "constant_set_mismatch:"
            f"{actual_rel}:{baseline_rel}:"
            f"missing={','.join(missing) if missing else '-'}:"
            f"unexpected={','.join(unexpected) if unexpected else '-'}"
        )


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    expected_text = _read_text(root, EXPECTED_REL, issues)
    layout_assert_text = _read_text(root, LAYOUT_ASSERT_REL, issues)
    phase3_abi_text = _read_text(root, PHASE3_ABI_REL, issues)
    phase3_abi_dump_text = _read_text(root, PHASE3_ABI_DUMP_REL, issues)
    c_harness_text = _read_text(root, PHASE3_ABI_C_HARNESS_REL, issues)

    expected_structs: dict[str, object] = {}
    expected_constants: dict[str, object] = {}
    expected_records: dict[str, object] = {}
    saw_expected_records = False
    if expected_text:
        try:
            parsed = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            expected_structs = parsed.get("structs", {})
            expected_constants = parsed.get("constants", {})
            saw_expected_records = "records" in parsed
            expected_records = parsed.get("records", {})
            if not isinstance(expected_structs, dict):
                issues.append("invalid_expected_json:structs-not-object")
                expected_structs = {}
            if not isinstance(expected_constants, dict):
                issues.append("invalid_expected_json:constants-not-object")
                expected_constants = {}
            if not isinstance(expected_records, dict):
                issues.append("invalid_expected_json:records-not-object")
                expected_records = {}

    if expected_structs and len(expected_structs) != len(CANONICAL_LAYOUTS):
        issues.append(
            "unexpected_expected_struct_count:"
            f"{len(expected_structs)}!= {len(CANONICAL_LAYOUTS)}"
        )

    for json_name, zig_name, assert_name, module_name in CANONICAL_LAYOUTS:
        if expected_structs and json_name not in expected_structs:
            issues.append(f"missing_expected_struct:{json_name}")

        if layout_assert_text and f"pub fn {assert_name}() void" not in layout_assert_text:
            issues.append(f"missing_layout_assert_fn:{assert_name}")
        if phase3_abi_text and f"layout_assert.{assert_name}();" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_layout_call:{assert_name}")
        if phase3_abi_dump_text and f'writeStructLayout(writer, "{json_name}", {module_name}.{zig_name},' not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_layout:{json_name}")
        if c_harness_text and f'{{"{json_name}", sizeof(struct {json_name}), _Alignof(struct {json_name})' not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_layout:{json_name}")

    for json_name, module_name, zig_name, c_name in REQUIRED_CONSTANTS:
        if expected_constants and json_name not in expected_constants:
            issues.append(f"missing_expected_constant:{json_name}")
        if phase3_abi_text and f"{module_name}.{zig_name}" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_constant:{zig_name}")
        if phase3_abi_dump_text and f"{module_name}.{zig_name}" not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_constant:{zig_name}")
        if c_harness_text and c_name not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_constant:{c_name}")

    if expected_constants and phase3_abi_dump_text:
        dump_constant_keys, dump_constant_issues = _extract_constant_packet_keys(
            phase3_abi_dump_text,
            start_marker=DUMP_CONSTANT_PACKET_START,
            end_marker=DUMP_CONSTANT_PACKET_END,
            rel=PHASE3_ABI_DUMP_REL,
        )
        issues.extend(dump_constant_issues)
        if dump_constant_keys:
            _append_constant_set_issues(
                issues,
                list(expected_constants.keys()),
                dump_constant_keys,
                baseline_rel=EXPECTED_REL,
                actual_rel=PHASE3_ABI_DUMP_REL,
            )
            if c_harness_text:
                harness_constant_keys, harness_constant_issues = _extract_constant_packet_keys(
                    c_harness_text,
                    start_marker=HARNESS_CONSTANT_PACKET_START,
                    end_marker=HARNESS_CONSTANT_PACKET_END,
                    rel=PHASE3_ABI_C_HARNESS_REL,
                )
                issues.extend(harness_constant_issues)
                if harness_constant_keys:
                    _append_constant_set_issues(
                        issues,
                        list(expected_constants.keys()),
                        harness_constant_keys,
                        baseline_rel=EXPECTED_REL,
                        actual_rel=PHASE3_ABI_C_HARNESS_REL,
                    )
                    _append_constant_set_issues(
                        issues,
                        dump_constant_keys,
                        harness_constant_keys,
                        baseline_rel=PHASE3_ABI_DUMP_REL,
                        actual_rel=PHASE3_ABI_C_HARNESS_REL,
                    )

    if phase3_abi_text and SHARED_RBTREE_SAMPLE_MARKER not in phase3_abi_text:
        issues.append("missing_phase3_abi_rbtree_sample_marker")

    for record_name, record_contract in SHARED_RBTREE_SAMPLE_RECORDS.items():
        if saw_expected_records and record_name not in expected_records:
            issues.append(f"missing_expected_record:{record_name}")
        elif saw_expected_records and expected_records.get(record_name) != record_contract["record"]:
            issues.append(f"unexpected_expected_record:{record_name}")

        if phase3_abi_text:
            phase3_markers = SHARED_RBTREE_PHASE3_MARKERS[record_name]
            if phase3_markers[0] not in phase3_abi_text:
                issues.append(f"missing_phase3_abi_record:{record_name}")
            if record_contract["phase3_value_snippet"] not in phase3_abi_text:
                issues.append(f"missing_phase3_abi_record_value:{record_name}")
            for snippet in record_contract.get("phase3_presence_snippets", ()):
                if snippet not in phase3_abi_text:
                    issues.append(f"missing_phase3_abi_record_presence:{record_name}:{snippet}")
            if phase3_markers[1] not in phase3_abi_text:
                issues.append(f"missing_phase3_abi_record_presence:{record_name}:{phase3_markers[1]}")

        if phase3_abi_dump_text and record_contract["dump_snippet"] not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_record:{record_name}")
        if phase3_abi_dump_text and "dump_value_snippet" in record_contract and record_contract["dump_value_snippet"] not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_record_value:{record_name}")

        if c_harness_text and record_contract["harness_snippet"] not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_record:{record_name}")
        if c_harness_text and "harness_value_snippet" in record_contract and record_contract["harness_value_snippet"] not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_record_value:{record_name}")

    if phase3_abi_text and "try std.testing.expect(rbtree.isEmpty(empty_root));" not in phase3_abi_text:
        issues.append("missing_phase3_abi_empty_rbtree_sample_flags")
    if phase3_abi_text and "try std.testing.expect(!rbtree.hasRoot(empty_root));" not in phase3_abi_text:
        issues.append("missing_phase3_abi_empty_rbtree_sample_root_check")
    if phase3_abi_text and ".flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID," not in phase3_abi_text:
        issues.append("missing_phase3_abi_rbtree_sample_flags")
    if phase3_abi_text and "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);" not in phase3_abi_text:
        issues.append("missing_phase3_abi_uncached_rbtree_sample_flags")

    if phase3_abi_dump_text and ".{rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID}" not in phase3_abi_dump_text:
        issues.append("missing_phase3_abi_dump_rbtree_sample_flags")
    if phase3_abi_dump_text and DUMP_UNCACHED_RECORD_TRAILER not in phase3_abi_dump_text:
        issues.append("missing_phase3_abi_dump_uncached_rbtree_sample_flags")

    if c_harness_text and "ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID" not in c_harness_text:
        issues.append("missing_phase3_abi_c_harness_rbtree_sample_flags")
    if c_harness_text and HARNESS_UNCACHED_RECORD_TRAILER not in c_harness_text:
        issues.append("missing_phase3_abi_c_harness_uncached_rbtree_sample_flags")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_layout_packet_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "zigux" / "tests" / "fixtures" / "phase3_abi").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "helpers").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests").mkdir(parents=True, exist_ok=True)

        expected = {
            "abi_version": 1,
            "constants": {
                json_name: index + 1
                for index, json_name in enumerate(
                    SELF_TEST_EXTRA_CONSTANT_KEYS
                    + tuple(json_name for json_name, _, _, _ in REQUIRED_CONSTANTS)
                )
            },
            "records": {
                record_name: dict(contract["record"])
                for record_name, contract in SHARED_RBTREE_SAMPLE_RECORDS.items()
            },
            "structs": {
                json_name: {"size": 0, "align": 0, "offsets": {}}
                for json_name, _, _, _ in CANONICAL_LAYOUTS
            },
        }
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")
        (root / LAYOUT_ASSERT_REL).write_text(
            "\n".join(f"pub fn {assert_name}() void {{}}" for _, _, assert_name, _ in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_REL).write_text(
            "\n".join(
                [*(f"layout_assert.{assert_name}();" for _, _, assert_name, _ in CANONICAL_LAYOUTS)]
                + [*(f"const _ = {module_name}.{zig_name};" for _, module_name, zig_name, _ in REQUIRED_CONSTANTS)]
                + [
                    f"// {SHARED_RBTREE_SAMPLE_MARKER}",
                    "const empty_root = rbtree.empty();",
                    "try std.testing.expectEqual(@as(usize, 0), empty_root.root_addr);",
                    "try std.testing.expectEqual(@as(usize, 0), empty_root.leftmost_addr);",
                    "try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_EMPTY), empty_root.flags);",
                    "try std.testing.expectEqual(@as(u32, 0), empty_root.reserved);",
                    "try std.testing.expect(rbtree.isValid(empty_root));",
                    "try std.testing.expect(rbtree.isEmpty(empty_root));",
                    "try std.testing.expect(!rbtree.isCached(empty_root));",
                    "try std.testing.expect(!rbtree.hasLeftmost(empty_root));",
                    "try std.testing.expect(!rbtree.hasRoot(empty_root));",
                    "try std.testing.expect(rbtree.isCanonical(empty_root));",
                    "const cached_root: rbtree.RootView = .{",
                    "    .root_addr = 0x2000,",
                    "    .leftmost_addr = 0x1800,",
                    "    .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,",
                    "    .reserved = 0,",
                    "};",
                    "try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);",
                    "try std.testing.expect(rbtree.isValid(cached_root));",
                    "try std.testing.expect(!rbtree.isEmpty(cached_root));",
                    "try std.testing.expect(rbtree.isCached(cached_root));",
                    "try std.testing.expect(rbtree.hasLeftmost(cached_root));",
                    "try std.testing.expect(rbtree.hasRoot(cached_root));",
                    "try std.testing.expect(rbtree.isCanonical(cached_root));",
                    "const uncached_root: rbtree.RootView = .{",
                    "    .root_addr = 0x2400,",
                    "    .leftmost_addr = 0,",
                    "    .flags = 0,",
                    "    .reserved = 0,",
                    "};",
                    "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
                    "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);",
                    "try std.testing.expect(rbtree.isValid(uncached_root));",
                    "try std.testing.expect(!rbtree.isEmpty(uncached_root));",
                    "try std.testing.expect(!rbtree.isCached(uncached_root));",
                    "try std.testing.expect(!rbtree.hasLeftmost(uncached_root));",
                    "try std.testing.expect(rbtree.hasRoot(uncached_root));",
                    "try std.testing.expect(rbtree.isCanonical(uncached_root));",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_DUMP_REL).write_text(
            "\n".join(
                [
                    DUMP_CONSTANT_PACKET_START,
                    *[
                        f'try writer.writeAll(",\\\"{json_name}\\\":");'
                        for json_name in SELF_TEST_EXTRA_CONSTANT_KEYS[1:]
                    ],
                    *[
                        f'try writer.writeAll(",\\\"{json_name}\\\":");'
                        for json_name, _, _, _ in REQUIRED_CONSTANTS
                    ],
                    DUMP_CONSTANT_PACKET_END,
                    'try writer.print("{d}", .{0});',
                    'try writer.writeAll(",\\\"leftmost_addr\\\":0,\\\"flags\\\":");',
                    SHARED_RBTREE_SAMPLE_RECORDS["rbtree_empty_root"]["dump_value_snippet"],
                ]
                + [*(f'writeStructLayout(writer, "{json_name}", {module_name}.{zig_name}, true);' for json_name, zig_name, _, module_name in CANONICAL_LAYOUTS[:-1])]
                + [f'writeStructLayout(writer, "{CANONICAL_LAYOUTS[-1][0]}", {CANONICAL_LAYOUTS[-1][3]}.{CANONICAL_LAYOUTS[-1][1]}, false);']
                + [*(f"const _ = {module_name}.{zig_name};" for _, module_name, zig_name, _ in REQUIRED_CONSTANTS)]
                + [
                    'const _ = "rbtree_empty_root";',
                    'const _ = "rbtree_cached_leftmost_root";',
                    'const _ = "rbtree_uncached_root";',
                    'try writer.print("{d}", .{rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID});',
                    DUMP_UNCACHED_RECORD_TRAILER,
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_C_HARNESS_REL).write_text(
            "\n".join(
                [
                    HARNESS_CONSTANT_PACKET_START,
                    *[
                        f'fputs(",\\\"{json_name}\\\":", stdout);'
                        for json_name in SELF_TEST_EXTRA_CONSTANT_KEYS[1:]
                    ],
                    *[
                        f'fputs(",\\\"{json_name}\\\":", stdout);'
                        for json_name, _, _, _ in REQUIRED_CONSTANTS
                    ],
                    HARNESS_CONSTANT_PACKET_END,
                    'fprintf(stdout, "%lu", 0UL);',
                    'fputs(",\\\"leftmost_addr\\\":0,\\\"flags\\\":", stdout);',
                    SHARED_RBTREE_SAMPLE_RECORDS["rbtree_empty_root"]["harness_value_snippet"],
                ]
                + [*(f'{{"{json_name}", sizeof(struct {json_name}), _Alignof(struct {json_name}), 0, 0}},' for json_name, _, _, _ in CANONICAL_LAYOUTS)]
                + [*(c_name for _, _, _, c_name in REQUIRED_CONSTANTS)]
                + [
                    '"rbtree_empty_root"',
                    '"rbtree_cached_leftmost_root"',
                    '"rbtree_uncached_root"',
                    "ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID",
                    HARNESS_UNCACHED_RECORD_TRAILER,
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        assert validate(root) == []

        reduced_expected = dict(expected)
        reduced_expected["records"] = {
            "rbtree_empty_root": dict(
                SHARED_RBTREE_SAMPLE_RECORDS["rbtree_empty_root"]["record"]
            ),
            "rbtree_cached_leftmost_root": dict(
                SHARED_RBTREE_SAMPLE_RECORDS["rbtree_cached_leftmost_root"]["record"]
            ),
        }
        (root / EXPECTED_REL).write_text(json.dumps(reduced_expected), encoding="utf-8")
        issues = validate(root)
        assert "missing_expected_record:rbtree_uncached_root" in issues
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")

        phase3_abi_path = root / PHASE3_ABI_REL
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(rbtree.isEmpty(empty_root));\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_phase3_abi_empty_rbtree_sample_flags" in issues
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(!rbtree.hasRoot(empty_root));\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_phase3_abi_empty_rbtree_sample_root_check" in issues

        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_phase3_abi_record_value:rbtree_uncached_root" in issues
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_phase3_abi_uncached_rbtree_sample_flags" in issues
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(rbtree.hasRoot(cached_root));\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(
            issue.startswith(
                "missing_phase3_abi_record_presence:rbtree_cached_leftmost_root:try std.testing.expect(rbtree.hasRoot(cached_root));"
            )
            for issue in issues
        )
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(rbtree.hasRoot(uncached_root));\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(
            issue.startswith(
                "missing_phase3_abi_record_presence:rbtree_uncached_root:try std.testing.expect(rbtree.hasRoot(uncached_root));"
            )
            for issue in issues
        )

        phase3_abi_dump_path = root / PHASE3_ABI_DUMP_REL
        phase3_abi_dump_path.write_text(
            phase3_abi_dump_path.read_text(encoding="utf-8").replace(
                'const _ = "rbtree_uncached_root";\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_phase3_abi_dump_record:rbtree_uncached_root" in issues

        phase3_abi_dump_path.write_text(
            phase3_abi_dump_path.read_text(encoding="utf-8").replace(
                'try writer.writeAll(",\\\"hlist_flag_empty\\\":");\n',
                'try writer.writeAll(",\\\"hlist_flag_missing\\\":");\n',
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert (
            f"constant_set_mismatch:{PHASE3_ABI_DUMP_REL}:{EXPECTED_REL}:"
            "missing=hlist_flag_empty:unexpected=hlist_flag_missing"
        ) in issues

    print("PHASE3_ABI_LAYOUT_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the canonical Phase 3 ABI layout packet stays aligned across the shared dump, harness, expected fixture, and Zig layout tests."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker tests without reading the full repo.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_ABI_LAYOUT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ABI_LAYOUT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
