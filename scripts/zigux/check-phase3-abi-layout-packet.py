#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


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
    ("zigux_cpumask_view", "CpuMaskView", "assertCpuMaskViewLayout", "abi"),
    ("zigux_rbtree_root_view", "RootView", "assertRbtreeRootViewLayout", "rbtree"),
)

REQUIRED_CONSTANTS = (
    ("root_flag_empty", "ROOT_FLAG_EMPTY", "ZIGUX_RBTREE_ROOT_FLAG_EMPTY"),
    ("root_flag_cached", "ROOT_FLAG_CACHED", "ZIGUX_RBTREE_ROOT_FLAG_CACHED"),
    ("root_flag_leftmost_valid", "ROOT_FLAG_LEFTMOST_VALID", "ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID"),
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    expected_text = _read_text(root, EXPECTED_REL, issues)
    layout_assert_text = _read_text(root, LAYOUT_ASSERT_REL, issues)
    phase3_abi_text = _read_text(root, PHASE3_ABI_REL, issues)
    phase3_abi_dump_text = _read_text(root, PHASE3_ABI_DUMP_REL, issues)
    c_harness_text = _read_text(root, PHASE3_ABI_C_HARNESS_REL, issues)

    expected_structs: dict[str, object] = {}
    expected_constants: dict[str, object] = {}
    if expected_text:
        try:
            parsed = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            expected_structs = parsed.get("structs", {})
            expected_constants = parsed.get("constants", {})
            if not isinstance(expected_structs, dict):
                issues.append("invalid_expected_json:structs-not-object")
                expected_structs = {}
            if not isinstance(expected_constants, dict):
                issues.append("invalid_expected_json:constants-not-object")
                expected_constants = {}

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

    for json_name, zig_name, c_name in REQUIRED_CONSTANTS:
        if expected_constants and json_name not in expected_constants:
            issues.append(f"missing_expected_constant:{json_name}")
        if phase3_abi_text and f"rbtree.{zig_name}" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_rbtree_constant:{zig_name}")
        if phase3_abi_dump_text and f"rbtree.{zig_name}" not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_rbtree_constant:{zig_name}")
        if c_harness_text and c_name not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_rbtree_constant:{c_name}")

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
                for index, (json_name, _, _) in enumerate(REQUIRED_CONSTANTS)
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
                + [*(f"const _ = rbtree.{zig_name};" for _, zig_name, _ in REQUIRED_CONSTANTS)]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_DUMP_REL).write_text(
            "\n".join(
                [*(f'writeStructLayout(writer, "{json_name}", {module_name}.{zig_name}, true);' for json_name, zig_name, _, module_name in CANONICAL_LAYOUTS)]
                + [*(f"const _ = rbtree.{zig_name};" for _, zig_name, _ in REQUIRED_CONSTANTS)]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_C_HARNESS_REL).write_text(
            "\n".join(
                [*(f'{{"{json_name}", sizeof(struct {json_name}), _Alignof(struct {json_name}), 0, 0}},' for json_name, _, _, _ in CANONICAL_LAYOUTS)]
                + [*(c_name for _, _, c_name in REQUIRED_CONSTANTS)]
            )
            + "\n",
            encoding="utf-8",
        )

        assert validate(root) == []

        reduced_expected = dict(expected)
        reduced_expected["structs"] = dict(expected["structs"])
        reduced_expected["structs"].pop(CANONICAL_LAYOUTS[-1][0])
        (root / EXPECTED_REL).write_text(json.dumps(reduced_expected), encoding="utf-8")
        issues = validate(root)
        assert "unexpected_expected_struct_count:6!= 7" in issues
        assert f"missing_expected_struct:{CANONICAL_LAYOUTS[-1][0]}" in issues
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")

        phase3_abi_dump_path = root / PHASE3_ABI_DUMP_REL
        phase3_abi_dump_path.write_text(
            phase3_abi_dump_path.read_text(encoding="utf-8").replace(
                f'writeStructLayout(writer, "{CANONICAL_LAYOUTS[-1][0]}", {CANONICAL_LAYOUTS[-1][3]}.{CANONICAL_LAYOUTS[-1][1]}, true);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"missing_phase3_abi_dump_layout:{CANONICAL_LAYOUTS[-1][0]}" in issues

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
