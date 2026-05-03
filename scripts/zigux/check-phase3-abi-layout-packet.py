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
    ("zigux_boundary_header", "BoundaryHeader", "assertBoundaryHeaderLayout"),
    ("zigux_export_status", "ExportStatus", "assertExportStatusLayout"),
    ("zigux_mmio_range", "MmioRange", "assertMmioRangeLayout"),
    ("zigux_interop_policy", "InteropPolicy", "assertInteropPolicyLayout"),
    ("zigux_bitmap_view", "BitmapView", "assertBitmapViewLayout"),
    ("zigux_cpumask_view", "CpuMaskView", "assertCpuMaskViewLayout"),
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
    if expected_text:
        try:
            parsed = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            expected_structs = parsed.get("structs", {})
            if not isinstance(expected_structs, dict):
                issues.append("invalid_expected_json:structs-not-object")
                expected_structs = {}

    if expected_structs and len(expected_structs) != len(CANONICAL_LAYOUTS):
        issues.append(
            "unexpected_expected_struct_count:"
            f"{len(expected_structs)}!= {len(CANONICAL_LAYOUTS)}"
        )

    for c_name, zig_name, assert_name in CANONICAL_LAYOUTS:
        if expected_structs and c_name not in expected_structs:
            issues.append(f"missing_expected_struct:{c_name}")

        if layout_assert_text and f"pub fn {assert_name}() void" not in layout_assert_text:
            issues.append(f"missing_layout_assert_fn:{assert_name}")
        if phase3_abi_text and f"layout_assert.{assert_name}();" not in phase3_abi_text:
            issues.append(f"missing_phase3_abi_layout_call:{assert_name}")
        if phase3_abi_dump_text and f'writeStructLayout(writer, "{c_name}", abi.{zig_name},' not in phase3_abi_dump_text:
            issues.append(f"missing_phase3_abi_dump_layout:{c_name}")
        if c_harness_text and f'{{"{c_name}", sizeof(struct {c_name}), _Alignof(struct {c_name})' not in c_harness_text:
            issues.append(f"missing_phase3_abi_c_harness_layout:{c_name}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_layout_packet_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "zigux" / "tests" / "fixtures" / "phase3_abi").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "helpers").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests").mkdir(parents=True, exist_ok=True)

        expected = {
            "abi_version": 1,
            "constants": {},
            "structs": {
                c_name: {"size": 0, "align": 0, "offsets": {}}
                for c_name, _, _ in CANONICAL_LAYOUTS
            },
        }
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")
        (root / LAYOUT_ASSERT_REL).write_text(
            "\n".join(f"pub fn {assert_name}() void {{}}" for _, _, assert_name in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_REL).write_text(
            "\n".join(f"layout_assert.{assert_name}();" for _, _, assert_name in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_DUMP_REL).write_text(
            "\n".join(
                f'writeStructLayout(writer, "{c_name}", abi.{zig_name}, true);'
                for c_name, zig_name, _ in CANONICAL_LAYOUTS
            )
            + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_ABI_C_HARNESS_REL).write_text(
            "\n".join(
                f'{{"{c_name}", sizeof(struct {c_name}), _Alignof(struct {c_name}), 0, 0}},'
                for c_name, _, _ in CANONICAL_LAYOUTS
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
        assert "unexpected_expected_struct_count:5!= 6" in issues
        assert f"missing_expected_struct:{CANONICAL_LAYOUTS[-1][0]}" in issues
        (root / EXPECTED_REL).write_text(json.dumps(expected), encoding="utf-8")

        layout_assert_path = root / LAYOUT_ASSERT_REL
        layout_assert_path.write_text(
            layout_assert_path.read_text(encoding="utf-8").replace(
                f"pub fn {CANONICAL_LAYOUTS[0][2]}() void {{}}\n", "", 1
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"missing_layout_assert_fn:{CANONICAL_LAYOUTS[0][2]}" in issues
        layout_assert_path.write_text(
            "\n".join(f"pub fn {assert_name}() void {{}}" for _, _, assert_name in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )

        phase3_abi_dump_path = root / PHASE3_ABI_DUMP_REL
        phase3_abi_dump_path.write_text(
            phase3_abi_dump_path.read_text(encoding="utf-8").replace(
                f'writeStructLayout(writer, "{CANONICAL_LAYOUTS[1][0]}", abi.{CANONICAL_LAYOUTS[1][1]}, true);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"missing_phase3_abi_dump_layout:{CANONICAL_LAYOUTS[1][0]}" in issues
        phase3_abi_dump_path.write_text(
            "\n".join(
                f'writeStructLayout(writer, "{c_name}", abi.{zig_name}, true);'
                for c_name, zig_name, _ in CANONICAL_LAYOUTS
            )
            + "\n",
            encoding="utf-8",
        )

        phase3_abi_path = root / PHASE3_ABI_REL
        phase3_abi_path.write_text(
            phase3_abi_path.read_text(encoding="utf-8").replace(
                f"layout_assert.{CANONICAL_LAYOUTS[2][2]}();\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"missing_phase3_abi_layout_call:{CANONICAL_LAYOUTS[2][2]}" in issues
        phase3_abi_path.write_text(
            "\n".join(f"layout_assert.{assert_name}();" for _, _, assert_name in CANONICAL_LAYOUTS) + "\n",
            encoding="utf-8",
        )

        c_harness_path = root / PHASE3_ABI_C_HARNESS_REL
        c_harness_path.write_text(
            c_harness_path.read_text(encoding="utf-8").replace(
                f'{{"{CANONICAL_LAYOUTS[3][0]}", sizeof(struct {CANONICAL_LAYOUTS[3][0]}), _Alignof(struct {CANONICAL_LAYOUTS[3][0]}), 0, 0}},\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"missing_phase3_abi_c_harness_layout:{CANONICAL_LAYOUTS[3][0]}" in issues

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