#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
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
        raise ValueError(
            f"archive_target_scope target {target} missing from archive_sha256 in {TOOLCHAIN_POLICY_PATH}"
        )
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
        raise ValueError(f"lane05 stage-helper parts contract missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            "lane05 stage-helper parts contract expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper parts contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 stage-helper parts contract expected {label} `{earlier}` before `{later}`"
        )


def check_stage_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / STAGE_HELPER_PATH)

    manifest_markers = [
        "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:",
        'manifest_path = parts_dir / "manifest.json"',
        'filename = require_manifest_string(manifest, "filename", manifest_path)',
        'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
        'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
        'size = require_manifest_int(manifest, "size", manifest_path)',
        'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
        "if filename != expected_filename:",
        'if encoding != "base64":',
        "if sha256 != expected_sha:",
        "if size != expected_size:",
        'if parts_glob != "part-*.b64":',
        "def reconstruct_archive_from_parts(",
        'for index in range(part_count):',
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        'raise ValueError(f"missing expected shard: {shard_path.name}")',
        'raise ValueError(f"invalid base64 shard: {shard_path.name}")',
    ]
    parts_mode_markers = [
        "def resolve_source_archive(",
        'if (source is None) == (parts_dir is None):',
        'raise ValueError("exactly one of source or parts_dir must be provided")',
        'reconstructed_source = Path(temp_dir.name) / str(metadata["filename"])',
        'return reconstructed_source, "parts_dir", temp_dir',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
        'assert input_mode == "parts_dir"',
        'expected_substring="missing shard manifest"',
        'expected_substring="expected shard manifest filename"',
        'expected_substring="missing expected shard"',
        'expected_substring="invalid base64 shard"',
    ]

    for marker in manifest_markers + parts_mode_markers:
        require_marker(helper_text, marker, "stage helper marker")

    require_exact_count(
        helper_text,
        'raise ValueError("exactly one of source or parts_dir must be provided")',
        1,
        "source/parts exclusivity guard",
    )
    require_exact_count(
        helper_text,
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
        1,
        "parts-dir output line",
    )
    require_exact_count(
        helper_text,
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
        1,
        "input-mode output line",
    )

    require_order(
        helper_text,
        "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:",
        "def reconstruct_archive_from_parts(",
        "manifest helper order",
    )
    require_order(
        helper_text,
        'filename = require_manifest_string(manifest, "filename", manifest_path)',
        "if filename != expected_filename:",
        "manifest filename validation order",
    )
    require_order(
        helper_text,
        'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
        'if parts_glob != "part-*.b64":',
        "manifest parts_glob validation order",
    )
    require_order(
        helper_text,
        "def reconstruct_archive_from_parts(",
        "def resolve_source_archive(",
        "parts reconstruction before source resolution order",
    )
    require_order(
        helper_text,
        'reconstructed_source = Path(temp_dir.name) / str(metadata["filename"])',
        'return reconstructed_source, "parts_dir", temp_dir',
        "parts reconstruction output order",
    )
    require_order(
        helper_text,
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
        "parts output order",
    )

    return len(manifest_markers) + len(parts_mode_markers)


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
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
                "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:",
                '    manifest_path = parts_dir / "manifest.json"',
                '    return {"filename": "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"}',
                "def require_manifest_string(manifest, key, manifest_path):",
                "    return manifest[key]",
                "def require_manifest_int(manifest, key, manifest_path):",
                "    return 1",
                "def reconstruct_archive_from_parts(",
                '    filename = require_manifest_string(manifest, "filename", manifest_path)',
                '    encoding = require_manifest_string(manifest, "encoding", manifest_path)',
                '    sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
                '    size = require_manifest_int(manifest, "size", manifest_path)',
                '    part_count = require_manifest_int(manifest, "part_count", manifest_path)',
                '    require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                '    parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
                '    if filename != expected_filename:',
                "        raise ValueError()",
                '    if encoding != "base64":',
                "        raise ValueError()",
                '    if sha256 != expected_sha:',
                "        raise ValueError()",
                "    if size != expected_size:",
                "        raise ValueError()",
                '    if parts_glob != "part-*.b64":',
                "        raise ValueError()",
                "    for index in range(part_count):",
                '        shard_path = parts_dir / f"part-{index:03d}.b64"',
                '        raise ValueError(f"missing expected shard: {shard_path.name}")',
                '        raise ValueError(f"invalid base64 shard: {shard_path.name}")',
                "def resolve_source_archive(",
                '    if (source is None) == (parts_dir is None):',
                '        raise ValueError("exactly one of source or parts_dir must be provided")',
                '    reconstructed_source = Path(temp_dir.name) / str(metadata["filename"])',
                '    return reconstructed_source, "parts_dir", temp_dir',
                '    assert input_mode == "parts_dir"',
                '    expected_substring="missing shard manifest"',
                '    expected_substring="expected shard manifest filename"',
                '    expected_substring="missing expected shard"',
                '    expected_substring="invalid base64 shard"',
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_parts_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        assert check_stage_helper(root, contract) == 31
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_parts_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                contract = resolve_contract(root)
                check_stage_helper(root, contract)
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
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'raise ValueError("exactly one of source or parts_dir must be provided")',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "exactly one of source or parts_dir must be provided",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")\n'
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")\n'
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                1,
            ),
            encoding="utf-8",
        ),
        "parts output order",
    )
    expect_failure(
        lambda root: (lambda payload: (root / TOOLCHAIN_POLICY_PATH).write_text(
            json.dumps(
                {
                    **payload,
                    "upgrade_policy": {
                        **payload["upgrade_policy"],
                        "archive_target_scope": ["x86_64-linux", "aarch64-linux"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        ))(json.loads((root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8"))),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'expected_substring="invalid base64 shard"',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "invalid base64 shard",
    )

    print("LANE05_STAGE_HELPER_PARTS_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 staged archive helper .parts reconstruction contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract = resolve_contract(root)
        marker_count = check_stage_helper(root, contract)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_PARTS_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_PARTS_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_STAGE_HELPER_PARTS_CONTRACT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_PARTS_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
