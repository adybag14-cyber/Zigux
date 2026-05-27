#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


GAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-np-wrapper-gap.md")
IOMAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-planner.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase13_devres_iomap_planner_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase13_devres_iomap_planner.zig")
HELPER_PATH = Path("lib/devres.zig")
IOMAP_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-iomap-planner.py")
WORKFLOW_GUIDE_PATH = Path("Documentation/zigux/phase13-contributor-workflow-guide.md")
RELEASE_SURVEY_PATH = Path("Documentation/zigux/phase13-release-notes-survey.md")
TRACEABILITY_PATH = Path("Documentation/zigux/phase13-roadmap-traceability.md")

REQUIRED_FILES = [
    GAP_NOTE_PATH,
    IOMAP_NOTE_PATH,
    SURVEY_PATH,
    MANIFEST_PATH,
    REPLAY_PATH,
    HELPER_PATH,
    IOMAP_CHECKER_PATH,
    WORKFLOW_GUIDE_PATH,
    RELEASE_SURVEY_PATH,
    TRACEABILITY_PATH,
]

GAP_NOTE_MARKERS = [
    "# Phase 13 devres Non-Posted Wrapper Gap",
    "blocked `devm_ioremap_np()` wrapper",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`python3 scripts/zigux/check-phase13-devres-np-wrapper-gap.py`",
]

IOMAP_NOTE_MARKERS = [
    "translated helper-first remap would still require the blocked `devm_ioremap_np()` wrapper",
    "devm_ioremap_np()",
]

SURVEY_MARKERS = [
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "helper-first iomap planning evidence",
]

MANIFEST_MARKERS = [
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
]

REPLAY_MARKERS = [
    "phase13 devres iomap planning keeps the blocked non-posted wrapper requirement explicit",
]

HELPER_REQUIRED_MARKERS = [
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".touches_live_mmio = false",
    "requires_nonposted_ioremap",
]

HELPER_FORBIDDEN_MARKERS = [
    "devm_ioremap_np(",
]

IOMAP_CHECKER_MARKERS = [
    "devm_ioremap_np()",
    "\"\\\"id\\\": \\\"phase13-devres-missing-devm-ioremap-np-surface\\\"\"",
]

SUMMARY_FORBIDDEN_MARKERS = [
    "devm_ioremap_np()",
    "phase13-devres-missing-devm-ioremap-np-surface",
    "requires_nonposted_ioremap",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:missing_marker:{marker}" for marker in markers if marker not in text]


def collect_unexpected(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:unexpected_marker:{marker}" for marker in markers if marker in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        (GAP_NOTE_PATH, GAP_NOTE_MARKERS, "gap_note"),
        (IOMAP_NOTE_PATH, IOMAP_NOTE_MARKERS, "iomap_note"),
        (SURVEY_PATH, SURVEY_MARKERS, "survey"),
        (MANIFEST_PATH, MANIFEST_MARKERS, "manifest"),
        (REPLAY_PATH, REPLAY_MARKERS, "replay"),
        (HELPER_PATH, HELPER_REQUIRED_MARKERS, "helper"),
        (IOMAP_CHECKER_PATH, IOMAP_CHECKER_MARKERS, "iomap_checker"),
    ]
    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))

    issues.extend(collect_unexpected(read_text(root / HELPER_PATH), HELPER_FORBIDDEN_MARKERS, "helper_scope"))

    for summary_path in [WORKFLOW_GUIDE_PATH, RELEASE_SURVEY_PATH, TRACEABILITY_PATH]:
        issues.extend(
            collect_unexpected(
                read_text(root / summary_path),
                SUMMARY_FORBIDDEN_MARKERS,
                summary_path.as_posix(),
            )
        )

    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        GAP_NOTE_PATH: "\n".join(GAP_NOTE_MARKERS) + "\n",
        IOMAP_NOTE_PATH: "\n".join(IOMAP_NOTE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        MANIFEST_PATH: "\n".join(MANIFEST_MARKERS) + "\n",
        REPLAY_PATH: "\n".join(REPLAY_MARKERS) + "\n",
        HELPER_PATH: "\n".join(HELPER_REQUIRED_MARKERS) + "\n",
        IOMAP_CHECKER_PATH: "\n".join(IOMAP_CHECKER_MARKERS) + "\n",
        WORKFLOW_GUIDE_PATH: "shared reminder packet only\n",
        RELEASE_SURVEY_PATH: "shared release packet only\n",
        TRACEABILITY_PATH: "roadmap anchor summary only\n",
    }
    for rel, text in writes.items():
        write_text(root / rel, text)


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-np-wrapper-gap-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / GAP_NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{GAP_NOTE_PATH.as_posix()}"],
            "missing_gap_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / IOMAP_NOTE_PATH,
            "devm_ioremap_np()\n",
        )
        assert_only(
            validate(root),
            [
                "iomap_note:missing_marker:translated helper-first remap would still require the blocked `devm_ioremap_np()` wrapper",
            ],
            "missing_iomap_note_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "helper-first iomap planning evidence\n")
        assert_only(
            validate(root),
            [
                "survey:missing_marker:blocked `phase13-devres-missing-devm-ioremap-np-surface`",
            ],
            "missing_survey_gap_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_REQUIRED_MARKERS + ["devm_ioremap_np("]) + "\n")
        assert_only(
            validate(root),
            ["helper_scope:unexpected_marker:devm_ioremap_np("],
            "unexpected_live_wrapper_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / WORKFLOW_GUIDE_PATH, "devm_ioremap_np()\n")
        assert_only(
            validate(root),
            [
                "Documentation/zigux/phase13-contributor-workflow-guide.md:unexpected_marker:devm_ioremap_np()",
            ],
            "unexpected_workflow_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / RELEASE_SURVEY_PATH, "phase13-devres-missing-devm-ioremap-np-surface\n")
        assert_only(
            validate(root),
            [
                "Documentation/zigux/phase13-release-notes-survey.md:unexpected_marker:phase13-devres-missing-devm-ioremap-np-surface",
            ],
            "unexpected_release_gap_id_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / TRACEABILITY_PATH, "requires_nonposted_ioremap\n")
        assert_only(
            validate(root),
            [
                "Documentation/zigux/phase13-roadmap-traceability.md:unexpected_marker:requires_nonposted_ioremap",
            ],
            "unexpected_traceability_helper_marker_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_NP_WRAPPER_GAP_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_NP_WRAPPER_GAP_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 13 devres non-posted MMIO wrapper reminder gap."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_NP_WRAPPER_GAP=fail")
        return 1

    print("PHASE13_DEVRES_NP_WRAPPER_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())