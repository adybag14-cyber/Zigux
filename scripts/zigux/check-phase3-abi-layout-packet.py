#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent

EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PHASE3_ABI_REL = "zigux/tests/phase3_abi.zig"
PHASE3_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
PHASE3_ABI_C_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"

CANONICAL_LAYOUTS = (
    ("zigux_boundary_header", "BoundaryHeader", "assertBoundaryHeaderLayout"),
    ("zigux_export_status", "ExportStatus", "assertExportStatusLayout"),
    ("zigux_mmio_range", "MmioRange", "assertMmioRangeLayout"),
    ("zigux_interop_policy", "InteropPolicy", "assertInteropPolicyLayout"),
    ("zigux_bitmap_view", "BitmapView", "assertBitmapViewLayout"),
    ("zigux_cpumask_view", "CpuMaskView", "assertCpuMaskViewLayout"),
    ("zigux_list_head_ref", "ListHeadRef", "assertListHeadRefLayout"),
    ("zigux_list_view", "ListView", "assertListViewLayout"),
    ("zigux_list_summary", "ListSummary", "assertListSummaryLayout"),
    ("zigux_hlist_head_ref", "HListHeadRef", "assertHListHeadRefLayout"),
    ("zigux_hlist_node_ref", "HListNodeRef", "assertHListNodeRefLayout"),
    ("zigux_hlist_view", "HListView", "assertHListViewLayout"),
    ("zigux_hlist_summary", "HListSummary", "assertHListSummaryLayout"),
    ("zigux_rbtree_root_view", "RbtreeRootView", "assertRbtreeRootViewLayout"),
)

REQUIRED_CONSTANTS = (
    ("list_flag_empty", "LIST_FLAG_EMPTY", "ZIGUX_LIST_FLAG_EMPTY"),
    ("list_flag_singular", "LIST_FLAG_SINGULAR", "ZIGUX_LIST_FLAG_SINGULAR"),
    ("list_flag_circular", "LIST_FLAG_CIRCULAR", "ZIGUX_LIST_FLAG_CIRCULAR"),
    ("list_flag_truncated", "LIST_FLAG_TRUNCATED", "ZIGUX_LIST_FLAG_TRUNCATED"),
    ("hlist_flag_empty", "HLIST_FLAG_EMPTY", "ZIGUX_HLIST_FLAG_EMPTY"),
    ("hlist_flag_singular", "HLIST_FLAG_SINGULAR", "ZIGUX_HLIST_FLAG_SINGULAR"),
    ("hlist_flag_terminated", "HLIST_FLAG_TERMINATED", "ZIGUX_HLIST_FLAG_TERMINATED"),
    ("hlist_flag_truncated", "HLIST_FLAG_TRUNCATED", "ZIGUX_HLIST_FLAG_TRUNCATED"),
    ("minor_alloc_flag_truncated", "MINOR_ALLOC_FLAG_TRUNCATED", "ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED"),
    ("minor_alloc_flag_found", "MINOR_ALLOC_FLAG_FOUND", "ZIGUX_MINOR_ALLOC_FLAG_FOUND"),
    ("minor_alloc_flag_exhausted", "MINOR_ALLOC_FLAG_EXHAUSTED", "ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED"),
    ("root_flag_empty", "RBTREE_ROOT_FLAG_EMPTY", "ZIGUX_RBTREE_ROOT_FLAG_EMPTY"),
    ("root_flag_cached", "RBTREE_ROOT_FLAG_CACHED", "ZIGUX_RBTREE_ROOT_FLAG_CACHED"),
    ("root_flag_leftmost_valid", "RBTREE_ROOT_FLAG_LEFTMOST_VALID", "ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID"),
)

SHARED_RBTREE_SAMPLE_MARKER = (
    "PHASE3_SHARED_RBTREE_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root"
)

