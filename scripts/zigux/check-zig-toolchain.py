#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
DEFAULT_POLICY_PHASE = "Phase 2"
VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-dev\.(?P<dev>\d+)(?:\+[0-9A-Za-z.-]+)?)?$")
ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def normalize_os(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith("linux"):
        return "linux"
    if lowered.startswith("darwin") or lowered.startswith("mac"):
        return "macos"
    if lowered.startswith("windows"):
        return "windows"
    raise ValueError(f"unsupported OS for Zig toolchain policy: {name}")


def normalize_arch(name: str) -> str:
    lowered = name.lower()
    if lowered in {"amd64", "x86_64", "x64"}:
        return "x86_64"
    if lowered in {"arm64", "aarch64"}:
        return "aarch64"
    if lowered in {"x86", "i386", "i686"}:
        return "x86"
    if lowered in {"riscv64", "rv64"}:
        return "riscv64"
    raise ValueError(f"unsupported architecture for Zig toolchain policy: {name}")


def parse_archive_sha256(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        raise ValueError("toolchain policy must define a non-empty archive_sha256 object")

    normalized: dict[str, str] = {}
    for target_key, digest in raw.items():
        if not isinstance(target_key, str) or not target_key:
            raise ValueError("toolchain policy archive_sha256 keys must be non-empty target strings")
        if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
            raise ValueError(
                f"toolchain policy archive_sha256 entry for {target_key!r} must be a 64-character hex string"
            )
        normalized[target_key] = digest.lower()
    return normalized


def parse_policy_data(raw: object) -> tuple[str, str, str, str, dict[str, str]]:
    if not isinstance(raw, dict):
        raise ValueError("toolchain policy must be a JSON object")

    phase = raw.get("phase")
    channel = raw.get("channel")
    minimum_version = raw.get("minimum_version")
    policy_note = raw.get("policy_note")
    if not isinstance(phase, str) or not phase:
        raise ValueError("toolchain policy must define a non-empty string phase")
    if not isinstance(channel, str) or not channel:
        raise ValueError("toolchain policy must define a non-empty string channel")
    if not isinstance(minimum_version, str) or not minimum_version:
        raise ValueError("toolchain policy must define a non-empty string minimum_version")
    if not isinstance(policy_note, str) or not policy_note:
        raise ValueError("toolchain policy must define a non-empty string policy_note")

    parsed_channel = parse_zig_version(channel)
    parsed_minimum = parse_zig_version(minimum_version)
    if parsed_minimum > parsed_channel:
        raise ValueError("toolchain policy minimum_version must not be newer than channel")

    archive_sha256 = parse_archive_sha256(raw.get("archive_sha256"))
    return phase, channel, minimum_version, policy_note, archive_sha256


def load_policy(path: Path) -> tuple[str, str, str, str, dict[str, str]]:
    phase, channel, minimum_version, policy_note, archive_sha256 = parse_policy_data(
        json.loads(path.read_text(encoding="utf-8"))
    )
    if path == DEFAULT_POLICY and phase != DEFAULT_POLICY_PHASE:
        raise ValueError(
            f"default toolchain policy phase must stay {DEFAULT_POLICY_PHASE!r}, got {phase!r}"
        )
    return phase, channel, minimum_version, policy_note, archive_sha256


def resolve_target_key(system_name: str, arch_name: str) -> str:
    return f"{normalize_arch(arch_name)}-{normalize_os(system_name)}"


def run_self_test() -> int:
    assert parse_zig_version("0.16.0") == ZigVersion(0, 16, 0, 1, 0)
    assert parse_zig_version("0.17.0-dev.87+9b177a7d2") == ZigVersion(0, 17, 0, 0, 87)
    assert parse_zig_version("0.17.0-dev.90") > parse_zig_version("0.17.0-dev.87+9b177a7d2")
    assert parse_zig_version("0.17.0") > parse_zig_version("0.17.0-dev.999+abcdef")
    assert parse_zig_version("0.17.1-dev.1") > parse_zig_version("0.17.0")
    assert normalize_os("Linux") == "linux"
    assert normalize_os("Darwin") == "macos"
    assert normalize_os("Windows_NT") == "windows"
    assert normalize_arch("amd64") == "x86_64"
    assert normalize_arch("aarch64") == "aarch64"
    assert normalize_arch("riscv64") == "riscv64"
    assert resolve_target_key("Linux", "x86_64") == "x86_64-linux"
    assert parse_policy_data(
        {
            "phase": "Phase 2",
            "channel": "0.17.0-dev.87+9b177a7d2",
            "minimum_version": "0.17.0-dev.87+9b177a7d2",
            "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
            "archive_sha256": {
                "x86_64-linux": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "aarch64-macos": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            },
        }
    ) == (
        "Phase 2",
        "0.17.0-dev.87+9b177a7d2",
        "0.17.0-dev.87+9b177a7d2",
        "Shared Zigux bootstrap and Phase 2 toolchain pin.",
        {
            "x86_64-linux": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "aarch64-macos": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        },
    )
    default_phase, default_channel, default_minimum_version, default_policy_note, default_archive_sha256 = load_policy(
        DEFAULT_POLICY
    )
    assert default_phase == DEFAULT_POLICY_PHASE
    assert default_channel == default_minimum_version
    assert default_policy_note == "Shared Zigux bootstrap and Phase 2 toolchain pin."
    assert resolve_target_key("Linux", "x86_64") in default_archive_sha256
    try:
        parse_zig_version("master")
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid version string to fail")
    try:
        parse_policy_data(
            {
                "phase": "",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected empty policy phase to fail")
    try:
        parse_policy_data(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.88+9b177a7d2",
                "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected newer minimum version to fail")
    try:
        parse_policy_data(
            {
                "phase": "Phase 2",
                "channel": "master",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid policy channel to fail")
    try:
        parse_policy_data(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected empty policy note to fail")
    try:
        parse_policy_data(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
                "archive_sha256": {},
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected empty archive sha map to fail")
    try:
        parse_policy_data(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "policy_note": "Shared Zigux bootstrap and Phase 2 toolchain pin.",
                "archive_sha256": {"x86_64-linux": "not-a-digest"},
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected invalid archive digest to fail")
    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")
    parser.add_argument("--min-version", help="Minimum supported Zig version string.")
    parser.add_argument("--exact-version", help="Require an exact Zig version string.")
    parser.add_argument("--policy", help="Toolchain policy JSON path. Defaults to scripts/zigux/zig-toolchain-policy.json.")
    parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
    parser.add_argument("--system", help="Override detected OS key when checking the policy target.")
    parser.add_argument("--arch", help="Override detected architecture key when checking the policy target.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    policy_path = Path(args.policy) if args.policy else DEFAULT_POLICY
    policy_phase = None
    policy_channel = None
    policy_minimum_version = None
    policy_note = None
    policy_archive_sha256: dict[str, str] = {}
    if policy_path.exists():
        try:
            (
                policy_phase,
                policy_channel,
                policy_minimum_version,
                policy_note,
                policy_archive_sha256,
            ) = load_policy(policy_path)
        except ValueError as exc:
            print(f"invalid toolchain policy {policy_path}: {exc}", file=sys.stderr)
            return 1
    elif args.policy:
        print(f"toolchain policy not found: {policy_path}", file=sys.stderr)
        return 1

    target_key = None
    expected_sha256 = None
    if policy_channel is not None:
        try:
            target_key = resolve_target_key(args.system or platform.system(), args.arch or platform.machine())
        except ValueError as exc:
            print(f"invalid toolchain policy target detection: {exc}", file=sys.stderr)
            return 1
        expected_sha256 = policy_archive_sha256.get(target_key)
        if expected_sha256 is None:
            print(
                f"toolchain policy missing archive sha256 for host target {target_key} in {policy_path}",
                file=sys.stderr,
            )
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
                print(f"ZIG_TOOLCHAIN_POLICY_PHASE={policy_phase}")
                print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
                print(f"ZIG_TOOLCHAIN_POLICY_NOTE={policy_note}")
                print(f"ZIG_TOOLCHAIN_TARGET={target_key}")
                print(f"ZIG_TOOLCHAIN_EXPECTED_SHA256={expected_sha256}")
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
            print(f"ZIG_TOOLCHAIN_POLICY_PHASE={policy_phase}")
            print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
            print(f"ZIG_TOOLCHAIN_POLICY_NOTE={policy_note}")
            print(f"ZIG_TOOLCHAIN_TARGET={target_key}")
            print(f"ZIG_TOOLCHAIN_EXPECTED_SHA256={expected_sha256}")
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
        print(f"ZIG_TOOLCHAIN_POLICY_PHASE={policy_phase}")
        print(f"ZIG_TOOLCHAIN_REQUIRED_VERSION={policy_channel}")
        print(f"ZIG_TOOLCHAIN_POLICY_NOTE={policy_note}")
        print(f"ZIG_TOOLCHAIN_TARGET={target_key}")
        print(f"ZIG_TOOLCHAIN_EXPECTED_SHA256={expected_sha256}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())