#!/usr/bin/env python3
"""Fail-close the current Phase 3 xarray-slot starter-plus-dump packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ERR_PTR_PATH = Path("zigux/helpers/err_ptr.zig")
XA_VALUE_PATH = Path("zigux/helpers/xa_value.zig")
HELPER_PATH = Path("zigux/helpers/xarray_slot_view.zig")
STARTER_TEST_PATH = Path("zigux/tests/phase3_xarray_slot_starter_packet.zig")
STARTER_BUILD_PATH = Path("zigux/tests/phase3_xarray_slot_starter_packet_build.zig")
STARTER_CHECK_PATH = Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")
DUMP_PATH = Path("zigux/tests/phase3_xarray_slot_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_xarray_slot_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_xarray_slot/expected.json")
C_HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c"
)
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_xarray_slot_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_MARKERS = {
    STARTER_CHECK_PATH: (
        "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass",
        "Validate the current Phase 3 xarray slot starter packet.",
    ),
    DUMP_PATH: (
        'const xarray_slot_view = @import("xarray_slot_view");',
        '.pointer => "pointer_like",',
        '\\"is_tagged_internal\\": {s}',
        'try writeCase(writer, "inline_zero", inline_zero_raw, true);',
        'try writeCase(writer, "inline_limit", inline_limit_raw, true);',
        'try writeCase(writer, "err_top", err_ptr.fromErrorCode(-1), true);',
        'try writeCase(writer, "err_max", err_ptr.fromErrorCode(-4095), false);',
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/xarray_slot_view.zig"),',
        '.root_source_file = b.path("phase3_xarray_slot_dump.zig"),',
        'xarray_slot_view.addImport("err_ptr", err_ptr);',
        'xarray_slot_view.addImport("xa_value", xa_value);',
        '"phase3-xarray-slot-dump"',
    ),
    MAKEFILE_PATH: (
        "phase3-xarray-slot-starter-packet:",
        "phase3-xarray-slot-starter-packet-test:",
        "phase3-xarray-slot-dump:",
        "$(ZIG) build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
        "$(ZIG) build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
        "$(ZIG) build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    ),
    C_HARNESS_PATH: (
        "#define MAX_ERRNO ((uintptr_t)4095)",
        "static const char *kind_name(uintptr_t raw) {",
        'return "pointer_like";',
        'write_case("inline_zero", make_value(0), 1);',
        'write_case("err_top", (uintptr_t)(intptr_t)-1, 1);',
        'write_case("err_max", (uintptr_t)(intptr_t)-4095, 0);',
    ),
    EXPECTED_PATH: (
        '"word_bits": 64',
        '"safe_inline_limit_raw_hex": "0xffffffffffffefff"',
        '"name": "inline_zero"',
        '"decoded_value": 0',
        '"name": "err_top"',
        '"decoded_error": -1',
        '"decoded_error": -4095',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-xarray-slot"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/Makefile"',
        '"zigux/tests/phase3_xarray_slot_dump.zig"',
        '"zigux/tests/phase3_xarray_slot_dump_build.zig"',
        '"zigux/tests/fixtures/phase3_xarray_slot/expected.json"',
        '"make -C zigux phase3-xarray-slot-starter-packet"',
        '"make -C zigux phase3-xarray-slot-starter-packet-test"',
        '"make -C zigux phase3-xarray-slot-dump"',
        '"python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc"',
    ),
}

REQUIRED_PACKET_FILES = (
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "zigux/Makefile",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --repo-root .",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "make -C zigux phase3-xarray-slot-starter-packet",
    "make -C zigux phase3-xarray-slot-starter-packet-test",
    "make -C zigux phase3-xarray-slot-dump",
)


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
    )
    return diff.strip() or f"{label} JSON differed without a textual diff"


def _run_starter_checker(repo_root: Path) -> None:
    result = _run(
        [sys.executable, str(repo_root / STARTER_CHECK_PATH), "--repo-root", str(repo_root)],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter checker failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _run_starter_build(repo_root: Path, zig: str) -> None:
    result = _run(
        [
            zig,
            "build",
            "phase3-xarray-slot-starter-packet-test",
            "--build-file",
            str(repo_root / STARTER_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter build failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _run_zig_dump(repo_root: Path, zig: str) -> object:
    result = _run(
        [
            zig,
            "build",
            "phase3-xarray-slot-dump",
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_xarray_slot_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_xarray_slot_c_harness"
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
                issues.append("phase3_xarray_slot_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_xarray_slot_manifest.json replay_routes is not a list")
            if isinstance(packet_files, list):
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_xarray_slot_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_xarray_slot_manifest.json missing replay route: "
                            f"{route}"
                        )

    if issues or skip_exec:
        return issues

    expected = _load_json(repo_root / EXPECTED_PATH)
    try:
        _run_starter_checker(repo_root)
        _run_starter_build(repo_root, zig)
        zig_actual = _run_zig_dump(repo_root, zig)
        c_actual = _run_c_harness(repo_root, cc)
    except Exception as exc:
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
        json.dumps(
            {
                "phase": "Phase 3",
                "lane": "helper-interop",
                "slug": "phase3-xarray-slot",
                "status": "starter_and_dump_packet_present",
                "scope": "helper-local xarray slot starter packet plus fixture-backed dump parity",
                "packet_files": list(REQUIRED_PACKET_FILES),
                "replay_routes": list(REQUIRED_REPLAY_ROUTES),
            },
            indent=2,
        )
        + "\n",
    )


SELF_TEST_CASES = (
    (STARTER_CHECK_PATH, "PHASE3_XARRAY_SLOT_STARTER_PACKET_SELF_TEST=pass"),
    (DUMP_PATH, 'try writeCase(writer, "inline_zero", inline_zero_raw, true);'),
    (MAKEFILE_PATH, "phase3-xarray-slot-dump:"),
    (C_HARNESS_PATH, 'write_case("err_max", (uintptr_t)(intptr_t)-4095, 0);'),
    (EXPECTED_PATH, '"decoded_error": -4095'),
    (MANIFEST_PATH, '"status": "starter_and_dump_packet_present"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_xarray_slot_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
        if issues:
            print("PHASE3_XARRAY_SLOT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_XARRAY_SLOT_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_XARRAY_SLOT_SELF_TEST=pass")
    print(f"PHASE3_XARRAY_SLOT_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 xarray-slot starter-plus-dump packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 xarray-slot packet",
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
        print("PHASE3_XARRAY_SLOT=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / STARTER_CHECK_PATH}")
    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
