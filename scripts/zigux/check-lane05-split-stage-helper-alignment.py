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

SPLIT_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    "DEFAULT_CHUNK_BYTES = 786_432",
    '"filename": f"zig-{target}-{channel}.tar.xz"',
    '"encoding": "base64",',
    '"sha256": sha256,',
    '"size": size,',
    '"chunk_bytes": chunk_bytes,',
    '"part_count": part_count,',
    '"parts_glob": "part-*.b64",',
    '(output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
    'RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass',
)

STAGE_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'manifest_path = parts_dir / "manifest.json"',
    'require_manifest_string(manifest, "filename", manifest_path)',
    'require_manifest_string(manifest, "encoding", manifest_path)',
    'require_manifest_string(manifest, "sha256", manifest_path)',
    'require_manifest_int(manifest, "size", manifest_path)',
    'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    'require_manifest_int(manifest, "part_count", manifest_path)',
    'require_manifest_string(manifest, "parts_glob", manifest_path)',
    'expected shard manifest encoding base64',
    'expected shard manifest parts_glob part-*.b64',
    'shard_path = parts_dir / f"part-{index:03d}.b64"',
    'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
)

SPLIT_ORDERED_MARKERS = (
    ('"filename": f"zig-{target}-{channel}.tar.xz"', '"encoding": "base64",'),
    ('"encoding": "base64",', '"sha256": sha256,'),
    ('"sha256": sha256,', '"size": size,'),
    ('"size": size,', '"chunk_bytes": chunk_bytes,'),
    ('"chunk_bytes": chunk_bytes,', '"part_count": part_count,'),
    ('"part_count": part_count,', '"parts_glob": "part-*.b64",'),
)

STAGE_ORDERED_MARKERS = (
    (
        'require_manifest_string(manifest, "filename", manifest_path)',
        'require_manifest_string(manifest, "encoding", manifest_path)',
    ),
    (
        'require_manifest_string(manifest, "encoding", manifest_path)',
        'require_manifest_string(manifest, "sha256", manifest_path)',
    ),
    (
        'require_manifest_string(manifest, "sha256", manifest_path)',
        'require_manifest_int(manifest, "size", manifest_path)',
    ),
    (
        'require_manifest_int(manifest, "size", manifest_path)',
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    ),
    (
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        'require_manifest_int(manifest, "part_count", manifest_path)',
    ),
    (
        'require_manifest_int(manifest, "part_count", manifest_path)',
        'require_manifest_string(manifest, "parts_glob", manifest_path)',
    ),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


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


def load_contract(root: Path) -> dict[str, object]:
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
        raise ValueError(
            f"archive_target_scope references missing archive_sha256 entry in {policy_path}: {target}"
        )
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    return {
        "target": target,
        "channel": channel,
        "sha256": normalized_archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-stage alignment missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-stage alignment expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-stage alignment missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 split-stage alignment expected {label} `{earlier}` before `{later}`"
        )


def check_helpers(root: Path, contract: dict[str, object]) -> int:
    split_text = read_text(root / SPLIT_HELPER_PATH)
    stage_text = read_text(root / STAGE_HELPER_PATH)

    for marker in SPLIT_MARKERS:
        require_marker(split_text, marker, "split helper marker")
    for marker in STAGE_MARKERS:
        require_marker(stage_text, marker, "stage helper marker")

    for marker in (
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        '"encoding": "base64",',
        '"parts_glob": "part-*.b64",',
    ):
        require_exact_count(split_text, marker, 1, "split helper marker")

    require_marker(split_text, f'"{contract["target"]}": {contract["size"]:_},', "split target-size marker")
    require_marker(stage_text, f'"{contract["target"]}": {contract["size"]:_},', "stage target-size marker")

    for earlier, later in SPLIT_ORDERED_MARKERS:
        require_order(split_text, earlier, later, "split manifest order")
    for earlier, later in STAGE_ORDERED_MARKERS:
        require_order(stage_text, earlier, later, "stage manifest order")

    require_order(
        stage_text,
        'manifest_path = parts_dir / "manifest.json"',
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        "manifest-before-shards order",
    )
    require_order(
        split_text,
        '(output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
        'RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass',
        "split replay order",
    )
    return len(SPLIT_MARKERS) + len(STAGE_MARKERS) + 2


def write_sample_root(root: Path) -> None:
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
    (root / SPLIT_HELPER_PATH).write_text(
        "\n".join(
            (
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "DEFAULT_CHUNK_BYTES = 786_432",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                'metadata = {"filename": f"zig-{target}-{channel}.tar.xz"}',
                'manifest = {',
                '    "filename": f"zig-{target}-{channel}.tar.xz",',
                '    "encoding": "base64",',
                '    "sha256": sha256,',
                '    "size": size,',
                '    "chunk_bytes": chunk_bytes,',
                '    "part_count": part_count,',
                '    "parts_glob": "part-*.b64",',
                '}',
                '(output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
            )
        )
        + "\n",
        encoding="utf-8",
    )
    (root / STAGE_HELPER_PATH).write_text(
        "\n".join(
            (
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                'manifest_path = parts_dir / "manifest.json"',
                'require_manifest_string(manifest, "filename", manifest_path)',
                'require_manifest_string(manifest, "encoding", manifest_path)',
                'require_manifest_string(manifest, "sha256", manifest_path)',
                'require_manifest_int(manifest, "size", manifest_path)',
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                'require_manifest_int(manifest, "part_count", manifest_path)',
                'require_manifest_string(manifest, "parts_glob", manifest_path)',
                'raise ValueError(f"expected shard manifest encoding base64, got {encoding}")',
                'raise ValueError(f"expected shard manifest parts_glob part-*.b64, got {parts_glob}")',
                'shard_path = parts_dir / f"part-{index:03d}.b64"',
                'print("STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=parts_dir")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_stage_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        contract = load_contract(root)
        assert check_helpers(root, contract) == len(SPLIT_MARKERS) + len(STAGE_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_stage_alignment_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                contract = load_contract(root)
                check_helpers(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing split helper marker",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing stage helper marker",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '    "chunk_bytes": chunk_bytes,\n    "part_count": part_count,\n',
                '    "part_count": part_count,\n    "chunk_bytes": chunk_bytes,\n',
                1,
            ),
            encoding="utf-8",
        ),
        "split manifest order",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'require_manifest_int(manifest, "size", manifest_path)\n'
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)\n',
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)\n'
                'require_manifest_int(manifest, "size", manifest_path)\n',
                1,
            ),
            encoding="utf-8",
        ),
        "stage manifest order",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY_PATH).write_text(
            (root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
                1,
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'raise ValueError(f"expected shard manifest parts_glob part-*.b64, got {parts_glob}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "parts_glob",
    )

    print("LANE05_SPLIT_STAGE_ALIGNMENT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper emits a shard packet the stage helper still consumes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact sample root that should satisfy this checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    try:
        root = args.root.resolve()
        contract = load_contract(root)
        marker_count = check_helpers(root, contract)
    except ValueError as exc:
        print("LANE05_SPLIT_STAGE_ALIGNMENT=fail")
        print(f"LANE05_SPLIT_STAGE_ALIGNMENT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_STAGE_ALIGNMENT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_STAGE_ALIGNMENT=pass")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_ROOT={root}")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_SIZE={contract['size']}")
    print(f"LANE05_SPLIT_STAGE_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
