#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

SPLIT_HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'DEFAULT_CHUNK_BYTES = 786_432',
    'EXPECTED_ARCHIVE_SIZES = {',
    '"x86_64-linux": 58_159_088,',
    'write_manifest(',
    '"filename": filename,',
    '"encoding": "base64",',
    '"sha256": sha256,',
    '"size": size,',
    '"chunk_bytes": chunk_bytes,',
    '"part_count": part_count,',
    '"parts_glob": "part-*.b64"',
    '(output_dir / f"part-{index:03d}.b64").write_text(',
    'base64.b64encode(chunk).decode("ascii") + "\\n"',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION=',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME=',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256=',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE=',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT=',
)

STAGE_HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'EXPECTED_ARCHIVE_SIZES = {',
    '"x86_64-linux": 58_159_088,',
    'load_shard_manifest(',
    'reconstruct_archive_from_parts(',
    'filename = require_manifest_string(manifest, "filename", manifest_path)',
    'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
    'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
    'size = require_manifest_int(manifest, "size", manifest_path)',
    'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
    'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
    'if encoding != "base64":',
    'if parts_glob != "part-*.b64":',
    'shard_path = parts_dir / f"part-{index:03d}.b64"',
    'chunk = base64.b64decode(encoded, validate=True)',
    'STAGE_PINNED_ZIG_ARCHIVE=pass',
    'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
    'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
    'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
    'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=',
    'STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def read_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json in {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid json shape in {path}: expected object")
    return payload


def require_non_empty_string(value: object, label: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {label} in {path}")
    return value.strip()


def require_string_map(value: object, label: str, path: Path) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {label} in {path}")
    normalized: dict[str, str] = {}
    for key, item in value.items():
        normalized_key = require_non_empty_string(key, f"{label} target", path)
        normalized[normalized_key] = require_non_empty_string(item, f"{label}[{normalized_key}]", path)
    return normalized


def require_string_list(value: object, label: str, path: Path) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {label} in {path}")
    return [require_non_empty_string(entry, label, path) for entry in value]


def resolve_contract(root: Path) -> dict[str, object]:
    policy_path = root / TOOLCHAIN_POLICY_PATH
    payload = read_json_object(policy_path)
    channel = require_non_empty_string(payload.get("channel"), "channel", policy_path)
    archives = require_string_map(payload.get("archive_sha256"), "archive_sha256", policy_path)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    targets = require_string_list(upgrade_policy.get("archive_target_scope"), "archive_target_scope", policy_path)
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}, got {len(targets)}")
    target = targets[0]
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} missing from archive_sha256 in {policy_path}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")
    return {
        "target": target,
        "channel": channel,
        "sha256": archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage/split packet contract missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage/split packet contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 stage/split packet contract expected {label} `{earlier}` before `{later}`"
        )


def check_helper_markers(root: Path, contract: dict[str, object]) -> tuple[int, int]:
    split_text = read_text(root / SPLIT_HELPER_PATH)
    stage_text = read_text(root / STAGE_HELPER_PATH)

    for marker in SPLIT_HELPER_MARKERS:
        require_marker(split_text, marker, "split-helper marker")
    for marker in STAGE_HELPER_MARKERS:
        require_marker(stage_text, marker, "stage-helper marker")

    shared_size_marker = f'"{contract["target"]}": {contract["size"]:_},'
    shared_filename_marker = 'f"zig-{target}-{channel}.tar.xz"'
    require_marker(split_text, shared_size_marker, "shared size marker")
    require_marker(stage_text, shared_size_marker, "shared size marker")
    require_marker(split_text, shared_filename_marker, "shared filename marker")
    require_marker(stage_text, shared_filename_marker, "shared filename marker")

    require_order(
        split_text,
        '"encoding": "base64",',
        '"parts_glob": "part-*.b64"',
        "split-helper manifest field order",
    )
    require_order(
        split_text,
        '"parts_glob": "part-*.b64"',
        '(output_dir / f"part-{index:03d}.b64").write_text(',
        "split-helper shard write order",
    )
    require_order(
        stage_text,
        'filename = require_manifest_string(manifest, "filename", manifest_path)',
        'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
        "stage-helper manifest field order",
    )
    require_order(
        stage_text,
        'if encoding != "base64":',
        'if parts_glob != "part-*.b64":',
        "stage-helper manifest validation order",
    )
    require_order(
        stage_text,
        'if parts_glob != "part-*.b64":',
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        "stage-helper shard reconstruction order",
    )
    require_order(
        split_text,
        'RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
        'RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION=',
        "split-helper reconstruct output order",
    )
    require_order(
        stage_text,
        'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
        'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
        "stage-helper staged output order",
    )
    require_order(
        stage_text,
        'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
        'STAGE_PINNED_ZIG_ARCHIVE_FILENAME=',
        "stage-helper staged output order",
    )
    return len(SPLIT_HELPER_MARKERS) + 1, len(STAGE_HELPER_MARKERS) + 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture(root: Path) -> None:
    write_text(
        root / TOOLCHAIN_POLICY_PATH,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
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
                "from pathlib import Path",
                "import base64",
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "DEFAULT_CHUNK_BYTES = 786_432",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                'expected_size = EXPECTED_ARCHIVE_SIZES["x86_64-linux"]',
                'filename = f"zig-{target}-{channel}.tar.xz"',
                "def write_manifest(output_dir, filename, sha256, size, chunk_bytes, part_count):",
                '    manifest = {"filename": filename, "encoding": "base64", "sha256": sha256, "size": size, "chunk_bytes": chunk_bytes, "part_count": part_count, "parts_glob": "part-*.b64"}',
                '    (output_dir / f"part-{index:03d}.b64").write_text(',
                '        base64.b64encode(chunk).decode("ascii") + "\\n"',
                "    )",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR=",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION=",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME=",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256=",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_SIZE=",
                "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT=",
            )
        )
        + "\n",
    )
    write_text(
        root / STAGE_HELPER_PATH,
        "\n".join(
            (
                "from pathlib import Path",
                "import base64",
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                'expected_size = EXPECTED_ARCHIVE_SIZES["x86_64-linux"]',
                'filename = f"zig-{target}-{channel}.tar.xz"',
                "def load_shard_manifest(parts_dir): pass",
                "def reconstruct_archive_from_parts(parts_dir, destination): pass",
                'filename = require_manifest_string(manifest, "filename", manifest_path)',
                'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
                'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
                'size = require_manifest_int(manifest, "size", manifest_path)',
                'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
                'if encoding != "base64":',
                '    raise ValueError("bad encoding")',
                'if parts_glob != "part-*.b64":',
                '    raise ValueError("bad parts_glob")',
                'shard_path = parts_dir / f"part-{index:03d}.b64"',
                'chunk = base64.b64decode(encoded, validate=True)',
                "STAGE_PINNED_ZIG_ARCHIVE=pass",
                "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=",
                "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
                "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=",
                "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=",
                "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=",
            )
        )
        + "\n",
    )


