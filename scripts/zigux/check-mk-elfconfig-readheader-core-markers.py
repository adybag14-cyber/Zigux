#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig.zig"

EXPECTED_MARKERS = {
    "fd_entrypoint": "pub fn runMkElfconfigFromFd(",
    "readheader_zero_eof": 'test "readHeader returns zero bytes on immediate EOF" {',
    "readheader_split_fill": 'test "readHeader stops after filling the first ELF header across split reads" {',
    "readheader_split_truncated_count": 'test "readHeader preserves truncated byte count across split reads" {',
    "readheader_immediate_error": 'test "readHeader treats an immediate read error like truncated input" {',
    "readheader_partial_failure": 'test "readHeader keeps partial bytes when a later read fails" {',
    "readheader_first_header": 'test "readHeader stops at the first ELF header" {',
    "readheader_truncated_count": 'test "readHeader reports the exact truncated byte count" {',
}
EXPECTED_ORDER = list(EXPECTED_MARKERS)


def validate_markers(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    positions: list[int] = []
    for label in EXPECTED_ORDER:
        marker = EXPECTED_MARKERS[label]
        count = text.count(marker)
        if count == 0:
            raise ValueError(f"{path}:missing_marker:{label}")
        if count > 1:
            raise ValueError(f"{path}:duplicate_marker:{label}")
        positions.append(text.index(marker))
    if positions != sorted(positions):
        raise ValueError(f"{path}:marker_order:{positions!r}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> Path:
    tool_path = root / "scripts" / "zigux" / "mk_elfconfig.zig"
    write_text(tool_path, "\n".join(EXPECTED_MARKERS[label] for label in EXPECTED_ORDER) + "\n")
    return tool_path


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane14-readheader-core-markers-") as tmp_dir:
        tmp_root = Path(tmp_dir)

        ok_root = tmp_root / "ok"
        validate_markers(write_sample_root(ok_root))

        missing_root = tmp_root / "missing"
        missing_path = write_sample_root(missing_root)
        missing_path.write_text(
            "\n".join(
                EXPECTED_MARKERS[label]
                for label in EXPECTED_ORDER
                if label != "readheader_partial_failure"
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(missing_path)
        except ValueError as exc:
            if "missing_marker:readheader_partial_failure" not in str(exc):
                raise
        else:
            raise AssertionError("expected missing-marker self-test failure")

        duplicate_root = tmp_root / "duplicate"
        duplicate_path = write_sample_root(duplicate_root)
        duplicate_path.write_text(
            "\n".join(
                [EXPECTED_MARKERS["fd_entrypoint"]]
                + [EXPECTED_MARKERS["fd_entrypoint"]]
                + [
                    EXPECTED_MARKERS[label]
                    for label in EXPECTED_ORDER
                    if label != "fd_entrypoint"
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(duplicate_path)
        except ValueError as exc:
            if "duplicate_marker:fd_entrypoint" not in str(exc):
                raise
        else:
            raise AssertionError("expected duplicate-marker self-test failure")

        reordered_root = tmp_root / "reordered"
        reordered_path = write_sample_root(reordered_root)
        reordered_path.write_text(
            "\n".join(
                [EXPECTED_MARKERS["fd_entrypoint"]]
                + [EXPECTED_MARKERS["readheader_split_fill"]]
                + [EXPECTED_MARKERS["readheader_zero_eof"]]
                + [
                    EXPECTED_MARKERS[label]
                    for label in EXPECTED_ORDER
                    if label not in {"fd_entrypoint", "readheader_zero_eof", "readheader_split_fill"}
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            validate_markers(reordered_path)
        except ValueError as exc:
            if "marker_order:" not in str(exc):
                raise
        else:
            raise AssertionError("expected marker-order self-test failure")

    print("MK_ELFCONFIG_READHEADER_CORE_MARKERS_SELF_TEST=pass")
    print("MK_ELFCONFIG_READHEADER_CORE_MARKERS_SELF_TEST_CASE_COUNT=4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that mk_elfconfig keeps the current readHeader core packet markers visible."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to inspect (defaults to the checker's repository root)",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal current-like sample root for focused validation",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="validate the checker logic against synthetic marker fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    validate_markers(args.root / "scripts" / "zigux" / "mk_elfconfig.zig")
    print("MK_ELFCONFIG_READHEADER_CORE_MARKERS=pass")
    print(f"MK_ELFCONFIG_READHEADER_CORE_MARKERS_COUNT={len(EXPECTED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
