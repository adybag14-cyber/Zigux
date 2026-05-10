#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-libfs-slice.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "include/zigux/abi.h",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "drivers/tty/hvc/hvc_console.h",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-notifier-packet.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
]

DOC_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "include/zigux/abi.h",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "the current eight-test shared-helper release packet",
]

REVIEW_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "include/zigux/abi.h",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "the same validator-first eight-test shared-helper release packet",
    "shipped direct evidence beside `zigux/tests/phase13_landlock_syscalls.zig` rather than an extra shared replay step",
]

DOC_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "the current eight-test shared-helper release packet": 1,
}

REVIEW_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "the same validator-first eight-test shared-helper release packet": 1,
    "shipped direct evidence beside `zigux/tests/phase13_landlock_syscalls.zig` rather than an extra shared replay step": 1,
}

RELEASE_NOTES_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "The helper-owned Landlock boundary notes stay in the broader shipped release packet because they record the current ruleset ownership and syscall-governance limits that still block tranche closure, but they do not add extra shared replay steps beyond the eight-test route above.",
    "The current Phase 13 packet still ships with no dedicated `Documentation/zigux/phase13-closure.md` note on `master`.",
    "the release-facing helper tranche remains active until the shared replay, the adjacent helper-owned Landlock boundary notes, and the remaining blocker posture all say the same thing",
]

RELEASE_NOTES_EXACT_COUNTS = {
    "The helper-owned Landlock boundary notes stay in the broader shipped release packet because they record the current ruleset ownership and syscall-governance limits that still block tranche closure, but they do not add extra shared replay steps beyond the eight-test route above.": 1,
    "The current Phase 13 packet still ships with no dedicated `Documentation/zigux/phase13-closure.md` note on `master`.": 1,
}

ROADMAP_TRACEABILITY_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "The helper-owned Landlock boundary notes stay in that adjacent release packet because they document the shipped ownership and governance blockers that still prevent a closure claim without inflating the eight-test shared replay count.",
    "the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work",
]

ROADMAP_TRACEABILITY_EXACT_COUNTS = {
    "The helper-owned Landlock boundary notes stay in that adjacent release packet because they document the shipped ownership and governance blockers that still prevent a closure claim without inflating the eight-test shared replay count.": 1,
    "the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work": 1,
}

CONTRIBUTOR_GUIDE_REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "adjacent shipped release-surface evidence",
    "they do not add extra shared replay steps beyond the validator-first route above",
    "the Phase 13 release packet stays active until the shared replay and the remaining blocker posture say otherwise together",
]

CONTRIBUTOR_GUIDE_EXACT_COUNTS = {
    "Documentation/zigux/phase13-release-notes-survey.md": 2,
    "Documentation/zigux/phase13-roadmap-traceability.md": 2,
    "Documentation/zigux/phase13-notifier-list-survey.md": 2,
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": 4,
    "zigux/tests/phase13_notifier_list_manifest.json": 2,
    "zigux/tests/phase13_notifier_list_reviewability.zig": 2,
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": 2,
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py": 3,
    "zigux/bindings/notifier_abi.zig": 2,
    "include/zigux/notifier_abi.h": 2,
    "zigux/helpers/notifier_chain_view.zig": 2,
    "adjacent shipped release-surface evidence": 2,
    "they do not add extra shared replay steps beyond the validator-first route above": 1,
    "the Phase 13 release packet stays active until the shared replay and the remaining blocker posture say otherwise together": 1,
}

CONTRIBUTOR_SYNC_REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "scripts/zigux/validate-phase13-release.py",
    "zigux/Makefile",
    "shared validator-first replay route separate from the broader shipped adjacent release-surface evidence",
    "extra replay steps",
]

CONTRIBUTOR_SYNC_EXACT_COUNTS = {
    "Documentation/zigux/phase13-release-notes-survey.md": 1,
    "Documentation/zigux/phase13-roadmap-traceability.md": 1,
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/tests/phase13_notifier_list_reviewability.zig": 2,
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": 2,
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "shared validator-first replay route separate from the broader shipped adjacent release-surface evidence": 1,
    "extra replay steps": 1,
}

