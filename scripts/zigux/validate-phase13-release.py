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
    "Documentation/zigux/phase13-libfs-slice.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
]

DOC_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "the current seven-test shared-helper release packet",
]

REVIEW_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "the same validator-first seven-test shared-helper release packet",
]

DOC_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "the current seven-test shared-helper release packet": 1,
}

REVIEW_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 1,
    "zigux/tests/phase13_notifier_list_manifest.json": 1,
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "the same validator-first seven-test shared-helper release packet": 1,
}

CONTRIBUTOR_GUIDE_REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
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
    "zigux/tests/phase13_notifier_list_manifest.json": 2,
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
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
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
    "zigux/bindings/notifier_abi.zig": 1,
    "include/zigux/notifier_abi.h": 1,
    "zigux/helpers/notifier_chain_view.zig": 1,
    "shared validator-first replay route separate from the broader shipped adjacent release-surface evidence": 1,
    "extra replay steps": 1,
}

TESTS_REVIEW_COMPANION_REQUIRED_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
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
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "include/zigux/notifier_abi.h",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/validate-phase13-release.py",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "same shipped validator-first release path",
    "extra Phase 13 checker or replay surfaces that are not on `master`",
]

TESTS_REVIEW_COMPANION_EXACT_COUNTS = {
    "Documentation/zigux/phase13-notifier-list-survey.md": 2,
    "zigux/tests/phase13_notifier_list_manifest.json": 3,
    "include/zigux/notifier_abi.h": 3,
    "zigux/bindings/notifier_abi.zig": 3,
    "zigux/helpers/notifier_chain_view.zig": 3,
    "same shipped validator-first release path": 1,
    "extra Phase 13 checker or replay surfaces that are not on `master`": 2,
}

SCRIPTS_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "zigux/tests/phase13_build.zig",
    "phase13_libfs.zig",
    "phase13_devres.zig",
    "phase13_devres_reviewability.zig",
    "phase13_devres_dma_coherent.zig",
    "phase13_landlock_ruleset.zig",
    "phase13_landlock_syscalls.zig",
    "phase13_libfs_reviewability.zig",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "the seven-test shared helper replay",
    "adjacent review evidence instead of adding extra shared replay steps on `master`",
]

TESTS_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/validate-phase13-release.py",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "the current seven-test shared-helper release packet",
    "adjacent release-surface evidence rather than extra shared replay steps",
]

PHASE13_BUILD_EXACT_COUNTS = {
    " = b.addTest(.{": 7,
    "test_step.dependOn(&run_phase13_": 7,
    '.root_source_file = b.path("phase13_libfs.zig"),': 1,
    '.root_source_file = b.path("phase13_devres.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_reviewability.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_dma_coherent.zig"),': 1,
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
    "phase13: phase13-validate phase13-test",
]

