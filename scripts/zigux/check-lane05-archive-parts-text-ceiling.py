#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_DIR = Path("third_party")
MAX_SHARD_TEXT_BYTES = 1_048_576
EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"invalid {label}")
    return value.strip()


def require_positive_int(value: object, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise SystemExit(f"invalid {label}")
    return value


def load_policy_metadata(root: Path) -> dict[str, object]:
    policy_path = root / TOOLCHAIN_POLICY
    policy = read_json(policy_path)
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in {policy_path}")
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in {policy_path}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or len(archive_target_scope) != 1:
        raise SystemExit(f"expected exactly one archive_target_scope entry in {policy_path}")
    target = require_string(archive_target_scope[0], "archive target")
    channel = require_string(policy.get("channel"), "channel")
    digest = require_string(archive_sha256.get(target), f"archive_sha256[{target}]")
    expected_size = EXPECTED_ARCHIVE_SIZES.get(target)
    if expected_size is None:
        raise SystemExit(f"missing expected archive size for {target}")
    return {
        "filename": f"zig-{target}-{channel}.tar.xz",
        "sha256": digest,
        "size": expected_size,
    }


def default_parts_dir(root: Path, filename: str) -> Path:
    return root / THIRD_PARTY_DIR / f"{filename}.parts"


def check_text_ceiling(root: Path, parts_dir: Path, *, allow_missing: bool) -> tuple[str, dict[str, object]]:
    metadata = load_policy_metadata(root)
    if not parts_dir.exists():
        if allow_missing:
            return "missing_allowed", {**metadata, "max_text_bytes": 0, "part_count": 0}
        raise SystemExit(f"required packet directory missing: {parts_dir}")
    if not parts_dir.is_dir():
        raise SystemExit(f"packet path is not a directory: {parts_dir}")
    manifest = read_json(parts_dir / "manifest.json")
    filename = require_string(manifest.get("filename"), "manifest filename")
    sha256 = require_string(manifest.get("sha256"), "manifest sha256")
    size = require_positive_int(manifest.get("size"), "manifest size")
    part_count = require_positive_int(manifest.get("part_count"), "manifest part_count")
    if filename != metadata["filename"]:
        raise SystemExit(f"packet filename mismatch: expected {metadata['filename']}, got {filename}")
    if sha256 != metadata["sha256"]:
        raise SystemExit(f"packet sha256 mismatch: expected {metadata['sha256']}, got {sha256}")
    if size != metadata["size"]:
        raise SystemExit(f"packet size mismatch: expected {metadata['size']}, got {size}")
    max_text_bytes = 0
    for index in range(part_count):
        shard_path = parts_dir / f"part-{index:03d}.b64"
        try:
            shard_text = shard_path.read_text(encoding="ascii")
        except FileNotFoundError as exc:
            raise SystemExit(f"packet missing shard file: {shard_path.name}") from exc
        text_bytes = len(shard_text.encode("ascii"))
        max_text_bytes = max(max_text_bytes, text_bytes)
        if text_bytes > MAX_SHARD_TEXT_BYTES:
            raise SystemExit(
                f"packet shard exceeds text ceiling: {shard_path.name} is {text_bytes} bytes, "
                f"limit is {MAX_SHARD_TEXT_BYTES}"
            )
        try:
            base64.b64decode(shard_text.strip(), validate=True)
        except binascii.Error as exc:
            raise SystemExit(f"packet shard is not valid base64: {shard_path.name}") from exc
    return "verified", {**metadata, "max_text_bytes": max_text_bytes, "part_count": part_count}


def write_fixture(parts_dir: Path, payload: bytes, *, filename: str, sha256: str, chunk_bytes: int) -> None:
    parts_dir.mkdir(parents=True, exist_ok=True)
    part_count = (len(payload) + chunk_bytes - 1) // chunk_bytes
    manifest = {
        "filename": filename,
        "encoding": "base64",
        "sha256": sha256,
        "size": len(payload),
        "chunk_bytes": chunk_bytes,
        "part_count": part_count,
        "parts_glob": "part-*.b64",
    }
    (parts_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for index in range(part_count):
        chunk = payload[index * chunk_bytes : (index + 1) * chunk_bytes]
        (parts_dir / f"part-{index:03d}.b64").write_text(
            base64.b64encode(chunk).decode("ascii") + "\n",
            encoding="ascii",
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        policy_dir = root / "scripts" / "zigux"
        policy_dir.mkdir(parents=True)
        payload = b"a" * 32
        digest = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
        policy = {
            "channel": "0.17.0-dev.87+9b177a7d2",
            "archive_sha256": {"x86_64-linux": digest},
            "upgrade_policy": {"archive_target_scope": ["x86_64-linux"]},
        }
        (policy_dir / "zig-toolchain-policy.json").write_text(json.dumps(policy) + "\n", encoding="utf-8")
        metadata = load_policy_metadata(root)
        metadata["size"] = len(payload)
        EXPECTED_ARCHIVE_SIZES["x86_64-linux"] = len(payload)

        parts_dir = default_parts_dir(root, metadata["filename"])
        write_fixture(parts_dir, payload, filename=metadata["filename"], sha256=digest, chunk_bytes=8)
        status, details = check_text_ceiling(root, parts_dir, allow_missing=False)
        assert status == "verified"
        assert details["part_count"] == 4
        case_count = 1

        missing_status, _ = check_text_ceiling(root, root / "missing.parts", allow_missing=True)
        assert missing_status == "missing_allowed"
        case_count += 1

        oversize = "A" * (MAX_SHARD_TEXT_BYTES + 1)
        (parts_dir / "part-000.b64").write_text(oversize, encoding="ascii")
        try:
            check_text_ceiling(root, parts_dir, allow_missing=False)
        except SystemExit as exc:
            assert "exceeds text ceiling" in str(exc)
            case_count += 1
        else:
            raise AssertionError("oversize shard did not fail")

    print("LANE05_ARCHIVE_PARTS_TEXT_CEILING_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that pinned Zig archive shard text files stay publish-safe."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--parts-dir", type=Path, help="Optional archive .parts directory override")
    parser.add_argument("--allow-missing", action="store_true", help="Pass when the packet has not landed yet")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    root = args.root.resolve()
    metadata = load_policy_metadata(root)
    parts_dir = args.parts_dir.resolve() if args.parts_dir else default_parts_dir(root, str(metadata["filename"]))
    status, details = check_text_ceiling(root, parts_dir, allow_missing=args.allow_missing)
    print("LANE05_ARCHIVE_PARTS_TEXT_CEILING=pass")
    print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_STATUS={status}")
    print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_DIR={parts_dir}")
    print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_LIMIT={MAX_SHARD_TEXT_BYTES}")
    if status == "verified":
        print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_PART_COUNT={details['part_count']}")
        print(f"LANE05_ARCHIVE_PARTS_TEXT_CEILING_MAX_TEXT_BYTES={details['max_text_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
