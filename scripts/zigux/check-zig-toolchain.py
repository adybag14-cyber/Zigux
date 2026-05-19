#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-dev\.(?P<dev>\d+)(?:\+[0-9A-Za-z.-]+)?)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")
ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FALLBACK_MIN_VERSION = "0.16.0"
POLICY_KEYS = {"phase", "channel", "minimum_version", "archive_sha256", "upgrade_policy"}
UPGRADE_POLICY_KEYS = {"channel_minimum_lockstep", "archive_target_scope", "required_make_routes"}


@dataclass(frozen=True, order=True)
class ZigVersion:
    major: int
    minor: int
    patch: int
    release_rank: int
    dev_build: int


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def parse_zig_version(raw: str) -> ZigVersion:
    match = VERSION_RE.fullmatch(raw.strip())
    if match is None:
        raise ValueError(f"unsupported Zig version string: {raw!r}")
    dev_build = match.group("dev")
    return ZigVersion(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        release_rank=1 if dev_build is None else 0,
        dev_build=int(dev_build) if dev_build is not None else 0,
    )


def require_non_empty_string(value: object, field_name: str, policy_path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {field_name} in {policy_path}")
    return value.strip()


def require_string_list(value: object, field_name: str, policy_path: Path) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {field_name} in {policy_path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for entry in value:
        normalized_entry = require_non_empty_string(entry, field_name, policy_path)
        if normalized_entry in seen:
            raise ValueError(
                f"duplicate {field_name} entry in {policy_path}: {normalized_entry}"
            )
        normalized.append(normalized_entry)
        seen.add(normalized_entry)
    return normalized


def validate_policy_payload(payload: dict[str, object], policy_path: Path) -> dict[str, object]:
    unexpected_policy_keys = sorted(set(payload) - POLICY_KEYS)
    if unexpected_policy_keys:
        raise ValueError(
            f"unexpected toolchain policy keys in {policy_path}: "
            + ", ".join(unexpected_policy_keys)
        )

    phase = require_non_empty_string(payload.get("phase"), "phase", policy_path)
    channel = require_non_empty_string(payload.get("channel"), "channel", policy_path)
    minimum_version = require_non_empty_string(payload.get("minimum_version"), "minimum_version", policy_path)
    parse_zig_version(channel)
    parse_zig_version(minimum_version)

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
        normalized_digest = require_non_empty_string(digest, f"archive_sha256[{normalized_target}]", policy_path)
        if SHA256_RE.fullmatch(normalized_digest) is None:
            raise ValueError(f"invalid archive_sha256[{normalized_target}] in {policy_path}")
        normalized_archives[normalized_target] = normalized_digest

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    if isinstance(upgrade_policy, DuplicateTrackingDict) and upgrade_policy.duplicate_keys:
        raise ValueError(
            f"duplicate upgrade_policy keys in {policy_path}: "
            + ", ".join(upgrade_policy.duplicate_keys)
        )
    unexpected_upgrade_keys = sorted(set(upgrade_policy) - UPGRADE_POLICY_KEYS)
    if unexpected_upgrade_keys:
        raise ValueError(
            f"unexpected upgrade_policy keys in {policy_path}: "
            + ", ".join(unexpected_upgrade_keys)
        )
    lockstep = upgrade_policy.get("channel_minimum_lockstep")
    if not isinstance(lockstep, bool):
        raise ValueError(f"invalid channel_minimum_lockstep in {policy_path}")
    archive_target_scope = require_string_list(
        upgrade_policy.get("archive_target_scope"),
        "archive_target_scope",
        policy_path,
    )
    required_make_routes = require_string_list(
        upgrade_policy.get("required_make_routes"),
        "required_make_routes",
        policy_path,
    )

    missing_archive_targets = [target for target in archive_target_scope if target not in normalized_archives]
    if missing_archive_targets:
        raise ValueError(
            f"archive_target_scope references missing archive_sha256 entries in {policy_path}: "
            + ", ".join(missing_archive_targets)
        )

    extra_archive_targets = [target for target in normalized_archives if target not in archive_target_scope]
    if extra_archive_targets:
        raise ValueError(
            f"archive_sha256 contains targets outside archive_target_scope in {policy_path}: "
            + ", ".join(extra_archive_targets)
        )

    if lockstep and minimum_version != channel:
        raise ValueError(f"minimum_version must match channel when channel_minimum_lockstep is true in {policy_path}")

    return {
        "phase": phase,
        "channel": channel,
        "minimum_version": minimum_version,
        "archive_sha256": normalized_archives,
        "upgrade_policy": {
            "channel_minimum_lockstep": lockstep,
            "archive_target_scope": archive_target_scope,
            "required_make_routes": required_make_routes,
        },
    }


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(
            policy_path.read_text(encoding="utf-8"),
            object_pairs_hook=DuplicateTrackingDict,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:
        raise ValueError(
            f"duplicate toolchain policy keys in {policy_path}: "
            + ", ".join(payload.duplicate_keys)
        )
    return validate_policy_payload(payload, policy_path)


def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:
    payload = load_policy(policy_path)
    if payload is None:
        return fallback
    return str(payload["minimum_version"])


def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    payload = load_policy(policy_path)
    if payload is None:
        return None
    return str(payload["channel"])


def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:
    search_roots: list[Path] = []

    def add_search_root(path: Path) -> None:
        if path not in search_roots:
            search_roots.append(path)

    add_search_root(root / ".zig-toolchain")
    add_search_root(root / "toolchains")
    add_search_root(root / ".toolchains")

    for parent in root.parents:
        add_search_root(parent / ".toolchains")
        add_search_root(parent / "toolchains")

    return search_roots


def normalize_explicit_zig_path(explicit_zig: str) -> str:
    normalized = Path(explicit_zig).expanduser()
    if not normalized.exists():
        raise ValueError(f"explicit zig path does not exist: {normalized}")
    if normalized.is_dir():
        raise ValueError(f"explicit zig path is a directory, expected an executable file: {normalized}")
    return str(normalized)


def iter_repo_local_zig_candidates(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
) -> list[Path]:
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    def add_candidate_roots(base: Path) -> None:
        add_candidate(base / "zig")
        add_candidate(base / "bin" / "zig")

    zig_search_roots = iter_zig_search_roots(root)
    if pinned_channel is not None:
        pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"
        for base in zig_search_roots:
            add_candidate_roots(base / pinned_dirname)
            if not base.exists():
                continue
            for child in sorted(base.iterdir()):
                if child.is_dir():
                    add_candidate_roots(child / pinned_dirname)

    for base in zig_search_roots:
        if not base.exists():
            continue
        add_candidate_roots(base)
        for child in sorted(base.iterdir()):
            if child.is_dir():
                add_candidate_roots(child)
    return candidates


def resolve_zig_executable(
    explicit_zig: str | None = None,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
    which=shutil.which,
) -> str | None:
    if explicit_zig is not None:
        return normalize_explicit_zig_path(explicit_zig)

    pinned_channel = load_pinned_channel(policy_path)
    for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):
        if candidate.is_file():
            return str(candidate)
    return which("zig")


def policy_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:
    search_roots: list[Path] = []

    def add_search_root(path: Path) -> None:
        if path not in search_roots:
            search_roots.append(path)

    add_search_root(root / ".zig-toolchain")
    add_search_root(root / "toolchains")
    add_search_root(root / ".toolchains")
    add_search_root(root / "third_party")
    add_search_root(root / "agent_files")

    for parent in root.parents:
        add_search_root(parent / ".toolchains")
        add_search_root(parent / "toolchains")
        add_search_root(parent / "agent_files")

    return search_roots


def format_search_roots(search_roots: list[Path]) -> str:
    return ",".join(str(path) for path in search_roots)


def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:
    if not expected_filename.endswith(".tar.xz"):
        return False
    match = ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)
    if match is None:
        return False
    return match.group("stem") == expected_filename[: -len(".tar.xz")]


def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:
    return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)


