#!/usr/bin/env python3
"""Validate the current Phase 3 ABI dump route against its expected snapshot."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


BUILD_PATH = Path("zigux/tests/build.zig")
DUMP_PATH = Path("zigux/tests/phase3_abi_dump_current.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_abi/expected.json")
REQUIRED_TOP_LEVEL_KEYS = (
    "abi_version",
    "boundary_header",
    "export_status",
    "interop_policy",
    "panic_mode",
    "allocator_mode",
    "unsafe_scope",
    "facility",
    "notifier",
)


def _read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_payload(payload: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(payload, dict):
        return ["payload is not a JSON object"]

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in payload:
            issues.append(f"missing top-level key: {key}")

    abi_version = payload.get("abi_version")
    if abi_version != 1:
        issues.append(f"unexpected abi_version: {abi_version!r}")

    boundary_header = payload.get("boundary_header")
    if isinstance(boundary_header, dict):
        compatibility = boundary_header.get("compatibility")
        if not isinstance(compatibility, dict):
            issues.append("boundary_header.compatibility is missing or invalid")
        else:
            for key in ("canonical", "size_matches", "version_matches"):
                if compatibility.get(key) is not True:
                    issues.append(f"boundary_header.compatibility.{key} is not true")
    else:
        issues.append("boundary_header is missing or invalid")

    interop_policy = payload.get("interop_policy")
    if isinstance(interop_policy, dict):
        default_policy = interop_policy.get("default")
        if not isinstance(default_policy, dict):
            issues.append("interop_policy.default is missing or invalid")
        else:
            expected_default = {
                "panic_mode": 0,
                "allocator_mode": 0,
                "unsafe_scope": 0,
                "reserved": 0,
            }
            for key, expected in expected_default.items():
                if default_policy.get(key) != expected:
                    issues.append(
                        f"interop_policy.default.{key} expected {expected}, found {default_policy.get(key)!r}"
                    )
    else:
        issues.append("interop_policy is missing or invalid")

    return issues


def _compare_payloads(expected: object, actual: object) -> list[str]:
    issues: list[str] = []
    issues.extend(_validate_payload(expected))
    issues.extend(_validate_payload(actual))
    if issues:
        return issues

    if expected != actual:
        issues.append("actual dump JSON does not match expected snapshot")
    return issues


def _run_dump(repo_root: Path, zig: str) -> object:
    if not (repo_root / BUILD_PATH).is_file():
        raise FileNotFoundError(f"missing repo file: {BUILD_PATH.as_posix()}")
    if not (repo_root / DUMP_PATH).is_file():
        raise FileNotFoundError(f"missing repo file: {DUMP_PATH.as_posix()}")

    result = subprocess.run(
        [zig, "build", "phase3-dump", "--build-file", str(BUILD_PATH)],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_self_test() -> int:
    good_payload = {
        "abi_version": 1,
        "boundary_header": {
            "compatibility": {
                "canonical": True,
                "size_matches": True,
                "version_matches": True,
            }
        },
        "export_status": {},
        "interop_policy": {
            "default": {
                "panic_mode": 0,
                "allocator_mode": 0,
                "unsafe_scope": 0,
                "reserved": 0,
            }
        },
        "panic_mode": {},
        "allocator_mode": {},
        "unsafe_scope": {},
        "facility": {},
        "notifier": {},
    }

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_dump_gate_") as temp_dir:
        root = Path(temp_dir)
        expected_path = root / "expected.json"
        actual_path = root / "actual.json"
        expected_path.write_text(json.dumps(good_payload, indent=2) + "\n", encoding="utf-8")
        actual_path.write_text(json.dumps(good_payload, indent=2) + "\n", encoding="utf-8")

        issues = _compare_payloads(_read_json(expected_path), _read_json(actual_path))
        if issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        bad_payload = dict(good_payload)
        bad_payload.pop("notifier")
        actual_path.write_text(json.dumps(bad_payload, indent=2) + "\n", encoding="utf-8")
        issues = _compare_payloads(_read_json(expected_path), _read_json(actual_path))
        if "missing top-level key: notifier" not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected missing notifier key was not reported")
            return 1

        actual_path.write_text(json.dumps(good_payload | {"abi_version": 2}, indent=2) + "\n", encoding="utf-8")
        issues = _compare_payloads(_read_json(expected_path), _read_json(actual_path))
        if "unexpected abi_version: 2" not in issues:
            print("PHASE3_ABI_DUMP_GATE_SELF_TEST=fail")
            print("expected abi_version mismatch was not reported")
            return 1

    print("PHASE3_ABI_DUMP_GATE_SELF_TEST=pass")
    print("PHASE3_ABI_DUMP_GATE_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ABI dump route against its expected snapshot."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/tests/build.zig",
    )
    parser.add_argument(
        "--expected",
        type=Path,
        default=EXPECTED_PATH,
        help="expected JSON snapshot path, relative to --repo-root by default",
    )
    parser.add_argument(
        "--actual-json",
        type=Path,
        help="compare a precomputed dump JSON file instead of invoking zig build",
    )
    parser.add_argument(
        "--zig",
        default="zig",
        help="zig executable to use when invoking the dump route",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = args.repo_root
    expected_path = args.expected if args.expected.is_absolute() else repo_root / args.expected
    if not expected_path.is_file():
        print("PHASE3_ABI_DUMP_GATE=fail")
        print(f"missing repo file: {expected_path.relative_to(repo_root).as_posix()}")
        return 1

    expected = _read_json(expected_path)
    try:
        if args.actual_json is not None:
            actual = _read_json(args.actual_json)
        else:
            actual = _run_dump(repo_root, args.zig)
    except FileNotFoundError as exc:
        print("PHASE3_ABI_DUMP_GATE=fail")
        print(str(exc))
        return 1
    except subprocess.CalledProcessError as exc:
        print("PHASE3_ABI_DUMP_GATE=fail")
        stderr = exc.stderr.strip()
        if stderr:
            print(stderr)
        return exc.returncode or 1

    issues = _compare_payloads(expected, actual)
    if issues:
        print("PHASE3_ABI_DUMP_GATE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ABI_DUMP_GATE=pass")
    print(f"PHASE3_ABI_DUMP_GATE_TOP_LEVEL_KEY_COUNT={len(REQUIRED_TOP_LEVEL_KEYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
