#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_DIR = Path("third_party")
EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {label}")
    return value.strip()


def require_positive_int(value: object, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"invalid {label}")
    return value


def load_policy_metadata(root: Path) -> dict[str, object]:
    policy = read_json_object(root / TOOLCHAIN_POLICY)
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in {root / TOOLCHAIN_POLICY}")

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in {root / TOOLCHAIN_POLICY}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or len(archive_target_scope) != 1:
        raise SystemExit(
            f"expected exactly one archive_target_scope entry in {root / TOOLCHAIN_POLICY}"
        )

    target = require_string(archive_target_scope[0], "archive target")
    channel = require_string(policy.get("channel"), "channel")
    digest = require_string(archive_sha256.get(target), f"archive_sha256[{target}]")
    optional_size = policy.get("archive_size_bytes")
    if optional_size is not None:
        if not isinstance(optional_size, int) or optional_size <= 0:
            raise SystemExit(f"invalid archive_size_bytes in {root / TOOLCHAIN_POLICY}")
        expected_size = optional_size
    else:
        if target not in EXPECTED_ARCHIVE_SIZES:
            raise SystemExit(f"missing expected archive size for {target}")
        expected_size = EXPECTED_ARCHIVE_SIZES[target]

    filename = f"zig-{target}-{channel}.tar.xz"
    return {
        "target": target,
        "filename": filename,
        "sha256": digest,
        "size": expected_size,
    }


def default_parts_dir(root: Path, filename: str) -> Path:
    return root / THIRD_PARTY_DIR / f"{filename}.parts"


