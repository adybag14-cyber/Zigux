#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 install-zig resolve-only packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALLER_PATH = Path("scripts/zigux/install-zig.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

RESOLVE_ONLY_FLAG = "parser.add_argument('--resolve-only', action='store_true'"
SELF_TEST_FLAG = "parser.add_argument('--self-test', action='store_true'"
POLICY_CHANNEL = "policy_channel = load_policy_channel()"
CHANNEL_ASSIGNMENT = "channel = args.channel or policy_channel"
TARGET_RESOLUTION = "target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)"
SHA_GUARD = "if channel == policy_channel:"
SHA_LOAD = "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)"
PRINT_CHANNEL = "print(f'ZIG_INSTALL_CHANNEL={channel}')"
PRINT_VERSION = "print(f'ZIG_INSTALL_VERSION={version}')"
PRINT_TARGET = "print(f'ZIG_INSTALL_TARGET={target_key}')"
PRINT_URL = "print(f'ZIG_INSTALL_URL={tarball_url}')"
PRINT_EXPECTED_SHA = "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')"
RESOLVE_ONLY_BRANCH = "if args.resolve_only:"
RESOLVED_STATUS = "print('ZIG_INSTALL_STATUS=resolved')"
DOWNLOAD_BLOCK = "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig resolve checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig resolve checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig resolve checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig resolve checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_installer(text: str) -> int:
    for marker, label in (
        (RESOLVE_ONLY_FLAG, "resolve-only flag"),
        (SELF_TEST_FLAG, "self-test flag"),
        (POLICY_CHANNEL, "policy-channel load"),
        (CHANNEL_ASSIGNMENT, "channel assignment"),
        (TARGET_RESOLUTION, "target resolution"),
        (SHA_GUARD, "policy sha guard"),
        (SHA_LOAD, "policy sha lookup"),
        (PRINT_CHANNEL, "channel output"),
        (PRINT_VERSION, "version output"),
        (PRINT_TARGET, "target output"),
        (PRINT_URL, "url output"),
        (PRINT_EXPECTED_SHA, "expected archive sha output"),
        (RESOLVE_ONLY_BRANCH, "resolve-only branch"),
        (RESOLVED_STATUS, "resolved status output"),
        (DOWNLOAD_BLOCK, "download block"),
    ):
        require_marker(text, marker, label)

    require_exact_count(text, RESOLVE_ONLY_FLAG, 1, "resolve-only flag")
    require_exact_count(text, RESOLVED_STATUS, 1, "resolved status output")
    require_exact_count(text, DOWNLOAD_BLOCK, 1, "download block")

    require_order(text, RESOLVE_ONLY_FLAG, SELF_TEST_FLAG, "argument order")
    require_order(text, POLICY_CHANNEL, CHANNEL_ASSIGNMENT, "policy channel flow")
    require_order(text, CHANNEL_ASSIGNMENT, TARGET_RESOLUTION, "resolution flow")
    require_order(text, SHA_GUARD, SHA_LOAD, "sha lookup flow")
    require_order(text, PRINT_CHANNEL, PRINT_VERSION, "summary output order")
    require_order(text, PRINT_VERSION, PRINT_TARGET, "summary output order")
    require_order(text, PRINT_TARGET, PRINT_URL, "summary output order")
    require_order(text, PRINT_URL, RESOLVE_ONLY_BRANCH, "resolve-only handoff")
    require_order(text, PRINT_EXPECTED_SHA, RESOLVE_ONLY_BRANCH, "sha-before-resolve handoff")
    require_order(text, RESOLVE_ONLY_BRANCH, RESOLVED_STATUS, "resolve-only status flow")
    require_order(text, RESOLVED_STATUS, DOWNLOAD_BLOCK, "resolved-before-download flow")

    return sum(
        text.count(marker)
        for marker in (
            RESOLVE_ONLY_FLAG,
            SHA_LOAD,
            PRINT_CHANNEL,
            PRINT_VERSION,
            PRINT_TARGET,
            PRINT_URL,
            PRINT_EXPECTED_SHA,
            RESOLVED_STATUS,
        )
    )


