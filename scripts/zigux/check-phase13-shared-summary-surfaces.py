#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FILES = {
    "docs_root_readme": "Documentation/zigux/README.md",
    "workflow_guide": "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "contributor_surface_sync": "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "lane_note": "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "release_matrix": "Documentation/zigux/phase13-release-coordination-matrix.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts_readme": "scripts/zigux/README.md",
    "tests_readme": "zigux/tests/README.md",
    "makefile": "zigux/Makefile",
}

CHECKER_MARKER = "`scripts/zigux/check-phase13-shared-summary-surfaces.py`"
VALIDATE_ROUTE = "`make -C zigux phase13-validate`"
BLOCKED_ROUTE = "blocked convenience route `make -C zigux phase13`"
PHASE13_BUILD_GAP = "`zigux/tests/phase13_build.zig`"
NOTIFIER_CHAIN_VIEW = "`zigux/helpers/notifier_chain_view.zig`"
HVC_HEADER = "`drivers/tty/hvc/hvc_console.h`"
DEVRES_BOUNDARY = "`zigux/tests/phase13_devres_boundary_evidence.zig`"
LANDLOCK_SYSCALLS_REVIEWABILITY = "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`"

REQUIRED_MARKERS = {
    "docs_root_readme": [
        "Phase 13 notes - `Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        NOTIFIER_CHAIN_VIEW,
        HVC_HEADER,
        "stable `make -C zigux phase13-validate`",
        BLOCKED_ROUTE,
        "`Documentation/zigux/phase13-libfs-slice.md`",
        PHASE13_BUILD_GAP,
    ],
    "workflow_guide": [
        "Use this guide when a change touches the active Phase 13 shared-helper packet",
        CHECKER_MARKER,
        "Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle.",
        "`make -C zigux phase13` still exists in `zigux/Makefile`, but treat it as blocked convenience wiring until `zigux/tests/phase13_build.zig` lands.",
        "Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header.",
        "Apply the same reread to the broader `zigux/tests/README.md` guide: keep it in scope as a shared contributor-facing surface, and current `master` now materializes a dedicated Phase 13 packet summary there.",
    ],
    "review_checklist": [
        "if the change touches the shared Phase 13 contributor packet",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "`Documentation/zigux/phase13-release-notes-survey.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "`zigux/tests/README.md`",
        CHECKER_MARKER,
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/Makefile`",
        VALIDATE_ROUTE,
        "`make -C zigux phase13`",
        PHASE13_BUILD_GAP,
        NOTIFIER_CHAIN_VIEW,
        HVC_HEADER,
    ],
    "contributor_surface_sync": [
        "# Phase 10, 11, and 13 Contributor Surface Sync",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        CHECKER_MARKER,
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        VALIDATE_ROUTE,
        BLOCKED_ROUTE,
    ],
    "lane_note": [
        "# Phase 13 Shared Helper Lane Sequencing",
        "Treat `make -C zigux phase13-validate` as the stable shared replay handle.",
        "`P13-Y08` for shared contributor reminders",
        "adjacent notifier evidence owns",
    ],
    "release_matrix": [
        "# Phase 13 Release Coordination Matrix",
        "- shared-summary checker: `scripts/zigux/check-phase13-shared-summary-surfaces.py`",
        "stable shared replay handle: `zigux/Makefile` and `make -C zigux phase13-validate`",
        "- blocked convenience route: `make -C zigux phase13`",
        "The older scripts-root Landlock direct-evidence undercount and the later docs-root plus tests-root command-posture drift are no longer present on current `master`: `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` already keep `make -C zigux phase13` framed as blocked convenience wiring beside the stable `make -C zigux phase13-validate` handle while `zigux/tests/phase13_build.zig` remains absent.",
    ],
    "tests_companion": [
        "## Phase 13 tests-root packet",
        CHECKER_MARKER,
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        NOTIFIER_CHAIN_VIEW,
        HVC_HEADER,
        VALIDATE_ROUTE,
        BLOCKED_ROUTE,
        "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.",
    ],
    "scripts_readme": [
        "Phase 13 flow - keep the shared Phase 13 contributor packet explicit through the shipped contributor and release-surface notes:",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        DEVRES_BOUNDARY,
        LANDLOCK_SYSCALLS_REVIEWABILITY,
        NOTIFIER_CHAIN_VIEW,
        HVC_HEADER,
        "while the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` stay explicit on current `master`.",
        "direct slice, survey, manifest, build, notifier, and Landlock tests-root companions that current `master` cannot materialize should stay framed as repo-reality gaps",
    ],
    "tests_readme": [
        "Phase 13 review packet",
        CHECKER_MARKER,
        VALIDATE_ROUTE,
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "`Documentation/zigux/phase13-release-notes-survey.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        NOTIFIER_CHAIN_VIEW,
        HVC_HEADER,
        PHASE13_BUILD_GAP,
        "`scripts/zigux/check-phase13-notifier-packet.py`",
        BLOCKED_ROUTE,
    ],
    "makefile": [
        "PHONY += phase13-validate phase13-test phase13",
        "phase13-validate:",
        "scripts/zigux/check-phase13-shared-summary-surfaces.py --self-test",
        "scripts/zigux/check-phase13-shared-summary-surfaces.py",
        "phase13: phase13-validate phase13-test",
    ],
}

FORBIDDEN_MARKERS = {
    "release_matrix": [
        "tests-root command-posture drift is still present",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, REQUIRED_MARKERS[label])
        expect_forbidden_markers_absent(label, text)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    for label, relative_path in FILES.items():
        lines = list(REQUIRED_MARKERS[label])
        write(root / relative_path, "\n".join(lines) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase13_shared_summary_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [
            (label, marker)
            for label, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8")
                .replace(marker + "\n", "", 1)
                .replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            (label, marker)
            for label, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        missing_file_cases = list(FILES.values())
        for idx, relative_path in enumerate(missing_file_cases, start=1):
            case_root = tmpdir / f"missing_file_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)

        print("PHASE13_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
        print(
            "PHASE13_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT="
            f"{len(required_cases) + len(forbidden_cases) + len(missing_file_cases)}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE13_SHARED_SUMMARY_SURFACES=fail: {exc}")
        return 1

    print("PHASE13_SHARED_SUMMARY_SURFACES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
