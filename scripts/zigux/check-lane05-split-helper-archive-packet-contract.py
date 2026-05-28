#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
ARCHIVE_PACKET_CHECKER_PATH = Path("scripts/zigux/check-lane05-archive-parts-packet.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

HELPER_MARKERS = (
    'DEFAULT_CHUNK_BYTES = 786_432',
    'manifest_path = output_dir / "manifest.json"',
    '"filename": filename,',
    '"encoding": "base64",',
    '"sha256": sha256,',
    '"size": size,',
    '"chunk_bytes": chunk_bytes,',
    '"part_count": part_count,',
    '"parts_glob": "part-*.b64",',
    'output_dir / f"part-{index:03d}.b64"',
    'manifest = json.loads(manifest_path.read_text(encoding="utf-8"))',
    'parts_glob = require_non_empty_string(payload.get("parts_glob"), "parts_glob", manifest_path)',
)

PACKET_CHECKER_MARKERS = (
    'manifest_path = parts_dir / "manifest.json"',
    'filename = require_string(manifest.get("filename"), "manifest filename")',
    'encoding = require_string(manifest.get("encoding"), "manifest encoding")',
    'sha256 = require_string(manifest.get("sha256"), "manifest sha256")',
    'size = require_positive_int(manifest.get("size"), "manifest size")',
    'chunk_bytes = require_positive_int(manifest.get("chunk_bytes"), "manifest chunk_bytes")',
    'part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")',
    'parts_glob = require_string(manifest.get("parts_glob"), "manifest parts_glob")',
    'if parts_glob != "part-*.b64":',
    'expected_names = {f"part-{index:03d}.b64" for index in range(part_count)}',
    'actual_names = {path.name for path in parts_dir.glob("part-*.b64")}',
    'part_path = parts_dir / f"part-{index:03d}.b64"',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper/archive-packet contract missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper/archive-packet contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 split-helper/archive-packet contract expected {label} `{earlier}` before `{later}`"
        )


def require_non_empty_string(value: object, field_name: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {field_name} in {path}")
    return value.strip()


def require_string_list(value: object, field_name: str, path: Path) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {field_name} in {path}")
    items: list[str] = []
    seen: set[str] = set()
    for entry in value:
        normalized = require_non_empty_string(entry, field_name, path)
        if normalized in seen:
            raise ValueError(f"duplicate {field_name} entry in {path}: {normalized}")
        items.append(normalized)
        seen.add(normalized)
    return items


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

    channel = require_non_empty_string(payload.get("channel"), "channel", policy_path)
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise ValueError(f"invalid archive_sha256 in {policy_path}")

    normalized_archives: dict[str, str] = {}
    for target, digest in archive_sha256.items():
        normalized_target = require_non_empty_string(target, "archive_sha256 target", policy_path)
        normalized_digest = require_non_empty_string(
            digest, f"archive_sha256[{normalized_target}]", policy_path
        )
        normalized_archives[normalized_target] = normalized_digest

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    archive_targets = require_string_list(
        upgrade_policy.get("archive_target_scope"),
        "archive_target_scope",
        policy_path,
    )
    if len(archive_targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}, got {len(archive_targets)}")

    target = archive_targets[0]
    if target not in normalized_archives:
        raise ValueError(f"archive_target_scope references missing archive_sha256 entry in {policy_path}: {target}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    return {
        "channel": channel,
        "target": target,
        "sha256": normalized_archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def check_contract(root: Path, contract: dict[str, object]) -> tuple[int, int]:
    helper_text = read_text(root / SPLIT_HELPER_PATH)
    packet_checker_text = read_text(root / ARCHIVE_PACKET_CHECKER_PATH)

    for marker in HELPER_MARKERS:
        require_marker(helper_text, marker, "split helper marker")
    for marker in PACKET_CHECKER_MARKERS:
        require_marker(packet_checker_text, marker, "archive packet checker marker")

    require_order(
        helper_text,
        '"chunk_bytes": chunk_bytes,',
        '"part_count": part_count,',
        "split-helper manifest order",
    )
    require_order(
        helper_text,
        '"part_count": part_count,',
        '"parts_glob": "part-*.b64",',
        "split-helper manifest order",
    )
    require_order(
        packet_checker_text,
        'chunk_bytes = require_positive_int(manifest.get("chunk_bytes"), "manifest chunk_bytes")',
        'part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")',
        "packet-checker manifest order",
    )
    require_order(
        packet_checker_text,
        'part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")',
        'parts_glob = require_string(manifest.get("parts_glob"), "manifest parts_glob")',
        "packet-checker manifest order",
    )
    require_marker(helper_text, f'"{contract["target"]}": {contract["size"]:_},', "target-size marker")
    require_marker(
        packet_checker_text,
        'EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}',
        "packet-checker size map",
    )
    return len(HELPER_MARKERS) + 1, len(PACKET_CHECKER_MARKERS) + 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
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
        root / SPLIT_HELPER_PATH,
        "\n".join(
            (
                "import json",
                'DEFAULT_CHUNK_BYTES = 786_432',
                'EXPECTED_ARCHIVE_SIZES = {',
                '    "x86_64-linux": 58_159_088,',
                '}',
                'manifest_path = output_dir / "manifest.json"',
                'manifest = {',
                '    "filename": filename,',
                '    "encoding": "base64",',
                '    "sha256": sha256,',
                '    "size": size,',
                '    "chunk_bytes": chunk_bytes,',
                '    "part_count": part_count,',
                '    "parts_glob": "part-*.b64",',
                '}',
                'manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")',
                'output_dir / f"part-{index:03d}.b64"',
                'manifest = json.loads(manifest_path.read_text(encoding="utf-8"))',
                'parts_glob = require_non_empty_string(payload.get("parts_glob"), "parts_glob", manifest_path)',
            )
        )
        + "\n",
    )
    write_text(
        root / ARCHIVE_PACKET_CHECKER_PATH,
        "\n".join(
            (
                'EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}',
                'manifest_path = parts_dir / "manifest.json"',
                'manifest = read_json_object(manifest_path)',
                'filename = require_string(manifest.get("filename"), "manifest filename")',
                'encoding = require_string(manifest.get("encoding"), "manifest encoding")',
                'sha256 = require_string(manifest.get("sha256"), "manifest sha256")',
                'size = require_positive_int(manifest.get("size"), "manifest size")',
                'chunk_bytes = require_positive_int(manifest.get("chunk_bytes"), "manifest chunk_bytes")',
                'part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")',
                'parts_glob = require_string(manifest.get("parts_glob"), "manifest parts_glob")',
                'if parts_glob != "part-*.b64":',
                '    raise SystemExit("bad glob")',
                'expected_names = {f"part-{index:03d}.b64" for index in range(part_count)}',
                'actual_names = {path.name for path in parts_dir.glob("part-*.b64")}',
                'part_path = parts_dir / f"part-{index:03d}.b64"',
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_packet_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        contract = load_policy(root)
        helper_marker_count, packet_marker_count = check_contract(root, contract)
        assert helper_marker_count == len(HELPER_MARKERS) + 1
        assert packet_marker_count == len(PACKET_CHECKER_MARKERS) + 1
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_packet_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                contract = load_policy(root)
                check_contract(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: write_text(root / SPLIT_HELPER_PATH, "missing\n"),
        "split helper marker",
    )
    expect_failure(
        lambda root: write_text(
            root / ARCHIVE_PACKET_CHECKER_PATH,
            read_text(root / ARCHIVE_PACKET_CHECKER_PATH).replace(
                'if parts_glob != "part-*.b64":',
                'if parts_glob != "shard-*.txt":',
                1,
            ),
        ),
        'if parts_glob != "part-*.b64":',
    )
    expect_failure(
        lambda root: write_text(
            root / SPLIT_HELPER_PATH,
            read_text(root / SPLIT_HELPER_PATH).replace('output_dir / f"part-{index:03d}.b64"', 'output_dir / f"piece-{index:03d}.txt"', 1),
        ),
        'output_dir / f"part-{index:03d}.b64"',
    )
    expect_failure(
        lambda root: write_text(
            root / ARCHIVE_PACKET_CHECKER_PATH,
            read_text(root / ARCHIVE_PACKET_CHECKER_PATH).replace(
                'expected_names = {f"part-{index:03d}.b64" for index in range(part_count)}',
                'expected_names = {f"piece-{index:03d}.txt" for index in range(part_count)}',
                1,
            ),
        ),
        'expected_names = {f"part-{index:03d}.b64" for index in range(part_count)}',
    )
    expect_failure(
        lambda root: write_text(
            root / TOOLCHAIN_POLICY_PATH,
            read_text(root / TOOLCHAIN_POLICY_PATH).replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
                1,
            ),
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: write_text(
            root / SPLIT_HELPER_PATH,
            read_text(root / SPLIT_HELPER_PATH).replace(
                '"chunk_bytes": chunk_bytes,\n    "part_count": part_count,',
                '"part_count": part_count,\n    "chunk_bytes": chunk_bytes,',
                1,
            ),
        ),
        "split-helper manifest order",
    )

    print("LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper and archive-parts packet checker still share the same packet contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract = load_policy(root)
        helper_marker_count, packet_marker_count = check_contract(root, contract)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT=fail")
        print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT=pass")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_SIZE={contract['size']}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_HELPER_MARKER_COUNT={helper_marker_count}")
    print(f"LANE05_SPLIT_HELPER_ARCHIVE_PACKET_CONTRACT_PACKET_MARKER_COUNT={packet_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
