#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
THIRD_PARTY_DIR = Path("third_party")
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}
POLICY_KEYS = {"phase", "channel", "minimum_version", "archive_sha256", "upgrade_policy"}
UPGRADE_POLICY_KEYS = {"channel_minimum_lockstep", "archive_target_scope", "required_make_routes"}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def require_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY}")
    return value.strip()


def require_string_map(payload: dict[str, object], key: str) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY}")
    if isinstance(value, DuplicateTrackingDict) and value.duplicate_keys:
        raise ValueError(
            f"duplicate {key} targets in {TOOLCHAIN_POLICY}: " + ", ".join(value.duplicate_keys)
        )

    normalized: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"invalid {key} target in {TOOLCHAIN_POLICY}")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"invalid {key}[{map_key}] in {TOOLCHAIN_POLICY}")
        normalized_key = map_key.strip()
        if normalized_key in normalized:
            raise ValueError(f"duplicate {key} targets in {TOOLCHAIN_POLICY}: {normalized_key}")
        normalized[normalized_key] = map_value.strip()
    return normalized


def require_string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {TOOLCHAIN_POLICY}")
    normalized: list[str] = []
    seen: set[str] = set()
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {TOOLCHAIN_POLICY}")
        normalized_entry = entry.strip()
        if normalized_entry in seen:
            raise ValueError(f"duplicate {key} entry in {TOOLCHAIN_POLICY}: {normalized_entry}")
        normalized.append(normalized_entry)
        seen.add(normalized_entry)
    return normalized


def validate_policy_payload(payload: dict[str, object]) -> dict[str, object]:
    unexpected_policy_keys = sorted(set(payload) - POLICY_KEYS)
    if unexpected_policy_keys:
        raise ValueError(
            f"unexpected toolchain policy keys in {TOOLCHAIN_POLICY}: "
            + ", ".join(unexpected_policy_keys)
        )

    phase = require_string(payload, "phase")
    channel = require_string(payload, "channel")
    minimum_version = require_string(payload, "minimum_version")

    archives = require_string_map(payload, "archive_sha256")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {TOOLCHAIN_POLICY}")
    if isinstance(upgrade_policy, DuplicateTrackingDict) and upgrade_policy.duplicate_keys:
        raise ValueError(
            f"duplicate upgrade_policy keys in {TOOLCHAIN_POLICY}: "
            + ", ".join(upgrade_policy.duplicate_keys)
        )

    unexpected_upgrade_keys = sorted(set(upgrade_policy) - UPGRADE_POLICY_KEYS)
    if unexpected_upgrade_keys:
        raise ValueError(
            f"unexpected upgrade_policy keys in {TOOLCHAIN_POLICY}: "
            + ", ".join(unexpected_upgrade_keys)
        )

    lockstep = upgrade_policy.get("channel_minimum_lockstep")
    if not isinstance(lockstep, bool):
        raise ValueError(f"invalid channel_minimum_lockstep in {TOOLCHAIN_POLICY}")

    targets = require_string_list(upgrade_policy, "archive_target_scope")
    required_make_routes = require_string_list(upgrade_policy, "required_make_routes")

    missing_archive_targets = [target for target in targets if target not in archives]
    if missing_archive_targets:
        raise ValueError(
            "archive_target_scope references missing archive_sha256 entries in "
            f"{TOOLCHAIN_POLICY}: " + ", ".join(missing_archive_targets)
        )

    extra_archive_targets = [target for target in archives if target not in targets]
    if extra_archive_targets:
        raise ValueError(
            f"archive_sha256 contains targets outside archive_target_scope in {TOOLCHAIN_POLICY}: "
            + ", ".join(extra_archive_targets)
        )

    if lockstep and minimum_version != channel:
        raise ValueError(
            f"minimum_version must match channel when channel_minimum_lockstep is true in {TOOLCHAIN_POLICY}"
        )

    return {
        "phase": phase,
        "channel": channel,
        "minimum_version": minimum_version,
        "archive_sha256": archives,
        "upgrade_policy": {
            "channel_minimum_lockstep": lockstep,
            "archive_target_scope": targets,
            "required_make_routes": required_make_routes,
        },
    }


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
            f"duplicate toolchain policy keys in {TOOLCHAIN_POLICY}: "
            + ", ".join(payload.duplicate_keys)
        )
    return validate_policy_payload(payload)


