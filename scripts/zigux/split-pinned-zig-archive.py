#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
DEFAULT_CHUNK_BYTES = 786_432
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


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
        "channel": channel,
        "target": target,
        "sha256": normalized_archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive(source: Path, *, expected_size: int, expected_sha: str) -> None:
    if not source.exists():
        raise ValueError(f"missing source archive: {source}")
    if not source.is_file():
        raise ValueError(f"source archive is not a regular file: {source}")
    actual_size = source.stat().st_size
    if actual_size != expected_size:
        raise ValueError(f"expected {source} to be {expected_size} bytes, got {actual_size}")
    actual_sha = compute_sha256(source)
    if actual_sha != expected_sha:
        raise ValueError(f"expected {source} to have sha256 {expected_sha}, got {actual_sha}")


def ensure_clean_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        existing = sorted(path.name for path in output_dir.iterdir())
        if existing:
            raise ValueError(f"output directory must be empty: {output_dir}")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)


def write_manifest(
    output_dir: Path,
    *,
    filename: str,
    sha256: str,
    size: int,
    chunk_bytes: int,
    part_count: int,
) -> Path:
    manifest = {
        "filename": filename,
        "encoding": "base64",
        "sha256": sha256,
        "size": size,
        "chunk_bytes": chunk_bytes,
        "part_count": part_count,
        "parts_glob": "part-*.b64",
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def split_archive(
    source: Path,
    output_dir: Path,
    *,
    expected_size: int,
    expected_sha: str,
    filename: str,
    chunk_bytes: int,
) -> tuple[int, Path]:
    if chunk_bytes <= 0:
        raise ValueError("chunk_bytes must be positive")

    validate_archive(source, expected_size=expected_size, expected_sha=expected_sha)
    ensure_clean_output_dir(output_dir)

    part_count = int(math.ceil(expected_size / chunk_bytes))
    with source.open("rb") as handle:
        for index in range(part_count):
            chunk = handle.read(chunk_bytes)
            if not chunk:
                raise ValueError(f"expected archive data for part {index}, got EOF")
            encoded = base64.b64encode(chunk).decode("ascii")
            (output_dir / f"part-{index:03d}.b64").write_text(encoded + "\n", encoding="utf-8")

        leftover = handle.read(1)
        if leftover:
            raise ValueError("source archive had unexpected trailing bytes after part split")

    manifest_path = write_manifest(
        output_dir,
        filename=filename,
        sha256=expected_sha,
        size=expected_size,
        chunk_bytes=chunk_bytes,
        part_count=part_count,
    )
    return part_count, manifest_path


def reconstruct_archive(parts_dir: Path, destination: Path) -> bytes:
    manifest = json.loads((parts_dir / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("invalid manifest shape")
    expected_count = manifest.get("part_count")
    if not isinstance(expected_count, int) or expected_count <= 0:
        raise ValueError("invalid manifest part_count")

    chunks: list[bytes] = []
    for index in range(expected_count):
        path = parts_dir / f"part-{index:03d}.b64"
        if not path.exists():
            raise ValueError(f"missing expected shard: {path.name}")
        encoded = path.read_text(encoding="utf-8").strip()
        chunks.append(base64.b64decode(encoded, validate=True))

    combined = b"".join(chunks)
    destination.write_bytes(combined)
    return combined


def write_fixture(root: Path, payload: bytes) -> tuple[Path, Path]:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)

    source_path = root / "sources" / "zig-source.tar.xz"
    source_path.write_bytes(payload)
    return root, source_path


def run_self_test() -> int:
    case_count = 0

    def write_policy(root: Path, sha256: str, size: int) -> None:
        (root / TOOLCHAIN_POLICY).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": sha256},
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
        EXPECTED_ARCHIVE_SIZES["x86_64-linux"] = size

    payload = (b"lane05-archive-payload-" * 64)[:4097]
    with tempfile.TemporaryDirectory(prefix="split_archive_pass_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir), payload)
        expected_sha = hashlib.sha256(payload).hexdigest()
        write_policy(root, expected_sha, len(payload))
        metadata = load_policy(root)
        output_dir = root / "out"
        part_count, manifest_path = split_archive(
            source,
            output_dir,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
            filename=str(metadata["filename"]),
            chunk_bytes=1024,
        )
        assert part_count == math.ceil(len(payload) / 1024)
        assert manifest_path.exists()
        rebuilt = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")
        assert rebuilt == payload
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="split_archive_fail_") as tmp_dir:
            root, source = write_fixture(Path(tmp_dir), payload)
            expected_sha = hashlib.sha256(payload).hexdigest()
            write_policy(root, expected_sha, len(payload))
            metadata = load_policy(root)
            output_dir = root / "out"
            mutator(root, source, output_dir, metadata)
            try:
                split_archive(
                    source,
                    output_dir,
                    expected_size=int(metadata["size"]),
                    expected_sha=str(metadata["sha256"]),
                    filename=str(metadata["filename"]),
                    chunk_bytes=1024,
                )
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected split_archive to fail")

    expect_failure(
        lambda root, source, output_dir, metadata: output_dir.mkdir(parents=True, exist_ok=True)
        or (output_dir / "existing.txt").write_text("busy\n", encoding="utf-8"),
        "output directory must be empty",
    )
    expect_failure(
        lambda root, source, output_dir, metadata: source.write_bytes(payload[:-1]),
        "to be",
    )
    expect_failure(
        lambda root, source, output_dir, metadata: source.write_bytes(b"0" * len(payload)),
        "to have sha256",
    )
    with tempfile.TemporaryDirectory(prefix="split_archive_chunk_bytes_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir), payload)
        expected_sha = hashlib.sha256(payload).hexdigest()
        write_policy(root, expected_sha, len(payload))
        metadata = load_policy(root)
        try:
            split_archive(
                source,
                root / "out",
                expected_size=int(metadata["size"]),
                expected_sha=str(metadata["sha256"]),
                filename=str(metadata["filename"]),
                chunk_bytes=0,
            )
        except ValueError as exc:
            assert "chunk_bytes must be positive" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected non-positive chunk_bytes failure")

    with tempfile.TemporaryDirectory(prefix="split_archive_manifest_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir), payload)
        expected_sha = hashlib.sha256(payload).hexdigest()
        write_policy(root, expected_sha, len(payload))
        metadata = load_policy(root)
        output_dir = root / "out"
        split_archive(
            source,
            output_dir,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
            filename=str(metadata["filename"]),
            chunk_bytes=1024,
        )
        middle_index = max(0, (len(list(output_dir.glob("part-*.b64"))) - 1) // 2)
        (output_dir / f"part-{middle_index:03d}.b64").unlink()
        try:
            reconstruct_archive(output_dir, root / "rebuilt.tar.xz")
        except ValueError as exc:
            assert "missing expected shard" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing shard failure")

    with tempfile.TemporaryDirectory(prefix="split_archive_invalid_b64_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir), payload)
        expected_sha = hashlib.sha256(payload).hexdigest()
        write_policy(root, expected_sha, len(payload))
        metadata = load_policy(root)
        output_dir = root / "out"
        split_archive(
            source,
            output_dir,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
            filename=str(metadata["filename"]),
            chunk_bytes=1024,
        )
        (output_dir / "part-000.b64").write_text("not base64!\n", encoding="utf-8")
        try:
            reconstruct_archive(output_dir, root / "rebuilt.tar.xz")
        except Exception:
            case_count += 1
        else:
            raise AssertionError("expected invalid base64 failure")

    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split the pinned Zig archive into base64 shards for connector-friendly publication."
    )
    parser.add_argument("--source", type=Path, help="Path to the validated pinned Zig archive payload.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root used to load scripts/zigux/zig-toolchain-policy.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory that will receive manifest.json plus part-XXX.b64 files.",
    )
    parser.add_argument(
        "--chunk-bytes",
        type=int,
        default=DEFAULT_CHUNK_BYTES,
        help="Raw binary bytes per shard before base64 encoding.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in shard helper coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.source is None or args.output_dir is None:
        raise SystemExit("--source and --output-dir are required unless --self-test is used")

    root = args.root.resolve()
    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    try:
        metadata = load_policy(root)
        part_count, manifest_path = split_archive(
            source,
            output_dir,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
            filename=str(metadata["filename"]),
            chunk_bytes=args.chunk_bytes,
        )
    except ValueError as exc:
        print("SPLIT_PINNED_ZIG_ARCHIVE=fail")
        print(f"SPLIT_PINNED_ZIG_ARCHIVE_ROOT={root}")
        print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")
        print(f"SPLIT_PINNED_ZIG_ARCHIVE_NOTE={exc}")
        return 1

    print("SPLIT_PINNED_ZIG_ARCHIVE=pass")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_ROOT={root}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata['sha256']}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SIZE={metadata['size']}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_CHUNK_BYTES={args.chunk_bytes}")
    print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
