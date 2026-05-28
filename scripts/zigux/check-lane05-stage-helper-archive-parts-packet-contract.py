#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
ARCHIVE_PACKET_PATH = Path("scripts/zigux/check-lane05-archive-parts-packet.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
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
        "parts_dir": f"third_party/{filename}.parts",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage/archive contract missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage/archive contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"lane05 stage/archive contract expected {label} `{earlier}` before `{later}`")


def check_stage_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / STAGE_HELPER_PATH)
    target = str(contract["target"])
    size_marker = f'"{target}": {int(contract["size"]):_}'

    helper_markers = [
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        'THIRD_PARTY_DIR = Path("third_party")',
        'f"zig-{target}-{channel}.tar.xz"',
        size_marker,
        'expected shard manifest filename',
        'expected shard manifest encoding base64',
        'expected shard manifest sha256',
        'expected shard manifest size',
        'expected shard manifest parts_glob part-*.b64',
        'missing expected shard:',
        'invalid base64 shard:',
        '--parts-dir',
        'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
        'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
    ]
    for marker in helper_markers:
        require_marker(helper_text, marker, "stage helper marker")

    require_order(
        helper_text,
        'expected shard manifest filename',
        'expected shard manifest encoding base64',
        "stage helper manifest checks",
    )
    require_order(
        helper_text,
        'expected shard manifest encoding base64',
        'expected shard manifest sha256',
        "stage helper manifest checks",
    )
    require_order(
        helper_text,
        'expected shard manifest sha256',
        'expected shard manifest size',
        "stage helper manifest checks",
    )
    require_order(
        helper_text,
        'expected shard manifest size',
        'expected shard manifest parts_glob part-*.b64',
        "stage helper manifest checks",
    )
    require_order(
        helper_text,
        'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
        'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
        "stage helper output order",
    )
    return len(helper_markers)


def check_archive_packet(root: Path, contract: dict[str, object]) -> int:
    packet_text = read_text(root / ARCHIVE_PACKET_PATH)
    target = str(contract["target"])
    size_marker = f'"{target}": {int(contract["size"]):_}'

    packet_markers = [
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        'THIRD_PARTY_DIR = Path("third_party")',
        'f"zig-{target}-{channel}.tar.xz"',
        size_marker,
        'packet filename mismatch: expected',
        'packet encoding mismatch: expected base64',
        'packet sha256 mismatch: expected',
        'packet size mismatch: expected',
        'packet parts_glob mismatch: expected part-*.b64',
        'packet missing shard files:',
        'packet shard is not valid base64:',
        '--parts-dir',
        'LANE05_ARCHIVE_PARTS_PACKET_STATUS=',
        'LANE05_ARCHIVE_PARTS_PACKET_DIR=',
    ]
    for marker in packet_markers:
        require_marker(packet_text, marker, "archive-parts checker marker")

    require_order(
        packet_text,
        'packet filename mismatch: expected',
        'packet encoding mismatch: expected base64',
        "archive-parts manifest checks",
    )
    require_order(
        packet_text,
        'packet encoding mismatch: expected base64',
        'packet sha256 mismatch: expected',
        "archive-parts manifest checks",
    )
    require_order(
        packet_text,
        'packet sha256 mismatch: expected',
        'packet size mismatch: expected',
        "archive-parts manifest checks",
    )
    require_order(
        packet_text,
        'packet size mismatch: expected',
        'packet parts_glob mismatch: expected part-*.b64',
        "archive-parts manifest checks",
    )
    require_order(
        packet_text,
        'LANE05_ARCHIVE_PARTS_PACKET_STATUS=',
        'LANE05_ARCHIVE_PARTS_PACKET_DIR=',
        "archive-parts output order",
    )
    return len(packet_markers)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)

    write_text(
        root / TOOLCHAIN_POLICY_PATH,
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
    )

    write_text(
        root / STAGE_HELPER_PATH,
        "\n".join(
            [
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'THIRD_PARTY_DIR = Path("third_party")',
                'EXPECTED_ARCHIVE_SIZES = {',
                '    "x86_64-linux": 58_159_088,',
                '}',
                'f"zig-{target}-{channel}.tar.xz"',
                'expected shard manifest filename',
                'expected shard manifest encoding base64',
                'expected shard manifest sha256',
                'expected shard manifest size',
                'expected shard manifest parts_glob part-*.b64',
                'missing expected shard:',
                'invalid base64 shard:',
                '--parts-dir',
                'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
                'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
                'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
            ]
        )
        + "\n",
    )

    write_text(
        root / ARCHIVE_PACKET_PATH,
        "\n".join(
            [
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'THIRD_PARTY_DIR = Path("third_party")',
                'EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}',
                'f"zig-{target}-{channel}.tar.xz"',
                'packet filename mismatch: expected',
                'packet encoding mismatch: expected base64',
                'packet sha256 mismatch: expected',
                'packet size mismatch: expected',
                'packet parts_glob mismatch: expected part-*.b64',
                'packet missing shard files:',
                'packet shard is not valid base64:',
                '--parts-dir',
                'LANE05_ARCHIVE_PARTS_PACKET_STATUS=',
                'LANE05_ARCHIVE_PARTS_PACKET_DIR=',
            ]
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_archive_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        assert check_stage_helper(root, contract) == 14
        assert check_archive_packet(root, contract) == 14
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_archive_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                contract = resolve_contract(root)
                check_stage_helper(root, contract)
                check_archive_packet(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: write_text(root / STAGE_HELPER_PATH, "missing\n"),
        "missing stage helper marker",
    )
    expect_failure(
        lambda root: write_text(root / ARCHIVE_PACKET_PATH, "missing\n"),
        "missing archive-parts checker marker",
    )
    expect_failure(
        lambda root: write_text(
            root / TOOLCHAIN_POLICY_PATH,
            (root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
            ),
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: write_text(
            root / STAGE_HELPER_PATH,
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'expected shard manifest filename\nexpected shard manifest encoding base64',
                'expected shard manifest encoding base64\nexpected shard manifest filename',
            ),
        ),
        "stage helper manifest checks",
    )
    expect_failure(
        lambda root: write_text(
            root / ARCHIVE_PACKET_PATH,
            (root / ARCHIVE_PACKET_PATH).read_text(encoding="utf-8").replace(
                'packet filename mismatch: expected\npacket encoding mismatch: expected base64',
                'packet encoding mismatch: expected base64\npacket filename mismatch: expected',
            ),
        ),
        "archive-parts manifest checks",
    )

    print("LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Lane 05 contract between the staged-archive helper and the archive-parts packet checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Optional path where a compact sample root should be written for contract replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_fixture(args.write_sample_root.resolve())
        print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        root = args.root.resolve()
        contract = resolve_contract(root)
        stage_helper_marker_count = check_stage_helper(root, contract)
        archive_packet_marker_count = check_archive_packet(root, contract)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_STAGE_HELPER_MARKER_COUNT={stage_helper_marker_count}")
    print(f"LANE05_STAGE_HELPER_ARCHIVE_PARTS_PACKET_CONTRACT_ARCHIVE_PACKET_MARKER_COUNT={archive_packet_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