MAKE_FORBIDDEN_LINES = [
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
]


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


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    docs_readme = _read(root / "Documentation/zigux/README.md")
    review_checklist = _read(root / "Documentation/zigux/review-checklist.md")
    contributor_workflow_guide = _read(root / "Documentation/zigux/phase13-contributor-workflow-guide.md")
    contributor_surface_sync = _read(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md")
    tests_review_companion = _read(root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
    scripts_readme = _read(root / "scripts/zigux/README.md")
    tests_readme = _read(root / "zigux/tests/README.md")
    makefile = _read(root / "zigux/Makefile")
    phase13_build = _read(root / "zigux/tests/phase13_build.zig")

    issues.extend(_collect_missing_markers(docs_readme, DOC_REQUIRED_MARKERS, "docs-readme"))
    issues.extend(_collect_missing_markers(review_checklist, REVIEW_REQUIRED_MARKERS, "review-checklist"))
    issues.extend(_collect_exact_count_issues(docs_readme, DOC_EXACT_COUNTS, "docs-readme-exact"))
    issues.extend(_collect_exact_count_issues(review_checklist, REVIEW_EXACT_COUNTS, "review-checklist-exact"))
    issues.extend(_collect_missing_markers(contributor_workflow_guide, CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, "contributor-workflow-guide"))
    issues.extend(_collect_exact_count_issues(contributor_workflow_guide, CONTRIBUTOR_GUIDE_EXACT_COUNTS, "contributor-workflow-guide-exact"))
    issues.extend(_collect_missing_markers(contributor_surface_sync, CONTRIBUTOR_SYNC_REQUIRED_MARKERS, "contributor-surface-sync"))
    issues.extend(_collect_exact_count_issues(contributor_surface_sync, CONTRIBUTOR_SYNC_EXACT_COUNTS, "contributor-surface-sync-exact"))
    issues.extend(_collect_missing_markers(tests_review_companion, TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, "tests-review-companion"))
    issues.extend(_collect_exact_count_issues(tests_review_companion, TESTS_REVIEW_COMPANION_EXACT_COUNTS, "tests-review-companion-exact"))
    issues.extend(_collect_missing_markers(scripts_readme, SCRIPTS_REQUIRED_MARKERS, "scripts-readme"))
    issues.extend(_collect_missing_markers(tests_readme, TESTS_REQUIRED_MARKERS, "tests-readme"))
    issues.extend(_collect_missing_markers(makefile, MAKE_REQUIRED_LINES, "makefile"))
    issues.extend(_collect_exact_count_issues(phase13_build, PHASE13_BUILD_EXACT_COUNTS, "phase13-build"))
    issues.extend(_collect_missing_markers(phase13_build, PHASE13_BUILD_REQUIRED_MARKERS, "phase13-build-marker"))
    for forbidden in MAKE_FORBIDDEN_LINES:
        if forbidden in makefile:
            issues.append(f"makefile:forbidden_route:{forbidden}")
    return issues


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "phase13-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
            "",
            "phase13-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase13_build.zig",
            "",
            "phase13: phase13-validate phase13-test",
            "",
        )
    )


def _baseline_phase13_build() -> str:
    return "\n".join(
        (
            "const phase13_libfs_tests = b.addTest(.{",
            '.name = "phase13-libfs-tests",',
            "});",
            "const run_phase13_libfs_tests = b.addRunArtifact(phase13_libfs_tests);",
            "const phase13_devres_tests = b.addTest(.{",
            '.name = "phase13-devres-tests",',
            "});",
            "const run_phase13_devres_tests = b.addRunArtifact(phase13_devres_tests);",
            "const phase13_devres_reviewability_tests = b.addTest(.{",
            '.name = "phase13-devres-reviewability-tests",',
            "});",
            "const run_phase13_devres_reviewability_tests = b.addRunArtifact(phase13_devres_reviewability_tests);",
            "const phase13_devres_dma_coherent_tests = b.addTest(.{",
            '.name = "phase13-devres-dma-coherent-tests",',
            "});",
            "const run_phase13_devres_dma_coherent_tests = b.addRunArtifact(phase13_devres_dma_coherent_tests);",
            "const phase13_landlock_ruleset_tests = b.addTest(.{",
            '.name = "phase13-landlock-ruleset-tests",',
            "});",
            "const run_phase13_landlock_ruleset_tests = b.addRunArtifact(phase13_landlock_ruleset_tests);",
            "const phase13_landlock_syscalls_tests = b.addTest(.{",
            '.name = "phase13-landlock-syscalls-tests",',
            "});",
            "const run_phase13_landlock_syscalls_tests = b.addRunArtifact(phase13_landlock_syscalls_tests);",
            "const phase13_libfs_reviewability_tests = b.addTest(.{",
            '.name = "phase13-libfs-reviewability-tests",',
            "});",
            "const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);",
            "test_step.dependOn(&run_phase13_libfs_tests.step);",
            "test_step.dependOn(&run_phase13_devres_tests.step);",
            "test_step.dependOn(&run_phase13_devres_reviewability_tests.step);",
            "test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);",
            "test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);",
            "test_step.dependOn(&run_phase13_landlock_syscalls_tests.step);",
            "test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);",
            '.root_source_file = b.path("phase13_libfs.zig"),',
            '.root_source_file = b.path("phase13_devres.zig"),',
            '.root_source_file = b.path("phase13_devres_reviewability.zig"),',
            '.root_source_file = b.path("phase13_devres_dma_coherent.zig"),',
            '.root_source_file = b.path("phase13_landlock_ruleset.zig"),',
            '.root_source_file = b.path("phase13_landlock_syscalls.zig"),',
            '.root_source_file = b.path("phase13_libfs_reviewability.zig"),',
            "",
        )
    )


