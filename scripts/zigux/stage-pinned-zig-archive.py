#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_DIR = Path("third_party")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58159088,
}
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


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
        payload = json.loads(
            policy_path.read_text(encoding="utf-8"),
            object_pairs_hook=DuplicateTrackingDict,
        )
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:
        raise ValueError(
            f"duplicate toolchain policy keys in {policy_path}: " + ", ".join(payload.duplicate_keys)
        )

    channel = require_non_empty_string(payload.get("channel"), "channel", policy_path)
    minimum_version = require_non_empty_string(
        payload.get("minimum_version"), "minimum_version", policy_path
    )
    if minimum_version != channel:
        upgrade_policy = payload.get("upgrade_policy")
        lockstep = isinstance(upgrade_policy, dict) and upgrade_policy.get("channel_minimum_lockstep")
        if lockstep:
            raise ValueError(
                f"minimum_version must match channel when channel_minimum_lockstep is true in {policy_path}"
            )

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise ValueError(f"invalid archive_sha256 in {policy_path}")
    if isinstance(archive_sha256, DuplicateTrackingDict) and archive_sha256.duplicate_keys:
        raise ValueError(
            f"duplicate archive_sha256 targets in {policy_path}: "
            + ", ".join(archive_sha256.duplicate_keys)
        )

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
    if isinstance(upgrade_policy, DuplicateTrackingDict) and upgrade_policy.duplicate_keys:
        raise ValueError(
            f"duplicate upgrade_policy keys in {policy_path}: "
            + ", ".join(upgrade_policy.duplicate_keys)
        )

    archive_targets = require_string_list(
        upgrade_policy.get("archive_target_scope"),
        "archive_target_scope",
        policy_path,
    )
    if len(archive_targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}, got {len(archive_targets)}")
    if archive_targets[0] not in normalized_archives:
        raise ValueError(
            f"archive_target_scope references missing archive_sha256 entry in {policy_path}: {archive_targets[0]}"
        )

    target = archive_targets[0]
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


def duplicate_archive_name(expected_filename: str) -> str:
    stem = expected_filename[: -len(".tar.xz")]
    return f"{stem} (1).tar.xz"


def duplicate_source_fixture_name(expected_filename: str) -> str:
    return duplicate_archive_name(expected_filename)


def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:
    match = ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)
    if match is None:
        return False
    return match.group("stem") == expected_filename[: -len(".tar.xz")]


def validate_source_archive(source: Path, *, expected_size: int, expected_sha: str) -> str:
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
    return actual_sha


def require_clean_third_party(root: Path, expected_filename: str) -> None:
    third_party_dir = root / THIRD_PARTY_DIR
    if not third_party_dir.exists():
        return

    duplicate_names = sorted(
        path.name
        for path in third_party_dir.glob("*.tar.xz")
        if archive_name_has_duplicate_suffix(path.name, expected_filename)
    )
    if duplicate_names:
        raise ValueError(
            "third_party contains duplicate-suffix archive copies: " + ", ".join(duplicate_names)
        )
    if duplicate_archive_name(expected_filename) in duplicate_names:
        raise ValueError(f"third_party must not contain {duplicate_archive_name(expected_filename)}")


def inspect_destination(
    source: Path,
    destination: Path,
    *,
    expected_size: int,
    expected_sha: str,
    actual_sha: str,
) -> tuple[str, str] | None:
    if not destination.exists():
        return None
    if not destination.is_file():
        raise ValueError(f"destination archive is not a regular file: {destination}")

    destination_sha = validate_source_archive(
        destination,
        expected_size=expected_size,
        expected_sha=expected_sha,
    )
    if source.resolve() == destination.resolve(strict=False):
        return ("already_present", destination_sha)
    if destination_sha != actual_sha:
        raise ValueError(
            f"destination archive {destination} already exists with different bytes than {source}"
        )
    return ("already_present", destination_sha)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def load_shard_manifest(parts_dir: Path) -> dict[str, object]:
    manifest_path = parts_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing shard manifest: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid shard manifest JSON in {manifest_path}: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"invalid shard manifest payload in {manifest_path}: expected object")
    return manifest


def require_manifest_string(manifest: dict[str, object], key: str, manifest_path: Path) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid shard manifest {key} in {manifest_path}")
    return value.strip()


