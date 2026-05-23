#!/usr/bin/env python3
"""Fail-close the Phase 3 ABI manifest's selftest-surface replay routes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase3.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_VALIDATOR_MARKERS = (
    '"python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"',
    '"python3 scripts/zigux/check-phase3-selftest-surface.py"',
)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
}

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "python3 scripts/zigux/check-phase3-selftest-surface.py",
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
        '    "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test",',
        '    "python3 scripts/zigux/check-phase3-selftest-surface.py",',
        ")",
        "",
    ]
    return "\n".join(lines)


def _sample_manifest() -> str:
    manifest = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
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
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].remove(
            "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"
        )
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(repo_root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "python3 scripts/zigux/check-phase3-selftest-surface.py --self-test"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST=fail")
            print("expected manifest self-test route drift was not reported")
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
    print("PHASE3_ABI_MANIFEST_REPLAY_ROUTES_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 ABI manifest's selftest-surface replay routes."
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