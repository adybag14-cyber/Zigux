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
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "Documentation/zigux/phase13-landlock-syscalls-governance.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase13-devres-packet-alignment.py",
    "scripts/zigux/check-phase13-landlock-ruleset-packet.py",
    "scripts/zigux/check-phase13-notifier-priority-signal.py",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 13 notes -",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-release-notes-survey.md`",
        "`Documentation/zigux/phase13-roadmap-traceability.md`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "the current eight-test shared-helper release packet",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 13 release packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
    ],
    "Documentation/zigux/phase13-release-notes-survey.md": [
        "Broad summaries should keep the active shared-helper release handle visible through:",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`zigux/tests/phase13_build.zig`",
        "`zigux/tests/phase13_devres_boundary_evidence.zig`",
        "repo-reality gaps rather than independently shipped current-`master` evidence.",
        "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:",
        "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:",
        "`zigux/bindings/notifier_abi.zig`",
        "`include/zigux/abi.h`",
        "`security/landlock/ruleset.zig`",
        "`security/landlock/syscalls.zig`",
    ],
    "Documentation/zigux/phase13-roadmap-traceability.md": [
        "Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.",
        "`landlock/ruleset` maps to the bounded shared-helper tranche and should keep its ownership boundary explicit.",
        "`landlock/syscalls` maps to the bounded shared-helper tranche and should keep its governance boundary explicit.",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "adjacent notifier evidence remains release-surface support",
    ],
    "Documentation/zigux/phase13-contributor-workflow-guide.md": [
        "Use this guide when a change touches the active Phase 13 shared-helper packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
        "`zigux/helpers/notifier_chain_view.zig`",
    ],
    "Documentation/zigux/phase13-shared-helper-lane-sequencing.md": [
        "# Phase 13 Shared Helper Lane Sequencing",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`make -C zigux phase13-validate`",
        "Treat `make -C zigux phase13-validate` as the stable shared replay handle.",
    ],
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md": [
        "# Phase 13 Landlock Ruleset Ownership Note",
        "`Documentation/zigux/review-checklist.md`",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`make -C zigux phase13-validate`",
    ],
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": [
        "# Phase 13 Landlock Syscalls Governance",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
        "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`make -C zigux phase13-validate`",
        "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
        "the release-side `fop_ruleset_release()` ownership drop",
        "the combined `ruleset_fops` wrapper contract",
    ],
    "Documentation/zigux/phase13-notifier-list-survey.md": [
        "# Phase 13 Notifier List Survey",
        "shared Phase 13 packet keeps this notifier evidence outside the validator-first shared-helper release handle",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`make -C zigux phase13-validate`",
    ],
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md": [
        "## Phase 13 contributor packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "keep the validator-first Phase 13 release handle explicit",
        "framed as repo reality rather than shipped evidence when current `master` still cannot materialize",
        "`scripts/zigux/check-phase13-notifier-packet.py`",
        "`zigux/tests/phase13Devres_reviewability.zig`",
        "treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "## Phase 13 tests-root packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "shared validator-first release handle",
        "`zigux/bindings/notifier_abi.zig`",
        "`include/zigux/abi.h`",
        "record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.",
    ],
    "scripts/zigux/README.md": [
        "Phase 13 flow",
        "`validate-phase13-release.py`",
        "`check-phase13-landlock-ruleset-packet.py`",
        "`check-phase13-notifier-priority-signal.py`",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`make -C zigux phase13-validate`",
        "eight-test shared helper replay",
    ],
    "zigux/tests/README.md": [
        "## Phase 13 tests-root packet",
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
        "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
        "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
        "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
        "`scripts/zigux/validate-phase13-release.py`",
        "`Documentation/zigux/phase13-notifier-list-survey.md`",
        "validator-first eight-test release path",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 13 release-discipline packet",
        "make -C zigux phase13-validate",
        "Run Phase 13 shared helper tests",
        "make -C zigux phase13-test",
    ],
}

