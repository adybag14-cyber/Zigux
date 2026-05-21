#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALLER_PATH = Path("scripts/zigux/install-zig.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"

INSTALLER_MARKERS = (
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "expected_archive_sha256 = None",
    "if channel == policy_channel:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "copy_url_to_file(tarball_url, archive_path)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"expected {label} `{earlier}` before `{later}`")


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise ValueError(f"expected exactly {expected} {label} `{marker}`, found {actual}")


def validate_policy(root: Path) -> tuple[str, str]:
    policy_text = read_text(root, POLICY_PATH)
    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON: {exc.msg}") from exc
    if not isinstance(policy, dict):
        raise ValueError("invalid toolchain policy payload: expected object")

    channel = policy.get("channel")
    if channel != EXPECTED_CHANNEL:
        raise ValueError(f"expected policy channel {EXPECTED_CHANNEL}, got {channel!r}")

    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        raise ValueError("invalid archive_sha256 map in toolchain policy")
    if archive_sha256.get(EXPECTED_TARGET) != EXPECTED_SHA256:
        raise ValueError(
            f"expected archive_sha256[{EXPECTED_TARGET}] to be {EXPECTED_SHA256}, got {archive_sha256.get(EXPECTED_TARGET)!r}"
        )

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError("invalid upgrade_policy in toolchain policy")
    targets = upgrade_policy.get("archive_target_scope")
    if targets != [EXPECTED_TARGET]:
        raise ValueError(f"expected archive_target_scope [{EXPECTED_TARGET!r}], got {targets!r}")

    return channel, EXPECTED_TARGET


def validate_installer(root: Path) -> int:
    installer_text = read_text(root, INSTALLER_PATH)
    for marker in INSTALLER_MARKERS:
        require_marker(installer_text, marker, "installer marker")

    require_exact_line_count(
        installer_text,
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        1,
        "archive-sha load line",
    )
    require_exact_line_count(
        installer_text,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        1,
        "verified-status line",
    )
    require_exact_line_count(
        installer_text,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
        1,
        "unverified-status line",
    )

    require_order(
        installer_text,
        "if channel == policy_channel:",
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "policy archive sha load order",
    )
    require_order(
        installer_text,
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
        "expected-sha print order",
    )
    require_order(
        installer_text,
        "copy_url_to_file(tarball_url, archive_path)",
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "download-before-verify order",
    )
    require_order(
        installer_text,
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
        "verified digest print order",
    )
    require_order(
        installer_text,
        "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        "verified-status print order",
    )
    require_order(
        installer_text,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "verify-before-extract order",
    )

    return len(INSTALLER_MARKERS)


def validate_root(root: Path) -> tuple[int, str, str]:
    channel, target = validate_policy(root)
    marker_count = validate_installer(root)
    return marker_count, channel, target


def sample_installer_text() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")

def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:
    return \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"

def verify_archive_sha256(path: Path, expected_sha256: str) -> str:
    return expected_sha256

def copy_url_to_file(url: str, destination: Path) -> None:
    return None

def extract_archive(path: Path, destination: Path) -> Path:
    return destination

def main() -> int:
    policy_channel = \"0.17.0-dev.87+9b177a7d2\"
    channel = policy_channel
    target_key = \"x86_64-linux\"
    tarball_url = \"https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz\"
    expected_archive_sha256 = None
    if channel == policy_channel:
        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)
    print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')
    archive_path = Path(\"archive.tar.xz\")
    tmpdir = Path(\"tmp\")
    copy_url_to_file(tarball_url, archive_path)
    if expected_archive_sha256 is not None:
        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)
        print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')
        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')
    else:
        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')
    extracted_root = extract_archive(archive_path, tmpdir / 'extract')
    return 0
"""


def sample_policy_text() -> str:
    return """{
  \"phase\": \"Phase 2\",
  \"channel\": \"0.17.0-dev.87+9b177a7d2\",
  \"minimum_version\": \"0.17.0-dev.87+9b177a7d2\",
  \"archive_sha256\": {
    \"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"
  },
  \"upgrade_policy\": {
    \"channel_minimum_lockstep\": true,
    \"archive_target_scope\": [
      \"x86_64-linux\"
    ],
    \"required_make_routes\": [
      \"phase2-toolchain\",
      \"phase2-validate\",
      \"phase2-cross\"
    ]
  }
}
"""


def write_sample_root(root: Path) -> None:
    write_text(root, INSTALLER_PATH, sample_installer_text())
    write_text(root, POLICY_PATH, sample_policy_text())


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_archive_verify_pass_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert validate_root(root) == (len(INSTALLER_MARKERS), EXPECTED_CHANNEL, EXPECTED_TARGET)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_archive_verify_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_root(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_root to fail")

    expect_failure(
        lambda root: write_text(root, POLICY_PATH, sample_policy_text().replace(EXPECTED_SHA256, "0" * 64, 1)),
        "expected archive_sha256",
    )
    expect_failure(
        lambda root: write_text(
            root,
            INSTALLER_PATH,
            read_text(root, INSTALLER_PATH).replace(
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n",
                "",
                1,
            ),
        ),
        "verify_archive_sha256",
    )
    expect_failure(
        lambda root: write_text(
            root,
            INSTALLER_PATH,
            read_text(root, INSTALLER_PATH).replace(
                "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')\n",
                "",
                1,
            ),
        ),
        "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    )
    expect_failure(
        lambda root: write_text(
            root,
            INSTALLER_PATH,
            read_text(root, INSTALLER_PATH).replace(
                "copy_url_to_file(tarball_url, archive_path)\n"
                "    if expected_archive_sha256 is not None:\n"
                "        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n",
                "if expected_archive_sha256 is not None:\n"
                "        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n"
                "    copy_url_to_file(tarball_url, archive_path)\n",
                1,
            ),
        ),
        "download-before-verify order",
    )

    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 install-zig archive verification packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a passing sample repo root for replay-oriented validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        marker_count, channel, target = validate_root(args.root.resolve())
    except ValueError as exc:
        print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=fail")
        print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_ROOT={args.root.resolve()}")
        print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_NOTE={exc}")
        return 1

    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_ROOT={args.root.resolve()}")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_MARKER_COUNT={marker_count}")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_CHANNEL={channel}")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_TARGET={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