SHARED_RBTREE_SAMPLE_RECORDS = {
    "rbtree_empty_root": {
        "phase3_decl": "const empty_root: abi.RbtreeRootView = .{",
        "phase3_value": "try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_EMPTY), empty_root.flags);",
        "phase3_checks": (
            "try std.testing.expect(isValidRbtreeRootView(empty_root));",
            "try std.testing.expect(isRbtreeEmpty(empty_root));",
            "try std.testing.expect(!isRbtreeCached(empty_root));",
            "try std.testing.expect(!hasRbtreeLeftmost(empty_root));",
            "try std.testing.expect(!hasRbtreeRoot(empty_root));",
            "try std.testing.expect(isCanonicalRbtreeRootView(empty_root));",
        ),
        "dump_key": '"rbtree_empty_root"',
        "dump_value": 'try writer.print("{d}", .{abi.RBTREE_ROOT_FLAG_EMPTY});',
        "harness_key": '"rbtree_empty_root"',
        "harness_value": 'fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_EMPTY);',
        "record": {
            "root_addr": 0,
            "leftmost_addr": 0,
            "flags": 1,
            "reserved": 0,
        },
    },
    "rbtree_cached_leftmost_root": {
        "phase3_decl": "const cached_root: abi.RbtreeRootView = .{",
        "phase3_value": "try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);",
        "phase3_checks": (
            "try std.testing.expect(isValidRbtreeRootView(cached_root));",
            "try std.testing.expect(!isRbtreeEmpty(cached_root));",
            "try std.testing.expect(isRbtreeCached(cached_root));",
            "try std.testing.expect(hasRbtreeLeftmost(cached_root));",
            "try std.testing.expect(hasRbtreeRoot(cached_root));",
            "try std.testing.expect(isCanonicalRbtreeRootView(cached_root));",
        ),
        "dump_key": '"rbtree_cached_leftmost_root"',
        "harness_key": '"rbtree_cached_leftmost_root"',
        "record": {
            "root_addr": 0x2000,
            "leftmost_addr": 0x1800,
            "flags": 0x6,
            "reserved": 0,
        },
    },
    "rbtree_uncached_root": {
        "phase3_decl": "const uncached_root: abi.RbtreeRootView = .{",
        "phase3_value": "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
        "phase3_checks": (
            "try std.testing.expect(isValidRbtreeRootView(uncached_root));",
            "try std.testing.expect(!isRbtreeEmpty(uncached_root));",
            "try std.testing.expect(!isRbtreeCached(uncached_root));",
            "try std.testing.expect(!hasRbtreeLeftmost(uncached_root));",
            "try std.testing.expect(hasRbtreeRoot(uncached_root));",
            "try std.testing.expect(isCanonicalRbtreeRootView(uncached_root));",
        ),
        "dump_key": '"rbtree_uncached_root"',
        "harness_key": '"rbtree_uncached_root"',
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


def validate(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    expected_text = _read_text(root, EXPECTED_REL, issues)
    layout_assert_text = _read_text(root, LAYOUT_ASSERT_REL, issues)
    phase3_abi_text = _read_text(root, PHASE3_ABI_REL, issues)
    phase3_abi_dump_text = _read_text(root, PHASE3_ABI_DUMP_REL, issues)
    c_harness_text = _read_text(root, PHASE3_ABI_C_HARNESS_REL, issues)

    expected_structs: dict[str, object] = {}
    expected_constants: dict[str, object] = {}
    expected_records: dict[str, object] = {}
    if expected_text:
        try:
            parsed = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            expected_structs = parsed.get("structs", {})
            expected_constants = parsed.get("constants", {})
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
            f"unexpected_expected_struct_count:{len(expected_structs)}!={len(CANONICAL_LAYOUTS)}"
        )

    for json_name, zig_name, assert_name in CANONICAL_LAYOUTS:
        if expected_structs and json_name not in expected_structs:
            issues.append(f"missing_expected_struct:{json_name}")
        if layout_assert_text and f"pub fn {assert_name}() void" not in layout_assert_text:
            issues.append(f"missing_layout_assert_fn:{assert_name}")
        if phase3_abi_text and f"layout_assert.{assert_name}();" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_layout_call:{assert_name}")
        if phase3_abi_dump_text and f'writeStructLayout(writer, "{json_name}", abi.{zig_name},' not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_layout:{json_name}")
        if c_harness_text and f'{{"{json_name}", sizeof(struct {json_name}), _Alignof(struct {json_name})' not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_layout:{json_name}")

    for json_name, zig_name, c_name in REQUIRED_CONSTANTS:
        if expected_constants and json_name not in expected_constants:
            issues.append(f"missing_expected_constant:{json_name}")
        if phase3_abi_text and f"abi.{zig_name}" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_constant:{zig_name}")
        if phase3_abi_dump_text and f"abi.{zig_name}" not in phase3_abi_dump_text:
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
            baseline_keys = list(expected_constants.keys())
            _append_constant_set_issues(
                issues,
                baseline_keys,
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
                        baseline_keys,
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

    for record_name, contract in SHARED_RBTREE_SAMPLE_RECORDS.items():
        if expected_records and expected_records.get(record_name) != contract["record"]:
            issues.append(f"unexpected_expected_record:{record_name}")
        if phase3_abi_text and contract["phase3_decl"] not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_record_decl:{record_name}")
        if phase3_abi_text and contract["phase3_value"] not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_record_value:{record_name}")
        for snippet in contract["phase3_checks"]:
            if phase3_abi_text and snippet not in phase3_abi_text:
                issues.append(f"missing_phase3_abi_record_check:{record_name}:{snippet}")
        if phase3_abi_dump_text and contract["dump_key"] not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_record:{record_name}")
        if "dump_value" in contract and phase3_abi_dump_text and contract["dump_value"] not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_record_value:{record_name}")
        if c_harness_text and contract["harness_key"] not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_record:{record_name}")
        if "harness_value" in contract and c_harness_text and contract["harness_value"] not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_record_value:{record_name}")

    if phase3_abi_text and ".flags = abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID," not in phase3_abi_text:
        issues.append("missing_phase3_abi_cached_rbtree_flags")
    if phase3_abi_text and "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);" not in phase3_abi_text:
        issues.append("missing_phase3_abi_uncached_rbtree_flags")
    if phase3_abi_dump_text and ".{abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID}" not in phase3_abi_dump_text:
        issues.append("missing_phase3_abi_dump_cached_rbtree_flags")
    if c_harness_text and "ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID" not in c_harness_text:
        issues.append("missing_phase3_abi_c_harness_cached_rbtree_flags")

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
                **{json_name: idx + 1 for idx, (json_name, _, _) in enumerate(REQUIRED_CONSTANTS)},
            },
            "records": {
                name: dict(contract["record"])
                for name, contract in SHARED_RBTREE_SAMPLE_RECORDS.items()
            },
            "structs": {
                json_name: {"size": 0, "align": 0, "offsets": {}}
                for json_name, _, _ in CANONICAL_LAYOUTS
            },
        }
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")

        (root / LAYOUT_ASSERT_REL).write_text(
            "\n".join(f"pub fn {assert_name}() void {{}}" for _, _, assert_name in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )

        phase3_lines = [*(f"layout_assert.{assert_name}();" for _, _, assert_name in CANONICAL_LAYOUTS)]
        phase3_lines.extend(f"const _ = abi.{zig_name};" for _, zig_name, _ in REQUIRED_CONSTANTS)
        phase3_lines.extend(
            [
                f"// {SHARED_RBTREE_SAMPLE_MARKER}",
                "const empty_root: abi.RbtreeRootView = .{",
                "    .root_addr = 0,",
                "    .leftmost_addr = 0,",
                "    .flags = abi.RBTREE_ROOT_FLAG_EMPTY,",
                "    .reserved = 0,",
                "};",
                "try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_EMPTY), empty_root.flags);",
                "try std.testing.expect(isValidRbtreeRootView(empty_root));",
                "try std.testing.expect(isRbtreeEmpty(empty_root));",
                "try std.testing.expect(!isRbtreeCached(empty_root));",
                "try std.testing.expect(!hasRbtreeLeftmost(empty_root));",
                "try std.testing.expect(!hasRbtreeRoot(empty_root));",
                "try std.testing.expect(isCanonicalRbtreeRootView(empty_root));",
                "const cached_root: abi.RbtreeRootView = .{",
                "    .root_addr = 0x2000,",
                "    .leftmost_addr = 0x1800,",
                "    .flags = abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID,",
                "    .reserved = 0,",
                "};",
                "try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);",
                "try std.testing.expect(isValidRbtreeRootView(cached_root));",
                "try std.testing.expect(!isRbtreeEmpty(cached_root));",
                "try std.testing.expect(isRbtreeCached(cached_root));",
                "try std.testing.expect(hasRbtreeLeftmost(cached_root));",
                "try std.testing.expect(hasRbtreeRoot(cached_root));",
                "try std.testing.expect(isCanonicalRbtreeRootView(cached_root));",
                "const uncached_root: abi.RbtreeRootView = .{",
                "    .root_addr = 0x2400,",
                "    .leftmost_addr = 0,",
                "    .flags = 0,",
                "    .reserved = 0,",
                "};",
                "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
                "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);",
                "try std.testing.expect(isValidRbtreeRootView(uncached_root));",
                "try std.testing.expect(!isRbtreeEmpty(uncached_root));",
                "try std.testing.expect(!isRbtreeCached(uncached_root));",
                "try std.testing.expect(!hasRbtreeLeftmost(uncached_root));",
                "try std.testing.expect(hasRbtreeRoot(uncached_root));",
                "try std.testing.expect(isCanonicalRbtreeRootView(uncached_root));",
            ]
        )
        (root / PHASE3_ABI_REL).write_text("\n".join(phase3_lines) + "\n", encoding="utf-8")

        dump_lines = [
            DUMP_CONSTANT_PACKET_START,
            *[f'try writer.writeAll(",\\\\\\\"{key}\\\\\\\":");' for key in list(expected["constants"].keys())[1:]],
            DUMP_CONSTANT_PACKET_END,
            'const _ = "rbtree_empty_root";',
            'const _ = "rbtree_cached_leftmost_root";',
            'const _ = "rbtree_uncached_root";',
            'try writer.print("{d}", .{abi.RBTREE_ROOT_FLAG_EMPTY});',
            'try writer.print("{d}", .{abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID});',
            *[
                f'writeStructLayout(writer, "{json_name}", abi.{zig_name}, {str(index + 1 < len(CANONICAL_LAYOUTS)).lower()});'
                for index, (json_name, zig_name, _) in enumerate(CANONICAL_LAYOUTS)
            ],
            *[f"const _ = abi.{zig_name};" for _, zig_name, _ in REQUIRED_CONSTANTS],
        ]
        (root / PHASE3_ABI_DUMP_REL).write_text("\n".join(dump_lines) + "\n", encoding="utf-8")

        harness_lines = [
            HARNESS_CONSTANT_PACKET_START,
            *[f'fputs(",\\\\\\\"{key}\\\\\\\":", stdout);' for key in list(expected["constants"].keys())[1:]],
            HARNESS_CONSTANT_PACKET_END,
            'const char *a = "rbtree_empty_root";',
            'const char *b = "rbtree_cached_leftmost_root";',
            'const char *c = "rbtree_uncached_root";',
            'fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_EMPTY);',
            'fprintf(stdout, "%u", ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID);',
            *[
                f'{{"{json_name}", sizeof(struct {json_name}), _Alignof(struct {json_name}), 0, 0}},'
                for json_name, _, _ in CANONICAL_LAYOUTS
            ],
            *[c_name for _, _, c_name in REQUIRED_CONSTANTS],
        ]
        (root / PHASE3_ABI_C_HARNESS_REL).write_text("\n".join(harness_lines) + "\n", encoding="utf-8")

        assert validate(root) == []

        phase3_abi_path = root / PHASE3_ABI_REL
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                "try std.testing.expect(isCanonicalRbtreeRootView(cached_root));\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(issue.startswith("missing_phase3_abi_record_check:rbtree_cached_leftmost_root:") for issue in issues)

        phase3_abi_path.write_text("\n".join(phase3_lines) + "\n", encoding="utf-8")
        phase3_abi_dump_path = root / PHASE3_ABI_DUMP_REL
        phase3_abi_dump_path.write_text(
            "\n".join(
                line
                for line in phase3_abi_dump_path.read_text(encoding="utf-8").splitlines()
                if not (line.startswith('try writer.writeAll(') and "facility_helpers" in line)
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(issue.startswith(f"constant_count_mismatch:{PHASE3_ABI_DUMP_REL}:") for issue in issues)
        assert any(
            issue.startswith(f"constant_set_mismatch:{PHASE3_ABI_DUMP_REL}:{EXPECTED_REL}:")
            for issue in issues
        )

        phase3_abi_dump_path.write_text("\n".join(dump_lines) + "\n", encoding="utf-8")
        phase3_abi_c_harness_path = root / PHASE3_ABI_C_HARNESS_REL
        phase3_abi_c_harness_path.write_text(
            "\n".join(
                line
                for line in phase3_abi_c_harness_path.read_text(encoding="utf-8").splitlines()
                if not (line.startswith('fputs(') and "facility_helpers" in line)
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(issue.startswith(f"constant_count_mismatch:{PHASE3_ABI_C_HARNESS_REL}:") for issue in issues)
        assert any(
            issue.startswith(f"constant_set_mismatch:{PHASE3_ABI_C_HARNESS_REL}:{EXPECTED_REL}:")
            for issue in issues
        )
        assert any(
            issue.startswith(f"constant_set_mismatch:{PHASE3_ABI_C_HARNESS_REL}:{PHASE3_ABI_DUMP_REL}:")
            for issue in issues
        )

    print("PHASE3_ABI_LAYOUT_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the canonical Phase 3 ABI layout packet stays aligned across the shared "
            "dump, harness, expected fixture, and Zig layout tests."
        )
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