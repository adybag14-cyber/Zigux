#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-dev\.(?P<dev>\d+)(?:\+[0-9A-Za-z.-]+)?)?$")


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


def parse_policy_data(raw: object) -> tuple[str, str]:
    if not isinstance(raw, dict):
        raise ValueError("toolchain policy must be a JSON object")

    channel = raw.get("channel")
    minimum_version = raw.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        raise ValueError("toolchain policy must define a non-empty string channel")
    if not isinstance(minimum_version, str) or not minimum_version:
        raise ValueError("toolchain policy must define a non-empty string minimum_version")

    parse_zig_version(channel)
    parse_zig_version(minimum_version)
    return channel, minimum_version


def load_policy(path: Path) -> tuple[str, str]:
    return parse_policy_data(json.loads(path.read_text(encoding="utf-8")))


def run_self_test() -> int:
    assert parse_zig_version("0.16.0") == ZigVersion(0, 16, 0, 1, 0)
    assert parse_zig_version("0.17.0-dev.87+9b177a7d2") == ZigVersion(0, 17, 0, 0, 87)
    assert parse_zig_version("0.17.0-dev.90") > parse_zig_version("0.17.0-dev.87+9b177a7d2")
    assert parse_zig_version("0.17.0") > parse_zig_version("0.17.0-dev.999+abcdef")
    assert parse_zig_version("0.17.1-dev.1") > parse_zig_version("0.17.0")
    assert parse_policy_data(
        {
            "channel": "0.17.0-dev.87+9b177a7d2",
            "minimum_version": "0.17.0-dev.87+9b177a7d2",
        }
    ) == ("0.17.0-dev.87+9b177a7d2", "0.17.0-dev.87+9b177a7d2")
    try:
        parse_zig_version("master")
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid version string to fail")
    try:
        parse_policy_data({"channel": "master", "minimum_version": "0.17.0-dev.87+9b177a7d2"})
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid policy channel to fail")
    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")
    parser.add_argument("--min-version", help="Minimum supported Zig version string.")
    parser.add_argument("--exact-version", help="Require an exact Zig version string.")
    parser.add_argument("--policy", help="Toolchain policy JSON path. Defaults to scripts/zigux/zig-toolchain-policy.json.")
    parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    policy_path = Path(args.policy) if args.policy else DEFAULT_POLICY
    policy_channel = None
    policy_minimum_version = None
    if policy_path.exists():
        try:
            policy_channel, policy_minimum_version = load_policy(policy_path)
        except ValueError as exc:
            print(f"invalid toolchain policy {policy_path}: {exc}", file=sys.stderr)
            return 1
    elif args.policy:
        print(f"toolchain policy not found: {policy_path}", file=sys.stderr)
        return 1

    exact_version = args.exact_version or policy_channel
    min_version_raw = args.min_version or policy_minimum_version or exact_version or "0.16.0"

    zig = args.zig or shutil.which("zig")
    if zig is None:
        message = "zig not found on PATH"
        if args.allow_missing:
            print("ZIG_TOOLCHAIN_STATUS=missing")
            print(f"ZIG_TOOLCHAIN_NOTE={message}")
            if policy_channel:
                print(f"ZIG_TOOLCHAIN_POLICY={policy_path}")
                print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
            print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
            return 0
        print(message, file=sys.stderr)
        return 1

    min_version = parse_zig_version(min_version_raw)
    result = subprocess.run([zig, "version"], capture_output=True, text=True, check=True)
    version = result.stdout.strip()
    try:
        parsed_version = parse_zig_version(version)
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig}")
        print(f"ZIG_TOOLCHAIN_VERSION={version}")
        if policy_channel:
            print(f"ZIG_TOOLCHAIN_POLICY={policy_path}")
            print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    status = "present"
    exit_code = 0
    if parsed_version < min_version:
        status = "too_old"
        exit_code = 1
    elif exact_version is not None and version != exact_version:
        status = "not_pinned"
        exit_code = 1

    print(f"ZIG_TOOLCHAIN_STATUS={status}")
    print(f"ZIG_TOOLCHAIN_PATH={zig}")
    print(f"ZIG_TOOLCHAIN_VERSION={version}")
    if policy_channel:
        print(f"ZIG_TOOLCHAIN_POLICY={policy_path}")
        print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
