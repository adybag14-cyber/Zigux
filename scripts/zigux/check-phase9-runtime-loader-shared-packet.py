#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
CATALOG = Path("scripts/zigux/phase9_catalog.py")
CATALOG_SELFTEST = Path("scripts/zigux/check-phase9-catalog-selftest.py")
ATOMIC64_PACKET = Path("scripts/zigux/check-phase9-atomic64-runtime-packet.py")
REVIEW_BOUNDARIES = Path("scripts/zigux/check-phase9-review-checklist-phase-boundaries.py")
FREEZE_BOUNDARIES = Path("scripts/zigux/check-phase9-freeze-map-study-boundaries.py")
BUILD_ONLY_SURFACE = Path("scripts/zigux/check-phase9-build-only-surface.py")
TRACE_EVENTS_PACKET = Path("scripts/zigux/check-phase9-trace-events-runtime-packet.py")
TRACE_EVENTS_DIRECT = Path("scripts/zigux/check-phase9-trace-events-direct-summary.py")
TRACE_EVENTS_SUMMARY = Path("scripts/zigux/check-phase9-trace-events-summary-preservation.py")
VALIDATOR = Path("scripts/zigux/check-phase9-runtime-loader-shared-packet.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
README = Path("scripts/zigux/README.md")
MANIFEST = Path("zigux/tests/runtime_pilot_manifest.json")
OWNERSHIP_MAP = Path("Documentation/zigux/phase9-runtime-pilot-ownership-map.md")
LANE_NOTE = Path("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md")
DOCS_README = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
PHASE9_BUILD = Path("zigux/tests/phase9_build.zig")
RUNTIME_LOADER = Path("zigux/kernel/runtime_loader.zig")
RUNTIME_LOADER_CONTRACT = Path("zigux/kernel/runtime_loader_contract.zig")
RUNTIME_LOADER_BOUNDARY_GUARD = Path("zigux/kernel/runtime_loader_command_env_boundary_guard.zig")
RUNTIME_LOADER_ALLOCATOR_INIT_FLOW = Path("zigux/tests/runtime_loader_allocator_init_flow.zig")
RUNTIME_BITMAP_LOADER = Path("samples/zigux/runtime_bitmap_loader.zig")
RUNTIME_KRETPROBE_LOADER = Path("samples/zigux/runtime_kretprobe_loader.zig")

REQUIRED_FILES = (
    DOCS_README,
    REVIEW_CHECKLIST,
    LANE_NOTE,
    OWNERSHIP_MAP,
    README,
    WORKFLOW,
    CATALOG,
    CATALOG_SELFTEST,
    ATOMIC64_PACKET,
    REVIEW_BOUNDARIES,
    FREEZE_BOUNDARIES,
    BUILD_ONLY_SURFACE,
    TRACE_EVENTS_PACKET,
    TRACE_EVENTS_DIRECT,
    TRACE_EVENTS_SUMMARY,
    VALIDATOR,
    MANIFEST,
    PHASE9_BUILD,
    RUNTIME_LOADER,
    RUNTIME_LOADER_CONTRACT,
    RUNTIME_LOADER_BOUNDARY_GUARD,
    RUNTIME_LOADER_ALLOCATOR_INIT_FLOW,
    RUNTIME_BITMAP_LOADER,
    RUNTIME_KRETPROBE_LOADER,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    README: (
        "scripts/zigux/check-phase9-runtime-loader-shared-packet.py",
        "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py",
        "the current scripts-root runtime-pilot reminder now keeps the dedicated shared `check-phase9-runtime-loader-shared-packet.py` rerun path explicit for this loader packet on current `master`",
    ),
    WORKFLOW: (
        "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py --self-test",
        "python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py",
        "Run current Phase 9 shared loader command-environment boundary guard tests",
        "Run current Phase 9 shared loader allocator-init-flow packet",
    ),
    CATALOG: (
        '"scripts/zigux/check-phase9-runtime-loader-shared-packet.py"',
        '"python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py"',
        '"blocked publication and install-root vocabulary remains historical rather than direct shipped proof"',
    ),
    MANIFEST: (
        '"scripts/zigux/check-phase9-runtime-loader-shared-packet.py"',
        '"python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py --self-test"',
        '"python3 scripts/zigux/check-phase9-runtime-loader-shared-packet.py"',
        '"blocked publication and install-root vocabulary remains historical rather than direct shipped proof"',
    ),
    PHASE9_BUILD: (
        "phase9-runtime-loader-shared-tests",
        "phase9-runtime-loader-command-env-boundary-guard-tests",
        "phase9-runtime-bitmap-tests",
        "phase9-runtime-kretprobe-tests",
    ),
    RUNTIME_LOADER: (
        "pub fn prepareRequest",
        "pub fn releaseWithoutSubstrate",
        "keepsAllocatorInitFlowConsistent",
    ),
    RUNTIME_LOADER_CONTRACT: (
        "pub fn allocatorRuntimeInitPolicyFor",
        "pub fn keepsAllocatorRuntimeInitPolicyConsistent",
        "pub const LoadPlan = struct {",
    ),
    RUNTIME_LOADER_BOUNDARY_GUARD: (
        "shared runtime loader surface keeps the bounded request contract explicit",
        "shared runtime loader surface rejects argv and environment control bleed-through",
    ),
    RUNTIME_LOADER_ALLOCATOR_INIT_FLOW: (
        "shared runtime loader keeps allocator handoff and anchor metadata from drifting before handoff",
        "shared runtime loader keeps waiting module-name and allocator handoff from drifting before release",
    ),
    RUNTIME_BITMAP_LOADER: (
        "runtime bitmap loader keeps loader-facing bitmap payload explicit",
        "runtime bitmap loader keeps loaded cross-word summary stable through selftest and exit",
    ),
    RUNTIME_KRETPROBE_LOADER: (
        "runtime kretprobe loader keeps initialized-stage shared contract plans explicit",
        "runtime kretprobe loader keeps selftest-complete shared requests blocked by the current loader family contract",
    ),
}

CHECKERS = (
    CATALOG_SELFTEST,
    ATOMIC64_PACKET,
    REVIEW_BOUNDARIES,
    FREEZE_BOUNDARIES,
    BUILD_ONLY_SURFACE,
    TRACE_EVENTS_PACKET,
    TRACE_EVENTS_DIRECT,
    TRACE_EVENTS_SUMMARY,
)


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]
    checker_failures: dict[str, list[str]]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _passing_checker(token: str) -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            f'print("{token}=pass")',
            "",
        )
    )