def require_manifest_int(manifest: dict[str, object], key: str, manifest_path: Path) -> int:
    value = manifest.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"invalid shard manifest {key} in {manifest_path}")
    return value


def reconstruct_archive_from_parts(
    parts_dir: Path,
    destination: Path,
    *,
    expected_filename: str,
    expected_sha: str,
    expected_size: int,
) -> str:
    manifest_path = parts_dir / "manifest.json"
    manifest = load_shard_manifest(parts_dir)
    filename = require_manifest_string(manifest, "filename", manifest_path)
    encoding = require_manifest_string(manifest, "encoding", manifest_path)
    sha256 = require_manifest_string(manifest, "sha256", manifest_path)
    size = require_manifest_int(manifest, "size", manifest_path)
    part_count = require_manifest_int(manifest, "part_count", manifest_path)
    require_manifest_int(manifest, "chunk_bytes", manifest_path)
    parts_glob = require_manifest_string(manifest, "parts_glob", manifest_path)

    if filename != expected_filename:
        raise ValueError(
            f"expected shard manifest filename {expected_filename}, got {filename}"
        )
    if encoding != "base64":
        raise ValueError(f"expected shard manifest encoding base64, got {encoding}")
    if sha256 != expected_sha:
        raise ValueError(f"expected shard manifest sha256 {expected_sha}, got {sha256}")
    if size != expected_size:
        raise ValueError(f"expected shard manifest size {expected_size}, got {size}")
    if parts_glob != "part-*.b64":
        raise ValueError(f"expected shard manifest parts_glob part-*.b64, got {parts_glob}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        for index in range(part_count):
            shard_path = parts_dir / f"part-{index:03d}.b64"
            if not shard_path.exists():
                raise ValueError(f"missing expected shard: {shard_path.name}")
            encoded = shard_path.read_text(encoding="utf-8").strip()
            try:
                chunk = base64.b64decode(encoded, validate=True)
            except binascii.Error as exc:
                raise ValueError(f"invalid base64 shard: {shard_path.name}") from exc
            handle.write(chunk)

    return validate_source_archive(
        destination,
        expected_size=expected_size,
        expected_sha=expected_sha,
    )


def resolve_source_archive(
    root: Path,
    *,
    source: Path | None,
    parts_dir: Path | None,
    metadata: dict[str, object],
) -> tuple[Path, str, tempfile.TemporaryDirectory[str] | None]:
    if (source is None) == (parts_dir is None):
        raise ValueError("exactly one of source or parts_dir must be provided")

    if source is not None:
        actual_sha = validate_source_archive(
            source,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
        )
        return source, "source", None

    assert parts_dir is not None
    temp_dir = tempfile.TemporaryDirectory(prefix="stage_archive_parts_")
    reconstructed_source = Path(temp_dir.name) / str(metadata["filename"])
    actual_sha = reconstruct_archive_from_parts(
        parts_dir,
        reconstructed_source,
        expected_filename=str(metadata["filename"]),
        expected_sha=str(metadata["sha256"]),
        expected_size=int(metadata["size"]),
    )
    return reconstructed_source, "parts_dir", temp_dir


def stage_archive(
    root: Path,
    source: Path | None,
    *,
    parts_dir: Path | None,
    check_only: bool,
) -> tuple[dict[str, object], str, str, Path, str]:
    metadata = load_policy(root)
    destination = root / THIRD_PARTY_DIR / str(metadata["filename"])
    require_clean_third_party(root, str(metadata["filename"]))
    resolved_source, input_mode, cleanup = resolve_source_archive(
        root,
        source=source,
        parts_dir=parts_dir,
        metadata=metadata,
    )
    try:
        actual_sha = validate_source_archive(
            resolved_source,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
        )

        existing_destination = inspect_destination(
            resolved_source,
            destination,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
            actual_sha=actual_sha,
        )
        if check_only:
            return (
                metadata,
                "checked",
                existing_destination[1] if existing_destination else actual_sha,
                destination,
                input_mode,
            )
        if existing_destination is not None:
            return (
                metadata,
                existing_destination[0],
                existing_destination[1],
                destination,
                input_mode,
            )

        copy_file(resolved_source, destination)
        staged_sha = validate_source_archive(
            destination,
            expected_size=int(metadata["size"]),
            expected_sha=str(metadata["sha256"]),
        )
        return metadata, "staged", staged_sha, destination, input_mode
    finally:
        if cleanup is not None:
            cleanup.cleanup()


def write_fixture(root: Path, source_bytes: bytes = b"x", source_size: int | None = None) -> tuple[Path, Path]:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)

    size = source_size if source_size is not None else EXPECTED_ARCHIVE_SIZES["x86_64-linux"]
    source_path = root / "sources" / "zig-source.tar.xz"
    repeat_count = (size + len(source_bytes) - 1) // len(source_bytes)
    source_path.write_bytes((source_bytes * repeat_count)[:size])
    return root, source_path


