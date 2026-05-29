#!/usr/bin/env python3
"""Validate the focused Phase 3 policy-and-unsafe replay packet."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
REPLAY_PATH = Path("zigux/tests/phase3_policy_unsafe.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_unsafe_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_POLICY_UNSAFE_REPLAY_GATE=python3 scripts/zigux/check-phase3-policy-unsafe-replay.py",
        "scripts/zigux/check-phase3-policy-unsafe-replay.py",
        "packet-local replay checker",
    ),
    REPLAY_PATH: (
        'test "phase3 policy unsafe replay decodes shared policy records" {',
        'test "phase3 policy unsafe replay keeps ABI recognition aligned with helper decoders" {',
        'test "phase3 policy unsafe replay keeps require gates fail closed" {',
        'test "phase3 policy unsafe replay keeps policy consequences explicit" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_unsafe.zig"),',
        'root_module.addImport("panic_policy", panic_policy);',
        'root_module.addImport("allocator_policy", allocator_policy);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        '"phase3-policy-unsafe-test"',
        '"Run the focused Phase 3 policy and unsafe replay"',
    ),
    MAKEFILE_PATH: (
        "phase3-policy-unsafe-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    ),
    MANIFEST_PATH: (
        '"zigux/tests/phase3_policy_unsafe.zig"',
        '"zigux/tests/phase3_policy_unsafe_build.zig"',
        '"scripts/zigux/check-phase3-policy-unsafe-replay.py"',
        '"python3 scripts/zigux/check-phase3-policy-unsafe-replay.py --self-test"',
        '"python3 scripts/zigux/check-phase3-policy-unsafe-replay.py"',
        '"zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig"',
        '"make -C zigux phase3-policy-unsafe-test"',
    ),
    ABI_BINDINGS_PATH: (
        "pub fn interopPolicyIsRecognized(policy: InteropPolicy) bool {",
        "pub fn unsafeScopeFromInteropPolicy(policy: InteropPolicy) ?UnsafeScope {",
    ),
    PANIC_POLICY_PATH: (
        "pub fn causesImmediateHaltInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn actionForInteropPolicy(policy: abi.InteropPolicy) ?Action {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub fn requireInitFlowInteropPolicy(policy: abi.InteropPolicy, expected: InitFlow) InitFlowError!void {",
        "pub fn requiresResetOnInitInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
    ),
    NARROW_PATH: (
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn surfaceFromInteropPolicy(policy: abi.InteropPolicy) ?Surface {",
    ),
}

REQUIRED_PACKET_FILES = (
    REPLAY_PATH.as_posix(),
    BUILD_PATH.as_posix(),
    "scripts/zigux/check-phase3-policy-unsafe-replay.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-policy-unsafe-replay.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-unsafe-replay.py",
    "zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "make -C zigux phase3-policy-unsafe-test",
)

SELF_TEST_CASES = (
    (SURVEY_PATH, REQUIRED_MARKERS[SURVEY_PATH][0]),
    (REPLAY_PATH, REQUIRED_MARKERS[REPLAY_PATH][0]),
    (BUILD_PATH, REQUIRED_MARKERS[BUILD_PATH][-2]),
    (MAKEFILE_PATH, REQUIRED_MARKERS[MAKEFILE_PATH][0]),
    (PANIC_POLICY_PATH, REQUIRED_MARKERS[PANIC_POLICY_PATH][0]),
    (ALLOCATOR_POLICY_PATH, REQUIRED_MARKERS[ALLOCATOR_POLICY_PATH][0]),
    (UNSAFE_POLICY_PATH, REQUIRED_MARKERS[UNSAFE_POLICY_PATH][0]),
    (NARROW_PATH, REQUIRED_MARKERS[NARROW_PATH][0]),
    (MANIFEST_PATH, REQUIRED_MARKERS[MANIFEST_PATH][2]),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        issues.append("phase3_policy_starter_packet_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    "phase3_policy_starter_packet_manifest.json missing packet_files entry: "
                    + entry
                )

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_policy_starter_packet_manifest.json replay_routes is not a list")
    else:
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    "phase3_policy_starter_packet_manifest.json missing replay route: "
                    + entry
                )

    return issues


def verify_replay(repo_root: Path, zig: str) -> list[str]:
    result = subprocess.run(
        [
            zig,
            "build",
            "phase3-policy-unsafe-test",
            "--build-file",
            BUILD_PATH.as_posix(),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
    return [f"phase3 policy-unsafe replay failed: {detail}"]


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")

    manifest = {
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_replay_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("scripts/zigux/check-phase3-policy-unsafe-replay.py")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_policy_starter_packet_manifest.json missing packet_files entry: "
            "scripts/zigux/check-phase3-policy-unsafe-replay.py"
        )
        if expected not in issues:
            print("PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=fail")
            print("expected manifest packet-file drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/check-phase3-policy-unsafe-replay.py"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_policy_starter_packet_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-policy-unsafe-replay.py"
        )
        if expected not in issues:
            print("PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=fail")
            print("expected manifest replay-route drift was not reported")
            return 1

    print("PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_REPLAY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 3}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 policy-and-unsafe replay packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--zig", help="path to zig executable")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if not args.skip_exec:
        issues.extend(verify_replay(args.repo_root, _resolve_tool(args.zig, "ZIG", "zig")))
    if issues:
        print("PHASE3_POLICY_UNSAFE_REPLAY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SURVEY_PATH}")
    print(f"validated {args.repo_root / REPLAY_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    if not args.skip_exec:
        print(f"verified replay {args.repo_root / BUILD_PATH}")
    print("PHASE3_POLICY_UNSAFE_REPLAY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
