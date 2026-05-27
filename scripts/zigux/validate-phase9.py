#!/usr/bin/env python3
"""Validate the bounded shared Phase 9 runtime pilot packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_FILE_PATH = Path(__file__).resolve()
ROOT = _FILE_PATH.parents[2] if len(_FILE_PATH.parents) > 2 else _FILE_PATH.parent

LANE_NOTE_PATH = Path("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md")
OWNERSHIP_MAP_PATH = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
MODULE_METADATA_SURVEY_PATH = Path("Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md")
CATALOG_PATH = Path("scripts/zigux/phase9_catalog.py")
CATALOG_SELFTEST_PATH = Path("scripts/zigux/check-phase9-catalog-selftest.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase9.py")
MANIFEST_PATH = Path("zigux/tests/runtime_pilot_manifest.json")
BUILD_PATH = Path("zigux/tests/phase9_build.zig")
RUNTIME_LOADER_PATH = Path("zigux/kernel/runtime_loader.zig")
RUNTIME_LOADER_CONTRACT_PATH = Path("zigux/kernel/runtime_loader_contract.zig")
RUNTIME_LOADER_BOUNDARY_GUARD_PATH = Path("zigux/kernel/runtime_loader_command_env_boundary_guard.zig")
RUNTIME_LOADER_ALLOCATOR_FLOW_PATH = Path("zigux/tests/runtime_loader_allocator_init_flow.zig")

CHECKERS = (
    Path("scripts/zigux/check-phase9-runtime-loader-shared-packet.py"),
    Path("scripts/zigux/check-phase9-atomic64-runtime-packet.py"),
    Path("scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"),
    Path("scripts/zigux/check-phase9-freeze-map-study-boundaries.py"),
    Path("scripts/zigux/check-phase9-trace-events-runtime-packet.py"),
    Path("scripts/zigux/check-phase9-trace-events-direct-summary.py"),
    Path("scripts/zigux/check-phase9-trace-events-summary-preservation.py"),
)

REQUIRED_FILES = (
    LANE_NOTE_PATH,
    OWNERSHIP_MAP_PATH,
    MODULE_METADATA_SURVEY_PATH,
    CATALOG_PATH,
    CATALOG_SELFTEST_PATH,
    VALIDATOR_PATH,
    MANIFEST_PATH,
    BUILD_PATH,
    RUNTIME_LOADER_PATH,
    RUNTIME_LOADER_CONTRACT_PATH,
    RUNTIME_LOADER_BOUNDARY_GUARD_PATH,
    RUNTIME_LOADER_ALLOCATOR_FLOW_PATH,
    *CHECKERS,
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
    "zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig",
    "zig build phase9-first-loadable-runtime-module-parity-behavior-tests --build-file zigux/tests/phase9_build.zig",
)

EXPECTED_GAPS = [
    "blocked module-metadata, depmod bridge, and install-root publication vocabulary remains historical rather than direct shipped proof",
]

EXPECTED_NEXT_SAFE_STEP = (
    "tighten one shared reminder surface at a time where current master still undercounts "
    "the blocked module-metadata and depmod bridge boundary before widening into runtime behavior, "
    "build wiring, or install-root claims"
)

REQUIRED_OWNERSHIP_MARKERS = (
    "PHASE9_RUNTIME_PILOT_MANIFEST=zigux/tests/runtime_pilot_manifest.json",
    "PHASE9_RUNTIME_PILOT_CATALOG=scripts/zigux/phase9_catalog.py",
    "PHASE9_RUNTIME_PILOT_CATALOG_SELFTEST=scripts/zigux/check-phase9-catalog-selftest.py",
    "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts/zigux/validate-phase9.py",
    "PHASE9_RUNTIME_PILOT_BLOCKED_DEPMOD_BRIDGE_SURVEY=Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
)


class ValidationError(RuntimeError):
    pass


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(_read(path))


def _run_python(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def _run_checker(root: Path, checker_path: Path, self_test: bool) -> None:
    args = [str(root / checker_path)]
    if self_test:
        args.append("--self-test")
    result = _run_python(root, args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        suffix = " self-test" if self_test else ""
        raise ValidationError(f"{checker_path.as_posix()}{suffix} failed: {detail}")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    manifest = _read_json(root / MANIFEST_PATH)
    if manifest.get("phase") != "Phase 9":
        raise ValidationError("phase9 manifest phase drift")
    if manifest.get("lane_key") != "P9-L11":
        raise ValidationError("phase9 manifest lane drift")
    if manifest.get("ownership_map_path") != OWNERSHIP_MAP_PATH.as_posix():
        raise ValidationError("phase9 manifest ownership-map drift")
    if manifest.get("packet_files") != list(EXPECTED_PACKET_FILES):
        raise ValidationError("phase9 manifest packet-files drift")
    if manifest.get("replay_routes") != list(EXPECTED_REPLAY_ROUTES):
        raise ValidationError("phase9 manifest replay-routes drift")
    if manifest.get("repo_reality_gaps") != EXPECTED_GAPS:
        raise ValidationError("phase9 manifest repo-reality-gaps drift")
    if manifest.get("next_safe_step") != EXPECTED_NEXT_SAFE_STEP:
        raise ValidationError("phase9 manifest next-safe-step drift")

    ownership_map = _read(root / OWNERSHIP_MAP_PATH)
    for marker in REQUIRED_OWNERSHIP_MARKERS:
        if marker not in ownership_map:
            raise ValidationError(f"phase9 ownership-map marker missing: {marker}")
    if MODULE_METADATA_SURVEY_PATH.as_posix() not in ownership_map:
        raise ValidationError("phase9 ownership-map module-metadata survey drift")

    catalog_result = _run_python(root, [str(root / CATALOG_PATH), "--pretty"])
    if catalog_result.returncode != 0:
        detail = catalog_result.stderr.strip() or catalog_result.stdout.strip() or f"exit {catalog_result.returncode}"
        raise ValidationError(f"{CATALOG_PATH.as_posix()} failed: {detail}")

    _run_checker(root, CATALOG_SELFTEST_PATH, True)
    _run_checker(root, CATALOG_SELFTEST_PATH, False)

    for checker in CHECKERS:
        _run_checker(root, checker, True)
        _run_checker(root, checker, False)


def _populate_fixture(root: Path) -> None:
    for path in REQUIRED_FILES:
        _write(root / path, f"{path.as_posix()}\n")

    _write(
        root / OWNERSHIP_MAP_PATH,
        "\n".join(
            REQUIRED_OWNERSHIP_MARKERS
            + (
                MODULE_METADATA_SURVEY_PATH.as_posix(),
                "## Shared Owner Packet",
            )
        )
        + "\n",
    )
    _write(root / CATALOG_PATH, "\n".join(("from __future__ import annotations", "print('{}')")) + "\n")
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "phase": "Phase 9",
                "lane_key": "P9-L11",
                "ownership_map_path": OWNERSHIP_MAP_PATH.as_posix(),
                "packet_files": list(EXPECTED_PACKET_FILES),
                "replay_routes": list(EXPECTED_REPLAY_ROUTES),
                "repo_reality_gaps": EXPECTED_GAPS,
                "next_safe_step": EXPECTED_NEXT_SAFE_STEP,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / CATALOG_PATH,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--pretty', action='store_true')",
                "parser.add_argument('--self-test', action='store_true')",
                "args = parser.parse_args()",
                "print('{}')",
            )
        )
        + "\n",
    )
    _write(
        root / CATALOG_SELFTEST_PATH,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "args = parser.parse_args()",
                "print('PHASE9_CATALOG_PACKET_SELF_TEST=pass' if args.self_test else 'PHASE9_CATALOG_PACKET=pass')",
            )
        )
        + "\n",
    )
    _write(root / VALIDATOR_PATH, _read(Path(__file__)))
    for checker in CHECKERS:
        token = checker.stem.replace("-", "_").upper()
        _write(
            root / checker,
            "\n".join(
                (
                    "#!/usr/bin/env python3",
                    "from __future__ import annotations",
                    "import argparse",
                    "parser = argparse.ArgumentParser()",
                    "parser.add_argument('--self-test', action='store_true')",
                    "args = parser.parse_args()",
                    f"print('{token}_SELF_TEST=pass' if args.self_test else '{token}=pass')",
                )
            )
            + "\n",
        )


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if text == updated:
        raise AssertionError(f"missing test marker: {old}")
    path.write_text(updated, encoding="utf-8")


def _expect_failure(root: Path) -> None:
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected failure")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_validate_") as tmpdir:
        root = Path(tmpdir)
        _populate_fixture(root)
        validate(root)
        case_count += 1

        (root / CHECKERS[0]).unlink()
        _expect_failure(root)
        case_count += 1

        _populate_fixture(root)
        manifest = _read_json(root / MANIFEST_PATH)
        manifest["packet_files"] = manifest["packet_files"][:-1]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _expect_failure(root)
        case_count += 1

        _populate_fixture(root)
        manifest = _read_json(root / MANIFEST_PATH)
        manifest["replay_routes"] = manifest["replay_routes"][:-1]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _expect_failure(root)
        case_count += 1

        _populate_fixture(root)
        manifest = _read_json(root / MANIFEST_PATH)
        manifest["repo_reality_gaps"] = [
            "no dedicated shared validate-phase9.py rerun path on current master",
            *EXPECTED_GAPS,
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _expect_failure(root)
        case_count += 1

        _populate_fixture(root)
        _replace_once(
            root / OWNERSHIP_MAP_PATH,
            MODULE_METADATA_SURVEY_PATH.as_posix(),
            "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        )
        _expect_failure(root)
        case_count += 1

        _populate_fixture(root)
        _replace_once(
            root / OWNERSHIP_MAP_PATH,
            "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts/zigux/validate-phase9.py",
            "PHASE9_RUNTIME_PILOT_VALIDATOR=scripts/zigux/phase9_catalog.py",
        )
        _expect_failure(root)
        case_count += 1

    print("PHASE9_VALIDATE_SELF_TEST=pass")
    print(f"PHASE9_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE9_VALIDATE=fail: {exc}")
        return 1
    print("PHASE9_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
