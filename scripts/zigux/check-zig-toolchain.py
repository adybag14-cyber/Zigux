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


def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:
    if not policy_path.exists():
        return fallback
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    min_version = payload.get("minimum_version")
    if not isinstance(min_version, str) or not min_version.strip():
        raise ValueError(f"invalid minimum_version in {policy_path}")
    return min_version.strip()


def run_self_test() -> int:
    assert parse_zig_version("0.16.0") == ZigVersion(0, 16, 0, 1, 0)
    assert parse_zig_version("0.17.0-dev.87+9b177a7d2") == ZigVersion(0, 17, 0, 0, 87)
    assert parse_zig_version("0.17.0-dev.90") > parse_zig_version("0.17.0-dev.87+9b177a7d2")
    assert parse_zig_version("0.17.0") > parse_zig_version("0.17.0-dev.999+abcdef")
    assert parse_zig_version("0.17.1-dev.1") > parse_zig_version("0.17.0")
    assert parse_zig_version("0.16.0") > parse_zig_version("0.15.2")
    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_policy_") as tmp_dir:
        policy_path = Path(tmp_dir) / "zig-toolchain-policy.json"
        assert load_min_version(policy_path, "0.15.0") == "0.15.0"
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2"}\n', encoding="utf-8")
        assert load_min_version(policy_path, "0.15.0") == "0.17.0-dev.87+9b177a7d2"
        policy_path.write_text('{"minimum_version":7}\n', encoding="utf-8")
        try:
            load_min_version(policy_path, "0.15.0")
        except ValueError as exc:
            assert "invalid minimum_version" in str(exc)
        else:
            raise AssertionError("expected invalid minimum_version to fail")
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        try:
            load_min_version(policy_path, "0.15.0")
        except ValueError as exc:
            assert "invalid toolchain policy JSON" in str(exc)
        else:
            raise AssertionError("expected invalid JSON policy to fail")
    try:
        parse_zig_version("master")
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid version string to fail")
    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")
    parser.add_argument(
        "--min-version",
        help="Minimum supported Zig version string. Defaults to scripts/zigux/zig-toolchain-policy.json when available.",
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
        min_version_raw = args.min_version or load_min_version()
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
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    status = "present"
    exit_code = 0
    if parsed_version < min_version:
        status = "too_old"
        exit_code = 1

    print(f"ZIG_TOOLCHAIN_STATUS={status}")
    print(f"ZIG_TOOLCHAIN_PATH={zig}")
    print(f"ZIG_TOOLCHAIN_VERSION={version}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
