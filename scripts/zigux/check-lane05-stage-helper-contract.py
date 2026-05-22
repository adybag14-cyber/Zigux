#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
README_PATH = Path("third_party/README.md")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / TOOLCHAIN_POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def require_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY_PATH}")
    return value.strip()


def require_string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY_PATH}")
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {TOOLCHAIN_POLICY_PATH}")
        normalized.append(entry.strip())
    return normalized


def require_string_map(payload: dict[str, object], key: str) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY_PATH}")
    normalized: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"invalid {key} target in {TOOLCHAIN_POLICY_PATH}")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"invalid {key}[{map_key}] in {TOOLCHAIN_POLICY_PATH}")
        normalized[map_key.strip()] = map_value.strip().lower()
    return normalized


def resolve_contract(root: Path) -> dict[str, object]:
    payload = load_policy(root)
    channel = require_string(payload, "channel")
    archives = require_string_map(payload, "archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {TOOLCHAIN_POLICY_PATH}")
    targets = require_string_list(upgrade_policy, "archive_target_scope")
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {TOOLCHAIN_POLICY_PATH}, got {len(targets)}")

    target = targets[0]
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} missing from archive_sha256 in {TOOLCHAIN_POLICY_PATH}")
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
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage helper contract missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage helper contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"lane05 stage helper contract expected {label} `{earlier}` before `{later}`")


def check_stage_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / STAGE_HELPER_PATH)
    target = str(contract["target"])
    size = int(contract["size"])

    helper_markers = [
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        'THIRD_PARTY_DIR = Path("third_party")',
        'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(',
        'duplicate_archive_name(',
        'archive_name_has_duplicate_suffix(',
        f'"{target}": {size},',
        'f"zig-{target}-{channel}.tar.xz"',
        'duplicate-suffix archive copies',
        'STAGE_PINNED_ZIG_ARCHIVE=pass',
        'STAGE_PINNED_ZIG_ARCHIVE=fail',
        'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
        'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=',
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=',
        'STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=',
        'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
        'STAGE_PINNED_ZIG_ARCHIVE_STATUS=',
        'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass',
        'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=',
    ]
    for marker in helper_markers:
        require_marker(helper_text, marker, "stage helper marker")

    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
        'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
        "stage helper output order",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=',
        "stage helper output order",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=',
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=',
        "stage helper output order",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=',
        'STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=',
        "stage helper output order",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=',
        'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
        "stage helper output order",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
        'STAGE_PINNED_ZIG_ARCHIVE_STATUS=',
        "stage helper output order",
    )
    return len(helper_markers)


def check_readme(root: Path, contract: dict[str, object]) -> int:
    readme_text = read_text(root / README_PATH)
    required_markers = [
        "# Zigux third-party archives",
        f"`{contract['target']}`",
        f"`{contract['channel']}`",
        f"`{contract['archive_path']}`",
        f"`{contract['sha256']}`",
        f"`{contract['size']}` bytes",
        f"`{contract['duplicate_name']}`",
    ]
    for marker in required_markers:
        require_marker(readme_text, marker, "README marker")
    return len(required_markers)


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)

    (root / TOOLCHAIN_POLICY_PATH).write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (root / STAGE_HELPER_PATH).write_text(
        "\n".join(
            [
                "import re",
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'THIRD_PARTY_DIR = Path("third_party")',
                'EXPECTED_ARCHIVE_SIZES = {',
                '    "x86_64-linux": 58159088,',
                '}',
                'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \\\\((?P<copy>\\\\d+)\\\\)(?P<suffix>\\\\.tar\\\\.xz)$")',
                'def duplicate_archive_name(expected_filename: str) -> str:',
                '    return expected_filename',
                'def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:',
                '    return False',
                'duplicate-suffix archive copies',
                'f"zig-{target}-{channel}.tar.xz"',
                'STAGE_PINNED_ZIG_ARCHIVE=fail',
                'STAGE_PINNED_ZIG_ARCHIVE=pass',
                'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
                'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
                'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=',
                'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=',
                'STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=',
                'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
                'STAGE_PINNED_ZIG_ARCHIVE_STATUS=',
                'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass',
                'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=8',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (root / README_PATH).write_text(
        "\n".join(
            [
                "# Zigux third-party archives",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "- size: `58159088` bytes",
                "- duplicate: `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        assert check_stage_helper(root, contract) == 19
        assert check_readme(root, contract) == 7
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                contract = resolve_contract(root)
                check_stage_helper(root, contract)
                check_readme(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing stage helper marker",
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text("# Zigux third-party archives\n", encoding="utf-8"),
        "missing README marker",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY_PATH).write_text(
            (root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=\nSTAGE_PINNED_ZIG_ARCHIVE_STATUS=',
                'STAGE_PINNED_ZIG_ARCHIVE_STATUS=\nSTAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
            ),
            encoding="utf-8",
        ),
        "output order",
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text(
            (root / README_PATH).read_text(encoding="utf-8").replace(
                '`58159088` bytes',
                '`1` bytes',
            ),
            encoding="utf-8",
        ),
        "missing README marker",
    )

    print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 staged-archive helper contract against policy and README."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract = resolve_contract(root)
        helper_marker_count = check_stage_helper(root, contract)
        readme_marker_count = check_readme(root, contract)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_MARKER_COUNT={helper_marker_count}")
    print(f"LANE05_STAGE_HELPER_README_MARKER_COUNT={readme_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())