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
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
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
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
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
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "zigux/tests/README.md",
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
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
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
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
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


def _repeat_markers(markers: list[str], exact_counts: dict[str, int]) -> str:
    entries = list(markers)
    for needle, expected in exact_counts.items():
        extra = expected - entries.count(needle)
        if extra > 0:
            entries.extend([needle] * extra)
    return "\n".join(entries) + "\n"


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
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py",
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


def _placeholder(rel: str) -> str:
    if rel.endswith(".json"):
        return "{}\n"
    if rel.endswith(".py"):
        return "# stub\n"
    if rel.endswith(".md"):
        return "# stub\n"
    if rel.endswith(".h"):
        return "// stub\n"
    if rel.endswith(".zig"):
        return "// stub\n"
    return "\n"


def _seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        _write(root / rel, _placeholder(rel))

    _write(root / "Documentation/zigux/README.md", "\n".join(DOC_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
    _write(
        root / "Documentation/zigux/phase13-contributor-workflow-guide.md",
        _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
    )
    _write(
        root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
        _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
    )
    _write(
        root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
        _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
    )
    _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/tests/README.md", "\n".join(TESTS_REQUIRED_MARKERS) + "\n")
    _write(root / "zigux/Makefile", _baseline_makefile())
    _write(root / "zigux/tests/phase13_build.zig", _baseline_phase13_build())


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _seed_fixture_tree(root)

        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        contributor_guide_path = root / "Documentation/zigux/phase13-contributor-workflow-guide.md"
        contributor_guide_path.write_text(
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS).replace(
                "scripts/zigux/check-phase13-landlock-ruleset-packet.py\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide-exact:scripts/zigux/check-phase13-landlock-ruleset-packet.py:expected=3:actual=2"],
            "contributor_guide_landlock_checker_exact_count_guard_failed",
        )
        _write(
            contributor_guide_path,
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
        )
        case_count += 1

        contributor_guide_path.write_text(
            "\n".join(
                marker
                for marker in _repeat_markers(
                    CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS
                ).splitlines()
                if marker != "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "contributor-workflow-guide:zigux/tests/phase13_landlock_syscalls_reviewability.zig",
                "contributor-workflow-guide-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=2:actual=0",
            ],
            "missing_contributor_guide_landlock_reviewability_marker_failed",
        )
        _write(
            contributor_guide_path,
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
        )
        case_count += 1

        contributor_guide_path.write_text(
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS).replace(
                "Documentation/zigux/phase13-shared-helper-lane-sequencing.md\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide-exact:Documentation/zigux/phase13-shared-helper-lane-sequencing.md:expected=4:actual=3"],
            "contributor_guide_sequencing_exact_count_guard_failed",
        )
        _write(
            contributor_guide_path,
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
        )
        case_count += 1

        contributor_guide_path.write_text(
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS).replace(
                "zigux/tests/phase13_landlock_syscalls_reviewability.zig\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=2:actual=1"],
            "contributor_guide_landlock_reviewability_exact_count_guard_failed",
        )
        _write(
            contributor_guide_path,
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
        )
        case_count += 1

        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            "\n".join(
                marker
                for marker in SCRIPTS_REQUIRED_MARKERS
                if marker != "check-phase13-landlock-ruleset-packet.py"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["scripts-readme:check-phase13-landlock-ruleset-packet.py"],
            "missing_scripts_readme_landlock_checker_marker_failed",
        )
        _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        tests_readme_path = root / "zigux/tests/README.md"
        tests_readme_path.write_text(
            "\n".join(
                marker
                for marker in TESTS_REQUIRED_MARKERS
                if marker != "scripts/zigux/check-phase13-landlock-ruleset-packet.py"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-readme:scripts/zigux/check-phase13-landlock-ruleset-packet.py"],
            "missing_tests_readme_landlock_checker_marker_failed",
        )
        _write(root / "zigux/tests/README.md", "\n".join(TESTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        tests_readme_path.write_text(
            "\n".join(
                marker
                for marker in TESTS_REQUIRED_MARKERS
                if marker != "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-readme:zigux/tests/phase13_landlock_syscalls_reviewability.zig"],
            "missing_tests_readme_landlock_reviewability_marker_failed",
        )
        _write(root / "zigux/tests/README.md", "\n".join(TESTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        scripts_readme_path.write_text(
            "\n".join(
                marker
                for marker in SCRIPTS_REQUIRED_MARKERS
                if marker != "zigux/tests/phase13_notifier_list_reviewability.zig"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["scripts-readme:zigux/tests/phase13_notifier_list_reviewability.zig"],
            "missing_scripts_readme_notifier_reviewability_marker_failed",
        )
        _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        contributor_guide_path.write_text(
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS).replace(
                "zigux/tests/phase13_notifier_list_reviewability.zig\n", "",
                1,
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-workflow-guide-exact:zigux/tests/phase13_notifier_list_reviewability.zig:expected=2:actual=1"],
            "contributor_guide_notifier_reviewability_exact_count_guard_failed",
        )
        _write(
            contributor_guide_path,
            _repeat_markers(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS, CONTRIBUTOR_GUIDE_EXACT_COUNTS),
        )
        case_count += 1

        contributor_surface_sync_path = root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"
        contributor_surface_sync_path.write_text(
            "\n".join(
                marker
                for marker in _repeat_markers(
                    CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS
                ).splitlines()
                if marker != "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "contributor-surface-sync:zigux/tests/phase13_landlock_syscalls_reviewability.zig",
                "contributor-surface-sync-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=2:actual=0",
            ],
            "missing_contributor_surface_sync_landlock_reviewability_marker_failed",
        )
        _write(
            contributor_surface_sync_path,
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
        )
        case_count += 1

        contributor_surface_sync_path.write_text(
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS).replace(
                "zigux/tests/phase13_landlock_syscalls_reviewability.zig\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-surface-sync-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=2:actual=1"],
            "contributor_surface_sync_landlock_reviewability_exact_count_guard_failed",
        )
        _write(
            contributor_surface_sync_path,
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
        )
        case_count += 1

        contributor_surface_sync_path.write_text(
            "\n".join(
                marker
                for marker in _repeat_markers(
                    CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS
                ).splitlines()
                if marker != "scripts/zigux/check-phase13-landlock-ruleset-packet.py"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "contributor-surface-sync:scripts/zigux/check-phase13-landlock-ruleset-packet.py",
                "contributor-surface-sync-exact:scripts/zigux/check-phase13-landlock-ruleset-packet.py:expected=1:actual=0",
            ],
            "missing_contributor_surface_sync_landlock_checker_marker_failed",
        )
        _write(
            contributor_surface_sync_path,
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
        )
        case_count += 1

        contributor_surface_sync_path.write_text(
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS).replace(
                "zigux/tests/phase13_notifier_list_reviewability.zig\n", "",
                1,
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-surface-sync-exact:zigux/tests/phase13_notifier_list_reviewability.zig:expected=2:actual=1"],
            "contributor_surface_sync_notifier_reviewability_exact_count_guard_failed",
        )
        _write(
            contributor_surface_sync_path,
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
        )
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(
            _baseline_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-landlock-ruleset-packet.py"],
            "missing_makefile_landlock_checker_route_failed",
        )
        _write(root / "zigux/Makefile", _baseline_makefile())
        case_count += 1

        tests_review_companion_path = root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        tests_review_companion_path.write_text(
            "\n".join(
                marker
                for marker in _repeat_markers(
                    TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS
                ).splitlines()
                if marker != "scripts/zigux/check-phase13-landlock-ruleset-packet.py"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "tests-review-companion:scripts/zigux/check-phase13-landlock-ruleset-packet.py",
                "tests-review-companion-exact:scripts/zigux/check-phase13-landlock-ruleset-packet.py:expected=3:actual=0",
            ],
            "missing_landlock_checker_marker_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        tests_review_companion_path.write_text(
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS).replace(
                "scripts/zigux/check-phase13-landlock-ruleset-packet.py\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-review-companion-exact:scripts/zigux/check-phase13-landlock-ruleset-packet.py:expected=3:actual=2"],
            "tests_review_companion_landlock_checker_exact_count_guard_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        tests_review_companion_path.write_text(
            "\n".join(
                marker
                for marker in _repeat_markers(
                    TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS
                ).splitlines()
                if marker != "zigux/tests/phase13_landlock_syscalls_reviewability.zig"
            )
            + "\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            [
                "tests-review-companion:zigux/tests/phase13_landlock_syscalls_reviewability.zig",
                "tests-review-companion-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=3:actual=0",
            ],
            "missing_landlock_reviewability_marker_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        tests_review_companion_path.write_text(
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS).replace(
                "zigux/tests/phase13_landlock_syscalls_reviewability.zig\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-review-companion-exact:zigux/tests/phase13_landlock_syscalls_reviewability.zig:expected=3:actual=2"],
            "tests_review_companion_landlock_reviewability_exact_count_guard_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        contributor_surface_sync_path.write_text(
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS).replace(
                "Documentation/zigux/phase13-shared-helper-lane-sequencing.md\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["contributor-surface-sync:Documentation/zigux/phase13-shared-helper-lane-sequencing.md"],
            "missing_contributor_surface_sync_sequencing_marker_failed",
        )
        _write(
            contributor_surface_sync_path,
            _repeat_markers(CONTRIBUTOR_SYNC_REQUIRED_MARKERS, CONTRIBUTOR_SYNC_EXACT_COUNTS),
        )
        case_count += 1

        tests_review_companion_path.write_text(
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS).replace(
                "Documentation/zigux/phase13-shared-helper-lane-sequencing.md\n", "", 1
            ),
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-review-companion:Documentation/zigux/phase13-shared-helper-lane-sequencing.md"],
            "missing_tests_review_companion_sequencing_marker_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        tests_review_companion_path.write_text(
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS)
            + "same shipped validator-first release path\n",
            encoding="utf-8",
        )
        _assert_only(
            validate(root),
            ["tests-review-companion-exact:same shipped validator-first release path:expected=1:actual=2"],
            "tests_review_companion_exact_count_guard_failed",
        )
        _write(
            tests_review_companion_path,
            _repeat_markers(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS, TESTS_REVIEW_COMPANION_EXACT_COUNTS),
        )
        case_count += 1

        (root / "scripts/zigux/check-phase13-landlock-ruleset-packet.py").unlink()
        _assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase13-landlock-ruleset-packet.py"],
            "missing_landlock_checker_file_failed",
        )
        _write(root / "scripts/zigux/check-phase13-landlock-ruleset-packet.py", "# stub\n")
        case_count += 1

        (root / "Documentation/zigux/phase13-shared-helper-lane-sequencing.md").unlink()
        _assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase13-shared-helper-lane-sequencing.md"],
            "missing_shared_helper_lane_sequencing_file_failed",
        )
        _write(root / "Documentation/zigux/phase13-shared-helper-lane-sequencing.md", "# stub\n")
        case_count += 1

        (root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_landlock_syscalls_reviewability.zig"],
            "missing_landlock_reviewability_file_failed",
        )
        _write(root / "zigux/tests/phase13_landlock_syscalls_reviewability.zig", "// stub\n")
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

    marker_total = (
        len(REQUIRED_FILES)
        + len(DOC_REQUIRED_MARKERS)
        + len(REVIEW_REQUIRED_MARKERS)
        + len(DOC_EXACT_COUNTS)
        + len(REVIEW_EXACT_COUNTS)
        + len(CONTRIBUTOR_GUIDE_REQUIRED_MARKERS)
        + len(CONTRIBUTOR_GUIDE_EXACT_COUNTS)
        + len(CONTRIBUTOR_SYNC_REQUIRED_MARKERS)
        + len(CONTRIBUTOR_SYNC_EXACT_COUNTS)
        + len(TESTS_REVIEW_COMPANION_REQUIRED_MARKERS)
        + len(TESTS_REVIEW_COMPANION_EXACT_COUNTS)
        + len(SCRIPTS_REQUIRED_MARKERS)
        + len(TESTS_REQUIRED_MARKERS)
        + len(MAKE_REQUIRED_LINES)
        + len(PHASE13_BUILD_EXACT_COUNTS)
        + len(PHASE13_BUILD_REQUIRED_MARKERS)
    )
    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_VALIDATION_MARKER_COUNT={marker_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
