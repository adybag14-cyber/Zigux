#!/usr/bin/env python3
"""Fail-close the current Phase 9 manifest/catalog/ownership packet."""

from __future__ import annotations

import argparse
import ast
import json
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

EXPECTED_PACKET_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-pilot-ownership-map.md",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/phase9_catalog.py",
    "scripts/zigux/check-phase9-catalog-selftest.py",
    "scripts/zigux/validate-phase9.py",
    "scripts/zigux/check-phase9-runtime-loader-shared-packet.py",
    "scripts/zigux/check-phase9-atomic64-runtime-packet.py",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "scripts/zigux/check-phase9-trace-events-direct-summary.py",
    "scripts/zigux/check-phase9-trace-events-summary-preservation.py",
    "scripts/zigux/check-phase9-kretprobe-runtime-packet.py",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_pilot_manifest.json",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_module.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_trace_events_module.zig",
    "zigux/tests/runtime_kretprobe_survey.zig",
    "zigux/tests/runtime_kretprobe_module.zig",
    "zigux/tests/runtime_first_loadable_parity_behavior.zig",
    "samples/zigux/runtime_atomic64.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig",
    "samples/zigux/runtime_kretprobe_registration_reentry_gate.zig",
    "samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig",
)

EXPECTED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase9-catalog-selftest.py --self-test",
    "python3 scripts/zigux/check-phase9-catalog-selftest.py",
    "python3 scripts/zigux/phase9_catalog.py --pretty",
    "python3 scripts/zigux/validate-phase9.py --self-test",
    "python3 scripts/zigux/validate-phase9.py",
    "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py",
    "python3 scripts/zigux/check-phase9-atomic64-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-atomic64-runtime-packet.py",
    "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test",
    "python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test",
    "python3 scripts/zigux/check-phase9-kretprobe-runtime-packet.py --self-test",
    "python3 scripts/zigux/check-phase9-kretprobe-runtime-packet.py",
    "zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig",
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