def write_parts_fixture(
    parts_dir: Path,
    payload: bytes,
    *,
    filename: str,
    sha256: str,
    chunk_bytes: int,
) -> None:
    parts_dir.mkdir(parents=True, exist_ok=True)
    chunks = [payload[i : i + chunk_bytes] for i in range(0, len(payload), chunk_bytes)]
    manifest = {
        "filename": filename,
        "encoding": "base64",
        "sha256": sha256,
        "size": len(payload),
        "chunk_bytes": chunk_bytes,
        "part_count": len(chunks),
        "parts_glob": "part-*.b64",
    }
    (parts_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for index, chunk in enumerate(chunks):
        (parts_dir / f"part-{index:03d}.b64").write_text(
            base64.b64encode(chunk).decode("ascii") + "\n",
            encoding="utf-8",
        )


def run_self_test() -> int:
    case_count = 0

    def write_policy(root: Path, sha256: str) -> None:
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
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir))
        expected_sha = compute_sha256(source)
        write_policy(root, expected_sha)

        metadata, status, actual_sha, destination, input_mode = stage_archive(
            root,
            source,
            parts_dir=None,
            check_only=False,
        )
        assert status == "staged"
        assert actual_sha == expected_sha
        assert destination.read_bytes() == source.read_bytes()
        assert metadata["filename"] == "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        assert input_mode == "source"
        case_count += 1

        _, status, actual_sha, destination, input_mode = stage_archive(
            root,
            source,
            parts_dir=None,
            check_only=False,
        )
        assert status == "already_present"
        assert actual_sha == expected_sha
        assert input_mode == "source"
        case_count += 1

        _, status, actual_sha, destination, input_mode = stage_archive(
            root,
            source,
            parts_dir=None,
            check_only=True,
        )
        assert status == "checked"
        assert actual_sha == expected_sha
        assert input_mode == "source"
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="stage_archive_external_duplicate_source_pass_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir))
        expected_sha = compute_sha256(source)
        write_policy(root, expected_sha)
        metadata = load_policy(root)
        source_with_duplicate_name = source.with_name(
            duplicate_source_fixture_name(str(metadata["filename"])
        )
        source.rename(source_with_duplicate_name)

        _, status, actual_sha, destination, input_mode = stage_archive(
            root,
            source_with_duplicate_name,
            parts_dir=None,
            check_only=False,
        )
        assert status == "staged"
        assert actual_sha == expected_sha
        assert destination.name == metadata["filename"]
        assert destination.read_bytes() == source_with_duplicate_name.read_bytes()
        assert input_mode == "source"
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir))
        expected_sha = compute_sha256(source)
        write_policy(root, expected_sha)
        metadata = load_policy(root)
        parts_dir = root / "parts"
        write_parts_fixture(
            parts_dir,
            source.read_bytes(),
            filename=str(metadata["filename"]),
            sha256=str(metadata["sha256"]),
            chunk_bytes=786432,
        )
        _, status, actual_sha, destination, input_mode = stage_archive(
            root,
            None,
            parts_dir=parts_dir,
            check_only=False,
        )
        assert status == "staged"
        assert actual_sha == expected_sha
        assert destination.read_bytes() == source.read_bytes()
        assert input_mode == "parts_dir"
        case_count += 1

    def expect_failure(
        *,
        source_bytes: bytes = b"x",
        source_size: int | None = None,
        mutator=None,
        expected_substring: str,
        check_only: bool = True,
        use_parts_dir: bool = False,
    ) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="stage_archive_fail_") as tmp_dir:
            root, source = write_fixture(Path(tmp_dir), source_bytes=source_bytes, source_size=source_size)
            expected_sha = compute_sha256(source)
            write_policy(root, expected_sha)
            parts_dir: Path | None = None
            if use_parts_dir:
                metadata = load_policy(root)
                parts_dir = root / "parts"
                write_parts_fixture(
                    parts_dir,
                    source.read_bytes(),
                    filename=str(metadata["filename"]),
                    sha256=str(metadata["sha256"]),
                    chunk_bytes=1024,
                )
            if mutator is not None:
                mutator(root, source, expected_sha, parts_dir)
            try:
                stage_archive(
                    root,
                    None if use_parts_dir else source,
                    parts_dir=parts_dir if use_parts_dir else None,
                    check_only=check_only,
                )
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected stage_archive to fail")

    expect_failure(source_size=1, expected_substring="to be 58159088 bytes, got 1")
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (root / TOOLCHAIN_POLICY).write_text(
            (root / TOOLCHAIN_POLICY).read_text(encoding="utf-8").replace(expected_sha, "3" * 64),
            encoding="utf-8",
        ),
        expected_substring="to have sha256",
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (
            root / "third_party" / duplicate_archive_name("zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")
        ).write_bytes(b"x"),
        expected_substring="duplicate-suffix archive copies",
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (
            root / "third_party" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        ).mkdir(),
        expected_substring="destination archive is not a regular file",
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (
            root / "third_party" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        ).write_bytes(b"y" * EXPECTED_ARCHIVE_SIZES["x86_64-linux"]),
        expected_substring="to have sha256",
        check_only=False,
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (root / TOOLCHAIN_POLICY).write_text(
            '{"phase":"Phase 2","phase":"Phase 3","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"'
            + expected_sha
            + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate"]}}\n',
            encoding="utf-8",
        ),
        expected_substring="duplicate toolchain policy keys",
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (parts_dir / "manifest.json").unlink(),
        expected_substring="missing shard manifest",
        use_parts_dir=True,
        check_only=False,
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (parts_dir / "manifest.json").write_text(
            (parts_dir / "manifest.json").read_text(encoding="utf-8").replace(
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
                "zig-aarch64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
                1,
            ),
            encoding="utf-8",
        ),
        expected_substring="expected shard manifest filename",
        use_parts_dir=True,
        check_only=False,
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (parts_dir / "part-001.b64").unlink(),
        expected_substring="missing expected shard",
        use_parts_dir=True,
        check_only=False,
    )
    expect_failure(
        mutator=lambda root, source, expected_sha, parts_dir: (parts_dir / "part-000.b64").write_text(
            "not base64!\n",
            encoding="utf-8",
        ),
        expected_substring="invalid base64 shard",
        use_parts_dir=True,
        check_only=False,
    )

    print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and optionally stage the pinned Zig archive into third_party."
    )
    parser.add_argument("--source", type=Path, help="Path to the candidate Zig archive payload.")
    parser.add_argument(
        "--parts-dir",
        type=Path,
        help="Directory containing manifest.json plus part-XXX.b64 shard files.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate and stage against. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate the candidate archive without copying it into third_party.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage for staging and failure cases.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if (args.source is None) == (args.parts_dir is None):
        raise SystemExit("exactly one of --source or --parts-dir is required unless --self-test is used")

    root = args.root.resolve()
    source = args.source.resolve() if args.source is not None else None
    parts_dir = args.parts_dir.resolve() if args.parts_dir is not None else None
    try:
        metadata, status, actual_sha, destination, input_mode = stage_archive(
            root,
            source,
            parts_dir=parts_dir,
            check_only=args.check_only,
        )
    except ValueError as exc:
        print("STAGE_PINNED_ZIG_ARCHIVE=fail")
        print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")
        if source is not None:
            print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")
        if parts_dir is not None:
            print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")
        print(f"STAGE_PINNED_ZIG_ARCHIVE_NOTE={exc}")
        return 1

    print("STAGE_PINNED_ZIG_ARCHIVE=pass")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")
    if source is not None:
        print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")
    if parts_dir is not None:
        print(f"STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_TARGET={metadata['target']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata['size']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())