EXACT_COUNTS = {
    "Documentation/zigux/phase13-release-notes-survey.md": {
        "Broad summaries should keep the active shared-helper release handle visible through:": 1,
        "repo-reality gaps rather than independently shipped current-`master` evidence.": 1,
        "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:": 1,
        "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:": 1,
        "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:": 1,
    },
    "Documentation/zigux/README.md": {
        "the current eight-test shared-helper release packet": 1,
    },
    "Documentation/zigux/phase13-landlock-syscalls-governance.md": {
        "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.": 1,
    },
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": {
        "record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.": 1,
    },
    "scripts/zigux/README.md": {
        "eight-test shared helper replay": 1,
        "`make -C zigux phase13-validate`": 1,
    },
    "zigux/tests/README.md": {
        "validator-first eight-test release path": 1,
    },
    ".github/workflows/zigux-bootstrap.yml": {
        "make -C zigux phase13-validate": 1,
        "make -C zigux phase13-test": 1,
    },
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def repeat_markers(markers: list[str], counts: dict[str, int] | None = None) -> str:
    items = list(markers)
    if counts:
        for marker, expected in counts.items():
            extra = expected - items.count(marker)
            if extra > 0:
                items.extend([marker] * extra)
    return "\n".join(items) + "\n"


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

    for rel_path, counts in EXACT_COUNTS.items():
        text = read_text(root, rel_path)
        for marker, expected in counts.items():
            actual = text.count(marker)
            if actual != expected:
                issues.append(
                    f"exact_count:{rel_path}:{marker}:expected={expected}:actual={actual}"
                )

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
                write_text(
                    root,
                    rel_path,
                    repeat_markers(REQUIRED_MARKERS[rel_path], EXACT_COUNTS.get(rel_path)),
                )
            elif rel_path.endswith(".yml"):
                write_text(root, rel_path, repeat_markers(REQUIRED_MARKERS[rel_path], EXACT_COUNTS.get(rel_path)))
            elif rel_path.endswith(".py"):
                write_text(root, rel_path, "# stub\n")
            else:
                write_text(root, rel_path, "# stub\n")

        assert_only(validate(root), [], "baseline_should_pass")
        case_count += 1

        (root / "scripts/zigux/check-phase13-notifier-priority-signal.py").unlink()
        assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase13-notifier-priority-signal.py"],
            "missing_priority_checker_failed",
        )
        write_text(root, "scripts/zigux/check-phase13-notifier-priority-signal.py", "# stub\n")
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                    if marker
                    != "Broad summaries should keep the active shared-helper release handle visible through:"
                ],
                {
                    "repo-reality gaps rather than independently shipped current-`master` evidence.": 1,
                    "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:": 1,
                    "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:": 1,
                    "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:": 1,
                },
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should keep the active shared-helper release handle visible through:",
                "exact_count:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should keep the active shared-helper release handle visible through::expected=1:actual=0",
            ],
            "missing_release_handle_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"],
                EXACT_COUNTS["Documentation/zigux/phase13-release-notes-survey.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                    if marker
                    != "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:"
                ],
                {
                    "Broad summaries should keep the active shared-helper release handle visible through:": 1,
                    "repo-reality gaps rather than independently shipped current-`master` evidence.": 1,
                    "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:": 1,
                    "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:": 1,
                },
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:",
                "exact_count:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through::expected=1:actual=0",
            ],
            "missing_landlock_pair_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"],
                EXACT_COUNTS["Documentation/zigux/phase13-release-notes-survey.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                    if marker
                    != "Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:"
                ],
                {
                    "Broad summaries should keep the active shared-helper release handle visible through:": 1,
                    "repo-reality gaps rather than independently shipped current-`master` evidence.": 1,
                    "Broad summaries should also keep the paired Landlock ownership and syscall-governance notes explicit inside that same release handle through:": 1,
                    "Broad summaries should also keep the shipped adjacent direct-evidence shards visible without counting them as extra shared replay steps:": 1,
                },
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through:",
                "exact_count:Documentation/zigux/phase13-release-notes-survey.md:Broad summaries should also keep the shipped devres packet-truthfulness guard explicit through::expected=1:actual=0",
            ],
            "missing_devres_truthfulness_guard_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"],
                EXACT_COUNTS["Documentation/zigux/phase13-release-notes-survey.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"]
                    if marker
                    not in {
                        "`zigux/bindings/notifier_abi.zig`",
                        "`security/landlock/ruleset.zig`",
                        "`security/landlock/syscalls.zig`",
                    }
                ],
                EXACT_COUNTS["Documentation/zigux/phase13-release-notes-survey.md"],
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`zigux/bindings/notifier_abi.zig`",
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`security/landlock/ruleset.zig`",
                "missing_marker:Documentation/zigux/phase13-release-notes-survey.md:`security/landlock/syscalls.zig`",
            ],
            "missing_adjacent_direct_evidence_markers_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-release-notes-survey.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase13-release-notes-survey.md"],
                EXACT_COUNTS["Documentation/zigux/phase13-release-notes-survey.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-governance.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-governance.md"]
                    if marker
                    != "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter."
                ],
                {},
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase13-landlock-syscalls-governance.md:Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.",
                "exact_count:Documentation/zigux/phase13-landlock-syscalls-governance.md:Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.:expected=1:actual=0",
            ],
            "missing_syscalls_anchor_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase13-landlock-syscalls-governance.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase13-landlock-syscalls-governance.md"],
                EXACT_COUNTS["Documentation/zigux/phase13-landlock-syscalls-governance.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]
                    if marker != "`scripts/zigux/check-phase13-devres-packet-alignment.py`"
                ],
                {
                    "record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.": 1,
                },
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:`scripts/zigux/check-phase13-devres-packet-alignment.py`",
            ],
            "missing_tests_companion_devres_guard_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"],
                EXACT_COUNTS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"]
                    if marker != "record them as repo-reality gaps instead of presenting them here as independently shipped review evidence."
                ],
                {},
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.",
                "exact_count:Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.:expected=1:actual=0",
            ],
            "missing_tests_companion_repo_reality_phrase_failed",
        )
        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
            repeat_markers(
                REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"],
                EXACT_COUNTS["Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "scripts/zigux/README.md",
            repeat_markers(
                REQUIRED_MARKERS["scripts/zigux/README.md"],
                EXACT_COUNTS["scripts/zigux/README.md"],
            )
            + "eight-test shared helper replay\n"
            + "`make -C zigux phase13-validate`\n",
        )
        assert_only(
            validate(root),
            [
                "exact_count:scripts/zigux/README.md:eight-test shared helper replay:expected=1:actual=2",
                "exact_count:scripts/zigux/README.md:`make -C zigux phase13-validate`:expected=1:actual=2",
            ],
            "duplicate_scripts_readme_markers_failed",
        )
        write_text(
            root,
            "scripts/zigux/README.md",
            repeat_markers(
                REQUIRED_MARKERS["scripts/zigux/README.md"],
                EXACT_COUNTS["scripts/zigux/README.md"],
            ),
        )
        case_count += 1

        write_text(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            repeat_markers(
                REQUIRED_MARKERS[".github/workflows/zigux-bootstrap.yml"],
                EXACT_COUNTS[".github/workflows/zigux-bootstrap.yml"],
            ).replace("Run Phase 13 shared helper tests\n", "", 1),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:.github/workflows/zigux-bootstrap.yml:Run Phase 13 shared helper tests",
            ],
            "missing_workflow_step_failed",
        )
        write_text(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            repeat_markers(
                REQUIRED_MARKERS[".github/workflows/zigux-bootstrap.yml"],
                EXACT_COUNTS[".github/workflows/zigux-bootstrap.yml"],
            ),
        )
        case_count += 1

        write_text(
            root,
            "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
            repeat_markers(
                [
                    marker
                    for marker in REQUIRED_MARKERS["Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md"]
                    if marker
                    != "treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path"
                ],
                {},
            ),
        )
        assert_only(
            validate(root),
            [
                "missing_marker:Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md:treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path",
            ],
            "missing_devres_typo_guard_failed",
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

    marker_total = (
        len(REQUIRED_FILES)
        + sum(len(markers) for markers in REQUIRED_MARKERS.values())
        + sum(len(counts) for counts in EXACT_COUNTS.values())
    )
    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_VALIDATION_MARKER_COUNT={marker_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
