#!/usr/bin/env python3
"""Fail-close the current Phase 3 err_ptr/xarray parity packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-errptr-xarray-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
ERR_PTR_PATH = Path("zigux/helpers/err_ptr.zig")
XA_VALUE_PATH = Path("zigux/helpers/xa_value.zig")
DUMP_PATH = Path("zigux/tests/phase3_errptr_xarray_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_errptr_xarray_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_errptr_xarray/expected.json")
C_HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c"
)
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_errptr_xarray_manifest.json")

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/tests/phase3_errptr_xarray_dump.zig",
        "zigux/tests/phase3_errptr_xarray_dump_build.zig",
        "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c",
        "zigux/tests/fixtures/phase3_errptr_xarray/expected.json",
        "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
        "scripts/zigux/check-phase3-errptr-xarray.py",
        "fixture-backed parity packet",
    ),
    VALIDATOR_NOTE_PATH: (
        "zigux/tests/phase3_errptr_xarray_dump.zig",
        "zigux/tests/phase3_errptr_xarray_dump_build.zig",
        "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
        "scripts/zigux/check-phase3-errptr-xarray.py",
        "fixture-backed parity packet",
    ),
    ERR_PTR_PATH: (
        "pub const max_errno: usize = 4095;",
        "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
        "pub fn fromErrorCode(code: isize) usize {",
        "pub fn isErrValue(raw: usize) bool {",
        "pub fn toErrorCode(raw: usize) isize {",
    ),
    XA_VALUE_PATH: (
        'const err_ptr = @import("err_ptr");',
        "pub const value_tag_mask: usize = 0x1;",
        "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
        "ValueWouldOverlapErrPtr",
        "return (value << 1) | value_tag_mask;",
    ),
    DUMP_PATH: (
        'return "null";',
        'return "xa_value";',
        'return "err_ptr";',
        '\\"safe_inline_limit_raw_hex\\"',
        'try writeCase(writer, "inline_limit", inline_limit_raw, true);',
        'try writeCase(writer, "err_floor_plus_one", err_ptr.err_floor + 1, true);',
        'try writeCase(writer, "err_enomem", err_ptr.fromErrorCode(-12), false);',
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/err_ptr.zig"),',
        '.root_source_file = b.path("../helpers/xa_value.zig"),',
        '.root_source_file = b.path("phase3_errptr_xarray_dump.zig"),',
        'xa_value.addImport("err_ptr", err_ptr);',
        '"phase3-errptr-xarray-dump"',
    ),
    C_HARNESS_PATH: (
        "#define MAX_ERRNO ((uintptr_t)4095)",
        "static uintptr_t err_floor(void) {",
        'return "xa_value";',
        'write_case("err_floor_plus_one", err_floor() + 1, 1);',
        'write_case("err_enomem", (uintptr_t)(intptr_t)-12, 0);',
    ),
    EXPECTED_PATH: (
        '"word_bits": 64',
        '"safe_inline_limit_raw_hex": "0xffffffffffffefff"',
        '"name": "err_floor_plus_one"',
        '"raw_hex": "0xfffffffffffff002"',
        '"decoded_error": -4094',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-errptr-xarray"',
        '"status": "parity_packet_present"',
        '"zigux/tests/phase3_errptr_xarray_dump.zig"',
        '"zigux/tests/phase3_errptr_xarray_dump_build.zig"',
        '"zigux/tests/fixtures/phase3_errptr_xarray/expected.json"',
        '"python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc"',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> object:
    return json.loads(_read(path))


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def _diff(label: str, expected: object, actual: object) -> str:
    expected_text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    actual_text = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    diff = "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            actual_text.splitlines(keepends=True),
            fromfile=f"{label}-expected",
            tofile=f"{label}-actual",
        )
    ).strip()
    return diff or f"{label} JSON differed without a textual diff"


def _run_zig_dump(repo_root: Path, zig: str) -> object:
    result = _run(
        [
            zig,
            "build",
            "phase3-errptr-xarray-dump",
            "--build-file",
            str(repo_root / DUMP_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "zig dump failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def _run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_errptr_xarray_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_errptr_xarray_c_harness"
        compile_result = _run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-o",
                str(binary),
                str(repo_root / C_HARNESS_PATH),
            ],
            cwd=repo_root,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "c harness compile failed:\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = _run([str(binary)], cwd=repo_root)
        if run_result.returncode != 0:
            raise RuntimeError(
                "c harness run failed:\n"
                f"stdout:\n{run_result.stdout}\n"
                f"stderr:\n{run_result.stderr}"
            )
        return json.loads(run_result.stdout)


def validate_repo(
    repo_root: Path,
    zig: str,
    cc: str,
    *,
    skip_exec: bool = False,
) -> list[str]:
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
            manifest = _load_json(manifest_path)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append("phase3_errptr_xarray_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_errptr_xarray_manifest.json replay_routes is not a list")
            if isinstance(packet_files, list):
                for required_path in (
                    "Documentation/zigux/phase3-errptr-xarray-slice.md",
                    "Documentation/zigux/phase3-validator-support-surface.md",
                    "zigux/helpers/err_ptr.zig",
                    "zigux/helpers/xa_value.zig",
                    "zigux/tests/phase3_errptr_xarray_dump.zig",
                    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
                    "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c",
                    "zigux/tests/fixtures/phase3_errptr_xarray/expected.json",
                    "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
                    "scripts/zigux/check-phase3-errptr-xarray.py",
                ):
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_errptr_xarray_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in (
                    "python3 scripts/zigux/check-phase3-errptr-xarray.py --self-test",
                    "python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc",
                    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
                ):
                    if route not in replay_routes:
                        issues.append(
                            "phase3_errptr_xarray_manifest.json missing replay route: "
                            f"{route}"
                        )

    if issues or skip_exec:
        return issues

    expected = _load_json(repo_root / EXPECTED_PATH)
    try:
        zig_actual = _run_zig_dump(repo_root, zig)
    except Exception as exc:  # pragma: no cover - surfaced to the caller
        issues.append(str(exc))
        return issues
    try:
        c_actual = _run_c_harness(repo_root, cc)
    except Exception as exc:  # pragma: no cover - surfaced to the caller
        issues.append(str(exc))
        return issues

    if zig_actual != expected:
        issues.append(_diff("zig-dump", expected, zig_actual))
    if c_actual != expected:
        issues.append(_diff("c-harness", expected, c_actual))
    if zig_actual != c_actual:
        issues.append(_diff("zig-vs-c", zig_actual, c_actual))

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        if relative_path == MANIFEST_PATH:
            continue
        _write(root / relative_path, "\n".join(markers) + "\n")
    _write(
        root / MANIFEST_PATH,
        """{
  "phase": "Phase 3",
  "lane": "helper-interop",
  "slug": "phase3-errptr-xarray",
  "status": "parity_packet_present",
  "scope": "fixture-backed err_ptr and xarray inline-value boundary parity dump",
  "packet_files": [
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zigux/tests/fixtures/phase3_errptr_xarray/phase3_errptr_xarray_c_harness.c",
    "zigux/tests/fixtures/phase3_errptr_xarray/expected.json",
    "zigux/tests/fixtures/phase3_errptr_xarray_manifest.json",
    "scripts/zigux/check-phase3-errptr-xarray.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-errptr-xarray.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig"
  ]
}
""",
    )


SELF_TEST_CASES = (
    (SLICE_PATH, "fixture-backed parity packet"),
    (VALIDATOR_NOTE_PATH, "zigux/tests/phase3_errptr_xarray_dump.zig"),
    (DUMP_PATH, '\\"safe_inline_limit_raw_hex\\"'),
    (C_HARNESS_PATH, 'write_case("err_floor_plus_one", err_floor() + 1, 1);'),
    (MANIFEST_PATH, '"status": "parity_packet_present"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_errptr_xarray_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
        if issues:
            print("PHASE3_ERRPTR_XARRAY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ERRPTR_XARRAY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_ERRPTR_XARRAY_SELF_TEST=pass")
    print(f"PHASE3_ERRPTR_XARRAY_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 err_ptr/xarray parity packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 err_ptr/xarray packet",
    )
    parser.add_argument("--zig", help="path to zig executable")
    parser.add_argument("--cc", help="path to C compiler")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, "ZIG", "zig")
    cc = _resolve_tool(args.cc, "CC", "gcc")
    issues = validate_repo(args.repo_root, zig, cc, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_ERRPTR_XARRAY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