def check_policy(text: str) -> tuple[str, str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"lane05 install-zig resolve checker found invalid policy JSON: {exc.msg}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit("lane05 install-zig resolve checker expected policy object")
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel:
        raise SystemExit("lane05 install-zig resolve checker missing policy channel")
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        raise SystemExit("lane05 install-zig resolve checker missing archive_sha256 map")
    target = archive_sha256.get("x86_64-linux")
    if not isinstance(target, str) or len(target) != 64:
        raise SystemExit(
            "lane05 install-zig resolve checker missing pinned x86_64-linux archive digest"
        )
    return channel, target


def write_sample_root(root: Path) -> None:
    installer_path = root / INSTALLER_PATH
    installer_path.parent.mkdir(parents=True, exist_ok=True)
    installer_path.write_text(
        """#!/usr/bin/env python3
import argparse
import tempfile

def load_policy_channel():
    return '0.17.0-dev.87+9b177a7d2'

def load_policy_archive_sha256(path, target_key):
    del path
    if target_key == 'x86_64-linux':
        return '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'
    return None

def resolve_target(index, channel, arch_key, system_key):
    del index, channel, arch_key, system_key
    return 'x86_64-linux', '0.17.0-dev.87+9b177a7d2', 'https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resolve-only', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--channel', default=None)
    args = parser.parse_args()
    if args.self_test:
        return 0
    policy_channel = load_policy_channel()
    channel = args.channel or policy_channel
    index = {}
    arch_key = 'x86_64'
    system_key = 'linux'
    target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)
    expected_archive_sha256 = None
    if channel == policy_channel:
        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)
    print(f'ZIG_INSTALL_CHANNEL={channel}')
    print(f'ZIG_INSTALL_VERSION={version}')
    print(f'ZIG_INSTALL_TARGET={target_key}')
    print(f'ZIG_INSTALL_URL={tarball_url}')
    if expected_archive_sha256 is not None:
        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')
    if args.resolve_only:
        print('ZIG_INSTALL_STATUS=resolved')
        return 0
    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:
        print(tmpdir_str)
    return 0
""",
        encoding="utf-8",
    )

    policy_path = root / POLICY_PATH
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(
        """{
  \"channel\": \"0.17.0-dev.87+9b177a7d2\",
  \"archive_sha256\": {
    \"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"
  }
}
""",
        encoding="utf-8",
    )


def run_self_test() -> int:
    good_installer = """#!/usr/bin/env python3
import argparse
import tempfile
parser = argparse.ArgumentParser()
parser.add_argument('--resolve-only', action='store_true')
parser.add_argument('--self-test', action='store_true')
policy_channel = load_policy_channel()
channel = args.channel or policy_channel
target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)
expected_archive_sha256 = None
if channel == policy_channel:
    expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)
print(f'ZIG_INSTALL_CHANNEL={channel}')
print(f'ZIG_INSTALL_VERSION={version}')
print(f'ZIG_INSTALL_TARGET={target_key}')
print(f'ZIG_INSTALL_URL={tarball_url}')
if expected_archive_sha256 is not None:
    print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')
if args.resolve_only:
    print('ZIG_INSTALL_STATUS=resolved')
    return 0
with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:
    print(tmpdir_str)
"""
    good_policy = """{
  \"channel\": \"0.17.0-dev.87+9b177a7d2\",
  \"archive_sha256\": {
    \"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"
  }
}
"""

    marker_count = check_installer(good_installer)
    channel, digest = check_policy(good_policy)
    assert marker_count == 8
    assert channel == "0.17.0-dev.87+9b177a7d2"
    assert digest == "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
    case_count = 2

    def expect_installer_failure(bad_text: str, expected_substring: str) -> None:
        nonlocal case_count
        try:
            check_installer(bad_text)
        except SystemExit as exc:
            assert expected_substring in str(exc), str(exc)
            case_count += 1
            return
        raise AssertionError("expected installer validation to fail")

    def expect_policy_failure(bad_text: str, expected_substring: str) -> None:
        nonlocal case_count
        try:
            check_policy(bad_text)
        except SystemExit as exc:
            assert expected_substring in str(exc), str(exc)
            case_count += 1
            return
        raise AssertionError("expected policy validation to fail")

    expect_installer_failure(
        good_installer.replace(
            "parser.add_argument('--resolve-only', action='store_true')\n",
            "",
            1,
        ),
        RESOLVE_ONLY_FLAG,
    )
    expect_installer_failure(
        good_installer.replace(RESOLVED_STATUS + "\n", "", 1),
        RESOLVED_STATUS,
    )
    expect_installer_failure(
        good_installer.replace(
            "if args.resolve_only:\n"
            "    print('ZIG_INSTALL_STATUS=resolved')\n"
            "    return 0\n",
            "",
            1,
        ).replace(
            "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:\n",
            "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:\n"
            "    print(tmpdir_str)\n"
            "if args.resolve_only:\n"
            "    print('ZIG_INSTALL_STATUS=resolved')\n"
            "    return 0\n",
            1,
        ),
        "resolved-before-download flow",
    )
    expect_policy_failure(
        good_policy.replace('\"channel\": \"0.17.0-dev.87+9b177a7d2\"', '\"channel\": \"\"', 1),
        "missing policy channel",
    )
    expect_policy_failure(
        good_policy.replace('\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"', "", 1),
        "missing pinned x86_64-linux archive digest",
    )

    print("LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 install-zig resolve-only behavior stays pinned."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for checker validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    root = args.root.resolve()
    installer_text = (root / INSTALLER_PATH).read_text(encoding="utf-8")
    policy_text = (root / POLICY_PATH).read_text(encoding="utf-8")

    marker_count = check_installer(installer_text)
    channel, digest = check_policy(policy_text)

    print("LANE05_INSTALL_ZIG_RESOLVE_CONTRACT=pass")
    print(f"LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_ROOT={root}")
    print(f"LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_MARKER_COUNT={marker_count}")
    print(f"LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_CHANNEL={channel}")
    print("LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_TARGET=x86_64-linux")
    print(f"LANE05_INSTALL_ZIG_RESOLVE_CONTRACT_SHA256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
