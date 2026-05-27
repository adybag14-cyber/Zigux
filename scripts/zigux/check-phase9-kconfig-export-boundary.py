#!/usr/bin/env python3
"""Guard the Phase 9 note that distinguishes config bridges from export boundaries."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile


NOTE_PATH = pathlib.Path("Documentation/zigux/phase9-kconfig-export-boundary-evidence.md")
CONF_BRIDGE_PATH = pathlib.Path("scripts/zigux/kconfig/conf_bridge.zig")
CONFDATA_BRIDGE_PATH = pathlib.Path("scripts/zigux/kconfig/confdata_bridge.zig")
EXPORT_SHIM_PATH = pathlib.Path("zigux/kernel/export_shim.zig")
RUST_EXPORTS_PATH = pathlib.Path("rust/exports.c")

NOTE_MARKERS = (
    "`scripts/zigux/kconfig/conf_bridge.zig` keeps the current mode and flag bridge for `syncconfig`, `defconfig`, and the bounded allconfig sentinel family",
    "`scripts/zigux/kconfig/confdata_bridge.zig` keeps the current config-file parsing bridge for `CONFIG_` keys, unset markers, quoted strings, and line-normalization edge cases",
    "`zigux/kernel/export_shim.zig` keeps the current direct Phase 3 export-boundary surface through `ExportStatus`, boundary-header validation, and interop-policy validation",
    "`rust/exports.c` does not materialize on the trusted current-`master` direct-read path",
)

CONF_BRIDGE_MARKERS = (
    'pub const Mode = enum {',
    '.syncconfig => "--syncconfig"',
    '.defconfig => "--defconfig"',
    "fn modeUsesAllConfigSentinel(mode: Mode) bool {",
)

CONFDATA_BRIDGE_MARKERS = (
    'const config_prefix = "CONFIG_";',
    "fn truncateAtFirstNull(text: []const u8) []const u8 {",
    "fn parseUnsetSymbol(line: []const u8) ?[]const u8 {",
    "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
)

EXPORT_SHIM_MARKERS = (
    "pub const ExportStatus = abi.ExportStatus;",
    "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {",
    "pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {",
)


class CheckError(RuntimeError):
    pass


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckError(f"missing required path: {path.as_posix()}") from exc


def require_markers(path: pathlib.Path, text: str, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = " | ".join(missing)
        raise CheckError(f"missing marker(s) in {path.as_posix()}: {joined}")


def check(root: pathlib.Path) -> list[str]:
    note = root / NOTE_PATH
    conf_bridge = root / CONF_BRIDGE_PATH
    confdata_bridge = root / CONFDATA_BRIDGE_PATH
    export_shim = root / EXPORT_SHIM_PATH
    rust_exports = root / RUST_EXPORTS_PATH

    note_text = read_text(note)
    conf_bridge_text = read_text(conf_bridge)
    confdata_bridge_text = read_text(confdata_bridge)
    export_shim_text = read_text(export_shim)

    require_markers(note, note_text, NOTE_MARKERS)
    require_markers(conf_bridge, conf_bridge_text, CONF_BRIDGE_MARKERS)
    require_markers(confdata_bridge, confdata_bridge_text, CONFDATA_BRIDGE_MARKERS)
    require_markers(export_shim, export_shim_text, EXPORT_SHIM_MARKERS)

    if rust_exports.exists():
        raise CheckError(
            "rust/exports.c is present, so the Phase 9 note must be revisited before this guard can pass"
        )

    return [
        "PHASE9_KCONFIG_EXPORT_BOUNDARY=pass",
        f"PHASE9_KCONFIG_EXPORT_BOUNDARY_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}",
        f"PHASE9_KCONFIG_EXPORT_BOUNDARY_CONF_BRIDGE_MARKER_COUNT={len(CONF_BRIDGE_MARKERS)}",
        f"PHASE9_KCONFIG_EXPORT_BOUNDARY_CONFDATA_MARKER_COUNT={len(CONFDATA_BRIDGE_MARKERS)}",
        f"PHASE9_KCONFIG_EXPORT_BOUNDARY_EXPORT_SHIM_MARKER_COUNT={len(EXPORT_SHIM_MARKERS)}",
        "PHASE9_KCONFIG_EXPORT_BOUNDARY_RUST_EXPORTS_PRESENT=no",
    ]


def write(rel_path: pathlib.Path, text: str, root: pathlib.Path) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: pathlib.Path) -> None:
    write(
        NOTE_PATH,
        "# Phase 9 Kconfig And Export Boundary Evidence\n\n"
        "This note records the current cross-phase boundary that the Phase 9 runtime-pilot lanes should treat as supporting evidence only.\n\n"
        "- `scripts/zigux/kconfig/conf_bridge.zig` keeps the current mode and flag bridge for `syncconfig`, `defconfig`, and the bounded allconfig sentinel family.\n"
        "- `scripts/zigux/kconfig/confdata_bridge.zig` keeps the current config-file parsing bridge for `CONFIG_` keys, unset markers, quoted strings, and line-normalization edge cases.\n"
        "- `zigux/kernel/export_shim.zig` keeps the current direct Phase 3 export-boundary surface through `ExportStatus`, boundary-header validation, and interop-policy validation.\n"
        "- `rust/exports.c` does not materialize on the trusted current-`master` direct-read path, so keep it as historical export-boundary vocabulary until direct rereads return it.\n",
        root,
    )
    write(
        CONF_BRIDGE_PATH,
        "pub const Mode = enum {\n"
        "    syncconfig,\n"
        "    defconfig,\n"
        "};\n"
        "fn modeUsesAllConfigSentinel(mode: Mode) bool {\n"
        "    return switch (mode) {\n"
        "        .syncconfig => false,\n"
        "        .defconfig => false,\n"
        "    };\n"
        "}\n"
        'const sentinel_sync = .syncconfig => "--syncconfig";\n'
        'const sentinel_def = .defconfig => "--defconfig";\n',
        root,
    )
    write(
        CONFDATA_BRIDGE_PATH,
        'const config_prefix = "CONFIG_";\n'
        "fn truncateAtFirstNull(text: []const u8) []const u8 { return text; }\n"
        "fn parseUnsetSymbol(line: []const u8) ?[]const u8 { _ = line; return null; }\n"
        "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {\n"
        "    _ = allocator;\n"
        "    _ = input;\n"
        "    return undefined;\n"
        "}\n",
        root,
    )
    write(
        EXPORT_SHIM_PATH,
        "pub const ExportStatus = abi.ExportStatus;\n"
        "pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {\n"
        "    _ = header;\n"
        "    return undefined;\n"
        "}\n"
        "pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {\n"
        "    _ = policy;\n"
        "    return undefined;\n"
        "}\n",
        root,
    )


def run_self_test() -> list[str]:
    with tempfile.TemporaryDirectory(prefix="phase9_kconfig_export_boundary_") as tmp:
        root = pathlib.Path(tmp)
        write_sample_root(root)
        check(root)
        bad_note = root / NOTE_PATH
        bad_note.write_text(
            bad_note.read_text(encoding="utf-8").replace(
                "`zigux/kernel/export_shim.zig` keeps the current direct Phase 3 export-boundary surface through `ExportStatus`, boundary-header validation, and interop-policy validation",
                "`zigux/kernel/export_shim.zig` stays nearby",
            ),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckError:
            pass
        else:
            raise CheckError("self-test expected the note marker check to fail")
    return [
        "PHASE9_KCONFIG_EXPORT_BOUNDARY_SELF_TEST=pass",
        "PHASE9_KCONFIG_EXPORT_BOUNDARY_SELF_TEST_CASE_COUNT=2",
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=pathlib.Path)
    args = parser.parse_args(argv)

    try:
        if args.write_sample_root is not None:
            write_sample_root(args.write_sample_root)
        if args.self_test:
            for line in run_self_test():
                print(line)
            return 0
        if args.write_sample_root is not None and args.root == pathlib.Path("."):
            return 0
        for line in check(args.root):
            print(line)
        return 0
    except CheckError as exc:
        print("PHASE9_KCONFIG_EXPORT_BOUNDARY=fail")
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
