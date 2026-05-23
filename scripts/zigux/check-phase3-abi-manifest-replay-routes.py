#!/usr/bin/env python3
"""Fail-close the Phase 3 ABI manifest's export/UAPI and policy-unsafe replay routes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase3-abi-manifest-replay-routes.py"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"',
    '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"',
    '"python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"',
    '"python3 scripts/zigux/check-phase3-selftest-surface.py"',
    '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-export-uapi-survey.py"',
    '"python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"',
    '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"',
    '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"',
    '"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"',
    '"python3 scripts/zigux/check-phase3-policy-dump.py"',
    '"zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig"',
    '"zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"',
    '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"',
    '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"',
)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
}

REQUIRED_PACKET_FILES = (
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "scripts/zigux/check-phase3-policy-dump.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-dump.py",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    validator_path = repo_root / VALIDATOR_PATH
    if not validator_path.is_file():
        issues.append(f"missing repo file: {VALIDATOR_PATH.as_posix()}")
    else:
        validator_text = _read(validator_path)
        for marker in REQUIRED_VALIDATOR_MARKERS:
            if marker not in validator_text:
                issues.append(
                    f"missing {VALIDATOR_PATH.as_posix()} marker: {marker}"
                )

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
        return issues

    for route in REQUIRED_REPLAY_ROUTES:
        if route not in replay_routes:
            issues.append(f"phase3_abi_manifest.json missing replay route: {route}")

    return issues


def _sample_validator() -> str:
    lines = [
        "#!/usr/bin/env python3",
        "REQUIRED_MANIFEST_REPLAY_ROUTES = (",
        '    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",',
        '    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",',
        '    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",',
        '    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",',
        '    "python3 scripts/zigux/check-phase3-selftest-surface.py",',
        '    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",',
        '    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",',
        '    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",',
        '    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",',
        '    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",',
        '    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",',
        '    "python3 scripts/zigux/check-phase3-policy-dump.py",',
        '    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",',
        '    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",',
        '    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",',
        '    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",',
        ")",
        "",
    ]
    return "\n".join(lines)


def _sample_manifest() -> str:
    manifest = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    }
    return json.dumps(manifest, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    _write(root / VALIDATOR_PATH, _sample_validator())
    _write(root / MANIFEST_PATH, _sample_manifest())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_manifest_routes_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        validator_path = repo_root / VALIDATOR_PATH
        manifest_path = repo_root / MANIFEST_PATH

        current = _read(validator_path)
        needle = '    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"scripts/zigux/check-phase3-abi-manifest-replay-routes.py"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected validator packet-file marker drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected validator self-test route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected validator direct route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/check-phase3-selftest-surface.py",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/check-phase3-selftest-surface.py"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected export-shim validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-unsafe self-test validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-unsafe direct validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/check-phase3-policy-dump.py --self-test"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump self-test validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "python3 scripts/zigux/check-phase3-policy-dump.py",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"python3 scripts/zigux/check-phase3-policy-dump.py"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump direct validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        current = _read(validator_path)
        needle = '    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",\n'
        _write(validator_path, current.replace(needle, "", 1))
        issues = validate_repo(repo_root)
        expected = (
            "missing scripts/zigux/validate-phase3.py marker: "
            '"zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"'
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump build validator-route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("scripts/zigux/check-phase3-abi-manifest-replay-routes.py")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "scripts/zigux/check-phase3-abi-manifest-replay-routes.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected checker packet-file drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove(
            "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-unsafe note packet-file drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("scripts/zigux/validate-phase3-policy-unsafe-survey.py")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "scripts/zigux/validate-phase3-policy-unsafe-survey.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-unsafe validator packet-file drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].remove("zigux/tests/phase3_policy_dump.zig")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "zigux/tests/phase3_policy_dump.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump packet-file drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected checker self-test route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected checker direct route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-unsafe self-test route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/check-phase3-policy-dump.py"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-policy-dump.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump direct route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected policy-dump build route drift was not reported")
            return 1

        _populate_repo(repo_root)
        manifest = json.loads(_read(manifest_path))
        manifest["slug"] = "stale-slug"
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = "phase3_abi_manifest.json wrong slug: 'stale-slug' != 'phase3-abi-packet'"
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected slug drift was not reported")
            return 1

    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=pass")
    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=20")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 ABI manifest's export/UAPI and policy-unsafe replay routes."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI validator and manifest",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
