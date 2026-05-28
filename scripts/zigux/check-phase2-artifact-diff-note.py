#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_NOTE = Path("Documentation/zigux/artifact-diff.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
BOOTSTRAP_LEDGER = Path("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")

REQUIRED_FILES = (
    ARTIFACT_NOTE,
    PHASE2_CLOSURE,
    SCRIPTS_README,
    BOOTSTRAP_LEDGER,
)

FILE_MARKERS = {
    ARTIFACT_NOTE: (
        "# Zigux Artifact-Diff Notes",
        "## Current Phase 2 use",
        "Phase 2 still routes focused host-tool fixture comparisons through the same helper family when validating `fixdep` and the kconfig bridge packet.",
        "The current `genksyms` bridge packet keeps its fixture comparisons local to `scripts/zigux/check-genksyms-bridge.py`.",
    ),
    PHASE2_CLOSURE: (
        "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`",
        "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
        "If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.",
    ),
    SCRIPTS_README: (
        "- `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the current fixdep governance, determinism, helper, fixture, and CI packet explicit from the scripts root",
    ),
    BOOTSTRAP_LEDGER: (
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "- `Documentation/zigux/artifact-diff.md`",
        "- `scripts/zigux/README.md`",
    ),
}

FORBIDDEN_MARKERS = {
    PHASE2_CLOSURE: (
        "`Documentation/zigux/artifact-diff.md`",
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root / ARTIFACT_NOTE,
        "\n".join(
            (
                "# Zigux Artifact-Diff Notes",
                "",
                "## Current Phase 2 use",
                "",
                FILE_MARKERS[ARTIFACT_NOTE][2],
                FILE_MARKERS[ARTIFACT_NOTE][3],
                "",
            )
        ),
    )
    write_text(
        root / PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                FILE_MARKERS[PHASE2_CLOSURE][0],
                FILE_MARKERS[PHASE2_CLOSURE][1],
                FILE_MARKERS[PHASE2_CLOSURE][2],
                "",
            )
        ),
    )
    write_text(
        root / SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                FILE_MARKERS[SCRIPTS_README][0],
                "",
            )
        ),
    )
    write_text(
        root / BOOTSTRAP_LEDGER,
        "\n".join(
            (
                "# Zigux Alpha Bootstrap Commit Ledger",
                "",
                "## Commit Train",
                "",
                FILE_MARKERS[BOOTSTRAP_LEDGER][0],
                FILE_MARKERS[BOOTSTRAP_LEDGER][1],
                FILE_MARKERS[BOOTSTRAP_LEDGER][2],
                "",
            )
        ),
    )


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        abs_path = root / rel_path
        if not abs_path.is_file():
            issues.append(f"missing_file:{rel_path.as_posix()}")
            continue

        text = read_text(abs_path)
        for marker in FILE_MARKERS[rel_path]:
            if marker not in text:
                issues.append(f"missing_marker:{rel_path.as_posix()}:{marker}")
        for marker in FORBIDDEN_MARKERS.get(rel_path, ()):
            if marker in text:
                issues.append(f"forbidden_marker:{rel_path.as_posix()}:{marker}")

    return issues


def run_self_test() -> int:
    cases_run = 0

    with tempfile.TemporaryDirectory(prefix="phase2_artifact_diff_note_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        if collect_issues(root):
            raise SystemExit("phase2-artifact-diff-note:self-test:good_tree")
        cases_run += 1

        build_sample_root(root)
        (root / ARTIFACT_NOTE).unlink()
        issues = collect_issues(root)
        if issues != [f"missing_file:{ARTIFACT_NOTE.as_posix()}"]:
            raise SystemExit("phase2-artifact-diff-note:self-test:missing_note")
        cases_run += 1

        build_sample_root(root)
        write_text(root / ARTIFACT_NOTE, "# Zigux Artifact-Diff Notes\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{ARTIFACT_NOTE.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-artifact-diff-note:self-test:note_markers")
        cases_run += 1

        build_sample_root(root)
        write_text(
            root / PHASE2_CLOSURE,
            "\n".join(
                (
                    "# Phase 2 Closure",
                    "",
                    FILE_MARKERS[PHASE2_CLOSURE][0],
                    FILE_MARKERS[PHASE2_CLOSURE][1],
                    FILE_MARKERS[PHASE2_CLOSURE][2],
                    "`Documentation/zigux/artifact-diff.md`",
                    "",
                )
            ),
        )
        issues = collect_issues(root)
        expected = (
            f"forbidden_marker:{PHASE2_CLOSURE.as_posix()}:"
            "`Documentation/zigux/artifact-diff.md`"
        )
        if expected not in issues:
            raise SystemExit("phase2-artifact-diff-note:self-test:closure_forbidden")
        cases_run += 1

        build_sample_root(root)
        write_text(root / SCRIPTS_README, "# scripts/zigux\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{SCRIPTS_README.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-artifact-diff-note:self-test:scripts_marker")
        cases_run += 1

        build_sample_root(root)
        write_text(root / BOOTSTRAP_LEDGER, "# Zigux Alpha Bootstrap Commit Ledger\n")
        issues = collect_issues(root)
        expected_prefix = f"missing_marker:{BOOTSTRAP_LEDGER.as_posix()}:"
        if not issues or not all(issue.startswith(expected_prefix) for issue in issues):
            raise SystemExit("phase2-artifact-diff-note:self-test:ledger_markers")
        cases_run += 1

    print("PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 25 artifact-diff note stays aligned with the "
            "current broadened Phase 2 reminder boundary."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_ARTIFACT_DIFF_NOTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_ARTIFACT_DIFF_NOTE=fail")
        print("PHASE2_ARTIFACT_DIFF_NOTE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_ARTIFACT_DIFF_NOTE_ISSUES_END")
        return 1

    print("PHASE2_ARTIFACT_DIFF_NOTE=pass")
    print(f"PHASE2_ARTIFACT_DIFF_NOTE_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_ARTIFACT_DIFF_NOTE_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    print(
        "PHASE2_ARTIFACT_DIFF_NOTE_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
