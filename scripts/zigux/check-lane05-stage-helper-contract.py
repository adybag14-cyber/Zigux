#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
README_PATH = Path("third_party/README.md")
HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


def require_string(payload: dict[str, object], key: str, path: Path) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {key} in {path}")
    return value.strip()


def require_string_list(payload: dict[str, object], key: str, path: Path) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {path}")
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {path}")
        normalized.append(entry.strip())
    return normalized


def require_string_map(payload: dict[str, object], key: str, path: Path) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {key} in {path}")
    normalized: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"invalid {key} target in {path}")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"invalid {key}[{map_key}] in {path}")
        normalized[map_key.strip()] = map_value.strip()
    return normalized


def load_policy(root: Path) -> dict[str, str | int]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    channel = require_string(payload, "channel", policy_path)
    archives = require_string_map(payload, "archive_sha256", policy_path)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    targets = require_string_list(upgrade_policy, "archive_target_scope", policy_path)
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}, got {len(targets)}")

    target = targets[0]
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} is missing from archive_sha256 in {policy_path}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    filename = f"zig-{target}-{channel}.tar.xz"
    return {
        "target": target,
        "channel": channel,
        "sha256": archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": filename,
        "duplicate_name": f"{filename[:-len('.tar.xz')]} (1).tar.xz",
        "archive_path": f"third_party/{filename}",
        "validation_command": (
            "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
            f"third_party/{filename} --archive-target {target}"
        ),
    }


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise ValueError(f"{label} is missing required markers: {', '.join(missing)}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(f"{label} expected exactly {expected} copies of {marker}, found {actual}")


def validate_contract(root: Path) -> tuple[str, str, int, int]:
    metadata = load_policy(root)
    helper_size_literal = f'{int(metadata["size"]):_}'
    helper_path = root / HELPER_PATH
    readme_path = root / README_PATH

    try:
        helper_text = helper_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing stage helper: {helper_path}") from exc
    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing archive README: {readme_path}") from exc

    helper_markers = [
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        'THIRD_PARTY_DIR = Path("third_party")',
        'EXPECTED_ARCHIVE_SIZES = {',
        f'    "{metadata["target"]}": {helper_size_literal},',
        'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(',
        '"filename": f"zig-{target}-{channel}.tar.xz",',
        'duplicate_archive_name(expected_filename)',
        "archive_name_has_duplicate_suffix(",
        'require_clean_third_party(root, str(metadata["filename"]))',
        'return metadata, "checked",',
        'return metadata, "already_present",',
        'return metadata, "staged",',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata[\'size\']}")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata[\'sha256\']}")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")',
        '"--check-only"',
    ]
    readme_markers = [
        "# Zigux third-party archives",
        "Lane 05 bootstrap CI",
        f'`{metadata["target"]}`',
        f'`{metadata["channel"]}`',
        f'`{metadata["archive_path"]}`',
        f'`{metadata["sha256"]}`',
        f'`{metadata["size"]}` bytes',
        f'`{metadata["validation_command"]}`',
        f'`{metadata["duplicate_name"]}`',
        f'`{POLICY_PATH}`',
    ]

    require_markers(helper_text, helper_markers, "lane05 stage helper")
    require_markers(readme_text, readme_markers, "lane05 archive README")

    require_exact_count(
        helper_text,
        f'    "{metadata["target"]}": {helper_size_literal},',
        1,
        "lane05 stage helper size mapping",
    )
    require_exact_count(
        readme_text,
        f'`{metadata["archive_path"]}`',
        2,
        "lane05 archive README pinned archive path markers",
    )
    require_exact_count(
        readme_text,
        f'`{metadata["duplicate_name"]}`',
        1,
        "lane05 archive README duplicate-suffix marker",
    )

    return str(metadata["target"]), str(metadata["channel"]), len(helper_markers), len(readme_markers)


def write_sample_root(root: Path) -> None:
    scripts_dir = root / "scripts" / "zigux"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    third_party_dir = root / "third_party"
    third_party_dir.mkdir(parents=True, exist_ok=True)

    policy_text = """{
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {
    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
  },
  "upgrade_policy": {
    "channel_minimum_lockstep": true,
    "archive_target_scope": [
      "x86_64-linux"
    ],
    "required_make_routes": [
      "phase2-toolchain",
      "phase2-validate"
    ]
  }
}
"""
    helper_text = """#!/usr/bin/env python3
from pathlib import Path
import re

TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_DIR = Path("third_party")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \\((?P<copy>\\d+)\\)(?P<suffix>\\.tar\\.xz)$")

def duplicate_archive_name(expected_filename: str) -> str:
    return expected_filename

def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:
    return path_name == expected_filename

def stage_archive(root: Path, source: Path, *, check_only: bool):
    metadata = {
        "filename": f"zig-{target}-{channel}.tar.xz",
        "size": 58_159_088,
        "sha256": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    }
    require_clean_third_party(root, str(metadata["filename"]))
    if check_only:
        return metadata, "checked", metadata["sha256"], root / THIRD_PARTY_DIR / metadata["filename"]
    if source == root:
        return metadata, "staged", metadata["sha256"], root / THIRD_PARTY_DIR / metadata["filename"]
    return metadata, "already_present", metadata["sha256"], root / THIRD_PARTY_DIR / metadata["filename"]

def require_clean_third_party(root: Path, expected_filename: str) -> None:
    duplicate_archive_name(expected_filename)
    archive_name_has_duplicate_suffix(expected_filename, expected_filename)

def emit(status: str, metadata: dict[str, object]) -> None:
    print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata['size']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")

parser_help = "--check-only"
target = "x86_64-linux"
channel = "0.17.0-dev.87+9b177a7d2"
"""
    readme_text = """# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- target: `x86_64-linux`
- channel: `0.17.0-dev.87+9b177a7d2`
- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- size: `58159088` bytes

## Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap CI reuses `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when present.

## Rules

- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json` changes the pinned target, channel, digest, or expected payload size
"""

    (scripts_dir / "zig-toolchain-policy.json").write_text(policy_text, encoding="utf-8")
    (scripts_dir / "stage-pinned-zig-archive.py").write_text(helper_text, encoding="utf-8")
    (third_party_dir / "README.md").write_text(readme_text, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_contract(root) == ("x86_64-linux", "0.17.0-dev.87+9b177a7d2", 17, 10)
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_contract(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_contract to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text("missing helper markers\n", encoding="utf-8"),
        "lane05 stage helper is missing required markers",
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text("missing README markers\n", encoding="utf-8"),
        "lane05 archive README is missing required markers",
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text('{"channel":7}\n', encoding="utf-8"),
        "invalid channel",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                '    "x86_64-linux": 58_159_088,\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        '    "x86_64-linux": 58_159_088,',
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text(
            (root / README_PATH).read_text(encoding="utf-8").replace(
                '`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`',
                "`zig-copy.tar.xz`",
                1,
            ),
            encoding="utf-8",
        ),
        '`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`',
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text(
            (root / README_PATH).read_text(encoding="utf-8").replace(
                '`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`',
                "`third_party/other.tar.xz`",
                1,
            ),
            encoding="utf-8",
        ),
        "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    )

    print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 pinned-archive staging helper contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
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

    try:
        target, channel, helper_marker_count, readme_marker_count = validate_contract(args.root.resolve())
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_TARGET={target}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_CHANNEL={channel}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_HELPER_MARKER_COUNT={helper_marker_count}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_README_MARKER_COUNT={readme_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
