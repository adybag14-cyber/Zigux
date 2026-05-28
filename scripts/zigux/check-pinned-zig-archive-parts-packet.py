#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_FILENAME = f"zig-{EXPECTED_TARGET}-{EXPECTED_CHANNEL}.tar.xz"
EXPECTED_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
EXPECTED_SIZE = 58_159_088


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {relative_path}") from exc


def require_contains(text: str, needle: str, *, source: Path) -> None:
    if needle not in text:
        raise SystemExit(f"{source} is missing required archive-parts marker: {needle}")


def load_policy(root: Path) -> dict[str, object]:
    try:
        policy = json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {POLICY_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {POLICY_PATH}: {exc.msg}") from exc
    if not isinstance(policy, dict):
        raise SystemExit(f"invalid policy payload in {POLICY_PATH}: expected object")
    return policy


def check_policy(root: Path) -> None:
    policy = load_policy(root)
    archive_sha256 = policy.get("archive_sha256")
    upgrade_policy = policy.get("upgrade_policy")
    if policy.get("channel") != EXPECTED_CHANNEL:
        raise SystemExit(f"unexpected Zig channel in {POLICY_PATH}: {policy.get('channel')!r}")
    if policy.get("minimum_version") != EXPECTED_CHANNEL:
        raise SystemExit(f"unexpected Zig minimum_version in {POLICY_PATH}: {policy.get('minimum_version')!r}")
    if not isinstance(archive_sha256, dict):
        raise SystemExit(f"invalid archive_sha256 in {POLICY_PATH}")
    if archive_sha256.get(EXPECTED_TARGET) != EXPECTED_SHA256:
        raise SystemExit(f"missing pinned archive digest for {EXPECTED_TARGET} in {POLICY_PATH}")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in {POLICY_PATH}")
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        raise SystemExit(f"unexpected archive_target_scope in {POLICY_PATH}")


def check_stage_helper(root: Path) -> None:
    helper = read_text(root, STAGE_HELPER_PATH)
    required_markers = [
        "EXPECTED_ARCHIVE_SIZES = {",
        f'"{EXPECTED_TARGET}": {EXPECTED_SIZE:_}',
        "def load_shard_manifest(parts_dir: Path) -> dict[str, object]:",
        "def reconstruct_archive_from_parts(",
        'require_manifest_string(manifest, "filename", manifest_path)',
        'require_manifest_string(manifest, "encoding", manifest_path)',
        'require_manifest_string(manifest, "sha256", manifest_path)',
        'require_manifest_int(manifest, "size", manifest_path)',
        'require_manifest_int(manifest, "part_count", manifest_path)',
        'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
        'require_manifest_string(manifest, "parts_glob", manifest_path)',
        'if parts_glob != "part-*.b64":',
        'shard_path = parts_dir / f"part-{index:03d}.b64"',
        "base64.b64decode(encoded, validate=True)",
        "--parts-dir",
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}",
    ]
    for marker in required_markers:
        require_contains(helper, marker, source=STAGE_HELPER_PATH)


def check_workflow(root: Path) -> None:
    workflow = read_text(root, WORKFLOW_PATH)
    required_markers = [
        'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        'repo_archive_parts_dir="${repo_archive_path}.parts"',
        'if [ ! -d "$repo_archive_parts_dir" ]; then',
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        '--root "$GITHUB_WORKSPACE"',
        '--parts-dir "$repo_archive_parts_dir"',
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org',
        "third_party/**",
    ]
    for marker in required_markers:
        require_contains(workflow, marker, source=WORKFLOW_PATH)


