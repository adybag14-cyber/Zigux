#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "scripts/zigux/validate-phase13-release.py",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-release-coordination-matrix.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase13-devres-packet-alignment.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "scripts/zigux/check-phase13-notifier-priority-signal.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "security/landlock/ruleset.zig",
    "security/landlock/syscalls.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/helpers/notifier_chain_view.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/abi.h",
    "drivers/tty/hvc/hvc_console.h",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 13 notes -",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-release-notes-survey.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
        "`security/landlock/ruleset.zig`",
        "`zigux/tests/phase13_landlock_ruleset.zig`",
        "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
        "`security/landlock/syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "rather than through an older shared-build bundle.",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 13 contributor packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
    ],
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "Broad summaries should keep the active shared-helper release handle visible through:",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-release-coordination-matrix.md`",
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/tests/phase13_build.zig`",
        "`zigux/tests/phase13_devres_boundary_evidence.zig`",
        "repo-reality gaps rather than independently shipped current-`master` evidence.",
        "Broad summaries should also keep the paired Landlock ownership, ruleset-survey, syscall-governance, and syscall-survey notes explicit inside that same release handle through:",
        "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:",
        "Broad summaries should also keep the current devres checker label explicit: older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift.",
        "Broad summaries should also keep the currently materialized manifest-backed helper anchors explicit through:",
        "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:",
        "Broad summaries should also keep the shipped adjacent notifier release surface visible through:",
        "If direct notifier companions such as:",
    ],
    "Documentation/zigux/phase13-release-coordination-matrix.md": [
        "# Phase 13 Release Coordination Matrix",
        "This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.",
        "release companion: `Documentation/zigux/phase13-release-notes-survey.md`",
        "traceability companion: `Documentation/zigux/phase13-roadmap-traceability.md`",
        "workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "tests-root companion: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "release validator: `scripts/zigux/validate-phase13-release.py`",
        "shared replay handle: `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13`",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.",
        "Current `master` also materializes four manifest-backed helper anchors",
        "Keep those four manifests explicit as the currently materialized helper-anchor set, while `zigux/tests/phase13_build.zig` stays framed as a repo-reality gap",
        "adjacent notifier evidence maps to Phase 13 release-surface truthfulness only",
    ],
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "Use this guide when a change touches the active Phase 13 shared-helper packet",
        "Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle.",
        "current `master` materializes the bounded `libfs` foothold",
        "the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md` note,",
        "the shipped `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes,",
        "the shipped `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json` direct ruleset replay pair,",
        "the shipped `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` direct syscall replay packet,",
        "Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`",
        "still does not materialize these direct Phase 13 companions:",
        "older `scripts/zigux/check-phase13-devres-packet.py`",
    ],
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": [
        "# Phase 13 Shared Helper Lane Sequencing",
        "Treat `make -C zigux phase13-validate` as the stable shared replay handle.",
        "`P13-L04` with verification alias `P13-L03` for `libfs`",
        "`P13-L01` with scheduled follow-through split `P13-L05` plus `P13-L06` for `devres`",
        "`P13-L09` with verification alias `P13-L11` for `landlock/ruleset`",
        "`P13-L17` with scheduled follow-through split `P13-Y04` plus `P13-L13` for `landlock/syscalls`",
        "`P13-Y08` for shared contributor reminders",
        "`P13-Y06` for this shared owner-map note.",
        "adjacent notifier evidence owns",
    ],
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md": [
        "# Phase 13 Landlock Ruleset Ownership Note",
        "`security/landlock/ruleset.zig`",
        "`zigux/tests/phase13_landlock_ruleset.zig`",
        "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`make -C zigux phase13-validate`",
    ],
    "Documentation/zigux/phase13-landlock-ruleset-survey.md": [
        "# Phase 13 Landlock Ruleset Survey",
        "`security/landlock/ruleset.zig`",
        "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
        "`zigux/tests/phase13_landlock_ruleset.zig`",
        "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`Documentation/zigux/phase13-landlock-ruleset-slice.md`",
        "`zigux/tests/phase13_build.zig`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": [
        "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
        "the release-side `fop_ruleset_release()` ownership drop",
        "the combined `ruleset_fops` wrapper contract",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-slice.md": [
        "# Phase 13 Landlock Syscalls Slice",
        "`security/landlock/syscalls.c`",
        "`landlock_restrict_self()`",
        "`landlock_add_rule()`",
        "`fop_ruleset_release()`",
        "`ruleset_fops`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "`zigux/tests/phase13_build.zig`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-survey.md": [
        "# Phase 13 Landlock Syscalls Survey",
        "`security/landlock/syscalls.zig`",
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
        "`zigux/tests/phase13_landlock_syscalls.zig`",
        "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
        "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
        "shared `phase13_build.zig` route still remains absent",
    ],
    "Documentation/zigux/phase13-notifier-list-survey.md": [
        "shared Phase 13 packet keeps this notifier evidence outside the validator-first shared-helper release handle as a counted helper path",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "`zigux/bindings/notifier_abi.zig`",
        "`include/zigux/abi.h`",
        "`drivers/tty/hvc/hvc_console.h`",
        "repo-reality gaps",
    ],
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md": [
        "Keep the shared-subsystems packet explicit through the verified docs-root, validator-first, and contributor-facing replay surfaces:",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "keep the shipped broader Phase 13 tests-root guide in `zigux/tests/README.md` explicit as shared packet evidence",
        "if a broad reminder still spells the missing devres reviewability companion as `zigux/tests/phase13Devres_reviewability.zig`, treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig`",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "## Phase 13 tests-root packet",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "`zigux/bindings/notifier_abi.zig`",
        "`include/zigux/abi.h`",
        "`drivers/tty/hvc/hvc_console.h`",
        "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.",
    ],
    "scripts/zigux/README.md": [
        "Phase 13 flow - keep the shared Phase 13 contributor packet explicit through the shipped contributor and release-surface notes:",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/bindings/notifier_abi.zig`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "while the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` stay explicit on current `master`.",
        "direct slice, survey, manifest, build, notifier, and Landlock tests-root companions that current `master` cannot materialize should stay framed as repo-reality gaps",
    ],
    "zigux/tests/README.md": [
        "keep the shared Phase 13 contributor packet explicit in the tests root too:",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-release-notes-survey.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/bindings/notifier_abi.zig`",
        "`include/zigux/abi.h`",
        "`zigux/helpers/notifier_chain_view.zig`",
        "`drivers/tty/hvc/hvc_console.h`",
        "`zigux/tests/phase13_build.zig`",
        "`scripts/zigux/check-phase13-notifier-packet.py`",
    ],
    "zigux/Makefile": [
        "PHONY += phase13-validate phase13-test phase13",
        "phase13-validate",
        "phase13-test",
        "phase13: phase13-validate phase13-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 13 release-discipline packet",
        "make -C zigux phase13-validate",
        "Run Phase 13 shared helper tests",
        "make -C zigux phase13-test",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")

    if issues:
        return issues

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{rel_path}:{marker}")

    return issues


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if sorted(actual) != sorted(expected):
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-release-validator-") as tmpdir:
        root = Path(tmpdir)
        for rel_path in REQUIRED_FILES:
            if rel_path in REQUIRED_MARKERS:
                write_text(root, rel_path, "\n".join(REQUIRED_MARKERS[rel_path]) + "\n")
            elif rel_path.endswith(".json"):
                write_text(root, rel_path, "{}\n")
            elif rel_path.endswith(".zig"):
                write_text(root, rel_path, "// stub\n")
            elif rel_path.endswith(".h"):
                write_text(root, rel_path, "/* stub */\n")
            elif rel_path.endswith(".py"):
                write_text(root, rel_path, "# stub\n")
            else:
                write_text(root, rel_path, "# stub\n")

        assert_only(validate(root), [], "baseline_should_pass")
        case_count += 1

        (root / "Documentation/zigux/phase13-release-coordination-matrix.md").unlink()
        assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase13-release-coordination-matrix.md"],
            "missing_release_coordination_matrix_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-coordination-matrix.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-release-coordination-matrix.md"]) + "\n",
        )
        case_count += 1

        (root / "scripts/zigux/check-phase13-notifier-priority-signal.py").unlink()
        assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase13-notifier-priority-signal.py"],
            "missing_priority_signal_checker_failed",
        )
        write_text(root, "scripts/zigux/check-phase13-notifier-priority-signal.py", "# stub\n")
        case_count += 1

        (root / "drivers/tty/hvc/hvc_console.h").unlink()
        assert_only(
            validate(root),
            ["missing_file:drivers/tty/hvc/hvc_console.h"],
            "missing_hvc_notifier_header_failed",
        )
        write_text(root, "drivers/tty/hvc/hvc_console.h", "/* stub */\n")
        case_count += 1

        (root / "Documentation/zigux/phase13-landlock-ruleset-survey.md").unlink()
        assert_only(
            validate(root),
            ["missing_file:Documentation/zigux/phase13-landlock-ruleset-survey.md"],
            "missing_ruleset_survey_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-landlock-ruleset-survey.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-ruleset-survey.md"]) + "\n",
        )
        case_count += 1

        (root / "zigux/tests/README.md").unlink()
        assert_only(
            validate(root),
            ["missing_file:zigux/tests/README.md"],
            "missing_tests_readme_failed",
        )
        write_text(root, "zigux/tests/README.md", "\n".join(REQUIRED_MARKERS["zigux/tests/README.md"]) + "\n")
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-slice.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-slice.md"]
                if marker != "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-landlock-syscalls-slice.md:"
                "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`"
            ],
            "missing_syscalls_reviewability_anchor_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-slice.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-slice.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                if marker
                != "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:"
                "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`"
            ],
            "missing_tests_root_review_companion_handle_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                if marker
                != "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:"
                "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:"
            ],
            "missing_devres_guard_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-contributor-workflow-guide.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-contributor-workflow-guide.md"]
                if marker != "Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle."
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-contributor-workflow-guide.md:"
                "Treat `make -C zigux phase13-validate` as the stable contributor-facing replay handle."
            ],
            "missing_stable_replay_handle_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-contributor-workflow-guide.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-contributor-workflow-guide.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-governance.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-governance.md"]
                if marker != "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter."
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-landlock-syscalls-governance.md:"
                "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter."
            ],
            "missing_syscalls_helper_anchor_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-governance.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-governance.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"]
                if marker
                != "keep the shipped broader Phase 13 tests-root guide in `zigux/tests/README.md` explicit as shared packet evidence"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md:"
                "keep the shipped broader Phase 13 tests-root guide in `zigux/tests/README.md` explicit as shared packet evidence"
            ],
            "missing_shipped_tests_root_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]
                if marker
                != "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up."
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:"
                "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up."
            ],
            "missing_materialized_tests_root_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            "\n".join(REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]) + "\n",
        )
        case_count += 1

        write_text(
            root,
            "scripts/zigux/README.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["scripts/zigux/README.md"]
                if marker
                != "while the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` stay explicit on current `master`."
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:scripts/zigux/README.md:"
                "while the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` stay explicit on current `master`."
            ],
            "missing_scripts_readme_notifier_shard_phrase_failed",
        )
        write_text(root, "scripts/zigux/README.md", "\n".join(REQUIRED_MARKERS["scripts/zigux/README.md"]) + "\n")
        case_count += 1

        write_text(
            root,
            "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS["zigux/tests/README.md"]
                if marker != "`zigux/helpers/notifier_chain_view.zig`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "missing_marker:zigux/tests/README.md:`zigux/helpers/notifier_chain_view.zig`"
            ],
            "missing_tests_readme_notifier_chain_view_failed",
        )
        write_text(root, "zigux/tests/README.md", "\n".join(REQUIRED_MARKERS["zigux/tests/README.md"]) + "\n")
        case_count += 1

        write_text(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[".github/workflows/zigux-bootstrap.yml"]
                if marker != "Run Phase 13 shared helper tests"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["missing_marker:.github/workflows/zigux-bootstrap.yml:Run Phase 13 shared helper tests"],
            "missing_phase13_workflow_step_failed",
        )
        case_count += 1

    print("PHASE13_RELEASE_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE13_RELEASE_VALIDATOR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 13 shared-helper release surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
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

    marker_total = len(REQUIRED_FILES) + sum(len(markers) for markers in REQUIRED_MARKERS.values())
    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_VALIDATION_MARKER_COUNT={marker_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())