TESTS_REVIEW_COMPANION_REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "include/zigux/notifier_abi.h",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "scripts/zigux/validate-phase13-release.py",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "same shipped validator-first release path",
    "extra Phase 13 checker or replay surfaces that are not on `master`",
]

TESTS_REVIEW_COMPANION_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 2,
    "Documentation/zigux/phase13-devres-survey.md": 3,
    "zigux/tests/phase13_notifier_list_manifest.json": 3,
    "zigux/tests/phase13_notifier_list_reviewability.zig": 2,
    "include/zigux/notifier_abi.h": 3,
    "zigux/bindings/notifier_abi.zig": 3,
    "zigux/helpers/notifier_chain_view.zig": 3,
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py": 3,
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": 3,
    "same shipped validator-first release path": 1,
    "extra Phase 13 checker or replay surfaces that are not on `master`": 2,
}

SCRIPTS_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "check-phase13-landlock-ruleset-packet.py",
    "zigux/tests/phase13_build.zig",
    "phase13_libfs.zig",
    "phase13_devres.zig",
    "phase13_devres_reviewability.zig",
    "phase13_devres_dma_coherent.zig",
    "phase13_devres_boundary_evidence.zig",
    "phase13_landlock_ruleset.zig",
    "phase13_landlock_syscalls.zig",
    "phase13_libfs_reviewability.zig",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "the eight-test shared helper replay",
    "adjacent review evidence instead of adding extra shared replay steps on `master`",
]

SCRIPTS_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/tests/phase13_notifier_list_reviewability.zig": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "phase13_devres_boundary_evidence.zig": 1,
    "make -C zigux phase13-validate": 1,
    "the eight-test shared helper replay": 1,
    "adjacent review evidence instead of adding extra shared replay steps on `master`": 1,
}

TESTS_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "scripts/zigux/validate-phase13-release.py",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "the current eight-test shared-helper release packet",
    "adjacent release-surface evidence rather than extra shared replay steps",
]

TESTS_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 2,
    "zigux/tests/phase13_notifier_list_manifest.json": 2,
    "zigux/bindings/notifier_abi.zig": 2,
    "include/zigux/notifier_abi.h": 2,
    "zigux/helpers/notifier_chain_view.zig": 2,
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py": 2,
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig": 2,
    "the current eight-test shared-helper release packet": 2,
    "adjacent release-surface evidence rather than extra shared replay steps": 1,
}

PHASE13_BUILD_EXACT_COUNTS = {
    " = b.addTest(.{": 8,
    "test_step.dependOn(&run_phase13_": 8,
    '.root_source_file = b.path("phase13_libfs.zig"),': 1,
    '.root_source_file = b.path("phase13_devres.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_reviewability.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_dma_coherent.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_boundary_evidence.zig"),': 1,
    '.root_source_file = b.path("phase13_landlock_ruleset.zig"),': 1,
    '.root_source_file = b.path("phase13_landlock_syscalls.zig"),': 1,
    '.root_source_file = b.path("phase13_libfs_reviewability.zig"),': 1,
}

PHASE13_BUILD_REQUIRED_MARKERS = [
    'const phase13_libfs_tests = b.addTest(.{',
    '.name = "phase13-libfs-tests"',
    "const run_phase13_libfs_tests = b.addRunArtifact(phase13_libfs_tests);",
    'const phase13_devres_tests = b.addTest(.{',
    '.name = "phase13-devres-tests"',
    "const run_phase13_devres_tests = b.addRunArtifact(phase13_devres_tests);",
    'const phase13_devres_reviewability_tests = b.addTest(.{',
    '.name = "phase13-devres-reviewability-tests"',
    "const run_phase13_devres_reviewability_tests = b.addRunArtifact(phase13_devres_reviewability_tests);",
    'const phase13_devres_dma_coherent_tests = b.addTest(.{',
    '.name = "phase13-devres-dma-coherent-tests"',
    "const run_phase13_devres_dma_coherent_tests = b.addRunArtifact(phase13_devres_dma_coherent_tests);",
    'const phase13_devres_boundary_evidence_tests = b.addTest(.{',
    '.name = "phase13-devres-boundary-evidence-tests"',
    "const run_phase13_devres_boundary_evidence_tests = b.addRunArtifact(phase13_devres_boundary_evidence_tests);",
    'const phase13_landlock_ruleset_tests = b.addTest(.{',
    '.name = "phase13-landlock-ruleset-tests"',
    "const run_phase13_landlock_ruleset_tests = b.addRunArtifact(phase13_landlock_ruleset_tests);",
    'const phase13_landlock_syscalls_tests = b.addTest(.{',
    '.name = "phase13-landlock-syscalls-tests"',
    "const run_phase13_landlock_syscalls_tests = b.addRunArtifact(phase13_landlock_syscalls_tests);",
    'const phase13_libfs_reviewability_tests = b.addTest(.{',
    '.name = "phase13-libfs-reviewability-tests"',
    "const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);",
]