def check_optional_parts_manifest(root: Path) -> None:
    parts_dir = root / "third_party" / f"{EXPECTED_FILENAME}.parts"
    manifest_path = parts_dir / "manifest.json"
    if not parts_dir.exists():
        return
    if not manifest_path.is_file():
        raise SystemExit(f"archive parts directory exists without manifest: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {manifest_path}: {exc.msg}") from exc
    expected = {
        "filename": EXPECTED_FILENAME,
        "encoding": "base64",
        "sha256": EXPECTED_SHA256,
        "size": EXPECTED_SIZE,
        "parts_glob": "part-*.b64",
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            raise SystemExit(f"unexpected {key} in {manifest_path}: {manifest.get(key)!r}")
    part_count = manifest.get("part_count")
    chunk_bytes = manifest.get("chunk_bytes")
    if not isinstance(part_count, int) or part_count <= 0:
        raise SystemExit(f"invalid part_count in {manifest_path}")
    if not isinstance(chunk_bytes, int) or chunk_bytes <= 0:
        raise SystemExit(f"invalid chunk_bytes in {manifest_path}")
    missing = [f"part-{index:03d}.b64" for index in range(part_count) if not (parts_dir / f"part-{index:03d}.b64").is_file()]
    if missing:
        raise SystemExit(f"archive parts manifest references missing shards: {', '.join(missing[:3])}")


def run_check(root: Path) -> None:
    check_policy(root)
    check_stage_helper(root)
    check_workflow(root)
    check_optional_parts_manifest(root)


def write_fixture(root: Path, *, include_manifest: bool = False) -> None:
    (root / POLICY_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / STAGE_HELPER_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / POLICY_PATH).write_text(
        json.dumps(
            {
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA256},
                "upgrade_policy": {"archive_target_scope": [EXPECTED_TARGET]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / STAGE_HELPER_PATH).write_text(
        "\n".join(
            [
                "EXPECTED_ARCHIVE_SIZES = {",
                f'    "{EXPECTED_TARGET}": {EXPECTED_SIZE:_},',
                "}",
                "def load_shard_manifest(parts_dir: Path) -> dict[str, object]: pass",
                "def reconstruct_archive_from_parts(: pass",
                'require_manifest_string(manifest, "filename", manifest_path)',
                'require_manifest_string(manifest, "encoding", manifest_path)',
                'require_manifest_string(manifest, "sha256", manifest_path)',
                'require_manifest_int(manifest, "size", manifest_path)',
                'require_manifest_int(manifest, "part_count", manifest_path)',
                'require_manifest_int(manifest, "chunk_bytes", manifest_path)',
                'require_manifest_string(manifest, "parts_glob", manifest_path)',
                'if parts_glob != "part-*.b64": pass',
                'shard_path = parts_dir / f"part-{index:03d}.b64"',
                "base64.b64decode(encoded, validate=True)",
                "--parts-dir",
                "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / WORKFLOW_PATH).write_text(
        "\n".join(
            [
                'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                'repo_archive_parts_dir="${repo_archive_path}.parts"',
                'if [ ! -d "$repo_archive_parts_dir" ]; then',
                "python3 scripts/zigux/stage-pinned-zig-archive.py",
                '--root "$GITHUB_WORKSPACE"',
                '--parts-dir "$repo_archive_parts_dir"',
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org',
                "third_party/**",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if include_manifest:
        parts_dir = root / "third_party" / f"{EXPECTED_FILENAME}.parts"
        parts_dir.mkdir(parents=True, exist_ok=True)
        (parts_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "filename": EXPECTED_FILENAME,
                    "encoding": "base64",
                    "sha256": EXPECTED_SHA256,
                    "size": EXPECTED_SIZE,
                    "chunk_bytes": 4_194_304,
                    "part_count": 1,
                    "parts_glob": "part-*.b64",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (parts_dir / "part-000.b64").write_text("AA==\n", encoding="utf-8")


def expect_failure(mutator, expected_substring: str) -> None:
    with tempfile.TemporaryDirectory(prefix="archive_parts_packet_fail_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        mutator(root)
        try:
            run_check(root)
        except SystemExit as exc:
            if expected_substring not in str(exc):
                raise AssertionError(f"expected {expected_substring!r} in {exc!s}") from exc
            return
        raise AssertionError("expected checker failure")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="archive_parts_packet_pass_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        run_check(root)
        case_count += 1
    with tempfile.TemporaryDirectory(prefix="archive_parts_packet_manifest_pass_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root, include_manifest=True)
        run_check(root)
        case_count += 1
    expect_failure(lambda root: (root / POLICY_PATH).write_text("{}\n", encoding="utf-8"), "unexpected Zig channel")
    case_count += 1
    expect_failure(lambda root: (root / STAGE_HELPER_PATH).write_text("", encoding="utf-8"), "missing required archive-parts marker")
    case_count += 1
    expect_failure(lambda root: (root / WORKFLOW_PATH).write_text("", encoding="utf-8"), "missing required archive-parts marker")
    case_count += 1
    expect_failure(
        lambda root: (root / "third_party" / f"{EXPECTED_FILENAME}.parts").mkdir(parents=True),
        "archive parts directory exists without manifest",
    )
    case_count += 1
    print("PINNED_ZIG_ARCHIVE_PARTS_PACKET_SELF_TEST=pass")
    print(f"PINNED_ZIG_ARCHIVE_PARTS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check pinned Zig archive parts bootstrap support packet.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    run_check(args.root.resolve())
    print("PINNED_ZIG_ARCHIVE_PARTS_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