def describe_missing_archive(
    archive_path: Path | None,
    *,
    explicit_archive: str | None,
    search_roots: list[Path],
) -> tuple[str, str | None]:
    if explicit_archive is not None:
        resolved = archive_path or Path(explicit_archive)
        return f"explicit archive path does not exist: {resolved}", None
    return "pinned Zig archive not found in archive search roots", format_search_roots(search_roots)


def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:
    if not archive_path.exists():
        return None
    if archive_path.is_dir():
        return f"explicit archive path is a directory, expected a regular file: {archive_path}"
    if not archive_path.is_file():
        return f"explicit archive path is not a regular file: {archive_path}"
    return None


def describe_missing_zig(
    *,
    pinned_channel: str | None,
    search_roots: list[Path],
) -> tuple[str, str]:
    message = "zig not found on PATH or in repo-local toolchain search roots"
    if pinned_channel is not None:
        message += f" for pinned channel {pinned_channel}"
    return message, format_search_roots(search_roots)


def iter_repo_local_archive_candidates(
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> list[tuple[str, Path]]:
    payload = load_policy(policy_path)
    if payload is None:
        return []

    channel = str(payload["channel"])
    archive_targets = payload["upgrade_policy"]["archive_target_scope"]
    candidates: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    for target in archive_targets:
        expected_filename = policy_archive_filename(str(target), channel)
        for base in iter_archive_search_roots(root):
            path = base / expected_filename
            if path not in seen:
                candidates.append((str(target), path))
                seen.add(path)
            if not base.exists():
                continue
            for child in sorted(base.iterdir()):
                if child in seen or not child.is_file():
                    continue
                if archive_name_has_duplicate_suffix(child.name, expected_filename):
                    candidates.append((str(target), child))
                    seen.add(child)
    return candidates


def resolve_policy_archive(
    explicit_archive: str | None = None,
    explicit_target: str | None = None,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> tuple[str | None, Path | None]:
    payload = load_policy(policy_path)
    if payload is None:
        return explicit_target, Path(explicit_archive) if explicit_archive is not None else None

    archive_targets = [str(target) for target in payload["upgrade_policy"]["archive_target_scope"]]
    target = explicit_target
    if target is not None and target not in archive_targets:
        raise ValueError(
            f"archive target {target!r} is outside archive_target_scope in {policy_path}: "
            + ", ".join(archive_targets)
        )

    if explicit_archive is not None:
        if target is None:
            if len(archive_targets) != 1:
                raise ValueError("archive target must be explicit when policy covers multiple archive targets")
            target = archive_targets[0]
        return target, Path(explicit_archive)

    candidates = iter_repo_local_archive_candidates(root=root, policy_path=policy_path)
    if target is not None:
        candidates = [(candidate_target, candidate_path) for candidate_target, candidate_path in candidates if candidate_target == target]
    for candidate_target, candidate_path in candidates:
        if candidate_path.is_file():
            return candidate_target, candidate_path

    if target is None and len(archive_targets) == 1:
        target = archive_targets[0]
    return target, None


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def expected_archive_metadata(
    archive_target: str,
    *,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> tuple[str, str]:
    payload = load_policy(policy_path)
    if payload is None:
        raise ValueError(f"toolchain policy not found at {policy_path}")
    if archive_target not in payload["archive_sha256"]:
        raise ValueError(f"archive target {archive_target!r} is not pinned in {policy_path}")
    return str(payload["archive_sha256"][archive_target]), policy_archive_filename(
        archive_target,
        str(payload["channel"]),
    )


def validate_policy_archive(path: Path, archive_target: str, *, policy_path: Path = TOOLCHAIN_POLICY) -> tuple[str, str | None, str, str]:
    expected_sha, expected_filename = expected_archive_metadata(archive_target, policy_path=policy_path)
    if not archive_name_matches_policy(path.name, expected_filename):
        actual_sha = compute_sha256(path)
        return (
            "mismatch",
            f"expected archive filename {expected_filename} for {archive_target}, got {path.name}",
            expected_sha,
            actual_sha,
        )
    actual_sha = compute_sha256(path)
    if actual_sha != expected_sha:
        return (
            "mismatch",
            f"expected sha256 {expected_sha} for {archive_target}, got {actual_sha}",
            expected_sha,
            actual_sha,
        )
    return "present", None, expected_sha, actual_sha

def read_zig_version(zig: str, *, runner=subprocess.run) -> str:
    try:
        completed = runner([zig, "version"], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise ValueError(f"zig executable not found: {zig}") from exc
    except OSError as exc:
        raise ValueError(f"failed to execute zig at {zig}: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise ValueError(f"zig version command failed: {detail}")

    version = completed.stdout.strip()
    if not version:
        raise ValueError("zig version command returned empty output")
    return version


def evaluate_toolchain_version(
    version: str,
    min_version_raw: str,
    expected_channel_raw: str | None = None,
) -> tuple[str, str | None]:
    parsed_version = parse_zig_version(version)
    min_version = parse_zig_version(min_version_raw)
    if parsed_version < min_version:
        return "too_old", None
    if expected_channel_raw is not None:
        expected_channel_raw = expected_channel_raw.strip()
        parse_zig_version(expected_channel_raw)
        if version.strip() != expected_channel_raw:
            return "not_pinned", f"expected pinned Zig channel {expected_channel_raw}"
    return "present", None


def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:
    payload = load_policy(policy_path)
    if payload is None:
        print("ZIG_TOOLCHAIN_POLICY_STATUS=missing")
        print(f"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}")
        return

    archive_sha256 = payload["archive_sha256"]
    upgrade_policy = payload["upgrade_policy"]
    print("ZIG_TOOLCHAIN_POLICY_STATUS=present")
    print(f"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}")
    print(f"ZIG_TOOLCHAIN_PHASE={payload['phase']}")
    print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload['channel']}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload['minimum_version']}")
    print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}")
    print("ZIG_TOOLCHAIN_ARCHIVE_TARGETS=" + ",".join(str(target) for target in upgrade_policy["archive_target_scope"]))
    print("ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(str(route) for route in upgrade_policy["required_make_routes"]))
    print("ZIG_TOOLCHAIN_PIN_POLICY=" + ("exact" if upgrade_policy["channel_minimum_lockstep"] else "minimum_only"))


def run_self_test() -> int:
    case_count = 0

    def expect_equal(actual, expected) -> None:
        nonlocal case_count
        assert actual == expected
        case_count += 1

    def expect_true(condition: bool) -> None:
        nonlocal case_count
        assert condition
        case_count += 1

    def expect_raises(fn, expected_substring: str | None = None) -> None:
        nonlocal case_count
        try:
            fn()
        except ValueError as exc:
            if expected_substring is not None:
                assert expected_substring in str(exc)
            case_count += 1
            return
        raise AssertionError("expected ValueError to fail")

    expect_equal(parse_zig_version("0.16.0"), ZigVersion(0, 16, 0, 1, 0))
    expect_equal(parse_zig_version("0.17.0-dev.87+9b177a7d2"), ZigVersion(0, 17, 0, 0, 87))
    expect_true(parse_zig_version("0.17.0-dev.90") > parse_zig_version("0.17.0-dev.87+9b177a7d2"))
    expect_true(parse_zig_version("0.17.0") > parse_zig_version("0.17.0-dev.999+abcdef"))
    expect_true(parse_zig_version("0.17.1-dev.1") > parse_zig_version("0.17.0"))
    expect_true(parse_zig_version("0.16.0") > parse_zig_version("0.15.2"))
    expect_equal(policy_archive_filename("x86_64-linux", "0.17.0-dev.87+9b177a7d2"), "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")
    expect_true(
        archive_name_has_duplicate_suffix(
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz",
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        )
    )
    expect_true(
        archive_name_matches_policy(
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (2).tar.xz",
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        )
    )
    expect_true(
        not archive_name_has_duplicate_suffix(
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2-copy.tar.xz",
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        )
    )
    expect_raises(lambda: normalize_explicit_zig_path("/tmp/zigux-toolchain-self-test-missing-zig"), "explicit zig path does not exist")

    expect_equal(
        evaluate_toolchain_version("0.17.0-dev.87+9b177a7d2", "0.17.0-dev.87+9b177a7d2"),
        ("present", None),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("present", None),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("not_pinned", "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.17.0-dev.90+abcdef",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("not_pinned", "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"),
    )
    expect_equal(
        evaluate_toolchain_version(
            "0.16.0",
            "0.17.0-dev.87+9b177a7d2",
            "0.17.0-dev.87+9b177a7d2",
        ),
        ("too_old", None),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_policy_") as tmp_dir:
        root = Path(tmp_dir) / "workspace" / "repo"
        root.mkdir(parents=True)
        policy_path = root / "zig-toolchain-policy.json"
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.15.0")
        expect_equal(load_pinned_channel(policy_path), None)
        expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (None, None))
        policy_path.write_text(
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
                }
            )
            + "\n",
            encoding="utf-8",
        )
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.17.0-dev.87+9b177a7d2")
        expect_equal(load_pinned_channel(policy_path), "0.17.0-dev.87+9b177a7d2")
        toolchain_dir = root / ".zig-toolchain" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2"
        toolchain_dir.mkdir(parents=True)
        pinned_zig = toolchain_dir / "zig"
        pinned_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: "/usr/bin/zig"), str(pinned_zig))
        alt_toolchain = root / ".zig-toolchain" / "fallback" / "bin"
        alt_toolchain.mkdir(parents=True)
        alt_zig = alt_toolchain / "zig"
        alt_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        pinned_zig.unlink()
        expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: "/usr/bin/zig"), str(alt_zig))
        explicit_zig = root / "custom-zig"
        explicit_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        expect_equal(
            resolve_zig_executable(str(explicit_zig), root=root, policy_path=policy_path, which=lambda _: None),
            str(explicit_zig),
        )
        explicit_dir = root / "explicit-zig-dir"
        explicit_dir.mkdir()
        expect_raises(lambda: resolve_zig_executable(str(explicit_dir), root=root, policy_path=policy_path, which=lambda _: None), "expected an executable file")
        pinned_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        expect_equal(
            iter_repo_local_zig_candidates(root=root, pinned_channel="0.17.0-dev.87+9b177a7d2")[:2],
            [pinned_zig, toolchain_dir / "bin" / "zig"],
        )
        expect_equal(
            iter_zig_search_roots(root)[:7],
            [
                root / ".zig-toolchain",
                root / "toolchains",
                root / ".toolchains",
                root.parent / ".toolchains",
                root.parent / "toolchains",
                root.parent.parent / ".toolchains",
                root.parent.parent / "toolchains",
            ],
        )
        parent_toolchain = root.parent / ".toolchains" / "lane03-followup"
        parent_pinned_root = parent_toolchain / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2"
        parent_pinned_root.mkdir(parents=True, exist_ok=True)
        parent_pinned_zig = parent_pinned_root / "zig"
        parent_pinned_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        pinned_zig.unlink()
        alt_zig.unlink()
        expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: "/usr/bin/zig"), str(parent_pinned_zig))
        expect_equal(
            describe_missing_zig(
                pinned_channel="0.17.0-dev.87+9b177a7d2",
                search_roots=iter_zig_search_roots(root),
            ),
            (
                "zig not found on PATH or in repo-local toolchain search roots for pinned channel 0.17.0-dev.87+9b177a7d2",
                format_search_roots(iter_zig_search_roots(root)),
            ),
        )
        expect_equal(
            describe_missing_zig(
                pinned_channel=None,
                search_roots=iter_zig_search_roots(root),
            ),
            (
                "zig not found on PATH or in repo-local toolchain search roots",
                format_search_roots(iter_zig_search_roots(root)),
            ),
        )
        expect_equal(
            iter_archive_search_roots(root)[:8],
            [
                root / ".zig-toolchain",
                root / "toolchains",
                root / ".toolchains",
                root / "third_party",
                root / "agent_files",
                root.parent / ".toolchains",
                root.parent / "toolchains",
                root.parent / "agent_files",
            ],
        )
        workspace_archive_path = root.parent / "agent_files" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        workspace_archive_path.parent.mkdir(parents=True, exist_ok=True)
        workspace_archive_path.write_bytes(b"zigux-archive")
        expected_archive_sha = hashlib.sha256(b"zigux-archive").hexdigest()
        policy_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": expected_archive_sha},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": ["x86_64-linux"],
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), ("x86_64-linux", workspace_archive_path))
        expect_equal(resolve_policy_archive(str(workspace_archive_path), root=root, policy_path=policy_path), ("x86_64-linux", workspace_archive_path))
        expect_equal(
            expected_archive_metadata("x86_64-linux", policy_path=policy_path),
            (
                expected_archive_sha,
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
            ),
        )
        expect_equal(
            validate_policy_archive(workspace_archive_path, "x86_64-linux", policy_path=policy_path),
            ("present", None, expected_archive_sha, expected_archive_sha),
        )
        duplicate_archive_path = workspace_archive_path.with_name(
            "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz"
        )
        duplicate_archive_path.write_bytes(b"zigux-archive")
        workspace_archive_path.unlink()
        expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), ("x86_64-linux", duplicate_archive_path))
        expect_equal(
            validate_policy_archive(duplicate_archive_path, "x86_64-linux", policy_path=policy_path),
            ("present", None, expected_archive_sha, expected_archive_sha),
        )
        renamed_archive_path = duplicate_archive_path.with_name("renamed-zig.tar.xz")
        renamed_archive_path.write_bytes(b"zigux-archive")
        expect_equal(
            validate_policy_archive(renamed_archive_path, "x86_64-linux", policy_path=policy_path),
            (
                "mismatch",
                "expected archive filename zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz for x86_64-linux, got renamed-zig.tar.xz",
                expected_archive_sha,
                expected_archive_sha,
            ),
        )
        missing_explicit_path = root / "missing.tar.xz"
        expect_equal(
            resolve_policy_archive(
                str(missing_explicit_path),
                "x86_64-linux",
                root=root,
                policy_path=policy_path,
            ),
            ("x86_64-linux", missing_explicit_path),
        )
        expect_equal(
            describe_missing_archive(
                missing_explicit_path,
                explicit_archive=str(missing_explicit_path),
                search_roots=iter_archive_search_roots(root),
            ),
            (
                f"explicit archive path does not exist: {missing_explicit_path}",
                None,
            ),
        )
        explicit_archive_dir = root / "archive-dir"
        explicit_archive_dir.mkdir()
        expect_equal(
            describe_invalid_explicit_archive_path(explicit_archive_dir),
            f"explicit archive path is a directory, expected a regular file: {explicit_archive_dir}",
        )
        expect_equal(
            describe_missing_archive(
                None,
                explicit_archive=None,
                search_roots=iter_archive_search_roots(root),
            ),
            (
                "pinned Zig archive not found in archive search roots",
                format_search_roots(iter_archive_search_roots(root)),
            ),
        )
        duplicate_archive_path.write_bytes(b"zigux-archive-drift")
        drift_sha = hashlib.sha256(b"zigux-archive-drift").hexdigest()
        expect_equal(
            validate_policy_archive(duplicate_archive_path, "x86_64-linux", policy_path=policy_path),
            (
                "mismatch",
                f"expected sha256 {expected_archive_sha} for x86_64-linux, got {drift_sha}",
                expected_archive_sha,
                drift_sha,
            ),
        )
        expect_raises(
            lambda: resolve_policy_archive(str(duplicate_archive_path), "aarch64-linux", root=root, policy_path=policy_path),
            "outside archive_target_scope",
        )
        expect_raises(lambda: validate_policy_archive(duplicate_archive_path, "aarch64-linux", policy_path=policy_path), "is not pinned")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":7,"channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid minimum_version")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":7,"archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_pinned_channel(policy_path), "invalid channel")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"oops"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid archive_sha256[x86_64-linux]")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["aarch64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "archive_target_scope references missing archive_sha256 entries")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":[]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid required_make_routes")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.90+abcdef","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "minimum_version must match channel")
        policy_path.write_text('{"phase":"Phase 2","phase":"Phase 3","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "duplicate toolchain policy keys")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"unexpected":"value","upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "unexpected toolchain policy keys")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"channel_minimum_lockstep":false,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "duplicate upgrade_policy keys")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"],"unexpected_route":"phase2-extra"}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "unexpected upgrade_policy keys")
        policy_path.write_text('{"phase":"Phase 2","minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + ("3" * 64) + '"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-toolchain"]}}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "duplicate required_make_routes entry")
        policy_path.write_text('{not-json}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid toolchain policy JSON")
        expect_raises(lambda: parse_zig_version("master"))

    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_resolution_") as tmp_dir:
        root = Path(tmp_dir)
        policy_path = root / "zig-toolchain-policy.json"
        policy_path.write_text(
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
                }
            )
            + "\n",
            encoding="utf-8",
        )
        expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: "/usr/bin/zig"), "/usr/bin/zig")

    expect_equal(
        read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                0,
                stdout="0.17.0-dev.87+9b177a7d2\n",
                stderr="",
            ),
        ),
        "0.17.0-dev.87+9b177a7d2",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/missing-zig",
            runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError("missing")),
        ),
        "zig executable not found",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                1,
                stdout="",
                stderr="permission denied\n",
            ),
        ),
        "zig version command failed: permission denied",
    )
    expect_raises(
        lambda: read_zig_version(
            "/tmp/zig",
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(
                args[0],
                0,
                stdout="\n",
                stderr="",
            ),
        ),
        "zig version command returned empty output",
    )

    print("ZIG_TOOLCHAIN_SELF_TEST=pass")
    print(f"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")
    parser.add_argument(
        "--min-version",
        help="Minimum supported Zig version string. Defaults to scripts/zigux/zig-toolchain-policy.json when available.",
    )
    parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")
    parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")
    parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")
    parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")
    parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")
    parser.add_argument("--zig", help="Explicit zig executable path.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.policy_only:
        try:
            emit_policy_summary()
        except ValueError as exc:
            print("ZIG_TOOLCHAIN_POLICY_STATUS=invalid")
            print(f"ZIG_TOOLCHAIN_POLICY_PATH={TOOLCHAIN_POLICY}")
            print(f"ZIG_TOOLCHAIN_NOTE={exc}")
            return 1
        return 0

    if args.archive_only:
        archive_target: str | None = None
        archive_path: Path | None = None
        expected_sha: str | None = None
        expected_filename: str | None = None
        try:
            archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)
            if archive_target is not None:
                expected_sha, expected_filename = expected_archive_metadata(archive_target)
        except ValueError as exc:
            print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")
            print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}")
            if args.archive_target is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}")
            print(f"ZIG_TOOLCHAIN_NOTE={exc}")
            return 1

        if args.archive is not None and archive_path is not None:
            invalid_archive_note = describe_invalid_explicit_archive_path(archive_path)
            if invalid_archive_note is not None:
                print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")
                print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}")
                print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
                if expected_filename is not None:
                    print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
                if expected_sha is not None:
                    print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}")
                print(f"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}")
                return 1

        if archive_path is None or not archive_path.is_file():
            search_roots = iter_archive_search_roots()
            message, search_roots_summary = describe_missing_archive(
                archive_path,
                explicit_archive=args.archive,
                search_roots=search_roots,
            )
            print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")
            print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}")
            print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
            if expected_filename is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
            if expected_sha is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}")
            if search_roots_summary is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")
            print(f"ZIG_TOOLCHAIN_NOTE={message}")
            return 0 if args.allow_missing else 1

        try:
            archive_status, note, validated_expected_sha, actual_sha = validate_policy_archive(
                archive_path,
                archive_target or "unresolved",
            )
        except ValueError as exc:
            print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")
            print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}")
            print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
            if expected_filename is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
            if expected_sha is not None:
                print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}")
            print(f"ZIG_TOOLCHAIN_NOTE={exc}")
            return 1

        print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")
        print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}")
        print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
        if expected_filename is not None:
            print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
        print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")
        print(f"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}")
        if note is not None:
            print(f"ZIG_TOOLCHAIN_NOTE={note}")
            return 1
        return 0

    zig: str | None = None
    min_version_raw: str | None = args.min_version
    expected_channel_raw: str | None = None
    version: str | None = None
    try:
        zig = resolve_zig_executable(args.zig)
        min_version_raw = args.min_version or load_min_version()
        expected_channel_raw = None if args.min_version else load_pinned_channel()
        parse_zig_version(min_version_raw)
        if expected_channel_raw is not None:
            parse_zig_version(expected_channel_raw)
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}")
        if expected_channel_raw is not None:
            print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
            print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
        elif args.min_version is not None:
            print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        else:
            print("ZIG_TOOLCHAIN_PIN_POLICY=unresolved")
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    if zig is None:
        search_roots = iter_zig_search_roots()
        message, search_roots_summary = describe_missing_zig(
            pinned_channel=expected_channel_raw,
            search_roots=search_roots,
        )
        print("ZIG_TOOLCHAIN_STATUS=missing")
        print("ZIG_TOOLCHAIN_PATH=unresolved")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
        if expected_channel_raw is not None:
            print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
            print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
        else:
            print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        print(f"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}")
        print(f"ZIG_TOOLCHAIN_NOTE={message}")
        return 0 if args.allow_missing else 1

    try:
        version = read_zig_version(zig)
        status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig}")
        if version is not None:
            print(f"ZIG_TOOLCHAIN_VERSION={version}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}")
        if expected_channel_raw is not None:
            print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
            print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
        elif args.min_version is not None:
            print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        else:
            print("ZIG_TOOLCHAIN_PIN_POLICY=unresolved")
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    exit_code = 0 if status == "present" else 1
    print(f"ZIG_TOOLCHAIN_STATUS={status}")
    print(f"ZIG_TOOLCHAIN_PATH={zig}")
    print(f"ZIG_TOOLCHAIN_VERSION={version}")
    print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")
    if expected_channel_raw is not None:
        print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
        print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
    else:
        print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
    if note is not None:
        print(f"ZIG_TOOLCHAIN_NOTE={note}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())