def _failing_checker(token: str, reason: str) -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            f'print("{token}=fail")',
            f"print({reason!r})",
            "raise SystemExit(1)",
            "",
        )
    )


def _collect_missing_markers(root: Path) -> list[str]:
    missing_markers: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{relative_path}:{marker}")
    return missing_markers


def _run_checker(root: Path, checker: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / checker)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    return output.splitlines()


def validate_root(root: Path) -> ValidationResult:
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    missing_markers = _collect_missing_markers(root)
    checker_failures: dict[str, list[str]] = {}
    if not missing_files and not missing_markers:
        for checker in CHECKERS:
            output = _run_checker(root, checker)
            if output:
                checker_failures[checker.as_posix()] = output
    return ValidationResult(missing_files, missing_markers, checker_failures)


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers or result.checker_failures:
        print("PHASE9_RUNTIME_LOADER_SHARED_PACKET=fail")
        if result.missing_files:
            print("PHASE9_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE9_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE9_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE9_MISSING_MARKERS_END")
        for checker, lines in result.checker_failures.items():
            print(f"PHASE9_CHECKER_FAILURE_START={checker}")
            for line in lines:
                print(line)
            print(f"PHASE9_CHECKER_FAILURE_END={checker}")
        return 1

    print("PHASE9_RUNTIME_LOADER_SHARED_PACKET=pass")
    print(f"PHASE9_SHARED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    print(f"PHASE9_CHECKER_COUNT={len(CHECKERS)}")
    return 0


def _passing_fixture(root: Path) -> None:
    for path in REQUIRED_FILES:
        if path in CHECKERS:
            continue
        if path in FILE_MARKERS:
            _write(root / path, "\n".join(FILE_MARKERS[path]) + "\n")
        else:
            _write(root / path, f"{path.as_posix()}\n")

    _write(root / CATALOG_SELFTEST, _passing_checker("PHASE9_CATALOG_PACKET"))
    _write(root / ATOMIC64_PACKET, _passing_checker("PHASE9_ATOMIC64_RUNTIME_PACKET"))
    _write(root / REVIEW_BOUNDARIES, _passing_checker("PHASE9_REVIEW_CHECKLIST_BOUNDARIES"))
    _write(root / FREEZE_BOUNDARIES, _passing_checker("PHASE9_FREEZE_MAP_STUDY_BOUNDARIES"))
    _write(root / BUILD_ONLY_SURFACE, _passing_checker("PHASE9_BUILD_ONLY_SURFACE"))
    _write(root / TRACE_EVENTS_PACKET, _passing_checker("PHASE9_TRACE_EVENTS_RUNTIME_PACKET"))
    _write(root / TRACE_EVENTS_DIRECT, _passing_checker("PHASE9_TRACE_EVENTS_DIRECT_SUMMARY"))
    _write(root / TRACE_EVENTS_SUMMARY, _passing_checker("PHASE9_TRACE_EVENTS_SUMMARY_PRESERVATION"))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase9-validate-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers or passing.checker_failures:
            raise AssertionError("expected passing fixture to validate")
        case_count += 1

        _write(
            root / CATALOG_SELFTEST,
            _failing_checker(
                "PHASE9_CATALOG_PACKET",
                'missing-marker:scripts/zigux/phase9_catalog.py:"scripts/zigux/check-phase9-runtime-loader-shared-packet.py"',
            ),
        )
        failing_catalog = validate_root(root)
        catalog_output = failing_catalog.checker_failures.get(CATALOG_SELFTEST.as_posix())
        if (
            catalog_output is None
            or "PHASE9_CATALOG_PACKET=fail" not in catalog_output
        ):
            raise AssertionError("expected failing catalog checker output to be reported")
        case_count += 1
        _write(root / CATALOG_SELFTEST, _passing_checker("PHASE9_CATALOG_PACKET"))

        _write(
            root / BUILD_ONLY_SURFACE,
            _failing_checker(
                "PHASE9_BUILD_ONLY_SURFACE",
                "missing-marker:zigux/tests/phase9_build.zig:phase9-runtime-loader-shared-tests",
            ),
        )
        failing_build_only = validate_root(root)
        build_only_output = failing_build_only.checker_failures.get(BUILD_ONLY_SURFACE.as_posix())
        if (
            build_only_output is None
            or "PHASE9_BUILD_ONLY_SURFACE=fail" not in build_only_output
            or "missing-marker:zigux/tests/phase9_build.zig:phase9-runtime-loader-shared-tests" not in build_only_output
        ):
            raise AssertionError("expected failing build-only checker output to be reported")
        case_count += 1
        _write(root / BUILD_ONLY_SURFACE, _passing_checker("PHASE9_BUILD_ONLY_SURFACE"))

        for relative_path, markers in FILE_MARKERS.items():
            path = root / relative_path
            if not path.exists():
                continue
            original = _read(path)
            for marker in markers:
                path.write_text(original.replace(marker, ""), encoding="utf-8")
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                path.write_text(original, encoding="utf-8")
                case_count += 1

        for relative_path in REQUIRED_FILES:
            if relative_path in CHECKERS:
                continue
            path = root / relative_path
            original = _read(path)
            path.unlink()
            result = validate_root(root)
            expected = relative_path.as_posix()
            if expected not in result.missing_files:
                raise AssertionError(f"expected missing file to be reported: {expected}")
            _write(path, original)
            case_count += 1

    print("PHASE9_RUNTIME_LOADER_SHARED_PACKET_SELF_TEST=pass")
    print(f"PHASE9_RUNTIME_LOADER_SHARED_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