def load_archive_metadata(root: Path) -> tuple[str, str, str, int, Path]:
    payload = load_policy(root)
    channel = str(payload["channel"])
    archives = payload["archive_sha256"]
    if not isinstance(archives, dict):
        raise ValueError(f"invalid archive_sha256 in {TOOLCHAIN_POLICY}")
    upgrade_policy = payload["upgrade_policy"]
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {TOOLCHAIN_POLICY}")
    targets = upgrade_policy["archive_target_scope"]
    if not isinstance(targets, list):
        raise ValueError(f"invalid archive_target_scope in {TOOLCHAIN_POLICY}")
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {TOOLCHAIN_POLICY}, got {len(targets)}")

    target = targets[0]
    if not isinstance(target, str):
        raise ValueError(f"invalid archive_target_scope entry in {TOOLCHAIN_POLICY}")
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} is missing from archive_sha256 in {TOOLCHAIN_POLICY}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    archive_sha = archives[target]
    if not isinstance(archive_sha, str):
        raise ValueError(f"invalid archive_sha256[{target}] in {TOOLCHAIN_POLICY}")

    filename = f"zig-{target}-{channel}.tar.xz"
    destination = root / THIRD_PARTY_DIR / filename
    return target, filename, archive_sha, EXPECTED_ARCHIVE_SIZES[target], destination


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duplicate_archive_name(expected_filename: str) -> str:
    stem = expected_filename[: -len(".tar.xz")]
    return f"{stem} (1).tar.xz"


def require_clean_third_party(root: Path, expected_filename: str) -> None:
    third_party_dir = root / THIRD_PARTY_DIR
    if not third_party_dir.exists():
        return
    duplicate_names = sorted(
        path.name
        for path in third_party_dir.glob("*.tar.xz")
        if ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path.name) is not None
    )
    if duplicate_names:
        raise ValueError(
            "third_party contains duplicate-suffix archive copies: " + ", ".join(duplicate_names)
        )
    if duplicate_archive_name(expected_filename) in duplicate_names:
        raise ValueError(
            f"third_party must not contain {duplicate_archive_name(expected_filename)}"
        )


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


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("wb") as dst:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            dst.write(chunk)


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
        return "already_present", destination_sha
    if destination_sha != actual_sha:
        raise ValueError(
            f"destination archive {destination} already exists with different bytes than {source}"
        )
    return "already_present", destination_sha


def stage_archive(root: Path, source: Path, *, check_only: bool) -> tuple[str, str, Path]:
    target, filename, expected_sha, expected_size, destination = load_archive_metadata(root)
    require_clean_third_party(root, filename)
    actual_sha = validate_source_archive(source, expected_size=expected_size, expected_sha=expected_sha)

    existing_destination = inspect_destination(
        source,
        destination,
        expected_size=expected_size,
        expected_sha=expected_sha,
        actual_sha=actual_sha,
    )
    if check_only:
        if existing_destination is not None:
            _, destination_sha = existing_destination
            return "checked", destination_sha, destination
        return "checked", actual_sha, destination
    if existing_destination is not None:
        status, destination_sha = existing_destination
        return status, destination_sha, destination

    copy_file(source, destination)
    staged_sha = validate_source_archive(
        destination,
        expected_size=expected_size,
        expected_sha=expected_sha,
    )
    return "staged", staged_sha, destination