def validate_packet(
    root: Path,
    parts_dir: Path,
    *,
    allow_missing: bool,
) -> tuple[str, dict[str, object]]:
    metadata = load_policy_metadata(root)
    if not parts_dir.exists():
        if allow_missing:
            return "missing_allowed", metadata
        raise SystemExit(f"required packet directory missing: {parts_dir}")
    if not parts_dir.is_dir():
        raise SystemExit(f"packet path is not a directory: {parts_dir}")

    manifest_path = parts_dir / "manifest.json"
    manifest = read_json_object(manifest_path)
    filename = require_string(manifest.get("filename"), "manifest filename")
    encoding = require_string(manifest.get("encoding"), "manifest encoding")
    sha256 = require_string(manifest.get("sha256"), "manifest sha256")
    size = require_positive_int(manifest.get("size"), "manifest size")
    chunk_bytes = require_positive_int(manifest.get("chunk_bytes"), "manifest chunk_bytes")
    part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")
    parts_glob = require_string(manifest.get("parts_glob"), "manifest parts_glob")

    if filename != metadata["filename"]:
        raise SystemExit(
            f"packet filename mismatch: expected {metadata['filename']}, got {filename}"
        )
    if encoding != "base64":
        raise SystemExit(f"packet encoding mismatch: expected base64, got {encoding}")
    if sha256 != metadata["sha256"]:
        raise SystemExit(
            f"packet sha256 mismatch: expected {metadata['sha256']}, got {sha256}"
        )
    if size != metadata["size"]:
        raise SystemExit(f"packet size mismatch: expected {metadata['size']}, got {size}")
    if parts_glob != "part-*.b64":
        raise SystemExit(f"packet parts_glob mismatch: expected part-*.b64, got {parts_glob}")

    expected_part_count = (size + chunk_bytes - 1) // chunk_bytes
    if part_count != expected_part_count:
        raise SystemExit(
            f"packet part_count mismatch: expected {expected_part_count}, got {part_count}"
        )

    expected_names = {f"part-{index:03d}.b64" for index in range(part_count)}
    actual_names = {path.name for path in parts_dir.glob("part-*.b64")}
    missing_names = sorted(expected_names - actual_names)
    extra_names = sorted(actual_names - expected_names)
    if missing_names:
        raise SystemExit("packet missing shard files: " + ", ".join(missing_names))
    if extra_names:
        raise SystemExit("packet has unexpected shard files: " + ", ".join(extra_names))

    other_names = sorted(
        path.name for path in parts_dir.iterdir() if path.name not in expected_names | {"manifest.json"}
    )
    if other_names:
        raise SystemExit("packet has unexpected non-shard files: " + ", ".join(other_names))

    digest = hashlib.sha256()
    total_size = 0
    for index in range(part_count):
        part_path = parts_dir / f"part-{index:03d}.b64"
        encoded = part_path.read_text(encoding="utf-8").strip()
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except binascii.Error as exc:
            raise SystemExit(f"packet shard is not valid base64: {part_path.name}") from exc
        if index < part_count - 1 and len(decoded) != chunk_bytes:
            raise SystemExit(
                f"packet shard size mismatch for {part_path.name}: expected {chunk_bytes}, got {len(decoded)}"
            )
        if index == part_count - 1 and not 0 < len(decoded) <= chunk_bytes:
            raise SystemExit(
                f"packet final shard size mismatch for {part_path.name}: got {len(decoded)}"
            )
        total_size += len(decoded)
        digest.update(decoded)

    if total_size != size:
        raise SystemExit(f"packet decoded size mismatch: expected {size}, got {total_size}")
    actual_sha256 = digest.hexdigest()
    if actual_sha256 != sha256:
        raise SystemExit(
            f"packet decoded sha256 mismatch: expected {sha256}, got {actual_sha256}"
        )

    return "verified", {
        **metadata,
        "chunk_bytes": chunk_bytes,
        "part_count": part_count,
        "parts_dir": str(parts_dir),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_policy(root: Path, *, filename_sha256: str, size: int) -> None:
    write_text(
        root / TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_size_bytes": size,
                "archive_sha256": {"x86_64-linux": filename_sha256},
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
    write_text(parts_dir / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    for index, chunk in enumerate(chunks):
        write_text(
            parts_dir / f"part-{index:03d}.b64",
            base64.b64encode(chunk).decode("ascii") + "\n",
        )


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 9
    payload = (b"zigux-lane05-packet-" * 200) + b"tail"
    sha256 = hashlib.sha256(payload).hexdigest()
    chunk_bytes = 1024
    filename = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"

    with tempfile.TemporaryDirectory(prefix="lane05_parts_packet_pass_") as tmp_dir:
        root = Path(tmp_dir)
        write_text(root / "scripts" / "zigux" / "placeholder.txt", "")
        write_policy(root, filename_sha256=sha256, size=len(payload))
        parts_dir = default_parts_dir(root, filename)
        write_parts_fixture(parts_dir, payload, filename=filename, sha256=sha256, chunk_bytes=chunk_bytes)

        status, validated = validate_packet(root, parts_dir, allow_missing=False)
        assert status == "verified"
        assert validated["part_count"] == (len(payload) + chunk_bytes - 1) // chunk_bytes
        checks_run += 1

        missing_dir = root / "missing.parts"
        status, _ = validate_packet(root, missing_dir, allow_missing=True)
        assert status == "missing_allowed"
        checks_run += 1

        try:
            validate_packet(root, missing_dir, allow_missing=False)
        except SystemExit as exc:
            assert "required packet directory missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing parts dir did not fail")

        manifest_path = parts_dir / "manifest.json"
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["filename"] = "wrong.tar.xz"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet filename mismatch" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("wrong filename did not fail")
        write_text(manifest_path, original_manifest)

        (parts_dir / "part-000.b64").unlink()
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet missing shard files" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing shard did not fail")
        write_parts_fixture(parts_dir, payload, filename=filename, sha256=sha256, chunk_bytes=chunk_bytes)

        write_text(parts_dir / "part-999.b64", "QQ==\n")
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet has unexpected shard files" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("extra shard did not fail")
        (parts_dir / "part-999.b64").unlink()

        write_text(parts_dir / "part-000.b64", "not-base64\n")
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet shard is not valid base64" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid base64 did not fail")
        write_parts_fixture(parts_dir, payload, filename=filename, sha256=sha256, chunk_bytes=chunk_bytes)

        write_text(parts_dir / "note.txt", "unexpected\n")
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet has unexpected non-shard files" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unexpected file did not fail")
        (parts_dir / "note.txt").unlink()

        manifest = json.loads(read_text(manifest_path))
        manifest["part_count"] += 1
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        try:
            validate_packet(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "packet part_count mismatch" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("bad part_count did not fail")

    assert checks_run == expected_case_count
    print("LANE05_ARCHIVE_PARTS_PACKET_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the repo-local pinned Zig archive parts packet matches policy and decodes cleanly."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--parts-dir",
        type=Path,
        help="Optional packet directory override. Defaults to third_party/<policy filename>.parts",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Pass when the packet directory is absent so the checker can land before the packet itself.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in packet checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    metadata = load_policy_metadata(root)
    parts_dir = args.parts_dir.resolve() if args.parts_dir is not None else default_parts_dir(
        root, str(metadata["filename"])
    )
    status, validated = validate_packet(root, parts_dir, allow_missing=args.allow_missing)
    print(f"LANE05_ARCHIVE_PARTS_PACKET={'pass' if status in {'verified', 'missing_allowed'} else 'fail'}")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_STATUS={status}")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_DIR={parts_dir}")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_FILENAME={validated['filename']}")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SHA256={validated['sha256']}")
    print(f"LANE05_ARCHIVE_PARTS_PACKET_EXPECTED_SIZE={validated['size']}")
    if status == "verified":
        print(f"LANE05_ARCHIVE_PARTS_PACKET_CHUNK_BYTES={validated['chunk_bytes']}")
        print(f"LANE05_ARCHIVE_PARTS_PACKET_PART_COUNT={validated['part_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())