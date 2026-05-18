#!/usr/bin/env python3
"""Guard the current Phase 11 HVC layout-proof packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


PACKET_FILES = {
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig": [
        'layout_assert.expectSize(HvOps, 72);',
        'layout_assert.expectAlign(HvOps, 8);',
        'layout_assert.expectOffset(HvOps, "dtr_rts", 64);',
        'try expectContains(hvc_header, "struct hv_ops {");',
        'try expectContains(hvc_header, "(*notifier_hangup)");',
        'try expectContains(hvc_header, "(*dtr_rts)");',
    ],
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig": [
        'layout_assert.assertSize(HvOpsLayout, 72);',
        'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
        'assertExactType(',
        '@FieldType(HvOpsLayout, "get_chars")',
        '@FieldType(HvcExportSurface, "hvc_alloc")',
        'try expectContains(hvc_header, "int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);");',
        'try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");',
    ],
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig": [
        '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
        '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
        '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
        '.name = "phase11-hvc-export-surface-layout-proof-tests",',
        'b.step("test", "Run the focused Phase 11 exported-header proofs");',
        "test_step.dependOn(&run_hv_ops_proof_tests.step);",
        "test_step.dependOn(&run_export_surface_proof_tests.step);",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 11 HVC layout-proof packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in regression coverage.",
    )
    return parser.parse_args()


def load_text(root: Path, relpath: str) -> str:
    path = root / relpath
    return path.read_text(encoding="utf-8")


def check_root(root: Path) -> tuple[list[str], int]:
    missing: list[str] = []
    marker_count = 0

    for relpath, markers in PACKET_FILES.items():
        path = root / relpath
        if not path.is_file():
            missing.append(f"missing file: {relpath}")
            continue

        content = load_text(root, relpath)
        for marker in markers:
            marker_count += 1
            if marker not in content:
                missing.append(f"missing marker in {relpath}: {marker}")

    return missing, marker_count


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_packet_fixture(root: Path) -> None:
    for relpath, markers in PACKET_FILES.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(
            [
                "// synthetic fixture for self-test",
                *markers,
                "",
            ]
        )
        path.write_text(body, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0
    tempdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_layout_packet_"))
    try:
        good_root = tempdir / "good"
        write_packet_fixture(good_root)

        missing, marker_count = check_root(good_root)
        case_count += 1
        expect(not missing, f"expected passing fixture, got: {missing}")
        expect(
            marker_count == sum(len(markers) for markers in PACKET_FILES.values()),
            "marker count mismatch for passing fixture",
        )

        broken_root = tempdir / "broken"
        shutil.copytree(good_root, broken_root)
        broken_path = broken_root / "zigux/tests/phase11_hvc_export_surface_layout_proof.zig"
        broken_text = broken_path.read_text(encoding="utf-8")
        broken_text = broken_text.replace(
            '@FieldType(HvcExportSurface, "hvc_alloc")',
            '@FieldType(HvcExportSurface, "hvc_remove")',
            1,
        )
        broken_path.write_text(broken_text, encoding="utf-8")

        missing, _ = check_root(broken_root)
        case_count += 1
        expect(
            any('@FieldType(HvcExportSurface, "hvc_alloc")' in item for item in missing),
            "expected exported-surface signature drift to fail",
        )

        absent_root = tempdir / "absent"
        absent_root.mkdir(parents=True, exist_ok=True)
        missing, _ = check_root(absent_root)
        case_count += 1
        expect(
            any("missing file: zigux/tests/phase11_hvc_hv_ops_layout_proof.zig" == item for item in missing),
            "expected missing proof file to fail",
        )

        print("PHASE11_HVC_LAYOUT_PROOF_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HVC_LAYOUT_PROOF_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    missing, marker_count = check_root(args.root)
    if missing:
        print("PHASE11_HVC_LAYOUT_PROOF_PACKET=fail")
        for item in missing:
            print(f"PHASE11_HVC_LAYOUT_PROOF_PACKET_ERROR={item}")
        return 1

    print("PHASE11_HVC_LAYOUT_PROOF_PACKET=pass")
    print(f"PHASE11_HVC_LAYOUT_PROOF_PACKET_FILE_COUNT={len(PACKET_FILES)}")
    print(f"PHASE11_HVC_LAYOUT_PROOF_PACKET_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