def _baseline_contributor_workflow_guide() -> str:
    return "\n".join(
        (
            "Documentation/zigux/README.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "zigux/tests/README.md",
            "scripts/zigux/README.md",
            "scripts/zigux/validate-phase13-release.py",
            "scripts/zigux/check-phase13-devres-packet.py",
            "zigux/Makefile",
            "zigux/tests/phase13_build.zig",
            "Documentation/zigux/phase13-release-notes-survey.md",
            "Documentation/zigux/phase13-roadmap-traceability.md",
            "Documentation/zigux/phase13-notifier-list-survey.md",
            "zigux/tests/phase13_notifier_list_manifest.json",
            "zigux/bindings/notifier_abi.zig",
            "include/zigux/notifier_abi.h",
            "zigux/helpers/notifier_chain_view.zig",
            "adjacent shipped release-surface evidence",
            "Documentation/zigux/phase13-release-notes-survey.md",
            "Documentation/zigux/phase13-roadmap-traceability.md",
            "Documentation/zigux/phase13-notifier-list-survey.md",
            "zigux/tests/phase13_notifier_list_manifest.json",
            "zigux/bindings/notifier_abi.zig",
            "include/zigux/notifier_abi.h",
            "zigux/helpers/notifier_chain_view.zig",
            "adjacent shipped release-surface evidence",
            "they do not add extra shared replay steps beyond the validator-first route above",
            "the Phase 13 release packet stays active until the shared replay and the remaining blocker posture say otherwise together",
            "",
        )
    )

def _baseline_tests_review_companion() -> str:
    return "\n".join(
        TESTS_REVIEW_COMPANION_REQUIRED_MARKERS
        + [
            "Documentation/zigux/phase13-notifier-list-survey.md",
            "zigux/tests/phase13_notifier_list_manifest.json",
            "zigux/tests/phase13_notifier_list_manifest.json",
            "include/zigux/notifier_abi.h",
            "include/zigux/notifier_abi.h",
            "zigux/bindings/notifier_abi.zig",
            "zigux/bindings/notifier_abi.zig",
            "zigux/helpers/notifier_chain_view.zig",
            "zigux/helpers/notifier_chain_view.zig",
            "extra Phase 13 checker or replay surfaces that are not on `master`",
            "",
        ]
    )


