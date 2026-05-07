#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

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


def write(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    write(
        root,
        DOCS_README_PATH,
        """# Zigux Documentation
Phase 12 notes
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `make -C zigux phase12-smoke`
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`
""",
    )
    write(
        root,
        REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist
- if the change touches the shared Phase 12 complex-driver packet
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `drivers/nvme/host/pci_verify.zig`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`
""",
    )
    write(
        root,
        PHASE12_SEQUENCE_PATH,
        """# Phase 12 Release Sequencing
- PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` keep the build-only contract fail-closed
- the checker-local closure-companion update is landed
- the next bounded same-lane follow-through is drift control
""",
    )
    write(
        root,
        PHASE12_CLOSURE_CHECKLIST_PATH,
        """# Phase 12 Release Closure Checklist
- scripts/zigux/check-build-only-phase12-surface.py
- Documentation/zigux/phase12-raw-github-coverage-survey.md
- two commit-pinned artifacts plus two shared-tree-only anchors
- now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set
- `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase12 ZIG=<attached-zig-path>`
- the smallest same-lane follow-through is now shared-surface drift control
""",
    )
    write(
        root,
        PHASE12_COMPLEX_DRIVER_LANE_PATH,
        """# Phase 12 Complex Driver Lane Sequencing
- complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`
- excluded from this note on purpose: the shared PMO release packet and the non-driver libbpf helper packet
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
""",
    )
    write(
        root,
        PHASE12_RAW_GITHUB_COVERAGE_PATH,
        """# Phase 12 Raw GitHub Coverage Survey
- commit-pinned fallback artifacts:
- shared-tree-only anchors:
- The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.
- current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion
- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview
- The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion
""",
    )
    write(
        root,
        PHASE12_COORDINATION_MATRIX_PATH,
        """# Phase 12 Release Coordination Matrix
- release-order authority: `Documentation/zigux/phase12-release-sequencing.md`
- PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2
- PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2
- PHASE12_SHARED_SMOKE_SURFACE_COUNT=6
- build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`
- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` packet, no focused libbpf-only replay route, no raw-coverage packet guard, no cross-build replay packet, and no `make -C zigux phase12-validate` target on `master`
""",
    )
    write(
        root,
        NVME_FALLBACK_MAP_PATH,
        """# Phase 12 NVMe PCI Raw GitHub Fallback Map
- PMO closure companion
- Documentation/zigux/phase12-release-closure-checklist.md
- Documentation/zigux/phase12-release-coordination-matrix.md
- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback map, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback map into a second sequencing document.
- The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.
- The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`
""",
    )
    write(
        root,
        VIRTIO_SCSI_FALLBACK_PATH,
        """# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog
- PMO closure companion
- Documentation/zigux/phase12-release-closure-checklist.md
- Documentation/zigux/phase12-release-coordination-matrix.md
- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.
- The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.
- The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`
""",
    )
    write(
        root,
        VIRTIO_NET_SURVEY_PATH,
        """# Phase 12 Virtio Net Survey
- public fallback posture: shared-tree-only anchor
- segmented rollout boundary
- runtime-data-path boundary remains blocked
""",
    )
    write(
        root,
        LIBBPF_SURVEY_PATH,
        """# Phase 12 Libbpf Segment Survey
- public fallback posture: shared-tree-only anchor
- Documentation/zigux/phase12-release-closure-checklist.md
- the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall
""",
    )
    write(
        root,
        SCRIPTS_README_PATH,
        """# scripts/zigux
Phase 12 flow
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`
""",
    )
    write(
        root,
        TESTS_README_PATH,
        """# zigux/tests
- keep `Documentation/zigux/phase12-release-closure-checklist.md` visible beside `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `make -C zigux phase12`
""",
    )
    write(
        root,
        PHASE12_BUILD_PATH,
        """const smoke_step = b.step("smoke", "Run Phase 12 direct driver and syntax-lab smoke tests");
const test_step = b.step("test", "Run Phase 12 driver and survey tests");
const phase12_virtio_net_syntax_lab_module = b.createModule(.{});
const phase12_virtio_scsi_syntax_lab_module = b.createModule(.{});
run_phase12_nvme_pci_verify_tests.step
run_phase12_virtio_scsi_syntax_lab_tests.step
const phase12_libbpf_reviewability_module = b.createModule(.{});
""",
    )
    write(
        root,
        MAKEFILE_PATH,
        """PHONY += phase12-smoke
phase12-smoke:
	$(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all
phase12-test:
	$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all
phase12: phase12-smoke phase12-test
""",
    )
    write(
        root,
        WORKFLOW_PATH,
        """name: zigux-bootstrap
- name: Self-test Phase 12 build-only surface checker
  run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
- name: Check Phase 12 build-only surface
  run: python3 scripts/zigux/check-build-only-phase12-surface.py
- name: Run focused Phase 12 smoke shard
  run: make -C zigux phase12-smoke
- name: Run Phase 12 complex driver tests
  run: zig build test --build-file zigux/tests/phase12_build.zig --summary all
""",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase12-build-only-surface-") as tmp:
        root = Path(tmp)
        write_fixture_tree(root)

        failures = validate(root)
        if failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1

        docs_readme_path = root / DOCS_README_PATH
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        broken_docs_readme = original_docs_readme.replace(
            "- `Documentation/zigux/phase12-release-coordination-matrix.md`\n",
            "",
            1,
        )
        docs_readme_path.write_text(broken_docs_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{DOCS_README_PATH}:`Documentation/zigux/phase12-release-coordination-matrix.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("docs-readme-coordination-matrix-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        checklist_path = root / REVIEW_CHECKLIST_PATH
        original_checklist = checklist_path.read_text(encoding="utf-8")
        broken_checklist = original_checklist.replace(
            "- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`\n",
            "",
            1,
        )
        checklist_path.write_text(broken_checklist, encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEW_CHECKLIST_PATH}:`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("review-checklist-complex-driver-lane-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        broken_checklist = original_checklist.replace(
            "- `Documentation/zigux/phase12-raw-github-coverage-survey.md`\n",
            "",
            1,
        )
        checklist_path.write_text(broken_checklist, encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEW_CHECKLIST_PATH}:`Documentation/zigux/phase12-raw-github-coverage-survey.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("review-checklist-raw-coverage-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        broken_checklist = original_checklist.replace(
            "- `drivers/nvme/host/pci_verify.zig`\n",
            "",
            1,
        )
        checklist_path.write_text(broken_checklist, encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEW_CHECKLIST_PATH}:`drivers/nvme/host/pci_verify.zig`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("review-checklist-nvme-verify-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        broken_checklist = original_checklist.replace(
            "- `zigux/tests/phase12_virtio_net_syntax_lab.zig`\n",
            "",
            1,
        )
        checklist_path.write_text(broken_checklist, encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEW_CHECKLIST_PATH}:`zigux/tests/phase12_virtio_net_syntax_lab.zig`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("review-checklist-virtio-net-syntax-lab-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        broken_checklist = original_checklist.replace(
            "- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`\n",
            "",
            1,
        )
        checklist_path.write_text(broken_checklist, encoding="utf-8")
        failures = validate(root)
        expected = f"{REVIEW_CHECKLIST_PATH}:`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("review-checklist-virtio-scsi-syntax-lab-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        sequence_path = root / PHASE12_SEQUENCE_PATH
        original_sequence = sequence_path.read_text(encoding="utf-8")
        broken_sequence = original_sequence.replace(
            "- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`\n",
            "",
            1,
        )
        sequence_path.write_text(broken_sequence, encoding="utf-8")
        failures = validate(root)
        expected = f"{PHASE12_SEQUENCE_PATH}:`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("sequence-complex-driver-lane-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        sequence_path.write_text(original_sequence, encoding="utf-8")

        closure_path = root / PHASE12_CLOSURE_CHECKLIST_PATH
        original_closure = closure_path.read_text(encoding="utf-8")
        broken_closure = original_closure.replace(
            "now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set\n",
            "",
            1,
        )
        closure_path.write_text(broken_closure, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_CLOSURE_CHECKLIST_PATH}:"
            "now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("closure-checklist-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        closure_path.write_text(original_closure, encoding="utf-8")

        broken_closure = original_closure.replace(
            "- `make -C zigux phase12-smoke ZIG=<attached-zig-path>`\n",
            "",
            1,
        )
        closure_path.write_text(broken_closure, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_CLOSURE_CHECKLIST_PATH}:"
            "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("closure-checklist-attached-zig-smoke-guard")
            for failure in failures:
                print(failure)
            return 1
        closure_path.write_text(original_closure, encoding="utf-8")

        complex_driver_lane_path = root / PHASE12_COMPLEX_DRIVER_LANE_PATH
        original_complex_driver_lane = complex_driver_lane_path.read_text(encoding="utf-8")
        broken_complex_driver_lane = original_complex_driver_lane.replace(
            "- complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`\n",
            "",
            1,
        )
        complex_driver_lane_path.write_text(broken_complex_driver_lane, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_COMPLEX_DRIVER_LANE_PATH}:"
            "complex-driver scope in this note: `virtio_net`, `nvme_pci`, and `virtio_scsi`"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("complex-driver-lane-scope-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        complex_driver_lane_path.write_text(original_complex_driver_lane, encoding="utf-8")

        raw_coverage_path = root / PHASE12_RAW_GITHUB_COVERAGE_PATH
        original_raw_coverage = raw_coverage_path.read_text(encoding="utf-8")
        broken_raw_coverage = original_raw_coverage.replace(
            "- shared-tree-only anchors:\n",
            "",
            1,
        )
        raw_coverage_path.write_text(broken_raw_coverage, encoding="utf-8")
        failures = validate(root)
        expected = f"{PHASE12_RAW_GITHUB_COVERAGE_PATH}:shared-tree-only anchors:"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("raw-coverage-shared-tree-anchor-guard")
            for failure in failures:
                print(failure)
            return 1
        raw_coverage_path.write_text(original_raw_coverage, encoding="utf-8")

        broken_raw_coverage = original_raw_coverage.replace(
            "- The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.\n",
            "",
            1,
        )
        raw_coverage_path.write_text(broken_raw_coverage, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_RAW_GITHUB_COVERAGE_PATH}:"
            "The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes."
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("raw-coverage-shared-smoke-order-guard")
            for failure in failures:
                print(failure)
            return 1
        raw_coverage_path.write_text(original_raw_coverage, encoding="utf-8")

        broken_raw_coverage = original_raw_coverage.replace(
            "- current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`\n",
            "",
            1,
        )
        raw_coverage_path.write_text(broken_raw_coverage, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_RAW_GITHUB_COVERAGE_PATH}:"
            "current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("raw-coverage-current-smoke-packet-guard")
            for failure in failures:
                print(failure)
            return 1
        raw_coverage_path.write_text(original_raw_coverage, encoding="utf-8")

        broken_raw_coverage = original_raw_coverage.replace(
            "- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview\n",
            "",
            1,
        )
        raw_coverage_path.write_text(broken_raw_coverage, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_RAW_GITHUB_COVERAGE_PATH}:"
            "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("raw-coverage-coordination-matrix-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        raw_coverage_path.write_text(original_raw_coverage, encoding="utf-8")

        coordination_matrix_path = root / PHASE12_COORDINATION_MATRIX_PATH
        original_coordination_matrix = coordination_matrix_path.read_text(encoding="utf-8")
        broken_coordination_matrix = original_coordination_matrix.replace(
            "- build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`\n",
            "",
            1,
        )
        coordination_matrix_path.write_text(broken_coordination_matrix, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{PHASE12_COORDINATION_MATRIX_PATH}:"
            "build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("coordination-matrix-build-only-guard")
            for failure in failures:
                print(failure)
            return 1
        coordination_matrix_path.write_text(original_coordination_matrix, encoding="utf-8")

        broken_coordination_matrix = original_coordination_matrix.replace(
            "- PHASE12_SHARED_SMOKE_SURFACE_COUNT=6\n",
            "",
            1,
        )
        coordination_matrix_path.write_text(broken_coordination_matrix, encoding="utf-8")
        failures = validate(root)
        expected = f"{PHASE12_COORDINATION_MATRIX_PATH}:PHASE12_SHARED_SMOKE_SURFACE_COUNT=6"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("coordination-matrix-smoke-count-guard")
            for failure in failures:
                print(failure)
            return 1
        coordination_matrix_path.write_text(original_coordination_matrix, encoding="utf-8")

        nvme_fallback_path = root / NVME_FALLBACK_MAP_PATH
        original_nvme_fallback = nvme_fallback_path.read_text(encoding="utf-8")
        broken_nvme_fallback = original_nvme_fallback.replace(
            "- The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.\n",
            "",
            1,
        )
        nvme_fallback_path.write_text(broken_nvme_fallback, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{NVME_FALLBACK_MAP_PATH}:"
            "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below."
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("nvme-fallback-shared-smoke-order-guard")
            for failure in failures:
                print(failure)
            return 1
        nvme_fallback_path.write_text(original_nvme_fallback, encoding="utf-8")

        broken_nvme_fallback = original_nvme_fallback.replace(
            "- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback map, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback map into a second sequencing document.\n",
            "",
            1,
        )
        nvme_fallback_path.write_text(broken_nvme_fallback, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{NVME_FALLBACK_MAP_PATH}:"
            "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback map, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback map into a second sequencing document."
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("nvme-fallback-coordination-matrix-guard")
            for failure in failures:
                print(failure)
            return 1
        nvme_fallback_path.write_text(original_nvme_fallback, encoding="utf-8")

        virtio_scsi_fallback_path = root / VIRTIO_SCSI_FALLBACK_PATH
        original_virtio_scsi_fallback = virtio_scsi_fallback_path.read_text(encoding="utf-8")
        broken_virtio_scsi_fallback = original_virtio_scsi_fallback.replace(
            "- The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.\n",
            "",
            1,
        )
        virtio_scsi_fallback_path.write_text(broken_virtio_scsi_fallback, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{VIRTIO_SCSI_FALLBACK_PATH}:"
            "The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below."
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("virtio-scsi-fallback-shared-smoke-order-guard")
            for failure in failures:
                print(failure)
            return 1
        virtio_scsi_fallback_path.write_text(original_virtio_scsi_fallback, encoding="utf-8")

        broken_virtio_scsi_fallback = original_virtio_scsi_fallback.replace(
            "- `Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.\n",
            "",
            1,
        )
        virtio_scsi_fallback_path.write_text(broken_virtio_scsi_fallback, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{VIRTIO_SCSI_FALLBACK_PATH}:"
            "`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document."
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("virtio-scsi-fallback-coordination-matrix-guard")
            for failure in failures:
                print(failure)
            return 1
        virtio_scsi_fallback_path.write_text(original_virtio_scsi_fallback, encoding="utf-8")

        libbpf_survey_path = root / LIBBPF_SURVEY_PATH
        original_libbpf_survey = libbpf_survey_path.read_text(encoding="utf-8")
        broken_libbpf_survey = original_libbpf_survey.replace(
            "- Documentation/zigux/phase12-release-closure-checklist.md\n",
            "",
            1,
        )
        libbpf_survey_path.write_text(broken_libbpf_survey, encoding="utf-8")
        failures = validate(root)
        expected = f"{LIBBPF_SURVEY_PATH}:Documentation/zigux/phase12-release-closure-checklist.md"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("libbpf-survey-closure-companion-guard")
            for failure in failures:
                print(failure)
            return 1
        libbpf_survey_path.write_text(original_libbpf_survey, encoding="utf-8")

        broken_libbpf_survey = original_libbpf_survey.replace(
            "- the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall\n",
            "",
            1,
        )
        libbpf_survey_path.write_text(broken_libbpf_survey, encoding="utf-8")
        failures = validate(root)
        expected = (
            f"{LIBBPF_SURVEY_PATH}:"
            "the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall"
        )
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("libbpf-survey-shared-bridge-boundary-guard")
            for failure in failures:
                print(failure)
            return 1
        libbpf_survey_path.write_text(original_libbpf_survey, encoding="utf-8")

        scripts_readme_path = root / SCRIPTS_README_PATH
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        broken_scripts_readme = original_scripts_readme.replace(
            "- `Documentation/zigux/phase12-release-coordination-matrix.md`\n",
            "",
            1,
        )
        scripts_readme_path.write_text(broken_scripts_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{SCRIPTS_README_PATH}:`Documentation/zigux/phase12-release-coordination-matrix.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("scripts-readme-coordination-matrix-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        broken_scripts_readme = original_scripts_readme.replace(
            "- `zigux/tests/phase12_virtio_net_syntax_lab.zig`\n",
            "",
            1,
        )
        scripts_readme_path.write_text(broken_scripts_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{SCRIPTS_README_PATH}:`zigux/tests/phase12_virtio_net_syntax_lab.zig`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("scripts-readme-net-syntax-lab-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        broken_scripts_readme = original_scripts_readme.replace(
            "- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`\n",
            "",
            1,
        )
        scripts_readme_path.write_text(broken_scripts_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{SCRIPTS_README_PATH}:`zigux/tests/phase12_virtio_scsi_syntax_lab.zig`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("scripts-readme-scsi-syntax-lab-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        tests_readme_path = root / TESTS_README_PATH
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        broken_tests_readme = original_tests_readme.replace(
            "- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`\n",
            "",
            1,
        )
        tests_readme_path.write_text(broken_tests_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{TESTS_README_PATH}:`Documentation/zigux/phase12-complex-driver-lane-sequencing.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("tests-readme-complex-driver-lane-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        broken_tests_readme = original_tests_readme.replace(
            "- `Documentation/zigux/phase12-raw-github-coverage-survey.md`\n",
            "",
            1,
        )
        tests_readme_path.write_text(broken_tests_readme, encoding="utf-8")
        failures = validate(root)
        expected = f"{TESTS_README_PATH}:`Documentation/zigux/phase12-raw-github-coverage-survey.md`"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("tests-readme-raw-coverage-marker-guard")
            for failure in failures:
                print(failure)
            return 1
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        build_path = root / PHASE12_BUILD_PATH
        original_build = build_path.read_text(encoding="utf-8")
        broken_build = original_build.replace(
            "run_phase12_nvme_pci_verify_tests.step\n",
            "",
            1,
        )
        build_path.write_text(broken_build, encoding="utf-8")
        failures = validate(root)
        expected = f"{PHASE12_BUILD_PATH}:run_phase12_nvme_pci_verify_tests.step"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("phase12-build-nvme-verify-smoke-guard")
            for failure in failures:
                print(failure)
            return 1
        build_path.write_text(original_build, encoding="utf-8")

        workflow_path = root / WORKFLOW_PATH
        original_workflow = workflow_path.read_text(encoding="utf-8")
        broken_workflow = original_workflow.replace(
            "- name: Run focused Phase 12 smoke shard\n  run: make -C zigux phase12-smoke\n",
            "",
            1,
        )
        workflow_path.write_text(broken_workflow, encoding="utf-8")
        failures = validate(root)
        expected = f"{WORKFLOW_PATH}:Run focused Phase 12 smoke shard"
        if expected not in failures:
            print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=fail")
            print("workflow-smoke-step-marker-guard")
            for failure in failures:
                print(failure)
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
