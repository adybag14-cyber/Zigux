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
ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FALLBACK_MIN_VERSION = "0.16.0"
EXPECTED_SELF_TEST_CASE_COUNT = 51
ARCHIVE_CACHE_DIRNAME = "archives"


@dataclass(frozen=True, order=True)
class ZigVersion:
    major: int
    minor: int
    patch: int
    release_rank: int
    dev_build: int


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate key {key!r}")
        payload[key] = value
    return payload


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


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(
            policy_path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    except ValueError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:
    payload = load_policy(policy_path)
    if payload is None:
        return fallback
    min_version = payload.get("minimum_version")
    if not isinstance(min_version, str) or not min_version.strip():
        raise ValueError(f"invalid minimum_version in {policy_path}")
    return min_version.strip()


def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    payload = load_policy(policy_path)
    if payload is None:
        return None
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"invalid channel in {policy_path}")
    return channel.strip()


def load_policy_archive_digests(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, str]:
    payload = load_policy(policy_path)
    if payload is None:
        return {}
    archive_sha256 = payload.get("archive_sha256")
    if archive_sha256 is None:
        return {}
    if not isinstance(archive_sha256, dict):
        raise ValueError(f"invalid archive_sha256 in {policy_path}")

    digests: dict[str, str] = {}
    for target_key, digest in archive_sha256.items():
        if not isinstance(target_key, str) or not target_key.strip():
            raise ValueError(f"invalid archive target in {policy_path}")
        if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
            raise ValueError(f"invalid archive sha256 for {target_key} in {policy_path}")
        digests[target_key.strip()] = digest.lower()
    return digests


def load_policy_archive_sha256(policy_path: Path = TOOLCHAIN_POLICY, target_key: str | None = None) -> str | None:
    if target_key is None:
        return None
    return load_policy_archive_digests(policy_path).get(target_key)


def resolve_archive_target(
    explicit_target: str | None = None,
    *,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> str | None:
    if explicit_target is not None and explicit_target.strip():
        return explicit_target.strip()
    digests = load_policy_archive_digests(policy_path)
    if not digests:
        return None
    if len(digests) == 1:
        return next(iter(digests))
    raise ValueError("archive target must be specified when multiple archive digests exist in the toolchain policy")


def resolve_default_archive_target(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:
    digests = load_policy_archive_digests(policy_path)
    if len(digests) == 1:
        return next(iter(digests))
    return None


def infer_archive_suffix(target_key: str) -> str:
    return ".zip" if target_key.rsplit("-", 1)[-1] == "windows" else ".tar.xz"


def calculate_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_archive_sha256(path: Path, expected_sha256: str) -> str:
    try:
        actual_sha256 = calculate_sha256(path)
    except FileNotFoundError as exc:
        raise ValueError(f"zig archive not found: {path}") from exc
    except OSError as exc:
        raise ValueError(f"failed to read zig archive {path}: {exc}") from exc

    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"zig archive sha256 mismatch for {path.name}: expected {expected_sha256.lower()}, got {actual_sha256.lower()}"
        )
    return actual_sha256.lower()


def iter_repo_local_zig_candidates(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
) -> list[Path]:
    toolchain_root = root / ".zig-toolchain"
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    if pinned_channel is not None:
        pinned_root = toolchain_root / f"zig-x86_64-linux-{pinned_channel}"
        add_candidate(pinned_root / "zig")
        add_candidate(pinned_root / "bin" / "zig")

    if toolchain_root.exists():
        for child in sorted(toolchain_root.iterdir()):
            add_candidate(child / "zig")
            add_candidate(child / "bin" / "zig")
    return candidates


def iter_repo_local_archive_candidates(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
    archive_target: str | None = None,
) -> list[Path]:
    if pinned_channel is None or archive_target is None:
        return []

    toolchain_root = root / ".zig-toolchain"
    archive_name = f"zig-{archive_target}-{pinned_channel}{infer_archive_suffix(archive_target)}"
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    add_candidate(toolchain_root / ARCHIVE_CACHE_DIRNAME / archive_name)
    add_candidate(toolchain_root / archive_name)
    return candidates


def resolve_repo_local_archive(
    *,
    root: Path = ROOT,
    pinned_channel: str | None = None,
    archive_target: str | None = None,
) -> Path | None:
    for candidate in iter_repo_local_archive_candidates(
        root=root,
        pinned_channel=pinned_channel,
        archive_target=archive_target,
    ):
        if candidate.is_file():
            return candidate
    return None


def resolve_zig_executable(
    explicit_zig: str | None = None,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
    which=shutil.which,
) -> str | None:
    if explicit_zig is not None:
        return explicit_zig

    pinned_channel = load_pinned_channel(policy_path)
    for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):
        if candidate.is_file():
            return str(candidate)
    return which("zig")


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


