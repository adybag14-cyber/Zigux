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
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
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
]

REVIEW_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
]

SCRIPTS_REQUIRED_MARKERS = [
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/bindings/notifier_abi.zig",
    "validate-phase13-release.py",
    "check-phase13-devres-packet.py",
    "zigux/tests/phase13_build.zig",
    "phase13_libfs.zig",
    "phase13_devres.zig",
    "phase13_devres_reviewability.zig",
    "phase13_landlock_ruleset.zig",
    "phase13_landlock_syscalls.zig",
    "phase13_libfs_reviewability.zig",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
    "the six-test shared helper replay",
    "adjacent review evidence instead of adding extra shared replay steps on `master`",
]

PHASE13_BUILD_EXACT_COUNTS = {
    " = b.addTest(.{": 6,
    "test_step.dependOn(&run_phase13_": 6,
    '.root_source_file = b.path("phase13_libfs.zig"),': 1,
    '.root_source_file = b.path("phase13_devres.zig"),': 1,
    '.root_source_file = b.path("phase13_devres_reviewability.zig"),': 1,
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
    scripts_readme = _read(root / "scripts/zigux/README.md")
    makefile = _read(root / "zigux/Makefile")
    phase13_build = _read(root / "zigux/tests/phase13_build.zig")

    issues.extend(_collect_missing_markers(docs_readme, DOC_REQUIRED_MARKERS, "docs-readme"))
    issues.extend(_collect_missing_markers(review_checklist, REVIEW_REQUIRED_MARKERS, "review-checklist"))
    issues.extend(_collect_missing_markers(scripts_readme, SCRIPTS_REQUIRED_MARKERS, "scripts-readme"))
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
            "test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);",
            "test_step.dependOn(&run_phase13_landlock_syscalls_tests.step);",
            "test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);",
            '.root_source_file = b.path("phase13_libfs.zig"),',
            '.root_source_file = b.path("phase13_devres.zig"),',
            '.root_source_file = b.path("phase13_devres_reviewability.zig"),',
            '.root_source_file = b.path("phase13_landlock_ruleset.zig"),',
            '.root_source_file = b.path("phase13_landlock_syscalls.zig"),',
            '.root_source_file = b.path("phase13_libfs_reviewability.zig"),',
            "",
        )
    )


def _seed_fixture_tree(root: Path) -> None:
    _write(root / "Documentation/zigux/README.md", "\n".join(DOC_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
    _write(root / "Documentation/zigux/phase13-release-notes-survey.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-roadmap-traceability.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-notifier-list-survey.md", "# stub\n")
    _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", "# stub\n")
    _write(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md", "# stub\n")
    _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
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
            "scripts/zigux/README.md",
            "zigux/Makefile",
            "zigux/tests/phase13_build.zig",
        }:
            continue
        _write(root / rel, "// stub\n" if rel.endswith((".zig", ".h", ".py")) else "{}\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase13-release-validator-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_release_validator_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        makefile_path = root / "zigux/Makefile"
        baseline_makefile = _read(makefile_path)
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
            ],
            "docs_marker_guard_failed",
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
            ],
            "review_marker_guard_failed",
        )
        _write(root / "Documentation/zigux/review-checklist.md", "\n".join(REVIEW_REQUIRED_MARKERS) + "\n")
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
                "scripts-readme:check-phase13-devres-packet.py",
                "scripts-readme:zigux/tests/phase13_build.zig",
                "scripts-readme:phase13_libfs.zig",
                "scripts-readme:phase13_devres.zig",
                "scripts-readme:phase13_devres_reviewability.zig",
                "scripts-readme:phase13_landlock_ruleset.zig",
                "scripts-readme:phase13_landlock_syscalls.zig",
                "scripts-readme:phase13_libfs_reviewability.zig",
                "scripts-readme:make -C zigux phase13-validate",
                "scripts-readme:make -C zigux phase13",
                "scripts-readme:the six-test shared helper replay",
                "scripts-readme:adjacent review evidence instead of adding extra shared replay steps on `master`",
            ],
            "scripts_marker_guard_failed",
        )
        _write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_REQUIRED_MARKERS) + "\n")
        case_count += 1

        phase13_build_path = root / "zigux/tests/phase13_build.zig"
        phase13_build_path.write_text(_baseline_phase13_build() + "const phase13_extra_tests = b.addTest(.{\n});\n", encoding="utf-8")
        _assert_only(
            validate(root),
            ["phase13-build: = b.addTest(.{:expected=6:actual=7"],
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
            ["phase13-build:test_step.dependOn(&run_phase13_:expected=6:actual=7"],
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
                'const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);\n',
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
        _write(root / "Documentation/zigux/phase13-contributor-workflow-guide.md", "# stub\n")
        case_count += 1

        (root / "zigux/tests/phase13_devres_manifest.json").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase13_devres_manifest.json"],
            "missing_devres_manifest_guard_failed",
        )
        _write(root / "zigux/tests/phase13_devres_manifest.json", "{}\n")
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
        f"{len(REQUIRED_FILES) + len(DOC_REQUIRED_MARKERS) + len(REVIEW_REQUIRED_MARKERS) + len(SCRIPTS_REQUIRED_MARKERS) + len(MAKE_REQUIRED_LINES) + len(PHASE13_BUILD_EXACT_COUNTS) + len(PHASE13_BUILD_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
