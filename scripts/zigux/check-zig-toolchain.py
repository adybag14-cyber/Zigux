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


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:
    payload = load_policy(policy_path)
    if payload is None:
        return fallback
    min_version = payload.get("minimum_version")
    if not isinstance(min_version, str) or not min_version.strip():
        raise ValueError(f"invalid minimum_version in {policy_path}")
    return min_version.strip()


def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    payload = load_policy(policy_path)
    if payload is None:
        return None
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"invalid channel in {policy_path}")
    return channel.strip()


def read_zig_version(zig: str, *, runner=subprocess.run) -> str:
    try:
        completed = runner([zig, "version"], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise ValueError(f"zig executable not found: {zig}") from exc
    except OSError as exc:
        raise ValueError(f"failed to execute zig at {zig}: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise ValueError(f"zig version command failed: {detail}")

    version = completed.stdout.strip()
    if not version:
        raise ValueError("zig version command returned empty output")
    return version


def evaluate_toolchain_version(
    version: str,
    min_version_raw: str,
    expected_channel_raw: str | None = None,
) -> tuple[str, str | None]:
    parsed_version = parse_zig_version(version)
    min_version = parse_zig_version(min_version_raw)
    if parsed_version < min_version:
        return "too_old", None
    if expected_channel_raw is not None:
        expected_channel_raw = expected_channel_raw.strip()
        parse_zig_version(expected_channel_raw)
        if version.strip() != expected_channel_raw:
            return "not_pinned", f"expected pinned Zig channel {expected_channel_raw}"
    return "present", None


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

    expect_equal(
        evaluate_toolchain_version("0.17.0-dev.87+9b177a7d2", "0.17.0-dev.87+9b177a7d2"),
        ("present", None),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("present", None),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("not_pinned", "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0-dev.90+abcdef",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("not_pinned", "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.16.0",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("too_old", None),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_policy_") as tmp_dir:
        policy_path = Path(tmp_dir) / "zig-toolchain-policy.json"
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.15.0")
        expect_equal(load_pinned_channel(policy_path), None)
        policy_path.write_text(
            '{"channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2"}\n',
            encoding="utf-8",
        )
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.17.0-dev.87+9b177a7d2")
        expect_equal(load_pinned_channel(policy_path), "0.17.0-dev.87+9b177a7d2")
        policy_path.write_text('{"minimum_version":7,"channel":"0.17.0-dev.87+9b177a7d2"}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid minimum_version")
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":7}\n', encoding="utf-8")
        expect_raises(lambda: load_pinned_channel(policy_path), "invalid channel")
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid toolchain policy JSON")
        expect_raises(lambda: parse_zig_version("master"))

    expect_equal(
        read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                0,
                stdout="0.17.0-dev.87+9b177a7d2\n",
                stderr="",
            ),
        ),
        "0.17.0-dev.87+9b177a7d2",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/missing-zig",
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError("missing")),
        ),
        "zig executable not found",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                1,
                stdout="",
                stderr="permission denied\n",
            ),
        ),
        "zig version command failed: permission denied",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                0,
                stdout="\n",
                stderr="",
            ),
        ),
        "zig version command returned empty output",
    )

    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    print(f"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}")
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

    zig = args.zig or shutil.which("zig")
    if args.self_test:
        return run_self_test()

    if zig is None:
        message = "zig not found on PATH"
        if args.allow_missing:
            print("ZIG_TOOLCHAIN_STATUS=missing")
            print(f"ZIG_TOOLCHAIN_NOTE={message}")
            return 0
        print(message, file=sys.stderr)
        return 1

    version: str | None = None
    try:
        min_version_raw = args.min_version or load_min_version()
        expected_channel_raw = None if args.min_version else load_pinned_channel()
        parse_zig_version(min_version_raw)
        if expected_channel_raw is not None:
            parse_zig_version(expected_channel_raw)
        version = read_zig_version(zig)
        status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig}")
        if version is not None:
            print(f"ZIG_TOOLCHAIN_VERSION={version}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={args.min_version or load_min_version()}")
        if args.min_version is None:
            expected_channel_raw = load_pinned_channel()
            if expected_channel_raw is not None:
                print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
                print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
            else:
                print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        else:
            print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    exit_code = 0 if status == "present" else 1
    print(f"ZIG_TOOLCHAIN_STATUS={status}")
    print(f"ZIG_TOOLCHAIN_PATH={zig}")
    print(f"ZIG_TOOLCHAIN_VERSION={version}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    if expected_channel_raw is not None:
        print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
        print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
    else:
        print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
    if note is not None:
        print(f"ZIG_TOOLCHAIN_NOTE={note}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
