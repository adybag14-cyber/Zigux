#!/usr/bin/env python3
"""Fail closed when the Phase 2 policy manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import string
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

EXPECTED_POLICY_SURFACE = (
    "scripts/zigux/zig-toolchain-policy.json",
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_TARGET_SCOPE = (
    "x86_64-linux",
)
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
EXPECTED_ARCHIVE_SHA_TARGET = "x86_64-linux"
EXPECTED_ARCHIVE_SHA256 = (
    "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(policy_surface: list[object] | None = None) -> str:
    payload = {
        "phase": EXPECTED_PHASE,
        "status": "active",
        "present_surfaces": {
            "policy": list(
                EXPECTED_POLICY_SURFACE if policy_surface is None else policy_surface
            ),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_policy(
    *,
    channel: str = EXPECTED_CHANNEL,
    minimum_version: str = EXPECTED_CHANNEL,
    archive_targets: list[object] | None = None,
    required_make_routes: list[object] | None = None,
    archive_sha256: dict[str, object] | None = None,
    channel_minimum_lockstep: bool = True,
) -> str:
    payload = {
        "phase": EXPECTED_PHASE,
        "channel": channel,
        "minimum_version": minimum_version,
        "archive_sha256": (
            {EXPECTED_ARCHIVE_SHA_TARGET: EXPECTED_ARCHIVE_SHA256}
            if archive_sha256 is None
            else archive_sha256
        ),
        "upgrade_policy": {
            "channel_minimum_lockstep": channel_minimum_lockstep,
            "archive_target_scope": list(
                EXPECTED_ARCHIVE_TARGET_SCOPE
                if archive_targets is None
                else archive_targets
            ),
            "required_make_routes": list(
                EXPECTED_REQUIRED_MAKE_ROUTES
                if required_make_routes is None
                else required_make_routes
            ),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def _is_hex_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in string.hexdigits for ch in value)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    policy_path = repo_root / POLICY_PATH

    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]
    if not policy_path.is_file():
        return [f"missing policy file: {POLICY_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid policy json: {exc.msg}"]

    issues: list[str] = []

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    policy_surface = surfaces.get("policy")
    if not isinstance(policy_surface, list):
        return ["invalid policy surface list"]

    seen_policy_surface: set[str] = set()
    for index, entry in enumerate(policy_surface):
        if not isinstance(entry, str):
            issues.append(f"invalid policy surface entry at index {index}: {entry!r}")
            continue
        if entry in seen_policy_surface:
            issues.append(f"duplicate policy surface entry: {entry}")
        seen_policy_surface.add(entry)

    if len(policy_surface) != len(EXPECTED_POLICY_SURFACE):
        issues.append(
            "policy surface count drift: "
            f"expected {len(EXPECTED_POLICY_SURFACE)}, found {len(policy_surface)}"
        )

    for index, expected in enumerate(EXPECTED_POLICY_SURFACE):
        if index >= len(policy_surface):
            issues.append(f"missing policy surface entry: {expected}")
            continue
        actual = policy_surface[index]
        if actual != expected:
            issues.append(
                f"policy surface order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    if policy.get("phase") != EXPECTED_PHASE:
        issues.append(
            f"policy phase drift: expected {EXPECTED_PHASE!r}, "
            f"found {policy.get('phase')!r}"
        )
    if policy.get("channel") != EXPECTED_CHANNEL:
        issues.append(
            f"policy channel drift: expected {EXPECTED_CHANNEL!r}, "
            f"found {policy.get('channel')!r}"
        )
    if policy.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(
            "policy minimum_version drift: "
            f"expected {EXPECTED_CHANNEL!r}, found {policy.get('minimum_version')!r}"
        )

    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("invalid archive_sha256 object")
    else:
        sha_value = archive_sha256.get(EXPECTED_ARCHIVE_SHA_TARGET)
        if sha_value != EXPECTED_ARCHIVE_SHA256:
            issues.append(
                f"archive sha drift for {EXPECTED_ARCHIVE_SHA_TARGET}: "
                f"expected {EXPECTED_ARCHIVE_SHA256!r}, found {sha_value!r}"
            )
        elif not _is_hex_sha256(sha_value):
            issues.append(
                f"invalid archive sha256 for {EXPECTED_ARCHIVE_SHA_TARGET}: {sha_value!r}"
            )
        extra_targets = sorted(
            target
            for target in archive_sha256
            if target != EXPECTED_ARCHIVE_SHA_TARGET
        )
        if extra_targets:
            issues.append(
                "unexpected archive_sha256 targets: " + ",".join(extra_targets)
            )

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + ["invalid upgrade_policy object"]

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append("channel_minimum_lockstep drift")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list):
        issues.append("invalid archive_target_scope list")
    else:
        seen_scope: set[str] = set()
        for index, entry in enumerate(archive_target_scope):
            if not isinstance(entry, str):
                issues.append(
                    f"invalid archive_target_scope entry at index {index}: {entry!r}"
                )
                continue
            if entry in seen_scope:
                issues.append(f"duplicate archive_target_scope entry: {entry}")
            seen_scope.add(entry)
        if len(archive_target_scope) != len(EXPECTED_ARCHIVE_TARGET_SCOPE):
            issues.append(
                "archive_target_scope count drift: "
                f"expected {len(EXPECTED_ARCHIVE_TARGET_SCOPE)}, "
                f"found {len(archive_target_scope)}"
            )
        for index, expected in enumerate(EXPECTED_ARCHIVE_TARGET_SCOPE):
            if index >= len(archive_target_scope):
                issues.append(f"missing archive_target_scope entry: {expected}")
                continue
            actual = archive_target_scope[index]
            if actual != expected:
                issues.append(
                    f"archive_target_scope order drift at index {index}: "
                    f"expected {expected!r}, found {actual!r}"
                )

    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list):
        issues.append("invalid required_make_routes list")
    else:
        seen_routes: set[str] = set()
        for index, entry in enumerate(required_make_routes):
            if not isinstance(entry, str):
                issues.append(
                    f"invalid required_make_routes entry at index {index}: {entry!r}"
                )
                continue
            if entry in seen_routes:
                issues.append(f"duplicate required_make_routes entry: {entry}")
            seen_routes.add(entry)
        if len(required_make_routes) != len(EXPECTED_REQUIRED_MAKE_ROUTES):
            issues.append(
                "required_make_routes count drift: "
                f"expected {len(EXPECTED_REQUIRED_MAKE_ROUTES)}, "
                f"found {len(required_make_routes)}"
            )
        for index, expected in enumerate(EXPECTED_REQUIRED_MAKE_ROUTES):
            if index >= len(required_make_routes):
                issues.append(f"missing required_make_routes entry: {expected}")
                continue
            actual = required_make_routes[index]
            if actual != expected:
                issues.append(
                    f"required_make_routes order drift at index {index}: "
                    f"expected {expected!r}, found {actual!r}"
                )

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_policy_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / POLICY_PATH, _sample_policy())

        issues = validate(root)
        if issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest([]))
        issues = validate(root)
        if "missing policy surface entry: scripts/zigux/zig-toolchain-policy.json" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected missing policy surface entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest([123]))
        issues = validate(root)
        if "invalid policy surface entry at index 0: 123" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected invalid policy surface entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(
                [
                    "scripts/zigux/zig-toolchain-policy.json",
                    "scripts/zigux/zig-toolchain-policy.json",
                ]
            ),
        )
        issues = validate(root)
        if "duplicate policy surface entry: scripts/zigux/zig-toolchain-policy.json" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected duplicate policy surface entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": "bad"}\n')
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / POLICY_PATH, _sample_policy(channel="0.18.0-dev"))
        issues = validate(root)
        if (
            "policy channel drift: expected '0.17.0-dev.87+9b177a7d2', "
            "found '0.18.0-dev'"
        ) not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected policy channel drift was not reported")
            return 1
        case_count += 1

        _write(
            root / POLICY_PATH,
            _sample_policy(archive_targets=["x86_64-linux", "aarch64-linux"]),
        )
        issues = validate(root)
        if "archive_target_scope count drift: expected 1, found 2" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected archive_target_scope count drift was not reported")
            return 1
        case_count += 1

        _write(
            root / POLICY_PATH,
            _sample_policy(
                required_make_routes=[
                    "phase2-toolchain",
                    "phase2-toolchain",
                    "phase2-kconfig",
                    "phase2-cross",
                    "phase2-genksyms",
                    "phase2-fixdep",
                    "phase2-validate",
                ]
            ),
        )
        issues = validate(root)
        if "duplicate required_make_routes entry: phase2-toolchain" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected duplicate required_make_routes entry was not reported")
            return 1
        case_count += 1

        _write(
            root / POLICY_PATH,
            _sample_policy(
                archive_sha256={
                    "x86_64-linux": "xyz",
                    "aarch64-linux": EXPECTED_ARCHIVE_SHA256,
                }
            ),
        )
        issues = validate(root)
        if (
            "archive sha drift for x86_64-linux: expected "
            "'313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77', "
            "found 'xyz'"
        ) not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected archive sha drift was not reported")
            return 1
        if "unexpected archive_sha256 targets: aarch64-linux" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected unexpected archive_sha256 target was not reported")
            return 1
        case_count += 1

        _write(root / POLICY_PATH, '{"phase": "Phase 2", "upgrade_policy": }\n')
        issues = validate(root)
        if "invalid policy json: Expecting value" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected invalid policy json was not reported")
            return 1
        case_count += 1

        _write(root / POLICY_PATH, _sample_policy())
        (root / POLICY_PATH).unlink()
        issues = validate(root)
        if "missing policy file: scripts/zigux/zig-toolchain-policy.json" not in issues:
            print("PHASE2_POLICY_SURFACE_SELF_TEST=fail")
            print("expected missing policy file was not reported")
            return 1
        case_count += 1

    print("PHASE2_POLICY_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_POLICY_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / POLICY_PATH, _sample_policy())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 policy surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 manifest and policy file",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    issues = validate(args.root)
    if issues:
        print("PHASE2_POLICY_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_POLICY_SURFACE=pass")
    print(f"PHASE2_POLICY_SURFACE_COUNT={len(EXPECTED_POLICY_SURFACE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())