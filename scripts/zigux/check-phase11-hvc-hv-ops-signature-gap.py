#!/usr/bin/env python3
"""Fail-closed guard for the current-head Phase 11 HVC hv_ops signature gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) > 3 else SELF_PATH.parent

NOTE_PATH = Path("Documentation/zigux/phase11-hvc-hv-ops-signature-gap.md")
ZIG_PATH = Path("drivers/tty/hvc/hvc_console.zig")
HEADER_PATH = Path("drivers/tty/hvc/hvc_console.h")

NOTE_MARKERS = (
    "`PHASE11_HVC_HV_OPS_SIGNATURE_GAP=current_head_mismatch_visible`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`HvOps.get_chars`",
    "`HvOps.put_chars`",
    "`usize` count and `isize` return types",
    "exported `int` count and `int` return contract",
    "realign `HvOps.get_chars` and",
)
HEADER_MARKERS = (
    "int (*get_chars)(uint32_t vtermno, char *buf, int count);",
    "int (*put_chars)(uint32_t vtermno, const char *buf, int count);",
)
ZIG_MARKERS = (
    "get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize = null,",
    "put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize = null,",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def run_check(root: Path) -> None:
    note = read_text(root / NOTE_PATH)
    zig = read_text(root / ZIG_PATH)
    header = read_text(root / HEADER_PATH)

    require_markers(note, NOTE_MARKERS, "note")
    require_markers(header, HEADER_MARKERS, "header")
    require_markers(zig, ZIG_MARKERS, "zig")

    if "int (*get_chars)(uint32_t vtermno, char *buf, int count);" not in header:
        raise CheckError("header no longer exposes the current get_chars contract")
    if "int (*put_chars)(uint32_t vtermno, const char *buf, int count);" not in header:
        raise CheckError("header no longer exposes the current put_chars contract")
    if "get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize = null," not in zig:
        raise CheckError("zig get_chars signature no longer matches the documented current-head gap")
    if "put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize = null," not in zig:
        raise CheckError("zig put_chars signature no longer matches the documented current-head gap")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / NOTE_PATH,
        """# Phase 11 HVC hv_ops Signature Gap

`PHASE11_HVC_HV_OPS_SIGNATURE_GAP=current_head_mismatch_visible`
`drivers/tty/hvc/hvc_console.zig`
`drivers/tty/hvc/hvc_console.h`
`HvOps.get_chars`
`HvOps.put_chars`
`usize` count and `isize` return types
exported `int` count and `int` return contract
The next honest step is to realign `HvOps.get_chars` and `HvOps.put_chars`.
""",
    )
    write(
        root / HEADER_PATH,
        """struct hv_ops {
    int (*get_chars)(uint32_t vtermno, char *buf, int count);
    int (*put_chars)(uint32_t vtermno, const char *buf, int count);
};
""",
    )
    write(
        root / ZIG_PATH,
        """pub const HvOps = extern struct {
    get_chars: ?*const fn (u32, [*]u8, usize) callconv(.c) isize = null,
    put_chars: ?*const fn (u32, [*]const u8, usize) callconv(.c) isize = null,
};
""",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_hv_ops_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_note_marker = tmpdir / "missing_note_marker"
        shutil.copytree(fixture, missing_note_marker, dirs_exist_ok=True)
        write(
            missing_note_marker / NOTE_PATH,
            read_text(missing_note_marker / NOTE_PATH).replace(
                "`usize` count and `isize` return types\n",
                "",
            ),
        )
        expect_failure(missing_note_marker, "missing note marker")

        header_aligned = tmpdir / "header_aligned"
        shutil.copytree(fixture, header_aligned, dirs_exist_ok=True)
        write(
            header_aligned / ZIG_PATH,
            read_text(header_aligned / ZIG_PATH).replace("usize", "c_int").replace("isize", "c_int"),
        )
        expect_failure(
            header_aligned,
            "missing zig marker",
        )

        print("PHASE11_HVC_HV_OPS_SIGNATURE_GAP_SELF_TEST=pass")
        print("PHASE11_HVC_HV_OPS_SIGNATURE_GAP_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_check(args.root.resolve())
    print("PHASE11_HVC_HV_OPS_SIGNATURE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