def _load_json(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        return json.loads(_read(path)), []
    except FileNotFoundError:
        return None, [f"missing repo file: {path.as_posix()}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON in {path.as_posix()}: {exc}"]


def _extract_string_sequence(
    path: Path,
    constant_name: str,
) -> tuple[tuple[str, ...] | None, list[str]]:
    try:
        tree = ast.parse(_read(path), filename=path.as_posix())
    except FileNotFoundError:
        return None, [f"missing repo file: {path.as_posix()}"]
    except SyntaxError as exc:
        return None, [f"invalid Python in {path.as_posix()}: {exc.msg}"]

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == constant_name:
                try:
                    value = ast.literal_eval(node.value)
                except Exception:
                    return None, [f"non-literal {path.as_posix()} constant: {constant_name}"]
                if not isinstance(value, (tuple, list)):
                    return None, [f"non-sequence {path.as_posix()} constant: {constant_name}"]
                if not all(isinstance(item, str) for item in value):
                    return None, [f"non-string {path.as_posix()} constant member: {constant_name}"]
                return tuple(value), []
    return None, [f"missing {path.as_posix()} constant: {constant_name}"]


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

    manifest, manifest_issues = _load_json(repo_root / MANIFEST_PATH)
    issues.extend(manifest_issues)
    if manifest is not None:
        packet_files = manifest.get("packet_files")
        if not isinstance(packet_files, list) or not all(isinstance(value, str) for value in packet_files):
            issues.append("runtime_pilot_manifest.json packet_files is not a string list")
        elif tuple(packet_files) != EXPECTED_PACKET_FILES:
            issues.append(
                "runtime_pilot_manifest.json packet_files drift from shared Phase 9 catalog packet expectations"
            )

        replay_routes = manifest.get("replay_routes")
        if not isinstance(replay_routes, list) or not all(
            isinstance(value, str) for value in replay_routes
        ):
            issues.append("runtime_pilot_manifest.json replay_routes is not a string list")
        elif tuple(replay_routes) != EXPECTED_REPLAY_ROUTES:
            issues.append(
                "runtime_pilot_manifest.json replay_routes drift from shared Phase 9 catalog packet expectations"
            )

    catalog_packet_files, extract_issues = _extract_string_sequence(
        repo_root / CATALOG_PATH,
        "EXPECTED_PACKET_FILES",
    )
    issues.extend(extract_issues)
    if catalog_packet_files is not None and catalog_packet_files != EXPECTED_PACKET_FILES:
        issues.append("phase9 catalog EXPECTED_PACKET_FILES drift from shared Phase 9 catalog packet expectations")

    catalog_replay_routes, extract_issues = _extract_string_sequence(
        repo_root / CATALOG_PATH,
        "EXPECTED_REPLAY_ROUTES",
    )
    issues.extend(extract_issues)
    if catalog_replay_routes is not None and catalog_replay_routes != EXPECTED_REPLAY_ROUTES:
        issues.append("phase9 catalog EXPECTED_REPLAY_ROUTES drift from shared Phase 9 catalog packet expectations")

    validator_packet_files, extract_issues = _extract_string_sequence(
        repo_root / VALIDATOR_PATH,
        "EXPECTED_PACKET_FILES",
    )
    issues.extend(extract_issues)
    if validator_packet_files is not None and validator_packet_files != EXPECTED_PACKET_FILES:
        issues.append(
            "phase9 validator EXPECTED_PACKET_FILES drift from shared Phase 9 catalog packet expectations"
        )

    validator_replay_routes, extract_issues = _extract_string_sequence(
        repo_root / VALIDATOR_PATH,
        "EXPECTED_REPLAY_ROUTES",
    )
    issues.extend(extract_issues)
    if validator_replay_routes is not None and validator_replay_routes != EXPECTED_REPLAY_ROUTES:
        issues.append(
            "phase9 validator EXPECTED_REPLAY_ROUTES drift from shared Phase 9 catalog packet expectations"
        )

    return issues


def _catalog_script_text(packet_files: tuple[str, ...], replay_routes: tuple[str, ...]) -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

PHASE9_CATALOG_PHASE = "Phase 9"
PHASE9_CATALOG_LANE = "P9-L11"
MANIFEST_PATH = Path("zigux/tests/runtime_pilot_manifest.json")
OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
EXPECTED_PACKET_FILES = (
{packet_files}
)
EXPECTED_REPLAY_ROUTES = (
{replay_routes}
)
EXPECTED_GAPS = (
    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",
)

parser = argparse.ArgumentParser()
parser.add_argument("--self-test", action="store_true")
parser.add_argument("--pretty", action="store_true")
args = parser.parse_args()
if args.self_test:
    print("PHASE9_CATALOG_SELF_TEST=pass")
else:
    print("PHASE9_CATALOG=pass")
""".format(
        packet_files="\n".join(f'    "{value}",' for value in packet_files),
        replay_routes="\n".join(f'    "{value}",' for value in replay_routes),
    )


def _validator_script_text(packet_files: tuple[str, ...], replay_routes: tuple[str, ...]) -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse

EXPECTED_PACKET_FILES = (
{packet_files}
)
EXPECTED_REPLAY_ROUTES = (
{replay_routes}
)
EXPECTED_GAPS = (
    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",
)

parser = argparse.ArgumentParser()
parser.add_argument("--self-test", action="store_true")
args = parser.parse_args()
if args.self_test:
    print("PHASE9_VALIDATE_SELF_TEST=pass")
else:
    print("PHASE9_VALIDATE=pass")
""".format(
        packet_files="\n".join(f'    "{value}",' for value in packet_files),
        replay_routes="\n".join(f'    "{value}",' for value in replay_routes),
    )


def _populate_repo(root: Path) -> None:
    _write(root / CATALOG_PATH, _catalog_script_text(EXPECTED_PACKET_FILES, EXPECTED_REPLAY_ROUTES))
    _write(root / OWNERSHIP_MAP_PATH, "\n".join(OWNERSHIP_MAP_MARKERS) + "\n")
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "phase": "Phase 9",
                "lane_key": "P9-L11",
                "ownership_map_path": OWNERSHIP_MAP_PATH.as_posix(),
                "packet_files": list(EXPECTED_PACKET_FILES),
                "replay_routes": list(EXPECTED_REPLAY_ROUTES),
                "repo_reality_gaps": [
                    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof"
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(root / VALIDATOR_PATH, _validator_script_text(EXPECTED_PACKET_FILES, EXPECTED_REPLAY_ROUTES))


def _expect_issue(root: Path, expected: str, message: str) -> int:
    issues = validate_repo(root)
    if expected not in issues:
        print("PHASE9_CATALOG_PACKET_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _remove_string_once(path: Path, marker: str) -> None:
    text = _read(path)
    updated = text.replace(marker, "", 1)
    if text == updated:
        raise ValueError(f"marker not found for mutation: {marker}")
    _write(path, updated)


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
            _remove_string_once(root / relative_path, marker)
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

        _populate_repo(root)
        _write(
            root / CATALOG_PATH,
            _catalog_script_text(EXPECTED_PACKET_FILES[:-1], EXPECTED_REPLAY_ROUTES),
        )
        expected_catalog_packet_drift = (
            "phase9 catalog EXPECTED_PACKET_FILES drift from shared Phase 9 catalog packet expectations"
        )
        if _expect_issue(
            root,
            expected_catalog_packet_drift,
            "expected catalog packet drift was not reported",
        ) != 0:
            return 1

        _populate_repo(root)
        _write(
            root / VALIDATOR_PATH,
            _validator_script_text(EXPECTED_PACKET_FILES, EXPECTED_REPLAY_ROUTES[:-1]),
        )
        expected_validator_route_drift = (
            "phase9 validator EXPECTED_REPLAY_ROUTES drift from shared Phase 9 catalog packet expectations"
        )
        if _expect_issue(
            root,
            expected_validator_route_drift,
            "expected validator replay-route drift was not reported",
        ) != 0:
            return 1

    print("PHASE9_CATALOG_PACKET_SELF_TEST=pass")
    print("PHASE9_CATALOG_PACKET_SELF_TEST_CASE_COUNT=9")
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
