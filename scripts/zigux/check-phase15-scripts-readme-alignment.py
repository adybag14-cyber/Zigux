#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

README_REL = "scripts/zigux/README.md"
READINESS_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"
BUILD_REL = "zigux/tests/phase15_build.zig"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

README_MARKERS = (
    "## Phase 15",
    "Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision",
    f"`{VALIDATOR_REL}`",
    f"`{BUILD_REL}`",
    "`scripts/zigux/validate-phase15.py` is directly readable on current `master`, while repeated authenticated reads still return missing for `zigux/tests/phase15_build.zig`, so keep the dedicated validator explicit as shipped scripts-root evidence and keep the broader shared-build companion framed as a repo-reality gap",
    "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths",
    "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route, so keep that workflow surface framed as shared-summary gap vocabulary rather than shipped Phase 15 replay evidence",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

READINESS_MARKERS = (
    "the dedicated validator now exists as a directly readable maintenance gate",
    f"`{VALIDATOR_REL}`",
    f"`{BUILD_REL}`",
    "dedicated `phase15*` wrapper routes",
)

STALE_README_MARKER = (
    "repeated authenticated reads on current `master` still return missing for "
    "`scripts/zigux/validate-phase15.py` and `zigux/tests/phase15_build.zig`, so keep "
    "those broader validator-first and build companions framed as repo-reality gaps "
    "instead of shipped scripts-root evidence"
)

WORKFLOW_STALE_MARKERS = (
    "Phase 15 validate",
    "Phase 15 test",
    "Run current Phase 15",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(text: str, markers: tuple[str, ...], prefix: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (README_REL, READINESS_REL, VALIDATOR_REL, MAKEFILE_REL, WORKFLOW_REL):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    readme = _read(root / README_REL)
    readiness = _read(root / READINESS_REL)
    makefile = _read(root / MAKEFILE_REL)
    workflow = _read(root / WORKFLOW_REL)

    _require_markers(readme, README_MARKERS, "readme", failures)
    _require_markers(readiness, READINESS_MARKERS, "readiness", failures)

    if STALE_README_MARKER in readme:
        failures.append("readme:stale_missing_validator_claim")

    if (root / BUILD_REL).exists():
        failures.append(f"unexpected_materialized_path:{BUILD_REL}")

    for marker in ("phase15-validate:", "phase15-test:", "phase15:", ".PHONY: phase15"):
        if marker in makefile:
            failures.append(f"makefile:unexpected_phase15_route:{marker}")

    for marker in WORKFLOW_STALE_MARKERS:
        if marker in workflow:
            failures.append(f"workflow:unexpected_phase15_route:{marker}")

    return failures


def _passing_readme() -> str:
    return f"""# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 15

- Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `scripts/zigux/validate-phase15.py` is directly readable on current `master`, while repeated authenticated reads still return missing for `zigux/tests/phase15_build.zig`, so keep the dedicated validator explicit as shipped scripts-root evidence and keep the broader shared-build companion framed as a repo-reality gap
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names as blocked route vocabulary rather than directly readable replay paths
- `.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route, so keep that workflow surface framed as shared-summary gap vocabulary rather than shipped Phase 15 replay evidence
- no Architecture Council approval is currently recorded for a freeze-map status change
"""


def _stale_readme() -> str:
    return _passing_readme().replace(
        "`scripts/zigux/validate-phase15.py` is directly readable on current `master`, while repeated authenticated reads still return missing for `zigux/tests/phase15_build.zig`, so keep the dedicated validator explicit as shipped scripts-root evidence and keep the broader shared-build companion framed as a repo-reality gap",
        STALE_README_MARKER,
        1,
    )


def _readiness_note() -> str:
    return f"""# Phase 15 Readiness Gate Survey

- the dedicated validator now exists as a directly readable maintenance gate
- `{VALIDATOR_REL}`
- `{BUILD_REL}`
- dedicated `phase15*` wrapper routes
"""


def write_sample_root(root: Path, stale_readme: bool = False, materialize_build: bool = False) -> None:
    _write(root / README_REL, _stale_readme() if stale_readme else _passing_readme())
    _write(root / READINESS_REL, _readiness_note())
    _write(root / VALIDATOR_REL, "#!/usr/bin/env python3\n")
    _write(root / MAKEFILE_REL, "phase2-toolchain:\n\t@true\n")
    _write(root / WORKFLOW_REL, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-scripts-readme-alignment.py\n")
    if materialize_build:
        _write(root / BUILD_REL, 'const std = @import("std");\n')


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_scripts_readme_alignment_") as tmpdir:
        root = Path(tmpdir)

        baseline = root / "baseline"
        write_sample_root(baseline)
        failures = validate(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        stale = root / "stale"
        write_sample_root(stale, stale_readme=True)
        failures = validate(stale)
        if failures != ["readme:missing:`scripts/zigux/validate-phase15.py` is directly readable on current `master`, while repeated authenticated reads still return missing for `zigux/tests/phase15_build.zig`, so keep the dedicated validator explicit as shipped scripts-root evidence and keep the broader shared-build companion framed as a repo-reality gap", "readme:stale_missing_validator_claim"]:
            raise AssertionError(f"unexpected stale fixture failure: {failures}")

        missing_validator = root / "missing_validator"
        write_sample_root(missing_validator)
        (missing_validator / VALIDATOR_REL).unlink()
        failures = validate(missing_validator)
        if failures != [f"missing_file:{VALIDATOR_REL}"]:
            raise AssertionError(f"unexpected missing-validator failure: {failures}")

        materialized_build = root / "materialized_build"
        write_sample_root(materialized_build, materialize_build=True)
        failures = validate(materialized_build)
        if failures != [f"unexpected_materialized_path:{BUILD_REL}"]:
            raise AssertionError(f"unexpected materialized-build failure: {failures}")

        workflow_route = root / "workflow_route"
        write_sample_root(workflow_route)
        _write(
            workflow_route / WORKFLOW_REL,
            _read(workflow_route / WORKFLOW_REL) + "      - name: Run current Phase 15 validate route\n",
        )
        failures = validate(workflow_route)
        if failures != [
            "workflow:unexpected_phase15_route:Phase 15 validate",
            "workflow:unexpected_phase15_route:Run current Phase 15",
        ]:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")

    print("PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 scripts-root reminder matches the live validator-first packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--write-stale-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0
    if args.write_stale_root is not None:
        write_sample_root(args.write_stale_root, stale_readme=True)
        return 0

    failures = validate(args.root)
    if failures:
        print("PHASE15_SCRIPTS_README_ALIGNMENT=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