def _seed_fixture_tree(root: Path) -> None:
    _write(root / "Documentation/zigux/README.md", "\n".join(DOC_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/phase13-release-notes-survey.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-roadmap-traceability.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-notifier-list-survey.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", _baseline_contributor_workflow_guide())
    _write(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md", "\n".join(CONTRIBUTOR_SYNC_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", _baseline_tests_review_companion())
    _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/README.md", "\n".join(TESTS_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/Makefile", _baseline_makefile())
    _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
    for rel in REQUIRED_FILES:
        if rel in {
            "Documentation/zigux/README.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/phase13-release-notes-survey.md",
            "Documentation/zigux/phase13-roadmap-traceability.md",
            "Documentation/zigux/phase13-notifier-list-survey.md",
            "Documentation/zigux/phase13-contributor-workflow-guide.md",
            "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "scripts/zigux/README.md",
            "zigux/tests/README.md",
            "zigux/Makefile",
            "zigux/tests/phase13_build.zig",
        }:
            continue
        stub = "{}\n" if rel.endswith(".json") else "// stub\n"
        if rel.endswith(".md"):
            stub = "# stub\n"
        if rel.endswith(".py"):
            stub = "# stub\n"
        _write(root / rel, stub)


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_fixture_tree(root)

        baseline_makefile = _baseline_makefile()

        issues = validate(root)
        if issues:
            raise AssertionError(f"baseline fixture should pass, got {issues!r}")
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        original_makefile = _read(makefile_path)
        makefile_path.write_text(
            baseline_makefile + "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-release-replay-exact-counts.py\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["makefile:forbidden_route:scripts/zigux/check-phase13-release-replay-exact-counts.py"],
            "forbidden_makefile_route_guard_failed",
        )
        makefile_path.write_text(baseline_makefile, encoding="utf-8")
        case_count += 1

        _write(root / "zigux/Makefile", "phase13-test:\n\t@true\n")
        _assert_only(
            validate(root),
            [
                "makefile:phase13-validate:",
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
                "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet.py",
                "makefile:phase13: phase13-validate phase13-test",
            ],
            "missing_makefile_marker_guard_failed",
        )
        _write(root / "zigux/Makefile", baseline_makefile)
        case_count += 1

        docs_readme_path = root / "Documentation/zigux/README.md"
        docs_readme_path.write_text("Documentation/zigux/phase13-release-notes-survey.md\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "docs-readme:Documentation/zigux/phase13-roadmap-traceability.md",
                "docs-readme:Documentation/zigux/phase13-contributor-workflow-guide.md",
                "docs-readme:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
                "docs-readme:Documentation/zigux/phase13-notifier-list-survey.md",
                "docs-readme:zigux/tests/phase13_notifier_list_manifest.json",
                "docs-readme:zigux/bindings/notifier_abi.zig",
                "docs-readme:zigux/tests/phase13_devres_dma_coherent.zig",
                "docs-readme:include/zigux/notifier_abi.h",
                "docs-readme:zigux/helpers/notifier_chain_view.zig",
                "docs-readme:the current seven-test shared-helper release packet",
                "docs-readme-exact:Documentation/zigux/phase13-notifier-list-survey.md:expected=1:actual=0",
                "docs-readme-exact:zigux/tests/phase13_notifier_list_manifest.json:expected=1:actual=0",
                "docs-readme-exact:zigux/bindings/notifier_abi.zig:expected=1:actual=0",
                "docs-readme-exact:include/zigux/notifier_abi.h:expected=1:actual=0",
                "docs-readme-exact:zigux/helpers/notifier_chain_view.zig:expected=1:actual=0",
                "docs-readme-exact:the current seven-test shared-helper release packet:expected=1:actual=0",
            ],
            "docs_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/README.md", "\n".join(DOC_REQUIRED_MARKERS) + "\n")
        case_count += 1

        docs_readme_path.write_text(
            "\n".join(DOC_REQUIRED_MARKERS + ["include/zigux/notifier_abi.h"]) + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["docs-readme-exact:include/zigux/notifier_abi.h:expected=1:actual=2"],
            "docs_exact_count_guard_failed",
        )
        _write(root / "Documentation/zigux/README.md", "\n".join(DOC_REQUIRED_MARKERS) + "\n")
        case_count += 1

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        review_checklist_path.write_text("Documentation/zigux/phase13-release-notes-survey.md\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "review-checklist:Documentation/zigux/phase13-roadmap-traceability.md",
                "review-checklist:Documentation/zigux/phase13-contributor-workflow-guide.md",
                "review-checklist:Documentation/zigux/phase13-notifier-list-survey.md",
                "review-checklist:zigux/tests/phase13_notifier_list_manifest.json",
                "review-checklist:zigux/bindings/notifier_abi.zig",
                "review-checklist:zigux/tests/phase13_devres_dma_coherent.zig",
                "review-checklist:include/zigux/notifier_abi.h",
                "review-checklist:zigux/helpers/notifier_chain_view.zig",
                "review-checklist:the same validator-first seven-test shared-helper release packet",
                "review-checklist-exact:Documentation/zigux/phase13-notifier-list-survey.md:expected=1:actual=0",
                "review-checklist-exact:zigux/tests/phase13_notifier_list_manifest.json:expected=1:actual=0",
                "review-checklist-exact:zigux/bindings/notifier_abi.zig:expected=1:actual=0",
                "review-checklist-exact:include/zigux/notifier_abi.h:expected=1:actual=0",
                "review-checklist-exact:zigux/helpers/notifier_chain_view.zig:expected=1:actual=0",
                "review-checklist-exact:the same validator-first seven-test shared-helper release packet:expected=1:actual=0",
            ],
            "review_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
        case_count += 1

        review_checklist_path.write_text(
            "\n".join(REVIEW_REQUIRED_MARKERS + ["zigux/helpers/notifier_chain_view.zig"]) + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["review-checklist-exact:zigux/helpers/notifier_chain_view.zig:expected=1:actual=2"],
            "review_exact_count_guard_failed",
        )
        _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
        case_count += 1

        contributor_workflow_guide_path = root / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_workflow_guide_path.write_text(
            _baseline_contributor_workflow_guide().replace("zigux/tests/README.md\n", "", 1),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide:zigux/tests/README.md"],
            "contributor_workflow_guide_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", _baseline_contributor_workflow_guide())
        case_count += 1

        contributor_workflow_guide_path.write_text(
            _baseline_contributor_workflow_guide() + "zigux/helpers/notifier_chain_view.zig\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide-exact:zigux/helpers/notifier_chain_view.zig:expected=2:actual=3"],
            "contributor_workflow_guide_exact_count_guard_failed",
        )
        _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", _baseline_contributor_workflow_guide())
        case_count += 1

        contributor_surface_sync_path = root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        contributor_surface_sync_path.write_text("Documentation/zigux/README.md\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "contributor-surface-sync:Documentation/zigux/review-checklist.md",
                "contributor-surface-sync:Documentation/zigux/phase13-contributor-workflow-guide.md",
                "contributor-surface-sync:Documentation/zigux/phase13-release-notes-survey.md",
                "contributor-surface-sync:Documentation/zigux/phase13-roadmap-traceability.md",
                "contributor-surface-sync:Documentation/zigux/phase13-notifier-list-survey.md",
                "contributor-surface-sync:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
                "contributor-surface-sync:zigux/tests/README.md",
                "contributor-surface-sync:zigux/tests/phase13_notifier_list_manifest.json",
                "contributor-surface-sync:zigux/bindings/notifier_abi.zig",
                "contributor-surface-sync:include/zigux/notifier_abi.h",
                "contributor-surface-sync:zigux/helpers/notifier_chain_view.zig",
                "contributor-surface-sync:scripts/zigux/check-phase13-devres-packet.py",
                "contributor-surface-sync:scripts/zigux/validate-phase13-release.py",
                "contributor-surface-sync:zigux/Makefile",
                "contributor-surface-sync:shared validator-first replay route separate from the broader shipped adjacent release-surface evidence",
                "contributor-surface-sync:extra replay steps",
                "contributor-surface-sync-exact:Documentation/zigux/phase13-release-notes-survey.md:expected=1:actual=0",
                "contributor-surface-sync-exact:Documentation/zigux/phase13-roadmap-traceability.md:expected=1:actual=0",
                "contributor-surface-sync-exact:Documentation/zigux/phase13-notifier-list-survey.md:expected=1:actual=0",
                "contributor-surface-sync-exact:zigux/tests/phase13_notifier_list_manifest.json:expected=1:actual=0",
                "contributor-surface-sync-exact:zigux/bindings/notifier_abi.zig:expected=1:actual=0",
                "contributor-surface-sync-exact:include/zigux/notifier_abi.h:expected=1:actual=0",
                "contributor-surface-sync-exact:zigux/helpers/notifier_chain_view.zig:expected=1:actual=0",
                "contributor-surface-sync-exact:shared validator-first replay route separate from the broader shipped adjacent release-surface evidence:expected=1:actual=0",
                "contributor-surface-sync-exact:extra replay steps:expected=1:actual=0",
            ],
            "contributor_surface_sync_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md", "\n".join(CONTRIBUTOR_SYNC_REQUIRED_MARKERS) + "\n")
        case_count += 1

        contributor_surface_sync_path.write_text(
            "\n".join(CONTRIBUTOR_SYNC_REQUIRED_MARKERS + ["extra replay steps"]) + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-surface-sync-exact:extra replay steps:expected=1:actual=2"],
            "contributor_surface_sync_exact_count_guard_failed",
        )
        _write(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md", "\n".join(CONTRIBUTOR_SYNC_REQUIRED_MARKERS) + "\n")
        case_count += 1

        tests_review_companion_path = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        tests_review_companion_path.write_text("Documentation/zigux/README.md\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "tests-review-companion:Documentation/zigux/phase13-contributor-workflow-guide.md",
                "tests-review-companion:Documentation/zigux/phase13-release-notes-survey.md",
                "tests-review-companion:Documentation/zigux/phase13-roadmap-traceability.md",
                "tests-review-companion:Documentation/zigux/phase13-notifier-list-survey.md",
                "tests-review-companion:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
                "tests-review-companion:Documentation/zigux/review-checklist.md",
                "tests-review-companion:zigux/tests/phase13_build.zig",
                "tests-review-companion:zigux/tests/phase13_libfs_manifest.json",
                "tests-review-companion:zigux/tests/phase13_devres_manifest.json",
                "tests-review-companion:zigux/tests/phase13_landlock_ruleset_manifest.json",
                "tests-review-companion:zigux/tests/phase13_landlock_syscalls_manifest.json",
                "tests-review-companion:zigux/tests/phase13_notifier_list_manifest.json",
                "tests-review-companion:zigux/tests/phase13_libfs_reviewability.zig",
                "tests-review-companion:zigux/tests/phase13_devres_reviewability.zig",
                "tests-review-companion:zigux/tests/phase13_devres_dma_coherent.zig",
                "tests-review-companion:zigux/tests/phase13_landlock_ruleset.zig",
                "tests-review-companion:zigux/tests/phase13_landlock_syscalls.zig",
                "tests-review-companion:include/zigux/notifier_abi.h",
                "tests-review-companion:zigux/bindings/notifier_abi.zig",
                "tests-review-companion:zigux/helpers/notifier_chain_view.zig",
                "tests-review-companion:scripts/zigux/check-phase13-devres-packet.py",
                "tests-review-companion:scripts/zigux/validate-phase13-release.py",
                "tests-review-companion:make -C zigux phase13-validate",
                "tests-review-companion:make -C zigux phase13",
                "tests-review-companion:same shipped validator-first release path",
                "tests-review-companion:extra Phase 13 checker or replay surfaces that are not on `master`",
                "tests-review-companion-exact:Documentation/zigux/phase13-notifier-list-survey.md:expected=2:actual=0",
                "tests-review-companion-exact:zigux/tests/phase13_notifier_list_manifest.json:expected=3:actual=0",
                "tests-review-companion-exact:include/zigux/notifier_abi.h:expected=3:actual=0",
                "tests-review-companion-exact:zigux/bindings/notifier_abi.zig:expected=3:actual=0",
                "tests-review-companion-exact:zigux/helpers/notifier_chain_view.zig:expected=3:actual=0",
                "tests-review-companion-exact:same shipped validator-first release path:expected=1:actual=0",
                "tests-review-companion-exact:extra Phase 13 checker or replay surfaces that are not on `master`:expected=2:actual=0",
            ],
            "tests_review_companion_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", _baseline_tests_review_companion())
        case_count += 1

        tests_review_companion_path.write_text(
            _baseline_tests_review_companion() + "same shipped validator-first release path\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-review-companion-exact:same shipped validator-first release path:expected=1:actual=2"],
            "tests_review_companion_exact_count_guard_failed",
        )
        _write(root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", _baseline_tests_review_companion())
        case_count += 1

        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_path.write_text("validate-phase13-release.py\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "scripts-readme:Documentation/zigux/phase13-release-notes-survey.md",
                "scripts-readme:Documentation/zigux/phase13-roadmap-traceability.md",
                "scripts-readme:Documentation/zigux/phase13-notifier-list-survey.md",
                "scripts-readme:zigux/tests/phase13_notifier_list_manifest.json",
                "scripts-readme:zigux/bindings/notifier_abi.zig",
                "scripts-readme:include/zigux/notifier_abi.h",
                "scripts-readme:zigux/helpers/notifier_chain_view.zig",
                "scripts-readme:check-phase13-devres-packet.py",
                "scripts-readme:zigux/tests/phase13_build.zig",
                "scripts-readme:phase13_libfs.zig",
                "scripts-readme:phase13_devres.zig",
                "scripts-readme:phase13_devres_reviewability.zig",
                "scripts-readme:phase13_devres_dma_coherent.zig",
                "scripts-readme:phase13_landlock_ruleset.zig",
                "scripts-readme:phase13_landlock_syscalls.zig",
                "scripts-readme:phase13_libfs_reviewability.zig",
                "scripts-readme:make -C zigux phase13-validate",
                "scripts-readme:make -C zigux phase13",
                "scripts-readme:the seven-test shared helper replay",
                "scripts-readme:adjacent review evidence instead of adding extra shared replay steps on `master`",
            ],
            "scripts_marker_guard_failed",
        )
        _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        tests_readme_path = root / "zigux/tests/README.md"
        tests_readme_path.write_text("Documentation/zigux/phase13-release-notes-survey.md\n", encoding="utf-8")
        _assert_only(
            validate(root),
            [
                "tests-readme:Documentation/zigux/phase13-roadmap-traceability.md",
                "tests-readme:Documentation/zigux/phase13-notifier-list-survey.md",
                "tests-readme:zigux/tests/phase13_notifier_list_manifest.json",
                "tests-readme:zigux/bindings/notifier_abi.zig",
                "tests-readme:include/zigux/notifier_abi.h",
                "tests-readme:zigux/helpers/notifier_chain_view.zig",
                "tests-readme:scripts/zigux/check-phase13-devres-packet.py",
                "tests-readme:scripts/zigux/validate-phase13-release.py",
                "tests-readme:make -C zigux phase13-validate",
                "tests-readme:make -C zigux phase13",
                "tests-readme:the current seven-test shared-helper release packet",
                "tests-readme:adjacent release-surface evidence rather than extra shared replay steps",
            ],
            "tests_marker_guard_failed",
        )
        _write(root / "zigux/tests/README.md", "\n".join(TESTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        phase13_build_path = root / "zigux/tests/phase13_build.zig"
        phase13_build_path.write_text(_baseline_phase13_build() + "const phase13_extra_tests = b.addTest(.{\n});\n", encoding="utf-8")
        _assert_only(
            validate(root),
            ["phase13-build: = b.addTest(.{:expected=7:actual=8"],
            "phase13_build_test_count_guard_failed",
        )
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        phase13_build_path.write_text(
            _baseline_phase13_build() + "test_step.dependOn(&run_phase13_extra_tests.step);\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["phase13-build:test_step.dependOn(&run_phase13_:expected=7:actual=8"],
            "phase13_build_dependency_count_guard_failed",
        )
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        phase13_build_path.write_text(
            _baseline_phase13_build().replace(
                '.root_source_file = b.path("phase13_libfs_reviewability.zig"),\n',
                '.root_source_file = b.path("phase13_devres.zig"),\n',
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                'phase13-build:.root_source_file = b.path("phase13_devres.zig"),:expected=1:actual=2',
                'phase13-build:.root_source_file = b.path("phase13_libfs_reviewability.zig"),:expected=1:actual=0',
            ],
            "phase13_build_root_source_file_guard_failed",
        )
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        phase13_build_path.write_text(
            _baseline_phase13_build().replace(
                "const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);\n",
                "",
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "phase13-build-marker:const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);",
            ],
            "phase13_build_named_run_artifact_guard_failed",
        )
        _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())
        case_count += 1

        (root / "Documentation/zigux/phase13-contributor-workflow-guide.md").unlink()
        _assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase13-contributor-workflow-guide.md"],
            "missing_contributor_workflow_guide_guard_failed",
        )
        _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", _baseline_contributor_workflow_guide())
        case_count += 1

        (root / "Documentation/zigux/phase13-landlock-syscalls-survey.md").unlink()
        _assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase13-landlock-syscalls-survey.md"],
            "missing_landlock_syscalls_survey_guard_failed",
        )
        _write(root / "Documentation/zigux/phase13-landlock-syscalls-survey.md", "# stub\n")
        case_count += 1

        (root / "include/zigux/notifier_abi.h").unlink()
        _assert_only(
            validate(root),
            ["missing_file:include/zigux/notifier_abi.h"],
            "missing_notifier_header_guard_failed",
        )
        _write(root / "include/zigux/notifier_abi.h", "// stub\n")
        case_count += 1

        (root / "zigux/tests/phase13_devres_manifest.json").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_devres_manifest.json"],
            "missing_devres_manifest_guard_failed",
        )
        _write(root / "zigux/tests/phase13_devres_manifest.json", "{}\n")
        case_count += 1

        (root / "zigux/tests/phase13_notifier_list_reviewability.zig").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_notifier_list_reviewability.zig"],
            "missing_notifier_reviewability_guard_failed",
        )
        _write(root / "zigux/tests/phase13_notifier_list_reviewability.zig", "// stub\n")
        case_count += 1

        (root / "scripts/zigux/check-phase13-devres-packet.py").unlink()
        _assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase13-devres-packet.py"],
            "missing_required_file_guard_failed",
        )
        _write(root / "scripts/zigux/check-phase13-devres-packet.py", "# stub\n")
        case_count += 1

    print("PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current shipped Phase 13 release packet surfaces."
    )
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

    print("PHASE13_RELEASE_VALIDATION=pass")
    print(
        "PHASE13_RELEASE_VALIDATION_MARKER_COUNT="
        f"{len(REQUIRED_FILES) + len(DOC_REQUIRED_MARKERS) + len(REVIEW_REQUIRED_MARKERS) + len(DOC_EXACT_COUNTS) + len(REVIEW_EXACT_COUNTS) + len(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS) + len(CONTRIBUTOR_GUIDE_EXACT_COUNTS) + len(CONTRIBUTOR_SYNC_REQUIRED_MARKERS) + len(CONTRIBUTOR_SYNC_EXACT_COUNTS) + len(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS) + len(TESTS_REVIEW_COMPANION_EXACT_COUNTS) + len(SCRIPTS_REQUIRED_MARKERS) + len(TESTS_REQUIRED_MARKERS) + len(MAKE_REQUIRED_LINES) + len(PHASE13_BUILD_EXACT_COUNTS) + len(PHASE13_BUILD_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
