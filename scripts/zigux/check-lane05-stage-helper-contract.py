#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'THIRD_PARTY_DIR = Path("third_party")',
    'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(',
    'def load_shard_manifest(parts_dir: Path) -> dict[str, object]:',
    'def reconstruct_archive_from_parts(',
    'manifest_path = parts_dir / "manifest.json"',
    'filename = require_manifest_string(manifest, "filename", manifest_path)',
    'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
    'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
    'size = require_manifest_int(manifest, "size", manifest_path)',
    'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
    'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
    'if filename != expected_filename:',
    'if encoding != "base64":',
    'if sha256 != expected_sha:',
    'if size != expected_size:',
    'if parts_glob != "part-*.b64":',
    'for index in range(part_count):',
    'shard_path = parts_dir / f"part-{index:03d}.b64"',
    'raise ValueError(f"missing expected shard: {shard_path.name}")',
    'raise ValueError(f"invalid base64 shard: {shard_path.name}")',
    'raise ValueError("exactly one of source or parts_dir must be provided")',
    'actual_sha = reconstruct_archive_from_parts(',
    'return reconstructed_source, "parts_dir", temp_dir',
    'input_mode == "parts_dir"',
    'parser.add_argument(',
    '"--parts-dir",',
    'help="Directory containing manifest.json plus part-XXX.b64 shard files."',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
    'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass',
    'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=',
    'STAGE_PINNED_ZIG_ARCHIVE=pass',
)

EXACT_ONCE_MARKERS = (
    'def reconstruct_archive_from_parts(',
    '"--parts-dir",',
    'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}',
    'STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass',
    'STAGE_PINNED_ZIG_ARCHIVE=pass',
)

ORDERED_MARKERS = (
    (
        'filename = require_manifest_string(manifest, "filename", manifest_path)',
        'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
    ),
    (
        'encoding = require_manifest_string(manifest, "encoding", manifest_path)',
        'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
    ),
    (
        'sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
        'size = require_manifest_int(manifest, "size", manifest_path)',
    ),
    (
        'size = require_manifest_int(manifest, "size", manifest_path)',
        'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
    ),
    (
        'part_count = require_manifest_int(manifest, "part_count", manifest_path)',
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
    ),
    (
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        'parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
    ),
    (
        'if filename != expected_filename:',
        'if encoding != "base64":',
    ),
    (
        'if encoding != "base64":',
        'if sha256 != expected_sha:',
    ),
    (
        'if sha256 != expected_sha:',
        'if size != expected_size:',
    ),
    (
        'if size != expected_size:',
        'if parts_glob != "part-*.b64":',
    ),
    (
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        'raise ValueError(f"missing expected shard: {shard_path.name}")',
    ),
    (
        'actual_sha = reconstruct_archive_from_parts(',
        'return reconstructed_source, "parts_dir", temp_dir',
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
    policy_path = root / TOOLCHAIN_POLICY
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
        raise ValueError(f"lane05 stage-helper contract missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 stage-helper contract expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"lane05 stage-helper contract expected {label} `{earlier}` before `{later}`")


def check_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / STAGE_HELPER)

    for marker in HELPER_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "helper marker")

    require_marker(helper_text, f'"{contract["target"]}": {contract["size"]:_},', "target-size marker")
    require_marker(
        helper_text,
        'duplicate_archive_name("zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")',
        "duplicate-suffix guard marker",
    )

    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "manifest or reconstruction order")

    return len(HELPER_MARKERS) + 2


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / TOOLCHAIN_POLICY).write_text(
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
    (root / STAGE_HELPER).write_text(
        "\n".join(
            (
                "from pathlib import Path",
                "import re",
                "",
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'THIRD_PARTY_DIR = Path("third_party")',
                'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \\\\((?P<copy>\\\\d+)\\\\)(?P<suffix>\\\\.tar\\\\.xz)$")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                "",
                'def load_shard_manifest(parts_dir: Path) -> dict[str, object]:',
                '    manifest_path = parts_dir / "manifest.json"',
                '    return {"manifest_path": manifest_path}',
                "",
                'def reconstruct_archive_from_parts(parts_dir: Path, destination: Path, *, expected_filename: str, expected_sha: str, expected_size: int) -> str:',
                '    manifest_path = parts_dir / "manifest.json"',
                '    manifest = load_shard_manifest(parts_dir)',
                '    filename = require_manifest_string(manifest, "filename", manifest_path)',
                '    encoding = require_manifest_string(manifest, "encoding", manifest_path)',
                '    sha256 = require_manifest_string(manifest, "sha256", manifest_path)',
                '    size = require_manifest_int(manifest, "size", manifest_path)',
                '    part_count = require_manifest_int(manifest, "part_count", manifest_path)',
                '    require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                '    parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)',
                '    if filename != expected_filename:',
                '        raise ValueError("filename")',
                '    if encoding != "base64":',
                '        raise ValueError("encoding")',
                '    if sha256 != expected_sha:',
                '        raise ValueError("sha")',
                '    if size != expected_size:',
                '        raise ValueError("size")',
                '    if parts_glob != "part-*.b64":',
                '        raise ValueError("parts_glob")',
                '    for index in range(part_count):',
                '        shard_path = parts_dir / f"part-{index:03d}.b64"',
                '        if not shard_path.exists():',
                '            raise ValueError(f"missing expected shard: {shard_path.name}")',
                '        raise ValueError(f"invalid base64 shard: {shard_path.name}")',
                '    return "sha"',
                "",
                'def resolve_source_archive(root: Path, *, source: Path | None, parts_dir: Path | None, metadata: dict[str, object]) -> tuple[Path, str, object | None]:',
                '    if (source is None) == (parts_dir is None):',
                '        raise ValueError("exactly one of source or parts_dir must be provided")',
                '    actual_sha = reconstruct_archive_from_parts(',
                '        parts_dir,',
                '        root / "rebuilt.tar.xz",',
                '        expected_filename=str(metadata["filename"]),',
                '        expected_sha=str(metadata["sha256"]),',
                '        expected_size=int(metadata["size"]),',
                '    )',
                '    return reconstructed_source, "parts_dir", temp_dir',
                "",
                'assert input_mode == "parts_dir"',
                'duplicate_archive_name("zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")',
                "parser = argparse.ArgumentParser()",
                "parser.add_argument(",
                '    "--parts-dir",',
                '    help="Directory containing manifest.json plus part-XXX.b64 shard files."',
                ")",
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=9")',
                'print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = load_contract(root)
        assert check_helper(root, contract) == len(HELPER_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                contract = load_contract(root)
                check_helper(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                'if parts_glob != "part-*.b64":\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "parts_glob",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                'print("STAGE_PINNED_ZIG_ARCHIVE=pass")\n',
                'print("STAGE_PINNED_ZIG_ARCHIVE=pass")\nprint("STAGE_PINNED_ZIG_ARCHIVE=pass")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                '    if encoding != "base64":\n        raise ValueError("encoding")\n    if sha256 != expected_sha:\n',
                '    if sha256 != expected_sha:\n        raise ValueError("sha")\n    if encoding != "base64":\n        raise ValueError("encoding")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "manifest or reconstruction order",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY).write_text(
            (root / TOOLCHAIN_POLICY).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY).write_text(
            (root / TOOLCHAIN_POLICY).read_text(encoding="utf-8").replace(
                "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "archive_sha256[x86_64-linux]",
    )

    print("LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 stage helper against the pinned archive shard contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract = load_contract(root)
        marker_count = check_helper(root, contract)
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
    print(f"LANE05_STAGE_HELPER_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
