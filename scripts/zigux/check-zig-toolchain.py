#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-dev\.(?P<dev>\d+)(?:\+[0-9A-Za-z.-]+)?)?$")

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FALLBACK_MIN_VERSION = "0.16.0"


@dataclass(frozen=True, order=True)
class ZigVersion:
    major: int
    minor: int
    patch: int
    release_rank: int
    dev_build: int


def parse_zig_version(raw: str) -> ZigVersion:
    match = VERSION_RE.fullmatch(raw.strip())
    if match is None:
        raise ValueError(f"unsupported Zig version string: {raw!r}")
    dev_build = match.group("dev")
    return ZigVersion(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        release_rank=1 if dev_build is None else 0,
        dev_build=int(dev_build) if dev_build is not None else 0,
    )


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object]:
    if not policy_path.exists():
        return {}
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy object in {policy_path}")
    return payload


def load_version_requirements(
    policy_path: Path = TOOLCHAIN_POLICY,
    fallback: str = FALLBACK_MIN_VERSION,
) -> tuple[str, str | None]:
    payload = load_policy(policy_path)
    if not payload:
        return fallback, None

    min_version = payload.get("minimum_version")
    if not isinstance(min_version, str) or not min_version.strip():
        raise ValueError(f"invalid minimum_version in {policy_path}")

    channel = payload.get("channel")
    exact_version: str | None = None
    if channel is not None:
        if not isinstance(channel, str) or not channel.strip():
            raise ValueError(f"invalid channel in {policy_path}")
        exact_version = channel.strip()

    return min_version.strip(), exact_version


def run_self_test() -> int:
    case_count = 0

    def expect_equal(actual, expected) -> None:
        nonlocal case_count
        assert actual == expected
        case_count += 1

    def expect_true(condition: bool) -> None:
        nonlocal case_count
        assert condition
        case_count += 1

    def expect_raises(fn, expected_substring: str | None = None) -> None:
        nonlocal case_count
        try:
            fn()
        except ValueError as exc:
            if expected_substring is not None:
                assert expected_substring in str(exc)
            case_count += 1
            return
        raise AssertionError("expected ValueError to fail")

    expect_equal(parse_zig_version("0.16.0"), ZigVersion(0, 16, 0, 1, 0))
    expect_equal(parse_zig_version("0.17.0-dev.87+9b177a7d2"), ZigVersion(0, 17, 0, 0, 87))
    expect_true(parse_zig_version("0.17.0-dev.90") > parse_zig_version("0.17.0-dev.87+9b177a7d2"))
    expect_true(parse_zig_version("0.17.0") > parse_zig_version("0.17.0-dev.999+abcdef"))
    expect_true(parse_zig_version("0.17.1-dev.1") > parse_zig_version("0.17.0"))
    expect_true(parse_zig_version("0.16.0") > parse_zig_version("0.15.2"))
    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_policy_") as tmp_dir:
        policy_path = Path(tmp_dir) / "zig-toolchain-policy.json"
        expect_equal(load_policy(policy_path), {})
        expect_equal(load_version_requirements(policy_path, "0.15.0"), ("0.15.0", None))
        policy_path.write_text(
            '{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2"}\n',
            encoding="utf-8",
        )
        expect_equal(
            load_version_requirements(policy_path, "0.15.0"),
            ("0.17.0-dev.87+9b177a7d2", "0.17.0-dev.87+9b177a7d2"),
        )
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2"}\n', encoding="utf-8")
        expect_equal(load_version_requirements(policy_path, "0.15.0"), ("0.17.0-dev.87+9b177a7d2", None))
        policy_path.write_text('{"minimum_version":7}\n', encoding="utf-8")
        expect_raises(lambda: load_version_requirements(policy_path, "0.15.0"), "invalid minimum_version")
        policy_path.write_text('{"minimum_version":"0.17.0","channel":7}\n', encoding="utf-8")
        expect_raises(lambda: load_version_requirements(policy_path, "0.15.0"), "invalid channel")
        policy_path.write_text("[]\n", encoding="utf-8")
        expect_raises(lambda: load_version_requirements(policy_path, "0.15.0"), "invalid toolchain policy object")
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        expect_raises(lambda: load_version_requirements(policy_path, "0.15.0"), "invalid toolchain policy JSON")
    expect_raises(lambda: parse_zig_version("master"))
    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    print(f"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")
    parser.add_argument(
        "--min-version",
        help="Minimum supported Zig version string. Defaults to scripts/zigux/zig-toolchain-policy.json when available.",
    )
    parser.add_argument(
        "--exact-version",
        help="Require an exact Zig version string. Defaults to the pinned channel in scripts/zigux/zig-toolchain-policy.json when available.",
    )
    parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = args.zig or shutil.which("zig")
    if zig is None:
        message = "zig not found on PATH"
        if args.allow_missing:
            print("ZIG_TOOLCHAIN_STATUS=missing")
            print(f"ZIG_TOOLCHAIN_NOTE={message}")
            return 0
        print(message, file=sys.stderr)
        return 1

    try:
        policy_min_version_raw, policy_exact_version_raw = load_version_requirements()
        min_version_raw = args.min_version or policy_min_version_raw
        exact_version_raw = args.exact_version if args.exact_version is not None else policy_exact_version_raw
        min_version = parse_zig_version(min_version_raw)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = subprocess.run([zig, "version"], capture_output=True, text=True, check=True)
    version = result.stdout.strip()
    try:
        parsed_version = parse_zig_version(version)
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig}")
        print(f"ZIG_TOOLCHAIN_VERSION={version}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
        if exact_version_raw is not None:
            print(f"ZIG_TOOLCHAIN_EXPECTED_VERSION={exact_version_raw}")
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    status = "present"
    exit_code = 0
    if parsed_version < min_version:
        status = "too_old"
        exit_code = 1
    elif exact_version_raw is not None and version != exact_version_raw:
        status = "mismatch"
        exit_code = 1

    print(f"ZIG_TOOLCHAIN_STATUS={status}")
    print(f"ZIG_TOOLCHAIN_PATH={zig}")
    print(f"ZIG_TOOLCHAIN_VERSION={version}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    if exact_version_raw is not None:
        print(f"ZIG_TOOLCHAIN_EXPECTED_VERSION={exact_version_raw}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
