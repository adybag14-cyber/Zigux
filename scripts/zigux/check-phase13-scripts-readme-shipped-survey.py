#!/usr/bin/env python3
"""Check that the Phase 13 scripts README does not list shipped survey notes as gaps."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

SCRIPTS_README = "scripts/zigux/README.md"
SUPPORTING_PATHS = (
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
)
SHIPPED_SURVEY_NOTES = (
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
)
PHASE13_ANCHOR = "Phase 13 flow - keep the shared Phase 13 contributor packet explicit"
GAP_PREFIX = "- broad scripts-root reminders should keep "
GAP_LIST_MARKER = "and treat missing direct paths such as "


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phase13_gap_line(readme: str) -> str | None:
    for line in readme.splitlines():
        if line.startswith(GAP_PREFIX):
            return line
    return None


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / SCRIPTS_README
    if not readme_path.is_file():
        return [f"missing_file:{SCRIPTS_README}"]

    readme = _read(readme_path)
    if PHASE13_ANCHOR not in readme:
        errors.append("missing_marker:scripts_readme:phase13_anchor")

    gap_line = _phase13_gap_line(readme)
    if gap_line is None:
        errors.append("missing_marker:scripts_readme:phase13_gap_line")
    else:
        gap_suffix = gap_line.split(GAP_LIST_MARKER, 1)[1] if GAP_LIST_MARKER in gap_line else gap_line
        for rel in SHIPPED_SURVEY_NOTES:
            if rel in gap_suffix:
                errors.append(f"scripts_readme:shipped_note_listed_as_gap:{rel}")

    for rel in SUPPORTING_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing_file:{rel}")
            continue
        text = _read(path)
        for shipped in SHIPPED_SURVEY_NOTES[1:]:
            if "landlock" in shipped and shipped not in text:
                errors.append(f"supporting_doc:missing_marker:{rel}:{shipped}")
        if rel.endswith("phase13-contributor-workflow-guide.md") and SHIPPED_SURVEY_NOTES[0] not in text:
            errors.append(f"supporting_doc:missing_marker:{rel}:{SHIPPED_SURVEY_NOTES[0]}")

    return errors


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    good_readme = (
        "# scripts/zigux\n"
        "Phase 13 flow - keep the shared Phase 13 contributor packet explicit through the shipped contributor and release-surface notes:\n"
        "- broad scripts-root reminders should keep `Documentation/zigux/phase13-landlock-syscalls-governance.md` explicit beside "
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`, keep adjacent notifier evidence separate from the four helper anchors, "
        "keep the shipped `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, "
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` explicit as "
        "landed helper-packet notes, and treat missing direct paths such as `Documentation/zigux/phase13-libfs-slice.md` and "
        "`Documentation/zigux/phase13-landlock-ruleset-slice.md` as repo-reality gaps instead of borrowing old checker names.\n"
    )
    bad_readme = (
        "# scripts/zigux\n"
        "Phase 13 flow - keep the shared Phase 13 contributor packet explicit through the shipped contributor and release-surface notes:\n"
        "- broad scripts-root reminders should keep `Documentation/zigux/phase13-landlock-syscalls-governance.md` explicit beside "
        "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`, keep adjacent notifier evidence separate from the four helper anchors, "
        "and treat missing direct paths such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, "
        "`Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, "
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` as repo-reality gaps.\n"
    )
    contributor = (
        "Current `master` materializes the bounded `libfs` foothold through `Documentation/zigux/phase13-libfs-survey.md`.\n"
        "Current `master` also materializes the helper-local Landlock packet through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, "
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md`.\n"
    )
    release = (
        "Broad summaries should also keep the paired Landlock ownership, ruleset-survey, syscall-governance, and syscall-survey notes explicit through:\n"
        "`Documentation/zigux/phase13-landlock-ruleset-survey.md`\n"
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`\n"
        "`Documentation/zigux/phase13-landlock-syscalls-survey.md`\n"
    )
    traceability = (
        "Keep the current `landlock/syscalls` mapping explicit through:\n"
        "`Documentation/zigux/phase13-landlock-syscalls-slice.md`\n"
        "`Documentation/zigux/phase13-landlock-syscalls-survey.md`\n"
        "Keep the current `landlock/ruleset` mapping explicit through:\n"
        "`Documentation/zigux/phase13-landlock-ruleset-survey.md`\n"
    )

    with tempfile.TemporaryDirectory(prefix="phase13-scripts-readme-") as tmpdir:
        root = Path(tmpdir)
        _write(root / SCRIPTS_README, good_readme)
        _write(root / SUPPORTING_PATHS[0], contributor)
        _write(root / SUPPORTING_PATHS[1], release)
        _write(root / SUPPORTING_PATHS[2], traceability)
        assert validate(root) == []

        _write(root / SCRIPTS_README, bad_readme)
        errors = validate(root)
        assert len(errors) == 4
        assert all(err.startswith("scripts_readme:shipped_note_listed_as_gap:") for err in errors)

        _write(root / SCRIPTS_README, "# scripts/zigux\n")
        errors = validate(root)
        assert "missing_marker:scripts_readme:phase13_anchor" in errors
        assert "missing_marker:scripts_readme:phase13_gap_line" in errors

        _write(root / SCRIPTS_README, good_readme)
        _write(root / SUPPORTING_PATHS[0], "Current `master` materializes the bounded `libfs` foothold.\n")
        errors = validate(root)
        assert f"supporting_doc:missing_marker:{SUPPORTING_PATHS[0]}:{SHIPPED_SURVEY_NOTES[0]}" in errors

    print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK=pass")
    print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 13 scripts README summary against shipped survey-note reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK=fail")
        print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK_ISSUES_END")
        return 1

    print("PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK=pass")
    print(f"PHASE13_SCRIPTS_README_SHIPPED_SURVEY_CHECK_ROOT={args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
