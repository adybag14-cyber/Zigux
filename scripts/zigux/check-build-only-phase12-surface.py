#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
PHASE12_SEQUENCE_PATH = "Documentation/zigux/phase12-release-sequencing.md"
PHASE12_CLOSURE_CHECKLIST_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
PHASE12_COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
PHASE12_RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
NVME_FALLBACK_MAP_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
VIRTIO_SCSI_FALLBACK_PATH = "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
VIRTIO_NET_SURVEY_PATH = "Documentation/zigux/phase12-virtio-net-survey.md"
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
PHASE12_COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase12.py",
]

FORBIDDEN_GLOBS = [
    "scripts/zigux/check-phase12-*.py",
]

REQUIRED_FILE_MARKERS = {
    DOCS_README_PATH: [
        "Phase 12 notes",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`make -C zigux phase12-smoke`",
        "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "if the change touches the shared Phase 12 complex-driver packet",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`drivers/nvme/host/pci_verify.zig`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`",
    ],
    PHASE12_SEQUENCE_PATH: [
        "PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` keep the build-only contract fail-closed",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "the checker-local closure-companion update is landed",
        "the next bounded same-lane follow-through is drift control",
    ],
    PHASE12_CLOSURE_CHECKLIST_PATH: [
        "Phase 12 Release Closure Checklist",
        "scripts/zigux/check-build-only-phase12-surface.py",
        "Documentation/zigux/phase12-raw-github-coverage-survey.md",
        "two commit-pinned artifacts plus two shared-tree-only anchors",
        "now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "the smallest same-lane follow-through is now shared-surface drift control",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`",
        "excluded from this note on purpose: the shared PMO release packet and the non-driver libbpf helper packet",
        "`Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
    ],
    PHASE12_RAW_GITHUB_COVERAGE_PATH: [
        "commit-pinned fallback artifacts:",
        "shared-tree-only anchors:",
        "The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.",
        "current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion",
    ],
    PHASE12_COORDINATION_MATRIX_PATH: [
        "Phase 12 Release Coordination Matrix",
        "release-order authority: `Documentation/zigux/phase12-release-sequencing.md`",
        "PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`",
        "shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
        "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
        "PHASE12_SHARED_SMOKE_SURFACE_COUNT=6",
        "build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`",
        "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase12 ZIG=<attached-zig-path>`",
        "there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` packet, no focused libbpf-only replay route, no raw-coverage packet guard, no cross-build replay packet, and no `make -C zigux phase12-validate` target on `master`",
    ],
    NVME_FALLBACK_MAP_PATH: [
        "PMO closure companion",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback map, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback map into a second sequencing document.",
        "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
    ],
    VIRTIO_SCSI_FALLBACK_PATH: [
        "PMO closure companion",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
        "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.",
        "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.",
        "The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`",
    ],
    VIRTIO_NET_SURVEY_PATH: [
        "public fallback posture: shared-tree-only anchor",
        "segmented rollout boundary",
        "runtime-data-path boundary remains blocked",
    ],
    LIBBPF_SURVEY_PATH: [
        "public fallback posture: shared-tree-only anchor",
        "Documentation/zigux/phase12-release-closure-checklist.md",
        "the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall",
    ],
    SCRIPTS_README_PATH: [
        "Phase 12 flow",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed",
        "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
    ],
    TESTS_README_PATH: [
        "keep `Documentation/zigux/phase12-release-closure-checklist.md` visible beside `Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "`Documentation/zigux/phase12-raw-github-coverage-survey.md`",
        "`zigux/tests/phase12_virtio_net_syntax_lab.zig`",
        "`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`",
        "`scripts/zigux/check-build-only-phase12-surface.py`",
        "`make -C zigux phase12`",
    ],
    PHASE12_BUILD_PATH: [
        'const smoke_step = b.step("smoke", "Run Phase 12 direct driver and syntax-lab smoke tests");',
        'const test_step = b.step("test", "Run Phase 12 driver and survey tests");',
        "phase12_virtio_net_syntax_lab_module",
        "phase12_virtio_scsi_syntax_lab_module",
        "run_phase12_nvme_pci_verify_tests.step",
        "run_phase12_virtio_scsi_syntax_lab_tests.step",
        "phase12_libbpf_reviewability_module",
    ],
    MAKEFILE_PATH: [
        "PHONY += phase12-smoke",
        "phase12-smoke:",
        "$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12-test:",
        "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
        "phase12: phase12-smoke phase12-test",
    ],
    WORKFLOW_PATH: [
        "Self-test Phase 12 build-only surface checker",
        "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "Check Phase 12 build-only surface",
        "python3 scripts/zigux/check-build-only-phase12-surface.py",
        "Run focused Phase 12 smoke shard",
        "make -C zigux phase12-smoke",
        "Run Phase 12 complex driver tests",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    for pattern in FORBIDDEN_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                failures.append(f"unexpected_file:{path.relative_to(root)}")

    if failures:
        return failures

    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel_path}:{marker}")

    return failures


def build_fixture_text(title: str, markers: list[str]) -> str:
    lines = [f"# {title}", ""]
    lines.extend(f"- {marker}" for marker in markers)
    lines.append("")
    return "\n".join(lines)


def write_fixture_tree(root: Path) -> None:
    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        title = Path(rel_path).name
        write_text(root, rel_path, build_fixture_text(title, markers))


def expect_missing_marker(root: Path, rel_path: str, marker: str, label: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if marker not in original:
        raise AssertionError(f"fixture missing marker for {label}: {marker}")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    expected = f"{rel_path}:{marker}"
    if expected not in failures:
        raise AssertionError(f"{label}: expected {expected!r}, got {failures!r}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="phase12-build-only-surface-") as tmp:
            root = Path(tmp)
            write_fixture_tree(root)

            failures = validate(root)
            if failures:
                print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
                for failure in failures:
                    print(failure)
                return 1

            expect_missing_marker(
                root,
                DOCS_README_PATH,
                "`Documentation/zigux/phase12-release-coordination-matrix.md`",
                "docs-readme-coordination-matrix-marker-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_CLOSURE_CHECKLIST_PATH,
                "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
                "closure-checklist-attached-zig-smoke-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_SEQUENCE_PATH,
                "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
                "sequence-attached-zig-smoke-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_SEQUENCE_PATH,
                "`make -C zigux phase12 ZIG=<attached-zig-path>`",
                "sequence-attached-zig-phase12-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_RAW_GITHUB_COVERAGE_PATH,
                "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
                "raw-coverage-attached-zig-smoke-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_RAW_GITHUB_COVERAGE_PATH,
                "`make -C zigux phase12 ZIG=<attached-zig-path>`",
                "raw-coverage-attached-zig-phase12-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_COORDINATION_MATRIX_PATH,
                "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`",
                "coordination-matrix-attached-zig-smoke-guard",
            )
            expect_missing_marker(
                root,
                PHASE12_COORDINATION_MATRIX_PATH,
                "`make -C zigux phase12 ZIG=<attached-zig-path>`",
                "coordination-matrix-attached-zig-phase12-guard",
            )
            expect_missing_marker(
                root,
                WORKFLOW_PATH,
                "Run focused Phase 12 smoke shard",
                "workflow-smoke-step-marker-guard",
            )

            forbidden_path = root / FORBIDDEN_FILES[0]
            write_text(root, FORBIDDEN_FILES[0], "# forbidden\n")
            failures = validate(root)
            expected = f"unexpected_file:{FORBIDDEN_FILES[0]}"
            if expected not in failures:
                raise AssertionError(f"forbidden-file-guard: expected {expected!r}, got {failures!r}")
            forbidden_path.unlink()

    except AssertionError as exc:
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
        print(str(exc))
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shared Phase 12 build-only review surface.")
    parser.add_argument("root", nargs="?", default=ROOT, type=Path, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
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
    print(f"PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT={sum(len(v) for v in REQUIRED_FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())