MAKE_REQUIRED_LINES = [
    "phase13-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py",
    "phase13: phase13-validate phase13-test",
]

MAKE_FORBIDDEN_LINES = [
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
]

WORKFLOW_REQUIRED_MARKERS = [
    "Validate Phase 13 release-discipline packet",
    "run: make -C zigux phase13-validate",
    "Run Phase 13 shared helper tests",
    "run: make -C zigux phase13-test",
]

WORKFLOW_EXACT_COUNTS = {
    "Validate Phase 13 release-discipline packet": 1,
    "run: make -C zigux phase13-validate": 1,
    "Run Phase 13 shared helper tests": 1,
    "run: make -C zigux phase13-test": 1,
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _collect_missing_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def _collect_exact_count_issues(text: str, counts: dict[str, int], prefix: str) -> list[str]:
    issues: list[str] = []
    for needle, expected in counts.items():
        actual = text.count(needle)
        if actual != expected:
            issues.append(f"{prefix}:{needle}:expected={expected}:actual={actual}")
    return issues


def _repeat_markers(markers: list[str], exact_counts: dict[str, int]) -> str:
    entries = list(markers)
    for needle, expected in exact_counts.items():
        extra = expected - entries.count(needle)
        if extra > 0:
            entries.extend([needle] * extra)
    return "\n".join(entries) + "\n"


def _baseline_scripts_readme() -> str:
    return _repeat_markers(SCRIPTS_REQUIRED_MARKERS, SCRIPTS_EXACT_COUNTS)


def _baseline_workflow() -> str:
    return "\n".join(
        (
            "- name: Validate Phase 13 release-discipline packet",
            "  run: make -C zigux phase13-validate",
            "- name: Run Phase 13 shared helper tests",
            "  run: make -C zigux phase13-test",
            "",
        )
    )


def _baseline_makefile() -> str:
    return "\n".join(MAKE_REQUIRED_LINES) + "\n"


def _baseline_phase13_build() -> str:
    return "\n".join(
        (
            'const phase13_libfs_tests = b.addTest(.{',
            '.name = "phase13-libfs-tests",',
            '.root_source_file = b.path("phase13_libfs.zig"),',
            "});",
            "const run_phase13_libfs_tests = b.addRunArtifact(phase13_libfs_tests);",
            'const phase13_devres_tests = b.addTest(.{',
            '.name = "phase13-devres-tests",',
            '.root_source_file = b.path("phase13_devres.zig"),',
            "});",
            "const run_phase13_devres_tests = b.addRunArtifact(phase13_devres_tests);",
            'const phase13_devres_reviewability_tests = b.addTest(.{',
            '.name = "phase13-devres-reviewability-tests",',
            '.root_source_file = b.path("phase13_devres_reviewability.zig"),',
            "});",
            "const run_phase13_devres_reviewability_tests = b.addRunArtifact(phase13_devres_reviewability_tests);",
            'const phase13_devres_dma_coherent_tests = b.addTest(.{',
            '.name = "phase13-devres-dma-coherent-tests",',
            '.root_source_file = b.path("phase13_devres_dma_coherent.zig"),',
            "});",
            "const run_phase13_devres_dma_coherent_tests = b.addRunArtifact(phase13_devres_dma_coherent_tests);",
            'const phase13_devres_boundary_evidence_tests = b.addTest(.{',
            '.name = "phase13-devres-boundary-evidence-tests",',
            '.root_source_file = b.path("phase13_devres_boundary_evidence.zig"),',
            "});",
            "const run_phase13_devres_boundary_evidence_tests = b.addRunArtifact(phase13_devres_boundary_evidence_tests);",
            'const phase13_landlock_ruleset_tests = b.addTest(.{',
            '.name = "phase13-landlock-ruleset-tests",',
            '.root_source_file = b.path("phase13_landlock_ruleset.zig"),',
            "});",
            "const run_phase13_landlock_ruleset_tests = b.addRunArtifact(phase13_landlock_ruleset_tests);",
            'const phase13_landlock_syscalls_tests = b.addTest(.{',
            '.name = "phase13-landlock-syscalls-tests",',
            '.root_source_file = b.path("phase13_landlock_syscalls.zig"),',
            "});",
            "const run_phase13_landlock_syscalls_tests = b.addRunArtifact(phase13_landlock_syscalls_tests);",
            'const phase13_libfs_reviewability_tests = b.addTest(.{',
            '.name = "phase13-libfs-reviewability-tests",',
            '.root_source_file = b.path("phase13_libfs_reviewability.zig"),',
            "});",
            "const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);",
            "test_step.dependOn(&run_phase13_libfs_tests.step);",
            "test_step.dependOn(&run_phase13_devres_tests.step);",
            "test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
            "test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
            "test_step.dependOn(&run_phase13_devres_boundary_evidence_tests.step);",
            "test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);",
            "test_step.dependOn(&run_phase13_landlock_syscalls_tests.step);",
            "test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);",
            "",
        )
    )


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    docs_readme = _read(root / "Documentation/zigux/README.md")
    review_checklist = _read(root / "Documentation/zigux/review-checklist.md")
    release_notes = _read(root / "Documentation/zigux/phase13-release-notes-survey.md")
    roadmap_traceability = _read(root / "Documentation/zigux/phase13-roadmap-traceability.md")
    contributor_guide = _read(root / "Documentation/zigux/phase13-contributor-workflow-guide.md")
    contributor_surface_sync = _read(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md")
    tests_review_companion = _read(root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
    scripts_readme = _read(root / "scripts/zigux/README.md")
    tests_readme = _read(root / "zigux/tests/README.md")
    makefile = _read(root / "zigux/Makefile")
    workflow = _read(root / ".github/workflows/zigux-bootstrap.yml")
    phase13_build = _read(root / "zigux/tests/phase13_build.zig")

    issues.extend(_collect_missing_markers(docs_readme, DOC_REQUIRED_MARKERS, "docs-readme"))
    issues.extend(_collect_exact_count_issues(docs_readme, DOC_EXACT_COUNTS, "docs-readme-exact"))
    issues.extend(_collect_missing_markers(review_checklist, REVIEW_REQUIRED_MARKERS, "review-checklist"))
    issues.extend(_collect_exact_count_issues(review_checklist, REVIEW_EXACT_COUNTS, "review-checklist-exact"))
    issues.extend(_collect_missing_markers(release_notes, RELEASE_NOTES_REQUIRED_MARKERS, "release-notes"))
    issues.extend(_collect_exact_count_issues(release_notes, RELEASE_NOTES_EXACT_COUNTS, "release-notes-exact"))
    issues.extend(_collect_missing_markers(roadmap_traceability, ROADMAP_TRACEABILITY_REQUIRED_MARKERS, "roadmap-traceability"))
    issues.extend(_collect_exact_count_issues(roadmap_traceability, ROADMAP_TRACEABILITY_EXACT_COUNTS, "roadmap-traceability-exact"))
    issues.extend(_collect_missing_markers(contributor_guide, CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, "contributor-guide"))
    issues.extend(_collect_exact_count_issues(contributor_guide, CONTRIBUTOR_GUIDE_EXACT_COUNTS, "contributor-guide-exact"))
    issues.extend(_collect_missing_markers(contributor_surface_sync, CONTRIBUTOR_SYNC_REQUIRED_MARKERS, "contributor-surface-sync"))
    issues.extend(_collect_exact_count_issues(contributor_surface_sync, CONTRIBUTOR_SYNC_EXACT_COUNTS, "contributor-surface-sync-exact"))
    issues.extend(_collect_missing_markers(tests_review_companion, TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, "tests-review-companion"))
    issues.extend(_collect_exact_count_issues(tests_review_companion, TESTS_REVIEW_COMPANION_EXACT_COUNTS, "tests-review-companion-exact"))
    issues.extend(_collect_missing_markers(scripts_readme, SCRIPTS_REQUIRED_MARKERS, "scripts-readme"))
    issues.extend(_collect_exact_count_issues(scripts_readme, SCRIPTS_EXACT_COUNTS, "scripts-readme-exact"))
    issues.extend(_collect_missing_markers(tests_readme, TESTS_REQUIRED_MARKERS, "tests-readme"))
    issues.extend(_collect_exact_count_issues(tests_readme, TESTS_EXACT_COUNTS, "tests-readme-exact"))
    for line in MAKE_REQUIRED_LINES:
        if line not in makefile:
            issues.append(f"makefile:{line}")
    for line in MAKE_FORBIDDEN_LINES:
        if line in makefile:
            issues.append(f"makefile-forbidden:{line}")
    issues.extend(_collect_missing_markers(workflow, WORKFLOW_REQUIRED_MARKERS, "workflow"))
    issues.extend(_collect_exact_count_issues(workflow, WORKFLOW_EXACT_COUNTS, "workflow-exact"))
    issues.extend(_collect_missing_markers(phase13_build, PHASE13_BUILD_REQUIRED_MARKERS, "phase13-build-marker"))
    issues.extend(_collect_exact_count_issues(phase13_build, PHASE13_BUILD_EXACT_COUNTS, "phase13-build"))

    return issues


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if sorted(actual) != sorted(expected):
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for rel in REQUIRED_FILES:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel == "Documentation/zigux/README.md":
                _write(path, _repeat_markers(DOC_REQUIRED_MARKERS, DOC_EXACT_COUNTS))
            elif rel == "Documentation/zigux/review-checklist.md":
                _write(path, _repeat_markers(REVIEW_REQUIRED_MARKERS, REVIEW_EXACT_COUNTS))
            elif rel == "Documentation/zigux/phase13-release-notes-survey.md":
                _write(path, _repeat_markers(RELEASE_NOTES_REQUIRED_MARKERS, RELEASE_NOTES_EXACT_COUNTS))
            elif rel == "Documentation/zigux/phase13-roadmap-traceability.md":
                _write(path, _repeat_markers(ROADMAP_TRACEABILITY_REQUIRED_MARKERS, ROADMAP_TRACEABILITY_EXACT_COUNTS))
            elif rel == "Documentation/zigux/phase13-contributor-workflow-guide.md":
                _write(path, _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS))
            elif rel == "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md":
                _write(path, _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS))
            elif rel == "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md":
                _write(path, _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS))
            elif rel == "scripts/zigux/README.md":
                _write(path, _baseline_scripts_readme())
            elif rel == "zigux/tests/README.md":
                _write(path, _repeat_markers(TESTS_REQUIRED_MARKERS, TESTS_EXACT_COUNTS))
            elif rel == "zigux/Makefile":
                _write(path, _baseline_makefile())
            elif rel == ".github/workflows/zigux-bootstrap.yml":
                _write(path, _baseline_workflow())
            elif rel == "zigux/tests/phase13_build.zig":
                _write(path, _baseline_phase13_build())
            elif rel.endswith(".json"):
                _write(path, "{}\n")
            elif rel.endswith(".zig"):
                _write(path, "// stub\n")
            else:
                _write(path, "# stub\n")

        if validate(root):
            raise SystemExit(f"baseline_should_pass:{validate(root)}")
        case_count += 1

        docs_readme_path = root / "Documentation/zigux/README.md"
        docs_readme_path.write_text("\n".join(marker for marker in DOC_REQUIRED_MARKERS if marker != "zigux/helpers/list_view.zig") + "\n", encoding="utf-8")
        _assert_only(validate(root), ["docs-readme:zigux/helpers/list_view.zig"], "missing_docs_readme_list_view_marker_failed")
        _write(docs_readme_path, _repeat_markers(DOC_REQUIRED_MARKERS, DOC_EXACT_COUNTS))
        case_count += 1

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        review_checklist_path.write_text("\n".join(marker for marker in REVIEW_REQUIRED_MARKERS if marker != "include/zigux/abi.h") + "\n", encoding="utf-8")
        _assert_only(validate(root), ["review-checklist:include/zigux/abi.h"], "missing_review_checklist_exported_list_abi_marker_failed")
        _write(review_checklist_path, _repeat_markers(REVIEW_REQUIRED_MARKERS, REVIEW_EXACT_COUNTS))
        case_count += 1

        release_notes_path = root / "Documentation/zigux/phase13-release-notes-survey.md"
        release_notes_path.write_text("\n".join(marker for marker in RELEASE_NOTES_REQUIRED_MARKERS if marker != "The current Phase 13 packet still ships with no dedicated `Documentation/zigux/phase13-closure.md` note on `master`.") + "\n", encoding="utf-8")
        _assert_only(validate(root), ["release-notes:The current Phase 13 packet still ships with no dedicated `Documentation/zigux/phase13-closure.md` note on `master`.", "release-notes-exact:The current Phase 13 packet still ships with no dedicated `Documentation/zigux/phase13-closure.md` note on `master`.:expected=1:actual=0"], "missing_release_notes_closure_posture_failed")
        _write(release_notes_path, _repeat_markers(RELEASE_NOTES_REQUIRED_MARKERS, RELEASE_NOTES_EXACT_COUNTS))
        case_count += 1

        roadmap_traceability_path = root / "Documentation/zigux/phase13-roadmap-traceability.md"
        roadmap_traceability_path.write_text("\n".join(marker for marker in ROADMAP_TRACEABILITY_REQUIRED_MARKERS if marker != "the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work") + "\n", encoding="utf-8")
        _assert_only(validate(root), ["roadmap-traceability:the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work", "roadmap-traceability-exact:the current shipped Phase 13 packet still has no dedicated `Documentation/zigux/phase13-closure.md`, so `Documentation/zigux/phase13-release-notes-survey.md` plus this traceability note carry the active tranche posture for the existing work:expected=1:actual=0"], "missing_roadmap_traceability_closure_posture_failed")
        _write(roadmap_traceability_path, _repeat_markers(ROADMAP_TRACEABILITY_REQUIRED_MARKERS, ROADMAP_TRACEABILITY_EXACT_COUNTS))
        case_count += 1

        contributor_guide_path = root / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(_repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS).replace("Documentation/zigux/phase13-landlock-syscalls-governance.md\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["contributor-guide:Documentation/zigux/phase13-landlock-syscalls-governance.md"], "missing_contributor_guide_syscalls_governance_marker_failed")
        _write(contributor_guide_path, _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS))
        case_count += 1

        contributor_surface_sync_path = root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        contributor_surface_sync_path.write_text(_repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS).replace("zigux/tests/phase13_landlock_syscalls_manifest.json\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["contributor-surface-sync:zigux/tests/phase13_landlock_syscalls_manifest.json"], "missing_contributor_surface_sync_syscalls_manifest_marker_failed")
        _write(contributor_surface_sync_path, _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS))
        case_count += 1

        tests_readme_path = root / "zigux/tests/README.md"
        tests_readme_path.write_text(_repeat_markers(TESTS_REQUIRED_MARKERS, TESTS_EXACT_COUNTS).replace("the current eight-test shared-helper release packet\n", "the current seven-test shared-helper release packet\n", 1), encoding="utf-8")
        _assert_only(validate(root), ["tests-readme-exact:the current eight-test shared-helper release packet:expected=2:actual=1"], "tests_readme_eight_test_wording_guard_failed")
        _write(tests_readme_path, _repeat_markers(TESTS_REQUIRED_MARKERS, TESTS_EXACT_COUNTS))
        case_count += 1

        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_path.write_text("\n".join(marker for marker in SCRIPTS_REQUIRED_MARKERS if marker != "phase13_devres_boundary_evidence.zig") + "\n", encoding="utf-8")
        _assert_only(validate(root), ["scripts-readme:phase13_devres_boundary_evidence.zig", "scripts-readme-exact:phase13_devres_boundary_evidence.zig:expected=1:actual=0"], "missing_scripts_readme_boundary_evidence_marker_failed")
        _write(scripts_readme_path, _baseline_scripts_readme())
        case_count += 1

        scripts_readme_path.write_text(_baseline_scripts_readme().replace("the eight-test shared helper replay\n", "the seven-test shared helper replay\n", 1), encoding="utf-8")
        _assert_only(validate(root), ["scripts-readme:the eight-test shared helper replay", "scripts-readme-exact:the eight-test shared helper replay:expected=1:actual=0"], "scripts_readme_eight_test_wording_guard_failed")
        _write(scripts_readme_path, _baseline_scripts_readme())
        case_count += 1

        scripts_readme_path.write_text(_baseline_scripts_readme() + "phase13_devres_boundary_evidence.zig\n", encoding="utf-8")
        _assert_only(validate(root), ["scripts-readme-exact:phase13_devres_boundary_evidence.zig:expected=1:actual=2"], "scripts_readme_duplicate_boundary_evidence_guard_failed")
        _write(scripts_readme_path, _baseline_scripts_readme())
        case_count += 1

        scripts_readme_path.write_text(_baseline_scripts_readme() + "make -C zigux phase13-validate\n", encoding="utf-8")
        _assert_only(validate(root), ["scripts-readme-exact:make -C zigux phase13-validate:expected=1:actual=2"], "scripts_readme_duplicate_phase13_validate_route_failed")
        _write(scripts_readme_path, _baseline_scripts_readme())
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(_baseline_makefile().replace("\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-notifier-packet.py"], "missing_makefile_notifier_route_failed")
        _write(root / "zigux/Makefile", _baseline_makefile())
        case_count += 1

        workflow_path = root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(_baseline_workflow().replace("run: make -C zigux phase13-test\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["workflow:run: make -C zigux phase13-test", "workflow-exact:run: make -C zigux phase13-test:expected=1:actual=0"], "missing_workflow_phase13_test_route_failed")
        _write(workflow_path, _baseline_workflow())
        case_count += 1

        workflow_path.write_text(_baseline_workflow().replace("Validate Phase 13 release-discipline packet", "Validate Phase 13 release packet", 1), encoding="utf-8")
        _assert_only(validate(root), ["workflow:Validate Phase 13 release-discipline packet", "workflow-exact:Validate Phase 13 release-discipline packet:expected=1:actual=0"], "missing_workflow_phase13_validate_step_failed")
        _write(workflow_path, _baseline_workflow())
        case_count += 1

        phase13_build_path = root / "zigux/tests/phase13_build.zig"
        phase13_build_path.write_text(_baseline_phase13_build().replace("const phase13_devres_boundary_evidence_tests = b.addTest(.{\n.name = \"phase13-devres-boundary-evidence-tests\",\n.root_source_file = b.path(\"phase13_devres_boundary_evidence.zig\"),\n});\nconst run_phase13_devres_boundary_evidence_tests = b.addRunArtifact(phase13_devres_boundary_evidence_tests);\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["phase13-build: = b.addTest(.{:expected=8:actual=7", "phase13-build-marker:const phase13_devres_boundary_evidence_tests = b.addTest(.{", "phase13-build-marker:.name = \"phase13-devres-boundary-evidence-tests\"", "phase13-build-marker:const run_phase13_devres_boundary_evidence_tests = b.addRunArtifact(phase13_devres_boundary_evidence_tests);", "phase13-build:.root_source_file = b.path(\"phase13_devres_boundary_evidence.zig\"),:expected=1:actual=0"], "missing_phase13_build_boundary_evidence_markers_failed")
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        phase13_build_path.write_text(_baseline_phase13_build().replace("test_step.dependOn(&run_phase13_devres_boundary_evidence_tests.step);\n", "", 1), encoding="utf-8")
        _assert_only(validate(root), ["phase13-build:test_step.dependOn(&run_phase13_:expected=8:actual=7"], "missing_phase13_build_boundary_evidence_dependency_failed")
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        (root / "zigux/tests/phase13_devres_boundary_evidence.zig").unlink()
        _assert_only(validate(root), ["missing_file:zigux/tests/phase13_devres_boundary_evidence.zig"], "missing_devres_boundary_evidence_file_failed")
        _write(root / "zigux/tests/phase13_devres_boundary_evidence.zig", "// stub\n")
        case_count += 1

        (root / "scripts/zigux/check-phase13-notifier-packet.py").unlink()
        _assert_only(validate(root), ["missing_file:scripts/zigux/check-phase13-notifier-packet.py"], "missing_notifier_checker_file_failed")
        _write(root / "scripts/zigux/check-phase13-notifier-packet.py", "# stub\n")
        case_count += 1

        (root / "scripts/zigux/check-phase13-landlock-ruleset-packet.py").unlink()
        _assert_only(validate(root), ["missing_file:scripts/zigux/check-phase13-landlock-ruleset-packet.py"], "missing_landlock_checker_file_failed")
        _write(root / "scripts/zigux/check-phase13-landlock-ruleset-packet.py", "# stub\n")
        case_count += 1

        (root / "Documentation/zigux/phase13-shared-helper-lane-sequencing.md").unlink()
        _assert_only(validate(root), ["missing_file:Documentation/zigux/phase13-shared-helper-lane-sequencing.md"], "missing_shared_helper_lane_sequencing_file_failed")
        _write(root / "Documentation/zigux/phase13-shared-helper-lane-sequencing.md", "# stub\n")
        case_count += 1

        (root / "Documentation/zigux/phase13-landlock-ruleset-ownership.md").unlink()
        _assert_only(validate(root), ["missing_file:Documentation/zigux/phase13-landlock-ruleset-ownership.md"], "missing_landlock_ruleset_ownership_file_failed")
        _write(root / "Documentation/zigux/phase13-landlock-ruleset-ownership.md", "# stub\n")
        case_count += 1

        (root / "Documentation/zigux/phase13-landlock-syscalls-governance.md").unlink()
        _assert_only(validate(root), ["missing_file:Documentation/zigux/phase13-landlock-syscalls-governance.md"], "missing_landlock_syscalls_governance_file_failed")
        _write(root / "Documentation/zigux/phase13-landlock-syscalls-governance.md", "# stub\n")
        case_count += 1

        (root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig").unlink()
        _assert_only(validate(root), ["missing_file:zigux/tests/phase13_landlock_syscalls_reviewability.zig"], "missing_landlock_reviewability_file_failed")
        _write(root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig", "// stub\n")
        case_count += 1

        (root / "drivers/tty/hvc/hvc_console.h").unlink()
        _assert_only(validate(root), ["missing_file:drivers/tty/hvc/hvc_console.h"], "missing_hvc_console_header_file_failed")
        _write(root / "drivers/tty/hvc/hvc_console.h", "# stub\n")
        case_count += 1

    print("PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current shipped Phase 13 release packet surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE13_RELEASE_VALIDATION=fail")
        print("PHASE13_RELEASE_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE13_RELEASE_VALIDATION_ISSUES_END")
        return 1

    marker_total = (
        len(REQUIRED_FILES)
        + len(DOC_REQUIRED_MARKERS)
        + len(REVIEW_REQUIRED_MARKERS)
        + len(RELEASE_NOTES_REQUIRED_MARKERS)
        + len(ROADMAP_TRACEABILITY_REQUIRED_MARKERS)
        + len(DOC_EXACT_COUNTS)
        + len(REVIEW_EXACT_COUNTS)
        + len(RELEASE_NOTES_EXACT_COUNTS)
        + len(ROADMAP_TRACEABILITY_EXACT_COUNTS)
        + len(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS)
        + len(CONTRIBUTOR_GUIDE_EXACT_COUNTS)
        + len(CONTRIBUTOR_SYNC_REQUIRED_MARKERS)
        + len(CONTRIBUTOR_SYNC_EXACT_COUNTS)
        + len(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS)
        + len(TESTS_REVIEW_COMPANION_EXACT_COUNTS)
        + len(SCRIPTS_REQUIRED_MARKERS)
        + len(SCRIPTS_EXACT_COUNTS)
        + len(TESTS_REQUIRED_MARKERS)
        + len(TESTS_EXACT_COUNTS)
        + len(MAKE_REQUIRED_LINES)
        + len(WORKFLOW_REQUIRED_MARKERS)
        + len(WORKFLOW_EXACT_COUNTS)
        + len(PHASE13_BUILD_EXACT_COUNTS)
        + len(PHASE13_BUILD_REQUIRED_MARKERS)
    )
    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_VALIDATION_MARKER_COUNT={marker_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
