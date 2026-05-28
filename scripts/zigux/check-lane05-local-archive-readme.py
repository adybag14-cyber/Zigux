#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
README_PATH = Path("third_party/README.md")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
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
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    return value.strip()


def require_string_map(payload: dict[str, object], key: str) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    normalized: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"invalid {key} target in {POLICY_PATH}")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"invalid {key}[{map_key}] in {POLICY_PATH}")
        normalized[map_key.strip()] = map_value.strip()
    return normalized


def require_string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {POLICY_PATH}")
        normalized.append(entry.strip())
    return normalized


def expected_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def duplicate_archive_name(expected_filename: str) -> str:
    stem = expected_filename[: -len(".tar.xz")]
    return f"{stem} (1).tar.xz"


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_readme(root: Path) -> tuple[str, int, str]:
    payload = load_policy(root)
    channel = require_string(payload, "channel")
    archives = require_string_map(payload, "archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {POLICY_PATH}")
    targets = require_string_list(upgrade_policy, "archive_target_scope")
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {POLICY_PATH}, got {len(targets)}")

    target = targets[0]
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} is missing from archive_sha256 in {POLICY_PATH}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    expected_filename = expected_archive_filename(target, channel)
    expected_path = f"third_party/{expected_filename}"
    expected_sha = archives[target]
    expected_size = EXPECTED_ARCHIVE_SIZES[target]
    validation_command = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{expected_path} --archive-target {target}"
    )
    expected_parts_path = f"{expected_path}.parts"

    readme_path = root / README_PATH
    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing archive README: {readme_path}") from exc

    required_markers = [
        "# Zigux third-party archives",
        "Lane 05 bootstrap CI",
        f"`{target}`",
        f"`{channel}`",
        f"`{expected_path}`",
        f"`{expected_parts_path}`",
        f"`{expected_sha}`",
        f"`{expected_size}` bytes",
        f"`{validation_command}`",
        "`community-mirrors.txt`",
        "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
        "`scripts/zigux/check-lane05-local-archive-readme.py`",
        "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
        "`scripts/zigux/stage-pinned-zig-archive.py`",
        "`scripts/zigux/check-lane05-stage-helper-contract.py`",
        "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
        f"`{duplicate_archive_name(expected_filename)}`",
        f"`{POLICY_PATH}`",
    ]
    missing_markers = [marker for marker in required_markers if marker not in readme_text]
    if missing_markers:
        raise ValueError(
            "archive README is missing required markers: " + ", ".join(missing_markers)
        )

    duplicate_copies = sorted(
        path.name
        for path in (root / "third_party").glob("*.tar.xz")
        if ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path.name) is not None
    )
    if duplicate_copies:
        raise ValueError(
            "third_party contains duplicate-suffix archive copies: " + ", ".join(duplicate_copies)
        )

    archive_path = root / expected_path
    payload_status = "missing_allowed"
    if archive_path.exists():
        if not archive_path.is_file():
            raise ValueError(f"expected archive payload is not a regular file: {archive_path}")
        actual_size = archive_path.stat().st_size
        if actual_size != expected_size:
            raise ValueError(
                f"expected {archive_path} to be {expected_size} bytes, got {actual_size}"
            )
        actual_sha = compute_sha256(archive_path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"expected {archive_path} to have sha256 {expected_sha}, got {actual_sha}"
            )
        payload_status = "present"

    return target, len(required_markers), payload_status


def write_fixture(
    root: Path,
    *,
    include_archive: bool = False,
    archive_size: int | None = None,
    archive_bytes: bytes = b"x",
    duplicate_copy: bool = False,
) -> None:
    scripts_dir = root / "scripts" / "zigux"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    third_party_dir = root / "third_party"
    third_party_dir.mkdir(parents=True, exist_ok=True)

    policy_text = (ROOT / POLICY_PATH).read_text(encoding="utf-8")
    (scripts_dir / "zig-toolchain-policy.json").write_text(policy_text, encoding="utf-8")
    readme_text = (ROOT / README_PATH).read_text(encoding="utf-8")
    (third_party_dir / "README.md").write_text(readme_text, encoding="utf-8")

    if include_archive:
        payload_name = "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        archive_path = third_party_dir / payload_name
        size = archive_size if archive_size is not None else EXPECTED_ARCHIVE_SIZES["x86_64-linux"]
        repeat_count = (size + len(archive_bytes) - 1) // len(archive_bytes)
        archive_path.write_bytes((archive_bytes * repeat_count)[:size])
        if duplicate_copy:
            (third_party_dir / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz").write_bytes(b"x")


def run_self_test() -> int:
    case_count = 0

    def expect_pass(*, include_archive: bool = False) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_archive_readme_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root, include_archive=include_archive)
            assert validate_readme(root) == ("x86_64-linux", 18, "present" if include_archive else "missing_allowed")
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_archive_readme_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                validate_readme(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_readme to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / README_PATH).write_text("missing markers\n", encoding="utf-8"),
        "missing required markers",
    )
    expect_failure(
        lambda root: write_fixture(root, include_archive=True, archive_size=1),
        "to be 58159088 bytes, got 1",
    )
    expect_failure(
        lambda root: write_fixture(root, include_archive=True, duplicate_copy=True),
        "duplicate-suffix archive copies",
    )
    expect_failure(
        lambda root: write_fixture(
            root,
            include_archive=True,
            archive_bytes=b"wrong-bytes",
        ),
        "to have sha256 a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858",
    )

    print("LANE05_LOCAL_ARCHIVE_README_SELF_TEST=pass")
    print(f"LANE05_LOCAL_ARCHIVE_README_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 repo-local archive README contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        target, marker_count, payload_status = validate_readme(args.root.resolve())
    except ValueError as exc:
        print("LANE05_LOCAL_ARCHIVE_README=fail")
        print(f"LANE05_LOCAL_ARCHIVE_README_ROOT={args.root.resolve()}")
        print(f"LANE05_LOCAL_ARCHIVE_README_NOTE={exc}")
        return 1

    print("LANE05_LOCAL_ARCHIVE_README=pass")
    print(f"LANE05_LOCAL_ARCHIVE_README_ROOT={args.root.resolve()}")
    print(f"LANE05_LOCAL_ARCHIVE_TARGET={target}")
    print(f"LANE05_LOCAL_ARCHIVE_README_MARKER_COUNT={marker_count}")
    print(f"LANE05_LOCAL_ARCHIVE_PAYLOAD_STATUS={payload_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
