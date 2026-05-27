#!/usr/bin/env python3
"""Fail-close the current Phase 9 manifest/catalog/ownership packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CATALOG_PATH = Path("scripts/zigux/phase9_catalog.py")
README_PATH = Path("scripts/zigux/README.md")
OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
MANIFEST_PATH = Path("zigux/tests/runtime_pilot_manifest.json")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase9.py")

REQUIRED_FILES = (
    CATALOG_PATH,
    README_PATH,
    OWNERSHIP_MAP_PATH,
    MANIFEST_PATH,
    VALIDATOR_PATH,
)

CATALOG_MARKERS = (
    'PHASE9_CATALOG_PHASE = "Phase 9"',
    'PHASE9_CATALOG_LANE = "P9-L11"',
    'MANIFEST_PATH = Path("zigux/tests/runtime_pilot_manifest.json")',
    'OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")',
    '"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof"',
    '"scripts/zigux/check-phase9-catalog-selftest.py"',
    '"scripts/zigux/validate-phase9.py"',
    '"python3 scripts/zigux/phase9_catalog.py --pretty"',
    '"python3 scripts/zigux/validate-phase9.py"',
    'print("PHASE9_CATALOG_SELF_TEST=pass")',
)

OWNERSHIP_MAP_MARKERS = (
    "PHASE9_RUNTIME_PILOT_MANIFEST=zigux/tests/runtime_pilot_manifest.json",
    "PHASE9_RUNTIME_PILOT_CATALOG=scripts/zigux/phase9_catalog.py",
    "PHASE9_RUNTIME_PILOT_CATALOG_SELFTEST=scripts/zigux/check-phase9-catalog-selftest.py",
    "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts/zigux/validate-phase9.py",
    "PHASE9_RUNTIME_PILOT_SCRIPTS_ROOT=scripts/zigux/README.md",
    "PHASE9_RUNTIME_PILOT_SHARED_NOTE=Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "PHASE9_RUNTIME_PILOT_SHARED_BUILD=zigux/tests/phase9_build.zig",
    "PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "## Shared Owner Packet",
    "## Shared Runtime Loader Owner",
    "## Trace Events Family Owner",
    "## Runtime Bitmap Family Owner",
    "## Runtime Kretprobe Family Owner",
)

README_MARKERS = (
    "scripts/zigux/phase9_catalog.py",
    "scripts/zigux/check-phase9-catalog-selftest.py",
    "python3 scripts/zigux/check-phase9-catalog-selftest.py --self-test",
    "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
    "zigux/tests/runtime_pilot_manifest.json",
    "scripts/zigux/validate-phase9.py",
    "python3 scripts/zigux/validate-phase9.py --self-test",
    "python3 scripts/zigux/validate-phase9.py",
)

README_FORBIDDEN_MARKERS = (
    "there is still no dedicated shared `validate-phase9.py` rerun path",
)

MANIFEST_MARKERS = (
    '"phase": "Phase 9"',
    '"lane_key": "P9-L11"',
    '"ownership_map_path": "Documentation/zigux/phase9-runtime-pilot-ownership-map.md"',
    '"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof"',
    '"scripts/zigux/phase9_catalog.py"',
    '"scripts/zigux/validate-phase9.py"',
    '"zigux/tests/runtime_pilot_manifest.json"',
)

VALIDATOR_MARKERS = (
    "EXPECTED_PACKET_FILES = (",
    '"scripts/zigux/validate-phase9.py",',
    '"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",',
    "EXPECTED_REPLAY_ROUTES = (",
    '"python3 scripts/zigux/validate-phase9.py",',
    "PHASE9_VALIDATE_SELF_TEST=pass",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (repo_root / relative_path).is_file():
            issues.append(f"missing repo file: {relative_path.as_posix()}")

    marker_map = {
        CATALOG_PATH: CATALOG_MARKERS,
        OWNERSHIP_MAP_PATH: OWNERSHIP_MAP_MARKERS,
        README_PATH: README_MARKERS,
        MANIFEST_PATH: MANIFEST_MARKERS,
        VALIDATOR_PATH: VALIDATOR_MARKERS,
    }
    for relative_path, markers in marker_map.items():
        path = repo_root / relative_path
        if not path.is_file():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    readme_path = repo_root / README_PATH
    if readme_path.is_file():
        readme_text = _read(readme_path)
        for marker in README_FORBIDDEN_MARKERS:
            if marker in readme_text:
                issues.append(f"stale {README_PATH.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    _write(root / CATALOG_PATH, "\n".join(CATALOG_MARKERS) + "\n")
    _write(root / OWNERSHIP_MAP_PATH, "\n".join(OWNERSHIP_MAP_MARKERS) + "\n")
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    _write(root / MANIFEST_PATH, "\n".join(MANIFEST_MARKERS) + "\n")
    _write(root / VALIDATOR_PATH, "\n".join(VALIDATOR_MARKERS) + "\n")


def _expect_issue(root: Path, expected: str, message: str) -> int:
    issues = validate_repo(root)
    if expected not in issues:
        print("PHASE9_CATALOG_PACKET_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_catalog_packet_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE9_CATALOG_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        required_cases = (
            (
                CATALOG_PATH,
                'PHASE9_CATALOG_LANE = "P9-L11"',
                'missing scripts/zigux/phase9_catalog.py marker: PHASE9_CATALOG_LANE = "P9-L11"',
                "expected missing catalog lane marker was not reported",
            ),
            (
                OWNERSHIP_MAP_PATH,
                "PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
                "missing Documentation/zigux/phase9-runtime-pilot-ownership-map.md marker: PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
                "expected missing ownership-map blocked depmod bridge marker was not reported",
            ),
            (
                README_PATH,
                "zigux/tests/runtime_pilot_manifest.json",
                "missing scripts/zigux/README.md marker: zigux/tests/runtime_pilot_manifest.json",
                "expected missing scripts README manifest marker was not reported",
            ),
            (
                MANIFEST_PATH,
                '"blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof"',
                'missing zigux/tests/runtime_pilot_manifest.json marker: "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof"',
                "expected missing manifest blocked-boundary marker was not reported",
            ),
            (
                VALIDATOR_PATH,
                '"python3 scripts/zigux/validate-phase9.py",',
                'missing scripts/zigux/validate-phase9.py marker: "python3 scripts/zigux/validate-phase9.py",',
                "expected missing validator replay marker was not reported",
            ),
        )

        for relative_path, marker, expected, message in required_cases:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            if _expect_issue(root, expected, message) != 0:
                return 1

        _populate_repo(root)
        readme_path = root / README_PATH
        _write(
            readme_path,
            _read(readme_path)
            + "there is still no dedicated shared `validate-phase9.py` rerun path\n",
        )
        expected_stale = (
            "stale scripts/zigux/README.md marker: "
            "there is still no dedicated shared `validate-phase9.py` rerun path"
        )
        if _expect_issue(root, expected_stale, "expected stale README validator denial was not reported") != 0:
            return 1

        _populate_repo(root)
        (root / MANIFEST_PATH).unlink()
        expected_missing = "missing repo file: zigux/tests/runtime_pilot_manifest.json"
        if _expect_issue(root, expected_missing, "expected missing manifest file was not reported") != 0:
            return 1

    print("PHASE9_CATALOG_PACKET_SELF_TEST=pass")
    print("PHASE9_CATALOG_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 9 manifest/catalog/ownership packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 9 delivery packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE9_CATALOG_PACKET=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / CATALOG_PATH}")
    print("PHASE9_CATALOG_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
