#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

HELPER_PATH = ROOT / "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
TEST_PATH = ROOT / "zigux/tests/phase8_file_path_handle_bridge.zig"
MANIFEST_PATH = ROOT / "tools/lib/bpf/zigux_segments/manifest.json"

FDINFO_REQUIRED_HELPERS = [
    "pub fn buildProcFdinfoPath",
    "pub fn parseFdinfoLine",
    "pub fn applyFdinfoMapInfoLine",
    "pub fn parseFdinfoMapInfo",
    "pub fn summarizeFdinfoMapInfo",
]

FDINFO_REQUIRED_TEST_MARKERS = [
    "buildProcFdinfoPath",
    "parseFdinfoMapInfo",
    "applyFdinfoMapInfoLine",
]

MAP_REUSE_REQUIRED_HELPERS = [
    "pub fn resolveReusedMapName",
    "pub fn summarizeMapReuseCompatibility",
    "pub fn isMapReuseCompatible",
]

MAP_REUSE_REQUIRED_TEST_MARKERS = [
    "resolveReusedMapName",
    "summarizeMapReuseCompatibility",
    "isMapReuseCompatible",
]


class CheckFailure(Exception):
    pass


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing required file: {path.as_posix()}") from exc


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        formatted = ", ".join(repr(marker) for marker in missing)
        raise CheckFailure(f"{label} is missing required markers: {formatted}")


def find_segment(manifest: dict, slug: str) -> dict:
    for segment in manifest.get("segments", []):
        if segment.get("slug") == slug:
            return segment
    raise CheckFailure(f"manifest is missing segment {slug!r}")


def check_scope(helper_text: str, test_text: str, manifest: dict) -> None:
    fdinfo_segment = find_segment(manifest, "fdinfo-map-info-helpers")
    map_reuse_segment = find_segment(manifest, "map-reuse-compatibility")

    if fdinfo_segment.get("status") == "starter_landed":
        require_markers(
            helper_text,
            FDINFO_REQUIRED_HELPERS,
            "file-path bridge helper for fdinfo-map-info-helpers",
        )
        require_markers(
            test_text,
            FDINFO_REQUIRED_TEST_MARKERS,
            "phase8_file_path_handle_bridge tests for fdinfo-map-info-helpers",
        )

    if map_reuse_segment.get("status") == "starter_landed":
        require_markers(
            helper_text,
            MAP_REUSE_REQUIRED_HELPERS,
            "file-path bridge helper for map-reuse-compatibility",
        )
        require_markers(
            test_text,
            MAP_REUSE_REQUIRED_TEST_MARKERS,
            "phase8_file_path_handle_bridge tests for map-reuse-compatibility",
        )


def run_repo_check(root: Path) -> None:
    helper_text = load_text(root / HELPER_PATH.relative_to(ROOT))
    test_text = load_text(root / TEST_PATH.relative_to(ROOT))
    manifest = json.loads(load_text(root / MANIFEST_PATH.relative_to(ROOT)))
    check_scope(helper_text, test_text, manifest)


PASSING_MANIFEST = {
    "segments": [
        {"slug": "fdinfo-map-info-helpers", "status": "starter_landed"},
        {"slug": "map-reuse-compatibility", "status": "deferred_high_risk"},
    ]
}

PASSING_HELPER = """
pub fn buildProcFdinfoPath() void {}
pub fn parseFdinfoLine() void {}
pub fn applyFdinfoMapInfoLine() void {}
pub fn parseFdinfoMapInfo() void {}
pub fn summarizeFdinfoMapInfo() void {}
"""

PASSING_TEST = """
test "fdinfo" {
    _ = buildProcFdinfoPath;
    _ = parseFdinfoMapInfo;
    _ = applyFdinfoMapInfoLine;
}
"""

FAILING_MANIFEST = {
    "segments": [
        {"slug": "fdinfo-map-info-helpers", "status": "starter_landed"},
        {"slug": "map-reuse-compatibility", "status": "starter_landed"},
    ]
}

FAILING_HELPER = """
pub fn buildProcFdinfoPath() void {}
pub fn parseFdinfoLine() void {}
pub fn applyFdinfoMapInfoLine() void {}
pub fn parseFdinfoMapInfo() void {}
pub fn summarizeFdinfoMapInfo() void {}
"""

FAILING_TEST = """
test "fdinfo" {
    _ = buildProcFdinfoPath;
    _ = parseFdinfoMapInfo;
    _ = applyFdinfoMapInfoLine;
}
"""

FAILING_FDINFO_HELPER = """
pub fn buildProcFdinfoPath() void {}
pub fn applyFdinfoMapInfoLine() void {}
pub fn parseFdinfoMapInfo() void {}
pub fn summarizeFdinfoMapInfo() void {}
"""


def expect_failure(
    helper_text: str,
    test_text: str,
    manifest: dict,
    expected_scope: str,
) -> None:
    try:
        check_scope(helper_text, test_text, manifest)
    except CheckFailure as exc:
        message = str(exc)
        if expected_scope not in message:
            raise CheckFailure(
                f"self-test expected a {expected_scope} failure, got: {message}"
            ) from exc
        return
    raise CheckFailure(f"self-test expected a {expected_scope} scope failure")


def run_self_test() -> None:
    check_scope(PASSING_HELPER, PASSING_TEST, PASSING_MANIFEST)
    expect_failure(
        FAILING_FDINFO_HELPER,
        PASSING_TEST,
        PASSING_MANIFEST,
        "fdinfo-map-info-helpers",
    )
    expect_failure(
        FAILING_HELPER,
        FAILING_TEST,
        FAILING_MANIFEST,
        "map-reuse-compatibility",
    )
    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_SCOPE_SELF_TEST=pass")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when the Phase 8 file-path bridge manifest claims "
            "landed helper scope that the helper or focused tests do not expose."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to inspect (defaults to the inferred repo root)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in coverage checks instead of inspecting a repo",
    )
    args = parser.parse_args()

    try:
        if args.self_test:
            run_self_test()
        else:
            run_repo_check(args.root.resolve())
            print("PHASE8_FILE_PATH_HANDLE_BRIDGE_SCOPE=pass")
    except CheckFailure as exc:
        print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_SCOPE=fail: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