def write_fixture(root: Path, *, source_bytes: bytes = b"x", source_size: int | None = None) -> tuple[Path, Path]:
    scripts_dir = root / "scripts" / "zigux"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    third_party_dir = root / "third_party"
    third_party_dir.mkdir(parents=True, exist_ok=True)
    source_dir = root / "sources"
    source_dir.mkdir(parents=True, exist_ok=True)

    policy_text = (ROOT / TOOLCHAIN_POLICY).read_text(encoding="utf-8")
    (scripts_dir / "zig-toolchain-policy.json").write_text(policy_text, encoding="utf-8")

    source_path = source_dir / "zig-source.tar.xz"
    size = source_size if source_size is not None else EXPECTED_ARCHIVE_SIZES["x86_64-linux"]
    repeat_count = (size + len(source_bytes) - 1) // len(source_bytes)
    source_path.write_bytes((source_bytes * repeat_count)[:size])
    return root, source_path


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_archive_pass_") as tmp_dir:
        root, source = write_fixture(Path(tmp_dir))
        expected_sha = compute_sha256(source)
        policy_path = root / TOOLCHAIN_POLICY
        policy_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": expected_sha},
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
        status, actual_sha, destination = stage_archive(root, source, check_only=False)
        assert status == "staged"
        assert actual_sha == expected_sha
        assert destination.read_bytes() == source.read_bytes()
        case_count += 1

        status, actual_sha, second_destination = stage_archive(root, source, check_only=False)
        assert status == "already_present"
        assert actual_sha == expected_sha
        assert second_destination == destination
        case_count += 1

        status, actual_sha, checked_destination = stage_archive(root, source, check_only=True)
        assert status == "checked"
        assert actual_sha == expected_sha
        assert checked_destination == destination
        case_count += 1

    def expect_failure(
        *,
        source_bytes: bytes = b"x",
        source_size: int | None = None,
        expected_substring: str,
        mutator=None,
        check_only: bool = False,
    ) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_archive_fail_") as tmp_dir:
            root, source = write_fixture(Path(tmp_dir), source_bytes=source_bytes, source_size=source_size)
            expected_sha = compute_sha256(source)
            policy_path = root / TOOLCHAIN_POLICY
            policy_path.write_text(
                json.dumps(
                    {
                        "phase": "Phase 2",
                        "channel": "0.17.0-dev.87+9b177a7d2",
                        "minimum_version": "0.17.0-dev.87+9b177a7d2",
                        "archive_sha256": {"x86_64-linux": expected_sha},
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
            if mutator is not None:
                mutator(root, source)
            try:
                stage_archive(root, source, check_only=check_only)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected stage_archive to fail")

    expect_failure(
        source_size=1,
        expected_substring="to be 58159088 bytes, got 1",
        check_only=True,
    )
    expect_failure(
        source_bytes=b"wrong-bytes",
        expected_substring="to have sha256",
        mutator=lambda root, source: (root / TOOLCHAIN_POLICY).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": "3" * 64},
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
        ),
        check_only=True,
    )
    expect_failure(
        expected_substring="duplicate-suffix archive copies",
        mutator=lambda root, source: (root / THIRD_PARTY_DIR / duplicate_archive_name(
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        )).write_bytes(b"x"),
        check_only=True,
    )
    expect_failure(
        expected_substring="to have sha256",
        mutator=lambda root, source: (root / THIRD_PARTY_DIR / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz").write_bytes(
            b"y" * EXPECTED_ARCHIVE_SIZES["x86_64-linux"]
        ),
        check_only=False,
    )
    expect_failure(
        expected_substring="destination archive is not a regular file",
        mutator=lambda root, source: (root / THIRD_PARTY_DIR / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz").mkdir(),
        check_only=True,
    )
    expect_failure(
        expected_substring="to have sha256",
        mutator=lambda root, source: (root / THIRD_PARTY_DIR / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz").write_bytes(
            b"y" * EXPECTED_ARCHIVE_SIZES["x86_64-linux"]
        ),
        check_only=True,
    )
    expect_failure(
        expected_substring="duplicate toolchain policy keys",
        mutator=lambda root, source: (root / TOOLCHAIN_POLICY).write_text(
            '{"phase":"Phase 2","phase":"Phase 3","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"'
            + expected_sha
            + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate"]}}\n',
            encoding="utf-8",
        ),
        check_only=True,
    )
    expect_failure(
        expected_substring="duplicate upgrade_policy keys",
        mutator=lambda root, source: (root / TOOLCHAIN_POLICY).write_text(
            '{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"'
            + expected_sha
            + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"channel_minimum_lockstep":false,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate"]}}\n',
            encoding="utf-8",
        ),
        check_only=True,
    )
    expect_failure(
        expected_substring="archive_target_scope references missing archive_sha256 entries",
        mutator=lambda root, source: (root / TOOLCHAIN_POLICY).write_text(
            '{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"other-target":"'
            + expected_sha
            + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate"]}}\n',
            encoding="utf-8",
        ),
        check_only=True,
    )
    expect_failure(
        expected_substring="duplicate required_make_routes entry",
        mutator=lambda root, source: (root / TOOLCHAIN_POLICY).write_text(
            '{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"'
            + expected_sha
            + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-toolchain"]}}\n',
            encoding="utf-8",
        ),
        check_only=True,
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

    if args.source is None:
        raise SystemExit("--source is required unless --self-test is used")

    root = args.root.resolve()
    source = args.source.resolve()
    try:
        target, filename, expected_sha, expected_size, destination = load_archive_metadata(root)
        status, actual_sha, staged_destination = stage_archive(
            root,
            source,
            check_only=args.check_only,
        )
    except ValueError as exc:
        print("STAGE_PINNED_ZIG_ARCHIVE=fail")
        print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")
        print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")
        print(f"STAGE_PINNED_ZIG_ARCHIVE_NOTE={exc}")
        return 1

    print("STAGE_PINNED_ZIG_ARCHIVE=pass")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_TARGET={target}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={filename}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={expected_size}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={expected_sha}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={staged_destination}")
    print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
