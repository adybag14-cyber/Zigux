#!/usr/bin/env python3
"""Fail-close the current Phase 3 err_ptr/xarray starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-errptr-xarray-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
ERR_PTR_PATH = Path("zigux/helpers/err_ptr.zig")
XA_VALUE_PATH = Path("zigux/helpers/xa_value.zig")
TEST_PATH = Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json")

STARTER_BUILD_ROUTE = (
    "zig build phase3-errptr-xarray-starter-packet-test --build-file "
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"
)

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
        "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
        STARTER_BUILD_ROUTE,
        "the highest tagged inline boundary still stays below the `err_ptr` floor",
        "It is one helper-local interop proof layered beside the existing `dev_t` starter packet.",
    ),
    VALIDATOR_NOTE_PATH: (
        "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
        "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
        "the manifest-backed starter packet",
    ),
    ERR_PTR_PATH: (
        "pub const max_errno: usize = 4095;",
        "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
        "pub fn fromErrorCode(code: isize) usize {",
        "pub fn isErrValue(raw: usize) bool {",
        "pub fn toErrorCode(raw: usize) isize {",
    ),
    XA_VALUE_PATH: (
        "const err_ptr = @import(\"err_ptr\");",
        "pub const value_tag_mask: usize = 0x1;",
        "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
        "ValueWouldOverlapErrPtr",
        "return (value << 1) | value_tag_mask;",
        "return (raw & value_tag_mask) == value_tag_mask and !err_ptr.isErrValue(raw);",
    ),
    TEST_PATH: (
        "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
        "test \"xa_value round-trips a bounded inline value without entering the err_ptr band\" {",
        "test \"xa_value rejects inline values that would overlap err_ptr encodings\" {",
        "test \"safe inline limit stays the highest tagged value below the err_ptr floor\" {",
        "try testing.expectEqual(err_ptr.err_floor, raw + 2);",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/err_ptr.zig"),',
        '.root_source_file = b.path("../helpers/xa_value.zig"),',
        '.root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),',
        'xa_value.addImport("err_ptr", err_ptr);',
        '"phase3-errptr-xarray-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-errptr-xarray-starter-packet"',
        '"status": "starter_packet_present"',
        '"Documentation/zigux/phase3-errptr-xarray-slice.md"',
        '"Documentation/zigux/phase3-validator-support-surface.md"',
        '"zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json"',
        '"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"',
        STARTER_BUILD_ROUTE,
        '"repo_reality_gaps": []',
        '"next_safe_step": "keep the helper-local err_ptr/xarray packet honest with manifest-backed replay before widening into broader Phase 3 validator or export-boundary claims"',
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    STARTER_BUILD_ROUTE,
)

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}
SAMPLE_FILES[MANIFEST_PATH] = f"""{{
  \"phase\": \"Phase 3\",
  \"lane\": \"helper-interop\",
  \"slug\": \"phase3-errptr-xarray-starter-packet\",
  \"status\": \"starter_packet_present\",
  \"scope\": \"helper-local err_ptr and xarray inline-value boundary replay\",
  \"packet_files\": [
    \"Documentation/zigux/phase3-errptr-xarray-slice.md\",
    \"Documentation/zigux/phase3-validator-support-surface.md\",
    \"zigux/helpers/err_ptr.zig\",
    \"zigux/helpers/xa_value.zig\",
    \"zigux/tests/phase3_errptr_xarray_starter_packet.zig\",
    \"zigux/tests/phase3_errptr_xarray_starter_packet_build.zig\",
    \"zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json\",
    \"scripts/zigux/check-phase3-errptr-xarray-starter-packet.py\"
  ],
  \"replay_routes\": [
    \"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test\",
    \"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py\",
    \"{STARTER_BUILD_ROUTE}\"
  ],
  \"repo_reality_gaps\": [],
  \"next_safe_step\": \"keep the helper-local err_ptr/xarray packet honest with manifest-backed replay before widening into broader Phase 3 validator or export-boundary claims\"
}}
"""

SELF_TEST_CASES = (
    (SLICE_PATH, "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json"),
    (SLICE_PATH, STARTER_BUILD_ROUTE),
    (VALIDATOR_NOTE_PATH, "the manifest-backed starter packet"),
    (ERR_PTR_PATH, "pub fn isErrValue(raw: usize) bool {"),
    (XA_VALUE_PATH, "ValueWouldOverlapErrPtr"),
    (TEST_PATH, "try testing.expectEqual(err_ptr.err_floor, raw + 2);"),
    (BUILD_PATH, '"phase3-errptr-xarray-starter-packet-test"'),
    (MANIFEST_PATH, '"status": "starter_packet_present"'),
    (MANIFEST_PATH, STARTER_BUILD_ROUTE),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append(
                    "phase3_errptr_xarray_starter_packet_manifest.json packet_files is not a list"
                )
            if not isinstance(replay_routes, list):
                issues.append(
                    "phase3_errptr_xarray_starter_packet_manifest.json replay_routes is not a list"
                )
            if not isinstance(repo_reality_gaps, list):
                issues.append(
                    "phase3_errptr_xarray_starter_packet_manifest.json repo_reality_gaps is not a list"
                )
            elif repo_reality_gaps:
                issues.append(
                    "phase3_errptr_xarray_starter_packet_manifest.json repo_reality_gaps should stay empty once the helper-local reminder follow-up is parked"
                )
            if isinstance(packet_files, list):
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_errptr_xarray_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_errptr_xarray_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_errptr_xarray_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["scripts/zigux/validate-phase3.py"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_errptr_xarray_starter_packet_manifest.json repo_reality_gaps should stay empty once the helper-local reminder follow-up is parked"
        )
        if expected not in issues:
            print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=fail")
            print("expected non-empty repo_reality_gaps issue was not reported")
            return 1

    print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 err_ptr/xarray starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 err_ptr/xarray starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
