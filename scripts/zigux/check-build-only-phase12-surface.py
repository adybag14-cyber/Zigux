#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "scripts/zigux/README.md").exists() and (candidate / ".github/workflows/zigux-bootstrap.yml").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SCRIPTS_README_PATH = "scripts/zigux/README.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
TESTS_README_PATH = "zigux/tests/README.md"

REQUIRED_PHASE12_PATHS = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    FREEZE_MAP_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "zigux/tests/phase12_build.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_virtio_net.zig",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_net_syntax_lab.zig",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "zigux/tests/fixtures/phase12_libbpf_snapshot.json",
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
    "zigux/tests/phase12_libbpf_snapshot_determinism.zig",
]

FORBIDDEN_PHASE12_PATHS = [
    "scripts/zigux/validate-phase12.py",
    "scripts/zigux/check-phase12-build-inventory.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_libbpf_manifest.json",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_cross_build.zig",
]

PHASE12_REMOVED_SURFACE_MARKER = (
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, "
    "cross-build, or `phase12-validate` surfaces that are not on `master`."
)

REQUIRED_SCRIPTS_README_MARKERS = [
    "Phase 12 flow",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`zigux/tests/phase12_build.zig`",
    "`make -C zigux phase12-smoke`",
    "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
    PHASE12_REMOVED_SURFACE_MARKER,
]

REQUIRED_SCRIPTS_README_EXACT_COUNTS = {
    PHASE12_REMOVED_SURFACE_MARKER: 1,
}

REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check Phase 12 build-only surface",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "Run focused Phase 12 smoke shard",
    "make -C zigux phase12-smoke",
    "Run Phase 12 complex driver and libbpf tests",
    "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
]

REQUIRED_MAKEFILE_MARKERS = [
    "phase12-smoke:",
    "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12-test:",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-smoke phase12-test",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "phase12-validate:",
    "phase12-libbpf-test:",
    "phase12-cross:",
]

FORBIDDEN_WORKFLOW_MARKERS = [
    "Validate Phase 12 files",
    "python3 scripts/zigux/validate-phase12.py",
    "Run focused Phase 12 libbpf replay",
    "Run Phase 12 cross-build replay",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_absent(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{label}_forbidden:{marker}")


def ensure_exact_counts(failures: list[str], label: str, text: str, counts: dict[str, int]) -> None:
    for marker, expected_count in counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            failures.append(f"{label}_exact_count:{marker}:expected={expected_count}:actual={actual_count}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_PHASE12_PATHS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_PHASE12_PATHS:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    makefile = read_text(root, MAKEFILE_PATH)

    ensure_contains(failures, "scripts_readme", scripts_readme, REQUIRED_SCRIPTS_README_MARKERS)
    ensure_exact_counts(failures, "scripts_readme", scripts_readme, REQUIRED_SCRIPTS_README_EXACT_COUNTS)
    ensure_contains(failures, "workflow", workflow, REQUIRED_WORKFLOW_MARKERS)
    ensure_absent(failures, "workflow", workflow, FORBIDDEN_WORKFLOW_MARKERS)
    ensure_contains(failures, "makefile", makefile, REQUIRED_MAKEFILE_MARKERS)
    ensure_absent(failures, "makefile", makefile, FORBIDDEN_MAKEFILE_MARKERS)

    return failures


def placeholder_for(rel_path: str) -> str:
    if rel_path.endswith(".zig"):
        return "// phase12 placeholder\n"
    if rel_path.endswith(".json"):
        return "{}\n"
    return "# phase12 placeholder\n"


def minimal_marker_doc(title: str, markers: list[str]) -> str:
    return "\n".join([f"# {title}", *markers, ""])


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / SCRIPTS_README_PATH, minimal_marker_doc("scripts/zigux", REQUIRED_SCRIPTS_README_MARKERS))
    write_text(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")
    write_text(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")

    for rel_path in REQUIRED_PHASE12_PATHS:
        if rel_path in {SCRIPTS_README_PATH, WORKFLOW_PATH, MAKEFILE_PATH}:
            continue
        write_text(root / rel_path, placeholder_for(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        scripts_readme_path = base / SCRIPTS_README_PATH
        workflow_path = base / WORKFLOW_PATH
        makefile_path = base / MAKEFILE_PATH

        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(scripts_readme.replace(PHASE12_REMOVED_SURFACE_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"scripts_readme:{PHASE12_REMOVED_SURFACE_MARKER}")

        write_fixture_tree(base)
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(scripts_readme + PHASE12_REMOVED_SURFACE_MARKER + "\n", encoding="utf-8")
        expect_failure(
            base,
            f"scripts_readme_exact_count:{PHASE12_REMOVED_SURFACE_MARKER}:expected=1:actual=2",
        )

        write_fixture_tree(base)
        workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(workflow.replace("make -C zigux phase12-smoke", "", 1), encoding="utf-8")
        expect_failure(base, "workflow:make -C zigux phase12-smoke")

        write_fixture_tree(base)
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(makefile + "phase12-validate:\n", encoding="utf-8")
        expect_failure(base, "makefile_forbidden:phase12-validate:")

        write_fixture_tree(base)
        write_text(base / FORBIDDEN_PHASE12_PATHS[0], "# stale phase12 validator placeholder\n")
        expect_failure(base, f"unexpected_file:{FORBIDDEN_PHASE12_PATHS[0]}")

        write_fixture_tree(base)
        write_text(base / FORBIDDEN_PHASE12_PATHS[3], "# stale phase12 coverage note\n")
        expect_failure(base, f"unexpected_file:{FORBIDDEN_PHASE12_PATHS[3]}")

        write_fixture_tree(base)
        missing_path = base / REQUIRED_PHASE12_PATHS[-1]
        missing_path.unlink()
        expect_failure(base, f"missing_file:{REQUIRED_PHASE12_PATHS[-1]}")

        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=7")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 12 build-only fallback surface against the surviving current-master packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the repository root inferred from this script.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(
        "PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{len(REQUIRED_PHASE12_PATHS) + len(REQUIRED_SCRIPTS_README_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