def emit_archive_metadata(
    archive_path: Path | None,
    archive_target: str | None,
    expected_archive_sha256: str | None,
    actual_archive_sha256: str | None,
    archive_status: str | None,
) -> None:
    if archive_path is None:
        return
    print(f"ZIG_TOOLCHAIN_ARCHIVE={archive_path}")
    if archive_target is not None:
        print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target}")
    if expected_archive_sha256 is not None:
        print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_archive_sha256}")
    if actual_archive_sha256 is not None:
        print(f"ZIG_TOOLCHAIN_ARCHIVE_SHA256={actual_archive_sha256}")
    if archive_status is not None:
        print(f"ZIG_TOOLCHAIN_ARCHIVE_SHA256_STATUS={archive_status}")


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
        root = Path(tmp_dir)
        policy_path = root / "zig-toolchain-policy.json"
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.15.0")
        expect_equal(load_pinned_channel(policy_path), None)
        expect_equal(load_policy_archive_sha256(policy_path, "x86_64-linux"), None)
        expect_equal(resolve_archive_target(policy_path=policy_path), None)
        expect_equal(resolve_default_archive_target(policy_path=policy_path), None)
        policy_path.write_text(
            '{"channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"}}\n',
            encoding="utf-8",
        )
        expect_equal(load_min_version(policy_path, "0.15.0"), "0.17.0-dev.87+9b177a7d2")
        expect_equal(load_pinned_channel(policy_path), "0.17.0-dev.87+9b177a7d2")
        expect_equal(load_policy_archive_sha256(policy_path, "x86_64-linux"), "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77")
        expect_equal(load_policy_archive_sha256(policy_path, "aarch64-linux"), None)
        expect_equal(resolve_archive_target(policy_path=policy_path), "x86_64-linux")
        expect_equal(resolve_archive_target("aarch64-linux", policy_path=policy_path), "aarch64-linux")
        expect_equal(resolve_default_archive_target(policy_path=policy_path), "x86_64-linux")
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
        expect_equal(resolve_zig_executable("/custom/zig", root=root, policy_path=policy_path, which=lambda _: None), "/custom/zig")
        pinned_zig.write_text("#!/bin/sh\n", encoding="utf-8")
        expect_equal(
            iter_repo_local_zig_candidates(root=root, pinned_channel="0.17.0-dev.87+9b177a7d2")[:2],
            [pinned_zig, toolchain_dir / "bin" / "zig"],
        )
        archive_path = root / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        archive_path.write_bytes(b"zigux-archive")
        expected_archive_sha256 = hashlib.sha256(b"zigux-archive").hexdigest()
        policy_path.write_text(
            '{"channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + expected_archive_sha256 + '"}}\n',
            encoding="utf-8",
        )
        cached_archive = root / ".zig-toolchain" / ARCHIVE_CACHE_DIRNAME / archive_path.name
        cached_archive.parent.mkdir(parents=True)
        cached_archive.write_bytes(b"zigux-archive")
        expect_equal(
            iter_repo_local_archive_candidates(
                root=root,
                pinned_channel="0.17.0-dev.87+9b177a7d2",
                archive_target="x86_64-linux",
            ),
            [cached_archive, root / ".zig-toolchain" / archive_path.name],
        )
        expect_equal(
            resolve_repo_local_archive(
                root=root,
                pinned_channel="0.17.0-dev.87+9b177a7d2",
                archive_target="x86_64-linux",
            ),
            cached_archive,
        )
        expect_equal(verify_archive_sha256(archive_path, expected_archive_sha256), expected_archive_sha256)
        expect_equal(verify_archive_sha256(cached_archive, expected_archive_sha256), expected_archive_sha256)
        expect_raises(lambda: verify_archive_sha256(archive_path, "0" * 64), "zig archive sha256 mismatch")
        expect_raises(lambda: verify_archive_sha256(root / "missing.tar.xz", expected_archive_sha256), "zig archive not found")
        policy_path.write_text('{"minimum_version":7,"channel":"0.17.0-dev.87+9b177a7d2"}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid minimum_version")
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":7}\n', encoding="utf-8")
        expect_raises(lambda: load_pinned_channel(policy_path), "invalid channel")
        expect_raises(lambda: resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: None), "invalid channel")
        expect_equal(resolve_default_archive_target(policy_path=policy_path), None)
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":7}\n', encoding="utf-8")
        expect_raises(lambda: load_policy_archive_sha256(policy_path, "x86_64-linux"), "invalid archive_sha256")
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"short"}}\n', encoding="utf-8")
        expect_raises(lambda: load_policy_archive_sha256(policy_path, "x86_64-linux"), "invalid archive sha256")
        policy_path.write_text('{"minimum_version":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.18.0","channel":"0.17.0-dev.87+9b177a7d2"}\n', encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "duplicate key 'minimum_version'")
        policy_path.write_text(
            '{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + expected_archive_sha256 + '","x86_64-linux":"' + ("1" * 64) + '"}}\n',
            encoding="utf-8",
        )
        expect_raises(lambda: load_policy_archive_sha256(policy_path, "x86_64-linux"), "duplicate key 'x86_64-linux'")
        policy_path.write_text(
            '{"minimum_version":"0.17.0-dev.87+9b177a7d2","channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"' + expected_archive_sha256 + '","aarch64-linux":"' + ("2" * 64) + '"}}\n',
            encoding="utf-8",
        )
        expect_raises(lambda: resolve_archive_target(policy_path=policy_path), "archive target must be specified when multiple archive digests exist")
        expect_equal(resolve_archive_target("aarch64-linux", policy_path=policy_path), "aarch64-linux")
        expect_equal(resolve_default_archive_target(policy_path=policy_path), None)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        expect_raises(lambda: load_min_version(policy_path, "0.15.0"), "invalid toolchain policy JSON")
        expect_raises(lambda: parse_zig_version("master"))

    with tempfile.TemporaryDirectory(prefix="zigux_toolchain_resolution_") as tmp_dir:
        root = Path(tmp_dir)
        policy_path = root / "zig-toolchain-policy.json"
        policy_path.write_text(
            '{"channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2"}\n',
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

    assert case_count == EXPECTED_SELF_TEST_CASE_COUNT
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
    parser.add_argument("--zig", help="Explicit zig executable path.")
    parser.add_argument("--archive", help="Optional local Zig bootstrap archive to verify against the pinned policy sha256.")
    parser.add_argument("--archive-target", help="Explicit policy target key for --archive, such as x86_64-linux.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    archive_path = Path(args.archive).expanduser() if args.archive is not None else None
    archive_target: str | None = None
    expected_archive_sha256: str | None = None
    actual_archive_sha256: str | None = None
    archive_status: str | None = None
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
        if archive_path is not None:
            archive_target = resolve_archive_target(args.archive_target)
            if archive_target is None:
                raise ValueError("archive target could not be resolved from toolchain policy")
            expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target)
            if expected_archive_sha256 is None:
                raise ValueError(f"toolchain policy does not define archive sha256 for target {archive_target}")
            actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)
            archive_status = "verified"
        elif args.min_version is None:
            archive_target = resolve_default_archive_target()
            expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target)
            archive_path = resolve_repo_local_archive(
                pinned_channel=expected_channel_raw,
                archive_target=archive_target,
            )
            if archive_path is not None and expected_archive_sha256 is not None:
                actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)
                archive_status = "verified"
    except ValueError as exc:
        print("ZIG_TOOLCHAIN_STATUS=invalid")
        print(f"ZIG_TOOLCHAIN_PATH={zig or 'unresolved'}")
        print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}")
        if expected_channel_raw is not None:
            print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
            print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
        elif args.min_version is not None:
            print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")
        else:
            print("ZIG_TOOLCHAIN_PIN_POLICY=unresolved")
        emit_archive_metadata(
            archive_path,
            archive_target,
            expected_archive_sha256,
            actual_archive_sha256,
            archive_status or ("invalid" if archive_path is not None else None),
        )
        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
        return 1

    if zig is None:
        message = "zig not found on PATH or in repo-local .zig-toolchain"
        if args.allow_missing:
            print("ZIG_TOOLCHAIN_STATUS=missing")
            print(f"ZIG_TOOLCHAIN_NOTE={message}")
            emit_archive_metadata(
                archive_path,
                archive_target,
                expected_archive_sha256,
                actual_archive_sha256,
                archive_status,
            )
            return 0
        print(message, file=sys.stderr)
        return 1

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
        emit_archive_metadata(
            archive_path,
            archive_target,
            expected_archive_sha256,
            actual_archive_sha256,
            archive_status or ("invalid" if archive_path is not None else None),
        )
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
    emit_archive_metadata(
        archive_path,
        archive_target,
        expected_archive_sha256,
        actual_archive_sha256,
        archive_status,
    )
    if note is not None:
        print(f"ZIG_TOOLCHAIN_NOTE={note}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())