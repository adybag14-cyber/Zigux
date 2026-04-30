#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

HEADER_BINDING_MARKERS = {
    "include/zigux/abi.h": (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_export_status {",
    ),
    "include/linux/zigux.h": (
        "#define ZIGUX_BITS_PER_LONG ((zigux_u32)(sizeof(unsigned long) * 8U))",
        "static inline struct zigux_export_status zigux_status_ok(zigux_u16 facility)",
        "static inline struct zigux_export_status zigux_status_err(zigux_s32 code,",
        "#define zigux_assert_layout(type, expected_size) \\",
        "zigux_bitmap_view_from_words(const unsigned long *words, zigux_u32 nbits)",
    ),
    "zigux/bindings/abi.zig": (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const Facility = enum(u16) {",
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
    ),
}


def validate_header_binding_markers(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    for rel, markers in HEADER_BINDING_MARKERS.items():
        path = root / rel
        if not path.exists():
            issues.append(f"header-binding-marker: missing {rel}")
            continue

        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"header-binding-marker: {rel} missing {marker}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_header_binding_marker_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel, markers in HEADER_BINDING_MARKERS.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8", newline="\n")

        assert validate_header_binding_markers(root) == []

        first_marker = HEADER_BINDING_MARKERS["include/zigux/abi.h"][0]
        abi_header = root / "include/zigux/abi.h"
        abi_header.write_text(
            abi_header.read_text(encoding="utf-8").replace(first_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_header_binding_markers(root) == [
            f"header-binding-marker: include/zigux/abi.h missing {first_marker}"
        ]

    print("PHASE3_HEADER_BINDING_MARKER_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_self_test())
