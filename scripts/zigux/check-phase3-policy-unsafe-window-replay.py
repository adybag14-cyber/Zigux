#!/usr/bin/env python3
"""Validate the Phase 3 policy/unsafe raw-pointer window replay."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
POLICY_UNSAFE_REPLAY_PATH = Path("zigux/tests/phase3_policy_unsafe.zig")

REQUIRED_MARKERS = {
    UNSAFE_POLICY_PATH: (
        "pub const RawPointerWindow = struct {",
        "pub const RawPointerWindowError = RawPointerBridgeError || error{",
        "fn requireWindowAddress(window: RawPointerWindow, byte_offset: usize, access_len: usize) RawPointerWindowError!usize {",
        "pub fn windowInteropPolicy(",
        "pub fn windowByte(base_addr: usize, byte_len: usize, scope: u8) RawPointerWindowError!RawPointerWindow {",
        "pub fn pointerAtWindow(",
        "pub fn constPointerAtWindow(",
        "pub fn sliceAtWindow(",
        "pub fn constSliceAtWindow(",
        "pub fn readValueAtWindow(",
        "pub fn writeValueAtWindow(",
        "pub fn exchangeValueAtWindow(",
        'test "phase3 unsafe policy keeps raw-pointer bridge windows bounded" {',
        "try std.testing.expectError(error.AccessOutsideWindow, pointerAtWindow(u32, window, byte_len));",
        "try std.testing.expectError(error.OffsetOverflow, readValueAtWindow(u32, window, std.math.maxInt(usize)));",
    ),
    POLICY_UNSAFE_REPLAY_PATH: (
        'test "phase3 policy unsafe replay keeps raw-pointer windows bounded" {',
        "const window = try unsafe_policy.windowInteropPolicy(base_addr, byte_len, raw);",
        "try testing.expectEqual(window, try unsafe_policy.windowByte(base_addr, byte_len, abi.UNSAFE_RAW_POINTER_BRIDGE));",
        "const first = try unsafe_policy.pointerAtWindow(u32, window, 0);",
        "const second = try unsafe_policy.constPointerAtWindow(u32, window, @sizeOf(u32));",
        "const mutable_slice = try unsafe_policy.sliceAtWindow(u32, window, 0, bridge_words.len);",
        "const replay_slice = try unsafe_policy.constSliceAtWindow(u32, window, 0, bridge_words.len);",
        "try unsafe_policy.writeValueAtWindow(u32, window, @sizeOf(u32) * 2, 73);",
        "try unsafe_policy.exchangeValueAtWindow(u32, window, @sizeOf(u32) * 2, 79),",
        "try testing.expectError(error.AccessOutsideWindow, unsafe_policy.pointerAtWindow(u32, window, byte_len));",
        "try testing.expectError(error.OffsetOverflow, unsafe_policy.readValueAtWindow(u32, window, std.math.maxInt(usize)));",
    ),
}

SELF_TEST_MUTATIONS = (
    (
        "missing helper window type",
        UNSAFE_POLICY_PATH,
        REQUIRED_MARKERS[UNSAFE_POLICY_PATH][0],
    ),
    (
        "missing helper outside-window proof",
        UNSAFE_POLICY_PATH,
        REQUIRED_MARKERS[UNSAFE_POLICY_PATH][13],
    ),
    (
        "missing replay test",
        POLICY_UNSAFE_REPLAY_PATH,
        REQUIRED_MARKERS[POLICY_UNSAFE_REPLAY_PATH][0],
    ),
    (
        "missing replay write window proof",
        POLICY_UNSAFE_REPLAY_PATH,
        REQUIRED_MARKERS[POLICY_UNSAFE_REPLAY_PATH][7],
    ),
    (
        "missing replay overflow proof",
        POLICY_UNSAFE_REPLAY_PATH,
        REQUIRED_MARKERS[POLICY_UNSAFE_REPLAY_PATH][10],
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = read_text(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def populate_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_window_replay_") as temp_dir:
        root = Path(temp_dir)
        populate_sample_repo(root)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_WINDOW_REPLAY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for case_name, relative_path, marker in SELF_TEST_MUTATIONS:
            populate_sample_repo(root)
            path = root / relative_path
            path.write_text(read_text(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_POLICY_UNSAFE_WINDOW_REPLAY_SELF_TEST=fail")
                print(f"{case_name}: expected issue not reported: {expected}")
                return 1

    print("PHASE3_POLICY_UNSAFE_WINDOW_REPLAY_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_WINDOW_REPLAY_SELF_TEST_CASE_COUNT={len(SELF_TEST_MUTATIONS) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 policy/unsafe raw-pointer window replay."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_WINDOW_REPLAY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / UNSAFE_POLICY_PATH}")
    print(f"validated {args.repo_root / POLICY_UNSAFE_REPLAY_PATH}")
    print("PHASE3_POLICY_UNSAFE_WINDOW_REPLAY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