def replace_once(text: str, needle: str, replacement: str) -> str:
    if needle not in text:
        raise AssertionError(f"missing fixture marker: {needle}")
    return text.replace(needle, replacement, 1)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="lane05_stage_split_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        split_marker_count, stage_marker_count = check_helper_markers(root, contract)
        assert split_marker_count >= len(SPLIT_HELPER_MARKERS)
        assert stage_marker_count >= len(STAGE_HELPER_MARKERS)
        cases += 1

        split_path = root / SPLIT_HELPER_PATH
        split_path.write_text(
            replace_once(
                split_path.read_text(encoding="utf-8"),
                '"parts_glob": "part-*.b64"',
                '"parts_glob": "piece-*.b64",',
            ),
            encoding="utf-8",
        )
        try:
            check_helper_markers(root, contract)
        except ValueError as exc:
            assert 'parts_glob": "part-*.b64"' in str(exc)
            cases += 1
        else:
            raise AssertionError("expected split-helper parts_glob failure")

    with tempfile.TemporaryDirectory(prefix="lane05_stage_split_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        stage_path = root / STAGE_HELPER_PATH
        stage_path.write_text(
            replace_once(
                stage_path.read_text(encoding="utf-8"),
                'shard_path = parts_dir / f"part-{index:03d}.b64"',
                'shard_path = parts_dir / f"piece-{index:03d}.b64"',
            ),
            encoding="utf-8",
        )
        try:
            check_helper_markers(root, contract)
        except ValueError as exc:
            assert 'part-{index:03d}.b64' in str(exc)
            cases += 1
        else:
            raise AssertionError("expected stage-helper shard naming failure")

    with tempfile.TemporaryDirectory(prefix="lane05_stage_split_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        split_path = root / SPLIT_HELPER_PATH
        split_path.write_text(
            replace_once(
                split_path.read_text(encoding="utf-8"),
                '"x86_64-linux": 58_159_088,',
                '"x86_64-linux": 1,',
            ),
            encoding="utf-8",
        )
        contract = resolve_contract(root)
        try:
            check_helper_markers(root, contract)
        except ValueError as exc:
            assert '"x86_64-linux": 58_159_088,' in str(exc)
            cases += 1
        else:
            raise AssertionError("expected split-helper size marker failure")

    with tempfile.TemporaryDirectory(prefix="lane05_stage_split_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        stage_path = root / STAGE_HELPER_PATH
        stage_path.write_text(
            replace_once(
                stage_path.read_text(encoding="utf-8"),
                'if encoding != "base64":\n    raise ValueError("bad encoding")\nif parts_glob != "part-*.b64":',
                'if parts_glob != "part-*.b64":\n    raise ValueError("bad parts_glob")\nif encoding != "base64":',
            ),
            encoding="utf-8",
        )
        try:
            check_helper_markers(root, contract)
        except ValueError as exc:
            assert "manifest validation order" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected stage-helper manifest-order failure")

    with tempfile.TemporaryDirectory(prefix="lane05_stage_split_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        policy_path = root / TOOLCHAIN_POLICY_PATH
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            resolve_contract(root)
        except ValueError as exc:
            assert "expected exactly one archive target" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected policy target-count failure")

    print("LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper emits a shard packet the staged-archive helper can consume."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    try:
        contract = resolve_contract(root)
        split_marker_count, stage_marker_count = check_helper_markers(root, contract)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_ROOT={root}")
        print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_SPLIT_MARKER_COUNT={split_marker_count}")
    print(f"LANE05_STAGE_HELPER_SPLIT_PACKET_CONTRACT_STAGE_MARKER_COUNT={stage_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
